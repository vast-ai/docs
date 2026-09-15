import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {projectFinalOwnerReview,loadFinalOwnerReview,FINAL_OWNER_PATH as REG,FINAL_OWNER_SHA256 as PIN,FINAL_OWNER_ATTEMPT as A} from './current_host_final_owner_review.mjs';
import {beforeFinalOwner} from './closure_historical_test_sources.mjs';
import {reconcileHostReviewOwnerQuestions,requireHostReviewOwnerQuestions} from './host_review_owner_questions.mjs';
import {buildHostReviewIssues} from './host_review_work_queue.mjs';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url)),exists=p=>fs.existsSync(new URL('../'+p,import.meta.url));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),index=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),omit=(o,keys)=>Object.fromEntries(Object.entries(o).filter(([k])=>!keys.includes(k)));
async function reseal(registry,change){const r=structuredClone(registry);change(r);const bytes=Buffer.from(JSON.stringify(r)),source=read('scripts/current_host_final_owner_review.mjs').toString().replace(PIN,sha(bytes)).replace("'./current_host_hardware_operator_review.mjs'",JSON.stringify(new URL('./current_host_hardware_operator_review.mjs',import.meta.url).href));const m=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>m.projectFinalOwnerReview({read:p=>p===REG?bytes:read(p),exists});}
test('12 exact transitions preserve all prior history and 1201 procedure outcomes with Python/JS parity',()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json')),before=JSON.parse(beforeFinalOwner(read)('verification/current-host-docs-review.json')),p=projectFinalOwnerReview({read,exists});
 assert.deepEqual(p.model,model);assert.deepEqual(loadFinalOwnerReview({read,exists,model}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_final_owner_review as m;print(json.dumps(m.project(Path.cwd())))"],{cwd:new URL('../',import.meta.url),maxBuffer:64*1024*1024}));assert.deepEqual(py,model);
 assert.deepEqual(model.counts.claim_statuses,{NOT_APPLICABLE:95,PASS:1913});const old=index(before),current=index(model),selected=new Set(registry.transitions.map(t=>t.claim_id));assert.equal(selected.size,12);assert.equal(current.size,2008);let unchanged=0;
 for(const[id,c]of current){const prior=old.get(id);assert.deepEqual(omit(c.history,['final_owner_review']),prior.history,id);if(!selected.has(id)){assert.deepEqual(omit(c,['spans']),omit(prior,['spans']),id);unchanged++;}else for(const key of ['evidence_refs','source_refs'])for(const source of prior[key])assert.ok(c[key].some(x=>JSON.stringify(x)===JSON.stringify(source)),id);}
 assert.equal(unchanged,1996);assert.equal(old.get('VOL-C28').status,'PASS');assert.equal(current.get('VOL-C28').status,'PASS');let procedures=0;
 for(let pi=0;pi<model.pages.length;pi++)for(let qi=0;qi<model.pages[pi].procedures.length;qi++){const a=model.pages[pi].procedures[qi],b=before.pages[pi].procedures[qi];for(const[n,k]of [[a,b],...a.nodes.map((x,i)=>[x,b.nodes[i]])]){procedures++;assert.deepEqual(omit(n,['nodes','spans','history','coverage_state']),omit(k,['nodes','spans','history','coverage_state']),n.id);assert.deepEqual(omit(n.history||{},['final_owner_review']),k.history||{},n.id);}}
 assert.equal(procedures,1201);assert.deepEqual(omit(JSON.parse(read('verification/current-host-owner-questions.json')),['model_sha256']),omit(JSON.parse(read(A+'/before-owner-questions.json')),['model_sha256']));assert.equal(p.hardwareOperator.registry.transitions.length,107);assert.equal(p.verificationStorage.registry.transitions.length,176);
 const impact=JSON.parse(read(A+'/integration-impact.json'));assert.equal(impact.affected_procedures.length,23);assert.ok(impact.affected_procedures.every(x=>x.fences_unchanged));
});
test('owner purpose separates 3 publication conflicts and 8 future details without changing the original 8 records',()=>{
 const p=projectFinalOwnerReview({read,exists}),m=p.model,original=requireHostReviewOwnerQuestions({read,model:m,modelSha256:sha(read('verification/current-host-docs-review.json'))}),frozen=structuredClone(original);
 const owners=reconcileHostReviewOwnerQuestions({projection:original,finalOwner:p.finalOwner,model:m});assert.deepEqual(original,frozen);assert.equal(owners.questions.length,11);assert.equal(owners.questions.filter(q=>q.presentationKind==='current_publication_conflict').length,3);assert.equal(owners.questions.filter(q=>q.presentationKind==='future_detail').length,8);assert.ok(owners.questions.every(q=>q.currentWordingRequiresAnswer===false&&q.status==='UNVALIDATED'&&q.relatedClaims.every(c=>c.status==='PASS')));
 const issues=buildHostReviewIssues({pages:m.pages,ownerQuestions:owners.questions,hardwareOperatorTransitions:p.hardwareOperator.registry.transitions,finalOwnerTransitions:p.finalOwner.registry.transitions});assert.equal(issues.corrections.length,0);assert.equal(issues.sourceFollowUps.length,0);assert.equal(issues.counts.blockedPassages,0);assert.equal(issues.counts.publicationConflicts,3);assert.equal(issues.counts.futureDetailQuestions,8);assert.equal(issues.workflows.length,11);assert.equal(issues.counts.recordedProcedures,14);
});
test('accepted source, selector, method, owner and procedure pins fail closed',async()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json'));
 assert.equal(loadFinalOwnerReview({read,exists:()=>false,model:{corrections:[]}}),null);assert.throws(()=>loadFinalOwnerReview({read,exists:()=>false,model:{corrections:[{id:'HOST-FINAL-OWNER-REVIEW-01'}]}}),/has no registry/);
 for(const ref of [REG,registry.scope.path,A+'/root-source-acceptance.json',A+'/final-seal.json',A+'/final/decisions-05.json',A+'/storage_adjacent/sources-05.json',A+'/owner-reconciliation.json',A+'/before-owner-questions.json','verification/current-host-hardware-operator-review.json'])assert.throws(()=>projectFinalOwnerReview({read:p=>p===ref?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift|digest mismatch/);
 for(const mutate of [r=>r.transitions[0].basis[0].excerpt+=' unaccepted',r=>r.transitions[0].after.owner_role='invented',r=>r.transitions[0].method_rationale='invented',r=>r.transitions.pop(),r=>r.procedures[0].after.status='PASS'])assert.throws(await reseal(registry,mutate),/accepted|transition scope/);
 const altered=structuredClone(model);altered.pages[0].claims[0].rationale+=' drift';assert.throws(()=>loadFinalOwnerReview({read,exists,model:altered}),/whole model differs/);
});
