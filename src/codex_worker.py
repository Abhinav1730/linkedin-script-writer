"""Tool-free Codex app-server turn authenticated by the existing ChatGPT sign-in."""
import json, os, re, selectors, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from prompts import rules_for
from model_json import parse_model_json

DISABLED = {
 'shell_tool','unified_exec','code_mode','code_mode_host','apps','plugins','remote_plugin',
 'multi_agent','multi_agent_v2','browser_use','browser_use_external','browser_use_full_cdp_access',
 'computer_use','image_generation','view_image','sleep_tool','hooks','shell_snapshot',
 'in_app_browser','skill_search','tool_suggest','workspace_dependencies','realtime_conversation',
 'in_app_chat','in_app_local_automation','memories','daemon_auto_start',
}

def subscription_environment(source):
 return {k:v for k,v in source.items() if k in {'PATH','HOME','CODEX_HOME','LANG','SSL_CERT_FILE','SSL_CERT_DIR','HTTPS_PROXY','HTTP_PROXY','NO_PROXY'}}

def schema_for(mode):
 if mode == 'write':
  fields={k:{'type':'string'} for k in ['hook','problem','benefit','cta']}
  fields.update(claim_ids={'type':'array','items':{'type':'integer'}},hashtags={'type':'array','items':{'type':'string'}})
 elif mode == 'review':
  fields={'approved':{'type':'boolean'},'unsupported_claims':{'type':'array','items':{'type':'string'}},'reason':{'type':'string'}}
 else:raise ValueError('Unknown marketing stage')
 return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}

class Rpc:
 def __init__(self,process,timeout=100):
  self.process=process;self.deadline=time.monotonic()+timeout;self.buffer=b'';self.serial=0
  self.reply='';self.usage=None;self.completed=None;self.bytes=0
  self.selector=selectors.DefaultSelector();self.selector.register(process.stdout,selectors.EVENT_READ)
 def write(self,value):
  self.process.stdin.write((json.dumps(value)+'\n').encode());self.process.stdin.flush()
 def read(self):
  while b'\n' not in self.buffer:
   remaining=self.deadline-time.monotonic()
   if remaining<=0 or not self.selector.select(remaining):raise TimeoutError('Codex turn timed out')
   data=os.read(self.process.stdout.fileno(),65536)
   if not data:raise RuntimeError('Codex ended before completion')
   self.bytes+=len(data)
   if self.bytes>2_000_000:raise RuntimeError('Codex response too large')
   self.buffer+=data
  line,self.buffer=self.buffer.split(b'\n',1)
  return json.loads(line)
 def handle(self,message):
  if 'id' in message and 'method' in message:
   self.write({'id':message['id'],'error':{'code':-32601,'message':'Tools are disabled for marketing inference.'}})
   raise RuntimeError('Unexpected Codex tool or approval request')
  method=message.get('method');params=message.get('params',{});item=params.get('item')
  if item and item.get('type') not in {'agentMessage','reasoning','userMessage'}:
   raise RuntimeError('Unexpected Codex tool activity')
  if method=='item/completed' and item and item.get('type')=='agentMessage':self.reply=item.get('text','')
  if method=='thread/tokenUsage/updated':
   usage=params.get('tokenUsage',{}).get('last',{})
   if all(type(usage.get(k)) is int and usage[k]>=0 for k in ['inputTokens','outputTokens']):self.usage=usage
  if method=='turn/completed':self.completed=params.get('turn',{}).get('status')
 def call(self,method,params):
  self.serial+=1;serial=self.serial;self.write({'id':serial,'method':method,'params':params})
  while True:
   message=self.read()
   if message.get('id')==serial and 'method' not in message:
    if 'error' in message:raise RuntimeError('Codex app-server rejected '+method)
    return message.get('result',{})
   self.handle(message)
 def close(self):self.selector.close()

def generate(payload):
 schema=schema_for(payload.get('mode'));env=subscription_environment(os.environ)
 executable=os.environ.get('MARKETING_CODEX_BIN') or shutil.which('codex')
 if not executable:raise RuntimeError('Codex executable unavailable')
 def inspect(args):
  result=subprocess.run([executable,*args],env=env,capture_output=True,text=True,timeout=15)
  if result.returncode:raise RuntimeError('Codex preflight failed')
  return result.stdout
 version=inspect(['--version']).strip()
 if version!='codex-cli 0.164.0':raise RuntimeError('Codex version needs acceptance before use')
 features={line.split()[0] for line in inspect(['features','list']).splitlines() if line.split()}
 inventory=json.loads(inspect(['mcp','list','--json']))
 names=[entry['name'] for entry in inventory] if isinstance(inventory,list) else list(inventory)
 if any(not re.fullmatch(r'[-a-zA-Z0-9_]+',name) for name in names):raise RuntimeError('Unexpected MCP name')
 args=[]
 for name in names:args+=['-c','mcp_servers.'+name+'.enabled=false']
 for feature in sorted(DISABLED & features):args+=['--disable',feature]
 for setting in ['web_search="disabled"','project_doc_max_bytes=0','include_environment_context=false','include_apps_instructions=false','skills.include_instructions=false']:
  args+=['-c',setting]
 process=None;rpc=None
 with tempfile.TemporaryDirectory(prefix='marketing-codex-') as cwd:
  try:
   process=subprocess.Popen([executable,*args,'app-server','--listen','stdio://'],cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=0)
   rpc=Rpc(process)
   rpc.call('initialize',{'clientInfo':{'name':'smartmeet_marketing','title':'SmartMeet marketing drafts','version':'1.0'},'capabilities':{'experimentalApi':True}})
   rpc.write({'method':'initialized'})
   account=rpc.call('account/read',{'refreshToken':False})
   if account.get('account',{}).get('type')!='chatgpt':raise RuntimeError('ChatGPT subscription sign-in required')
   request={'cwd':cwd,'modelProvider':'openai','environments':[],'ephemeral':True,'approvalPolicy':'never','sandbox':'read-only','dynamicTools':[],'baseInstructions':rules_for(payload)}
   model=payload.get('model','subscription-default')
   if model!='subscription-default':
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',model):raise ValueError('Invalid Codex model')
    request['model']=model
   thread=rpc.call('thread/start',request)
   if thread.get('modelProvider')!='openai':raise RuntimeError('Unexpected model provider')
   rpc.call('turn/start',{'threadId':thread['thread']['id'],'environments':[],'runtimeWorkspaceRoots':[],'effort':'low','input':[{'type':'text','text':json.dumps(payload),'text_elements':[]}],'outputSchema':schema})
   while rpc.completed is None:rpc.handle(rpc.read())
   if rpc.completed!='completed':raise RuntimeError('Codex turn did not complete')
   if rpc.usage is None:
    rpc.deadline=min(rpc.deadline,time.monotonic()+0.5)
    try:
     while rpc.usage is None:rpc.handle(rpc.read())
    except TimeoutError:pass
   if rpc.usage is None:raise RuntimeError('Subscription token usage unavailable')
   output=parse_model_json(rpc.reply)
   return {'output':output,'runtime':{'provider':'codex-subscription','auth':'chatgpt','model':thread.get('model'),'version':version,'input_tokens':rpc.usage['inputTokens'],'output_tokens':rpc.usage['outputTokens']}}
  finally:
   if rpc:rpc.close()
   if process:
    process.terminate()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:process.kill();process.wait()

if __name__=='__main__':
 try:print(json.dumps(generate(json.load(sys.stdin))))
 except Exception as error:
  print(json.dumps({'error_type':type(error).__name__,'reason':str(error) if isinstance(error,(RuntimeError,TimeoutError,ValueError)) else 'Codex subscription worker failed'}),file=sys.stderr);sys.exit(1)
