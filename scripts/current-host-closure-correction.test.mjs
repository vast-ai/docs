import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {projectClosureCorrection,loadClosureCorrection,CLOSURE_PATH,CLOSURE_SHA256} from './current_host_closure_correction.mjs';
import {loadCurrentHostReviewTransition} from './current_host_review_transition.mjs';
import {loadHostReviewOwnerQuestions} from './host_review_owner_questions.mjs';
const read=ref=>fs.readFileSync(new URL('../'+ref,import.meta.url)),exists=ref=>fs.existsSync(new URL('../'+ref,import.meta.url));
const registry=JSON.parse(read(CLOSURE_PATH)),projected=projectClosureCorrection({read,exists}),model=JSON.parse(read('verification/current-host-docs-review.json'));
const index=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),claims=index(model),before=index(JSON.parse(read(registry.baseline.path))),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const evidenceAttempt='verification/evidence/2026-09-14-host-unvalidated-evidence-attempt-02',evidenceInventory=JSON.parse(read(evidenceAttempt+'/inventory.json')),evidenceScope=JSON.parse(read(evidenceAttempt+'/integration-scope.json')),evidenceIds=new Set(evidenceScope.accepted_ids),evidenceOriginal=new Map(evidenceInventory.claims.map(item=>[item.claim.id,item.claim]));
const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;
const hashObject=value=>sha(JSON.stringify(canonical(value)));
function priorProcedureView(){const rows=structuredClone(model.pages.map(p=>p.procedures)),original=new Map(evidenceScope.affected_procedures.map(item=>[item.id,item.before]));for(const procedures of rows)for(const procedure of procedures)for(const node of [procedure,...procedure.nodes])if(original.has(node.id)){const id=node.id,children=node.nodes;for(const key of Object.keys(node))delete node[key];Object.assign(node,structuredClone(original.get(id)));if(children!==undefined)node.nodes=children;}return rows;}
// Resealing is test-only: this exercises selector/scope checks below the digest guard.
async function withRegistry(change){const edited=structuredClone(registry);change(edited);const bytes=Buffer.from(JSON.stringify(edited));const source=read('scripts/current_host_closure_correction.mjs').toString().replace(CLOSURE_SHA256,sha(bytes)).replace("'./current_host_payout_invoice_correction.mjs'",JSON.stringify(new URL('./current_host_payout_invoice_correction.mjs',import.meta.url).href));const module=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>module.projectClosureCorrection({read:ref=>ref===CLOSURE_PATH?bytes:read(ref),exists});}
test('Python/JavaScript project the same newest model and preserve original finding accounting',()=>{
 assert.deepEqual(projected.model,model);assert.deepEqual(loadCurrentHostReviewTransition({read,model,exists}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_closure_correction as m;print(json.dumps(m.project(Path.cwd())))"],{cwd:new URL('../',import.meta.url),maxBuffer:16*1024*1024}));assert.deepEqual(py,model);
 assert.equal(claims.size,2008);assert.deepEqual(model.counts.claim_statuses,{BLOCKED:21,FAIL:2,NOT_APPLICABLE:87,PASS:392,UNVALIDATED:1506});assert.equal(registry.original_findings.length,26);assert.equal(new Set(registry.original_findings.map(f=>f.claim_id)).size,26);
 for(const item of registry.original_findings.filter(f=>f.disposition!=='CORRECT_NOW'))assert.deepEqual(claims.get(item.claim_id),before.get(item.claim_id));
});
test('five application failures retire into one existing navigation instruction, retaining historical failures',()=>{
 const app=claims.get('MCL-0ae9c2fd5ac2ef9a');assert.equal(app.classification,'REVIEWED_NAVIGATION_INSTRUCTION');assert.equal(app.history.superseded_claims.length,5);
 for(const retired of registry.retirements){assert.equal(claims.has(retired.claim_id),false);assert.deepEqual(app.history.superseded_claims.find(x=>x.claim.id===retired.claim_id).claim,before.get(retired.claim_id));}
 assert.equal(projected.closure.retiredClaims.length,5);assert.equal(projected.presentation.get(app.id).auditHistory.filter(x=>x.method==='WITHDRAWN_UNSUPPORTED_CHECKLIST').length,5);assert.match(read('host/datacenter-status.mdx').toString(),/## Apply/);assert.doesNotMatch(read('host/datacenter-status.mdx').toString(),/Prepare:|Government-issued ID|certificate of good standing|Contract or invoice linking/);
});
test('runtime observations stay partial and preserve the failed normal self-test',()=>{
 for(const id of ['MCL-d2f649ad765ea7bb','MCL-b15c6cfc26e189c2','MCL-115b4938222083ac','MCL-9edeb94eaa736bca','MCL-e6fb82f7e167fdc8']){assert.equal(claims.get(id).status,'UNVALIDATED');assert.ok(claims.get(id).evidence_refs.length>before.get(id).evidence_refs.length);assert.match(claims.get(id).rationale,/remain|not|No/);}
 const normal=claims.get('MCL-3aca6b1f291d4d0c');assert.equal(normal.status,'BLOCKED');assert.match(normal.rationale,/success=false.*0\.8506588.*221\.1/);assert.match(normal.rationale,/No diagnostic rental or workload ran/);assert.ok(normal.evidence_refs.some(e=>e.artifact_ref.endsWith('selftest-normal-preflight-01.json')));
 for(const id of ['VOL-C31','VOL-C33']){assert.equal(claims.get(id).status,'UNVALIDATED');assert.deepEqual(claims.get(id).evidence_refs,before.get(id).evidence_refs);assert.match(claims.get(id).rationale,/no demonstrated unavailable prerequisite/);}
});
test('newest evidence, source, registry and model drift fail closed',()=>{
 for(const ref of [CLOSURE_PATH,registry.baseline.path,registry.sources[0].path,registry.sources[0].before_artifact.path,registry.artifacts[0].path])assert.throws(()=>projectClosureCorrection({read:path=>path===ref?Buffer.concat([read(path),Buffer.from('\n')]):read(path),exists}),/digest drift/);
 const changed=structuredClone(model);changed.pages[0].claims[0].rationale+=' tamper';assert.throws(()=>loadClosureCorrection({read,model:changed,exists}),/whole model differs/);
 assert.throws(()=>loadClosureCorrection({read,model,exists:ref=>ref===CLOSURE_PATH?false:exists(ref)}),/marked model has no registry/);
});
test('exact source selectors and partial-result scope are enforced below registry sealing',async()=>{
 let run=await withRegistry(r=>{r.transitions[0].basis[0].text_pointer='/sections/2/text';});assert.throws(run,/selector\/excerpt drift/);
 run=await withRegistry(r=>{r.transitions.find(x=>x.claim_id==='MCL-d2f649ad765ea7bb').after.status='PASS';});assert.throws(run,/runtime promotion forbidden/);
 run=await withRegistry(r=>{r.retirements.pop();});assert.throws(run,/retirement inventory/);
});
test('complete predecessor proof is replayed, including predecessor artifact tampering',()=>{
 const ref='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/published-invoice-guidance-01.json';assert.throws(()=>projectClosureCorrection({read:p=>p===ref?Buffer.from('{}'):read(p),exists}),/digest drift/);
 const appSource=registry.sources.find(s=>s.path==='host/datacenter-status.mdx');assert.notEqual(sha(read(appSource.path)),appSource.before_artifact.sha256);assert.ok(projected.payoutInvoice);assert.ok(projected.terms);assert.ok(projected.presentation.get('MCL-af1c482a08b09316').auditHistory.length);
});
test('owner registry points at active exact passages and retains concrete rental questions',()=>{
 const owners=loadHostReviewOwnerQuestions({read,model,modelSha256:sha(read('verification/current-host-docs-review.json'))});assert.equal(owners.available,true);assert.equal(owners.questions.length,8);assert.ok(owners.questions.some(q=>q.id==='HQ-RENTAL-DATES'));assert.ok(owners.questions.some(q=>q.id==='HQ-RENTAL-AVAILABILITY'));for(const q of owners.questions)for(const c of q.relatedClaims)assert.ok(claims.has(c.id));
});

test('mixed public-observation artifact keeps each selected canonical destination',async()=>{
 const application=projected.presentation.get('MCL-0ae9c2fd5ac2ef9a').basis[0];
 const account=projected.presentation.get('MCL-57133525f112013a').basis[0];
 assert.equal(application.artifactRef,account.artifactRef);
 assert.equal(application.sourceUrl,'https://vast.ai/data-center-application');
 assert.equal(account.sourceUrl,'https://docs.vast.ai/host/hosting-overview#account-setup-and-hosting-agreement');
 assert.ok(claims.get('MCL-0ae9c2fd5ac2ef9a').source_refs.some(ref=>ref.path===application.sourceUrl&&ref.locator==='/observations/1/excerpt'));
 const run=await withRegistry(r=>{const t=r.transitions.find(t=>t.claim_id==='MCL-0ae9c2fd5ac2ef9a');t.basis[0].sourceUrl=account.sourceUrl;t.after.source_refs[0].path=account.sourceUrl;});
 assert.throws(run,/selected observation canonical URL drift/);
});

test('nine withdrawn rental assertions retain FAIL history and exact bounded replacement evidence',()=>{
 const attempt='verification/evidence/2026-09-14-host-closure-correction-attempt-02';
 const change=JSON.parse(read(attempt+'/change-map.json')),previous=index(JSON.parse(read(attempt+'/pre-narrowing-model.json')));
 assert.equal(change.original_fail_corrections.length,9);assert.equal(new Set(change.original_fail_corrections).size,9);
 for(const id of change.original_fail_corrections){
  const claim=claims.get(id),entry=registry.transitions.find(t=>t.claim_id===id),mapping=change.changes.find(c=>c.claim_id===id);
  assert.equal(previous.get(id).status,'FAIL');assert.equal(claim.status,'PASS');assert.equal(claim.text,mapping.after);
  assert.equal(claim.history.predecessor.status,'FAIL');assert.equal(claim.history.predecessor.text,mapping.before);
  assert.deepEqual(projected.presentation.get(id).previous,previous.get(id));
  for(const evidence of previous.get(id).evidence_refs)assert.ok(claim.evidence_refs.some(e=>JSON.stringify(e)===JSON.stringify(evidence)));
  assert.equal(entry.method,'WITHDRAW_UNSUPPORTED_RENTAL_RULE_RETAIN_SCOPED_GUIDANCE');
  assert.match(claim.rationale,/remain unresolved/);assert.match(claim.next_action,/HQ-RENTAL-DATES.*HQ-RENTAL-AVAILABILITY/);
 }
 for(const id of ['MCL-9cfc73236e4c395a','MCL-250a0c0aa31550a1']){
  const basis=projected.presentation.get(id).basis.find(b=>b.kind==='CANONICAL_IMPLEMENTATION_SOURCE');
  assert.match(basis.sourceUrl,/ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd\/vastai\/cli\/commands\/machines.py#L240$/);
  assert.match(basis.excerpt,/contract offer expiration - the available until date/);
 }
 for(const id of change.unchanged_tax_failures)assert.deepEqual(claims.get(id),previous.get(id));
 const sourceReview=JSON.parse(read('verification/evidence/2026-09-14-host-unvalidated-source-attempt-01/inventory.json'));
 const changedIds=new Set([...change.original_fail_corrections,...change.adjacent_edits,...sourceReview.accepted_ids,...evidenceIds]);
 for(const [id,claim]of claims)if(!changedIds.has(id))assert.deepEqual(claim,previous.get(id),`unrelated claim changed: ${id}`);
 const owners=loadHostReviewOwnerQuestions({read,model,modelSha256:sha(read('verification/current-host-docs-review.json'))});
 for(const id of ['HQ-RENTAL-DATES','HQ-RENTAL-AVAILABILITY']){const q=owners.questions.find(q=>q.id===id);assert.equal(q.status,'UNVALIDATED');assert.match(q.coverageGaps.join(' '),/does not resolve this owner question/);}
});

test('two adjacent edits preserve hypothetical scope, shared introductions, commands and historical evidence',()=>{
 const attempt='verification/evidence/2026-09-14-host-closure-correction-attempt-02';
 const oldModel=JSON.parse(read(attempt+'/pre-narrowing-model.json')),oldClaims=index(oldModel),change=JSON.parse(read(attempt+'/change-map.json'));
 assert.deepEqual(change.adjacent_edits,['MCL-5ab653314f9e68e8','MCL-23085b459da844bc']);
 assert.equal(claims.get('MCL-5ab653314f9e68e8').status,'NOT_APPLICABLE');assert.equal(claims.get('MCL-5ab653314f9e68e8').text,'| Offer end date | 12/31/2026 (example) |');
 assert.equal(claims.get('MCL-23085b459da844bc').history.predecessor.status,'UNVALIDATED');
 assert.match(claims.get('MCL-23085b459da844bc').rationale,/No runtime or safe-stop result/);
 for(const id of ['MCL-470bf8ec992a342e','MCL-6e0046c21ac71be4','MCL-c9441dfe43eb92f1'])assert.equal(claims.get(id).text.split('\n')[0],oldClaims.get(id).text.split('\n')[0]);
 const commands=source=>[...source.matchAll(/```bash\n([\s\S]*?)```/g)].map(m=>m[1]);
 for(const ref of ['host/pricing-your-listing.mdx','host/maintenance-windows.mdx']){
  const source=registry.sources.find(s=>s.path===ref);assert.deepEqual(commands(read(ref).toString()),commands(read(source.before_artifact.path).toString()));
 }
 assert.doesNotMatch(read('host/pricing-your-listing.mdx').toString(),/Maintenance-safe date/);
 assert.doesNotMatch(read('host/maintenance-windows.mdx').toString(),/When the active contracts have ended/);
 const procedures=m=>new Map(m.pages.flatMap(p=>p.procedures.flatMap(pr=>[pr,...pr.nodes]).map(n=>[n.id,n]))),oldProcedures=procedures(oldModel);
 const invalidated=[];for(const [id,node]of procedures(model)){const prior=oldProcedures.get(id);if(prior.status!=='STALE'&&node.status==='STALE'){invalidated.push(id);assert.equal(node.history.carry_decision,'CURRENT_HOST_CLOSURE_SOURCE_CHANGED');assert.deepEqual(node.evidence_refs,prior.evidence_refs);}}
 assert.deepEqual(invalidated.sort(),['CUR-hosting-overview-H05','PRICE-C01-main-s03','MNT-E01-B01-S02','MNT-E01-B02-S03','MNT-E01-B-common','MNT-E01-B-common-S01','MNT-E01-B-common-S02',...evidenceScope.affected_procedures.map(n=>n.id)].sort());
 const manifest=JSON.parse(read(attempt+'/attempt-01-artifact-manifest.json'));for(const file of manifest.files)assert.equal(sha(read(file.path)),file.sha256,`attempt-01 changed: ${file.path}`);
});

test('historical 24-source batch remains exact and two held rows retain their original review state',async()=>{
 const attempt='verification/evidence/2026-09-14-host-unvalidated-source-attempt-01',inventory=JSON.parse(read(attempt+'/inventory.json'));
 assert.equal(inventory.candidates.length,26);assert.equal(inventory.accepted_ids.length,24);
 assert.deepEqual(inventory.held_ids,['CUR-d4f1da8861e06594','CUR-6a6640ac777aa39c']);
 for(const item of inventory.candidates){
  const claim=claims.get(item.claim_id),prior=item.original_claim;
  assert.equal(prior.status,'UNVALIDATED');
  if(inventory.held_ids.includes(item.claim_id)){assert.deepEqual(evidenceOriginal.get(item.claim_id),prior);assert.equal(claim.history.predecessor.text,prior.text);assert.match(claim.text,/\(rounded\)/);continue;}
  assert.equal(claim.text,prior.text);assert.deepEqual(claim.spans,prior.spans);
  assert.equal(claim.status,'PASS');assert.deepEqual(claim.required_evidence_types,prior.required_evidence_types);assert.equal(claim.classification,prior.classification);
  assert.deepEqual(projected.presentation.get(item.claim_id).previous,prior);
  assert.match(claim.rationale,/only|not|No/);assert.equal(claim.history.predecessor.status,'UNVALIDATED');
 }
 const defaultDirectory=registry.transitions.find(t=>t.claim_id==='MCL-582bf3922775c488');
 assert.ok(defaultDirectory.basis.every(b=>b.kind==='CANONICAL_IMPLEMENTATION_SOURCE'));
 assert.match(defaultDirectory.after.rationale,/source-only.*override/);
 const bundle=JSON.parse(read('verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/selftest-normal-preflight-01.json'));
 assert.equal(bundle.structured_result.success,false);assert.equal(bundle.source_revision,'ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd');assert.equal(bundle.bundle_inventory[0].members.length,4);
 for(const source of JSON.parse(read(attempt+'/runtime-source-equivalence.json')).sources)assert.equal(sha(read(source.current_source_artifact)),source.whole_file_sha256);
 for(const [ref,hash]of Object.entries(inventory.customer_mdx_sha256)){const frozen=evidenceScope.before_sources.find(s=>s.path===ref);assert.equal(sha(read(frozen?.before_artifact.path||ref)),hash);}
 const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;
 const hashObject=value=>sha(JSON.stringify(canonical(value)));
 for(const [id,claim]of claims)if(!inventory.accepted_ids.includes(id)&&!evidenceIds.has(id))assert.equal(hashObject(claim),inventory.all_current_claim_hashes[id]);
 assert.equal(hashObject(priorProcedureView()),inventory.procedures_sha256);
 const ownerRegistry=JSON.parse(read('verification/current-host-owner-questions.json'));delete ownerRegistry.model_sha256;assert.equal(hashObject(ownerRegistry),inventory.owner_questions_without_model_hash_sha256);
 let run=await withRegistry(r=>{r.transitions.find(t=>t.claim_id===inventory.accepted_ids[0]).after.text+=' invented';});assert.throws(run,/unchanged review scope/);
 run=await withRegistry(r=>{r.transitions.find(t=>t.claim_id===inventory.accepted_ids[0]).after.required_evidence_types=[];});assert.throws(run,/unchanged review scope/);
 run=await withRegistry(r=>{r.transitions.find(t=>t.claim_id==='MCL-b4de2df6a8e20829').after.source_refs[0].path='https://vast.ai/terms';});assert.throws(run,/unchanged review canonical binding/);
});


test('evidence attempt02 changes exactly23 selected claims and preserves1985 complete claim objects',()=>{
 assert.equal(evidenceIds.size,23);assert.equal(evidenceScope.pending_ids.length,0);let unchanged=0;
 for(const[id,claim]of claims){if(!evidenceIds.has(id)){assert.equal(hashObject(claim),evidenceInventory.all_baseline_claim_hashes[id],id);unchanged++;continue;}
  const prior=evidenceOriginal.get(id),decision=evidenceScope.decisions[id];assert.equal(prior.status,'UNVALIDATED');assert.equal(claim.status,'PASS');assert.equal(claim.text,decision.expected_text);assert.equal(claim.classification,prior.classification);assert.deepEqual(claim.required_evidence_types,prior.required_evidence_types);assert.equal(claim.owner_role,prior.owner_role);
  for(const e of prior.evidence_refs)assert.ok(claim.evidence_refs.some(x=>JSON.stringify(x)===JSON.stringify(e)));for(const e of prior.source_refs)assert.ok(claim.source_refs.some(x=>JSON.stringify(x)===JSON.stringify(e)));
  assert.deepEqual(projected.presentation.get(id).previous,prior);assert.equal(claim.history.predecessor.text,prior.text);
  if(!evidenceScope.corrected_ids.includes(id)){assert.equal(claim.text,prior.text);assert.deepEqual(claim.spans,prior.spans);}
 }
 assert.equal(unchanged,1985);assert.equal(evidenceScope.corrected_ids.length,3);
 const historical=JSON.parse(execFileSync('git',['show','2bdf8e5c9bddca827c671166a5d9ed912b1c388c:verification/current-host-closure-correction.json'],{cwd:new URL('../',import.meta.url),maxBuffer:4*1024*1024}));assert.deepEqual(registry.transitions.slice(0,historical.transitions.length),historical.transitions);for(const a of historical.artifacts){assert.equal(sha(read(a.path)),a.sha256);assert.deepEqual(registry.artifacts.find(x=>x.path===a.path),a);}
});

test('only three approved MDX lines change and exactly three procedure records become stale',()=>{
 const expected={'host/fleet-operations.mdx':[35],'host/self-test-reference.mdx':[95,97]};
 for(const source of evidenceScope.before_sources){const old=read(source.before_artifact.path).toString().split('\n'),now=read(source.path).toString().split('\n');assert.equal(now.length,old.length);assert.deepEqual(old.flatMap((line,i)=>line===now[i]?[]:[i+1]),expected[source.path]);}
 for(const[ref,hash]of Object.entries(evidenceInventory.all_baseline_page_hashes))if(!Object.hasOwn(expected,ref))assert.equal(sha(read(ref)),hash);
 const allNodes=new Map(model.pages.flatMap(p=>p.procedures.flatMap(pr=>[pr,...pr.nodes]).map(n=>[n.id,n])));
 assert.deepEqual(evidenceScope.affected_procedures.map(n=>n.id).sort(),['CUR-self-test-reference-ORDERED-SECTIONS','CUR-self-test-reference-H04','FLT-E02-B01-S02'].sort());
 for(const item of evidenceScope.affected_procedures){const node=allNodes.get(item.id),prior=item.before;assert.equal(prior.status,'UNVALIDATED');assert.equal(node.status,'STALE');assert.deepEqual(node.evidence_refs,prior.evidence_refs);assert.deepEqual(Object.fromEntries(Object.entries(node).filter(([k])=>k!=='nodes')),{...prior,spans:[],status:'STALE',coverage_state:'CHANGED',limits:[...(prior.limits||[]),'Closure source changed; retained procedure evidence does not transfer to changed steps.'],history:{...prior.history,carry_decision:'CURRENT_HOST_CLOSURE_SOURCE_CHANGED'}});}
 assert.equal(hashObject(priorProcedureView()),evidenceInventory.procedure_population_sha256);
 const sourceReview=JSON.parse(read(evidenceAttempt+'/source-review.json'));for(const id of ['CUR-d4f1da8861e06594','CUR-6a6640ac777aa39c']){const row=sourceReview.claims.find(c=>c.claim_id===id);assert.match(row.proposed_result,/FAIL/);assert.equal(row.original_full_wording,evidenceOriginal.get(id).text);assert.match(claims.get(id).text,/\(rounded\)/);}
});

test('new source bindings and complete methods remain guarded below registry sealing',async()=>{
 let run=await withRegistry(r=>{r.transitions.find(t=>t.claim_id==='MCL-67c1400801647f68').after.text+=' broader promise';});assert.throws(run,/evidence review disposition/);
 run=await withRegistry(r=>{r.transitions.find(t=>t.claim_id==='MCL-f0a3f4f3f551bac6').after.required_evidence_types=['CANONICAL_IMPLEMENTATION_SOURCE'];});assert.throws(run,/evidence review method drift/);
 const entry=registry.transitions.find(t=>t.claim_id==='MCL-720d258a01fceff8');assert.ok(entry.basis.some(b=>b.text_pointer.includes('~1')));
 run=await withRegistry(r=>{const t=r.transitions.find(t=>t.claim_id==='MCL-720d258a01fceff8'),b=t.basis.find(b=>b.text_pointer.includes('~1'));for(const ref of t.after.source_refs)if(ref.locator===b.text_pointer)ref.path='https://vast.ai/terms';b.sourceUrl='https://vast.ai/terms';});assert.throws(run,/selected source canonical URL drift/);
});
