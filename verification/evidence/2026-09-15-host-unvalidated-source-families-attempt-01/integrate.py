"""Apply the root-accepted bounded source review through the existing sealed convention."""
from pathlib import Path
import json,hashlib,copy,difflib,datetime,re,sys
R=Path(__file__).resolve().parents[3]; A=Path(__file__).resolve().parent; AR=str(A.relative_to(R))
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
oh=lambda v:sha(canon(v).encode())
read=lambda p:json.loads((R/p).read_text())
inv=read(AR+'/inventory.json');model=read('verification/current-host-docs-review.json');claims={c['id']:c for p in model['pages'] for c in p['claims']}
assert sha((R/'verification/current-host-docs-review.json').read_bytes())==inv['baseline_model_sha256']
assert oh(model)==read(AR+'/integration-baseline.json')['baseline_model_canonical_sha256']
decisions={};families={};contexts=[]
for family in ['s1','s2-s3','s4-s5']:
 data=read(AR+'/'+family+'/decisions.json')
 for d in data['decisions']:
  assert d['id'] not in decisions;decisions[d['id']]=d;families[d['id']]=family
 contexts+=data.get('context_corrections',[])
assert set(decisions)=={d['id'] for d in inv['claims']} and len(decisions)==358
accepted=read(AR+'/root-source-review-acceptance.json')['accepted_families']
for f in ['s1','s2-s3']:assert sha((A/f/'decisions.json').read_bytes())==accepted[f]['decisions_sha256']
assert sha((A/'s4-s5/decisions.json').read_bytes())=='09e7abd41100fb1781e880ca9aadc2c46b0d1beb4aded4fa3b1e34c73c1a2c26'
changes={};replacement_spans={}
for cid,d in decisions.items():
 c=claims[cid];assert c['status']=='UNVALIDATED' and sha(c['text'].encode())==d.get('literal_sha256',d.get('current_literal_sha256'))
 if d['decision']!='correction':continue
 replacement=d.get('proposed_replacement',d.get('full_replacement',d.get('replacement')));assert isinstance(replacement,str) and replacement!=c['text'];assert len(c['spans'])==1
 s=c['spans'][0];changes.setdefault(s['source_file'],[]).append({'id':cid,'start':s['start'],'end':s['end'],'before':c['text'],'after':replacement})
for c in contexts:
 assert c['page']=='host/optimization-guide.mdx' and c['line']==34
 changes.setdefault(c['page'],[]).append({'id':None,'start':c['line'],'end':c['line'],'before':c['current'],'after':c['replacement']})
sources=[];texts={};maps={};oldtexts={}
for ref,edits in sorted(changes.items()):
 raw=(R/ref).read_bytes();assert sha(raw)==inv['source_hashes'][ref];old=raw.decode().splitlines();new=[];cursor=0
 for e in sorted(edits,key=lambda e:e['start']):
  assert cursor<e['start'];assert '\n'.join(old[e['start']-1:e['end']])==e['before'];new+=old[cursor:e['start']-1];first=len(new)+1;new+=e['after'].splitlines();last=len(new);cursor=e['end']
  if e['id']:replacement_spans[e['id']]=[{'source_file':ref,'start':first,'end':last,'text_sha256':sha(e['after'].encode())}]
 new+=old[cursor:];texts[ref]='\n'.join(new)+'\n';oldtexts[ref]=raw
 line_map=[];diffs=[]
 for op,a,z,b,y in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
  if op=='equal':line_map.extend([[a+i+1,b+i+1] for i in range(z-a)])
  else:diffs.append({'before_start':a+1,'before_end':z,'after_start':b+1,'after_end':y})
 maps[ref]=dict(line_map);sources.append({'path':ref,'before_artifact':{'path':AR+'/sources-before/'+ref,'sha256':sha(raw)},'after_sha256':sha(texts[ref].encode()),'line_map':line_map,'edits':diffs})
def relocate(s):
 if s['source_file'] not in maps:return copy.deepcopy(s)
 values=[maps[s['source_file']].get(i) for i in range(s['start'],s['end']+1)]
 if None in values or values!=list(range(values[0],values[-1]+1)):return None
 return {**s,'start':values[0],'end':values[-1]}
affected=[]
for page in model['pages']:
 for p in page['procedures']:
  for n in [p,*p['nodes']]:
   if any(relocate(s) is None for s in n.get('spans',[])):
    affected.append({'id':n['id'],'status':n['status'],'spans':n.get('spans',[]),'title':n.get('title',n.get('label')),'node_keys':list(n)})
impact={'record_type':'BOUNDED_SOURCE_FAMILY_INTEGRATION_IMPACT','literal_corrections':sum(d['decision']=='correction' for d in decisions.values()),'context_headers':len(contexts),'changed_sources':[s['path'] for s in sources],'affected_procedures':affected,'out_of_scope_overlaps':[]}
for cid,c in claims.items():
 if cid not in decisions and any(relocate(s) is None for s in c['spans']):impact['out_of_scope_overlaps'].append({'id':cid,'spans':c['spans']})
(A/'integration-impact.json').write_text(json.dumps(impact,indent=2)+'\n')
print(json.dumps({k:v for k,v in impact.items() if k!='affected_procedures'}))
if '--apply' not in sys.argv:raise SystemExit()
import importlib.util
spec=importlib.util.spec_from_file_location('prior',R/'scripts/current_host_closure_correction.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
source_index=read(AR+'/s1/sources.json')['sources'];artifacts={};transitions=[];scope={'decisions':{},'procedures':{}}
def bind(ref,wanted=None):
 raw=(R/ref).read_bytes();digest=sha(raw)
 if wanted:assert digest==wanted,(ref,digest,wanted)
 assert ref not in artifacts or artifacts[ref]==digest
 artifacts[ref]=digest;return raw
for f in ['s1/decisions.json','s1/sources.json','s2-s3/decisions.json','s4-s5/decisions.json','root-source-review-acceptance.json','root-s4-s5-acceptance.json','root-payout-publication-conflict.json']:
 bind(AR+'/'+f)
for cid,d in decisions.items():
 c=claims[cid];family=families[cid];basis=[];ev=copy.deepcopy(c['evidence_refs']);refs=copy.deepcopy(c['source_refs'])
 for b in d.get('source_refs',d.get('proofs',[])):
  meta=source_index[b['source']] if family=='s1' else b
  path=meta.get('path',meta.get('artifact_ref'));raw=bind(path,meta['sha256']);pointer=b['text_pointer'];excerpt=prior.selection(raw,pointer)
  expected=b.get('source_excerpt',b.get('excerpt'));expected=expected if isinstance(expected,str) else canon(expected)
  assert excerpt.rstrip('\n')==expected.rstrip('\n'),(cid,pointer)
  url=meta.get('source_url',meta.get('url'))
  if not url and meta.get('repository') and meta.get('repository_path'):url=f"https://github.com/{meta['repository']}/blob/{meta['revision']}/{meta['repository_path']}"
  kind=meta.get('source_kind','RETAINED_SOURCE_REVIEW');revision=meta.get('revision',meta.get('source_revision'))
  basis.append({'artifactRef':path,'text_pointer':pointer,'excerpt':excerpt,'sourceUrl':url,'sourceRevision':revision,'sourceKind':kind,'support_rationale':'Supports the scoped assertion described in the claim rationale; see retained source provenance.'})
  evidence={'id':'SOURCE-FAMILY-'+cid+'-'+str(len(basis)),'role':kind,'limit':'Exact retained selector; source/runtime boundary is stated in the passage review.','artifact_ref':path}
  if not any(e['artifact_ref']==path for e in ev):ev.append(evidence)
  sr={'repository':meta.get('repository','retained-primary-source'),'revision':revision or 'sha256:'+meta['sha256'],'path':url or path,'locator':pointer,'source_kind':kind}
  if sr not in refs:refs.append(sr)
 status=d.get('proposed_status','UNVALIDATED' if d['decision']=='residual' else 'PASS')
 text=d.get('proposed_replacement',d.get('full_replacement',d.get('replacement',c['text'])))
 methods=d.get('proposed_methods',d.get('proposed_required_methods',c['required_evidence_types']))
 limits=d.get('limitation',d.get('limits'));method_reason=d.get('method_rationale',d.get('method_change_rationale',''))
 action=d['next_action'] if d['decision']!='correction' else 'The accepted wording correction is applied. Re-review this assertion if its wording or pinned sources change; the stated evidence limits remain.'
 after={'text':text,'status':status,'classification':d.get('proposed_classification',c['classification']),'required_evidence_types':methods,'owner_role':c['owner_role'],'rationale':d['support_rationale'],'next_action':action,'evidence_refs':ev,'source_refs':refs,'coverage_state':'CHANGED'}
 if cid in replacement_spans:after['spans']=replacement_spans[cid]
 scope['decisions'][cid]={'fields_sha256':oh({k:after[k] for k in ['text','status','classification','required_evidence_types','owner_role']}),'method_rationale':method_reason}
 transitions.append({'claim_id':cid,'before_sha256':oh(c),'after':after,'decision':d['decision'],'method':'SCOPED_SOURCE_FAMILY_REVIEW','method_rationale':method_reason,'limits':limits,'basis':basis})
def inclusive_span(s):
 same=relocate(s)
 if same:return same
 source=next(x for x in sources if x['path']==s['source_file']);mapping=maps[s['source_file']]
 def boundary(n,start):
  if n in mapping:return mapping[n]
  e=next(e for e in source['edits'] if e['before_start']<=n<=e['before_end'])
  return e['after_start'] if start else e['after_end']
 first,last=boundary(s['start'],True),boundary(s['end'],False);assert first<=last
 return {**s,'start':first,'end':last,'text_sha256':sha('\n'.join(texts[s['source_file']].splitlines()[first-1:last]).encode())}
procedures=[];command_comparisons=[]
for pi,page in enumerate(model['pages']):
 for qi,q in enumerate(page['procedures']):
  for ni,n in enumerate([q,*q['nodes']]):
   if not any(relocate(s) is None for s in n.get('spans',[])):continue
   pointer=f'/pages/{pi}/procedures/{qi}'+(f'/nodes/{ni-1}' if ni else '')
   spans=[inclusive_span(s) for s in n['spans']]
   hist={**n.get('history',{}),'source_family_review':{'prior_spans':copy.deepcopy(n['spans']),'before_source_root':AR+'/sources-before/','reason':'Source/context correction only; existing status and evidence remain unchanged.'}}
   after={'spans':spans,'history':hist,'coverage_state':'CHANGED'}
   reason='Exact changed spans rebound to the corrected source; no execution or procedure status promotion.'
   patch={'id':n['id'],'model_pointer':pointer,'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'after':after,'reason':reason}
   procedures.append(patch);scope['procedures'][pointer]={'after':after,'reason':reason}
   if n['status']=='PASS':
    assert n['id']=='ERR-T05-B02-S01'
    def commands(s,new):
     content=texts[s['source_file']] if new else oldtexts[s['source_file']].decode()
     found=[]
     for match in re.finditer(r'^```[^\n]*\n([\s\S]*?)^```',content,re.M):
      first=content[:match.start()].count('\n')+1;last=content[:match.end()].count('\n')+1
      if first<=s['end'] and last>=s['start']:found.append(match.group(1))
     return found
    oldcommands=[b for s in n['spans'] for b in commands(s,False)];newcommands=[b for s in spans for b in commands(s,True)]
    assert oldcommands and oldcommands==newcommands
    command_comparisons.append({'id':n['id'],'model_pointer':pointer,'status_unchanged':'PASS','before_spans':n['spans'],'after_spans':spans,'executed_fences_sha256':[sha(x.encode()) for x in oldcommands],'command_bytes_unchanged':True,'limit':'Context narrowed; retained command collection proof only. No new runtime check or recovery proof.'})
assert len(procedures)==43 and len(command_comparisons)==1
(A/'procedure-context-comparison.json').write_text(json.dumps({'comparisons':command_comparisons,'all_43_statuses_and_evidence_unchanged':True},indent=2)+'\n');bind(AR+'/procedure-context-comparison.json')
for source in sources:
 p=R/source['before_artifact']['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(oldtexts[source['path']])
 (R/source['path']).write_text(texts[source['path']])
amendment=read(AR+'/owner-context-amendment.json');owner=read(amendment['before_artifact']['path'])
owner['questions']=[copy.deepcopy(amendment['after']) if q['id']==amendment['question_id'] else q for q in owner['questions']]
(R/'verification/current-host-owner-questions.json').write_text(json.dumps(owner,indent=2,ensure_ascii=False)+'\n')
(A/'integration-scope.json').write_text(json.dumps(scope,separators=(',',':'),ensure_ascii=False)+'\n')
registry={'schema_version':'1.0','record_type':'HOST_SOURCE_FAMILY_REVIEW','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':{'path':AR+'/integration-scope.json','sha256':sha((A/'integration-scope.json').read_bytes())},'sources':sources,'artifacts':[{'path':p,'sha256':h} for p,h in sorted(artifacts.items())],'transitions':transitions,'procedures':procedures,'limits':'358 frozen occurrences: source-defined behavior, dated primary guidance, bounded retained observations and static recommendations only. No induced failures, new host runs, deployment qualification, full procedure acceptance or human approval. Two CPU implementation/policy conflicts remain FAIL; AutoSort and badbandwidthtest2 remain explicit UNVALIDATED source follow-ups. All prior findings and evidence are preserved.'}
rp=R/'verification/current-host-source-family-review.json';rp.write_text(json.dumps(registry,separators=(',',':'),ensure_ascii=False)+'\n');digest=sha(rp.read_bytes())
for ref in ['scripts/current_host_source_family_review.py','scripts/current_host_source_family_review.mjs']:
 p=R/ref;s=p.read_text();assert 'PENDING_ROOT_ACCEPTED_REGISTRY' in s;p.write_text(s.replace('PENDING_ROOT_ACCEPTED_REGISTRY',digest))
print(json.dumps({'registry_sha256':digest,'registry_bytes':rp.stat().st_size,'scope_bytes':(A/'integration-scope.json').stat().st_size,'transitions':len(transitions),'procedures':len(procedures),'statuses':dict(__import__('collections').Counter(t['after']['status'] for t in transitions))}))
