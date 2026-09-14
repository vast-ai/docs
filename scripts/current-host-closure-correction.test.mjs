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
// Resealing is test-only: this exercises selector/scope checks below the digest guard.
async function withRegistry(change){const edited=structuredClone(registry);change(edited);const bytes=Buffer.from(JSON.stringify(edited));const source=read('scripts/current_host_closure_correction.mjs').toString().replace(CLOSURE_SHA256,sha(bytes)).replace("'./current_host_payout_invoice_correction.mjs'",JSON.stringify(new URL('./current_host_payout_invoice_correction.mjs',import.meta.url).href));const module=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>module.projectClosureCorrection({read:ref=>ref===CLOSURE_PATH?bytes:read(ref),exists});}
test('Python/JavaScript project the same newest model and preserve original finding accounting',()=>{
 assert.deepEqual(projected.model,model);assert.deepEqual(loadCurrentHostReviewTransition({read,model,exists}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_closure_correction as m;print(json.dumps(m.project(Path.cwd())))"],{cwd:new URL('../',import.meta.url),maxBuffer:16*1024*1024}));assert.deepEqual(py,model);
 assert.equal(claims.size,2008);assert.deepEqual(model.counts.claim_statuses,{BLOCKED:21,FAIL:11,NOT_APPLICABLE:87,PASS:335,UNVALIDATED:1554});assert.equal(registry.original_findings.length,26);assert.equal(new Set(registry.original_findings.map(f=>f.claim_id)).size,26);
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
