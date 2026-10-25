"""Evidence-controlled marketing pipeline. No LinkedIn publishing capability."""
import argparse, base64, datetime as dt, fcntl, hashlib, json, os, re, sqlite3, subprocess, sys, urllib.request
from pathlib import Path
from editorial import brief_for_slot
ROOT=Path(__file__).resolve().parents[1]
RECIPIENTS=['rahuljalan23.rj@gmail.com','abhinav.saxena1730@gmail.com','vig6604@gmail.com']
def free_model(model):
 if not isinstance(model,str) or model != model.strip() or not (model=='openrouter/free' or re.fullmatch(r'[\w./-]+:free',model)): raise ValueError('Only OpenRouter free models allowed')
 return model

def validate_draft(d,f):
 if not isinstance(d,dict) or set(d)!={'hook','problem','benefit','claim_ids','cta','hashtags'}: raise ValueError('Draft schema')
 for k in ['hook','problem','benefit','cta']:
  if not isinstance(d[k],str) or not 5<=len(d[k])<=500: raise ValueError('Draft text')
 if not isinstance(d['claim_ids'],list) or not d['claim_ids'] or any(type(i)!=int or not 0<=i<len(f['claims']) for i in d['claim_ids']): raise ValueError('Unverified claim')
 if not isinstance(d['hashtags'],list) or not 1<=len(d['hashtags'])<=4 or any(not isinstance(h,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{1,30}',h) for h in d['hashtags']): raise ValueError('Hashtags')
 text='\n\n'.join([d['hook'],d['problem'],'\n'.join('• '+f['claims'][i] for i in dict.fromkeys(d['claim_ids'])),d['benefit'],d['cta'],' '.join('#'+h for h in d['hashtags'])])
 if d['cta']!='Explore SmartMeet: https://smartmeet.org': raise ValueError('CTA')
 creative=' '.join(d[k] for k in ['hook','problem','benefit'])
 if re.search(r'\d|https?://|@|guarantee|proven|best in|increase.*sales|double|triple|save.*hours|offline|in seconds|in minutes|seamless|GDPR|HIPAA',creative,re.I): raise ValueError('Unsupported marketing assertion')
 if re.search(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|sixty|hundred)\s+(seconds?|minutes?|hours?)\b',creative,re.I):raise ValueError('Unmeasured timing claim')
 if re.search(r'\b(many|most|all)\s+(teams|founders|businesses|companies|users|people)\b|\b(teams|team leads|founders|businesses|companies|users|people)\s+(often|usually|always|typically)\b',creative,re.I):raise ValueError('Unsupported audience prevalence claim')
 if len(text)>2800: raise ValueError('LinkedIn length')
 return text

class State:
 def __init__(self,path):
  self.db=sqlite3.connect(path); self.db.execute('CREATE TABLE IF NOT EXISTS runs(slot TEXT PRIMARY KEY, feature TEXT, status TEXT, updated TEXT)')
 def reserve(self,slot,feature):
  try:
   self.db.execute('INSERT INTO runs VALUES (?,?,?,?)',(slot,feature,'reserved',dt.datetime.now(dt.timezone.utc).isoformat())); self.db.commit(); return True
  except sqlite3.IntegrityError:
   cursor=self.db.execute("UPDATE runs SET status='reserved' WHERE slot=? AND status IN ('failed','preview')",(slot,));self.db.commit();return cursor.rowcount==1
 def status(self,slot,status):
  self.db.execute('UPDATE runs SET status=?,updated=? WHERE slot=?',(status,dt.datetime.now(dt.timezone.utc).isoformat(),slot));self.db.commit()
 def used(self): return [r[0] for r in self.db.execute("SELECT feature FROM runs WHERE status IN ('sent','failed','preview') ORDER BY updated")]

def choose_feature(features,history):
 enabled=[f for f in features if f.get('enabled')]
 if not enabled:raise ValueError('No verified feature available')
 return min(enabled,key=lambda f:max((i for i,v in enumerate(history) if v==f['id']),default=-1))

def email_payload(slot,text,screenshot,sender,brief=None):
 if screenshot is not None and (screenshot.suffix!='.png' or not screenshot.is_file() or screenshot.stat().st_size>5_000_000):raise ValueError('Invalid screenshot')
 note='Screenshot uses a dedicated demo account.' if screenshot is not None else 'Text-only marketing draft; product claims use the verified capability catalog.'
 body={'from':sender,'to':RECIPIENTS,'subject':'SmartMeet LinkedIn draft — '+slot,'text':'Ready for your review and manual LinkedIn posting. '+note+'\nEditorial theme: '+(brief or {}).get('pillar','feature-demo')+'\n\n'+text}
 if screenshot is not None:body['attachments']=[{'filename':'smartmeet-demo.png','content':base64.b64encode(screenshot.read_bytes()).decode()}]
 return body

def request_json(url,body,headers):
 req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','User-Agent':'SmartMeet-Marketing/1.0',**headers})
 with urllib.request.urlopen(req,timeout=45) as res:return json.load(res)

def hermes(payload):
 env={k:os.environ[k] for k in ['PATH','OPENROUTER_API_KEY','HERMES_HOME'] if k in os.environ}
 env.update(PYTHON_DOTENV_DISABLED='1',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
 p=subprocess.run([os.environ.get('HERMES_PYTHON','/usr/local/lib/hermes-agent/venv/bin/python'),str(ROOT/'src/hermes_worker.py')],input=json.dumps(payload),text=True,capture_output=True,env=env,timeout=120)
 if p.returncode:raise RuntimeError('Hermes inference failed: '+p.stderr[-200:])
 return json.loads(p.stdout)

def run(send=False,slot=None):
 state_dir=Path(os.environ.get('AGENT_STATE_DIR',str(ROOT/'var')));state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
 with (state_dir/'run.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return {'status':'already_running'}
  model=free_model(os.environ.get('OPENROUTER_MODEL','nvidia/nemotron-3.5-lightning:free'))
  review_model=free_model(os.environ.get('OPENROUTER_REVIEW_MODEL','openrouter/free'))
  if not os.environ.get('OPENROUTER_API_KEY'):raise ValueError('OPENROUTER_API_KEY missing')
  now=dt.datetime.now(dt.timezone(dt.timedelta(hours=5,minutes=30)))
  slot=slot or now.replace(hour=now.hour//3*3,minute=0,second=0,microsecond=0).isoformat()
  if not re.fullmatch(r'[A-Za-z0-9_:+.-]{1,90}',slot):raise ValueError('Invalid slot')
  state=State(state_dir/'state.db'); features=json.loads((ROOT/'config/features.json').read_text());feature=choose_feature(features,state.used())
  if not state.reserve(slot,feature['id']):return {'status':'already_reserved','slot':slot}
  feature=next(f for f in features if f['id']==state.db.execute('SELECT feature FROM runs WHERE slot=?',(slot,)).fetchone()[0])
  folder=state_dir/slot;folder.mkdir(mode=0o700,exist_ok=True)
  try:
   brief_path=folder/'brief.json'
   if brief_path.exists():brief=json.loads(brief_path.read_text())
   else:
    brief={'pillar':'feature-demo','screenshot_required':True,'direction':'Continue this legacy screenshot-backed draft.'} if (folder/'draft.json').exists() else brief_for_slot(slot)
    brief_path.write_text(json.dumps(brief,indent=2))
   if (folder/'draft.json').exists() and (folder/'review.json').exists():
    draft=json.loads((folder/'draft.json').read_text());text=validate_draft(draft,feature)
    review=json.loads((folder/'review.json').read_text())
    (folder/'review.json').write_text(json.dumps(review,indent=2))
    if review.get('approved') is not True or review.get('unsupported_claims')!=[]:raise ValueError('Unapproved stored draft')
   else:
    if brief['screenshot_required']:
     proc=subprocess.run(['node',str(ROOT/'src/capture.mjs')],input=json.dumps({'feature':feature,'out':str(folder)}),capture_output=True,text=True,timeout=90,env={k:os.environ[k] for k in ['PATH','HOME','DEMO_EMAIL','DEMO_PASSWORD','PLAYWRIGHT_BROWSERS_PATH'] if k in os.environ})
     if proc.returncode:raise RuntimeError('Demo screenshot capture failed')
     evidence=json.loads((folder/'evidence.json').read_text())
     if not evidence.get('observed') or evidence['feature_id']!=feature['id']:raise ValueError('Missing screenshot evidence')
     evidence['type']='observed-ui'
     (folder/'evidence.json').write_text(json.dumps(evidence,indent=2))
    else:
     evidence={'type':'verified-catalog','feature_id':feature['id'],'claims':feature['claims'],'observed':None,'note':'No UI observation or live trend research for this draft.'}
     (folder/'evidence.json').write_text(json.dumps(evidence,indent=2))
    attempts=[];feedback=[]
    for attempt in range(min(2,max(1,int(os.environ.get('MAX_DRAFT_ATTEMPTS','2'))))):
     writer_model=model if attempt==0 else 'openrouter/free'
     reviewer_model=review_model if attempt==0 else model
     stage='write'
     try:
      draft=hermes({'mode':'write','model':writer_model,'feature':feature,'brief':brief,'evidence':evidence,'recent_hooks':recent_hooks(state_dir),'feedback':feedback,'guidance':'Keep every sentence factual. Avoid offline, speed, comparative and outcome claims.'})
      (folder/'candidate.json').write_text(json.dumps(draft,indent=2))
      stage='validate'
      text=validate_draft(draft,feature)
      stage='review'
      review=hermes({'mode':'review','model':reviewer_model,'feature':feature,'brief':brief,'evidence':evidence,'draft':draft})
      (folder/'review.json').write_text(json.dumps(review,indent=2))
      if review.get('approved') is not True or review.get('unsupported_claims')!=[]:
       feedback=review.get('unsupported_claims',[])
       raise ValueError('Factual review rejected draft')
      attempts.append({'writer':writer_model,'reviewer':reviewer_model,'accepted':True})
      break
     except (ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
      if not feedback:feedback=[str(error)[:250]]
      attempts.append({'writer':writer_model,'reviewer':reviewer_model,'accepted':False,'error':type(error).__name__,'stage':stage,'detail':str(error)[:250]})
    else:
     (folder/'attempts.json').write_text(json.dumps(attempts,indent=2))
     raise ValueError('No approved draft within free-model attempt budget')
    (folder/'attempts.json').write_text(json.dumps(attempts,indent=2))
    (folder/'draft.json').write_text(json.dumps(draft,indent=2));(folder/'draft.txt').write_text(text)
   if any(draft['hook'].casefold()==h.casefold() for h in recent_hooks(state_dir,exclude=folder)):raise ValueError('Repeated hook')
   if not send:state.status(slot,'preview');return {'status':'preview','directory':str(folder)}
   payload=email_payload(slot,text,folder/'screenshot.png' if brief['screenshot_required'] else None,os.environ['EMAIL_FROM'],brief)
   state.status(slot,'sending')
   result=request_json('https://api.resend.com/emails',payload,{'Authorization':'Bearer '+os.environ['RESEND_API_KEY'],'Idempotency-Key':'smartmeet-'+hashlib.sha256(slot.encode()).hexdigest()})
   if not result.get('id'):raise RuntimeError('Missing delivery receipt')
   (folder/'delivery.json').write_text(json.dumps({'id':result['id'],'recipients':RECIPIENTS}));state.status(slot,'sent')
   return {'status':'sent','directory':str(folder),'id':result['id']}
  except Exception:
   current=state.db.execute('SELECT status FROM runs WHERE slot=?',(slot,)).fetchone()[0]
   state.status(slot,'delivery_unknown' if current=='sending' else 'failed');raise

def recent_hooks(directory,exclude=None):
 return [json.loads(p.read_text())['hook'] for p in sorted(directory.glob('*/draft.json'))[-60:] if p.parent!=exclude]

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--send',action='store_true');parser.add_argument('--slot');args=parser.parse_args()
 try: print(json.dumps(run(args.send,args.slot)))
 except Exception as e:print(json.dumps({'status':'failed','reason':type(e).__name__}),file=sys.stderr);sys.exit(1)
