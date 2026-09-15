import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {buildHostReviewQueue, describeHostReview, normalizeSharedWording} from './host_review_work_queue.mjs';
import {buildReport} from './export_host_review_html.mjs';
import {encodeHostReviewPayload, decodeHostReviewPayload} from './host_review_payload.mjs';

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
  // The continuations add 15 Teams/console captions and one Problem Reports caption.
  assert.equal(cohort.length,model.corrections.some(x=>x.id==='HOST-TEAMS-CONSOLE-REVIEW-01')?36:model.corrections.some(x=>x.id==='HOST-DIAGNOSTICS-SSH-REVIEW-01')?33:model.corrections.some(x=>x.id==='HOST-CONTINUATION-REVIEW-01')?32:17);
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
  if(payload.hardware_operator_transition) {
    const review=payload.hardware_operator_transition;assert.equal(review.reviewed_claims,106);assert.equal(review.transition_records,107);assert.equal(review.newly_resolved,105);assert.equal(review.adjacent_pass_consistency_records,1);assert.equal(review.wording_corrections,36);assert.equal(review.corrected_claim_literals,37);assert.equal(review.adjacent_wording_corrections,1);assert.equal(review.uncounted_heading_changes,1);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    for(const artifact of JSON.parse(payload.files[review.registry_ref].text).artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.verification_storage_transition) {
    const review=payload.verification_storage_transition;assert.equal(review.reviewed_claims,175);assert.equal(review.transition_records,176);assert.equal(review.newly_resolved,174);assert.equal(review.adjacent_pass_consistency_records,1);assert.equal(review.wording_corrections,46);assert.equal(review.corrected_claim_literals,47);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    for(const artifact of JSON.parse(payload.files[review.registry_ref].text).artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.recovery_earnings_transition) {
    const review=payload.recovery_earnings_transition;assert.equal(review.reviewed_claims,148);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    for(const artifact of JSON.parse(payload.files[review.registry_ref].text).artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.setup_metrics_transition) {
    const review=payload.setup_metrics_transition;assert.equal(review.reviewed_claims,117);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    for(const artifact of JSON.parse(payload.files[review.registry_ref].text).artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.teams_console_transition) {
    const review=payload.teams_console_transition;assert.equal(review.reviewed_claims,121);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
  }
  if(payload.diagnostics_ssh_transition) {
    const review=payload.diagnostics_ssh_transition;assert.equal(review.reviewed_claims,120);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    for(const artifact of JSON.parse(payload.files[review.registry_ref].text).artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.continuation_transition) {
    const review=payload.continuation_transition;
    assert.equal(review.reviewed_claims,88);
    for(const ref of [review.registry_ref,review.baseline_ref,review.result_ref])assert.ok(payload.files[ref],ref);
    const registry=JSON.parse(payload.files[review.registry_ref].text);
    for(const artifact of registry.artifacts)assert.ok(payload.files[artifact.path],artifact.path);
  }
  if(payload.evidence_reuse_transition) {
    assert.equal(payload.current_result_ref,(payload.final_owner_transition||payload.hardware_operator_transition||payload.verification_storage_transition||payload.recovery_earnings_transition||payload.setup_metrics_transition||payload.teams_console_transition||payload.diagnostics_ssh_transition||payload.continuation_transition||payload.evidence_reuse_transition).result_ref);
    for(const ref of [payload.evidence_reuse_transition.registry_ref,payload.evidence_reuse_transition.baseline_ref,
      payload.evidence_reuse_transition.result_ref,payload.source_family_transition.result_ref,payload.closure_transition.result_ref])assert.ok(payload.files[ref],ref);
    const registry=JSON.parse(payload.files[payload.evidence_reuse_transition.registry_ref].text);
    for(const artifact of registry.artifacts)assert.ok(payload.files[artifact.path],artifact.path);
    assert.deepEqual(payload.issues.sourceFollowUpTopics.flatMap(topic=>topic.claimIds).sort(),payload.issues.sourceFollowUps.map(item=>item.claimId).sort());
    assert.equal(new Set(payload.issues.sourceFollowUps.map(item=>item.claimId)).size,payload.issues.sourceFollowUps.length);
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

test('issues view uses only recorded findings and prerequisites, preserving every fallback and overlapping owner question', async () => {
  const {buildHostReviewIssues} = await import('./host_review_work_queue.mjs');
  const {loadHostReviewOwnerQuestions} = await import('./host_review_owner_questions.mjs');
  const {createHash} = await import('node:crypto');
  const bytes=fs.readFileSync(new URL('verification/current-host-docs-review.json',root));
  const owner=loadHostReviewOwnerQuestions({read:ref=>fs.readFileSync(new URL(ref,root)),model,modelSha256:createHash('sha256').update(bytes).digest('hex')});
  const before=JSON.stringify(model), projection=buildHostReviewIssues({pages:model.pages,ownerQuestions:owner.questions});
  const finalReviewed=model.corrections.some(x=>x.id==='HOST-FINAL-OWNER-REVIEW-01');
  const hardwareReviewed=model.corrections.some(x=>x.id==='HOST-HARDWARE-OPERATOR-REVIEW-01');
  const sourceReviewed=model.corrections.some(x=>x.id==='HOST-VERIFICATION-STORAGE-REVIEW-01');
  assert.deepEqual(projection.counts,{correctionTopics:finalReviewed?0:hardwareReviewed?1:2,correctionPassages:finalReviewed?0:hardwareReviewed?2:3,ownerQuestions:8,publicationConflicts:0,futureDetailQuestions:0,workflowPageGroups:hardwareReviewed?11:sourceReviewed?12:13,recordedProcedures:14,blockedPassages:hardwareReviewed?0:sourceReviewed?5:21});
  assert.deepEqual(projection.corrections.flatMap(group=>group.claimIds).sort(),claims.filter(c=>c.status==='FAIL').map(c=>c.id).sort());
  assert.deepEqual(projection.workflows.flatMap(group=>group.claimIds).sort(),claims.filter(c=>c.status==='BLOCKED').map(c=>c.id).sort());
  const parents=projection.workflows.flatMap(group=>group.procedures);
  assert.equal(parents.filter(procedure=>procedure.status==='FAIL').length,1);
  assert.equal(parents.find(procedure=>procedure.id==='TS-ST-E01').recorded_nodes.filter(node=>node.status==='FAIL').length,4);
  if(finalReviewed)assert.equal(projection.corrections.length,0);else assert.ok(projection.corrections[0].ownerQuestionIds.includes('HQ-VAST-TAX-HANDLING'));
  if(hardwareReviewed)assert.equal(projection.workflows.some(group=>group.unassignedClaimIds.length),false);
  else assert.ok(projection.workflows.some(group=>group.unassignedClaimIds.length));
  assert.equal(JSON.stringify(model),before);
  const fallback=buildHostReviewIssues({pages:[{route:'/host/new',title:'New page',claims:[{...sample,id:'new-block',status:'BLOCKED'}, {...sample,id:'new-uv'}]}],ownerQuestions:[]});
  assert.deepEqual(fallback.workflows[0].unassignedClaimIds,['new-block']);
  assert.deepEqual(fallback.workflows[0].claimIds,['new-block']);
  assert.equal(fallback.corrections.length,0);
  assert.equal(fallback.workflows[0].procedures.length,0);
});

// Execute the entire production script, not a hand-picked function slice. The
// small DOM double exposes the APIs used here; root also checks a real browser.
async function runWholeTemplate(payload,hash='') {
  const template=read('scripts/templates/host-docs-review.html');
  const elements=new Map();
  for(const match of template.matchAll(/<([a-z][\w-]*)\b([^>]*\bid="([^"]+)"[^>]*)>/gi)) {
    if(match[3].includes('${'))continue;
    elements.set(match[3],{id:match[3],tagName:match[1].toUpperCase(),attributes:match[2],hidden:/\bhidden\b/.test(match[2]),textContent:'',innerHTML:'',value:'',style:{},options:[],listeners:{},
      add(option){this.options.push(option);},addEventListener(name,callback){this.listeners[name]=callback;},scrollIntoView(){this.scrolled=true;},showModal(){this.open=true;},close(){this.open=false;},
      querySelector(){return null;},get selectedOptions(){return [{text:this.options.find(option=>option.value===this.value)?.text||this.value||'All'}];}});
  }
  elements.get('report-data').textContent=JSON.stringify(encodeHostReviewPayload(payload));
  elements.get('status').value='OPEN';elements.get('queue-view').value='individual';
  const listeners={},windowListeners={};
  const document={getElementById:id=>elements.get(id)||null,querySelectorAll:selector=>{
    if(selector==='[data-coverage-view]'||selector==='[data-issues-view]')return [...elements.values()].filter(element=>element.attributes.includes(selector.slice(1,-1)));
    return [];
  },addEventListener:(name,callback)=>(listeners[name]??=[]).push(callback)};
  const context=vm.createContext({atob,Blob,Response,DecompressionStream,document,window:{addEventListener:(name,callback)=>(windowListeners[name]??=[]).push(callback),print(){}},location:{hash},URL,
    Option:function(text,value){this.text=text;this.value=value;},console});
  const script=template.match(/<script>\s*([\s\S]*?)<\/script>/)[1]
    .replace('/*__REPORT_DECODER__*/',()=>decodeHostReviewPayload.toString())
    .replace('return report;','Object.assign(globalThis,{handleReviewHash,goToClaims,showWorkflow,showPassage});\nreturn report;');
  vm.runInContext(script,context,{timeout:20000});
  assert.ok(await context.window.hostReviewReady,elements.get('report-init').textContent);
  return {context,elements,listeners,windowListeners};
}

test('whole offline script initializes with preserved owner questions, defaults to issues and keeps all ledger navigation and evidence controls', async () => {
  const before=JSON.stringify(model),{payload}=buildReport();
  const {context,elements}=await runWholeTemplate(payload);
  assert.equal(elements.get('issue-owner-count').textContent,payload.final_owner_transition?'3 + 8':8);
  assert.equal(elements.get('issue-workflow-count').textContent,payload.hardware_operator_transition?11:payload.verification_storage_transition?12:13);
  if(payload.final_owner_transition){assert.match(elements.get('priority-cards').innerHTML,/No current FAIL/);for(const id of ['HOST-AMD-LISTING-COMPATIBILITY','HOST-CPU-ARCHITECTURE-REQUIREMENTS','HOST-TEAM-EARNINGS-PAYOUT-POLICY'])assert.ok(elements.get('issue-owner-list').innerHTML.includes(id));}else assert.match(elements.get('priority-cards').innerHTML,/CUR-11f83626486ada1d/);
  assert.match(elements.get('issue-owner-list').innerHTML,/HQ-RENTAL-AVAILABILITY/);
  if(payload.hardware_operator_transition)assert.doesNotMatch(elements.get('issue-workflow-list').innerHTML,/page-based fallback/);
  else assert.match(elements.get('issue-workflow-list').innerHTML,/page-based fallback/);
  assert.equal(elements.get('issue-source-count').textContent,payload.issues.sourceFollowUpTopics.length);
  for(const topic of payload.issues.sourceFollowUpTopics) {
    assert.ok(elements.get('issue-source-list').innerHTML.includes(topic.title.replaceAll('&','&amp;')));
    for(const id of topic.claimIds)assert.ok(elements.get('issue-source-list').innerHTML.includes(`data-issue-claim="${id}"`),id);
  }
  assert.equal(elements.has('correction-progress'),false,'a historical 26-item queue is not overall project progress');
  assert.doesNotMatch(read('scripts/templates/host-docs-review.html'),/of \$\{issues\.originalFindings\.total\}/);
  assert.equal(elements.get('coverage').hidden,true);
  assert.equal(elements.get('claims').hidden,true);
  assert.equal(elements.get('overview').hidden,false);
  assert.equal(elements.get('coverage-unvalidated').textContent,(model.counts.claim_statuses.UNVALIDATED||0).toLocaleString());
  vm.runInContext("location.hash='#claims';handleReviewHash();",context);
  assert.equal(elements.get('claims').hidden,false);
  assert.equal(elements.get('overview').hidden,true);
  vm.runInContext("location.hash='#claim-CUR-11f83626486ada1d';handleReviewHash();",context);
  assert.match(elements.get('results-count').textContent,/1 matching passages/);
  assert.match(elements.get('claim-list').innerHTML,/data-passage="CUR-11f83626486ada1d"/);
  vm.runInContext("location.hash='#overview';handleReviewHash();",context);
  assert.equal(elements.get('claims').hidden,true);
  vm.runInContext("goToClaims();showWorkflow('workflow:/host/how-to-self-test');",context);
  assert.equal(elements.get('claims').hidden,false);
  assert.match(elements.get('viewer-body').innerHTML,/TS-ST-E01/);
  assert.match(elements.get('viewer-body').innerHTML,/Open source page/);
  if(payload.hardware_operator_transition){
    assert.match(elements.get('viewer-body').innerHTML,/Recorded procedure status: FAIL/);
    const instruction=payload.claims.find(c=>c.id==='MCL-eeaf6da83da9eca7');
    assert.equal(instruction.status,'PASS');
    assert.equal(payload.authority_scan.transitions[instruction.id].previous.status,'BLOCKED');
    assert.match(payload.authority_scan.transitions[instruction.id].previous.rationale,/preflight|reliability/i);
    assert.ok(payload.files['verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/selftest-normal-preflight-01.json']);
  }else assert.match(elements.get('viewer-body').innerHTML,/preflight|reliability/i);
  assert.match(elements.get('viewer-body').innerHTML,/data-artifact=/);
  vm.runInContext("showPassage('CUR-11f83626486ada1d');",context);
  assert.match(elements.get('viewer-body').innerHTML,/source-line highlight/);
  assert.equal(JSON.stringify(model),before);
});
