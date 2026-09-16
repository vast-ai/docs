from pathlib import Path
import json,hashlib,subprocess,datetime,platform,re
ROOT=Path(__file__).resolve().parents[3];A=Path(__file__).parent;PREFIX=str(A.relative_to(ROOT))
BASE_REPO=Path('/Users/hanneszietsman/VastAi/CON-1584/docs-pr185-closure-20260914');COMMIT='853d6610e91b2749f2dd8ea8fa7c19de072b9918'
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
encoded=lambda d:(json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode()
def stats(name):
 s=(A/name).read_text();d={k:int(v) for k,v in re.findall(r'ℹ (tests|pass|fail) (\d+)',s)};assert set(d)=={'tests','pass','fail'},name;return d
assert stats('focused-tests-03.log')=={'tests':55,'pass':54,'fail':1}
assert stats('queue-retest-05.log')=={'tests':10,'pass':10,'fail':0}
assert stats('reader-fixture-retest-03.log')=={'tests':20,'pass':20,'fail':0}
# Initial historical run's three failing Python source-view fixtures were
# rerun in the ten-test historical subset; all ten passed (the two failures
# in that combined log were old reader-copy fixtures, later20/20).
assert stats('historical-tests-01.log')=={'tests':22,'pass':19,'fail':3}
assert stats('fixture-retests-02.log')=={'tests':30,'pass':28,'fail':2}
log=(A/'fixture-retests-02.log').read_text();assert all(x=='host-review-reader-copy.test.mjs' for x in re.findall(r'^test at scripts/([^:]+):',log,re.M))
model=(ROOT/'verification/current-host-docs-review.json').read_bytes();registry=(ROOT/'verification/current-host-hardware-operator-review.json').read_bytes();html=(ROOT/'verification/host-docs-review.html').read_bytes()
export=json.loads((A/'export-check.log').read_text());assert export['result']=='PASS' and export['html_sha256']==sha(html)
assert 'PASS' in (A/'generated-check.log').read_text()
checks={'record_type':'HARDWARE_OPERATOR_FOCUSED_CHECKS','state':'PASS','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':COMMIT,'baseline_model_sha256':'794b1e3a7ba316d6c10de2f5f43b8838b5f6896be90b68f39050d4803ed258c0','model_sha256':sha(model),'registry_sha256':sha(registry),'required_unique_tests':106,'current_focused_tests':{'tests':64,'pass':64,'fail':0,'components':[{'log':'focused-tests-03.log','passed_tests':54,'remaining':'Queue file had a duplicate test-local variable; no queue cases ran.'},{'log':'queue-retest-05.log','passed_tests':10}]},'historical_projector_tests':{'tests':22,'pass':22,'fail':0,'initial_log':'historical-tests-01.log','corrected_fixture_retest_log':'fixture-retests-02.log'},'historical_reader_copy_tests':stats('reader-fixture-retest-03.log'),'generated_check':'PASS','export_check':export,'initial_failures_retained':{'focused-tests-01.log':stats('focused-tests-01.log'),'focused-tests-02.log':stats('focused-tests-02.log'),'historical-tests-01.log':stats('historical-tests-01.log'),'fixture-retests-02.log':stats('fixture-retests-02.log'),'focused-tests-03.log':stats('focused-tests-03.log'),'queue-retest-04.log':stats('queue-retest-04.log')},'corrections_during_checks':['Preserve the exact non-secret Bash prompt before credential masking and retain line positions for masked multiline values. A regression also checks a real credential on the next line.','Current review fixtures now use the new result, exact two resolved connection instructions,11workflow page groups and zero blocked-passage fallbacks; an explicit synthetic fallback still verifies unmapped BLOCKED handling.','Historical Python fixtures replay106before-source bytes and retain their older complete model/count expectations. Reader-copy historical assertions use their frozen2013 corpus and the exact cleanup calculator transition; the separate current export assertion retains null metadata.'],'logs':{p.name:{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in sorted(A.glob('*.log'))},'environment':{'os':platform.platform(),'python':platform.python_version(),'node':subprocess.check_output(['node','--version'],text=True).strip()},'limits':['Source/projection and offline reviewer checks only; no Host,account,rental,boot,trust or GPU actions.','The accepted credential evidence is the existing eight isolated synthetic-key macOS fixtures. No fixtures or Host workloads were rerun during integration.','Root owns actual browser review,original checkout integration,signing andGraphify.']}
(A/'checks.json').write_bytes(encoded(checks))
rows=subprocess.check_output(['git','-C',str(BASE_REPO),'ls-tree','-r','-z',COMMIT]).decode().split('\0');baseline={x.split('\t')[1]:x.split()[2] for x in rows if x}
paths=set(subprocess.check_output(['git','-C',str(ROOT),'ls-files','-c','-o','--exclude-standard','-z']).decode().split('\0'))-{''};paths.update(str(p.relative_to(ROOT)) for p in A.rglob('*') if p.is_file() and '__pycache__' not in p.parts);paths.discard(PREFIX+'/integration-handoff.json')
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
pres=A/'preservation.json';handoff={'record_type':'HOST_HARDWARE_OPERATOR_INTEGRATION_HANDOFF','state':'READY_FOR_ROOT_INTEGRATION_AND_BROWSER_REVIEW','prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':str(ROOT),'baseline_commit':COMMIT,'baseline_model_sha256':checks['baseline_model_sha256'],'model_sha256':sha(model),'registry_ref':'verification/current-host-hardware-operator-review.json','registry_sha256':sha(registry),'html_sha256':sha(html),'html_bytes':len(html),'checks':{'path':PREFIX+'/checks.json','sha256':sha((A/'checks.json').read_bytes())},'preservation':{'path':str(pres.relative_to(ROOT)),'sha256':sha(pres.read_bytes())},'public_batch':{'reviewed':106,'newly_resolved':105,'adjacent_already_pass_records':1,'transitions':107,'counted_wording_corrections':36,'adjacent_wording_corrections':1,'uncounted_heading_edits':1,'physical_source_edits':38,'corrected_claim_literals':37},'counts':json.loads(model)['counts'],'files':files,'file_count':len(files),'changed_files':sum(x['before_sha256'] is not None for x in files),'new_files':sum(x['before_sha256'] is None for x in files),'removed_files':removed,'copy_handoff_itself_separately':PREFIX+'/integration-handoff.json','limits':['Original checkout,Git,Graphify and liveHost untouched by integrator.','Pending final11 narrowing and owner-card changes are explicitly excluded.','Previous sealed records and 345 image files remain unchanged.']}
(A/'integration-handoff.json').write_bytes(encoded(handoff));print(json.dumps({k:v for k,v in handoff.items() if k not in ('files','limits','counts')},indent=2));print('handoff_sha256',sha((A/'integration-handoff.json').read_bytes()))
