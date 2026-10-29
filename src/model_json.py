"""Strict JSON response parsing shared by marketing inference and checks."""
import json

def parse_model_json(raw):
 if not isinstance(raw,str) or len(raw)>64000:raise ValueError('Invalid model response size')
 text=raw.strip()
 if text.startswith('```'):
  lines=text.splitlines()
  if len(lines)<3 or lines[0] not in ('```','```json') or lines[-1]!='```':raise ValueError('Invalid JSON fence')
  text='\n'.join(lines[1:-1]).strip()
 try:output=json.loads(text)
 except json.JSONDecodeError as error:raise ValueError('Invalid model JSON') from error
 if not isinstance(output,dict):raise ValueError('Expected JSON object')
 return output

