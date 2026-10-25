import sys, unittest, tempfile, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from agent import free_model, validate_draft, State, email_payload, choose_feature

FEATURE={'id':'instant-setup','claims':['Choose microphone and camera before joining.'],'audience':'team leads'}
DRAFT={'hook':'Your next meeting starts before the first hello.','problem':'Scrambling to prepare can interrupt your focus.','benefit':'Give your team a more deliberate start.','claim_ids':[0],'cta':'Explore SmartMeet: https://smartmeet.org','hashtags':['SmartMeet','TeamWork']}
class AgentTests(unittest.TestCase):
 def test_free_only(self):
  for m in ['openrouter/free','qwen/test:free']: self.assertEqual(free_model(m),m)
  for m in ['openrouter/auto','gpt-4','test:free ', '',None]:
   with self.assertRaises(ValueError): free_model(m)
 def test_draft_contract(self):
  self.assertIn(FEATURE['claims'][0],validate_draft(DRAFT,FEATURE))
  for change in [{'claim_ids':[99]},{'hook':'Guaranteed 10x sales'},{'cta':'https://evil.example'},{'extra':'x'},{'claim_ids':[]},{'benefit':'Choose an avatar while offline in seconds.'},{'hashtags':['hello\nBcc: evil']}]:
   with self.assertRaises(ValueError): validate_draft({**DRAFT,**change},FEATURE)
 def test_slots_and_ambiguous_delivery(self):
  with tempfile.TemporaryDirectory() as d:
   s=State(Path(d)/'state.db'); self.assertTrue(s.reserve('slot','setup')); self.assertFalse(s.reserve('slot','setup'))
   s.status('slot','sending'); self.assertFalse(s.reserve('slot','setup'))
   s.status('slot','sent'); self.assertEqual(s.used(),['setup'])
 def test_rotation(self):
  fs=[{'id':'a','enabled':True},{'id':'b','enabled':False},{'id':'c','enabled':True}]
  self.assertEqual(choose_feature(fs,['a'])['id'],'c'); self.assertEqual(choose_feature(fs,['a','c'])['id'],'a')
 def test_attachments_and_recipients(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'screen.png'; p.write_bytes(b'png')
   body=email_payload('slot','text',p,'demo@example.org')
   self.assertEqual(body['to'],['rahuljalan23.rj@gmail.com','abhinav.saxena1730@gmail.com','vig6604@gmail.com'])
   self.assertEqual(body['attachments'][0]['filename'],'smartmeet-demo.png')
   with self.assertRaises(ValueError): email_payload('slot','text',Path(d)/'secrets.env','demo@example.org')

from unittest.mock import patch
from types import SimpleNamespace
import agent, os
class PipelineTests(unittest.TestCase):
 def pipeline(self,d,send=True,review=None,mail=None,responses=None,attempts=1):
  def capture(*args,**kw):
   data=json.loads(kw['input']);folder=Path(data['out']);(folder/'evidence.json').write_text(json.dumps({'feature_id':data['feature']['id'],'observed':'Demo UI'}));(folder/'screenshot.png').write_bytes(b'png');return SimpleNamespace(returncode=0)
  feature={**FEATURE,'enabled':True}
  with patch.dict(os.environ,{'AGENT_STATE_DIR':d,'OPENROUTER_API_KEY':'fake','RESEND_API_KEY':'fake','EMAIL_FROM':'demo@example.org','MAX_DRAFT_ATTEMPTS':str(attempts)}),patch.object(agent.json,'loads',wraps=json.loads),patch.object(agent.subprocess,'run',side_effect=capture),patch.object(agent,'hermes',side_effect=responses or [DRAFT,review or {'approved':True,'unsupported_claims':[]}]),patch.object(agent,'request_json',side_effect=mail) as req,patch.object(agent,'choose_feature',return_value=feature):
   result=agent.run(send,slot='controlled');return result,req.call_args_list
 def test_controlled_send_and_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   result,calls=self.pipeline(d,mail=lambda *a:{'id':'mail-1'});self.assertEqual(result['status'],'sent');self.assertEqual(calls[0].args[1]['to'],agent.RECIPIENTS)
   result,calls=self.pipeline(d);self.assertEqual(result['status'],'already_reserved');self.assertEqual(calls,[])
 def test_concurrent_run_returns_without_inference(self):
  import fcntl
  with tempfile.TemporaryDirectory() as d:
   with (Path(d)/'run.lock').open('w') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    self.assertEqual(self.pipeline(d)[0]['status'],'already_running')
 def test_second_free_attempt_can_recover_rejected_first_draft(self):
  with tempfile.TemporaryDirectory() as d:
   replies=[DRAFT,{'approved':False,'unsupported_claims':['invented']},DRAFT,{'approved':True,'unsupported_claims':[]}]
   result,calls=self.pipeline(d,responses=replies,attempts=2,mail=lambda *a:{'id':'recovered'})
   self.assertEqual(result['status'],'sent');self.assertEqual(len(calls),1)
   attempts=json.loads((Path(d)/'controlled'/'attempts.json').read_text());self.assertEqual([a['accepted'] for a in attempts],[False,True])
   for a in attempts:free_model(a['writer']);free_model(a['reviewer'])
 def test_rejected_claim_feedback_reaches_next_writer(self):
  with tempfile.TemporaryDirectory() as d:
   seen=[];replies=iter([DRAFT,{'approved':False,'unsupported_claims':['Do not assert a customer already scheduled a meeting.']},DRAFT,{'approved':True,'unsupported_claims':[]}])
   def model(payload):seen.append(payload);return next(replies)
   self.pipeline(d,responses=model,attempts=2,mail=lambda *a:{'id':'corrected'})
   self.assertIn('Do not assert a customer already scheduled a meeting.',seen[2]['feedback'])
 def test_rejected_review_never_sends(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):self.pipeline(d,review={'approved':False,'unsupported_claims':['invented']})
   self.assertEqual(State(Path(d)/'state.db').db.execute('SELECT status FROM runs').fetchone()[0],'failed')
 def test_ambiguous_delivery_not_retried(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(TimeoutError):self.pipeline(d,mail=TimeoutError())
   self.assertEqual(State(Path(d)/'state.db').db.execute('SELECT status FROM runs').fetchone()[0],'delivery_unknown')
   self.assertEqual(self.pipeline(d)[0]['status'],'already_reserved')
 def test_preview_promotes_without_regeneration(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(self.pipeline(d,send=False)[0]['status'],'preview')
   self.assertEqual(self.pipeline(d,mail=lambda *a:{'id':'mail-2'})[0]['status'],'sent')
 def test_failed_slot_can_retry(self):
  with tempfile.TemporaryDirectory() as d:
   s=State(Path(d)/'state.db');s.reserve('x','setup');s.status('x','failed');self.assertTrue(s.reserve('x','setup'))
 def test_duplicate_rejected_again_on_retry(self):
  with tempfile.TemporaryDirectory() as d:
   old=Path(d)/'older';old.mkdir();(old/'draft.json').write_text(json.dumps(DRAFT))
   for attempt in range(2):
    with self.assertRaises(ValueError):self.pipeline(d,mail=lambda *a:{'id':'must-not-send'})

class WorkerTests(unittest.TestCase):
 def test_isolated_hermes_transport_and_tools(self):
  import importlib.util,io,types,contextlib
  spec=importlib.util.spec_from_file_location('marketing_worker',agent.ROOT/'src/hermes_worker.py');worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
  instances=[]
  class FakeAgent:
   def __init__(self,**kwargs):self.kwargs=kwargs;self.tools=[];instances.append(self)
   def run_conversation(self,*args,**kwargs):
    self.asserted=(self._disable_streaming,self._api_max_retries);return {'final_response':json.dumps(DRAFT)}
  loader=types.SimpleNamespace(load_hermes_dotenv=lambda **kwargs:None)
  with patch.dict(sys.modules,{'hermes_cli':types.SimpleNamespace(env_loader=loader),'run_agent':types.SimpleNamespace(AIAgent=FakeAgent)}),patch.dict(os.environ,{'OPENROUTER_API_KEY':'fake'}),patch.object(sys,'stdin',io.StringIO(json.dumps({'model':'openrouter/free','mode':'write'}))),contextlib.redirect_stdout(io.StringIO()) as output:
   worker.main()
  self.assertEqual(json.loads(output.getvalue()),DRAFT);self.assertEqual(instances[0].asserted,(True,1));self.assertEqual(instances[0].kwargs['enabled_toolsets'],[]);self.assertIsNone(instances[0].kwargs['fallback_model']);self.assertTrue(instances[0].kwargs['skip_context_files'])

class TransportTests(unittest.TestCase):
 def test_provider_request_identifies_agent(self):
  import io
  class Reply(io.BytesIO):
   def __enter__(self):return self
   def __exit__(self,*args):self.close()
  with patch.object(agent.urllib.request,'urlopen',return_value=Reply(b'{"id":"controlled"}')) as opened:
   agent.request_json('https://example.invalid',{},{});request=opened.call_args.args[0]
   self.assertEqual(request.get_header('User-agent'),'SmartMeet-Marketing/1.0')

class ModelResponseTests(unittest.TestCase):
 def test_complete_json_fences_are_supported_without_scanning_prose(self):
  from hermes_worker import parse_model_json
  value={'approved':True,'unsupported_claims':[],'reason':'Verified against the supplied UI.'}
  for raw in [json.dumps(value),'```json\n'+json.dumps(value)+'\n```','```\n'+json.dumps(value)+'\n```']:
   self.assertEqual(parse_model_json(raw),value)
  for raw in ['Here is JSON: '+json.dumps(value),'[]','```json\n{}', '{}\nextra']:
   with self.assertRaises(ValueError):parse_model_json(raw)
 def test_unmeasured_number_word_timings_are_rejected(self):
  with self.assertRaises(ValueError):validate_draft({**DRAFT,'problem':'The first ten minutes become a scramble to align.'},FEATURE)
