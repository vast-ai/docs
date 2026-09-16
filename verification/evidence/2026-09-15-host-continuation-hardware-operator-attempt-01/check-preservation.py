from pathlib import Path
import json,hashlib,subprocess,collections
ROOT=Path(__file__).resolve().parents[3]
BASE_REPO=Path('/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914')
COMMIT='853d6610e91b2749f2dd8ea8fa7c19de072b9918'
A=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
omit=lambda d,*names:{k:v for k,v in d.items() if k not in names}
def previous(ref):return subprocess.check_output(['git','-C',str(BASE_REPO),'show',COMMIT+':'+ref])
raw=previous('verification/current-host-docs-review.json');assert sha(raw)=='794b1e3a7ba316d6c10de2f5f43b8838b5f6896be90b68f39050d4803ed258c0'
old=json.loads(raw);newraw=(ROOT/'verification/current-host-docs-review.json').read_bytes();new=json.loads(newraw)
index=lambda m:{c['id']:c for p in m['pages'] for c in p['claims']}
before,after=index(old),index(new);assert set(before)==set(after) and len(after)==2008
reg=json.loads((ROOT/'verification/current-host-hardware-operator-review.json').read_bytes());selected={x['claim_id'] for x in reg['transitions']};assert len(selected)==107
impact=json.loads((A/'integration-impact.json').read_bytes());hs={x['model_pointer']:x for x in impact['heading_metadata_changes']};assert len(hs)==11
unselected=0;procedure_counts=collections.Counter()
for pi,(p,q) in enumerate(zip(old['pages'],new['pages'])):
 assert len(p['claims'])==len(q['claims']) and len(p['procedures'])==len(q['procedures'])
 for ci,(b,c) in enumerate(zip(p['claims'],q['claims'])):
  pointer=f'/pages/{pi}/claims/{ci}';h=hs.get(pointer)
  assert b['id']==c['id'];assert omit(c['history'],'hardware_operator_review','hardware_operator_heading_rebind')==b['history']
  if h:
   assert c['headings']==h['after_headings'] and b['headings']==h['before_headings'];assert c['history'][h['history_key']]==h['history_value']
  else:assert c['headings']==b['headings']
  if c['id'] not in selected:
   assert omit(b,'spans','history','headings')==omit(c,'spans','history','headings');unselected+=1
  for key in ('evidence_refs','source_refs'):assert all(v in c[key] for v in b[key])
 for qi,(b,c) in enumerate(zip(p['procedures'],q['procedures'])):
  assert len(b['nodes'])==len(c['nodes'])
  for ni,(b1,c1) in enumerate([(b,c),*zip(b['nodes'],c['nodes'])]):
   pointer=f'/pages/{pi}/procedures/{qi}'+(f'/nodes/{ni-1}' if ni else '')
   assert omit(b1,'spans','history','coverage_state','headings','nodes')==omit(c1,'spans','history','coverage_state','headings','nodes'),pointer
   assert omit(c1.get('history',{}),'hardware_operator_review','hardware_operator_heading_rebind')==b1.get('history',{}),pointer
   h=hs.get(pointer)
   if h:assert c1['headings']==h['after_headings'] and c1['history'][h['history_key']]==h['history_value']
   else:assert c1.get('headings')==b1.get('headings')
   procedure_counts[c1['status']]+=1
assert unselected==1901 and sum(procedure_counts.values())==1201
owners_before=json.loads(previous('verification/current-host-owner-questions.json'));owners_after=json.loads((ROOT/'verification/current-host-owner-questions.json').read_bytes());assert omit(owners_before,'model_sha256')==omit(owners_after,'model_sha256');assert owners_after['model_sha256']==sha(newraw)
tracked=subprocess.check_output(['git','-C',str(BASE_REPO),'ls-tree','-r','-z',COMMIT]).decode().split('\0');trees={x.split('\t')[1]:x.split()[2] for x in tracked if x}
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
images=[];prior=[]
for ref,oid in trees.items():
 frozen=(ref.startswith('images/') or (ref.startswith('scripts/current_host_') and ref.endswith(('.py','.mjs')) and ref!='scripts/current_host_review_transition.mjs') or (ref.startswith('verification/current-host-') and ref.endswith('.json') and ref not in ('verification/current-host-docs-review.json','verification/current-host-owner-questions.json')))
 if frozen:
  b=(ROOT/ref).read_bytes();assert blob(b)==oid,ref
  (images if ref.startswith('images/') else prior).append({'path':ref,'sha256':sha(b)})
result={'record_type':'HARDWARE_OPERATOR_PRESERVATION','state':'PASS','baseline_commit':COMMIT,'baseline_model_sha256':sha(raw),'model_sha256':sha(newraw),'counts':new['counts']['claim_statuses'],'selected_transitions':107,'unselected_claims':unselected,'heading_only_unselected_claims':[x['id'] for x in hs.values() if x['kind']=='claim' and not x['selected']],'heading_metadata_bindings':11,'procedure_node_records_preserved':1201,'procedure_node_statuses':dict(procedure_counts),'owner_question_objects_unchanged':len(owners_after['questions']),'prior_projector_registry_files_unchanged':prior,'image_files_unchanged':len(images),'image_manifest_sha256':sha(canon(images).encode()),'limits':'Read-only comparison against signed175 Git bytes. No new Host/runtime checks; existing procedure outcomes and prior failures remain retained.'}
(A/'preservation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='prior_projector_registry_files_unchanged'}))
