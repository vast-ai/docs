import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {projectSourceFamilyReview,loadSourceFamilyReview,SOURCE_FAMILY_PATH,SOURCE_FAMILY_SHA256,SOURCE_FAMILY_ATTEMPT as A} from './current_host_source_family_review.mjs';
import {beforeEvidenceReuse,beforeSourceFamily} from './closure_historical_test_sources.mjs';
import {loadHostReviewOwnerQuestions} from './host_review_owner_questions.mjs';
import {buildHostReviewIssues} from './host_review_work_queue.mjs';

const liveRead=ref=>fs.readFileSync(new URL('../'+ref,import.meta.url)),read=beforeEvidenceReuse(liveRead),exists=ref=>fs.existsSync(new URL('../'+ref,import.meta.url));
const model=JSON.parse(read('verification/current-host-docs-review.json')),registry=JSON.parse(read(SOURCE_FAMILY_PATH));
const historicalRead=beforeSourceFamily(read),before=JSON.parse(historicalRead('verification/current-host-docs-review.json'));
const index=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),claims=index(model),old=index(before);
const sha=value=>crypto.createHash('sha256').update(value).digest('hex'),omit=(o,keys)=>Object.fromEntries(Object.entries(o).filter(([k])=>!keys.includes(k)));
const at=(o,pointer)=>pointer.slice(1).split('/').reduce((value,key)=>value[key],o);
const projected=projectSourceFamilyReview({read,exists});

// Test-only resealing exercises invariants beneath the immutable registry pin.
async function withRegistry(change){
 const edited=structuredClone(registry);change(edited);const raw=Buffer.from(JSON.stringify(edited));
 const source=read('scripts/current_host_source_family_review.mjs').toString().replace(SOURCE_FAMILY_SHA256,sha(raw)).replace("'./current_host_closure_correction.mjs'",JSON.stringify(new URL('./current_host_closure_correction.mjs',import.meta.url).href));
 const module=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 return ()=>module.projectSourceFamilyReview({read:ref=>ref===SOURCE_FAMILY_PATH?raw:read(ref),exists});
}

test('358 accepted occurrences project identically in Python and JavaScript, preserving the other 1650 claim objects apart from relocated spans',()=>{
 assert.deepEqual(projected.model,model);assert.deepEqual(loadSourceFamilyReview({read,model,exists}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_source_family_review as m;r=Path.cwd();p=r/'verification/current-host-evidence-reuse-review.json';reg=json.loads(p.read_text()) if p.exists() else {'sources':[]};frozen={s['path']:(r/s['before_artifact']['path']).read_bytes() for s in reg['sources']};print(json.dumps(m.project(r,frozen_source_overrides=frozen)))"],{cwd:new URL('../',import.meta.url),maxBuffer:20*1024*1024}));
 assert.deepEqual(py,model);assert.equal(claims.size,2008);assert.deepEqual(model.counts.claim_statuses,{BLOCKED:21,FAIL:4,NOT_APPLICABLE:89,PASS:744,UNVALIDATED:1150});
 const ids=new Set(registry.transitions.map(t=>t.claim_id));assert.equal(ids.size,358);let unselected=0;
 for(const[id,claim]of claims){const prior=old.get(id);if(!ids.has(id)){assert.deepEqual(omit(claim,['spans']),omit(prior,['spans']),id);unselected++;continue;}
  assert.equal(prior.status,'UNVALIDATED');for(const e of prior.evidence_refs)assert.ok(claim.evidence_refs.some(x=>JSON.stringify(x)===JSON.stringify(e)),id);
  for(const e of prior.source_refs)assert.ok(claim.source_refs.some(x=>JSON.stringify(x)===JSON.stringify(e)),id);
  assert.deepEqual(omit(claim.history,['source_family_review']),prior.history,id);assert.equal(claim.history.source_family_review.prior_status,'UNVALIDATED');
 }
 assert.equal(unselected,1650);assert.equal(registry.transitions.filter(t=>t.decision==='correction').length,69);
});

test('43 pointer-keyed procedure context changes retain every status, evidence field and exact before span',()=>{
 assert.equal(registry.procedures.length,43);assert.equal(new Set(registry.procedures.map(p=>p.model_pointer)).size,43);
 for(const entry of registry.procedures){const prior=at(before,entry.model_pointer),current=at(model,entry.model_pointer);assert.equal(current.status,prior.status,entry.model_pointer);assert.deepEqual(omit(current,['spans','history','coverage_state','nodes']),omit(prior,['spans','history','coverage_state','nodes']),entry.model_pointer);assert.deepEqual(current.history.source_family_review.prior_spans,prior.spans);}
 const record=JSON.parse(read(A+'/procedure-context-comparison.json'));assert.equal(record.all_43_statuses_and_evidence_unchanged,true);assert.equal(record.comparisons.length,1);assert.equal(record.comparisons[0].id,'ERR-T05-B02-S01');assert.equal(record.comparisons[0].command_bytes_unchanged,true);
 for(const comparison of record.comparisons){const fences=(ref,spans)=>{const content=read(ref).toString();return [...content.matchAll(/^```[^\n]*\n([\s\S]*?)^```/gm)].filter(m=>{const a=content.slice(0,m.index).split('\n').length,b=content.slice(0,m.index+m[0].length).split('\n').length;return spans.some(s=>a<=s.end&&b>=s.start);}).map(m=>m[1]);};
  assert.deepEqual(fences(A+'/sources-before/host/machine-errors.mdx',comparison.before_spans),fences('host/machine-errors.mdx',comparison.after_spans));}
});

test('CPU conflicts stay FAIL and two exact reviewed source residuals appear as follow-ups without a blanket UNVALIDATED promotion',()=>{
 for(const id of ['CUR-f992e392221fe492','CUR-1de91e8c48307d8b']){assert.equal(claims.get(id).status,'FAIL');assert.equal(claims.get(id).text,old.get(id).text);assert.match(claims.get(id).next_action,/align|revision|source/i);}
 const owner=loadHostReviewOwnerQuestions({read,model,modelSha256:sha(read('verification/current-host-docs-review.json'))});assert.equal(owner.available,true,owner.error);
 const issues=buildHostReviewIssues({pages:model.pages,ownerQuestions:owner.questions,originalFindings:projected.closure.registry.original_findings,sourceFamilyTransitions:registry.transitions});
 assert.deepEqual(issues.sourceFollowUps.map(x=>x.claimId).sort(),['MCL-1221941af8a7a4fe','MCL-b106578dbaccc269']);
 for(const row of issues.sourceFollowUps){assert.equal(claims.get(row.claimId).status,'UNVALIDATED');assert.equal(row.nextAction,claims.get(row.claimId).next_action);}
});

test('amended payout link is question context only; unchanged payout proof and unrelated source-link guards remain exact',()=>{
 const owners=JSON.parse(read('verification/current-host-owner-questions.json')),amendment=JSON.parse(read(A+'/owner-context-amendment.json'));
 assert.equal(owners.questions.length,8);assert.deepEqual(owners.questions.find(q=>q.id===amendment.question_id),amendment.after);
 for(const id of ['MCL-e2b956d14494e470','MCL-5936430d1b2d8de9'])assert.deepEqual(claims.get(id),old.get(id));
 for(const question of owners.questions.filter(q=>q.id!==amendment.question_id))assert.deepEqual(question,JSON.parse(historicalRead('verification/current-host-owner-questions.json')).questions.find(q=>q.id===question.id));
 for(const qid of [amendment.question_id,owners.questions.find(q=>q.id!==amendment.question_id).id]){
  const changed=structuredClone(owners);changed.questions.find(q=>q.id===qid).related_claims[0].source_links.push('https://example.invalid/unrelated');
  const result=loadHostReviewOwnerQuestions({read:ref=>ref==='verification/current-host-owner-questions.json'?Buffer.from(JSON.stringify(changed)):read(ref),model,modelSha256:sha(read('verification/current-host-docs-review.json'))});assert.equal(result.available,false);assert.match(result.error,/drift/);
 }
 const bad=loadHostReviewOwnerQuestions({read:ref=>ref===A+'/owner-context-amendment.json'?Buffer.from('{}'):read(ref),model,modelSha256:sha(read('verification/current-host-docs-review.json'))});assert.equal(bad.available,false);assert.match(bad.error,/amendment drift/);
});

test('registry, retained sources, complete historical proof, current model and accepted decisions reject tampering',async()=>{
 for(const ref of [SOURCE_FAMILY_PATH,registry.scope.path,registry.sources[0].path,registry.sources[0].before_artifact.path,registry.artifacts[0].path,'verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/published-invoice-guidance-01.json'])assert.throws(()=>projectSourceFamilyReview({read:path=>path===ref?Buffer.concat([read(path),Buffer.from('\n')]):read(path),exists}),/digest drift|digest mismatch/);
 const changed=structuredClone(model);changed.pages[0].claims[0].rationale+=' unsupported';assert.throws(()=>loadSourceFamilyReview({read,model:changed,exists}),/whole model differs/);
 let run=await withRegistry(r=>{r.transitions[0].basis[0].excerpt+=' unsupported';});assert.throws(run,/selector\/excerpt drift/);
 run=await withRegistry(r=>{r.transitions.find(t=>t.after.status==='UNVALIDATED').after.status='PASS';});assert.throws(run,/accepted disposition drift/);
 run=await withRegistry(r=>{r.transitions.pop();});assert.throws(run,/transition scope/);
 run=await withRegistry(r=>{r.procedures[0].after.status='PASS';});assert.throws(run,/unaccepted procedure change/);
});
