/** Presentation only. Every passage keeps its recorded status and individual evidence. */
export const REVIEW_STATUS_LABELS = Object.freeze({
  UNVALIDATED: 'Review pending', FAIL: 'Correction needed', BLOCKED: 'Prerequisite unavailable',
  PASS: 'Checked within scope', NOT_APPLICABLE: 'Not applicable',
});
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
  'Technical declaration': ['DECLARED_INTERFACE_OR_UNIT','REVIEWED_TECHNICAL_DECLARATION','IMPLEMENTATION_OR_CONCEPT','SUPPORT_SCOPE_WITH_TECHNICAL_CONTEXT'],
  'Technical behavior or workflow': ['ACCOUNT_CONFIGURATION_OR_PERMISSION','IMPLEMENTED_BEHAVIOR','CONTRACT_TERMS_AND_IMPLEMENTED_EFFECT','RUNTIME_BEHAVIOR','UI_SURFACE_OR_WORKFLOW','REVIEWED_UI_PROVIDER_OPTION','REVIEWED_SETUP_INSTRUCTION','INTERFACE_WITH_BACKEND_EFFECT','VOLUME_ATOMIC_CLAIM','VERIFICATION_ENFORCEMENT','REVIEWED_BEHAVIOR_DESCRIPTION','RUNTIME_DIAGNOSTIC_GUIDANCE'],
};
const reviewTypes = new Map(Object.entries(typeGroups).flatMap(([label, classes]) => classes.map(kind => [kind,label])));
const lanes = new Set(['REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','AUTHORITATIVE_DOCUMENTATION_CITATION','ACCOUNTABLE_OWNER_CONFIRMATION','PRODUCT_PUBLICATION_SOURCE']);
const field = (claim, snake, camel) => claim[snake] ?? claim[camel];
export function describeHostReview(claim) {
  const required = field(claim, 'required_evidence_types', 'requiredEvidenceTypes');
  const type = reviewTypes.get(claim.classification) || 'Needs triage';
  const statusLabel = REVIEW_STATUS_LABELS[claim.status] || 'Needs triage';
  const unknown = type === 'Needs triage' || statusLabel === 'Needs triage' || !Array.isArray(required) || required.some(item => !lanes.has(item)) || (!required.length && type !== 'Editorial');
  const completed = !unknown && ['PASS','NOT_APPLICABLE'].includes(claim.status);
  const bucket = unknown ? 'triage' : completed ? 'completed' : claim.status === 'FAIL' ? 'correction' : claim.status === 'BLOCKED' ? 'blocked' :
    required.includes('RUNTIME_OR_UI_OBSERVATION') ? 'technical' : required.some(item => item !== 'REPOSITORY_STATIC_CHECK') ? 'source' :
      required.length || type === 'Editorial' ? 'documentation' : 'triage';
  const scopeLabel = completed && claim.status === 'PASS' && required?.length === 1 && required[0] === 'REPOSITORY_STATIC_CHECK'
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
  return {total: claims.length, buckets, statuses, statusLabels: REVIEW_STATUS_LABELS, types, groups,
    sharedWordingGroups: groups.filter(group => group.occurrenceIds.length > 1).length,
    sharedWordingOccurrences: groups.filter(group => group.occurrenceIds.length > 1).reduce((sum,group) => sum + group.occurrenceIds.length,0),
    countMeaning: 'Counts are passages, not unique questions. Shared wording does not mean the same proven fact. Each passage keeps its own evidence and review status.'};
}
