from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;AR=str(A.relative_to(R));sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False);oh=lambda x:sha(canon(x).encode())
m=json.loads((R/'verification/current-host-docs-review.json').read_text());inv=json.loads((A/'inventory.json').read_text());assert sha((R/'verification/current-host-docs-review.json').read_bytes())==inv['baseline_model_sha256']
baseline={'baseline_model_sha256':inv['baseline_model_sha256'],'baseline_model_canonical_sha256':oh(m),'baseline_commit':inv['baseline_commit'],'claim_hashes':{c['id']:oh(c) for p in m['pages'] for c in p['claims']},'procedure_population_sha256':oh([p['procedures'] for p in m['pages']]),'counts':m['counts']}
(A/'integration-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n');basehash=sha((A/'integration-baseline.json').read_bytes());invhash=sha((A/'inventory.json').read_bytes())
# Keep original358 logic/guards; allow the successor to supply exact before bytes.
p=R/'scripts/current_host_source_family_review.py';s=p.read_text();s=s.replace('def project(root: Path):','def project(root: Path, frozen_source_overrides=None):').replace('    def read(ref): return pre.safe(root,ref).read_bytes()','    frozen_source_overrides = frozen_source_overrides or {}\n    def read(ref): return frozen_source_overrides.get(ref, pre.safe(root,ref).read_bytes())').replace('frozen_source_overrides={**before,OWNER:owner_before}','frozen_source_overrides={**frozen_source_overrides,**before,OWNER:owner_before}');p.write_text(s)
# Bounded next projection is the same sealed pattern, with owner objects unchanged.
for ext in ['py','mjs']:
 s=(R/f'scripts/current_host_source_family_review.{ext}').read_text()
 for old,new in [('current_host_source_family_review','current_host_evidence_reuse_review'),('current-host-source-family-review','current-host-evidence-reuse-review'),('SOURCE_FAMILY','EVIDENCE_REUSE'),('SourceFamily','EvidenceReuse'),('sourceFamily','evidenceReuse'),('source_family','evidence_reuse'),('source-family','evidence-reuse'),('HOST_SOURCE_FAMILY_REVIEW','HOST_EVIDENCE_REUSE_REVIEW'),('HOST-SOURCE-FAMILY-REVIEW-01','HOST-EVIDENCE-REUSE-REVIEW-01'),('2026-09-15-host-unvalidated-source-families-attempt-01','2026-09-15-host-evidence-reuse-source-review-attempt-01'),('6502a30c0e3f27f2808239fdca61a0497d8efd7406a0c5af02fa76c58ffe544d','PENDING_ROOT_ACCEPTED_REGISTRY'),('25652cd08b4f811ff09237def69ee2e6b699f241e4735919115ea7116554f841',invhash),('663f62b97a54c809a6516205583acf1a63d1866706d0c40296aacef4552ebd7b',basehash),('358 frozen evidence-reuse occurrences','312 frozen occurrences (309 review + 3 adjacent fixes)'),('===358','===312'),('==358','==312')]:s=s.replace(old,new)
 if ext=='mjs':
  s=s.replace("import {projectClosureCorrection} from './current_host_closure_correction.mjs';","import {projectSourceFamilyReview} from './current_host_source_family_review.mjs';")
  s=s.replace(",OWNER='verification/current-host-owner-questions.json'",'')
  s=s.replace(",OWNER_SHA='01482cf7725940c5d84f06774c886ee10c358837b532557f99b8a43de40dd5a5'",'')
  s=s.replace("ids=new Set(inventory.claims.map(c=>c.id));", "expansion=JSON.parse(pin(A+'/adjacent-scope.json',ADJACENT_SHA256)),frozenClaims=[...inventory.claims,...expansion.claims],ids=new Set(frozenClaims.map(c=>c.id));")
  s=s.replace('inventory.claims.length===312','inventory.claims.length===309&&expansion.claims.length===3')
  start=s.index(" const amendment=JSON.parse(pin(");end=s.index(" const artifacts=",start)
  s=s[:start]+" const historicalRead=ref=>before.get(ref)||read(ref),pre=projectSourceFamilyReview({read:historicalRead,exists}),baseline=pre.model,old=index(baseline);req(sha(serial(baseline))===baselineCheck.baseline_model_canonical_sha256,'complete predecessor differs from baseline');req(equal(Object.fromEntries([...old].map(([id,c])=>[id,sha(serial(c))])),baselineCheck.claim_hashes),'baseline claim inventory');req(sha(serial(baseline.pages.map(p=>p.procedures)))===baselineCheck.procedure_population_sha256,'baseline procedures');for(const c of frozenClaims)req(old.get(c.id).status===c.claim.status&&sha(old.get(c.id).text)===c.literal_sha256,'frozen literal drift');\n"+s[end:]
  s=s.replace("[A+'/owner-context-amendment.json',OWNER_SHA],", "[A+'/adjacent-scope.json',ADJACENT_SHA256],")
  s=s.replace("[amendment.before_artifact.path,amendment.before_artifact.sha256],",'')
  s=s.replace("const A=EVIDENCE_REUSE_ATTEMPT", "const ADJACENT_SHA256='PENDING_ADJACENT_SCOPE';\nconst A=EVIDENCE_REUSE_ATTEMPT")
  s=s.replace("'Sealed closure predecessor replayed with exact before-source bytes; all prior findings and evidence retained.'","'Sealed source-family predecessor replayed with exact before-source bytes; all prior findings and evidence retained.'")
  # New topic keys are accepted scope, not inferred from status.
  s=s.replace("req(entry.before_sha256===sha(serial(prior)),'claim predecessor '+id);", "req(entry.before_sha256===sha(serial(prior)),'claim predecessor '+id);req(equal(entry.residual_topic||null,decision.residual_topic||null),'unaccepted residual topic');")
 else:
  s=s.replace("'source_family_closure_predecessor'","'evidence_reuse_source_family_predecessor'")
  s=s.replace("'evidence_reuse_closure_predecessor'","'evidence_reuse_source_family_predecessor'")
  s=s.replace("'current_host_closure_correction.py'","'current_host_source_family_review.py'")
  s=s.replace("OWNER_AMENDMENT_SHA256 = '01482cf7725940c5d84f06774c886ee10c358837b532557f99b8a43de40dd5a5'\nOWNER = 'verification/current-host-owner-questions.json'", "ADJACENT_SHA256 = 'PENDING_ADJACENT_SCOPE'")
  s=s.replace('root=root.resolve();pre=prior_module()','root=root.resolve();pre=prior_module();utils=pre.prior_module()')
  s=s.replace('pre.safe(root,ref)','utils.safe(root,ref)').replace('pre.selection(artifacts[ref]','utils.selection(artifacts[ref]')
  s=s.replace("ids={c['id'] for c in inventory['claims']}","expansion=json.loads(pin(ATTEMPT+'/adjacent-scope.json',ADJACENT_SHA256))\n    frozen_claims=[*inventory['claims'],*expansion['claims']]\n    ids={c['id'] for c in frozen_claims}")
  s=s.replace("len(inventory['claims'])==312","len(inventory['claims'])==309 and len(expansion['claims'])==3")
  start=s.index("    amendment=json.loads(pin(");end=s.index("    artifacts=",start)
  s=s[:start]+"    baseline=pre.project(root,frozen_source_overrides={**frozen_source_overrides,**before})\n    req(objhash(baseline)==baseline_check['baseline_model_canonical_sha256'],'complete predecessor differs from baseline')\n    old=index(baseline)\n    req({cid:objhash(c) for cid,c in old.items()}==baseline_check['claim_hashes'],'baseline claim inventory')\n    req(objhash([p['procedures'] for p in baseline['pages']])==baseline_check['procedure_population_sha256'],'baseline procedures')\n    req(all(old[c['id']]['status']==c['claim']['status'] and sha(old[c['id']]['text'].encode())==c['literal_sha256'] for c in frozen_claims),'frozen literal drift')\n"+s[end:]
  s=s.replace("'Sealed closure predecessor replayed with exact before-source bytes; all prior findings and evidence retained.'","'Sealed source-family predecessor replayed with exact before-source bytes; all prior findings and evidence retained.'")
  s=s.replace("req(entry['before_sha256']==objhash(prior),'claim predecessor '+cid)","req(entry['before_sha256']==objhash(prior),'claim predecessor '+cid)\n        req(entry.get('residual_topic')==decision.get('residual_topic'),'unaccepted residual topic')")
 (R/f'scripts/current_host_evidence_reuse_review.{ext}').write_text(s)
print('prepared successor',basehash,invhash)
