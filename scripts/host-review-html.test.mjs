import {projectHardwareOperatorReview} from './current_host_hardware_operator_review.mjs';
import {projectVerificationStorageReview} from './current_host_verification_storage_review.mjs';
import {projectRecoveryEarningsReview} from './current_host_recovery_earnings_review.mjs';
import {projectSetupMetricsReview} from './current_host_setup_metrics_review.mjs';
import {projectTeamsConsoleReview} from './current_host_teams_console_review.mjs';
import {projectDiagnosticsSshReview} from './current_host_diagnostics_ssh_review.mjs';
import {projectContinuationReview} from './current_host_continuation_review.mjs';
import {projectEvidenceReuseReview} from './current_host_evidence_reuse_review.mjs';
import {beforeContinuation,beforeDiagnosticsSsh,beforeTeamsConsole,beforeSetupMetrics,beforeRecoveryEarnings,beforeVerificationStorage,beforeHardwareOperator,beforeFinalOwner} from './closure_historical_test_sources.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';
import { buildReport, sanitize, sanitizeArtifact } from './export_host_review_html.mjs';
import {readEmbeddedHostReviewPayload, decodeHostReviewPayload, encodeHostReviewPayload} from './host_review_payload.mjs';
import {projectClosureCorrection} from './current_host_closure_correction.mjs';
import {projectSourceFamilyReview} from './current_host_source_family_review.mjs';
import {hostReviewReaderCopy} from './host_review_reader_copy.mjs';

const {html,payload,manifest}=buildReport();
const app=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const model=JSON.parse(fs.readFileSync(new URL('../verification/current-host-docs-review.json',import.meta.url)));
const inputClaims=model.pages.flatMap(p=>p.claims);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const currentResultTransition=payload.tax_retirement_transition||payload.final_owner_transition||payload.hardware_operator_transition||payload.verification_storage_transition||payload.recovery_earnings_transition||payload.setup_metrics_transition||payload.teams_console_transition||payload.diagnostics_ssh_transition||payload.continuation_transition||payload.evidence_reuse_transition||payload.source_family_transition||payload.closure_transition||payload.payout_invoice_transition||payload.payout_terms_transition||payload.payout_provider_transition||payload.cleanup_transition||payload.jurisdiction_transition||payload.terms_transition;
const jurisdictionIds=new Map([
 ['CUR-708c718cf735c8b2','Advice checked'],['CUR-555543e9b2ceddb4','Advice checked'],['CUR-2ead4eda972e84b0','Advice checked'],
 ['MCL-8fe2020c0e7efe26','Advice and rule checked'],
 ['MCL-1536a1bd58d80927','Published program source checked'],['MCL-c9882f043e407640','Published program source checked'],
 ['MCL-c8bf23127171e2b0','Published program source checked'],['MCL-3acecd71e6a7b312','Published program source checked'],
]);

test('all current occurrences retain identity, status, source and bounded text',()=>{
 assert.equal(payload.claims.length,model.counts.claims);
 assert.equal(payload.pages.length,model.counts.primary_pages);
 assert.equal(payload.support_layers.length,33);
 for(const [i,c] of payload.claims.entries()){
  const original=inputClaims[i];
  assert.equal(c.id,original.id);assert.equal(c.status,original.status);
  assert.equal(c.text,sanitize(original.text));
  assert.deepEqual(c.spans,original.spans);
  assert.equal(c.rationale,sanitize(original.rationale));
  assert.equal(c.next_action,typeof original.next_action==='string'?sanitize(original.next_action):original.next_action);
  assert.deepEqual(c.required_evidence_types,original.required_evidence_types);
 }
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
});
test('workstream totals and historical PASS scopes agree with records',()=>{
 const open=payload.claims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status));
 assert.equal(open.length,inputClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status)).length);
 for(const type of ['RUNTIME_OR_UI_OBSERVATION','CANONICAL_IMPLEMENTATION_SOURCE','ACCOUNTABLE_OWNER_CONFIRMATION','AUTHORITATIVE_DOCUMENTATION_CITATION']) assert.equal(open.filter(c=>c.required_evidence_types.includes(type)).length,inputClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status)&&c.required_evidence_types.includes(type)).length);
 const pass=payload.claims.filter(c=>c.status==='PASS');
 assert.equal(pass.filter(c=>c.history.carry_decision==='CARRIED_FORWARD_EXACT_SOURCE').length,inputClaims.filter(c=>c.status==='PASS'&&c.history.carry_decision==='CARRIED_FORWARD_EXACT_SOURCE').length);
 assert.equal(pass.filter(c=>c.history.carry_decision!=='CARRIED_FORWARD_EXACT_SOURCE').length,inputClaims.filter(c=>c.status==='PASS'&&c.history.carry_decision!=='CARRIED_FORWARD_EXACT_SOURCE').length);
});
test('six bounded Terms citations are source-only PASS cards with no acknowledgement request',()=>{
 if(!payload.terms_transition)return;
 const ids=new Set(['MCL-99ca28f707d5966a','MCL-2c3f7082e2c7fdf2','MCL-c4c4bfc59eb7b49f','MCL-399798a3c4946b5f','MCL-633317ca7ebecfef','MCL-fe3eccd1cd40b4bd']);
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
 assert.equal(payload.terms_transition.changed_claims,ids.size);
 assert.equal(payload.current_result_ref,currentResultTransition.result_ref);
 assert.equal(payload.terms_transition.source_path,'host/workload-policy.mdx');
 assert.ok(payload.files[payload.terms_transition.registry_ref]);
 assert.ok(payload.files[payload.terms_transition.source_before_ref]);
 for(const ref of payload.terms_transition.capture_refs)assert.ok(payload.files[ref],ref);
 const selected=payload.claims.filter(claim=>ids.has(claim.id));
 assert.equal(selected.length,ids.size);
 for(const claim of selected){
  assert.equal(claim.status,'PASS',claim.id);assert.deepEqual(claim.required_evidence_types,['AUTHORITATIVE_DOCUMENTATION_CITATION'],claim.id);
  assert.equal(claim.reader_copy.reviewKind,'published-terms-source',claim.id);
  assert.match(claim.reader_copy.finding,/does not prove runtime enforcement/i,claim.id);
  assert.equal(claim.reader_copy.nextStep,'Recheck if the wording or cited source changes.',claim.id);
  assert.equal(claim.reader_copy.pendingNote,undefined,claim.id);
  assert.ok(claim.source_refs.some(ref=>ref.path==='https://vast.ai/terms'),claim.id);
  assert.ok(claim.evidence_refs.some(ref=>payload.terms_transition.capture_refs.includes(ref.artifact_ref)),claim.id);
 }
 assert.match(html,/https:\/\/vast\.ai\/terms/);
 assert.doesNotMatch(html,/Captured Hosting Agreement source/);
});
test('eight jurisdiction source and advice cards retain exact labels, current sources and selectable source controls',()=>{
 if(!payload.jurisdiction_transition)return;
 const jurisdiction=payload.jurisdiction_transition;
 assert.equal(jurisdiction.changed_claims,8);
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
 assert.equal(payload.current_result_ref,currentResultTransition.result_ref);
 assert.equal(jurisdiction.registry_ref,'verification/current-host-jurisdiction.json');
 for(const ref of [jurisdiction.registry_ref,jurisdiction.baseline_ref,...jurisdiction.capture_refs,...jurisdiction.sources.map(source=>source.before_artifact.path)])assert.ok(payload.files[ref],ref);
 const registry=JSON.parse(payload.files[jurisdiction.registry_ref].text);
 assert.deepEqual(registry.transitions.map(row=>row.claim_id).sort(),[...jurisdictionIds.keys()].sort());
 const selected=payload.claims.filter(claim=>jurisdictionIds.has(claim.id));
 assert.equal(selected.length,8);
 const sourceFunctions=app.slice(app.indexOf('function authorityScanHTML('),app.indexOf('function twoDefectTransitionHTML('));
 const escapeHTML=value=>String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 let shown;const context={report:payload,claimMap:new Map(payload.claims.map(claim=>[claim.id,claim])),escapeHTML,pill:status=>status,showDialog:(title,body)=>{shown={title,body};}};
 for(const claim of selected){
  const decision=registry.transitions.find(row=>row.claim_id===claim.id),label=jurisdictionIds.get(claim.id);
  assert.equal(claim.status,'PASS',claim.id);assert.equal(claim.reader_copy.statusLabel,label,claim.id);assert.equal(claim.reader_copy.label,label,claim.id);
  assert.deepEqual(claim.required_evidence_types,decision.after.required_evidence_types,claim.id);
  assert.deepEqual(claim.source_refs,decision.after.source_refs,claim.id);
  const transition=payload.authority_scan.transitions[claim.id];
  assert.equal(transition.registryRef,jurisdiction.registry_ref,claim.id);assert.equal(transition.basis.length,decision.basis.length,claim.id);
  const controls=vm.runInNewContext(sourceFunctions+'\nauthorityScanHTML(claim);',{...context,claim});
  for(const [index,basis]of transition.basis.entries()){
   assert.ok(controls.includes(`data-basis="${index}" data-context="${claim.id}"`),claim.id);
   assert.ok(controls.includes(escapeHTML(basis.sourceLabel)),claim.id);
   shown=null;vm.runInNewContext(sourceFunctions+`\nshowSourceBasis(${JSON.stringify(claim.id)},${JSON.stringify(String(index))});`,context);
   assert.equal(shown.title,basis.kind==='CONTEXT_REVIEW'?'Review note — not an independent source':'Exact bound source excerpt',claim.id);
   assert.ok(shown.body.includes(basis.kind==='CONTEXT_REVIEW'?'Review scope:':'What this source proves:'),claim.id);
   assert.ok(shown.body.includes(escapeHTML(basis.excerpt)),claim.id);
   assert.ok(shown.body.includes(escapeHTML(basis.support_rationale)),claim.id);
   if(basis.sourceUrl)assert.ok(shown.body.includes(`href="${escapeHTML(basis.sourceUrl)}"`),claim.id);
  }
 }
});
test('current reviewed residuals show their actual source scope without claiming proof',()=>{
 const sourceFunctions=app.slice(app.indexOf('function authorityScanHTML('),app.indexOf('function twoDefectTransitionHTML('));
 const escapeHTML=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const selected=payload.claims.filter(claim=>{const scan=payload.authority_scan?.transitions[claim.id];return (scan?.sourceFamily||scan?.evidenceReuse||scan?.continuation||scan?.diagnosticsSsh||scan?.teamsConsole||scan?.setupMetrics||scan?.recoveryEarnings||scan?.verificationStorage||scan?.hardwareOperator||scan?.finalOwner)&&['FAIL','UNVALIDATED'].includes(claim.status);});
 assert.deepEqual(selected.map(claim=>claim.id).sort(),[
  'MCL-b106578dbaccc269','MCL-1221941af8a7a4fe',
  'MCL-d8c581b080df635b','MCL-c569a7d52ef2d67c','MCL-14fafb4770a2b16f','MCL-71aa2b81147538fb',
  'CUR-99fb8d131e321e03','CUR-c8657007c73f9603','CUR-b66a8e30a355a76e','MCL-a313bdc48d3cfd1d','MCL-68656ca5b481d313',
  'MCL-dd01d426b53b2e5f','MCL-5413b0eb68620dc3','MCL-9ad33b25fd88c5cb',
  'CUR-718eae8798859de8','CUR-2a4d8f7b6bf42c0c','CUR-0186c37202bd5029','CUR-1da68c391b45b80a','CUR-ac44298a51ffb285','MCL-d7643ee2685f24ec',
 ].filter(id=>!payload.continuation_transition||id!=='CUR-c8657007c73f9603').filter(id=>!payload.diagnostics_ssh_transition||id!=='MCL-1221941af8a7a4fe').filter(id=>!payload.teams_console_transition||!['MCL-68656ca5b481d313','CUR-b66a8e30a355a76e','MCL-a313bdc48d3cfd1d'].includes(id)).concat(payload.teams_console_transition?['MCL-f426518c26948ea1','MCL-350d25401b2594d2','MCL-ff0e592ec9d37394','MCL-fe79b15ff39543a3']:[]).concat(payload.recovery_earnings_transition?['MCL-b5b2716c025774a3']:[]).filter(id=>!payload.verification_storage_transition||!['MCL-b106578dbaccc269','MCL-d7643ee2685f24ec','CUR-0186c37202bd5029','CUR-2a4d8f7b6bf42c0c','CUR-718eae8798859de8','CUR-ac44298a51ffb285'].includes(id)).filter(id=>!payload.hardware_operator_transition||!['MCL-d8c581b080df635b','MCL-c569a7d52ef2d67c','MCL-14fafb4770a2b16f','MCL-71aa2b81147538fb','MCL-dd01d426b53b2e5f','MCL-5413b0eb68620dc3','MCL-9ad33b25fd88c5cb'].includes(id)).concat(payload.hardware_operator_transition?['MCL-6842b63298275c23']:[]).filter(id=>!payload.final_owner_transition||!JSON.parse(payload.files[payload.final_owner_transition.registry_ref].text).transitions.some(t=>t.claim_id===id)).sort());
 if(payload.diagnostics_ssh_transition){
  for(const id of ['MCL-1221941af8a7a4fe','MCL-6b3a48733434c5e5']){const c=payload.claims.find(c=>c.id===id);assert.equal(c.status,'PASS');assert.ok(payload.authority_scan.transitions[id].diagnosticsSsh);assert.ok(payload.authority_scan.transitions[id].basis.some(b=>b.kind==='OPERATOR_PUBLISHED_REFERENCE'));}
  assert.ok(payload.files[payload.diagnostics_ssh_transition.incident_follow_up_ref]);assert.match(app,/Open operator reference/);
 }
 if(payload.continuation_transition){
  const notification=payload.claims.find(c=>c.id==='CUR-c8657007c73f9603');
  assert.equal(notification.status,'PASS');assert.ok(payload.authority_scan.transitions[notification.id].continuation);
 }
 for(const claim of selected){
  const scan=payload.authority_scan.transitions[claim.id],basis=scan.basis[0];
  let shown;const context={report:payload,claim,claimMap:new Map([[claim.id,claim]]),escapeHTML,pill:status=>status,showDialog:(_,body)=>{shown=body;}};
  const card=vm.runInNewContext(sourceFunctions+'\nauthorityScanHTML(claim);',context);
  assert.match(card,/Source scope:/);assert.ok(card.includes(escapeHTML(claim.rationale)));
  assert.doesNotMatch(card,/What (?:the|this) source proves/);
  vm.runInNewContext(sourceFunctions+`\nshowSourceBasis(${JSON.stringify(claim.id)},'0');`,context);
  assert.match(shown,/Source scope:/);assert.ok(shown.includes(escapeHTML(claim.rationale)));
  assert.doesNotMatch(shown,/What (?:the|this) source proves/);
  assert.ok(shown.includes(escapeHTML(basis.excerpt)));
  assert.ok(shown.includes(payload.files[basis.artifactRef].sha256));
  assert.ok(shown.includes(escapeHTML(scan.remaining)));
 }
});
test('all citation-lane FAIL records are visibly distinct from the two documentation defects',()=>{
 const citation=c=>c.status==='FAIL'&&c.required_evidence_types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION');
 const citationClaims=payload.claims.filter(citation);
 const readonlyFindings=JSON.parse(fs.readFileSync(new URL('../verification/current-host-readonly-findings.json',import.meta.url)));
 assert.equal(citationClaims.length,inputClaims.filter(citation).length);
 if(!payload.authority_scan)assert.equal(citationClaims.length,151);
 assert.equal(readonlyFindings.findings.filter(f=>f.status==='FAIL'&&f.classification==='CONFIRMED_DOCUMENTATION_DEFECT').length,2);
 if(payload.final_owner_transition){assert.equal(citationClaims.length,0);const previous=Object.values(payload.authority_scan.transitions).filter(t=>t.finalOwner).map(t=>t.previous).filter(citation);assert.equal(previous.length,2);assert.ok(previous.some(c=>!c.rationale.startsWith('CONFIRMED_CITATION_DEFECT:')));}else assert.ok(citationClaims.some(c=>!c.rationale.startsWith('CONFIRMED_CITATION_DEFECT:')),'alternate citation wording stays visible');
 assert.match(html,/const citationDefect=c=>c\.status==='FAIL'&&c\.required_evidence_types\.includes\('AUTHORITATIVE_DOCUMENTATION_CITATION'\)/);
 assert.match(html,/Missing authoritative citation \(\$\{citationDefects\.length\.toLocaleString\(\)\} FAIL\)/);
 assert.match(html,/lane==='citation'\?citationDefect\(c\)/);
 assert.match(html,/The required source citation is missing or incomplete\./);
 assert.match(html,/Existing published authority can suffice/);
 assert.match(html,/The required source citation is missing or incomplete\. Link the official source for this statement\./);
 assert.doesNotMatch(html,/This does not mean a runtime test failed\./);
 assert.doesNotMatch(html,/c\.rationale\.startsWith\('CONFIRMED_CITATION_DEFECT:'/);
});
test('current cards suppress old findings and bookkeeping controls',()=>{
 assert.doesNotMatch(app,/Original finding|Previous finding|Exact predecessor wording|Open frozen|Open bounded authority registry|Open runtime adjudication record|c\.history\.reason|c\.history\.carry_decision/);
 assert.match(app,/function bookkeepingEvidence/);
 assert.match(app,/Current finding/);
});

test('offline legend separates source, advice, runtime and static-link review',()=>{
 for(const phrase of ['What this review is asking for','Basic descriptions:','Policy:','Advice:','Settings and declarations:','Behavior and outcomes:','Links and navigation:'])assert.match(html,new RegExp(phrase));
 assert.match(html,/a working link does not prove its page/i);
 assert.match(html,/Reading a draft is not approval/);
 const checker=fs.readFileSync(new URL('./check_host_review_html.mjs',import.meta.url),'utf8');
 assert.match(checker,/2026-09-10-host-\(\?:policy-acknowledgement\|clarification-sweep\|terms-binding\|split-review\)-attempt-01/);
 assert.match(checker,/const selectedIds=new Set/);
 assert.doesNotMatch(checker,/selected\.length!==7/);
});

test('typed reader reviews have taxonomy-specific empty-evidence wording',()=>{
 assert.match(html,/function readerEvidenceFallback\(c\)/);
 assert.match(html,/kind\.startsWith\('policy'\)/);
 assert.match(html,/wording and advice review, not a product test/);
 assert.match(html,/static link and wording review/);
 assert.match(html,/No retained result is attached for the claimed behavior/);
 assert.match(html,/technical declaration needs an exact source/);
 assert.doesNotMatch(html,/c\.reader_copy\?\.reviewKind\?'<p>This is a policy review/);
 assert.match(html,/clarification-method-note/);
 assert.match(html,/clarificationTransition\?\.changed_claims/);
 assert.match(html,/This updates what to check, not the product evidence or statuses/);
 assert.match(html,/<h4>What this review needs<\/h4>/);
 assert.doesNotMatch(html,/What would establish this statement\?/);
});

test('authority transitions expose the hash-bound exact predecessor, while a new atom has none',()=>{
 const baseline='verification/evidence/2026-09-09-host-authority-correction-attempt-01/pre-authority-current-host-docs-review.json';
 const digest='8b24aad067b2d98d41cd1824a31a831fa88f9a9cfaa8cb39379c6c37839bdaf9';
 assert.equal(payload.files[baseline].sha256,digest);
 const frozen=JSON.parse(payload.files[baseline].text);
 const predecessors=new Map(frozen.pages.flatMap(page=>page.claims).map(claim=>[claim.id,claim]));
 const phaseClaims=payload.authority_scan?JSON.parse(payload.files[payload.authority_scan.baseline_ref].text).pages.flatMap(page=>page.claims):payload.claims;
 for(const id of ['MCL-508003945b6ef934','MCL-805ef8a72833f2b8','MCL-f855ff5e92cfbec1']){
  const current=phaseClaims.find(claim=>claim.id===id),previous=predecessors.get(current.history.baseline_claim_id);
  assert.equal(current.history.carry_decision,'CURRENT_HOST_AUTHORITY_SOURCE_TRANSITION');
  assert.ok(previous,`missing predecessor for ${id}`);assert.notEqual(previous.status,current.status);
  assert.notEqual(previous.text,current.text);
 }
 const newAtom=phaseClaims.find(claim=>claim.id==='AUTH-DATA-SECURITY-01');
 assert.equal(newAtom.history.baseline_claim_id,null);assert.equal(predecessors.has(newAtom.id),false);
 assert.match(html,/authorityBaselineSha256='8b24aad067b2d98d41cd1824a31a831fa88f9a9cfaa8cb39379c6c37839bdaf9'/);
 assert.match(html,/const authorityPredecessors=/);
 assert.doesNotMatch(app,/Previous finding|Exact predecessor wording|Open full frozen model/);
});
test('supplemental live checks retain exact versus partial scope without changing claim status',()=>{
 const supplemental=payload.supplemental_live_checks;
 assert.equal(supplemental.mapped_claims.length,20);
 assert.deepEqual(supplemental.summary,{host_checks:20,cli_checks:21,api_checks:6,total_checks:47,
  note:'Six direct API reads: three Market Metrics endpoints plus selected-machine, maintenance and reports reads. Only the three Market Metrics endpoint-description claims have separate API PASS adjudications. All 15 documented Market Metrics CLI examples also ran; those are separate command observations, not additional API-claim closures.'});
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
 const hardware=supplemental.mapped_claims.find(c=>c.claim_id==='MCL-a43d2c31e8cfcd4f');
 assert.equal(hardware.coverage.level,'PARTIAL');assert.equal(hardware.checks.length,9);
 const market=supplemental.mapped_claims.filter(c=>c.route==='/host/market-metrics');
 assert.deepEqual(market.map(c=>c.checks.length),[3,7,5]);
 assert.equal(market.reduce((total,c)=>total+c.checks.length,0),15);
 for(const record of supplemental.mapped_claims){
  assert.ok(!('status' in record));assert.ok(!('baseline_status' in record));
  for(const check of record.checks)assert.ok(payload.files[check.artifact_ref],check.artifact_ref);
 }
 assert.ok(payload.files['verification/evidence/2026-09-08-host-live-readonly-attempt-01/check-to-claim-map.json']);
});
test('supplemental map rejects current source-text drift',()=>{
 const original=fs.readFileSync;
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-live-readonly-attempt-01/check-to-claim-map.json')){
   const map=JSON.parse(original(file,'utf8'));map.records[0].text+=' drift';return Buffer.from(JSON.stringify(map));
  }
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Supplemental source text\/span drift/);}finally{fs.readFileSync=original;}
});
test('current read-only map binds exact claims and capture digests without adjudicating status',()=>{
 const current=payload.current_readonly_checks;
 assert.equal(current.mapped_claims.length,8);
 assert.equal(payload.current_result_ref,currentResultTransition?.result_ref|| (payload.authority_scan?'verification/evidence/2026-09-09-host-authority-scan-attempt-01/result.md':'verification/evidence/2026-09-09-host-authority-correction-attempt-01/result.md'));
 assert.equal(payload.claim_correction_history_ref,'verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/result.md');
 assert.equal(payload.historical_summary_ref,'verification/evidence/2026-09-08-host-client-unblocking-attempt-01/result.md');
 assert.equal(payload.earlier_baseline_summary_ref,'verification/evidence/2026-09-07-host-current-vv-attempt-01/result.md');
 assert.match(current.summary,/do not grant paid, self-test or VM-mutation authority/i);
 for(const record of current.mapped_claims){
  const claim=inputClaims.find(c=>c.id===record.claim_id);
  assert.ok(claim,record.claim_id);assert.ok(!('status' in record));assert.ok(!('baseline_status' in record));
  assert.equal(record.route,model.pages.find(p=>p.claims.some(c=>c.id===record.claim_id)).route);
  for(const check of record.checks)assert.ok(payload.files[check.artifact_ref],check.artifact_ref);
 }
 const defaultSearch=current.mapped_claims.find(c=>c.claim_id==='MCL-728ef13be833d21e');
 assert.deepEqual(defaultSearch.checks.map(c=>c.id),['HOST-05','CLIENT-03']);
 const rawSearch=current.mapped_claims.find(c=>c.claim_id==='MCL-a54378e7f20b92e9');
 assert.deepEqual(rawSearch.checks.map(c=>c.id),['HOST-06','CLIENT-04','CLIENT-07']);
 const local=current.mapped_claims.find(c=>c.claim_id==='MCL-9ad33b25fd88c5cb');
 assert.match(local.limit,/0644/);assert.match(local.limit,/No real credential/i);
 assert.equal(current.mapped_claims.some(c=>c.claim_id==='MCL-dfebca7edafe9c59'),false);
 const off=current.historical_superseded.find(c=>c.historical_claim_id==='MCL-dfebca7edafe9c59');
 assert.equal(off.status,'FAIL');assert.match(off.limit,/inconclusive/i);assert.doesNotMatch(off.limit,/VM support is disabled\.$/);
 assert.match(off.context,/Historical FAIL retained/);assert.equal(off.transition_ref,'verification/current-two-defect-transition.json');
 const vmCheck=current.mapped_claims.find(c=>c.claim_id==='MCL-53020aef5be19505');
 assert.equal(vmCheck.route,'/host/vms');assert.ok(!('status' in vmCheck));
 assert.doesNotMatch(app,/Historical VM finding|historical context only; it does not prove VM support is disabled/);
 const retry=current.mapped_claims.find(c=>c.claim_id==='MCL-60ec9280a68ab6d7');
 assert.match(retry.coverage.level,/PARTIAL_NOT_POST_ENABLE/);
 for(const ref of ['account-observations-01.json','vm-helper-source-retest-02.json','local-key-storage-limitations-02.json'])assert.ok(payload.files[`verification/evidence/2026-09-08-host-client-unblocking-attempt-01/${ref}`]);
});
test('current authority summary is not mislabeled as new operational execution',()=>{
 if(payload.jurisdiction_transition){assert.match(app,/jurisdictionActive/);assert.match(app,/const latestChecks=evidenceReuseActive[\s\S]*: sourceFamilyActive[\s\S]*: payoutInvoiceActive[\s\S]*: payoutTermsActive[\s\S]*: report\.payout_provider_transition[\s\S]*: report\.cleanup_transition[\s\S]*: jurisdictionActive/);}
 if(payload.payout_invoice_transition){assert.match(app,/Published payout and invoice guidance/);assert.match(app,/does not test invoice generation or payment processing/);}
 if(payload.payout_terms_transition){assert.match(app,/Published payout Terms and FAQ guidance/);assert.match(app,/backend\/runtime behavior/);}
 if(payload.payout_provider_transition){assert.match(app,/Evidence update: 14 Sep 2026/);assert.match(app,/No payment, fee, account-state or bank-transfer rule was verified/);}
 assert.match(app,/Published Terms source check/);assert.match(app,/This source check adds no runtime execution/);
 assert.match(app,/Current full-inventory review/);assert.match(app,/Source review adds no runtime execution/);
 assert.doesNotMatch(app,/const latestChecks=\[\['Bounded operational evidence/);
 if(payload.source_family_transition){
  const elements={'evidence-update-label':{},'check-rows':{}};
  vm.runInNewContext(app.slice(app.indexOf('const jurisdictionActive='),app.indexOf("$('support-rows')")),{report:payload,$:id=>elements[id],escapeHTML:value=>String(value)});
  assert.equal(elements['evidence-update-label'].textContent,'Evidence update: 15 Sep 2026');
  const rows=elements['check-rows'].innerHTML;
  assert.match(rows,/358 passages reviewed; 69 wording corrections/);
  assert.ok(rows.includes(`data-artifact="${payload.source_family_transition.result_ref}"`));
  assert.ok(rows.includes(`data-artifact="${payload.closure_transition.result_ref}"`));
  if(payload.evidence_reuse_transition){
   assert.ok(rows.includes(`data-artifact="${payload.evidence_reuse_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.evidence_reuse_transition.reviewed_claims} passages reviewed; ${payload.evidence_reuse_transition.wording_corrections} wording corrections`));
   assert.match(rows,/Earlier source-family review/);
  }
  if(payload.hardware_operator_transition){
   assert.ok(rows.includes(`data-artifact="${payload.hardware_operator_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.hardware_operator_transition.reviewed_claims} passages reviewed; ${payload.hardware_operator_transition.wording_corrections} wording corrections`));
  }
  if(payload.verification_storage_transition){
   assert.ok(rows.includes(`data-artifact="${payload.verification_storage_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.verification_storage_transition.reviewed_claims} passages reviewed; ${payload.verification_storage_transition.wording_corrections} wording corrections`));
  }
  if(payload.recovery_earnings_transition){
   assert.ok(rows.includes(`data-artifact="${payload.recovery_earnings_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.recovery_earnings_transition.reviewed_claims} passages reviewed; ${payload.recovery_earnings_transition.wording_corrections} wording corrections`));
  }
  if(payload.setup_metrics_transition){
   assert.ok(rows.includes(`data-artifact="${payload.setup_metrics_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.setup_metrics_transition.reviewed_claims} passages reviewed; ${payload.setup_metrics_transition.wording_corrections} wording corrections`));
  }
  if(payload.continuation_transition){
   assert.ok(rows.includes(`data-artifact="${payload.continuation_transition.result_ref}"`));
   assert.ok(rows.includes(`${payload.continuation_transition.reviewed_claims} passages reviewed; ${payload.continuation_transition.wording_corrections} wording corrections`));
   assert.match(rows,/read-only console observations/);
  }
  assert.match(rows,/Earlier correction and evidence review/);
  assert.doesNotMatch(rows,/Published payout and invoice guidance/);
 }
});

test('current result and two registers replace dated aggregate history in the visible report',()=>{
 assert.ok(payload.files[payload.current_result_ref]);
 assert.ok(payload.files[payload.claim_correction_history_ref],'immutable internal history remains validated');
 assert.match(html,/id="runtime-register"/);assert.match(html,/id="source-register"/);
 assert.doesNotMatch(app,/Dated September|Historical September|earlierBaselineChecks|historical-checks|repository-reconciliation|failure-chain/);
});

test('HTML payload keeps all six current connection rows exact and the historical search refs visible',()=>{
 const rows=new Map(payload.claims.filter(c=>[
  'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT','MCL-4c49eaf437cfa29e','MCL-1ebb3e6e2b370757',
  'MCL-3fb43d8a410371df','MCL-da591d84b7d08317','MCL-eeaf6da83da9eca7',
 ].includes(c.id)).map(c=>[c.id,c]));
 assert.deepEqual([...rows].map(([id,c])=>[id,c.status]).sort(),[
  ['COR-01-MCL-323c8fb8180f5f62-REPLACEMENT','PASS'],['MCL-4c49eaf437cfa29e','PASS'],
  ['MCL-1ebb3e6e2b370757',payload.hardware_operator_transition?'PASS':'BLOCKED'],['MCL-3fb43d8a410371df','PASS'],
  ['MCL-da591d84b7d08317','PASS'],['MCL-eeaf6da83da9eca7',payload.hardware_operator_transition?'PASS':'BLOCKED'],
 ].sort());
 for(const id of ['MCL-3fb43d8a410371df','MCL-da591d84b7d08317']){
  assert.equal(payload.authority_scan.transitions[id].previous.status,'UNVALIDATED');
  assert.equal(payload.authority_scan.transitions[id].evidenceReuse,true);
 }
 const search=rows.get('COR-01-MCL-323c8fb8180f5f62-REPLACEMENT');
 assert.equal(search.history.carry_decision,'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
 assert.ok(search.evidence_refs.some(r=>r.id==='CLI-QUERY-SOURCE-INSPECTION-01'));
 assert.ok(search.evidence_refs.some(r=>r.id==='CONNECTION-COR-01-MCL-323c8fb8180f5f62-REPLACEMENT-01'));
 for(const row of rows.values())assert.ok(row.evidence_refs.some(r=>r.artifact_ref==='verification/current-host-connection-adjudications.json'));
});
test('current read-only map rejects source and capture drift',()=>{
 const original=fs.readFileSync;
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-client-unblocking-attempt-01/check-to-claim-map.json')){
   const map=JSON.parse(original(file,'utf8'));map.records[0].headings=['drift'];return Buffer.from(JSON.stringify(map));
  }
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Current source text\/span drift/);}finally{fs.readFileSync=original;}
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-client-unblocking-attempt-01/cli-execution-01.json'))return Buffer.from('{"records":[]}');
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Current capture hash drift|authority scan: digest drift/);}finally{fs.readFileSync=original;}
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/current-two-defect-transition.json'))return Buffer.from(`${original(file,'utf8')}\n`);
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Two-defect transition registry hash drift|authority scan: digest drift/);}finally{fs.readFileSync=original;}
});
test('offline inventory summary takes current counts from the embedded payload',()=>{
 const template=fs.readFileSync(new URL('./templates/host-docs-review.html',import.meta.url),'utf8');
 assert.match(template,/id="inventory-summary"/);
 assert.match(template,/report\.counts\.procedures/);assert.match(template,/report\.counts\.procedure_nodes/);
 assert.match(template,/report\.counts\.page_coverage_states\?\.CHANGED/);
 assert.doesNotMatch(template,/110 procedure records \/ 1,047 nodes/);
 assert.match(template,/id="evidence-update-label">Evidence update: 9 Sep 2026/);
 assert.match(template,/termsActive.*evidence-update-label.*10 Sep 2026/);
 if(payload.jurisdiction_transition)assert.match(template,/jurisdictionActive.*evidence-update-label.*11 Sep 2026/);
 assert.match(template,/Presentation updated 15 Sep 2026\. Evidence dates are shown with their sources\./);
 assert.match(template,/Fetch the current/);
 assert.doesNotMatch(template,/have <strong>not been pushed<\/strong>|At the 8 Sep 2026 check/);
 assert.doesNotMatch(template,/signed payload/);
});
test('route and accessibility reconciliation is embedded, bounded, and readable',()=>{
 const attempt='verification/evidence/2026-09-09-host-repository-live-merge-attempt-01';
 const refs={
  generated_routes_ref:`${attempt}/generated-route-reconciliation-01.json`,
  mint_links_ref:`${attempt}/mint-links-post-exclusion-02.json`,
  mint_accessibility_ref:`${attempt}/mint-a11y-retest-01.json`,
  rendered_theme_ref:`${attempt}/rendered-theme-token-01.json`,
 };
 assert.deepEqual(payload.repository_reconciliation,refs);
 for(const ref of Object.values(refs))assert.ok(payload.files[ref],ref);
 const routes=JSON.parse(fs.readFileSync(new URL('../'+refs.generated_routes_ref,import.meta.url),'utf8'));
 const routeReport=JSON.parse(routes.stdout);
 assert.equal(routes.exit_code,0);assert.equal(routeReport.reportedTargetCount,85);
 assert.ok(routeReport.results.every(result=>result.status===200&&result.finalUrlMatchesCanonical&&result.canonicalTitleMatches&&result.passed));
 assert.equal(routeReport.negativeControl.status,404);assert.equal(routeReport.negativeControl.passed,true);
 const links=JSON.parse(fs.readFileSync(new URL('../'+refs.mint_links_ref,import.meta.url),'utf8'));
 assert.equal(links.exit_code,1);assert.match(links.stdout,/found 99 broken links in 10 files/i);
 const a11y=JSON.parse(fs.readFileSync(new URL('../'+refs.mint_accessibility_ref,import.meta.url),'utf8'));
 assert.equal(a11y.exit_code,1);assert.match(a11y.stdout,/4\.53:1[\s\S]*meets WCAG AA/i);assert.match(a11y.stdout,/Found 74 accessibility issues in 19 files/);
 const theme=JSON.parse(fs.readFileSync(new URL('../'+refs.rendered_theme_ref,import.meta.url),'utf8'));
 assert.equal(theme.exit_code,0);assert.deepEqual(JSON.parse(theme.stdout),{dark:true,primaryLight:'63 109 255',scope:'Rendered token adoption only; not a full accessibility audit'});
 assert.doesNotMatch(app,/Open generated-route reconciliation|Open Mint static link report|Open accessibility retest|Open rendered color-token check/);
 assert.doesNotMatch(html,/99 inherited broken links/);
});
test('current report suppresses pre-install intake history without changing internal observations',()=>{
 assert.match(payload.installation_evidence_intake.message,/USD 0\.01\/GB in both directions/);
 assert.doesNotMatch(app,/Historical pre-install selected observation|H100×4 direct-install observations|Earlier USD 1\/GB/);
 assert.match(app,/Selected direct post-install runtime observation/);
});

test('four direct runtime adjudications select only their pinned post-install observations',()=>{
 const expected=[
  ['MCL-ead93c85c2ff4168','POST-03','GPU_INVENTORY_4_H100'],
  ['MCL-82fa8860fe3ef124','POST-01','FOUR_SERVICES_ACTIVE'],
  ['MCL-2f9f572d80e1e8f9','POST-05','DOCKER_XFS_PROJECT_QUOTA'],
  ['MCL-aa383ba37f55f306','POST-07','PROJECT_QUOTA_ON'],
 ];
 for(const [claim,post,predicate] of expected){assert.match(html,new RegExp(`${claim}.*${post}.*${predicate}`));}
 for(const label of ['View GPU visibility result','View service-status result','View Docker filesystem result','View project-quota result'])assert.ok(html.includes(label),label);
 assert.match(html,/directPostinstallRegistry/);
 assert.match(html,/if\(direct&&\(!c\.evidence_refs\.some/);
 assert.match(html,/checkId!==direct\.observationId/);
});
test('a current read-only PASS uses its current next action in either proof layer',()=>{
 // Historical maps are immutable observation records. A later current-status
 // adjudication must take precedence over their older “still adjudicate” next.
 assert.match(app,/const next=c\.next_action/);
 assert.doesNotMatch(html,/kind==='current'&&c\.status==='PASS'/);
});
test('all ten readonly registry carriers expose exact retained observations, including the source-only occurrence',()=>{
 const registry=JSON.parse(fs.readFileSync(new URL('../verification/current-host-readonly-adjudications.json',import.meta.url)));
 assert.equal(payload.readonly_command_proofs.length,10);
 for(const entry of registry.adjudications){
  const proof=payload.readonly_command_proofs.find(item=>item.claim_id===entry.claim_id);
  assert.ok(proof,entry.claim_id);assert.equal(proof.limit,sanitize(entry.limits));
  assert.deepEqual(proof.checks.map(check=>check.id),entry.checks.map(check=>check.check_id));
  for(const check of proof.checks){const raw=JSON.parse(payload.files[check.artifact_ref].text);const selected=raw.records.find(item=>item.check_id===check.id);assert.equal(selected.exit_code,0);assert.ok(check.recorded_at);}
 }
 const sourceOnly=payload.readonly_command_proofs.find(item=>item.claim_id==='MCL-aa735864a1cb734d');
 assert.equal(sourceOnly.coverage.level,'SOURCE_ONLY');
 const supplementalFunction=app.split('\n').find(line=>line.startsWith('function supplementalHTML('));
 const result=vm.runInNewContext(supplementalFunction+'\nsupplementalHTML({id:"MCL-aa735864a1cb734d"});',{
  readonlyCommandByClaim:new Map([[sourceOnly.claim_id,sourceOnly]]),supplementalByClaim:new Map(),currentReadonlyByClaim:new Map(),proofHTML:(_claim,proof)=>proof.checks.map(check=>check.id).join(',')});
 assert.equal(result,'D01');
});
test('official publication source links are clickable only for the retained publication allowlist',()=>{
 const sourceFunction=app.slice(app.indexOf('function sourceHTML('),app.indexOf('function proofHTML('));
 const source={repository:'official-publication',source_kind:'AUTHORITATIVE_DOCUMENTATION_CITATION',revision:'sha256:'+'a'.repeat(64),path:'https://cloud.vast.ai/host/agreement',locator:'/sections/6/text'};
 const context={source,escapeHTML:s=>String(s)};
 assert.match(vm.runInNewContext(sourceFunction+'\nsourceHTML(source);',context),/href="https:\/\/cloud\.vast\.ai\/host\/agreement"/);
 source.path='https://vast.ai/terms';const terms=vm.runInNewContext('sourceHTML(source);',context);assert.match(terms,/href="https:\/\/vast\.ai\/terms"/);assert.match(terms,/Vast Terms/);
 source.path='javascript:alert(1)';assert.doesNotMatch(vm.runInNewContext('sourceHTML(source);',context),/href=/);
});
test('server source-reference guard accepts only the exact bound Terms pointer list',()=>{
 const server=fs.readFileSync(new URL('../review-server.mjs',import.meta.url),'utf8');
 const helper=server.slice(server.indexOf('function currentReviewSourceRefs('),server.indexOf('function currentReviewHistory('));
 const ids=['MCL-2c3f7082e2c7fdf2','MCL-c4c4bfc59eb7b49f'];
 const selected=inputClaims.filter(claim=>ids.includes(claim.id));
 const termsArtifact='verification/evidence/2026-09-10-host-terms-binding-attempt-01/terms-source-01.json';
 const scan={
  matches:new Map(selected.map(claim=>[claim.id,{claim}])),
  presentation:new Map(selected.map(claim=>[claim.id,{basis:claim.source_refs.filter(ref=>ref.path==='https://vast.ai/terms').flatMap(ref=>ref.locator.split('; ').map(text_pointer=>({sourceUrl:'https://vast.ai/terms',artifactRef:termsArtifact,text_pointer})))}])),
  artifactHashes:new Map([[termsArtifact,selected[0].source_refs.find(ref=>ref.path==='https://vast.ai/terms').revision.slice(7)]]),
 };
 const context={CURRENT_AUTHORITY_SCAN:scan,currentReviewExactArray:value=>value,vvExactKeys:()=>{},currentReviewText:value=>{if(typeof value!=='string')throw Error('text');return value;},Error};
 for(const claim of selected)assert.doesNotThrow(()=>vm.runInNewContext(helper+`\ncurrentReviewSourceRefs(${JSON.stringify(claim.source_refs)},'source guard',${JSON.stringify(claim.id)});`,context),claim.id);
 const altered=structuredClone(selected[0].source_refs);altered[0].locator='/sections/0/items/0/text; /sections/0/items/3/text; /sections/0/items/4/text; /sections/0/items/8/text';
 assert.throws(()=>vm.runInNewContext(helper+`\ncurrentReviewSourceRefs(${JSON.stringify(altered)},'source guard',${JSON.stringify(selected[0].id)});`,context),/source guard/);
});
test('all evidence and source passage references are embedded with digests',()=>{
 for(const c of payload.claims){
  for(const e of c.evidence_refs)assert.ok(payload.files[e.artifact_ref],e.artifact_ref);
  for(const s of c.spans){const f=payload.files[s.source_file];assert.ok(f);assert.ok(s.start>=1&&s.end<=f.text.split('\n').length);}
 }
 for(const f of Object.values(payload.files)){
  const raw=fs.readFileSync(new URL('../'+(f.historical_source_ref||f.ref),import.meta.url));
  assert.equal(f.sha256,hash(raw));assert.equal(f.display_sha256,hash(f.text));
  assert.equal(f.masked,raw.toString('utf8')!==f.text);
  if(f.ref.startsWith('host/')||f.ref.startsWith('snippets/'))assert.equal(raw.toString('utf8').split('\n').length,f.text.split('\n').length,'source line numbers must survive masking');
  assert.ok(!f.ref.includes('private-evidence')&&!f.ref.includes('.orchestra'));
 }
});
test('gzip embedding preserves the entire decoded JSON without executable data and stays below the existing 100 MiB limit',async()=>{
 const data=html.match(/<script id="report-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
 assert.equal(JSON.parse(data).encoding,'gzip-base64');
 assert.deepEqual(await readEmbeddedHostReviewPayload(html),payload);
 assert.ok(Buffer.byteLength(html)<100*1024*1024);
 assert.ok(!data.includes('<')&&!data.includes('>')&&!data.includes('&'));
 assert.equal((html.match(/<script\b/g)||[]).length,2);
 for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))assert.doesNotThrow(()=>new vm.Script(m[1]));
});
test('malformed encoding and unsupported decompression fail with a visible offline initialization message',async()=>{
 for(const envelope of [{encoding:'unknown',data:'AAAA'},{encoding:'gzip-base64',data:'!!!'},{encoding:'gzip-base64',data:'AAAA'}]) {
  await assert.rejects(()=>decodeHostReviewPayload(envelope));
 }
 const notice={textContent:'Loading',hidden:false};
 const context=vm.createContext({window:{},document:{getElementById:id=>id==='report-data'?{textContent:JSON.stringify(encodeHostReviewPayload({}))}:notice},DecompressionStream:undefined});
 vm.runInContext(app,context);
 assert.equal(await context.window.hostReviewReady,null);
 assert.equal(notice.hidden,false);
 assert.match(notice.textContent,/could not be opened.*cannot decompress/);
});
test('single-file report has no remote assets or network code',()=>{
 assert.doesNotMatch(html,/<(?:script|img|iframe)\b[^>]*\bsrc=/i);
 assert.doesNotMatch(html,/<link\b[^>]*\bhref=/i);
 const app=html.match(/<script>([\s\S]*?)<\/script>/)[1];
 assert.doesNotMatch(app,/\b(?:fetch|XMLHttpRequest|WebSocket|eval)\s*\(/);
 assert.match(html,/connect-src 'none'/);
});
test('display sanitizer removes selected restricted forms without changing source data',()=>{
 for(const s of ['/Users/reviewer/work/private.md','someone@internal.invalid','machine_id: 987654','10.1.2.3','Authorization: Bearer exampleCredentialValue']) assert.ok(sanitize(s).includes('[redacted'));
 assert.equal(sanitize('vastai set api-key <API_KEY>'),'vastai set api-key <API_KEY>');
 assert.equal(sanitize('http://127.0.0.1:4000'),'http://127.0.0.1:4000');
});
test('JSON evidence masking preserves escapes, source formatting and numeric identifier redaction',()=>{
 const source={code:'\n@parser.command(\n    help="Show team members"\n)',path:'/Users/example/private-notes',email:'someone@private.example',machine_id:654321,instance_id:'654321',offer_id:12345};
 const raw=JSON.stringify(source,null,2)+'\n',display=sanitizeArtifact('verification/example.json',raw),parsed=JSON.parse(display);
 assert.equal(parsed.code,source.code);
 assert.equal(parsed.path,'[redacted-local-path]');assert.equal(parsed.email,'[redacted-email]');
 assert.equal(parsed.machine_id,'[redacted-identifier]');assert.equal(parsed.instance_id,'[redacted-identifier]');assert.equal(parsed.offer_id,12345);
 assert.equal(display.split('\n').length,raw.split('\n').length);
 assert.equal(sanitizeArtifact('verification/example.json',JSON.stringify({code:source.code},null,2)),JSON.stringify({code:source.code},null,2));
 const artifact=payload.files[payload.evidence_reuse_transition.registry_ref];
 assert.doesNotThrow(()=>JSON.parse(artifact.text));
 assert.notEqual(artifact.sha256,artifact.display_sha256);assert.equal(artifact.masked,true);
});
test('setup explains published PR versus local snapshot and nonpublic loopback review',()=>{
 for(const text of ['git fetch origin pull/185/head','git switch --detach FETCH_HEAD','npm ci','npm run dev:review','--host 127.0.0.1 --port 4000 --target http://127.0.0.1:3000','compare the package digest below with this report','Saving locally does not post to Jira or GitHub','Ctrl+C','Node.js 24'])assert.ok(html.includes(text),text);
 assert.equal(JSON.parse(fs.readFileSync(new URL('../package.json',import.meta.url))).scripts['dev:review'],'node scripts/mint-dev-loopback.mjs');
 assert.match(html,/fresh network clone\/install was not executed/);
});
test('the pending export is deterministic',()=>{
 const fresh=buildReport();
 assert.equal(fresh.html,html);
 assert.deepEqual(fresh.manifest,manifest);
});
test('exact source control shows only current passage, bound excerpt and gap without invented source anchors',()=>{
 const functionSource=app.slice(app.indexOf('function showSourceBasis('),app.indexOf('function twoDefectTransitionHTML('));
 assert.ok(functionSource);
 const id='FIXTURE-SOURCE',ref='verification/evidence/source.json',current={id,text:'Current exact passage.',status:'UNVALIDATED'};
 const basis={artifactRef:ref,text_pointer:'/sections/0/text',excerpt:'Exact governing excerpt <limited>.',support_rationale:'Only maintenance duty.',origin:{url:'https://cloud.vast.ai/host/agreement'}};
 const transition={basis:[basis],remaining:'Inspect the missing UI enforcement.',previous:{text:'Original broad passage.',status:'FAIL',rationale:'Prior citation absent.'}};
 let shown;
 const context={report:{authority_scan:{transitions:{[id]:transition}},files:{[ref]:{sha256:'a'.repeat(64),text:'Whole retained source',masked:false}}},claimMap:new Map([[id,current]]),pill:s=>s,escapeHTML:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),showDialog:(title,body)=>{shown={title,body}}};
 vm.runInNewContext(functionSource+'\nshowSourceBasis("FIXTURE-SOURCE","0");',context);
 assert.equal(shown.title,'Exact bound source excerpt');
 for(const literal of ['Current exact passage.','Exact governing excerpt &lt;limited&gt;.','Only maintenance duty.','Inspect the missing UI enforcement.','/sections/0/text'])assert.ok(shown.body.includes(literal),literal);
 assert.match(shown.body,/<details><summary>Whole retained source/);
 assert.doesNotMatch(shown.body,/Original broad passage|Prior citation absent|Original finding/);
 assert.doesNotMatch(shown.body,/https:\/\/cloud\.vast\.ai\/host\/agreement#/);
 shown=null;vm.runInNewContext('showSourceBasis("FIXTURE-SOURCE","1");',context);assert.equal(shown,null);
 vm.runInNewContext('showSourceBasis("OTHER","0");',context);assert.equal(shown,null);
});
test('calculator documentation modal explains the link check and retains the original record',()=>{
 const functionSource=app.slice(app.indexOf('function showSourceBasis('),app.indexOf('function twoDefectTransitionHTML('));
 const actual=payload.claims.find(c=>c.id==='MCL-18f04c2ae7ee95b4');
 const active=payload.authority_scan.transitions[actual.id];
 const history=entry=>[entry,...(entry.auditHistory||[]).flatMap(history)];
 const retained=history(active).find(entry=>entry.cleanup);
 const current=active.evidenceReuse?{...actual,...active.previous,reader_copy:hostReviewReaderCopy(active.previous)}:actual;
 const historicalPayload=active.evidenceReuse?{...payload,authority_scan:{...payload.authority_scan,transitions:{...payload.authority_scan.transitions,[actual.id]:retained}}}:payload;
 assert.ok(retained,'the earlier documentation check remains in the retained review history');
 let shown;
 const escapeHTML=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 vm.runInNewContext(functionSource+'\nshowSourceBasis("MCL-18f04c2ae7ee95b4","0");',{
  report:historicalPayload,claimMap:new Map([[current.id,current]]),pill:s=>s,escapeHTML,showDialog:(title,body)=>{shown={title,body};},
 });
 assert.equal(shown.title,'Exact documentation check');
 const visibleSummary=shown.body.split('<details>')[0];
 assert.ok(visibleSummary.includes(escapeHTML(current.reader_copy.documentationCheck.finding)));
 assert.ok(visibleSummary.includes(escapeHTML(current.reader_copy.nextStep)));
 assert.doesNotMatch(visibleSummary,/no external retrieval was authorized|console availability|agreement\/Terms currency/);
 assert.match(shown.body,/Whole retained documentation check and fingerprint/);
 assert.match(shown.body,/no external retrieval was authorized/);
 assert.match(shown.body,/UNVALIDATED/);
 if(active.evidenceReuse){
  vm.runInNewContext(functionSource+'\nshowSourceBasis("MCL-18f04c2ae7ee95b4","0");',{
   report:payload,claimMap:new Map([[actual.id,actual]]),pill:s=>s,escapeHTML,showDialog:(title,body)=>{shown={title,body};},
  });
  assert.equal(actual.status,'PASS');
  assert.equal(shown.title,'Exact bound source excerpt');
  assert.match(shown.body,/https:\/\/vast\.ai\/hosting\/calculator/);
  assert.doesNotMatch(shown.body.split('<details>')[0],/no external retrieval was authorized/);
 }
});
test('active authority scan retains per-claim predecessor and bounded source bindings offline',()=>{
 if(!payload.authority_scan)return;
 const scan=payload.authority_scan;
 for(const ref of [scan.registry_ref,scan.baseline_ref,scan.runtime_register_ref,scan.source_register_ref])assert.ok(payload.files[ref],ref);
 assert.equal(scan.runtime_register_ref,'verification/current-runtime-operator-blockers.md');
 assert.equal(scan.source_register_ref,'verification/current-source-owner-blockers.md');
 assert.equal(scan.runtime_register_sha256,payload.files[scan.runtime_register_ref].sha256);
 assert.equal(scan.source_register_sha256,payload.files[scan.source_register_ref].sha256);
 assert.match(scan.historical_runtime_register_ref,/host-authority-scan-attempt-01\/runtime-operator-register\.md$/);
 assert.match(scan.historical_source_register_ref,/host-authority-scan-attempt-01\/source-owner-register\.md$/);
 const clarification=payload.clarification_transition;
 const terms=payload.terms_transition;
 const jurisdiction=payload.jurisdiction_transition;
 const cleanup=payload.cleanup_transition;
 if(cleanup){
  const baseline='verification/evidence/2026-09-11-host-review-cleanup-attempt-01/before-current-host-docs-review.json';
  const digest='f18e61882f50a2785f2fe863aba88ecf3d79af8a45bdcbf1596e6e64c6b7059d';
  assert.equal(cleanup.baseline_ref,baseline);assert.equal(cleanup.baseline_sha256,digest);
  assert.equal(payload.files[cleanup.baseline_ref].sha256,digest);
 }
 const payoutTerms=payload.payout_terms_transition;
 const payoutInvoice=payload.payout_invoice_transition;
 const closure=payload.closure_transition;
 const sourceFamily=payload.source_family_transition;
 const evidenceReuse=payload.evidence_reuse_transition;
 const continuation=payload.continuation_transition;
 const diagnosticsSsh=payload.diagnostics_ssh_transition;
 const teamsConsole=payload.teams_console_transition;
 const finalOwner=payload.final_owner_transition;
 const hardwareOperator=payload.hardware_operator_transition;
 const verificationStorage=payload.verification_storage_transition;
 const recoveryEarnings=payload.recovery_earnings_transition;
 const setupMetrics=payload.setup_metrics_transition;
 const rawRead=ref=>fs.readFileSync(new URL('../'+ref,import.meta.url));
 const read=beforeContinuation(rawRead);
 const latestFrozen=evidenceReuse?new Map(JSON.parse(read(evidenceReuse.registry_ref)).sources.map(source=>[source.path,read(source.before_artifact.path)])):new Map();
 const baselineRefs=[scan.baseline_ref,...(finalOwner?[finalOwner.baseline_ref]:[]),...(hardwareOperator?[hardwareOperator.baseline_ref]:[]),...(verificationStorage?[verificationStorage.baseline_ref]:[]),...(recoveryEarnings?[recoveryEarnings.baseline_ref]:[]),...(setupMetrics?[setupMetrics.baseline_ref]:[]),...(teamsConsole?[teamsConsole.baseline_ref]:[]),...(diagnosticsSsh?[diagnosticsSsh.baseline_ref]:[]),...(continuation?[continuation.baseline_ref]:[]),...(evidenceReuse?[evidenceReuse.baseline_ref]:[]),...(sourceFamily?[sourceFamily.baseline_ref]:[]),...(closure?[closure.baseline_ref]:[]),...(clarification?[clarification.baseline_ref]:[]),...(terms?[terms.baseline_ref]:[]),...(jurisdiction?[jurisdiction.baseline_ref]:[]),...(cleanup?[cleanup.baseline_ref]:[]),...(payload.payout_provider_transition?[payload.payout_provider_transition.baseline_ref]:[]),...(payoutTerms?[payoutTerms.baseline_ref]:[]),...(payoutInvoice?[payoutInvoice.baseline_ref]:[])];
 const predecessorsByBaseline=new Map(baselineRefs.map(ref=>{
  assert.ok(payload.files[ref],ref);
  const before=JSON.parse(payload.files[ref].text);
  if(ref===finalOwner?.baseline_ref||ref===hardwareOperator?.baseline_ref||ref===verificationStorage?.baseline_ref||ref===recoveryEarnings?.baseline_ref||ref===setupMetrics?.baseline_ref||ref===teamsConsole?.baseline_ref||ref===diagnosticsSsh?.baseline_ref||ref===continuation?.baseline_ref||ref===sourceFamily?.baseline_ref||ref===evidenceReuse?.baseline_ref){
   // This successor retains a complete hash inventory rather than another full
   // model copy. Replay the existing sealed predecessor against its before files.
   const frozen=ref===finalOwner?.baseline_ref||ref===hardwareOperator?.baseline_ref||ref===verificationStorage?.baseline_ref||ref===recoveryEarnings?.baseline_ref||ref===setupMetrics?.baseline_ref||ref===teamsConsole?.baseline_ref||ref===diagnosticsSsh?.baseline_ref||ref===continuation?.baseline_ref?new Map():new Map(latestFrozen);
   if(ref===sourceFamily?.baseline_ref){
    const registry=JSON.parse(read(sourceFamily.registry_ref));
    for(const source of registry.sources)frozen.set(source.path,read(source.before_artifact.path));
    const amendment=JSON.parse(read('verification/evidence/2026-09-15-host-unvalidated-source-families-attempt-01/owner-context-amendment.json'));
    frozen.set('verification/current-host-owner-questions.json',read(amendment.before_artifact.path));
   }
   const projector=ref===finalOwner?.baseline_ref?projectHardwareOperatorReview:ref===hardwareOperator?.baseline_ref?projectVerificationStorageReview:ref===verificationStorage?.baseline_ref?projectRecoveryEarningsReview:ref===recoveryEarnings?.baseline_ref?projectSetupMetricsReview:ref===setupMetrics?.baseline_ref?projectTeamsConsoleReview:ref===teamsConsole?.baseline_ref?projectDiagnosticsSshReview:ref===diagnosticsSsh?.baseline_ref?projectContinuationReview:ref===continuation?.baseline_ref?projectEvidenceReuseReview:ref===evidenceReuse?.baseline_ref?projectSourceFamilyReview:projectClosureCorrection;
   const baselineRead=ref===finalOwner?.baseline_ref?beforeFinalOwner(rawRead):ref===hardwareOperator?.baseline_ref?beforeHardwareOperator(rawRead):ref===verificationStorage?.baseline_ref?beforeVerificationStorage(rawRead):ref===recoveryEarnings?.baseline_ref?beforeRecoveryEarnings(rawRead):ref===setupMetrics?.baseline_ref?beforeSetupMetrics(rawRead):ref===teamsConsole?.baseline_ref?beforeTeamsConsole(rawRead):ref===diagnosticsSsh?.baseline_ref?beforeDiagnosticsSsh(rawRead):read;
   const prior=projector({read:ref=>frozen.get(ref)||baselineRead(ref),exists:ref=>fs.existsSync(new URL('../'+ref,import.meta.url))}).model;
   const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,canonical(value[key])])):value;
   const priorClaims=prior.pages.flatMap(page=>page.claims);
   assert.deepEqual(Object.fromEntries(priorClaims.map(claim=>[claim.id,hash(JSON.stringify(canonical(claim)))])),before.claim_hashes);
   return [ref,new Map(priorClaims.map(claim=>[claim.id,JSON.parse(JSON.stringify(claim,(_,value)=>typeof value==='string'?sanitize(value):value))]))];
  }
  return [ref,new Map(before.pages.flatMap(p=>p.claims).map(c=>[c.id,c]))];
 }));
 if(clarification)assert.equal(payload.files[clarification.baseline_ref].sha256,clarification.baseline_sha256);
 const lineage=transition=>[transition,...(transition.auditHistory||[]).flatMap(lineage)];
 for(const [id,current]of Object.entries(scan.transitions))for(const transition of lineage(current)){
  assert.ok(payload.claims.some(c=>c.id===id));
  const predecessors=predecessorsByBaseline.get(transition.baselineRef);
  assert.ok(predecessors,`unknown predecessor baseline: ${transition.baselineRef}`);
  if(transition.previous?.id!==id){
   assert.ok(closure?.retired_claims.some(retired=>retired.claim_id===transition.previous?.id&&retired.replaced_by===id),'only an exact retained checklist retirement may use another predecessor ID');
  }
  assert.deepEqual(transition.previous,predecessors.get(transition.previous?.id||id));
  assert.equal(transition.registryRef,transition.baselineRef===finalOwner?.baseline_ref?finalOwner.registry_ref:transition.baselineRef===hardwareOperator?.baseline_ref?hardwareOperator.registry_ref:transition.baselineRef===verificationStorage?.baseline_ref?verificationStorage.registry_ref:transition.baselineRef===recoveryEarnings?.baseline_ref?recoveryEarnings.registry_ref:transition.baselineRef===setupMetrics?.baseline_ref?setupMetrics.registry_ref:transition.baselineRef===teamsConsole?.baseline_ref?teamsConsole.registry_ref:transition.baselineRef===diagnosticsSsh?.baseline_ref?diagnosticsSsh.registry_ref:transition.baselineRef===continuation?.baseline_ref?continuation.registry_ref:transition.baselineRef===evidenceReuse?.baseline_ref?evidenceReuse.registry_ref:transition.baselineRef===sourceFamily?.baseline_ref?sourceFamily.registry_ref:transition.baselineRef===closure?.baseline_ref?closure.registry_ref:transition.baselineRef===payoutInvoice?.baseline_ref?payoutInvoice.registry_ref:transition.baselineRef===payoutTerms?.baseline_ref?payoutTerms.registry_ref:transition.baselineRef===payload.payout_provider_transition?.baseline_ref?payload.payout_provider_transition.registry_ref:transition.baselineRef===scan.baseline_ref?scan.registry_ref:transition.baselineRef===jurisdiction?.baseline_ref?jurisdiction.registry_ref:transition.baselineRef===terms?.baseline_ref?terms.registry_ref:transition.baselineRef===clarification?.baseline_ref?clarification.registry_ref:cleanup?.registry_ref);
  for(const basis of transition.basis){assert.ok(payload.files[basis.artifactRef]);assert.ok(basis.support_rationale);if(basis.kind==='GOVERNING_SOURCE'){assert.ok(basis.excerpt);assert.match(basis.text_pointer,/^\//);}}
 }
 if(jurisdiction)for(const id of jurisdictionIds.keys())assert.ok(scan.transitions[id].auditHistory.length,`predecessor source history retained: ${id}`);
 if(clarification){
  const phase43=predecessorsByBaseline.get(scan.baseline_ref),phase45=predecessorsByBaseline.get(clarification.baseline_ref);
  const clarificationOnly=Object.entries(scan.transitions).find(([,transition])=>transition.baselineRef===clarification.baseline_ref);
  if(clarificationOnly){
   const [id,transition]=clarificationOnly;
   assert.deepEqual(transition.previous,phase45.get(id));
  }
 }
 assert.match(payload.current_result_ref,finalOwner?/host-final-owner-reconciliation-attempt-01\/result\.md$/:hardwareOperator?/host-continuation-hardware-operator-attempt-01\/result\.md$/:verificationStorage?/host-continuation-verification-storage-attempt-01\/result\.md$/:recoveryEarnings?/host-continuation-recovery-earnings-attempt-01\/result\.md$/:setupMetrics?/host-continuation-setup-metrics-attempt-01\/result\.md$/:teamsConsole?/host-continuation-teams-console-attempt-01\/result\.md$/:diagnosticsSsh?/host-continuation-diagnostics-ssh-attempt-01\/result\.md$/:continuation?/host-continuation-88-attempt-01\/result\.md$/:evidenceReuse?/host-evidence-reuse-source-review-attempt-01\/result-02\.md$/:sourceFamily?/host-unvalidated-source-families-attempt-01\/result\.md$/:closure?/host-unvalidated-evidence-attempt-02\/result\.md$/:payload.payout_invoice_transition?/payout-invoice-correction-attempt-01\/result\.md$/:payload.payout_terms_transition?/payout-terms-correction-attempt-01\/result\.md$/:payload.payout_provider_transition?/payout-provider-correction-attempt-01\/result\.md$/:payload.cleanup_transition?/host-review-cleanup-attempt-01\/result\.md$/:jurisdiction?/host-jurisdiction-authority-attempt-01\/result\.md$/:terms?/host-terms-binding-attempt-01\/result\.md$/:/host-authority-scan-attempt-01\/result\.md$/);
 assert.match(app,/Source review adds no runtime execution/);
});
test('clarification metadata reports bounded changed claim and node context only',()=>{
 if(!payload.clarification_transition)return;
 const transition=payload.clarification_transition;
 const registry=JSON.parse(fs.readFileSync(new URL('../verification/current-host-clarification.json',import.meta.url)));
 assert.equal(transition.changed_claims,registry.claims.length);
 assert.equal(transition.changed_nodes,registry.nodes.length);
 assert.ok(payload.files[transition.registry_ref]);
 assert.ok(payload.files[transition.baseline_ref]);
 assert.match(transition.limit,/not product evidence/i);
});
test('generated HTML and manifest match the deterministic current export',()=>{
 assert.equal(fs.readFileSync(new URL('../verification/host-docs-review.html',import.meta.url),'utf8'),html);
 assert.deepEqual(JSON.parse(fs.readFileSync(new URL('../verification/host-docs-review-export.json',import.meta.url))),manifest);
});

test('the exact non-secret Bash prompt stays readable while credential values and line positions remain protected',()=>{
 const prompt="  read -r -s -p 'Host API key: ' task_vast_key || exit 1\n  printf '\\n'";
 assert.equal(sanitize(prompt),prompt);
 assert.doesNotMatch(sanitize("read -r -s -p 'Host API key: ' task_vast_key || exit 1\napi_key='must-stay-private'"),/must-stay-private/);
 for(const value of ["api_key='sensitive-value'", "api_key='first-line\nsecond-line'"]){const shown=sanitize(value);assert.doesNotMatch(shown,/sensitive-value|first-line|second-line/);assert.equal(shown.split('\n').length,value.split('\n').length);assert.match(shown,/\[redacted\]/);}
});

test('final owner purposes and immutable historical Tax Guide keep current and earlier text separate',()=>{
 const escapeHTML=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\"','&quot;').replaceAll("'",'&#39;');
 if(!payload.final_owner_transition)return;
 assert.equal(payload.owner_questions.original_questions.length,payload.tax_retirement_transition?7:8);assert.equal(payload.owner_questions.questions.length,payload.tax_retirement_transition?10:11);
 assert.equal(payload.issues.counts.publicationConflicts,3);assert.equal(payload.issues.counts.futureDetailQuestions,payload.tax_retirement_transition?7:8);
 assert.equal(payload.issues.counts.correctionPassages,0);assert.equal(payload.issues.counts.blockedPassages,0);
 assert.match(app,/At that checkpoint, four financial passages remained unresolved/);assert.match(app,/At that checkpoint, five financial passages remained open/);
 const ref=payload.final_owner_transition.attempt_ref+'/sources-before/host/guide-to-taxes.mdx',old=payload.files[ref],current=payload.files[payload.tax_retirement_transition ? 'verification/evidence/2026-09-15-host-tax-guide-retirement-attempt-01/sources-before/host/guide-to-taxes.mdx' : 'host/guide-to-taxes.mdx'];
 assert.equal(old.sha256,'0cef831564be2dfcbfd90291acfe00169da777f0af8bd5157ea0b4210ca1471a');assert.notEqual(current.sha256,old.sha256);
 assert.ok(old.text.includes('VAT'));assert.ok(current.text.includes('Ask Vast Billing or Support to confirm the VAT treatment'));
 let shown;const source=app.slice(app.indexOf('function showArtifact('),app.indexOf('const jurisdictionActive=',app.indexOf('function showArtifact(')));
 vm.runInNewContext(source+`\nshowArtifact(${JSON.stringify(ref)});`,{report:payload,claimMap:new Map(),escapeHTML,showDialog:(_,body)=>shown=body});
 assert.ok(shown.includes(old.sha256));assert.ok(shown.includes(escapeHTML(old.text)));assert.ok(!shown.includes(escapeHTML('Ask Vast Billing or Support to confirm the VAT treatment')));
 assert.ok(payload.files[payload.final_owner_transition.result_ref].text.includes('sources-before/host/guide-to-taxes.mdx'));
});
