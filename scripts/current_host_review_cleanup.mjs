/** Fail-closed repository-local editorial cleanup above the jurisdiction gate. */
import crypto from 'node:crypto';
import {loadJurisdiction} from './current_host_jurisdiction.mjs';

export const CLEANUP_PATH='verification/current-host-review-cleanup.json';
// Filled with the sealed registry digest when the independent proposal freezes.
export const CLEANUP_SHA256='ae2c8781c9d0d806818649052ad9bace4e8e6e9cf0b08e61f1d797049c20906c';
export const CLEANUP_ATTEMPT='verification/evidence/2026-09-11-host-review-cleanup-attempt-01';
export const CLEANUP_BASELINE=CLEANUP_ATTEMPT+'/before-current-host-docs-review.json';
export const CLEANUP_BASELINE_SHA256='f18e61882f50a2785f2fe863aba88ecf3d79af8a45bdcbf1596e6e64c6b7059d';
export const CLEANUP_MARKER='HOST-REVIEW-CLEANUP-01';
export const CLEANUP_DECISION='CURRENT_HOST_REVIEW_CLEANUP';
const STATIC='REPOSITORY_STATIC_CHECK';
const EDITORIAL=new Set(['EDITORIAL_SCOPE_OR_LEAD_IN','EDITORIAL_NAVIGATION_PREAMBLE']);
const STATIC_CLASSES=new Set(['REVIEWED_ADVICE','REVIEWED_NAVIGATION_INSTRUCTION','REVIEWED_EXAMPLE_CALCULATION']);
const METHODS=new Set(['MARKUP_OR_PREAMBLE_INSPECTION','CONTEXTUAL_INSPECTION','LOCAL_NAVIGATION_CHECK','ARITHMETIC_CHECK','MIXED_REPOSITORY_LOCAL_EDITORIAL_CHECKS']);
const AFTER=['classification','status','required_evidence_types','owner_role','rationale','next_action','evidence_refs','source_refs'];
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const req=(x,message)=>{if(!x)throw Error('cleanup: '+message)};
const canon=x=>Array.isArray(x)?x.map(canon):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canon(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canon(a))===JSON.stringify(canon(b));
const objhash=x=>hash(JSON.stringify(canon(x)));
const keys=(x,names)=>req(x&&typeof x==='object'&&!Array.isArray(x)&&equal(Object.keys(x).sort(),[...names].sort()),'missing/unknown fields');
const index=model=>new Map(model.pages.flatMap(page=>page.claims.map(claim=>[claim.id,claim])));

function correction(count){return {id:CLEANUP_MARKER,scope:`${count} exact editorial/navigation/calculation cleanup transitions`,
 history:'The sealed jurisdiction predecessor is hash-pinned. Original claim text, spans, statuses, sources and evidence remain available.',
 current:`${count} individually observed repository-local editorial checks; no Host, API, SSH, credentialed, paid or mutating operation was run.`,
 reason:'A completed navigation, arithmetic or contextual editorial inspection is limited to the documented passage. It does not establish product behavior, a runtime result, policy enforcement or human acceptance.'};}

export function projectReviewCleanup({read,exists}){
 const pinned=(ref,wanted)=>{req(typeof ref==='string'&&!ref.startsWith('/')&&!ref.includes('\\')&&ref.split('/').every(p=>p&&!['.','..'].includes(p)),'unsafe path');const value=read(ref);req(hash(value)===wanted,'digest drift '+ref);return value};
 req(CLEANUP_SHA256,'cleanup registry digest not sealed');const registryBytes=pinned(CLEANUP_PATH,CLEANUP_SHA256),registrySha256=CLEANUP_SHA256,registry=JSON.parse(registryBytes);
 keys(registry,['schema_version','record_type','generated_at','baseline','artifacts','transitions','result_ref']);
 req(registry.schema_version==='1.0'&&registry.record_type==='HOST_REVIEW_CLEANUP_TRANSITION','wrong registry type');
 req(equal(registry.baseline,{path:CLEANUP_BASELINE,sha256:CLEANUP_BASELINE_SHA256}),'baseline substitution');
 req(typeof registry.result_ref==='string'&&registry.result_ref.startsWith(CLEANUP_ATTEMPT+'/')&&(exists?exists(registry.result_ref):!!read(registry.result_ref)),'invalid result reference');
 const baseline=JSON.parse(pinned(CLEANUP_BASELINE,CLEANUP_BASELINE_SHA256));
 const predecessor=loadJurisdiction({read,model:baseline,exists});req(predecessor?.jurisdiction,'sealed jurisdiction predecessor required');
 const artifacts=new Map();
 for(const artifact of registry.artifacts){
  keys(artifact,['id','path','sha256','method']);const id=artifact.id;
  req(typeof id==='string'&&id&&!artifacts.has(id)&&METHODS.has(artifact.method),'invalid artifact');req(typeof artifact.path==='string'&&artifact.path.startsWith(CLEANUP_ATTEMPT+'/'),'artifact outside cleanup attempt');
  const capture=JSON.parse(pinned(artifact.path,artifact.sha256));keys(capture,['schema_version','record_type','generated_at','baseline','method','limits','source_candidate','support_artifacts','observations']);
  req(capture.schema_version==='1.0'&&capture.record_type==='HOST_REVIEW_CLEANUP_LOCAL_CHECKS','wrong cleanup capture');req(equal(capture.baseline,registry.baseline)&&capture.method===artifact.method,'capture baseline/method drift');req(typeof capture.limits==='string'&&capture.limits.trim()&&Array.isArray(capture.observations)&&Array.isArray(capture.support_artifacts),'capture limits/observations required');keys(capture.source_candidate,['path','sha256']);const candidate=JSON.parse(pinned(capture.source_candidate.path,capture.source_candidate.sha256));req(candidate.record_type==='HOST_EDITORIAL_INSPECTION_CANDIDATES'&&equal(candidate.baseline,registry.baseline)&&Array.isArray(candidate.records),'raw independent candidate drift');for(const support of capture.support_artifacts){keys(support,['path','sha256']);pinned(support.path,support.sha256)}artifacts.set(id,{artifact,capture,candidates:new Map(candidate.records.map(item=>[item.claim_id,item]))});
 }
 const model=structuredClone(baseline),before=index(baseline),after=index(model),seen=new Set(),presentation=new Map(predecessor.presentation);
 for(const entry of registry.transitions){
  keys(entry,['claim_id','before_sha256','artifact_id','observation_id','after','review_rationale','limits']);const id=entry.claim_id;
  req(before.has(id)&&!seen.has(id)&&entry.before_sha256===objhash(before.get(id)),'claim identity/predecessor drift');seen.add(id);
  const prior=before.get(id),claim=after.get(id);req(prior.status==='UNVALIDATED','only known selected UNVALIDATED claims may transition');keys(entry.after,AFTER);Object.assign(claim,structuredClone(entry.after));
  req(['PASS','NOT_APPLICABLE','UNVALIDATED'].includes(claim.status),'only PASS, NOT_APPLICABLE or scoped UNVALIDATED cleanup status');req(claim.text===prior.text&&equal(claim.headings,prior.headings)&&equal(claim.spans,prior.spans),'source literal/span mutation');
  req(prior.evidence_refs.every(ref=>claim.evidence_refs.some(item=>equal(item,ref)))&&prior.source_refs.every(ref=>claim.source_refs.some(item=>equal(item,ref))),'prior evidence/source dropped');
  const bundle=artifacts.get(entry.artifact_id);req(bundle,'missing cleanup artifact');const observation=bundle.capture.observations.find(item=>item.id===entry.observation_id);
  keys(observation,['id','claim_id','before_sha256','text','text_sha256','source_file','source_sha256','spans','method','result','finding','limits','context','expected','observed','links','arithmetic','candidate_record']);req(prior.spans.length&&prior.spans.every(span=>span.source_file===prior.spans[0].source_file),'cleanup spans must be in one exact source file');const sourceFile=prior.spans[0].source_file;
  req(observation.claim_id===id&&observation.before_sha256===entry.before_sha256&&observation.text===prior.text&&observation.text_sha256===hash(prior.text),'observation claim identity drift');
  req(observation.source_file===sourceFile&&equal(observation.spans,prior.spans)&&observation.source_sha256===hash(read(sourceFile)),'observation source/span drift');req(METHODS.has(observation.method)&&bundle.artifact.method==='MIXED_REPOSITORY_LOCAL_EDITORIAL_CHECKS'&&observation.finding===entry.review_rationale&&observation.limits===entry.limits,'observation rationale/limits drift');req(equal(observation.candidate_record,bundle.candidates.get(id)),'raw candidate record substitution');req(typeof observation.context==='string'&&read(sourceFile).toString().includes(observation.context)&&typeof observation.expected==='string'&&observation.expected.trim()&&typeof observation.observed==='string'&&observation.observed.trim(),'raw contextual expected/observed evidence missing');req(Array.isArray(observation.links),'navigation evidence must be a list');req(typeof entry.review_rationale==='string'&&entry.review_rationale.trim()&&typeof entry.limits==='string'&&entry.limits.trim(),'rationale/limits required');
  if(claim.status==='NOT_APPLICABLE')req(EDITORIAL.has(claim.classification)&&equal(claim.required_evidence_types,[])&&observation.method==='MARKUP_OR_PREAMBLE_INSPECTION'&&observation.result==='NOT_APPLICABLE'&&observation.arithmetic===null,'invalid editorial non-claim closure');
  else {req(STATIC_CLASSES.has(claim.classification)&&equal(claim.required_evidence_types,[STATIC])&&['CONTEXTUAL_INSPECTION','LOCAL_NAVIGATION_CHECK','ARITHMETIC_CHECK'].includes(observation.method)&&observation.result===(claim.status==='PASS'?'PASS':'UNVALIDATED'),'invalid bounded static closure');req(claim.evidence_refs.some(ref=>ref.artifact_ref===bundle.artifact.path),'selected static evidence missing');}
  if(claim.status==='PASS'&&observation.method==='LOCAL_NAVIGATION_CHECK')req(observation.links.length&&observation.arithmetic===null&&observation.links.every(item=>item&&typeof item==='object'&&equal(Object.keys(item).sort(),['destination','href','result'])&&item.result==='PASS'),'exact local navigation observation required');
  if(claim.status==='PASS'&&observation.method==='ARITHMETIC_CHECK')req(!observation.links.length&&observation.arithmetic&&typeof observation.arithmetic==='object'&&equal(Object.keys(observation.arithmetic).sort(),['expected','formula','inputs','observed'])&&observation.arithmetic.expected===observation.arithmetic.observed,'exact arithmetic observation required');
  if(observation.method==='CONTEXTUAL_INSPECTION')req(!observation.links.length&&observation.arithmetic===null,'contextual inspection must not pose as link/arithmetic proof');
  if(claim.status==='UNVALIDATED')req(observation.method==='CONTEXTUAL_INSPECTION'&&claim.rationale!==prior.rationale&&claim.next_action!==prior.next_action,'unvalidated cleanup needs exact current rationale and next action');
  claim.history={...prior.history,carry_decision:CLEANUP_DECISION,reason:(prior.history.reason||'')+' Exact repository-local cleanup observation; no product/runtime or human-acceptance result is inferred.'};claim.coverage_state='CHANGED';
  const earlier=presentation.get(id),observationIndex=bundle.capture.observations.indexOf(observation);presentation.set(id,{previous:structuredClone(prior),method:observation.method,reviewRationale:entry.review_rationale,remaining:entry.limits+' '+claim.next_action,registryRef:CLEANUP_PATH,baselineRef:CLEANUP_BASELINE,basis:[{kind:'DOCUMENTATION_CHECK',sourceLabel:'Documentation check',sourceLocator:'Observation '+observation.id,sourceUrl:null,artifactRef:bundle.artifact.path,method:observation.method,observationId:observation.id,excerpt:observation.finding,text_pointer:'/observations/'+observationIndex+'/finding',support_rationale:observation.limits}],auditHistory:earlier?[structuredClone(earlier)]:[],cleanup:{reviewRationale:entry.review_rationale,remaining:entry.limits}});
 }
 req(seen.size,'empty cleanup registry is not an additive transition');req([...before].filter(([id,claim])=>equal(claim,after.get(id))).length===before.size-seen.size,'unrelated claim drift');
 model.counts.claim_statuses={};for(const claim of after.values())model.counts.claim_statuses[claim.status]=(model.counts.claim_statuses[claim.status]||0)+1;model.generated_at=registry.generated_at;model.corrections.push(correction(seen.size));
 const artifactHashes=new Map(predecessor.artifactHashes);artifactHashes.set(CLEANUP_PATH,registrySha256);artifactHashes.set(CLEANUP_BASELINE,CLEANUP_BASELINE_SHA256);for(const {artifact,capture} of artifacts.values()){artifactHashes.set(artifact.path,artifact.sha256);artifactHashes.set(capture.source_candidate.path,capture.source_candidate.sha256);for(const support of capture.support_artifacts)artifactHashes.set(support.path,support.sha256);}
 const contextHashes=new Map(predecessor.contextHashes||[]);contextHashes.set(CLEANUP_PATH,registrySha256);contextHashes.set(CLEANUP_BASELINE,CLEANUP_BASELINE_SHA256);for(const {artifact,capture} of artifacts.values()){contextHashes.set(artifact.path,artifact.sha256);contextHashes.set(capture.source_candidate.path,capture.source_candidate.sha256);for(const support of capture.support_artifacts)contextHashes.set(support.path,support.sha256);}
 const matches=new Map([...predecessor.matches].map(([id,match])=>[id,{...match,claim:after.get(id),cleanup:registry.transitions.find(entry=>entry.claim_id===id)||null}]));
 return {...predecessor,model,presentation,matches,artifactHashes,contextHashes,cleanup:{registry,registrySha256,baseline:CLEANUP_BASELINE,baselineSha256:CLEANUP_BASELINE_SHA256,artifacts:[...artifacts.values()].map(({artifact})=>artifact),resultRef:registry.result_ref}};
}

export function loadReviewCleanup({read,model,exists}){
 const present=exists?exists(CLEANUP_PATH):(()=>{try{read(CLEANUP_PATH);return true}catch{return false}})();const marked=(model.corrections||[]).some(item=>item.id===CLEANUP_MARKER);
 if(!present){req(!marked,'cleanup-marked model has no registry');return null}const projected=projectReviewCleanup({read,exists});req(equal(model,projected.model),'whole model differs from cleanup projection');return projected;
}
