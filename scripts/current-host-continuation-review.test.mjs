import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {projectContinuationReview,loadContinuationReview,CONTINUATION_PATH as REG,CONTINUATION_SHA256 as PIN,CONTINUATION_ATTEMPT as A} from './current_host_continuation_review.mjs';
import {beforeContinuation,beforeDiagnosticsSsh} from './closure_historical_test_sources.mjs';
import {buildHostReviewIssues} from './host_review_work_queue.mjs';
const rawRead=p=>fs.readFileSync(new URL('../'+p,import.meta.url)),read=beforeDiagnosticsSsh(rawRead),exists=p=>{try{read(p);return true;}catch(e){if(e.code==='ENOENT')return false;throw e;}};
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),index=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),omit=(o,keys)=>Object.fromEntries(Object.entries(o).filter(([k])=>!keys.includes(k)));
async function reseal(registry,change){const r=structuredClone(registry);change(r);const bytes=Buffer.from(JSON.stringify(r)),source=read('scripts/current_host_continuation_review.mjs').toString().replace(PIN,sha(bytes)).replace("'./current_host_evidence_reuse_review.mjs'",JSON.stringify(new URL('./current_host_evidence_reuse_review.mjs',import.meta.url).href));const m=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>m.projectContinuationReview({read:p=>p===REG?bytes:read(p),exists});}
test('an absent successor preserves the older lane but a marked model without its registry fails',()=>{
 const missing=p=>{if(p===REG){const e=Error('not present');e.code='ENOENT';throw e;}return read(p);};
 assert.equal(loadContinuationReview({read:missing,exists:()=>false,model:{corrections:[]}}),null);
 assert.throws(()=>loadContinuationReview({read:missing,exists:()=>false,model:{corrections:[{id:'HOST-CONTINUATION-REVIEW-01'}]}}),/has no registry/);
});
test('all 88 accepted decisions have Python/JS parity, preserve 1920 other claims and retain prior 318/358 history',()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json')),before=JSON.parse(beforeContinuation(read)('verification/current-host-docs-review.json'));
 const projected=projectContinuationReview({read,exists});assert.deepEqual(projected.model,model);assert.deepEqual(loadContinuationReview({read,exists,model}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_continuation_review as m;r=Path.cwd(); paths=[r/'verification/current-host-recovery-earnings-review.json',r/'verification/current-host-setup-metrics-review.json',r/'verification/current-host-teams-console-review.json',r/'verification/current-host-diagnostics-ssh-review.json']; overrides={s['path']:(r/s['before_artifact']['path']).read_bytes() for p in paths if p.exists() for s in json.loads(p.read_text())['sources']};print(json.dumps(m.project(r,frozen_source_overrides=overrides)))"],{cwd:new URL('../',import.meta.url),maxBuffer:64*1024*1024}));assert.deepEqual(py,model);
 const old=index(before),current=index(model),selected=new Set(registry.transitions.map(t=>t.claim_id));assert.equal(selected.size,88);assert.equal(current.size,2008);let unchanged=0;
 for(const[id,c]of current){const prior=old.get(id);if(!selected.has(id)){assert.deepEqual(omit(c,['spans']),omit(prior,['spans']),id);unchanged++;continue;}
  assert.deepEqual(omit(c.history,['continuation_review']),prior.history,id);assert.equal(c.history.continuation_review.prior_status,prior.status);
  for(const key of ['evidence_refs','source_refs'])for(const source of prior[key])assert.ok(c[key].some(x=>JSON.stringify(x)===JSON.stringify(source)),id);
 }
 assert.equal(unchanged,1920);assert.equal(projected.evidenceReuse.registry.transitions.length,318);assert.equal(projected.sourceFamily.registry.transitions.length,358);assert.ok(projected.closure);
 assert.equal(sha(read('verification/current-host-evidence-reuse-review.json')),'0b861b45f54eae3b646480818b147b1936cfed698b750c4b4dc7720d574606e7');
 assert.deepEqual(omit(JSON.parse(read('verification/current-host-owner-questions.json')),['model_sha256']),omit(JSON.parse(beforeContinuation(read)('verification/current-host-owner-questions.json')),['model_sha256']));
 for(let pi=0;pi<model.pages.length;pi++)for(let qi=0;qi<model.pages[pi].procedures.length;qi++){
  const a=model.pages[pi].procedures[qi],b=before.pages[pi].procedures[qi];for(const[n,k]of [[a,b],...a.nodes.map((x,i)=>[x,b.nodes[i]])])assert.deepEqual(omit(n,['nodes','spans','history','coverage_state']),omit(k,['nodes','spans','history','coverage_state']),n.id);
 }
 const beforeIssues=buildHostReviewIssues({pages:before.pages,ownerQuestions:[],sourceFamilyTransitions:projected.sourceFamily.registry.transitions,evidenceReuseTransitions:projected.evidenceReuse.registry.transitions});
 const afterIssues=buildHostReviewIssues({pages:model.pages,ownerQuestions:[],sourceFamilyTransitions:projected.sourceFamily.registry.transitions,evidenceReuseTransitions:projected.evidenceReuse.registry.transitions,continuationTransitions:registry.transitions});
 const currentFollowUps=new Set(afterIssues.sourceFollowUps.map(x=>x.claimId));for(const old of beforeIssues.sourceFollowUps)if(!selected.has(old.claimId))assert.ok(currentFollowUps.has(old.claimId),'unrelated residual lost '+old.claimId);
});
test('accepted data, source locators, whole-model and procedure gates reject drift',async()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json'));
 for(const ref of [REG,registry.scope.path,A+'/root-lane-acceptance.json',A+'/a-cli-reuse/decisions.json',A+'/c-teams-source/sources.json',registry.artifacts[0].path,'verification/current-host-evidence-reuse-review.json'])assert.throws(()=>projectContinuationReview({read:p=>p===ref?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift|digest mismatch/);
 const modified=structuredClone(model);modified.pages[0].claims[0].rationale+=' changed';assert.throws(()=>loadContinuationReview({read,exists,model:modified}),/whole model differs/);
 for(const mutate of [r=>r.transitions[0].basis[0].excerpt+=' unaccepted',r=>r.transitions[0].after.owner_role='invented',r=>r.transitions[0].method_rationale='invented',r=>r.transitions.pop()])assert.throws(await reseal(registry,mutate),/accepted|transition scope/);
 if(registry.procedures.length)assert.throws(await reseal(registry,r=>r.procedures[0].after.status='PASS'),/unaccepted procedure change/);
 for(const source of registry.sources)assert.throws(()=>projectContinuationReview({read:p=>p===source.path?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift/);
});
