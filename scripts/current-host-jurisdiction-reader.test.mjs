import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {hostReviewReaderCopy} from './host_review_reader_copy.mjs';
import {buildHostReviewQueue, describeHostReview} from './host_review_work_queue.mjs';
import {loadCurrentHostReviewTransition} from './current_host_review_transition.mjs';

const template = fs.readFileSync(new URL('./templates/host-docs-review.html', import.meta.url), 'utf8');
const server = fs.readFileSync(new URL('../review-server.mjs', import.meta.url), 'utf8');
const citationWarning = 'The required source citation is missing or incomplete. Link the official source for this statement.';
const escapeHTML = value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
function section(source, start, end) {
  const from = source.indexOf(start), to = source.indexOf(end, from + start.length);
  assert.ok(from !== -1 && to > from, `Production function boundaries: ${start}`);
  return source.slice(from, to);
}
const offlineWarningSource = template.split('\n').find(line => line.startsWith('const citationDefect=')) + '\n' +
  section(template, 'function citationDefectHTML(', 'function authorityScanHTML(');
const liveWarningSource = section(server, '  function currentCitationDefect(', '  function claimWording(') +
  section(server, '  function currentReviewHtml(', '  function renderPageContext(');

function offlineWarning(claim) {
  return vm.runInNewContext(offlineWarningSource + '\ncitationDefectHTML(claim);', {claim, escapeHTML});
}
function liveReview(claims, actualEvidence = false) {
  const current = claims.map(claim => ({
    ...claim, requiredEvidenceTypes: claim.required_evidence_types, readerCopy: claim.reader_copy, reviewWork: describeHostReview(claim),
    nextAction: claim.next_action, ownerRole: claim.owner_role, coverageState: claim.coverage_state,
    headings: claim.headings || ['Tax documents'], spans: claim.spans || [],
    evidenceRefs: claim.evidence_refs?.map(ref => ({...ref, artifactRef: ref.artifact_ref})) || claim.evidenceRefs,
  }));
  const evidenceFunctions = actualEvidence ? section(server, '  function sourceTransitionHtml(', '  function readonlyProofHtml(') : '';
  return vm.runInNewContext(evidenceFunctions + '\n' + liveWarningSource + '\ncurrentReviewHtml(review);', {
    review: {available: true, workQueue: buildHostReviewQueue(claims), page: {title: 'Tax Guide', route: '/host/guide-to-taxes', claims: current}},
    esc: escapeHTML, currentClaimSectionFilter: null, currentCitationDefectFilter: 'ALL', sectionFromHash: () => '',
    currentClaimLocator: (_page, claim) => ({id: claim.id, claim, checkedContent: {sections: claim.headings}, sourcePassages: [{text: claim.text}]}),
    passageWording: passage => ({text: passage.text}), claimWording: text => text, readableStatus: status => status,
    checkedContentLink: () => ({href: '#tax-documents'}), installationIntakeRecord: () => null,
    sourceTransitionHtml: () => '', authorityTransitionHtml: () => '', currentEvidenceRefs: () => '',
    readonlyProofHtml: () => '', installationIntakeHtml: () => '', currentSourceLinks: () => '',
    H100_DIRECT_POSTINSTALL_ADJUDICATION: 'unused-direct-registry', H100_DIRECT_POSTCHECK_ARTIFACT: 'unused-direct-artifact', H100_DIRECT_POSTCHECK_BY_CLAIM: new Map(),
  });
}

test('production readers separate contextual review notes from independent source proof without changing selectors', () => {
  const read = ref => fs.readFileSync(new URL('../' + ref, import.meta.url));
  const model = JSON.parse(read('verification/current-host-docs-review.json'));
  const transition = loadCurrentHostReviewTransition({read, model});
  const claims = new Map(model.pages.flatMap(page => page.claims).map(item => [item.id, {...item, reader_copy: hostReviewReaderCopy(item)}]));
  const transitions = Object.fromEntries(transition.presentation);
  const files = Object.fromEntries([...transition.jurisdiction.artifacts.values()].map(a => [a.path, {text: read(a.path).toString(), sha256: a.sha256}]));
  let dialogTitle = '', dialog = '';
  const offline = vm.createContext({report: {authority_scan: {transitions}, files}, claimMap: claims, escapeHTML, pill: () => '',
    showDialog: (title, content) => {dialogTitle = title; dialog = content;}});
  vm.runInContext(section(template, 'function authorityScanHTML(', 'function twoDefectTransitionHTML('), offline);
  const basisEndpoint = section(server, "        if (url.searchParams.has('basis')) {", '        if (authorityHistoryRef)');
  for (const id of ['CUR-708c718cf735c8b2', 'CUR-555543e9b2ceddb4', 'CUR-2ead4eda972e84b0', 'MCL-8fe2020c0e7efe26']) {
    const item = claims.get(id), scan = transitions[id], before = JSON.stringify(scan);
    offline.selectedId = id;
    const htmls = {offline: vm.runInContext('authorityScanHTML(claimMap.get(selectedId))', offline), live: liveReview([{...item, authorityScan: scan}], true)};
    for (const [reader, html] of Object.entries(htmls)) {
      const note = html.match(/<details class="[^"]*review-note[^"]*">[\s\S]*?<\/details>/)?.[0];
      assert.ok(note, `${reader}: neutral collapsed review note required`);
      assert.doesNotMatch(note.split('>')[0], /\bopen\b/);
      assert.match(note, /Review note — not an independent source/);
      assert.match(note, /Review scope/);
      assert.doesNotMatch(note, /What (?:this |the )?source proves/);
      assert.match(note, reader === 'offline' ? /class="callout partial review-note"/ : /class="vv-source-partial review-note"/);
      const foreground = html.replace(note, '');
      for (const [index, basis] of scan.basis.entries()) {
        const selected = basis.kind === 'CONTEXT_REVIEW' ? note : foreground;
        assert.ok(selected.includes(escapeHTML(basis.sourceLabel)), `${reader}: ${basis.sourceLabel}`);
        assert.ok(selected.includes(reader === 'offline' ? `data-basis="${index}"` : `&amp;basis=${index}`), `${reader}: preserved basis index ${index}`);
        if (basis.kind === 'CONTEXT_REVIEW') assert.ok(!foreground.includes(escapeHTML(basis.sourceLabel)));
      }
    }
    for (const [index, basis] of scan.basis.entries()) {
      offline.selector = index; vm.runInContext('showSourceBasis(selectedId,selector)', offline);
      assert.ok(dialog.includes(escapeHTML(basis.excerpt)));
      let selected = '';
      vm.runInNewContext('(() => {' + basisEndpoint + '})()', {url: new URL('http://127.0.0.1/?basis=' + index), scan,
        ref: basis.artifactRef, claim: item, hostReviewReaderCopy, esc: escapeHTML, expectedHash: files[basis.artifactRef].sha256,
        bytes: read(basis.artifactRef), evidenceTextForDisplay: bytes => bytes.toString(), res: {writeHead: () => {}, end: html => selected = html}});
      assert.ok(selected.includes(escapeHTML(basis.excerpt)));
      if (basis.kind === 'CONTEXT_REVIEW') {
        assert.equal(dialogTitle, 'Review note — not an independent source');
        for (const content of [dialog, selected]) {assert.match(content, /Review scope/); assert.doesNotMatch(content, /What (?:this |the )?source proves/);}
        assert.match(selected, /Review note — not an independent source/);
      } else {
        assert.equal(dialogTitle, 'Exact bound source excerpt');
        for (const content of [dialog, selected]) assert.match(content, /What this source proves/);
      }
    }
    assert.equal(JSON.stringify(scan), before, 'presentation grouping must not change the source bindings');
  }
});

test('production readers present local cleanup observations as neutral documentation checks with exact selectors', () => {
  const basis={kind:'DOCUMENTATION_CHECK',artifactRef:'verification/evidence/local-review.json',observationId:'CHECK-01',method:'CONTEXTUAL_INSPECTION',sourceLabel:'Documentation check',sourceLocator:'Observation CHECK-01',excerpt:'The advice is clear within this heading.',text_pointer:'/observations/0/finding',support_rationale:'Wording only; no operation was run.'};
  const scan={basis:[basis],cleanup:{reviewRationale:basis.excerpt,remaining:basis.support_rationale},remaining:basis.support_rationale,previous:{evidence_refs:[]}};
  const claim={id:'LOCAL-ONE',text:'Read the guide.',status:'PASS',classification:'REVIEWED_ADVICE',required_evidence_types:['REPOSITORY_STATIC_CHECK'],headings:['Guide'],spans:[],evidence_refs:[],authorityScan:scan};
  let shown;
  const context={claim,report:{authority_scan:{transitions:{[claim.id]:scan}},files:{[basis.artifactRef]:{text:'Retained record',sha256:'f'.repeat(64)}}},claimMap:new Map([[claim.id,claim]]),escapeHTML,pill:()=>'',showDialog:(title,body)=>{shown={title,body};}};
  const source=section(template,'function authorityScanHTML(','function twoDefectTransitionHTML(');
  const html=vm.runInNewContext(source+'\nauthorityScanHTML(claim);',context);
  assert.match(html,/class="callout partial documentation-check"/);assert.match(html,/data-basis="0"/);assert.match(html,/CHECK-01/);
  assert.doesNotMatch(html,/What the source proves|Open exact bound source/);
  vm.runInNewContext(source+'\nshowSourceBasis(claim.id,"0");',context);
  assert.equal(shown.title,'Exact documentation check');assert.match(shown.body,/Review scope/);assert.match(shown.body,/\/observations\/0\/finding/);assert.doesNotMatch(shown.body,/What this source proves/);
  const live=liveReview([claim],true);
  assert.match(live,/class="vv-source-partial documentation-check"/);assert.match(live,/basis=0/);assert.match(live,/CHECK-01/);assert.doesNotMatch(live,/What the source proves|Open exact bound source/);
  const responseSource=section(server,'          const sourceUrl = basis.sourceUrl;','          return;');
  let response;
  vm.runInNewContext(responseSource,{basis,scan,claim,esc:escapeHTML,expectedHash:'f'.repeat(64),bytes:Buffer.from('Retained record'),hostReviewReaderCopy,evidenceTextForDisplay:bytes=>String(bytes),res:{writeHead:()=>{},end:body=>{response=body;}}});
  assert.match(response,/<h1>Exact documentation check<\/h1>/);assert.match(response,/Review scope/);assert.match(response,/CHECK-01/);assert.doesNotMatch(response,/What this source proves/);
});

test('production live page queue shows shared wording without dropping individual passages or their statuses', () => {
  const claim={id:'LOCAL-ONE',text:'Read the guide.',status:'UNVALIDATED',classification:'REVIEWED_ADVICE',required_evidence_types:['REPOSITORY_STATIC_CHECK'],headings:['Guide'],spans:[],evidence_refs:[],owner_role:'Documentation',rationale:'Check clarity.',next_action:'Review this advice.'};
  const html=liveReview([claim,{...claim,id:'LOCAL-TWO'}]);
  assert.match(html,/Review work on this page/);assert.match(html,/2 passages/);assert.match(html,/Shared wording on this page: 1 compatible groups \/ 2 passages/);
  const policyGuide=html.match(/<details class="vv-reading-audit vv-review-guide">[\s\S]*?<\/details>/)?.[0];
  const queueDetails=html.match(/<details class="vv-reading-audit vv-work-queue-details">[\s\S]*?<\/details>/)?.[0];
  assert.ok(policyGuide);assert.doesNotMatch(policyGuide.split('>')[0],/\bopen\b/);
  assert.ok(queueDetails);assert.doesNotMatch(queueDetails.split('>')[0],/\bopen\b/);
  assert.ok(html.indexOf('id="current-work-filter"')<html.indexOf('vv-work-queue-details'));
  assert.ok(html.indexOf('id="current-status-filter"')<html.indexOf('vv-work-queue-details'));
  assert.ok(html.indexOf('data-current-work-category')>html.indexOf('vv-work-queue-details'));
  for(const id of ['LOCAL-ONE','LOCAL-TWO']){assert.equal(html.split('data-current-claim="'+id+'"').length,2);assert.match(html,new RegExp('data-current-queue-claim="'+id+'"'));}
  assert.equal(html.split('data-status="UNVALIDATED">Review pending').length,3);assert.doesNotMatch(html,/Needs evidence/);
});

test('active jurisdiction review keeps superseded limits and links in collapsed historical evidence', () => {
  const read = ref => fs.readFileSync(new URL('../' + ref, import.meta.url));
  const model = JSON.parse(read('verification/current-host-docs-review.json'));
  const transition = loadCurrentHostReviewTransition({read, model});
  const item = model.pages.flatMap(page => page.claims).find(c => c.id === 'MCL-8fe2020c0e7efe26');
  const scan = transition.presentation.get(item.id), before = JSON.stringify(item);
  const input = {...item, authorityScan: scan, reader_copy: hostReviewReaderCopy(item)};
  const html = liveReview([input], true);
  const audit = html.match(/<details class="vv-reading-history">[\s\S]*?<\/details>/)?.[0];
  assert.ok(audit, 'a collapsed historical evidence section is required');
  assert.doesNotMatch(audit.split('>')[0], /\bopen\b/);
  assert.match(audit, /Historical evidence and earlier limits/);
  const foreground = html.replace(audit, '');
  for (const ref of scan.previous.evidence_refs) {
    assert.ok(audit.includes(escapeHTML(ref.limit)), ref.id);
    assert.ok(audit.includes(encodeURIComponent(ref.artifact_ref)), ref.artifact_ref);
    assert.ok(audit.includes(escapeHTML(ref.id)), ref.id);
    assert.ok(!foreground.includes(escapeHTML(ref.limit)), 'old limit must not be a current limit: ' + ref.id);
  }
  assert.ok(foreground.includes(escapeHTML(scan.jurisdiction.remaining)));
  assert.match(foreground, /Current proof limits/);
  for (const [index, basis] of scan.basis.entries()) {
    assert.ok(foreground.includes(escapeHTML(basis.sourceLabel)));
    assert.ok(foreground.includes('&amp;basis=' + index), 'current source selector retained');
  }
  assert.equal(JSON.stringify(item), before, 'rendering must preserve the model and refs');
  const legacy = {...input, authorityScan: {...scan, jurisdiction: undefined}};
  const legacyHtml = liveReview([legacy], true);
  assert.doesNotMatch(legacyHtml, /vv-reading-history/);
  assert.ok(legacyHtml.includes(escapeHTML(scan.previous.evidence_refs[0].limit)), 'non-jurisdiction rendering remains unchanged');
});
const claim = (types = ['AUTHORITATIVE_DOCUMENTATION_CITATION'], extra = {}) => ({
  id: 'CITATION-FIXTURE', status: 'FAIL', classification: 'TAX_OR_REPORTING_REQUIREMENT',
  required_evidence_types: types, text: 'The source of this statement needs review.',
  rationale: 'A required source is missing.', next_action: 'Link the official source.', ...extra,
});

for (const reader of ['offline', 'live']) test(`actual ${reader} citation warning requests an official source without an unrelated runtime disclaimer`, () => {
  for (const types of [
    ['AUTHORITATIVE_DOCUMENTATION_CITATION'],
    ['AUTHORITATIVE_DOCUMENTATION_CITATION', 'REPOSITORY_STATIC_CHECK'],
    ['CANONICAL_IMPLEMENTATION_SOURCE', 'RUNTIME_OR_UI_OBSERVATION', 'AUTHORITATIVE_DOCUMENTATION_CITATION'],
  ]) {
    const fixture = claim(types);
    const html = reader === 'offline' ? offlineWarning(fixture) : liveReview([fixture]);
    assert.ok(html.includes(citationWarning), `${reader}: ${types.join(',')}`);
    const warning = reader === 'offline' ? html : html.match(/<div class="vv-citation-defect">[\s\S]*?<\/div>/)?.[0];
    assert.ok(warning, reader);
    assert.doesNotMatch(warning, /runtime|rental|test failed/i, reader);
  }
});

test('actual live citation summary describes missing sources, without classifying them as runtime checks', () => {
  const html = liveReview([claim()]);
  const summary = html.match(/<p class="vv-reading-counts">[\s\S]*?<\/p>/)?.[0];
  assert.ok(summary);
  assert.match(summary, /1 missing authoritative citations across Host pages; 1 on this page/);
  assert.doesNotMatch(summary, /runtime|test|rental/i);
});

test('actual renderers preserve pending decisions and do not warn for claims without a citation defect', () => {
  for (const fixture of [claim([], {status: 'FAIL'}), claim(undefined, {status: 'PASS'}), claim(undefined, {status: 'UNVALIDATED'})]) {
    assert.equal(offlineWarning(fixture), '');
    assert.doesNotMatch(liveReview([fixture]), /class="vv-citation-defect"/);
  }
  const pending = claim(undefined, {reader_copy: {pendingNote: 'Confirm <this> scoped rule.', label: 'Policy review', finding: 'Rule review pending.', nextStep: 'Cite the decision.'}});
  for (const html of [offlineWarning(pending), liveReview([pending])]) {
    assert.match(html, /Confirm &lt;this&gt; scoped rule\./);
    assert.ok(!html.includes(citationWarning));
  }
});

const baseline = JSON.parse(fs.readFileSync(new URL('../verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/before-review.json', import.meta.url)));
const baselineClaims = baseline.pages.flatMap(page => page.claims);
const taxGapIds = ['CUR-a991f28f683ba829', 'CUR-99fb8d131e321e03', 'CUR-93f089288e67669d', 'CUR-11f83626486ada1d', 'CUR-86b30052c0aa0b9c', 'CUR-8eb23dae453fdd8b'];
const baselineClaim = id => {
  const found = baselineClaims.find(item => item.id === id);
  assert.ok(found, `Missing frozen occurrence ${id}`);
  return found;
};

test('six exact unresolved Tax Guide copies explain the separate source gaps without changing recorded facts', () => {
  const before = JSON.stringify(baseline);
  assert.deepEqual(baselineClaims.filter(item => hostReviewReaderCopy(item).reviewKind === 'jurisdiction-source-gap').map(item => item.id).sort(), [...taxGapIds].sort());
  for (const id of taxGapIds) {
    const item = baselineClaim(id), copy = hostReviewReaderCopy(item);
    assert.equal(copy.reviewKind, 'jurisdiction-source-gap', id);
    assert.ok(copy.finding && copy.nextStep, id);
    assert.doesNotMatch(copy.finding + copy.nextStep, /runtime|test rental/i, id);
    assert.match(liveReview([{...item, reader_copy: copy}]), new RegExp(escapeHTML(copy.finding).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), id);
  }
  assert.equal(JSON.stringify(baseline), before);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-a991f28f683ba829')).finding, /agreement supports.*official source is still needed/i);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-99fb8d131e321e03')).finding, /withholding.*jurisdiction and period/i);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-93f089288e67669d')).finding, /outside the United States does not by itself settle US tax obligations/);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-11f83626486ada1d')).finding, /Wise payouts and the approved W-9 submission channel/);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-86b30052c0aa0b9c')).finding, /California does not determine VAT obligations/);
  assert.match(hostReviewReaderCopy(baselineClaim('CUR-8eb23dae453fdd8b')).finding, /invoice-display evidence.*does not determine whether VAT is owed, collected or remitted/);
});

test('Tax gap presentation expires for changed IDs, wording, status, classification, evidence lanes or review metadata', () => {
  for (const id of taxGapIds) {
    const original = baselineClaim(id);
    for (const change of [
      {id: original.id + '-CHANGED'}, {text: original.text + ' Changed.'}, {status: 'PASS'},
      {classification: original.classification + '_CHANGED'},
      {required_evidence_types: [...original.required_evidence_types, 'ACCOUNTABLE_OWNER_CONFIRMATION']},
      {rationale: original.rationale + ' Changed.'}, {next_action: original.next_action + ' Changed.'},
    ]) {
      assert.notEqual(hostReviewReaderCopy({...original, ...change}).reviewKind, 'jurisdiction-source-gap', id + JSON.stringify(change));
    }
    const {required_evidence_types, next_action, ...rest} = original;
    assert.deepEqual(hostReviewReaderCopy({...rest, requiredEvidenceTypes: required_evidence_types, nextAction: next_action}), hostReviewReaderCopy(original), id);
  }
});

const jurisdiction = JSON.parse(fs.readFileSync(new URL('../verification/current-host-jurisdiction.json', import.meta.url)));
const checkedLabels = new Map([
  ['CUR-708c718cf735c8b2', 'Advice checked'],
  ['CUR-555543e9b2ceddb4', 'Advice checked'],
  ['CUR-2ead4eda972e84b0', 'Advice checked'],
  ['MCL-8fe2020c0e7efe26', 'Advice and rule checked'],
  ['MCL-1536a1bd58d80927', 'Published program source checked'],
  ['MCL-c9882f043e407640', 'Published program source checked'],
  ['MCL-c8bf23127171e2b0', 'Published program source checked'],
  ['MCL-3acecd71e6a7b312', 'Published program source checked'],
]);
const checkedClaims = jurisdiction.transitions.map(record => ({...baselineClaim(record.claim_id), ...record.after}));

test('eight exact reviewed occurrences show bounded advice, advice-and-rule and program-source labels', () => {
  const before = JSON.stringify(checkedClaims);
  assert.deepEqual(checkedClaims.map(item => item.id).sort(), [...checkedLabels.keys()].sort());
  for (const item of checkedClaims) {
    const copy = hostReviewReaderCopy(item), expected = checkedLabels.get(item.id);
    assert.equal(copy.label, expected, item.id);
    assert.equal(copy.statusLabel, expected, item.id);
    assert.equal(item.status, 'PASS', item.id);
    assert.doesNotMatch(copy.finding + copy.nextStep, /runtime|test rental/i, item.id);
    const html = liveReview([{...item, reader_copy: copy}]);
    assert.ok(html.includes(escapeHTML(copy.finding)), item.id);
    assert.ok(html.includes('data-status="PASS">Checked within scope'), item.id);
    assert.ok(html.includes('<b>Review type:</b>') && html.includes(expected), item.id);
    assert.equal(offlineWarning({...item, reader_copy: copy}), '', item.id);
  }
  assert.equal(JSON.stringify(checkedClaims), before);
  const finding = id => hostReviewReaderCopy(checkedClaims.find(item => item.id === id)).finding;
  assert.match(finding('CUR-708c718cf735c8b2'), /account and platform’s available options/);
  assert.match(finding('CUR-555543e9b2ceddb4'), /does not decide.*form eligibility or income-reporting duties/);
  assert.match(finding('CUR-2ead4eda972e84b0'), /California guidance applies only when its rules apply to the host/);
  assert.match(finding('MCL-8fe2020c0e7efe26'), /host-side evidence.*rule against reviewing renter data.*does not establish report accuracy or a completed investigation/);
  assert.match(finding('MCL-1536a1bd58d80927'), /Actual ranking and reliability were not checked/);
  assert.match(finding('MCL-c9882f043e407640'), /does not promise a particular chat channel or response time; support delivery was not checked/);
  assert.match(finding('MCL-c8bf23127171e2b0'), /did not check.*ownership, eligibility or certification/);
  assert.match(finding('MCL-3acecd71e6a7b312'), /These excerpts do not specify which registration documents to submit or show that an applicant completed the checks\./);
  assert.match(finding('MCL-3acecd71e6a7b312'), /Secure Cloud datacenter partner audits/);
  assert.doesNotMatch(finding('MCL-3acecd71e6a7b312'), /do not require a particular registration filing/);
});

test('bounded checked labels expire for every guarded field and normalize live field names', () => {
  for (const original of checkedClaims) {
    for (const change of [
      {id: original.id + '-CHANGED'}, {text: original.text + ' Changed.'}, {status: 'UNVALIDATED'},
      {classification: original.classification + '_CHANGED'},
      {required_evidence_types: [...original.required_evidence_types, 'RUNTIME_OR_UI_OBSERVATION']},
      {rationale: original.rationale + ' Changed.'}, {next_action: original.next_action + ' Changed.'},
    ]) {
      assert.equal(hostReviewReaderCopy({...original, ...change}).statusLabel, undefined, original.id + JSON.stringify(change));
    }
    if (original.required_evidence_types.length > 1) {
      assert.equal(hostReviewReaderCopy({...original, required_evidence_types: [...original.required_evidence_types].reverse()}).statusLabel, undefined);
    }
    const {required_evidence_types, next_action, ...rest} = original;
    assert.deepEqual(hostReviewReaderCopy({...rest, requiredEvidenceTypes: required_evidence_types, nextAction: next_action}), hostReviewReaderCopy(original), original.id);
  }
});
