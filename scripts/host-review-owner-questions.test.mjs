import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';
import { loadHostReviewOwnerQuestions } from './host_review_owner_questions.mjs';
import { buildReport } from './export_host_review_html.mjs';
import { hostReviewReaderCopy } from './host_review_reader_copy.mjs';
import { sortHostReviewDisplay } from './host_review_work_queue.mjs';

const root = new URL('../', import.meta.url);
const read = ref => fs.readFileSync(new URL('../' + ref, import.meta.url));
const modelBytes = read('verification/current-host-docs-review.json');
const model = JSON.parse(modelBytes);
const modelSha256 = crypto.createHash('sha256').update(modelBytes).digest('hex');

test('eight independent owner questions are validated separately from the current claim inventory', () => {
  const projection = loadHostReviewOwnerQuestions({read, model, modelSha256});
  assert.equal(projection.available, true);
  assert.equal(projection.questions.length, 8);
  assert.deepEqual(projection.questions.map(question => question.id), [
    'HQ-DATACENTER-DOCUMENTS', 'HQ-DATACENTER-CERTIFICATION', 'HQ-PAYOUT-THRESHOLD',
    'HQ-STORAGE-REMOVAL', 'HQ-LOCAL-WORKLOADS', 'HQ-VAST-TAX-HANDLING', 'HQ-RENTAL-DATES', 'HQ-RENTAL-AVAILABILITY',
  ]);
  for (const question of projection.questions) {
    assert.equal(question.status, 'UNVALIDATED');
    assert.ok(question.proposedTeams.length);
    assert.ok(question.relatedClaims.length);
    assert.doesNotMatch(question.id, /^MCL-/);
  }
  const storage = projection.questions.find(question => question.id === 'HQ-STORAGE-REMOVAL');
  assert.match(storage.coverageGaps.join(' '), /does not state a secure-erasure guarantee/i);
  assert.equal(storage.relatedClaims.some(claim => claim.id === 'VOL-C18'), true);
});

test('missing, stale, and source-link-drift owner-question registries fail visibly', () => {
  const missing = loadHostReviewOwnerQuestions({read: () => { throw new Error('not found'); }, model, modelSha256});
  assert.equal(missing.available, false);
  assert.match(missing.error, /not found/);
  const stale = loadHostReviewOwnerQuestions({read, model, modelSha256: '0'.repeat(64)});
  assert.equal(stale.available, false);
  assert.match(stale.error, /stale|invalid/i);
  const sourceDrift = loadHostReviewOwnerQuestions({
    read: ref => ref === 'verification/current-host-owner-questions.json'
      ? Buffer.from(read(ref).toString('utf8').replace('https://vast.ai/compliance', 'https://example.invalid')) : read(ref), model, modelSha256,
  });
  assert.equal(sourceDrift.available, false);
  assert.match(sourceDrift.error, /source link drift/);
});

test('owner questions are payload-only handoff context and source-only payout PASS stays bounded', () => {
  const before = JSON.stringify(model);
  const {payload, html} = buildReport();
  assert.equal(payload.claims.length, 2008);
  assert.deepEqual(payload.counts.claim_statuses, model.counts.claim_statuses);
  assert.equal(payload.owner_questions.questions.length, payload.final_owner_transition ? 11 : 8);
  if(payload.final_owner_transition){assert.equal(payload.owner_questions.original_questions.length,8);assert.equal(payload.issues.counts.publicationConflicts,3);assert.equal(payload.issues.counts.futureDetailQuestions,8);}
  assert.equal(payload.work_queue.total, 2008);
  assert.match(html, /Owner questions that remain open/);
  assert.match(html, /Show all page corrections/);
  const payout = payload.claims.find(claim => claim.id === 'MCL-e2b956d14494e470');
  assert.equal(payout.status, 'PASS');
  assert.equal(payout.classification, 'PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION');
  assert.match(payout.reader_copy.finding, /published payout guidance/i);
  assert.match(payout.reader_copy.finding, /does not test invoice generation or payment processing/i);
  for (const ref of [
    'verification/evidence/2026-09-14-host-closure-correction-attempt-01/result.md',
    'verification/evidence/2026-09-14-host-closure-correction-attempt-02/plan.md',
    'verification/evidence/2026-09-14-host-closure-correction-attempt-02/change-map.json',
    'verification/evidence/2026-09-14-host-closure-correction-attempt-02/pre-narrowing-model.json',
    'verification/evidence/2026-09-14-host-closure-correction-attempt-02/focused-tests-01.log',
    'verification/evidence/2026-09-14-host-closure-correction-attempt-02/owner-payload-retest-02.log',
  ]) assert.equal(payload.files[ref].sha256, crypto.createHash('sha256').update(read(ref)).digest('hex'));
  assert.equal(JSON.stringify(model), before);
});

test('display ordering exposes open work first without mutating model claim order', () => {
  const sample = [{id:'pass',status:'PASS'}, {id:'pending',status:'UNVALIDATED'}, {id:'fail',status:'FAIL'}, {id:'blocked',status:'BLOCKED'}, {id:'na',status:'NOT_APPLICABLE'}];
  assert.deepEqual(sortHostReviewDisplay(sample).map(claim => claim.id), ['fail', 'blocked', 'pending', 'pass', 'na']);
  assert.deepEqual(sample.map(claim => claim.id), ['pass', 'pending', 'fail', 'blocked', 'na']);
});

test('real Datacenter page retains one unresolved certification question and one application instruction', () => {
  const page = model.pages.find(item => item.route === '/host/datacenter-status');
  const original = page.claims.map(claim => claim.id);
  const displayed = sortHostReviewDisplay(page.claims);
  assert.equal(page.claims.filter(claim => claim.status === 'FAIL').length, 0);
  const sourceReviewed=model.corrections.some(x=>x.id==='HOST-VERIFICATION-STORAGE-REVIEW-01');
  assert.equal(page.claims.filter(claim => claim.status === 'UNVALIDATED').length, sourceReviewed?0:1);
  if(sourceReviewed){assert.equal(page.claims.find(c=>c.id==='MCL-1998fd97e70ac6c0').status,'PASS');assert.ok(loadHostReviewOwnerQuestions({read,model,modelSha256}).questions.some(q=>q.id==='HQ-DATACENTER-CERTIFICATION'&&q.status==='UNVALIDATED'));}
  else assert.equal(displayed[0].id, 'MCL-1998fd97e70ac6c0');
  assert.equal(page.claims.find(claim => claim.id === 'MCL-0ae9c2fd5ac2ef9a').history.superseded_claims.length, 5);
  assert.deepEqual(page.claims.map(claim => claim.id), original);
});

test('production overlay has its own display ordering and keeps owner questions above live filters', () => {
  const source = fs.readFileSync(new URL('../review-server.mjs', import.meta.url), 'utf8');
  const functionSource = source.slice(source.indexOf('  function currentReviewHtml('), source.indexOf('  function renderPageContext()'));
  const context = {
    esc: value => String(value), currentWorkFilter: '', currentStatusFilter: 'ALL', currentClaimSectionFilter: '', currentCitationDefectFilter: 'ALL',
    currentCitationDefect: () => false, sectionFromHash: () => '', readableStatus: value => value,
    currentClaimLocator: (_page, claim) => ({id: 'current-' + claim.id, claim, checkedContent: {sections: claim.headings}}),
    passageWording: value => ({text: value.text}), claimWording: value => value, checkedContentLink: () => ({href: '#source'}),
    sourceTransitionHtml: () => '', authorityTransitionHtml: () => '', currentEvidenceRefs: () => '', readonlyProofHtml: () => '',
    installationIntakeRecord: () => null, installationIntakeHtml: () => '', currentSourceLinks: () => '',
  };
  vm.runInNewContext(functionSource + '\nglobalThis.renderCurrentReview = currentReviewHtml;', context);
  const claim = (id, status) => ({id, text: id, headings:['Apply'], status, reviewWork:{type:'Source',bucket:status === 'FAIL' ? 'correction' : 'completed',statusLabel:status}, readerCopy:{label:'Finding',finding:id,nextStep:'Check'}, evidenceRefs:[], sourceRefs:[], requiredEvidenceTypes:[], ownerRole:'Documentation', coverageState:'UNCHANGED_EXACT', rationale:'', nextAction:'', spans:[]});
  const queue = {total:2,statuses:{FAIL:1,PASS:1},statusLabels:{FAIL:'Correction needed',PASS:'Checked within scope'},buckets:[{id:'correction',label:'Correction needed',count:1}],sharedWordingGroups:0,sharedWordingOccurrences:0,groups:[]};
  const html = context.renderCurrentReview({available:true, page:{title:'Datacenter Status',route:'/host/datacenter-status',claims:[claim('pass','PASS'),claim('fail','FAIL')]}, workQueue:queue,citationDefects:{total:0,page:0},ownerQuestions:{available:true,questions:[{id:'HQ-DATACENTER-DOCUMENTS',status:'UNVALIDATED',question:'Which documents?',proposedTeams:['Product'],requiredDecisionOrSource:'Publish checklist.',relatedClaims:[{id:'fail',route:'/host/datacenter-status',headings:['Apply']}],coverageGaps:[]}]}});
  assert.ok(html.indexOf('data-current-claim="fail"') < html.indexOf('data-current-claim="pass"'));
  assert.ok(html.indexOf('Open owner questions') < html.indexOf('current-work-filter'));
  assert.match(html, /Page-wide exact claim summary:.*1 Correction needed.*1 Checked within scope/);
});

test('offline correction and owner-passage controls preserve the selected page and open exact source context', () => {
  const source = fs.readFileSync(new URL('../scripts/templates/host-docs-review.html', import.meta.url), 'utf8');
  const controls = Object.fromEntries(['search','page','lane','owner','work-category','status','queue-view'].map(id => [id, {value: id === 'page' ? '/host/datacenter-status' : 'kept'}]));
  let applied = 0, opened = '';
  const context = {$: id => controls[id], applyFilters: () => { applied++; }, showPassage: id => { opened = id; }};
  const corrections = source.slice(source.indexOf('function showAllCorrections()'), source.indexOf('function goToClaims()'));
  vm.runInNewContext(corrections + '\nglobalThis.showAll = showAllCorrections; globalThis.openOwner = openOwnerQuestionPassage;', context);
  context.showAll();
  assert.equal(controls.page.value, '/host/datacenter-status');
  assert.equal(controls.status.value, 'FAIL');
  assert.equal(controls.search.value, '');
  assert.equal(controls['work-category'].value, '');
  assert.equal(applied, 1);
  context.openOwner('MCL-08d534d1cc02eb2c');
  assert.equal(opened, 'MCL-08d534d1cc02eb2c');
});

test('offline selected-page summary stays exact while claim filters are narrowed', () => {
  const source = fs.readFileSync(new URL('../scripts/templates/host-docs-review.html', import.meta.url), 'utf8');
  const functionSource = source.slice(source.indexOf('function renderPageClaimSummary()'), source.indexOf('function sourceHTML('));
  const summary = {textContent:''};
  const context = {
    report:{claims:[
      ...Array.from({length:5}, (_, index) => ({route:'/host/datacenter-status',status:'FAIL',id:index})),
      ...Array.from({length:2}, (_, index) => ({route:'/host/datacenter-status',status:'UNVALIDATED',id:index + 10})),
      ...Array.from({length:10}, (_, index) => ({route:'/host/datacenter-status',status:'PASS',id:index + 20})),
    ]}, statusNames:{FAIL:'Correction needed',BLOCKED:'Prerequisite unavailable',UNVALIDATED:'Review pending',PASS:'Checked within scope',NOT_APPLICABLE:'Not applicable'},
    $: id => id === 'page' ? {value:'/host/datacenter-status',selectedOptions:[{text:'Datacenter Status'}]} : summary,
  };
  vm.runInNewContext(functionSource + '\nglobalThis.renderSummary = renderPageClaimSummary;', context);
  context.renderSummary();
  assert.match(summary.textContent, /Datacenter Status.*17 passages.*5 Correction needed.*2 Review pending.*10 Checked within scope/);
  assert.match(summary.textContent, /ignores search, status, category, owner, and citation filters/);
});
