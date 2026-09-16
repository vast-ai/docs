#!/usr/bin/env python3
"""Independent final comparison with the signed pre-batch Git snapshot."""
import collections, datetime, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
N=Path(__file__).resolve().parent
BASE='61fbb472fadd1c9242a34fae14b67ddf0eb3f376'
def sha(b): return hashlib.sha256(b).hexdigest()
def read(ref): return (ROOT/ref).read_bytes()
def old(ref): return subprocess.check_output(['git','show',BASE+':'+ref],cwd=ROOT)
def index(m): return {c['id']:c for p in m['pages'] for c in p['claims']}
def omit(o,ks): return {k:v for k,v in o.items() if k not in ks}
def load(ref): return json.loads(read(ref))
modelref='verification/current-host-docs-review.json'
regref='verification/current-host-evidence-reuse-review.json'
before=json.loads(old(modelref));model=load(modelref);registry=load(regref)
prior=index(before);claims=index(model);scope={t['claim_id'] for t in registry['transitions']}
assert len(scope)==318 and len(registry['transitions'])==318
assert set(prior)==set(claims) and len(claims)==2008
assert model['counts']['claim_statuses']==dict(BLOCKED=21,FAIL=3,NOT_APPLICABLE=91,PASS=1042,UNVALIDATED=851)
relocated=[];corrections=[]
for cid,c in claims.items():
 p=prior[cid]
 if cid not in scope:
  assert omit(c,['spans'])==omit(p,['spans']),cid
  if c['spans']!=p['spans']: relocated.append(cid)
 if c['text']!=p['text']:corrections.append(cid)
 for field in ['evidence_refs','source_refs']:
  assert all(e in c[field] for e in p[field]),(cid,field)
 assert omit(c.get('history',{}),['evidence_reuse_review'])==p.get('history',{}),cid
assert len(corrections)==47
for lane in ['a-policy-account','b-hardware-install','c-operations-verification']:
 for d in json.loads((N/lane/'decisions.json').read_text())['decisions']:
  assert claims[d['id']]['status']==d['proposed_status'],d['id']
  if d['decision']=='correction': assert claims[d['id']]['text']==d['proposed_replacement'],d['id']
for path in ['b-hardware-install/adjacent-proposals.json','duplicate-diagnostic-proposals.json']:
 for d in json.loads((N/path).read_text())['proposals']:
  assert claims[d['id']]['text']==d['proposed_replacement'],d['id']
flat=lambda m:[v for p in m['pages'] for q in p['procedures'] for v in [q,*q['nodes']]]
a,b=flat(before),flat(model);assert len(a)==len(b)==1201
for p,c in zip(a,b):
 assert omit(p,['nodes','spans','coverage_state','history'])==omit(c,['nodes','spans','coverage_state','history']),p['id']
 assert omit(c.get('history',{}),['evidence_reuse_review'])==p.get('history',{}),p['id']
own='verification/current-host-owner-questions.json'
assert omit(load(own),['model_sha256'])==omit(json.loads(old(own)),['model_sha256'])
assert load(own)['model_sha256']==sha(read(modelref))
assert sha(read('verification/current-host-source-family-review.json'))=='6502a30c0e3f27f2808239fdca61a0497d8efd7406a0c5af02fa76c58ffe544d'
amendment=json.loads((N/'root-owner-role-amendment.json').read_text())
for change in amendment['changes']:
 c=claims[change['id']]
 assert c['owner_role']=='Host Product/Engineering owner'
 canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
 assert sha(canonical(c))==change['after_claim_canonical_sha256']
 restored=dict(c,owner_role=change['before_owner_role'])
 assert sha(canonical(restored))==change['before_claim_canonical_sha256']
# Every prior durable evidence file remains byte-identical, including failures.
priorfiles=subprocess.check_output(['git','ls-tree','-r',BASE,'verification/evidence'],cwd=ROOT,text=True).splitlines()
for row in priorfiles:
 meta,ref=row.split('\t',1);blob=meta.split()[2];data=read(ref)
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob,ref
# The finite edits plus proven unchanged line mappings account for every source line.
for source in registry['sources']:
 assert read(source['before_artifact']['path'])==old(source['path']),source['path']
 assert sha(read(source['path']))==source['after_sha256']
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
report={'record_type':'ROOT_FINAL_INDEPENDENT_COMPARISON','state':'PASS','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':BASE,'model_sha256':sha(read(modelref)),'registry_sha256':sha(read(regref)),'checker_sha256':sha(Path(__file__).read_bytes()),'counts':model['counts']['claim_statuses'],'selected_claims':len(scope),'unselected_claims_preserved_except_spans':len(claims)-len(scope),'unselected_line_relocations':len(relocated),'literal_corrections':len(corrections),'procedure_and_node_records_preserved':len(a),'prior_evidence_files_preserved':len(priorfiles),'owner_questions_preserved':True,'prior_registry_unchanged':True,'limits':'Source/model and retained-history comparison. No new product runtime or human acceptance.'}
(N/'root-final-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
