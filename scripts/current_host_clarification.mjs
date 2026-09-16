/** Independent reader for bounded, pinned Host-review clarification patches.
 * Registry context records review provenance only; it is never product proof.
 */
import crypto from 'node:crypto';

export const CLARIFICATION_PATH='verification/current-host-clarification.json';
export const CLARIFICATION_REGISTRY_SHA256='528460ae02f689bc1e6a3469af6fcb058073197a853611c72ec78a6473b3f66f';
export const CLARIFICATION_ATTEMPT='verification/evidence/2026-09-10-host-clarification-sweep-attempt-01';
export const CLARIFICATION_BASELINE_PATH=`${CLARIFICATION_ATTEMPT}/before-review.json`;
export const CLARIFICATION_BASELINE_SHA256='f1e6086481a372131db5f786c3ab390169bd7620b25a6fa37d033baf5cb779a7';
export const CLARIFICATION_MARKER='HOST-REVIEW-CLARIFICATION-SWEEP-01';
const CLAIM_FIELDS=new Set(['classification','required_evidence_types','owner_role','rationale','next_action']);
const METHODS=new Set(['ADVICE_REVIEW','ADVICE_WITH_FACTUAL_INPUTS','POLICY_SOURCE','POLICY_ACKNOWLEDGEMENT','STATIC_CHECK','TECHNICAL_SOURCE','MIXED','SETUP_INSTRUCTION']);
const EVIDENCE=new Set(['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','ACCOUNTABLE_OWNER_CONFIRMATION','AUTHORITATIVE_DOCUMENTATION_CITATION','REPOSITORY_STATIC_CHECK','PRODUCT_PUBLICATION_SOURCE']);
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
export const clarificationCanonical=value=>Array.isArray(value)?value.map(clarificationCanonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,clarificationCanonical(value[key])])):value;
export const clarificationHash=value=>hash(JSON.stringify(clarificationCanonical(value)));
const fail=reason=>{throw new Error(`clarification transition: ${reason}`)};
const requireThat=(value,reason)=>{if(!value)fail(reason)};
const keys=(value,required,optional=[],label='record')=>requireThat(value&&typeof value==='object'&&!Array.isArray(value)&&required.every(key=>Object.hasOwn(value,key))&&Object.keys(value).every(key=>required.includes(key)||optional.includes(key)),`invalid ${label} fields`);
const text=(value,label)=>requireThat(typeof value==='string'&&value.trim(),`missing ${label}`);
const safePath=value=>{requireThat(typeof value==='string'&&/^[A-Za-z0-9._/-]+$/.test(value)&&!value.startsWith('/')&&!value.split('/').some(p=>!p||p==='.'||p==='..'),'unsafe path');return value;};
const equal=(a,b)=>JSON.stringify(clarificationCanonical(a))===JSON.stringify(clarificationCanonical(b));
function index(model){const claims=new Map(),procedures=new Map(),nodes=new Map();for(const page of model.pages){for(const claim of page.claims){requireThat(!claims.has(claim.id),'duplicate predecessor claim ID');claims.set(claim.id,claim)}for(const procedure of page.procedures){requireThat(!procedures.has(procedure.id),'duplicate predecessor procedure ID');procedures.set(procedure.id,procedure);for(const node of procedure.nodes){requireThat(!nodes.has(node.id),'duplicate predecessor node ID');nodes.set(node.id,node)}}}return {claims,procedures,nodes}}
function after(value){requireThat(value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).length&&Object.keys(value).every(key=>CLAIM_FIELDS.has(key)),'unauthorized claim patch fields');for(const [key,item] of Object.entries(value)){if(key==='required_evidence_types')requireThat(Array.isArray(item)&&item.length&&new Set(item).size===item.length&&item.every(lane=>EVIDENCE.has(lane)),'invalid evidence enum');else text(item,`claim patch ${key}`)}}

/** `validatePredecessor` is supplied by the unchanged authority wrapper. */
export function validateClarificationInput({read,model,pins,validatePredecessor}){
  const artifactHashes=new Map();
  const pinnedRead=(ref,wanted)=>{safePath(ref);requireThat(/^[a-f0-9]{64}$/.test(wanted),'unsealed trusted digest');const bytes=read(ref);requireThat(hash(bytes)===wanted,`digest drift: ${ref}`);artifactHashes.set(ref,wanted);return bytes};
  const registryBytes=pinnedRead(CLARIFICATION_PATH,pins.registry),registry=JSON.parse(registryBytes);
  keys(registry,['schema_version','record_type','generated_at','baseline','claims','nodes','procedures'],[],'registry');
  requireThat(registry.schema_version==='1.0'&&registry.record_type==='HOST_REVIEW_CLARIFICATION_TRANSITION','wrong registry type');text(registry.generated_at,'generation time');keys(registry.baseline,['path','sha256'],[],'baseline');requireThat(registry.baseline.path===CLARIFICATION_BASELINE_PATH&&registry.baseline.sha256===pins.baseline,'baseline substitution');
  const baseline=JSON.parse(pinnedRead(registry.baseline.path,pins.baseline));
  // Phase-43 remains the independent predecessor gate.  No clarification
  // entry is parsed or applied until this callback accepts the frozen model.
  const authorityScan=validatePredecessor(baseline);
  const before=index(baseline),expected=structuredClone(baseline),out=index(expected),entries=new Map(),presentation=new Map();
  for(const entry of registry.claims){keys(entry,['claim_id','before_sha256','review_method','review_rationale','after'],[],'claim transition');const prior=before.claims.get(entry.claim_id);requireThat(prior&&!entries.has(entry.claim_id),'missing/duplicate claim ID');requireThat(entry.before_sha256===clarificationHash(prior),`claim predecessor drift: ${entry.claim_id}`);requireThat(!['PASS','NOT_APPLICABLE'].includes(prior.status),`PASS/N/A claim method/source remains exact: ${entry.claim_id}`);requireThat(METHODS.has(entry.review_method),'invalid review method');text(entry.review_rationale,'review rationale');after(entry.after);if(prior.status==='FAIL'&&prior.required_evidence_types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION'))requireThat(!Object.hasOwn(entry.after,'required_evidence_types')||entry.after.required_evidence_types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION'),`FAIL citation lane removed: ${entry.claim_id}`);if(prior.status==='BLOCKED')for(const field of ['classification','required_evidence_types','rationale','next_action'])requireThat(!Object.hasOwn(entry.after,field)||equal(entry.after[field],prior[field]),`BLOCKED prerequisite changed: ${entry.claim_id}`);Object.assign(out.claims.get(entry.claim_id),structuredClone(entry.after));entries.set(entry.claim_id,entry);presentation.set(entry.claim_id,{method:entry.review_method,previous:prior,reviewRationale:entry.review_rationale,remaining:out.claims.get(entry.claim_id).next_action,registryRef:CLARIFICATION_PATH,baselineRef:CLARIFICATION_BASELINE_PATH,basis:[]});}
  for(const [collection,priorIndex,outIndex,label] of [[registry.nodes,before.nodes,out.nodes,'node'],[registry.procedures,before.procedures,out.procedures,'procedure']]){const seen=new Set();for(const entry of collection){keys(entry,[`${label}_id`,'before_sha256','next_action'],[],`${label} transition`);const prior=priorIndex.get(entry[`${label}_id`]);requireThat(prior&&!seen.has(entry[`${label}_id`]),'missing/duplicate '+label+' ID');requireThat(entry.before_sha256===clarificationHash(prior),`${label} predecessor drift: ${entry[`${label}_id`]}`);requireThat(!['PASS','NOT_APPLICABLE'].includes(prior.status),`${label} is not unresolved/STALE: ${entry[`${label}_id`]}`);text(entry.next_action,`${label} next action`);outIndex.get(entry[`${label}_id`]).next_action=entry.next_action;seen.add(entry[`${label}_id`])}}
  expected.generated_at=registry.generated_at;
  expected.corrections.push({id:CLARIFICATION_MARKER,scope:'Bounded clarification transition',history:'Frozen phase-43 predecessor is hash-pinned and validated before patch projection.',current:`${entries.size} exact claim review-method corrections; ${registry.nodes.length} node and ${registry.procedures.length} procedure next-action corrections; registry SHA-256 ${pins.registry}.`,reason:'Review-method/action provenance only; no status, source, citation, evidence, span, or runtime-proof transition is authorized.'});
  requireThat(equal(model,expected),'whole model differs from clarification projection');
  const matches=new Map([...out.claims].map(([id,claim])=>[id,{claim,previous:before.claims.get(id),entry:entries.get(id)||null}]));
  return {registry,baseline,authorityScan,entries,presentation,matches,artifactHashes,registrySha256:hash(registryBytes),contextHashes:new Map([[CLARIFICATION_PATH,pins.registry],[CLARIFICATION_BASELINE_PATH,pins.baseline]])};
}

export function loadClarificationTransition({read,model,exists,validatePredecessor}){
  const present=exists?exists(CLARIFICATION_PATH):(()=>{try{read(CLARIFICATION_PATH);return true}catch{return false}})();
  const marked=(model.corrections||[]).some(item=>item.id===CLARIFICATION_MARKER);
  if(!present){requireThat(!marked,'missing registry for clarified model');return null}
  return validateClarificationInput({read,model,validatePredecessor,pins:{registry:CLARIFICATION_REGISTRY_SHA256,baseline:CLARIFICATION_BASELINE_SHA256}});
}
