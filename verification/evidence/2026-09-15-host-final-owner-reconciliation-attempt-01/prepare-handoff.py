from pathlib import Path
import json,hashlib,subprocess,datetime,platform,re,tempfile
ROOT=Path(__file__).resolve().parents[3];A=Path(__file__).parent;PREFIX=str(A.relative_to(ROOT))
BASE_REPO=Path('/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914');COMMIT='09212ce653938550097714529e5dd1677638e777'
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
encoded=lambda d:(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode()
def stats(name):
 s=(A/name).read_text();d={k:int(v) for k,v in re.findall(r'ℹ (tests|pass|fail) (\d+)',s)};assert set(d)=={'tests','pass','fail'},name;return d
assert stats('projector-tests-01.txt')=={'tests':3,'pass':3,'fail':0}
assert stats('reviewer-tests-01.txt')=={'tests':47,'pass':45,'fail':2}
assert stats('reviewer-retest-02.txt')=={'tests':4,'pass':2,'fail':2}
assert stats('reviewer-retest-03.txt')=={'tests':2,'pass':2,'fail':0}
assert stats('queue-tests-01.txt')=={'tests':13,'pass':13,'fail':0}
review_path=Path('/Users/hanneszietsman/VastAi/research/host-docs-meeting-20260914/reconciliation/continuation-final-owner-reconciliation-20260915/presentation-independent-review.json')
review=review_path.read_bytes();assert sha(review)=='011dd8d1b637db9c6740d8c2659c3772c4907e69a1d11fe75eb85158d2d524de';(A/'presentation-independent-review.json').write_bytes(review)
model=(ROOT/'verification/current-host-docs-review.json').read_bytes();registry=(ROOT/'verification/current-host-final-owner-review.json').read_bytes();html=(ROOT/'verification/host-docs-review.html').read_bytes()
export=json.loads((A/'export-check-01.txt').read_text());assert export['result']=='PASS' and export['html_sha256']==sha(html)
assert 'PASS' in (A/'generated-check-01.txt').read_text()
rows=subprocess.check_output(['git','-C',str(BASE_REPO),'ls-tree','-r','-z',COMMIT]).decode().split('\0');baseline={x.split('\t')[1]:x.split()[2] for x in rows if x}
paths=set(subprocess.check_output(['git','-C',str(ROOT),'ls-files','-c','-o','--exclude-standard','-z']).decode().split('\0'))-{''};paths.update(str(p.relative_to(ROOT)) for p in A.rglob('*') if p.is_file() and '__pycache__' not in p.parts);paths.discard(PREFIX+'/integration-handoff.json')
checked=[]
for ref in sorted(paths):
 if not ref.startswith(('scripts/','host/')):continue
 p=ROOT/ref
 if not p.is_file() or '__pycache__' in p.parts:continue
 raw=p.read_bytes()
 if baseline.get(ref)==blob(raw):continue
 old=subprocess.check_output(['git','-C',str(BASE_REPO),'show',COMMIT+':'+ref]) if ref in baseline else b''
 with tempfile.NamedTemporaryFile() as f:
  f.write(old);f.flush();result=subprocess.run(['git','diff','--no-index','--check','--',f.name,str(p)],capture_output=True,text=True)
 assert not result.stdout and not result.stderr and result.returncode in (0,1),(ref,result.returncode,result.stdout,result.stderr)
 checked.append(ref)
checks={'record_type':'FINAL_OWNER_FOCUSED_CHECKS','state':'PASS','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':COMMIT,'baseline_model_sha256':'fc76c7280e3b94ede14bd25e909e22eba7eff7f4c05996a081d31810df0335c7','model_sha256':sha(model),'registry_sha256':sha(registry),'unique_required_cases':64,'projector_cases':stats('projector-tests-01.txt'),'reviewer_cases':{'tests':48,'pass':48,'fail':0,'composition':'45 initial passes + owner payload corrected fixture pass in retest02 + citation corrected fixture and new immutable-tax popup passes in retest03. The malformed decoder retest was a duplicate; it adds no case.'},'queue_and_source_followups':stats('queue-tests-01.txt'),'generated_check':'PASS','export_check':export,'source_and_code_whitespace_check':{'state':'PASS','paths':checked,'scope':'Changed current MDX and code only; raw retained evidence/help/log whitespace is not rewritten.'},'independent_presentation_review':{'path':PREFIX+'/presentation-independent-review.json','sha256':sha(review)},'retained_initial_failures':{'reviewer-tests-01.txt':stats('reviewer-tests-01.txt'),'reviewer-retest-02.txt':stats('reviewer-retest-02.txt')},'fixture_corrections':['Current citation fixture now asserts zero citation FAILs and checks the two preserved prior tax FAILs.','Current owner-payload fixture expects eleven presentation questions and preserves all eight original owner objects.','The new historical-tax popup fixture supplies its own HTML escaping helper and checks exact before/current hashes and old displayed bytes.'],'logs':{p.name:{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in sorted(A.glob('*.txt'))},'environment':{'os':platform.platform(),'python':platform.python_version(),'node':subprocess.check_output(['node','--version'],text=True).strip()},'limits':['Source/projection and offline reviewer checks only; no Host,account,rental,boot,trust,GPU or payout actions.','Native browser verification,original checkout integration,signing andGraphify remain root responsibilities.']}
(A/'checks.json').write_bytes(encoded(checks));paths.add(PREFIX+'/checks.json');paths.add(PREFIX+'/presentation-independent-review.json')
files=[];removed=[]
for ref in sorted(paths|set(baseline)):
 p=ROOT/ref
 if not p.is_file():
  if ref in baseline:removed.append(ref)
  continue
 b=p.read_bytes()
 if ref in baseline and blob(b)==baseline[ref]:continue
 if ref.startswith('graphify-out/') or any(x in p.parts for x in ['node_modules','__pycache__']):raise ValueError('out-of-scope changed file '+ref)
 prev=subprocess.check_output(['git','-C',str(BASE_REPO),'show',COMMIT+':'+ref]) if ref in baseline else None
 files.append({'path':ref,'sha256':sha(b),'bytes':len(b),'before_sha256':sha(prev) if prev is not None else None})
assert not removed,removed
pres=A/'preservation.json';handoff={'record_type':'HOST_FINAL_OWNER_INTEGRATION_HANDOFF','state':'READY_FOR_ROOT_INTEGRATION_AND_BROWSER_REVIEW','prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':str(ROOT),'baseline_commit':COMMIT,'baseline_model_sha256':checks['baseline_model_sha256'],'model_sha256':sha(model),'registry_ref':'verification/current-host-final-owner-review.json','registry_sha256':sha(registry),'html_sha256':sha(html),'html_bytes':len(html),'checks':{'path':PREFIX+'/checks.json','sha256':sha((A/'checks.json').read_bytes())},'preservation':{'path':str(pres.relative_to(ROOT)),'sha256':sha(pres.read_bytes())},'public_batch':{'reviewed':11,'newly_resolved':11,'adjacent_already_pass_records':1,'transitions':12,'counted_wording_corrections':11,'adjacent_wording_corrections':1,'physical_source_edits':12,'corrected_claim_literals':12},'owner_presentation':{'original_objects_preserved':8,'current_publication_conflicts':3,'future_detail_questions':8,'current_wording_requires_answer':False},'counts':json.loads(model)['counts'],'files':files,'file_count':len(files),'changed_files':sum(x['before_sha256'] is not None for x in files),'new_files':sum(x['before_sha256'] is None for x in files),'removed_files':removed,'copy_handoff_itself_separately':PREFIX+'/integration-handoff.json','limits':['Original checkout,Git,Graphify and liveHost untouched by integrator.','Original policy assertions are not established by their scoped wording replacements. Three publication conflicts and eight future-detail questions remain useful follow-ups, not unanswered conditions on current wording.','All original owner objects,1201historical procedure/node outcomes,prior sealed records and345 image files remain unchanged except explicit source-span/history rebinding.']}
(A/'integration-handoff.json').write_bytes(encoded(handoff));print(json.dumps({k:v for k,v in handoff.items() if k not in ('files','limits','counts')},indent=2));print('handoff_sha256',sha((A/'integration-handoff.json').read_bytes()))
