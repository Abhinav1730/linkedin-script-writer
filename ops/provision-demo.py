#!/usr/bin/env python3
"""Create only the explicitly authorized ordinary demo identity. No mail/providers."""
import json,urllib.request,urllib.error
from pathlib import Path
config=dict(line.split('=',1) for line in Path('/etc/smartmeet-marketing/agent.env').read_text().splitlines() if line and not line.startswith('#'))
config={k:json.loads(v) for k,v in config.items()}
assert config['DEMO_EMAIL']=='marketing-demo@smartmeet.invalid'
body={'name':'SmartMeet Marketing Demo','email':config['DEMO_EMAIL'],'password':config['DEMO_PASSWORD'],'phone':'00000000002410'}
base='http://127.0.0.1:4482/api/auth/'
def request(path,data):
 req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as res:return json.load(res)
try:value=request('register',body)
except urllib.error.HTTPError as error:
 if error.code!=409:raise
 value=request('login',{'email':body['email'],'password':body['password']})
assert value['user']['name']==body['name']
print('Dedicated demo account ready; credentials remain in protected configuration.')
