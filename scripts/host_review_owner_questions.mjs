/** Separate owner-decision handoff. It never changes claims, totals, or proof. */
import crypto from 'node:crypto';

export const OWNER_QUESTIONS_PATH = 'verification/current-host-owner-questions.json';
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const requiredText = (value, label) => {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`Invalid owner-question ${label}`);
  return value;
};
const exactKeys = (value, keys, label) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
    JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...keys].sort())) throw new Error(`Invalid owner-question ${label}`);
};
const claimField = (claim, snake, camel) => claim[snake] ?? claim[camel];

function currentClaims(model) {
  if (!model || !Array.isArray(model.pages)) throw new Error('Owner-question review model is unavailable');
  const rows = [];
  for (const page of model.pages) {
    if (!page || typeof page.route !== 'string' || !Array.isArray(page.claims)) throw new Error('Owner-question review page is invalid');
    for (const claim of page.claims) rows.push({ page, claim });
  }
  const ids = new Set(rows.map(({claim}) => claim.id));
  if (ids.size !== rows.length) throw new Error('Owner-question review claim IDs are not unique');
  return new Map(rows.map((row) => [row.claim.id, row]));
}

function validateRelatedClaim(value, claims) {
  exactKeys(value, ['claim_id', 'route', 'headings', 'source_links'], 'related claim');
  const claimId = requiredText(value.claim_id, 'claim ID');
  const row = claims.get(claimId);
  if (!row || row.page.route !== requiredText(value.route, 'related route') || !Array.isArray(value.headings) || !value.headings.length ||
    JSON.stringify(value.headings) !== JSON.stringify(row.claim.headings)) throw new Error(`Owner-question related claim drift: ${claimId}`);
  if (!Array.isArray(value.source_links)) throw new Error(`Invalid owner-question source links: ${claimId}`);
  const currentLinks = (claimField(row.claim, 'source_refs', 'sourceRefs') || []).map(ref => ref.path);
  if (new Set(value.source_links).size !== value.source_links.length || value.source_links.some(link => typeof link !== 'string' || !currentLinks.includes(link))) {
    throw new Error(`Owner-question current source link drift: ${claimId}`);
  }
  return { id: claimId, route: row.page.route, headings: [...row.claim.headings], sourceLinks: [...value.source_links],
    text: row.claim.text, status: row.claim.status };
}

export function loadHostReviewOwnerQuestions({ read, model, modelSha256 }) {
  try {
    if (typeof read !== 'function') throw new Error('Owner-question registry reader is unavailable');
    const raw = read(OWNER_QUESTIONS_PATH);
    const bytes = Buffer.isBuffer(raw) ? raw : Buffer.from(raw);
    const registry = JSON.parse(bytes.toString('utf8'));
    exactKeys(registry, ['schema_version', 'record_type', 'model_ref', 'model_sha256', 'questions'], 'registry');
    if (registry.schema_version !== '1.0' || registry.record_type !== 'HOST_REVIEW_OWNER_QUESTIONS' ||
      registry.model_ref !== 'verification/current-host-docs-review.json' || registry.model_sha256 !== modelSha256 ||
      !Array.isArray(registry.questions) || registry.questions.length === 0) throw new Error('Owner-question registry is missing, stale, or invalid');
    const claims = currentClaims(model), ids = new Set();
    const questions = registry.questions.map(question => {
      exactKeys(question, ['id', 'status', 'proposed_teams', 'question', 'required_decision_or_source', 'related_claims', 'coverage_gaps'], 'record');
      const id = requiredText(question.id, 'ID');
      if (!/^HQ-[A-Z0-9-]+$/.test(id) || ids.has(id) || question.status !== 'UNVALIDATED' ||
        !Array.isArray(question.proposed_teams) || !question.proposed_teams.length || question.proposed_teams.some(team => typeof team !== 'string' || !team.trim()) ||
        !Array.isArray(question.related_claims) || !question.related_claims.length || !Array.isArray(question.coverage_gaps) ||
        question.coverage_gaps.some(gap => typeof gap !== 'string' || !gap.trim())) throw new Error(`Invalid owner-question record: ${id}`);
      ids.add(id);
      return { id, status: 'UNVALIDATED', proposedTeams: [...question.proposed_teams], question: requiredText(question.question, 'question'),
        requiredDecisionOrSource: requiredText(question.required_decision_or_source, 'required decision or source'),
        relatedClaims: question.related_claims.map(item => validateRelatedClaim(item, claims)), coverageGaps: [...question.coverage_gaps] };
    });
    return { available: true, registryRef: OWNER_QUESTIONS_PATH, registrySha256: hash(bytes), questions };
  } catch (error) {
    return { available: false, registryRef: OWNER_QUESTIONS_PATH, error: String(error?.message || error) };
  }
}

export function requireHostReviewOwnerQuestions(options) {
  const projection = loadHostReviewOwnerQuestions(options);
  if (!projection.available) throw new Error(`Owner-question registry unavailable: ${projection.error}`);
  return projection;
}
