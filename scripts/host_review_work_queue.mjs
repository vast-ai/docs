/** Presentation only. Every passage keeps its recorded status and individual evidence. */
export const REVIEW_STATUS_LABELS = Object.freeze({
  UNVALIDATED: 'Review pending', FAIL: 'Correction needed', BLOCKED: 'Prerequisite unavailable',
  PASS: 'Checked within scope', NOT_APPLICABLE: 'Not applicable',
});
// Presentation priority only. Claim payloads retain their source/model order.
export const REVIEW_STATUS_DISPLAY_ORDER = Object.freeze(['FAIL', 'BLOCKED', 'UNVALIDATED', 'PASS', 'NOT_APPLICABLE']);
export function reviewStatusRank(status) {
  const rank = REVIEW_STATUS_DISPLAY_ORDER.indexOf(status);
  return rank === -1 ? REVIEW_STATUS_DISPLAY_ORDER.length : rank;
}
export function sortHostReviewDisplay(claims) {
  return claims.map((claim, index) => ({claim, index})).sort((left, right) =>
    reviewStatusRank(left.claim.status) - reviewStatusRank(right.claim.status) || left.index - right.index).map(item => item.claim);
}
export const REVIEW_WORK_BUCKETS = Object.freeze([
  {id: 'documentation', label: 'Documentation checks', description: 'Review advice, links, examples and wording.'},
  {id: 'source', label: 'Source/citation checks', description: 'Check the relevant code, publication or official rule.'},
  {id: 'technical', label: 'Technical verification', description: 'Review the required technical source and retained execution or UI evidence. This queue grants no permission to run a test.'},
  {id: 'blocked', label: 'Prerequisite unavailable', description: 'Resolve the specific missing permission, input or environment.'},
  {id: 'correction', label: 'Correction needed', description: 'Correct the recorded defect or missing citation, then recheck.'},
  {id: 'triage', label: 'Needs triage', description: 'The review type, status or required check is unrecognized. Inspect the record before assigning work.'},
  {id: 'completed', label: 'Completed checks', description: 'Checked within the recorded scope, or explicitly not applicable. This is not human acceptance.'},
]);
const typeGroups = {
  Advice: ['REVIEWED_ADVICE','REVIEWED_ADVICE_WITH_FACTUAL_INPUTS','OPERATIONAL_ADVICE_WITH_TECHNICAL_SUBCLAIMS','REVIEWED_ADVICE_WITH_GOVERNING_RULE'],
  Navigation: ['REVIEWED_NAVIGATION_INSTRUCTION','NAVIGATION_CONTRACT','BOUNDED_NAVIGATION'],
  Calculation: ['REVIEWED_EXAMPLE_CALCULATION'],
  Editorial: ['EDITORIAL_NAVIGATION_PREAMBLE','EDITORIAL_SCOPE_OR_LEAD_IN','EDITORIAL_STATIC_API_ROUTING'],
  'Published source or rule': ['PRODUCT_DESCRIPTION','GOVERNING_REQUIREMENT','PUBLISHED_SOURCE_CLAUSE','REVIEWED_POLICY_RULE','PROGRAM_ELIGIBILITY_OR_BENEFIT','PUBLISHED_FINANCIAL_RULE','PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION','PUBLICATION_DESCRIPTION','PUBLISHED_TERMS_SUMMARY','TAX_OR_REPORTING_ASSERTION','REVIEWED_POLICY_REFERENCE','HIGH_LEVEL_PRODUCT_DESCRIPTION'],
  'Technical declaration': ['DECLARED_INTERFACE_OR_UNIT','REVIEWED_TECHNICAL_DECLARATION','IMPLEMENTATION_OR_CONCEPT','SUPPORT_SCOPE_WITH_TECHNICAL_CONTEXT','REVIEWED_DIAGNOSTIC_RECIPE'],
  'Technical behavior or workflow': ['ACCOUNT_CONFIGURATION_OR_PERMISSION','IMPLEMENTED_BEHAVIOR','CONTRACT_TERMS_AND_IMPLEMENTED_EFFECT','RUNTIME_BEHAVIOR','UI_SURFACE_OR_WORKFLOW','REVIEWED_UI_PROVIDER_OPTION','REVIEWED_SETUP_INSTRUCTION','INTERFACE_WITH_BACKEND_EFFECT','VOLUME_ATOMIC_CLAIM','VERIFICATION_ENFORCEMENT','REVIEWED_BEHAVIOR_DESCRIPTION','RUNTIME_DIAGNOSTIC_GUIDANCE'],
};
const reviewTypes = new Map(Object.entries(typeGroups).flatMap(([label, classes]) => classes.map(kind => [kind,label])));
const lanes = new Set(['STATIC_CONTEXT_REVIEW','REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','AUTHORITATIVE_DOCUMENTATION_CITATION','ACCOUNTABLE_OWNER_CONFIRMATION','PRODUCT_PUBLICATION_SOURCE','PRIMARY_ENGINEERING_SOURCE','PUBLISHED_VENDOR_DOCUMENTATION']);
const field = (claim, snake, camel) => claim[snake] ?? claim[camel];
export function describeHostReview(claim) {
  const required = field(claim, 'required_evidence_types', 'requiredEvidenceTypes');
  const type = reviewTypes.get(claim.classification) || 'Needs triage';
  const statusLabel = REVIEW_STATUS_LABELS[claim.status] || 'Needs triage';
  const unknown = type === 'Needs triage' || statusLabel === 'Needs triage' || !Array.isArray(required) || required.some(item => !lanes.has(item)) || (!required.length && type !== 'Editorial');
  const completed = !unknown && ['PASS','NOT_APPLICABLE'].includes(claim.status);
  const bucket = unknown ? 'triage' : completed ? 'completed' : claim.status === 'FAIL' ? 'correction' : claim.status === 'BLOCKED' ? 'blocked' :
    required.includes('RUNTIME_OR_UI_OBSERVATION') ? 'technical' : required.some(item => !['REPOSITORY_STATIC_CHECK','STATIC_CONTEXT_REVIEW'].includes(item)) ? 'source' :
      required.length || type === 'Editorial' ? 'documentation' : 'triage';
  const scopeLabel = completed && claim.status === 'PASS' && required?.length === 1 && ['REPOSITORY_STATIC_CHECK','STATIC_CONTEXT_REVIEW'].includes(required[0])
    ? ({Advice:'Advice checked',Navigation:'Links and wording checked',Calculation:'Calculation checked',Editorial:'Wording checked'}[type] || 'Repository check completed') : '';
  return {type, classification: claim.classification || '', status: claim.status, statusLabel, scopeLabel, bucket, completed, needsTriage: bucket === 'triage'};
}
// Only normalize CRLF. Even trailing whitespace can change shell continuation
// semantics, so case, punctuation, spacing and line boundaries remain exact.
export const normalizeSharedWording = text => String(text ?? '').replace(/\r\n/g, '\n');
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key,val]) => [key.replace(/_([a-z])/g, (_,c) => c.toUpperCase()),canonical(val)]).sort(([a],[b]) => a.localeCompare(b)));
  return value;
}
function sharedKey(claim, work) {
  return JSON.stringify(canonical({
    text: normalizeSharedWording(claim.text), type: work.type, classification: claim.classification, status: claim.status,
    lanes: field(claim,'required_evidence_types','requiredEvidenceTypes'), owner: field(claim,'owner_role','ownerRole'),
    rationale: claim.rationale, nextAction: field(claim,'next_action','nextAction'), headings: claim.headings,
    prerequisites: claim.prerequisites ?? claim.prerequisite ?? claim.blockers ?? null,
    evidenceRefs: field(claim,'evidence_refs','evidenceRefs') || [], sourceRefs: field(claim,'source_refs','sourceRefs') || [],
  }));
}
export function buildHostReviewQueue(claims) {
  const buckets = REVIEW_WORK_BUCKETS.map(bucket => ({...bucket, count: 0}));
  const counts = new Map(buckets.map(bucket => [bucket.id,bucket]));
  const grouped = new Map(), statuses = {}, types = {}, ids = new Set();
  for (const claim of claims) {
    if (!claim.id || ids.has(claim.id)) throw new Error('Review queue requires distinct passage IDs');
    ids.add(claim.id);
    const work = describeHostReview(claim);
    counts.get(work.bucket).count++;
    statuses[claim.status] = (statuses[claim.status] || 0) + 1;
    types[work.type] = (types[work.type] || 0) + 1;
    // Completed records and unknown types never imply shared open work.
    const key = work.completed || work.needsTriage ? claim.id : sharedKey(claim,work);
    if (!grouped.has(key)) grouped.set(key, {id: `wording-${grouped.size + 1}`, bucket: work.bucket, type: work.type, status: claim.status, occurrenceIds: []});
    grouped.get(key).occurrenceIds.push(claim.id);
  }
  const groups = [...grouped.values()];
  return {total: claims.length, buckets, statuses, statusLabels: REVIEW_STATUS_LABELS, statusDisplayOrder: REVIEW_STATUS_DISPLAY_ORDER, types, groups,
    sharedWordingGroups: groups.filter(group => group.occurrenceIds.length > 1).length,
    sharedWordingOccurrences: groups.filter(group => group.occurrenceIds.length > 1).reduce((sum,group) => sum + group.occurrenceIds.length,0),
    countMeaning: 'Counts are passages, not unique questions. Shared wording does not mean the same proven fact. Each passage keeps its own evidence and review status.'};
}

/** A review landing page, not another adjudication or a release-gate count.
 * Page grouping is deliberately transparent: it asserts no shared root cause.
 * UNVALIDATED alone never creates a finding or workflow follow-up.
 */
export function buildHostReviewIssues({pages, ownerQuestions, originalFindings = [], sourceFamilyTransitions = []}) {
  if (!Array.isArray(pages) || !Array.isArray(ownerQuestions) || !Array.isArray(sourceFamilyTransitions)) throw new Error('Issue view requires current pages, validated owner questions and explicit source-family transitions');
  const claims = pages.flatMap(page => page.claims);
  const ids = new Set(claims.map(claim => claim.id));
  if (ids.size !== claims.length) throw new Error('Issue view requires distinct passage IDs');
  const currentClaims = new Map(pages.flatMap(page => page.claims.map(claim => [claim.id, {claim, page}])));
  const sourceIds = new Set();
  const sourceFollowUps = sourceFamilyTransitions.filter(entry => entry?.decision === 'residual' && entry.after?.status === 'UNVALIDATED').map(entry => {
    const current = currentClaims.get(entry.claim_id);
    if (!current || sourceIds.has(entry.claim_id) || current.claim.status !== 'UNVALIDATED' ||
        entry.after.text !== current.claim.text || typeof entry.after.next_action !== 'string' || !entry.after.next_action.trim() ||
        entry.after.next_action !== current.claim.next_action) throw new Error('Issue view source follow-up does not match a distinct current reviewed residual');
    sourceIds.add(entry.claim_id);
    const {claim, page} = current;
    // Quick-lookup rows use their literal diagnostic name; prose uses its heading.
    const title = /^\|\s*`([^`]+)`\s*\|/.exec(claim.text)?.[1] || claim.headings?.at(-1) || page.title;
    return {id: `source:${claim.id}`, claimId: claim.id, route: page.route, title, nextAction: entry.after.next_action};
  });
  const ownerIds = new Set();
  const questions = ownerQuestions.map(question => {
    if (!question.id || ownerIds.has(question.id) || !Array.isArray(question.relatedClaims) || question.relatedClaims.some(claim => !ids.has(claim.id))) throw new Error('Issue view owner mapping is invalid');
    ownerIds.add(question.id);
    return {id: question.id, claimIds: question.relatedClaims.map(claim => claim.id),
      routes: [...new Set(question.relatedClaims.map(claim => claim.route))]};
  });
  const corrections = [], workflows = [];
  for (const page of pages) {
    const failIds = page.claims.filter(claim => claim.status === 'FAIL').map(claim => claim.id);
    if (failIds.length) corrections.push({id: `correction:${page.route}`, route: page.route, title: page.title,
      claimIds: failIds, ownerQuestionIds: questions.filter(question => question.claimIds.some(id => failIds.includes(id))).map(question => question.id)});
    const blocked = page.claims.filter(claim => claim.status === 'BLOCKED');
    // Use only top-level procedure outcomes; child failures are detail, not extra issues.
    const procedures = (page.procedures || []).filter(procedure => ['FAIL','BLOCKED'].includes(procedure.status)).map(procedure => ({
      id: procedure.id, title: procedure.title, status: procedure.status, coverage_state: procedure.coverage_state,
      spans: procedure.spans, limits: procedure.limits, history: procedure.history,
      recorded_nodes: (procedure.nodes || []).filter(node => ['FAIL','BLOCKED'].includes(node.status)),
    }));
    if (blocked.length || procedures.length) workflows.push({id: `workflow:${page.route}`, route: page.route, title: page.title,
      claimIds: blocked.map(claim => claim.id), procedures,
      ownerQuestionIds: questions.filter(question => question.claimIds.some(id => blocked.some(claim => claim.id === id))).map(question => question.id),
      // Explicit fallbacks ensure a new/unmapped BLOCKED record cannot disappear.
      unassignedClaimIds: blocked.filter(claim => !questions.some(question => question.claimIds.includes(claim.id))).map(claim => claim.id),
    });
  }
  return {corrections, questions, workflows, sourceFollowUps,
    counts: {correctionTopics: corrections.length, correctionPassages: corrections.reduce((sum,group) => sum + group.claimIds.length,0),
      ownerQuestions: questions.length, workflowPageGroups: workflows.length,
      recordedProcedures: workflows.reduce((sum,group) => sum + group.procedures.length,0),
      blockedPassages: workflows.reduce((sum,group) => sum + group.claimIds.length,0)},
    originalFindings: {total: originalFindings.length, addressed: originalFindings.filter(finding => finding.disposition === 'CORRECT_NOW').length},
    limit: 'These lists overlap and are not a total issue count or an automatic release gate. Recorded prerequisites may have changed. Reuse existing evidence and reassess the gap before deciding whether another check is needed. Unvalidated passage coverage remains in the full ledger.'};
}
