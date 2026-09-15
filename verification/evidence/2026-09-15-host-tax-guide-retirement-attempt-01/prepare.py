#!/usr/bin/env python3
"""One finite authorized editorial removal; preserve the signed predecessor."""
import copy, hashlib, json, re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[3]; A=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda o:json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
oh=lambda o:sha(canon(o).encode())
def save(p,o): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def ref(p): return p.relative_to(R).as_posix()
def artifact(p):return {'path':ref(p),'sha256':sha(p.read_bytes())}
model=json.loads((R/'verification/current-host-docs-review.json').read_bytes())
assert sha((R/'verification/current-host-docs-review.json').read_bytes())=='8137ba5eff4e8d9f83266057ec08fa4a58c6f2d8a7ec543e7a9484aec0d7c817'
assert model['counts']['claims']==2008 and model['counts']['claim_statuses']=={'NOT_APPLICABLE':95,'PASS':1913}
page=next(p for p in model['pages'] if p['route']=='/host/guide-to-taxes'); claims={c['id']:c for p in model['pages'] for c in p['claims']}
faq='MCL-7b86589912c968bb';ids=[c['id'] for c in page['claims']]+[faq]
assert len(ids)==16
owners=json.loads((R/'verification/current-host-owner-questions.json').read_bytes());tax_owner=next(q for q in owners['questions'] if q['id']=='HQ-VAST-TAX-HANDLING')
save(A/'retired-records.json',{'record_type':'RETIRED_HOST_TAX_GUIDE','reason':'Removed at explicit user instruction following CON-1417 comment 34984; retirement is not validation or a new PASS.','baseline_commit':'7509cffe0e59409593fa78f12baff98028752f49','page':page,'faq_claim':claims[faq],'owner_question':tax_owner})
(A/'before-owner-questions.json').write_bytes((R/'verification/current-host-owner-questions.json').read_bytes())
instruction=Path('/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/reconciliation/tax-guide-removal-20260915/jira-instruction.json');(A/'instruction.json').write_bytes(instruction.read_bytes())
replacements={
 'MCL-e9c7af0148732c9b':'For payout timing, see [Host Payouts](/host/payment).',
 'MCL-335de916e219e04a':'Manage payouts from **Earnings** in the console.'}
changes={claims[cid]['spans'][0]['source_file']:[{'before':claims[cid]['text'],'after':txt}] for cid,txt in replacements.items()}
changes['host/common-host-questions.mdx']=[{'before':claims[faq]['text']+'\n','after':''}]
nav=(R/'docs.json').read_text();lines=nav.splitlines(keepends=True);needle='                    "host/guide-to-taxes",\n'
# Preserve current JSON formatting; only the accepted routes change.
navnew=nav.replace('              "host/earning",\n              "host/guide-to-taxes"','              "host/earning"')
assert navnew!=nav
navnew=navnew.replace('"source": "/guide-to-taxes",\n      "destination": "/host/guide-to-taxes"','"source": "/guide-to-taxes",\n      "destination": "/host/payment"')
anchor='    {\n      "source": "/documentation/host/:slug*",'
assert navnew.count(anchor)==1
navnew=navnew.replace(anchor,'    {\n      "source": "/host/guide-to-taxes",\n      "destination": "/host/payment"\n    },\n    {\n      "source": "/documentation/host/guide-to-taxes",\n      "destination": "/host/payment"\n    },\n'+anchor)
json.loads(navnew);changes['docs.json']=[{'before':nav,'after':navnew}]
changes['host/guide-to-taxes.mdx']=[]
sources=[];after={};before={}
for path,edits in changes.items():
 raw=(R/path).read_bytes();before[path]=raw
 dest=A/'sources-before'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 removed=path=='host/guide-to-taxes.mdx';text=raw.decode()
 for e in edits:assert text.count(e['before'])==1;(None)
 for e in edits:text=text.replace(e['before'],e['after'],1)
 after[path]=None if removed else text.encode()
 sources.append({'path':path,'before_artifact':artifact(dest),'after_sha256':None if removed else sha(after[path]),'removed':removed,'edits':edits})
def move(s):
 if s['source_file'] not in after:return copy.deepcopy(s)
 path=s['source_file'];assert after[path] is not None
 old=before[path].decode().splitlines();new=after[path].decode().splitlines();start,end=s['start'],s['end']
 assert sha('\n'.join(old[start-1:end]).encode())==s['text_sha256']
 if path=='host/common-host-questions.mdx':
  deleted=claims[faq]['spans'][0]['start'];assert not(start==end==deleted)
  start-=start>deleted;end-=end>=deleted
 text='\n'.join(new[start-1:end]);return {**s,'start':start,'end':end,'text_sha256':sha(text.encode())}
patches=[];procedure_patches=[];retire=set(ids)
for p in model['pages']:
 if p['route']==page['route']:continue
 for c in p['claims']:
  if c['id'] in retire:continue
  new=copy.deepcopy(c);new['spans']=[move(s) for s in c['spans']]
  if c['id'] in replacements:
   new['text']=replacements[c['id']];new['history']={**c.get('history',{}),'tax_guide_retirement':{'prior_text':c['text'],'before_claim_sha256':oh(c),'reason':'Remove the Tax Guide referral; retained payment/navigation assertion and PASS scope are unchanged.'}}
  assert '\n'.join('\n'.join((after.get(s['source_file']) or (R/s['source_file']).read_bytes()).decode().splitlines()[s['start']-1:s['end']]) for s in new['spans'])==new['text'] or new['text']==c['text']
  if new!=c:patches.append({'id':c['id'],'before_sha256':oh(c),'after':new,'text_changed':new['text']!=c['text']})
 for pi,proc in enumerate(p['procedures']):
  for ni,n in enumerate([proc,*proc['nodes']]):
   spans=[move(s) for s in n['spans']]
   if spans==n['spans']:continue
   oldtext='\n'.join('\n'.join((before.get(s['source_file']) or (R/s['source_file']).read_bytes()).decode().splitlines()[s['start']-1:s['end']]) for s in n['spans'])
   newtext='\n'.join('\n'.join((after.get(s['source_file']) or (R/s['source_file']).read_bytes()).decode().splitlines()[s['start']-1:s['end']]) for s in spans)
   fences=lambda t:re.findall(r'^```[^\n]*\n.*?^```',t,re.M|re.S)
   assert fences(oldtext)==fences(newtext)
   procedure_patches.append({'route':p['route'],'procedure_index':pi,'node_index':None if ni==0 else ni-1,'id':n['id'],'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'spans':spans,'fences_unchanged':True})
registry={'schema_version':'1.0','record_type':'HOST_TAX_GUIDE_RETIREMENT','generated_at':'2026-09-15T18:30:00Z','baseline_commit':'7509cffe0e59409593fa78f12baff98028752f49','baseline_model_sha256':sha((R/'verification/current-host-docs-review.json').read_bytes()),'baseline_canonical_sha256':oh(model),'sources':sources,'retired_route':page['route'],'retired_claim_ids':ids,'archive':artifact(A/'retired-records.json'),'before_owners':artifact(A/'before-owner-questions.json'),'instruction':artifact(A/'instruction.json'),'claims':patches,'procedures':procedure_patches,'retired_owner_ids':['HQ-VAST-TAX-HANDLING'],'limits':'Tax guidance was removed by editorial instruction, not established as policy. Sixteen passages are retired, with zero new validation credit. Historical source, claim, procedure and owner evidence remains archived. No Host operation, publication or merge is implied.'}
save(R/'verification/current-host-tax-guide-retirement.json',registry)
for path,data in after.items():
 if data is None:(R/path).unlink()
 else:(R/path).write_bytes(data)
print(json.dumps({'registry_sha256':sha((R/'verification/current-host-tax-guide-retirement.json').read_bytes()),'retired_ids':ids,'claim_patches':len(patches),'procedure_patches':len(procedure_patches)},indent=2))
