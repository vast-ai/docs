import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {hostReviewReaderCopy} from './host_review_reader_copy.mjs';
import {buildReport, sanitize} from './export_host_review_html.mjs';
const model=JSON.parse(fs.readFileSync(new URL('../verification/current-host-docs-review.json',import.meta.url)));
const claims=model.pages.flatMap(p=>p.claims);
const cleanupPredecessor=new URL('../verification/evidence/2026-09-11-host-review-cleanup-attempt-01/before-current-host-docs-review.json',import.meta.url);
const clarificationCohortModel=fs.existsSync(cleanupPredecessor)?JSON.parse(fs.readFileSync(cleanupPredecessor)):model;
const clarificationCohortClaims=clarificationCohortModel.pages.flatMap(p=>p.claims);
const quickstart=claims.find(c=>c.id==='MCL-790d76c6e2bea8fa');
const calculator=claims.find(c=>c.id==='MCL-18f04c2ae7ee95b4');
const clarification=JSON.parse(fs.readFileSync(new URL('../verification/evidence/2026-09-10-host-clarification-sweep-attempt-01/root-policy-runtime-decisions-01.json',import.meta.url)));
const finalClarification=JSON.parse(fs.readFileSync(new URL('../verification/current-host-clarification.json',import.meta.url)));
const clarificationBaseline=JSON.parse(fs.readFileSync(new URL('../verification/evidence/2026-09-10-host-clarification-sweep-attempt-01/before-review.json',import.meta.url)));
const clarificationBaselineById=new Map(clarificationBaseline.pages.flatMap(p=>p.claims).map(c=>[c.id,c]));
const finalizedClaim=id=>{
 const before=clarificationBaselineById.get(id),record=finalClarification.claims.find(c=>c.claim_id===id);
 assert.ok(before&&record?.after,`missing final fixture ${id}`);
 return {...before,...record.after};
};
const reviewedClaim=id=>{
 const before=clarificationCohortClaims.find(c=>c.id===id), decision=clarification.records.find(r=>r.claim_id===id)?.after;
 assert.ok(before&&decision,`missing reviewed fixture ${id}`);
 return {...before,...decision};
};

test('account requirement is understandable without claiming enforcement',()=>{
 const copy=hostReviewReaderCopy(quickstart),clarified=quickstart.classification==='REVIEWED_SETUP_INSTRUCTION';
 assert.equal(copy.finding,clarified?quickstart.rationale:'The page says you must use a separate host account and accept the agreement. We still need evidence confirming both requirements.');
 assert.equal(copy.nextStep,clarified?quickstart.next_action:'Check Vast’s account setup rules and record what the setup page requires.');
 assert.equal(copy.label,clarified?'Setup review':'What is missing');
 if(clarified)assert.equal(copy.statusLabel,'Check setup requirements');
 assert.doesNotMatch(copy.finding,/Vast enforces|enforced by Vast|permission enforcement|state transition/);
});
test('calculator link has bounded completion criteria, separate from output validation',()=>{
 const copy=hostReviewReaderCopy(calculator);
 assert.equal(copy.reviewKind,'calculator-link-review');
 assert.equal(copy.statusLabel,'Check calculator link');
 assert.match(copy.finding,/No saved observation of the destination page is attached/);
 assert.match(copy.nextStep,/https:\/\/vast.ai\/hosting\/calculator/);
 assert.match(copy.nextStep,/final URL, date and time, screenshot, and outcome/);
 assert.match(copy.nextStep,/attach that record to this entry/);
 assert.match(copy.nextStep,/no paid rental or new owner approval/);
 assert.match(copy.documentationCheck.finding,/does not record a visit/);
 assert.match(copy.documentationCheck.scope,/does not establish calculator accuracy/);
 assert.deepEqual(copy.proofGuide.items.map(item=>item.label),['Calculations','Market history']);
 assert.match(copy.proofGuide.items[0].text,/independently/);
 assert.match(copy.proofGuide.items[1].text,/actual data source and period/);
 assert.match(copy.proofGuide.items[1].text,/does not prove the calculator uses that data/);
 assert.match(copy.proofGuide.limit,/not requirements for closing this link entry/);
 assert.equal(copy.status,undefined);
 assert.equal(calculator.status,'UNVALIDATED');
 assert.deepEqual(claims.filter(c=>hostReviewReaderCopy(c).proofGuide).map(c=>c.id),[calculator.id]);
});
test('calculator-specific copy fails closed when the passage or finding changes',()=>{
 for(const change of [
  {id:'unreviewed'}, {text:calculator.text+' Uses history.'}, {headings:['Different heading']},
  {status:'PASS'}, {classification:'REVIEWED_BEHAVIOR_DESCRIPTION'},
  {required_evidence_types:['RUNTIME_OR_UI_OBSERVATION']},
  {rationale:calculator.rationale+' New limit.'}, {next_action:'Retain a new observation.'},
  {evidence_refs:[]}, {source_refs:[{url:'https://example.org'}]},
  {evidence_refs:[...calculator.evidence_refs,{id:'NEW_OBSERVATION'}]},
  {evidence_refs:[{...calculator.evidence_refs[0],limit:'New observation was added.'}]},
  {spans:[{...calculator.spans[0],source_file:'host/market-metrics.mdx'}]},
  {spans:[{...calculator.spans[0],text_sha256:'changed'}]},
 ])assert.equal(hostReviewReaderCopy({...calculator,...change}).proofGuide,undefined,JSON.stringify(change));
 const normalized={...calculator,requiredEvidenceTypes:calculator.required_evidence_types,nextAction:calculator.next_action,
  sourceRefs:[],evidenceRefs:calculator.evidence_refs.map(({artifact_ref,...ref})=>({...ref,artifactRef:artifact_ref})),
  spans:calculator.spans.map(({source_file,text_sha256,...span})=>({...span,sourceFile:source_file,textSha256:text_sha256}))};
 for(const key of ['required_evidence_types','next_action','source_refs','evidence_refs'])delete normalized[key];
 assert.deepEqual(hostReviewReaderCopy(normalized),hostReviewReaderCopy(calculator));
});
test('wording does not mutate any of the 2013 claim or proof records',()=>{
 const before=JSON.stringify(model);
 for(const claim of claims){const copy=hostReviewReaderCopy(claim);assert.ok(copy.finding&&copy.nextStep&&copy.label,claim.id);}
 assert.equal(JSON.stringify(model),before);
 assert.equal(claims.length,2013);
});
test('offline reader uses the same formatter, preserving recorded facts',()=>{
 const report=buildReport();
 for(const [i,c] of report.payload.claims.entries()){
  assert.deepEqual(c.reader_copy,hostReviewReaderCopy(c));
  assert.equal(c.status,claims[i].status);
  assert.equal(c.rationale,sanitize(claims[i].rationale));
  assert.equal(c.next_action,sanitize(claims[i].next_action));
 }
});
test('added claim-specific limits and changed source wording bypass the specific override',()=>{
 const changed={...quickstart,rationale:quickstart.rationale+' Only the button was observed.'};
 assert.equal(hostReviewReaderCopy(changed).finding,changed.rationale);
 assert.equal(hostReviewReaderCopy(changed).nextStep,changed.next_action);
 const changedText=hostReviewReaderCopy({...quickstart,text:'Different requirements.'});
 if(quickstart.classification==='REVIEWED_SETUP_INSTRUCTION')assert.equal(changedText.reviewKind,undefined);
 else assert.notEqual(changedText.finding,hostReviewReaderCopy(quickstart).finding);
 assert.equal(hostReviewReaderCopy({...quickstart,status:'PASS'}).finding,quickstart.rationale);
});
test('real blocking prerequisites and special self-test limits remain intact',()=>{
 for(const c of claims.filter(c=>c.status==='BLOCKED')){
  const copy=hostReviewReaderCopy(c);
  assert.equal(copy.label,'What is stopping the check');
  assert.equal(copy.finding,c.rationale.replace(/^UNAVAILABLE_PREREQUISITE [A-Z_]+:\s*/,''));
 }
 const c=claims.find(c=>c.id==='MCL-eeaf6da83da9eca7');
 assert.equal(hostReviewReaderCopy(c).nextStep,c.next_action);
 assert.match(hostReviewReaderCopy(c).finding,/0\.8506588/);
});
test('missing citations remain distinct from runtime failures',()=>{
 const c=claims.find(c=>c.id==='MCL-9cfc73236e4c395a');
 assert.ok(c,'current rental-terms citation-gap fixture must exist');
 assert.equal(c.status,'FAIL');
 assert.ok(c.required_evidence_types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION'));
 assert.ok(c.required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION'));
 const copy=hostReviewReaderCopy(c);
 assert.match(copy.finding,/required citation is missing/);
 assert.doesNotMatch(copy.finding,/runtime failure/i);
 assert.match(copy.nextStep,/relevant agreement section/);
 assert.match(copy.nextStep,/approved test/);
});
test('link support does not become product support',()=>{
 const c=claims.find(c=>c.rationale.startsWith('Every local destination'));
 const copy=hostReviewReaderCopy(c);
 assert.match(copy.finding,/does not verify the statements/);
 assert.equal(c.status,'PASS');
});

test('five exact workload rules request confirmation, not runtime proof or acceptance',()=>{
 const eligible=claims.filter(c=>hostReviewReaderCopy(c).reviewKind==='policy-acknowledgement');
 assert.deepEqual(eligible.map(c=>c.id).sort(),['MCL-b61d15c0282ef567','MCL-c59caa4cd52bcc1f','MCL-af1c482a08b09316','MCL-393941d0e9be9d31','MCL-03c73e4182b1e7fe'].sort());
 for(const c of eligible){
  const copy=hostReviewReaderCopy(c);
  assert.equal(copy.statusLabel,'Needs policy acknowledgement');
  assert.match(copy.finding,/No runtime test is needed to establish the rule/);
  assert.match(copy.nextStep,/existing approved policy first/);
  assert.match(copy.nextStep,/responsible Vast policy owner to confirm or correct/);
  assert.match(copy.nextStep,/Cite the policy or recorded decision/);
  assert.match(copy.pendingNote,/citation are still pending/);
  assert.match(copy.pendingNote,/does not record approval/);
  assert.ok(['FAIL','UNVALIDATED'].includes(c.status));
  assert.equal(copy.status,undefined);
 }
 assert.match(hostReviewReaderCopy(eligible.find(c=>c.id==='MCL-c59caa4cd52bcc1f')).nextStep,/advice or a requirement/);
});
test('policy acknowledgement is withdrawn if any reviewed boundary changes',()=>{
 for(const c of claims.filter(c=>hostReviewReaderCopy(c).reviewKind==='policy-acknowledgement')){
  for(const change of [{id:'MCL-unreviewed'}, {text:c.text+' Always enforced.'}, {classification:'CONTRACT_TERM'}, {status:'PASS'}, {status:'BLOCKED'}, {required_evidence_types:[...c.required_evidence_types,'RUNTIME_OR_UI_OBSERVATION']}, {rationale:c.rationale+' Added limitation.'}, {next_action:'New required approval.'}]){
   assert.equal(hostReviewReaderCopy({...c,...change}).reviewKind,undefined,c.id+JSON.stringify(change));
  }
  const normalized={...c,requiredEvidenceTypes:c.required_evidence_types,nextAction:c.next_action};
  delete normalized.required_evidence_types;delete normalized.next_action;
  assert.deepEqual(hostReviewReaderCopy(normalized),hostReviewReaderCopy(c));
 }
});
test('following a policy link needs no fresh compliance approval',()=>{
 const claim=claims.find(c=>c.id==='MCL-3b10b5e64ee55003'),copy=hostReviewReaderCopy(claim),clarified=claim.classification==='REVIEWED_POLICY_REFERENCE';
 assert.equal(copy.reviewKind,'policy-reference');
 assert.equal(copy.statusLabel,'Check policy source');
 if(clarified){assert.equal(copy.finding,claim.rationale);assert.equal(copy.nextStep,claim.next_action);}
 else {assert.match(copy.finding,/does not need a new approval or a test rental/);assert.match(copy.nextStep,/do not treat two draft pages repeating each other as proof/);}
 assert.equal(copy.pendingNote,undefined);
});
test('already-supported marketplace description needs no test rental',()=>{
 const c=claims.find(c=>c.id==='MCL-e12ac9f6be2ce502'), copy=hostReviewReaderCopy(c);
 assert.equal(c.status,'PASS');
 assert.equal(copy.finding,'Official Vast publications support this basic description. No test rental is needed. This finding covers the published description only.');
 assert.equal(copy.nextStep,'Recheck if the wording or supporting sources change.');
 for(const change of [{status:'UNVALIDATED'},{text:c.text+' Every listing is available.'},{rationale:c.rationale+' New limitation.'},{required_evidence_types:['RUNTIME_OR_UI_OBSERVATION']}]){
  assert.notEqual(hostReviewReaderCopy({...c,...change}).finding,copy.finding);
 }
});
test('bounded published Terms source PASS rows use concise non-runtime wording and fail closed on drift',()=>{
 const expected=new Map([
  ['MCL-99ca28f707d5966a','The cited Terms support this rule. This does not prove runtime enforcement.'],
  ['MCL-2c3f7082e2c7fdf2','The cited Terms support this rule. This does not prove runtime enforcement.'],
  ['MCL-c4c4bfc59eb7b49f','The cited Terms and Hosting Agreement support this rule. This does not prove runtime enforcement.'],
  ['MCL-399798a3c4946b5f','The cited Terms and Hosting Agreement support this rule. This does not prove runtime enforcement.'],
  ['MCL-633317ca7ebecfef','The cited Terms support this rule. This does not prove runtime enforcement.'],
 ['MCL-fe3eccd1cd40b4bd','The cited Terms support this rule. This does not prove runtime enforcement.'],
 ]);
 for(const [id,finding] of expected){
  const c=claims.find(claim=>claim.id===id),copy=hostReviewReaderCopy(c);
  assert.equal(c.status,'PASS',id);assert.equal(copy.reviewKind,'published-terms-source',id);assert.equal(copy.finding,finding,id);
  assert.equal(copy.nextStep,'Recheck if the wording or cited source changes.',id);
  assert.equal(copy.statusLabel,undefined,id);assert.equal(copy.pendingNote,undefined,id);
  for(const change of [{status:'FAIL'},{classification:'REVIEWED_POLICY_RULE'},{required_evidence_types:['AUTHORITATIVE_DOCUMENTATION_CITATION','REPOSITORY_STATIC_CHECK']},{rationale:c.rationale+' Changed.'},{next_action:c.next_action+' Changed.'}])assert.notEqual(hostReviewReaderCopy({...c,...change}).reviewKind,'published-terms-source',id+JSON.stringify(change));
 }
});
test('clarification cohorts use their recorded source, advice, link and setup review wording',()=>{
 const cases=[
  ['MCL-96a7de8300ee0824','Advice review','Advice review','advice-review'],
  ['MCL-054a98ae8bf901da','Link and wording review','Check link and wording','navigation-review'],
  ['MCL-3b10b5e64ee55003','Policy reference','Check policy source','policy-reference'],
  ['MCL-790d76c6e2bea8fa','Setup review','Check setup requirements','setup-review'],
  ['CUR-d83c946956b9328a','Settings and behavior review','Check technical source and retained result','settings-review'],
 ];
 for(const [id,label,statusLabel,reviewKind] of cases){
  const c=reviewedClaim(id),copy=hostReviewReaderCopy(c);
  assert.equal(copy.label,label,id);assert.equal(copy.statusLabel,statusLabel,id);assert.equal(copy.reviewKind,reviewKind,id);
 assert.equal(copy.finding,c.rationale,id);assert.equal(copy.nextStep,c.next_action,id);
 }
});
test('current cleanup state remains distinct from the frozen clarification cohort',()=>{
 if(!fs.existsSync(new URL('../verification/current-host-review-cleanup.json',import.meta.url)))return;
 const current=claims.find(c=>c.id==='MCL-054a98ae8bf901da'),cohort=reviewedClaim('MCL-054a98ae8bf901da');
 assert.equal(current.status,'NOT_APPLICABLE');assert.notEqual(current.status,cohort.status);
});
test('only the five exact retained policy examples request an acknowledgement',()=>{
 const special=finalizedClaim('MCL-b61d15c0282ef567'),copy=hostReviewReaderCopy(special);
 assert.equal(copy.reviewKind,'policy-acknowledgement');
 assert.match(copy.pendingNote,/does not record approval/);
 assert.equal(copy.finding.includes(special.rationale),false);
 for(const change of [{text:special.text+' Changed.'},{id:'MCL-99ca28f707d5966a'},{required_evidence_types:[...special.required_evidence_types,'REPOSITORY_STATIC_CHECK']},{rationale:special.rationale+' Changed.'},{next_action:special.next_action+' Changed.'}]){
  assert.notEqual(hostReviewReaderCopy({...special,...change}).reviewKind,'policy-acknowledgement',JSON.stringify(change));
 }
});
test('new technical, calculation and behavior lanes require their exact recorded review shape',()=>{
 const cases=[
  ['REVIEWED_TECHNICAL_DECLARATION',['CANONICAL_IMPLEMENTATION_SOURCE'],'This is a technical description or instruction. Check the exact definition in the relevant code, API schema, configuration or primary tool documentation. A written example is not evidence that an operation ran.','Find the exact definition or instruction in canonical code, an API schema, configuration or primary tool documentation. Compare each option, unit, limit and safety condition with this passage. Use a separate retained result if claiming that the operation ran or succeeded.','Check technical source'],
  ['REVIEWED_EXAMPLE_CALCULATION',['REPOSITORY_STATIC_CHECK'],'This is a planning example, not an observed earning or bill. Check the arithmetic, units and stated assumptions.','Recalculate the example with its stated inputs and units. Label hypothetical inputs clearly; do not present the result as measured revenue, a bill or a promised return.','Check calculation assumptions'],
  ['REVIEWED_BEHAVIOR_DESCRIPTION',['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION'],'This describes a behavior or result. Check the implementation first; use retained execution or UI evidence for any claimed timing, state change or completed outcome. Do not turn this into a general policy-approval request.','Check the implementation and any retained result that covers this exact behavior. For an asserted timing, state change or completed outcome, identify the smallest authorized runtime/UI check and retain its result. Do not rent or mutate merely to establish a declared interface.','Check implementation and retained result'],
 ];
 for(const [classification,required_evidence_types,rationale,next_action,statusLabel] of cases){
  const c={...quickstart,status:'UNVALIDATED',classification,required_evidence_types,rationale,next_action},copy=hostReviewReaderCopy(c);
  assert.equal(copy.statusLabel,statusLabel,classification);assert.equal(copy.finding,rationale,classification);assert.equal(copy.nextStep,next_action,classification);
  for(const change of [{classification:'UNREVIEWED'},{status:'FAIL'},{rationale:rationale+' Changed.'},{next_action:next_action+' Changed.'},{required_evidence_types:[...required_evidence_types,'REPOSITORY_STATIC_CHECK']}])assert.equal(hostReviewReaderCopy({...c,...change}).reviewKind,undefined,classification+JSON.stringify(change));
 }
});
test('pure advice wording has no implied platform proof and fails closed on changed review fields',()=>{
 const c=finalizedClaim('MCL-11d3dfb2a39b7a30'),copy=hostReviewReaderCopy(c);
 assert.equal(c.classification,'REVIEWED_ADVICE');assert.equal(copy.statusLabel,'Advice review');
 assert.equal(copy.finding,c.rationale);assert.equal(copy.nextStep,c.next_action);
 assert.match(copy.finding,/does not claim that a platform operation succeeded/i);
 for(const change of [{classification:'REVIEWED_TECHNICAL_DECLARATION'},{status:'FAIL'},{required_evidence_types:['CANONICAL_IMPLEMENTATION_SOURCE']},{rationale:c.rationale+' Changed.'},{next_action:c.next_action+' Changed.'}])assert.equal(hostReviewReaderCopy({...c,...change}).reviewKind,undefined,JSON.stringify(change));
});
test('all 701 finalized clarification records have their intended reader-review label',()=>{
 const expected={
  'REVIEWED_ADVICE_WITH_FACTUAL_INPUTS|Advice review|advice-review':136,
  'REVIEWED_ADVICE|Advice review|advice-review':58,
  'REVIEWED_POLICY_RULE|Needs policy acknowledgement|policy-acknowledgement':5,
  'ACCOUNT_CONFIGURATION_OR_PERMISSION|Check technical source and retained result|settings-review':35,
  'REVIEWED_SETUP_INSTRUCTION|Check setup requirements|setup-review':1,
  'REVIEWED_POLICY_REFERENCE|Check policy source|policy-reference':1,
  'REVIEWED_POLICY_RULE|Check policy source|policy-source-review':4,
  'REVIEWED_NAVIGATION_INSTRUCTION|Check link and wording|navigation-review':65,
  'REVIEWED_TECHNICAL_DECLARATION|Check technical source|technical-declaration-review':372,
  'REVIEWED_EXAMPLE_CALCULATION|Check calculation assumptions|example-calculation-review':13,
  'REVIEWED_BEHAVIOR_DESCRIPTION|Check implementation and retained result|behavior-review':11,
 };
 const observed={};
 assert.equal(finalClarification.claims.length,701);
 for(const record of finalClarification.claims){
  const before=clarificationBaselineById.get(record.claim_id);assert.ok(before&&record.after,record.claim_id);
  const claim={...before,...record.after},copy=hostReviewReaderCopy(claim);
  const key=`${claim.classification}|${copy.statusLabel||'none'}|${copy.reviewKind||'none'}`;
  observed[key]=(observed[key]||0)+1;
  if(copy.reviewKind!=='policy-acknowledgement'){
   assert.equal(copy.finding,claim.rationale,record.claim_id);
   assert.equal(copy.nextStep,claim.next_action,record.claim_id);
  }
 }
 assert.deepEqual(observed,expected);
});
