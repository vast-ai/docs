import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import crypto from 'node:crypto';import {execFileSync} from 'node:child_process';
import {projectTaxGuideRetirement,loadTaxGuideRetirement,TAX_RETIREMENT_PATH as REG,TAX_RETIREMENT_ATTEMPT as A} from './current_host_tax_guide_retirement.mjs';
import {projectFinalOwnerReview} from './current_host_final_owner_review.mjs';
import {requireHostReviewOwnerQuestions,reconcileHostReviewOwnerQuestions} from './host_review_owner_questions.mjs';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url)),exists=p=>fs.existsSync(new URL('../'+p,import.meta.url)),sha=x=>crypto.createHash('sha256').update(x).digest('hex'),omit=(o,keys)=>Object.fromEntries(Object.entries(o).filter(([k])=>!keys.includes(k)));
const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json'));
test('retirement replays both languages and preserves all non-retired claims and execution outcomes',()=>{
 const actual=projectTaxGuideRetirement({read,exists});assert.deepEqual(actual.model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_tax_guide_retirement as m;print(json.dumps(m.project(Path.cwd())))"],{cwd:new URL('../',import.meta.url),maxBuffer:64*1024*1024}));assert.deepEqual(py,model);
 const frozen=new Map(registry.sources.map(s=>[s.path,read(s.before_artifact.path)]));frozen.set('verification/current-host-owner-questions.json',read(registry.before_owners.path));const before=projectFinalOwnerReview({read:p=>frozen.get(p)||read(p)}).model;
 const old=new Map(before.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),now=new Map(model.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),selected=new Set(registry.claims.map(c=>c.id));assert.equal(old.size-now.size,16);
 for(const[id,c]of now){const b=old.get(id);if(!selected.has(id))assert.deepEqual(c,b,id);else{assert.equal(c.status,b.status,id);assert.deepEqual(c.evidence_refs,b.evidence_refs,id);assert.deepEqual(c.source_refs,b.source_refs,id);}}
 const archive=JSON.parse(read(registry.archive.path));assert.deepEqual(archive.page,before.pages.find(p=>p.route===registry.retired_route));assert.deepEqual(archive.faq_claim,old.get('MCL-7b86589912c968bb'));let outcomes=0;
 for(const p of model.pages){const previous=before.pages.find(q=>q.route===p.route);p.procedures.forEach((q,qi)=>[q,...q.nodes].forEach((n,ni)=>{const b=[previous.procedures[qi],...previous.procedures[qi].nodes][ni];assert.deepEqual(omit(n,['nodes','spans']),omit(b,['nodes','spans']),n.id);outcomes++;}));}
 assert.equal(outcomes,1185);assert.deepEqual(model.counts.claim_statuses,{NOT_APPLICABLE:94,PASS:1898});assert.equal(model.pages.length,43);assert.ok(!exists('host/guide-to-taxes.mdx'));
});
test('only tax owner question is retired and all three conflicts plus seven future details remain',()=>{
 const p=projectTaxGuideRetirement({read,exists}),original=requireHostReviewOwnerQuestions({read,model,modelSha256:sha(read('verification/current-host-docs-review.json'))}),current=JSON.parse(read('verification/current-host-owner-questions.json')),old=JSON.parse(read(registry.before_owners.path));
 assert.deepEqual(current.questions,old.questions.filter(q=>q.id!=='HQ-VAST-TAX-HANDLING'));
 const out=reconcileHostReviewOwnerQuestions({projection:original,finalOwner:p.finalOwner,taxRetirement:p.taxRetirement,model});assert.equal(out.questions.length,10);assert.equal(out.questions.filter(q=>q.presentationKind==='current_publication_conflict').length,3);assert.equal(out.questions.filter(q=>q.presentationKind==='future_detail').length,7);assert.ok(out.questions.every(q=>!q.currentWordingRequiresAnswer));
});
test('missing registry and altered source or current model fail closed',()=>{
 for(const ref of [REG,registry.archive.path,registry.instruction.path,registry.before_owners.path,'host/payment.mdx','docs.json'])assert.throws(()=>projectTaxGuideRetirement({read:p=>p===ref?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift/);
 assert.throws(()=>loadTaxGuideRetirement({read,exists:()=>false,model}),/registry missing/);const wrong=structuredClone(model);wrong.pages[0].claims[0].status='FAIL';assert.throws(()=>loadTaxGuideRetirement({read,exists,model:wrong}),/whole model differs/);
});
