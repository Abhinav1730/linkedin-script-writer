"""Source-owned editorial briefs; no trend or customer claims."""
import datetime as dt

PILLARS=[
 {'pillar':'user-value','screenshot_required':False,'direction':'Start with a recognizable user challenge. Explain why a verified SmartMeet capability might matter, with conditional benefits rather than promises.'},
 {'pillar':'practical-advice','screenshot_required':False,'direction':'Offer one actionable meeting or follow-up habit. Connect it naturally to a relevant verified SmartMeet capability. Make the advice useful even before the reader signs up.'},
 {'pillar':'modern-collaboration','screenshot_required':False,'direction':'Offer a perspective on intentional collaboration in digitally connected work. Discuss clarity, participation or follow-through as priorities. No claims about current news, adoption, prevalence or what all teams do.'},
 {'pillar':'audience-use-case','screenshot_required':False,'direction':'Describe a clearly hypothetical situation relevant to feature.audience. Show where a verified SmartMeet capability fits into their work and invite the reader to consider it.'},
 {'pillar':'feature-demo','screenshot_required':True,'direction':'Use the observed app evidence to demonstrate a verified capability, connecting it to a user need rather than narrating buttons.'},
]

def brief_for_slot(slot):
 try:
  stamp=dt.datetime.fromisoformat(slot)
  if stamp.tzinfo is None:raise ValueError('Slot timezone required')
  index=int(stamp.timestamp()//10800)
 except ValueError:
  import hashlib
  index=int.from_bytes(hashlib.sha256(slot.encode()).digest()[:4],'big')
 return dict(PILLARS[index%len(PILLARS)])
