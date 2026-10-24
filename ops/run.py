#!/usr/bin/env python3
"""Load the protected JSON-quoted environment without shell evaluation."""
import json, os, sys
from pathlib import Path
for line in Path('/etc/smartmeet-marketing/agent.env').read_text().splitlines():
 if line.strip() and not line.startswith('#'):
  key,value=line.split('=',1);os.environ[key]=json.loads(value)
os.chdir(Path(__file__).resolve().parents[1]);os.execv('/usr/bin/python3',['python3','src/agent.py',*sys.argv[1:]])
