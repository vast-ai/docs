import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {buildHostReviewQueue, describeHostReview, normalizeSharedWording} from './host_review_work_queue.mjs';
import {buildReport} from './export_host_review_html.mjs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');
const model = JSON.parse(read('verification/current-host-docs-review.json'));
const claims = model.pages.flatMap(page => page.claims.map(claim => ({...claim,route:page.route,page_title:page.title})));
const sample = {id:'ONE',text:'Check the link.',headings:['Guide'],status:'UNVALIDATED',classification:'REVIEWED_NAVIGATION_INSTRUCTION',required_evidence_types:['REPOSITORY_STATIC_CHECK'],owner_role:'Documentation',rationale:'Check the destination.',next_action:'Check the link.',evidence_refs:[],source_refs:[],spans:[]};
const camel = value => Array.isArray(value) ? value.map(camel) : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).map(([key,item]) => [key.replace(/_([a-z])/g,(_,c)=>c.toUpperCase()),camel(item)])) : value;

test('production readers separate review type and pending status and expose an actionable queue', () => {
  const offline = read('scripts/templates/host-docs-review.html');
  const live = read('review-server.mjs');
  assert.match(offline, /UNVALIDATED:'Review pending'/);
  assert.match(live, /UNVALIDATED: 'Review pending'/);
  assert.match(offline, /id="work-queue-summary"/);
  assert.match(offline, /Review type:/);
  assert.match(live, /Review type:/);
  assert.match(live, /current-work-filter/);
});

test('every current occurrence belongs to exactly one actionable category; support layers stay separate', () => {
  const before = JSON.stringify(claims), queue = buildHostReviewQueue(claims);
  assert.equal(queue.total, model.counts.claims);
  assert.equal(queue.buckets.reduce((sum,bucket)=>sum+bucket.count,0), claims.length);
  assert.deepEqual(queue.statuses, model.counts.claim_statuses);
  const ids = queue.groups.flatMap(group=>group.occurrenceIds);
  assert.equal(new Set(ids).size, claims.length);
  assert.deepEqual([...ids].sort(),claims.map(claim=>claim.id).sort());
  assert.equal(JSON.stringify(claims),before);
  assert.equal(queue.buckets.find(b=>b.id==='triage').count,0,'new current classes need explicit review mapping');
  assert.equal(queue.buckets.find(b=>b.id==='completed').count,claims.filter(c=>['PASS','NOT_APPLICABLE'].includes(c.status)).length);
  const cohort=claims.filter(c=>['PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION','PUBLICATION_DESCRIPTION','PUBLISHED_TERMS_SUMMARY','REVIEWED_UI_PROVIDER_OPTION'].includes(c.classification));
  assert.equal(cohort.length,11);
  assert.ok(cohort.every(c=>describeHostReview(c).completed&&!describeHostReview(c).needsTriage));
  assert.equal(cohort.filter(c=>c.classification==='REVIEWED_UI_PROVIDER_OPTION').every(c=>describeHostReview(c).type==='Technical behavior or workflow'),true);
  assert.equal(cohort.filter(c=>c.classification!=='REVIEWED_UI_PROVIDER_OPTION').every(c=>describeHostReview(c).type==='Published source or rule'),true);
});

test('offline and live field names produce identical categories, status counts and shared-wording groups', () => {
  assert.deepEqual(buildHostReviewQueue(claims.map(camel)),buildHostReviewQueue(claims));
  for(const claim of claims) assert.deepEqual(describeHostReview(camel(claim)),describeHostReview(claim));
});

test('review type is independent of completion status and pending does not imply runtime work', () => {
  for(const status of ['UNVALIDATED','FAIL','BLOCKED','PASS','NOT_APPLICABLE'])assert.equal(describeHostReview({...sample,status}).type,'Navigation');
  assert.equal(describeHostReview(sample).statusLabel,'Review pending');
  assert.equal(describeHostReview(sample).bucket,'documentation');
  assert.equal(describeHostReview({...sample,required_evidence_types:['CANONICAL_IMPLEMENTATION_SOURCE']}).bucket,'source');
  assert.equal(describeHostReview({...sample,classification:'RUNTIME_BEHAVIOR',required_evidence_types:['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION']}).bucket,'technical');
  assert.equal(describeHostReview({...sample,status:'FAIL'}).bucket,'correction');
  assert.equal(describeHostReview({...sample,status:'BLOCKED'}).bucket,'blocked');
});

test('unknown types, statuses, lanes and missing requirements visibly require triage', () => {
  for(const change of [{classification:'NEW_SECURITY_FACT'},{status:'APPROVED'},{required_evidence_types:['UNKNOWN_PROOF']},{required_evidence_types:null},{classification:'RUNTIME_BEHAVIOR',required_evidence_types:[]}]) {
    const work=describeHostReview({...sample,...change});assert.equal(work.bucket,'triage');assert.equal(work.completed,false);
  }
  assert.equal(describeHostReview({...sample,status:'PASS',classification:'NEW_SECURITY_FACT'}).bucket,'triage');
  assert.equal(describeHostReview({...sample,status:'UNVALIDATED',classification:'PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION',required_evidence_types:['AUTHORITATIVE_DOCUMENTATION_CITATION']}).completed,false);
  assert.equal(describeHostReview({...sample,status:'FAIL',classification:'REVIEWED_UI_PROVIDER_OPTION',required_evidence_types:['RUNTIME_OR_UI_OBSERVATION']}).bucket,'correction');
  assert.throws(()=>buildHostReviewQueue([sample,sample]),/distinct passage IDs/);
});

test('shared wording only groups compatible open work and preserves exact individual IDs', () => {
  const other={...sample,id:'TWO',route:'/other'};
  const queue=buildHostReviewQueue([sample,other]);
  assert.deepEqual(queue.groups[0].occurrenceIds,['ONE','TWO']);assert.equal(queue.sharedWordingGroups,1);assert.equal(queue.sharedWordingOccurrences,2);
  assert.equal(normalizeSharedWording('  Run  CMD\r\n next  '),'  Run  CMD\n next  ');
  assert.notEqual(normalizeSharedWording('cmd \\ \nnext'),normalizeSharedWording('cmd \\\nnext'));
  for(const change of [
    {text:'check the link.'},{text:'Check the link. '},{text:'Check  the link.'},{status:'BLOCKED'},{classification:'REVIEWED_ADVICE'},
    {required_evidence_types:['CANONICAL_IMPLEMENTATION_SOURCE']},{owner_role:'Operator'},
    {prerequisite:'A different permission'},{rationale:'A different gap'},{next_action:'A different question'},
    {headings:['Different context']},{evidence_refs:[{id:'partial',limit:'Partial only',artifact_ref:'partial.json'}]},
    {source_refs:[{path:'other-source',locator:'different passage'}]},
  ]) assert.equal(buildHostReviewQueue([sample,{...other,...change}]).sharedWordingGroups,0,JSON.stringify(change));
  for(const status of ['PASS','NOT_APPLICABLE'])assert.equal(buildHostReviewQueue([{...sample,status},{...other,status}]).sharedWordingGroups,0);
});

test('export carries the shared queue without changing any claim status, lanes, text or source controls', () => {
  const {payload,html}=buildReport();
  assert.deepEqual(payload.work_queue,buildHostReviewQueue(claims));
  for(const [index,claim] of payload.claims.entries()) {
    assert.deepEqual(claim.review_work,describeHostReview(claims[index]));
    assert.equal(claim.status,claims[index].status);
    assert.deepEqual(claim.required_evidence_types,claims[index].required_evidence_types);
    assert.deepEqual(claim.spans,claims[index].spans);
  }
  assert.equal(payload.support_layers.length,model.support_layers.length);
  assert.match(html,/data-passage=/);assert.match(html,/Evidence & next action/);assert.match(html,/data-basis=/);
  assert.match(html,/Shared wording is not one proven fact|not one proven fact/);
  if(payload.cleanup_transition && !payload.payout_invoice_transition) {
    assert.equal(payload.current_result_ref,payload.cleanup_transition.result_ref);
    for(const ref of [payload.cleanup_transition.registry_ref,payload.cleanup_transition.baseline_ref,...payload.cleanup_transition.context_refs])assert.ok(payload.files[ref],ref);
  }
});

test('production offline filters and grouped rendering retain every matching passage and independent proof controls', () => {
  const template=read('scripts/templates/host-docs-review.html');
  const source=template.slice(template.indexOf('function applyFilters('),template.indexOf('function reset()'));
  const items=[sample,{...sample,id:'TWO'},{...sample,id:'THREE',status:'FAIL',rationale:'Different gap'}].map(c=>({...c,route:'/test',page_title:'Test',review_work:describeHostReview(c)}));
  const controls=Object.fromEntries(['search','page','status','lane','owner','work-category','queue-view','claim-list','results-count','page-count','prev','next','print-selection'].map(id=>[id,{value:'',selectedOptions:[{text:''}]}]));
  controls.status.value='ALL';controls['queue-view'].value='shared';
  const context={report:{claims:items},workQueue:buildHostReviewQueue(items),claimMap:new Map(items.map(c=>[c.id,c])),pageIndex:0,pageSize:20,filtered:[],printing:false,
    $:id=>controls[id],escapeHTML:s=>s,sourceTypes:[],openStatus:c=>!['PASS','NOT_APPLICABLE'].includes(c.status),citationDefect:()=>false,
    renderClaim:c=>`<article id="claim-${c.id}"><button data-passage="${c.id}">Show passage</button><details><summary>Evidence & next action</summary></details></article>`};
  vm.runInNewContext(source+'\napplyFilters();',context);
  assert.match(controls['claim-list'].innerHTML,/Shared wording: 2 passages/);
  for(const item of items)assert.equal(controls['claim-list'].innerHTML.split(`id="claim-${item.id}"`).length,2,item.id);
  assert.match(controls['results-count'].textContent,/3 matching passages/);
  controls['work-category'].value='correction';vm.runInNewContext(source+'\napplyFilters();',context);
  assert.match(controls['claim-list'].innerHTML,/claim-THREE/);assert.doesNotMatch(controls['claim-list'].innerHTML,/claim-ONE|claim-TWO/);
});
