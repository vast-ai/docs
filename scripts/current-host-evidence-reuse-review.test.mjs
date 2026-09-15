import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {projectEvidenceReuseReview,loadEvidenceReuseReview,EVIDENCE_REUSE_PATH as REG,EVIDENCE_REUSE_SHA256 as PIN,EVIDENCE_REUSE_ATTEMPT as A} from './current_host_evidence_reuse_review.mjs';
import {beforeContinuation,beforeEvidenceReuse} from './closure_historical_test_sources.mjs';
const rawRead=p=>fs.readFileSync(new URL('../'+p,import.meta.url)),read=beforeContinuation(rawRead),exists=p=>{try{read(p);return true;}catch(error){if(error.code==='ENOENT')return false;throw error;}};
const registry=JSON.parse(read(REG)),model=JSON.parse(read('verification/current-host-docs-review.json')),before=JSON.parse(beforeEvidenceReuse(read)('verification/current-host-docs-review.json'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),index=x=>new Map(x.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),old=index(before),claims=index(model),omit=(o,ks)=>Object.fromEntries(Object.entries(o).filter(([k])=>!ks.includes(k))),at=(o,p)=>p.slice(1).split('/').reduce((v,k)=>v[k],o);
async function reseal(change){const r=structuredClone(registry);change(r);const bytes=Buffer.from(JSON.stringify(r));const source=read('scripts/current_host_evidence_reuse_review.mjs').toString().replace(PIN,sha(bytes)).replace("'./current_host_source_family_review.mjs'",JSON.stringify(new URL('./current_host_source_family_review.mjs',import.meta.url).href));const m=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));return ()=>m.projectEvidenceReuseReview({read:p=>p===REG?bytes:read(p),exists});}
test('318 scoped decisions have exact Python/JS parity and preserve all1690 unselected claims apart from spans',()=>{
 const js=projectEvidenceReuseReview({read,exists});assert.deepEqual(js.model,model);assert.deepEqual(loadEvidenceReuseReview({read,exists,model}).model,model);
 const py=JSON.parse(execFileSync('python3',['-c',"import json,sys;from pathlib import Path;sys.path.insert(0,'scripts');import current_host_evidence_reuse_review as m;r=Path.cwd();paths=[r/'verification/current-host-teams-console-review.json',r/'verification/current-host-diagnostics-ssh-review.json',r/'verification/current-host-continuation-review.json'];overrides={s['path']:(r/s['before_artifact']['path']).read_bytes() for p in paths if p.exists() for s in json.loads(p.read_text())['sources']};print(json.dumps(m.project(r,frozen_source_overrides=overrides)))"],{cwd:new URL('../',import.meta.url),maxBuffer:24*1024*1024}));assert.deepEqual(py,model);
 assert.deepEqual(model.counts.claim_statuses,{BLOCKED:21,FAIL:3,NOT_APPLICABLE:91,PASS:1042,UNVALIDATED:851});assert.equal(claims.size,2008);
 const selected=new Set(registry.transitions.map(t=>t.claim_id));assert.equal(selected.size,318);let unaffected=0;
 for(const[id,c]of claims){const p=old.get(id);if(!selected.has(id)){assert.deepEqual(omit(c,['spans']),omit(p,['spans']),id);unaffected++;continue;}
  assert.deepEqual(omit(c.history,['evidence_reuse_review']),p.history,id);assert.equal(c.history.evidence_reuse_review.prior_status,p.status);
  for(const key of ['evidence_refs','source_refs'])for(const ref of p[key])assert.ok(c[key].some(e=>JSON.stringify(e)===JSON.stringify(ref)),id);
 }
 assert.equal(unaffected,1690);assert.equal(registry.transitions.filter(t=>t.decision==='correction').length,47);
 assert.equal(js.sourceFamily.registry.transitions.length,358);assert.ok(js.closure&&js.presentation&&js.evidenceReuse);
 for(const id of ['CUR-f992e392221fe492','CUR-1de91e8c48307d8b']){assert.equal(old.get(id).status,'FAIL');assert.equal(claims.get(id).status,'PASS');assert.equal(claims.get(id).history.source_family_review.prior_status,'UNVALIDATED');}
 assert.equal(claims.get('MCL-9ad33b25fd88c5cb').status,'FAIL');
});
test('73 pointer-keyed procedure span patches retain every status and evidence; only approved postcheck comment changes',()=>{
 assert.equal(registry.procedures.length,73);const record=JSON.parse(read(A+'/procedure-context-comparison-02.json'));assert.equal(record.all_procedure_statuses_and_evidence_unchanged,true);
 for(const e of registry.procedures){const p=at(before,e.model_pointer),c=at(model,e.model_pointer);assert.deepEqual(omit(c,['spans','history','coverage_state','nodes']),omit(p,['spans','history','coverage_state','nodes']));assert.deepEqual(c.history.evidence_reuse_review.prior_spans,p.spans);}
 const changes=record.comparisons.filter(x=>!x.fence_bytes_unchanged);assert.equal(changes.length,1);assert.equal(changes[0].id,'CLM-6391e55bdef1e3cc');assert.equal(changes[0].executable_command_bytes_unchanged,true);
 const priorOwners=JSON.parse(execFileSync('git',['show','61fbb472fadd1c9242a34fae14b67ddf0eb3f376:verification/current-host-owner-questions.json'],{cwd:new URL('../',import.meta.url)}));assert.deepEqual(omit(JSON.parse(read('verification/current-host-owner-questions.json')),['model_sha256']),omit(priorOwners,['model_sha256']));
});
test('current sources, adjacent scope, entire historical proof and source excerpts fail closed under tampering',async()=>{
 for(const ref of [REG,registry.scope.path,A+'/adjacent-scope.json',A+'/supplemental-scope-02.json',registry.sources[0].path,registry.sources[0].before_artifact.path,registry.artifacts[0].path,'verification/current-host-source-family-review.json'])assert.throws(()=>projectEvidenceReuseReview({read:p=>p===ref?Buffer.concat([read(p),Buffer.from('\n')]):read(p),exists}),/digest drift|digest mismatch/);
 const changed=structuredClone(model);changed.pages[0].claims[0].rationale+=' changed';assert.throws(()=>loadEvidenceReuseReview({read,exists,model:changed}),/whole model differs/);
 let run=await reseal(r=>r.transitions[0].basis[0].excerpt+=' unsupported');assert.throws(run,/selector\/excerpt drift/);
 run=await reseal(r=>r.transitions.find(t=>t.after.status==='UNVALIDATED').after.status='PASS');assert.throws(run,/accepted disposition drift/);
 run=await reseal(r=>r.transitions.pop());assert.throws(run,/transition scope/);
 run=await reseal(r=>r.procedures[0].after.status='PASS');assert.throws(run,/unaccepted procedure change/);
 run=await reseal(r=>r.transitions.find(t=>t.residual_topic).residual_topic={key:'invented',title:'invented'});assert.throws(run,/unaccepted residual topic/);
});
