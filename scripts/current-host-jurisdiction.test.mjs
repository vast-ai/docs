import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
import {loadCurrentHostReviewTransition} from './current_host_review_transition.mjs';
import {JURISDICTION_PATH,JURISDICTION_BASELINE,JURISDICTION_IDS,loadJurisdiction,projectJurisdiction} from './current_host_jurisdiction.mjs';
import {buildReport} from './export_host_review_html.mjs';

const root=new URL('../',import.meta.url),read=ref=>fs.readFileSync(new URL(ref,root)),exists=ref=>fs.existsSync(new URL(ref,root));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const CLEANUP_PATH='verification/current-host-review-cleanup.json';
const CLEANUP_PREDECESSOR='verification/evidence/2026-09-11-host-review-cleanup-attempt-01/before-current-host-docs-review.json';
const model=()=>JSON.parse(read('verification/current-host-docs-review.json'));
const jurisdictionModel=()=>JSON.parse(read(exists(CLEANUP_PREDECESSOR)?CLEANUP_PREDECESSOR:'verification/current-host-docs-review.json'));
const registry=JSON.parse(read(JURISDICTION_PATH));
const byId=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c])));

test('JavaScript projection equals the sealed cleanup predecessor and changes only eight claims',()=>{
 const result=projectJurisdiction({read,exists}),current=jurisdictionModel();assert.deepEqual(result.model,current);
 assert.deepEqual(current.counts.claim_statuses,{BLOCKED:23,FAIL:35,NOT_APPLICABLE:13,PASS:241,UNVALIDATED:1701});
 const before=byId(JSON.parse(read(JURISDICTION_BASELINE))),after=byId(current);
 for(const [id,claim] of before)if(!JURISDICTION_IDS.has(id))assert.deepEqual(after.get(id),claim,id);
 assert.equal(before.size-JURISDICTION_IDS.size,2005);
 for(const id of JURISDICTION_IDS){assert.equal(after.get(id).status,'PASS');assert.ok(result.presentation.get(id).auditHistory.length);assert.deepEqual(result.presentation.get(id).previous,before.get(id));}
 for(const [ref,digest]of result.artifactHashes)assert.equal(hash(read(ref)),digest,ref);
});

test('all new registry, source, capture, raw and predecessor pins reject modification',()=>{
 const refs=[JURISDICTION_PATH,JURISDICTION_BASELINE,...registry.sources.flatMap(s=>[s.path,s.before_artifact.path]),...registry.artifacts.map(a=>a.path),...registry.retained_raw_sources.map(a=>a.path),'host/payment.mdx','verification/current-host-terms-binding.json'];
 for(const target of refs)assert.throws(()=>projectJurisdiction({read:ref=>ref===target?Buffer.concat([read(ref),Buffer.from(' ')]):read(ref),exists}),undefined,target);
});

test('missing current registry/model and unrelated current claim drift fail closed',()=>{
 const hidden=ref=>{if(ref===JURISDICTION_PATH)throw Error('missing');return read(ref)};
 assert.throws(()=>loadJurisdiction({read:hidden,model:jurisdictionModel(),exists:ref=>ref!==JURISDICTION_PATH&&exists(ref)}),/has no registry/);
 assert.throws(()=>loadCurrentHostReviewTransition({read,model:{},exists}),/whole model differs/);
 const modified=model();byId(modified).get('CUR-99fb8d131e321e03').status='PASS';
 assert.throws(()=>loadCurrentHostReviewTransition({read,model:modified,exists}),/whole model differs/);
 for(const id of JURISDICTION_IDS){const changed=model();byId(changed).get(id).source_refs=[];assert.throws(()=>loadCurrentHostReviewTransition({read,model:changed,exists}),/whole model differs/);}
});

test('optional registry preserves the sealed historical Terms reader through frozen source overlays',()=>{
 const original=new Map(registry.sources.map(s=>[s.path,read(s.before_artifact.path)]));
 const historicalRead=ref=>{if(ref===CLEANUP_PATH||ref===JURISDICTION_PATH)throw Error('historical fixture has no successor registry');return original.get(ref)||read(ref)};
 const loaded=loadCurrentHostReviewTransition({read:historicalRead,model:JSON.parse(read(JURISDICTION_BASELINE)),exists:ref=>ref!==CLEANUP_PATH&&ref!==JURISDICTION_PATH&&exists(ref)});
 assert.ok(loaded.terms);assert.equal(loaded.jurisdiction,undefined);assert.equal(loaded.terms.registry.transitions.length,6);
});

test('actual offline source controls expose every exact new basis and preserve current passage scope',()=>{
 const {payload,html}=buildReport();assert.equal(payload.jurisdiction_transition.changed_claims,8);
 assert.equal(payload.current_result_ref,payload.cleanup_transition?.result_ref||payload.jurisdiction_transition.result_ref);
 const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
 const functions=script.slice(script.indexOf('function authorityScanHTML('),script.indexOf('function twoDefectTransitionHTML('));
 const escapeHTML=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 const claims=new Map(payload.claims.map(c=>[c.id,c]));let selected='';
 const context=vm.createContext({report:payload,claimMap:claims,escapeHTML,pill:()=>'',showDialog:(_title,text)=>selected=text});vm.runInContext(functions,context);
 for(const id of JURISDICTION_IDS){
  const claim=claims.get(id),transition=payload.authority_scan.transitions[id];context.claim=claim;
  const card=vm.runInContext('authorityScanHTML(claim)',context);
  for(const [index,basis]of transition.basis.entries()){
   assert.ok(card.includes('data-basis="'+index+'"'));assert.ok(payload.files[basis.artifactRef]);
   context.selectedId=id;context.selector=index;vm.runInContext('showSourceBasis(selectedId,selector)',context);
   assert.ok(selected.includes(escapeHTML(basis.excerpt)));assert.ok(selected.includes(escapeHTML(basis.sourceLabel)));assert.ok(selected.includes(escapeHTML(basis.text_pointer)));
   assert.ok(selected.includes(escapeHTML(claim.text)));if(basis.sourceUrl)assert.ok(selected.includes(escapeHTML(basis.sourceUrl)));
  }
  const before=selected;context.selector=999;vm.runInContext('showSourceBasis(selectedId,selector)',context);assert.equal(selected,before);
 }
});
