import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import test from 'node:test';
import {CLEANUP_BASELINE, CLEANUP_BASELINE_SHA256, CLEANUP_PATH, loadReviewCleanup, projectReviewCleanup} from './current_host_review_cleanup.mjs';
import {projectJurisdiction} from './current_host_jurisdiction.mjs';

const root=new URL('../',import.meta.url);
const read=ref=>fs.readFileSync(new URL(ref,root));
const exists=ref=>fs.existsSync(new URL(ref,root));
const current=()=>JSON.parse(read('verification/current-host-docs-review.json'));
const byId=model=>new Map(model.pages.flatMap(page=>page.claims.map(claim=>[claim.id,claim])));

test('sealed cleanup projects the actual current 151-transition model',()=>{
 const projected=projectReviewCleanup({read,exists});
 assert.deepEqual(current(),projected.model);
 assert.equal(projected.cleanup.registry.transitions.length,151);
 assert.deepEqual(projected.model.counts.claim_statuses,{PASS:308,UNVALIDATED:1560,NOT_APPLICABLE:87,FAIL:35,BLOCKED:23});
 assert.equal(loadReviewCleanup({read,model:current(),exists}).cleanup.registrySha256,projected.cleanup.registrySha256);
});

test('jurisdiction predecessor is not accepted as cleanup current model',()=>{
 const predecessor=JSON.parse(read(CLEANUP_BASELINE));
 assert.throws(()=>loadReviewCleanup({read,model:predecessor,exists}),/whole model differs/);
});

test('cleanup baseline is the pinned jurisdiction projection, not actual cleanup current',()=>{
 const baseline=JSON.parse(read(CLEANUP_BASELINE));
 assert.equal(crypto.createHash('sha256').update(read(CLEANUP_BASELINE)).digest('hex'),CLEANUP_BASELINE_SHA256);
 assert.deepEqual(baseline,projectJurisdiction({read,exists}).model);
 assert.notDeepEqual(baseline,current());
});

test('registry, predecessor, raw candidate, fresh checks, and wrapper pins reject drift',()=>{
 const registry=JSON.parse(read(CLEANUP_PATH));
 const wrapper=JSON.parse(read(registry.artifacts[0].path));
 const refs=[CLEANUP_PATH,CLEANUP_BASELINE,registry.artifacts[0].path,wrapper.source_candidate.path,...wrapper.support_artifacts.map(item=>item.path)];
 for(const target of refs)assert.throws(()=>projectReviewCleanup({read:ref=>ref===target?Buffer.concat([read(ref),Buffer.from(' ')]):read(ref),exists}),undefined,target);
});

test('arbitrary unselected mutation and fake PASS fail the exact projected-model gate',()=>{
 const registry=JSON.parse(read(CLEANUP_PATH));
 const selected=new Set(registry.transitions.map(item=>item.claim_id));
 const changed=current(),claims=byId(changed);
 const unselected=[...claims.values()].find(claim=>!selected.has(claim.id));
 unselected.rationale+=' tampered';
 assert.throws(()=>loadReviewCleanup({read,model:changed,exists}),/whole model differs/);
 const fake=current();
 const unvalidated=[...byId(fake).values()].find(claim=>claim.status==='UNVALIDATED');
 unvalidated.status='PASS';
 assert.throws(()=>loadReviewCleanup({read,model:fake,exists}),/whole model differs/);
});
