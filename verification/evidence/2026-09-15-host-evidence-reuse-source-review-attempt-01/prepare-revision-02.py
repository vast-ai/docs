"""Prepare only the bounded second scope revision; application is a separate step."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;AR=str(A.relative_to(R));stage=A/'stage-312';stage.mkdir(exist_ok=True)
# Retain initial sealed registry, exact projector/test bytes and check/result artifacts.
for rel in ['verification/current-host-evidence-reuse-review.json','scripts/current_host_evidence_reuse_review.py','scripts/current_host_evidence_reuse_review.mjs','scripts/current-host-evidence-reuse-review.test.mjs']:
 target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copyfile(R/rel,target)
for name in ['integration-impact.json','procedure-context-comparison.json','integration-handoff.json']:
 if not (stage/name).exists():shutil.copyfile(A/name,stage/name)
# Original inventory/adjacent-scope/root acceptance/integration-scope/results/checks are not overwritten.
s=(A/'integrate.py').read_text()
s=s.replace("inv=read(AR+'/inventory.json');model=read('verification/current-host-docs-review.json');claims={c['id']:c for p in model['pages'] for c in p['claims']}","""inv=read(AR+'/inventory.json')
import importlib.util
spec=importlib.util.spec_from_file_location('sealed_predecessor',R/'scripts/current_host_source_family_review.py');predecessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(predecessor)
initial_registry=read(AR+'/stage-312/verification/current-host-evidence-reuse-review.json')
before_files={s['path']:(R/s['before_artifact']['path']).read_bytes() for s in initial_registry['sources']}
model=predecessor.project(R,frozen_source_overrides=before_files);claims={c['id']:c for p in model['pages'] for c in p['claims']}
""")
s=s.replace("assert sha((R/'verification/current-host-docs-review.json').read_bytes())==inv['baseline_model_sha256']","assert sha((json.dumps(model,indent=2,ensure_ascii=False)+'\\n').encode())==inv['baseline_model_sha256']")
s=s.replace("frozen={x['id']:x for x in [*inv['claims'],*expansion['claims']]}","""extra=read(AR+'/supplemental-scope-02.json')
for group in extra['groups']:
 assert sha((R/group['proposals_ref']).read_bytes())==group['proposals_sha256']
 for d in read(group['proposals_ref'])['proposals']:assert d['id'] not in decisions;decisions[d['id']]=d;families[d['id']]=group['source_family']
frozen={x['id']:x for x in [*inv['claims'],*expansion['claims'],*extra['claims']]}
inv['source_hashes'].update(extra['source_hashes'])""")
s=s.replace('assert len(decisions)==312','assert len(decisions)==318')
s=s.replace("raw=(R/ref).read_bytes();assert sha(raw)==inv['source_hashes'][ref]","raw=(A/'sources-before'/ref).read_bytes() if (A/'sources-before'/ref).exists() else (R/ref).read_bytes();assert sha(raw)==inv['source_hashes'][ref]")
s=s.replace("source_indexes={f:read(AR+'/'+f+'/sources.json')['sources'] for f in ['a-policy-account','b-hardware-install','c-operations-verification']};","source_indexes={f:read(AR+'/'+f+'/sources.json')['sources'] for f in ['a-policy-account','b-hardware-install','c-operations-verification']};source_indexes['cpu-policy']=read(AR+'/supplemental-scope-02.json')['policy_sources'];")
s=s.replace("for family in source_indexes:\n for name in ['decisions.json','sources.json']:bind(AR+'/'+family+'/'+name)","for family in ['a-policy-account','b-hardware-install','c-operations-verification']:\n for name in ['decisions.json','sources.json']:bind(AR+'/'+family+'/'+name)\nfor group in extra['groups']:bind(group['proposals_ref'],group['proposals_sha256'])\nfor name in ['supplemental-scope-02.json','duplicate-diagnostic-scope.json','root-supplemental-acceptance-02.json']:bind(AR+'/'+name)")
s=s.replace('integration-impact.json','integration-impact-02.json').replace('integration-scope.json','integration-scope-02.json').replace('procedure-context-comparison.json','procedure-context-comparison-02.json')
s=s.replace("'312 occurrences: 309 previously unvalidated plus two CPU diagnostic FAIL corrections and one adjacent AMD configuration correction.","'318 occurrences: 309 previously unvalidated, five adjacent diagnostic/configuration corrections and four unchanged-literal CPU policy residuals.")
s=s.replace("assert 'PENDING_ROOT_ACCEPTED_REGISTRY' in s;p.write_text(s.replace('PENDING_ROOT_ACCEPTED_REGISTRY',digest))","assert 'PENDING_REVISION_02_REGISTRY' in s;p.write_text(s.replace('PENDING_REVISION_02_REGISTRY',digest))")
(A/'integrate-02.py').write_text(s)
print('Prepared revision02 integration script; no source/model/active projector changes applied.')
