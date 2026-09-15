import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {sourceOrigin,projectHardwareOperatorReview,loadHardwareOperatorReview,HARDWARE_OPERATOR_PATH as REG,HARDWARE_OPERATOR_SHA256 as PIN,HARDWARE_OPERATOR_ATTEMPT as A} from './current_host_hardware_operator_review.mjs';
import {beforeHardwareOperator} from './closure_historical_test_sources.mjs';
import {buildHostReviewIssues,describeHostReview} from './host_review_work_queue.mjs';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url)),exists=p=>fs.existsSync(new URL('../'+p,import.meta.url));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),index=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),omit=(o,keys)=>Object.fromEntries(Object.entries(o).filter(([k])=>!keys.includes(k)));
async function reseal(registry,change){const r=structuredClone(registry);change(r);const bytes=Buffer.from(JSON.stringify(r)),source=read('scripts/current_host_hardware_operator_review.mjs').toString().replace(PIN,sha(bytes)).replace("'./current_host_verification_storage_review.mjs'",JSON.stringify(new URL('./current_host_verification_storage_review.mjs',import.meta.url).href));const m=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>m.projectHardwareOperatorReview({read:p=>p===REG?bytes:read(p),exists});}
test('absent successor preserves the older lane; marked model without registry fails',()=>{
 assert.equal(loadHardwareOperatorReview({read,exists:()=>false,model:{corrections:[]}}),null);
 assert.throws(()=>loadHardwareOperatorReview({read,exists:()=>false,model:{corrections:[{id:'HOST-HARDWARE-OPERATOR-REVIEW-01'}]}}),/has no registry/);
});
test('107 exact transitions have Python/JS parity; all unselected literals and historical outcomes remain intact',()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json')),before=JSON.parse(beforeHardwareOperator(read)('verification/current-host-docs-review.json')),impact=JSON.parse(read(A+'/integration-impact.json'));
 const projected=projectHardwareOperatorReview({read,exists});assert.deepEqual(projected.model,model);assert.deepEqual(loadHardwareOperatorReview({read,exists,model}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_hardware_operator_review as m;print(json.dumps(m.project(Path.cwd())))"],{cwd:new URL('../',import.meta.url),maxBuffer:64*1024*1024}));assert.deepEqual(py,model);
 const old=index(before),current=index(model),selected=new Set(registry.transitions.map(t=>t.claim_id)),headings=new Set(impact.heading_metadata_changes.filter(x=>x.kind==='claim').map(x=>x.id));assert.equal(selected.size,107);assert.equal(current.size,2008);
 assert.deepEqual(model.counts.claim_statuses,{FAIL:2,NOT_APPLICABLE:95,PASS:1902,UNVALIDATED:9});
 assert.equal(model.corrections.filter(x=>x.id==='HOST-HARDWARE-OPERATOR-REVIEW-01').length,1);assert.equal(model.corrections.filter(x=>x.id==='HOST-VERIFICATION-STORAGE-REVIEW-01').length,1);
 const ac=JSON.parse(read(A+'/integration-acceptance.json'));assert.deepEqual(ac.scope_counts,{reviewed_passages:106,adjacent_pass_consistency_records:1,transitions:107,newly_resolved:105,uncounted_context_edits:1});let unchanged=0;
 for(const[id,c]of current){const prior=old.get(id),h=headings.has(id),history=omit(c.history,['hardware_operator_review','hardware_operator_heading_rebind']);assert.deepEqual(history,prior.history,id);
  if(h){assert.deepEqual(c.headings,prior.headings.map(x=>x==='Minimum Listing Baseline'?'Hardware Planning':x));assert.deepEqual(c.history.hardware_operator_heading_rebind.prior_headings,prior.headings);}
  if(!selected.has(id)){assert.deepEqual(omit(c,['spans','history',...(h?['headings']:[])]),omit(prior,['spans','history',...(h?['headings']:[])]),id);unchanged++;continue;}
  assert.equal(c.history.hardware_operator_review.prior_status,prior.status);for(const key of ['evidence_refs','source_refs'])for(const source of prior[key])assert.ok(c[key].some(x=>JSON.stringify(x)===JSON.stringify(source)),id);
 }
 assert.equal(unchanged,1901);assert.equal(old.get('CUR-97f860901c54e022').status,'PASS');assert.equal(current.get('CUR-97f860901c54e022').status,'PASS');
 for(let pi=0;pi<model.pages.length;pi++)for(let qi=0;qi<model.pages[pi].procedures.length;qi++){const a=model.pages[pi].procedures[qi],b=before.pages[pi].procedures[qi];for(const[n,k]of [[a,b],...a.nodes.map((x,i)=>[x,b.nodes[i]])]){assert.deepEqual(omit(n,['nodes','spans','history','coverage_state','headings']),omit(k,['nodes','spans','history','coverage_state','headings']),n.id);assert.deepEqual(omit(n.history||{},['hardware_operator_review','hardware_operator_heading_rebind']),k.history||{},n.id);}}
 assert.equal(projected.verificationStorage.registry.transitions.length,176);assert.equal(projected.recoveryEarnings.registry.transitions.length,148);assert.equal(projected.evidenceReuse.registry.transitions.length,318);assert.equal(projected.sourceFamily.registry.transitions.length,358);
 assert.deepEqual(omit(JSON.parse(read('verification/current-host-owner-questions.json')),['model_sha256']),omit(JSON.parse(beforeHardwareOperator(read)('verification/current-host-owner-questions.json')),['model_sha256']));
 const issues=buildHostReviewIssues({pages:model.pages,ownerQuestions:[],hardwareOperatorTransitions:registry.transitions});assert.equal(issues.sourceFollowUps.length,1);assert.equal(issues.sourceFollowUps[0].claimId,'MCL-6842b63298275c23');assert.equal(describeHostReview(current.get('MCL-9ad33b25fd88c5cb')).needsTriage,false);
 const priorCredential=JSON.parse(read('verification/evidence/2026-09-15-host-continuation-credential-storage-attempt-01/decisions.json'));assert.equal(priorCredential.decisions[0].id,'MCL-9ad33b25fd88c5cb');assert.ok(read('verification/evidence/2026-09-15-host-continuation-credential-storage-attempt-02/checks.json').length);
});
test('accepted decisions, source locators, procedure outcomes and whole model fail closed on drift',async()=>{
 const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json'));
 for(const ref of [REG,registry.scope.path,A+'/integration-acceptance.json',A+'/hardware/root-acceptance.json',A+'/credential/decisions.json',A+'/blocked/sources.json',A+'/ssh_adjacent/root-acceptance.json','verification/current-host-verification-storage-review.json'])assert.throws(()=>projectHardwareOperatorReview({read:p=>p===ref?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift|digest mismatch/);
 const modified=structuredClone(model);modified.pages[0].claims[0].rationale+=' changed';assert.throws(()=>loadHardwareOperatorReview({read,exists,model:modified}),/whole model differs/);
 for(const mutate of [r=>r.transitions[0].basis[0].excerpt+=' unaccepted',r=>r.transitions[0].after.owner_role='invented',r=>r.transitions[0].method_rationale='invented',r=>r.transitions.pop()])assert.throws(await reseal(registry,mutate),/accepted|transition scope/);
 assert.throws(await reseal(registry,r=>r.procedures[0].after.status='PASS'),/unaccepted procedure change/);
 for(const source of registry.sources)assert.throws(()=>projectHardwareOperatorReview({read:p=>p===source.path?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift/);
});
test('selected child source URL/revision/kind wins over aggregate metadata',()=>{
 const raw=Buffer.from(JSON.stringify({url:'https://example.org/bundle',blocks:{correct:{source_url:'https://vendor.example.org/exact',revision:'reviewed-commit',source_kind:'PRIMARY_ENGINEERING_SOURCE',text:'definition'},sibling:{url:'https://other.example.org/wrong'}}}));assert.deepEqual(sourceOrigin(raw,'/blocks/correct/text',{url:'https://example.org/bundle',revision:'bundle-date'}),['https://vendor.example.org/exact','reviewed-commit','PRIMARY_ENGINEERING_SOURCE']);
});
