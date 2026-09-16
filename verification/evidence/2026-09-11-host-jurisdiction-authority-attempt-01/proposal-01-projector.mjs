/** Eight sealed source/advice corrections; no operational or acceptance credit. */
import crypto from 'node:crypto';
import {loadTermsBinding} from './current_host_terms_binding.mjs';
export const JURISDICTION_PATH='verification/current-host-jurisdiction.json';
export const JURISDICTION_SHA256='babb63b8ddc584d2718958d4330a9bb9edc9960c1e74d82aee6b9bb0925bc1fb';
export const JURISDICTION_ATTEMPT='verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01';
export const JURISDICTION_BASELINE=JURISDICTION_ATTEMPT+'/before-review.json';
export const JURISDICTION_BASELINE_SHA256='e66ff7fe9253634c7ffcb2571816728a39549cf0236dc7052a8c1aab8d081b8a';
export const JURISDICTION_MARKER='HOST-JURISDICTION-01';
export const JURISDICTION_DECISION='CURRENT_HOST_JURISDICTION';
const SOURCES={'host/guide-to-taxes.mdx':[25,26,27],'host/datacenter-status.mdx':[19,20,25,26]};
const TAX=new Set(['CUR-708c718cf735c8b2','CUR-555543e9b2ceddb4','CUR-2ead4eda972e84b0']);
const WORKLOAD='MCL-8fe2020c0e7efe26';
const PROGRAM=new Set(['MCL-1536a1bd58d80927','MCL-c9882f043e407640','MCL-c8bf23127171e2b0','MCL-3acecd71e6a7b312']);
export const JURISDICTION_IDS=new Set([...TAX,WORKLOAD,...PROGRAM]);
const STATIC='REPOSITORY_STATIC_CHECK',CITE='AUTHORITATIVE_DOCUMENTATION_CITATION';
const AFTER=['classification','status','required_evidence_types','owner_role','rationale','next_action','text','headings','spans','evidence_refs','source_refs'];
const HISTORY_REASON=' Exact contextual advice and independent source review; no operational result or human acceptance is inferred.';
const NODE_LIMIT='Previous procedure span crosses the jurisdiction source edit; no procedure evidence transfers.';
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const req=(x,message)=>{if(!x)throw Error('jurisdiction: '+message)};
const canon=x=>Array.isArray(x)?x.map(canon):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canon(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canon(a))===JSON.stringify(canon(b)),objhash=x=>hash(JSON.stringify(canon(x)));
const keys=(x,names)=>req(x&&typeof x==='object'&&!Array.isArray(x)&&equal(Object.keys(x).sort(),[...names].sort()),'missing/unknown fields');
const lines=bytes=>bytes.toString().split(/\r?\n/).slice(0,bytes.toString().endsWith('\n')?-1:undefined);
const index=model=>new Map(model.pages.flatMap(p=>p.claims.map(c=>[c.id,c])));
const difference=(a,b,at='$')=>{if(equal(a,b))return '';if(!a||!b||typeof a!=='object'||typeof b!=='object')return at;for(const k of new Set([...Object.keys(a),...Object.keys(b)])){if(!Object.hasOwn(a,k)||!Object.hasOwn(b,k))return at+'.'+k;const child=difference(a[k],b[k],at+'.'+k);if(child)return child}return at};
function pointer(capture,ref){
 req(['/text','/source_text','/excerpts/0/text','/sections/6/text',...Array.from({length:8},(_,i)=>`/reviews/${i}/finding`)].includes(ref),'invalid source pointer');
 let value=capture,parent;for(const part of ref.slice(1).split('/')){parent=value;value=value?.[part]}
 req(typeof value==='string'&&value.trim(),'missing selected source text');
 if(ref.endsWith('/text')&&parent?.text_sha256)req(parent.text_sha256===hash(value),'selected source text hash drift');return value;
}
function correction(sources){return {id:JURISDICTION_MARKER,scope:'Eight exact Tax Guide, Workload Policy and Datacenter source/advice corrections',
 history:'The complete Terms predecessor is hash-pinned and validated with the exact frozen Tax Guide and Datacenter bytes. Original wording, failures and all previous evidence remain available.',
 current:'8 bounded claim transitions; 2 exact source transitions: '+sources.map(s=>s.path+' '+s.before_sha256+' → '+s.after_sha256).join('; ')+'.',
 reason:'Contextual advice, existing Agreement rule and published program scope only; no tax determination, runtime outcome, certification, procedure completion or human acceptance is inferred.'};}

export function projectJurisdiction({read,exists}){
 const pinned=(ref,wanted)=>{req(typeof ref==='string'&&!ref.startsWith('/')&&!ref.includes('\\')&&ref.split('/').every(p=>p&&!['.','..'].includes(p)),'unsafe path');const value=read(ref);req(hash(value)===wanted,'digest drift '+ref);return value};
 const bytes=pinned(JURISDICTION_PATH,JURISDICTION_SHA256),registry=JSON.parse(bytes);
 keys(registry,['schema_version','record_type','generated_at','baseline','sources','artifacts','retained_raw_sources','transitions']);
 req(registry.schema_version==='1.0'&&registry.record_type==='HOST_JURISDICTION_TRANSITION','wrong registry type');
 req(equal(registry.baseline,{path:JURISDICTION_BASELINE,sha256:JURISDICTION_BASELINE_SHA256}),'baseline substitution');
 const old=new Map(),current=new Map(),edited=new Map();
 for(const source of registry.sources){
  keys(source,['path','before_sha256','after_sha256','before_artifact','changed_lines']);const ref=source.path;
  req(Object.hasOwn(SOURCES,ref)&&!old.has(ref)&&equal(source.changed_lines,SOURCES[ref]),'out-of-scope source');keys(source.before_artifact,['path','sha256']);
  old.set(ref,pinned(source.before_artifact.path,source.before_artifact.sha256));req(hash(old.get(ref))===source.before_sha256,'before source mismatch');
  current.set(ref,pinned(ref,source.after_sha256));const left=lines(old.get(ref)),right=lines(current.get(ref));req(left.length===right.length,'source line count changed');
  const changed=left.flatMap((line,i)=>line===right[i]?[]:[i+1]);req(equal(changed,SOURCES[ref]),'source edits exceed exact approved lines');edited.set(ref,new Set(changed));
 }
 req(equal([...old.keys()].sort(),Object.keys(SOURCES).sort()),'two source transitions required');
 const baseline=JSON.parse(pinned(JURISDICTION_BASELINE,JURISDICTION_BASELINE_SHA256));
 const overlay=ref=>old.has(ref)?old.get(ref):read(ref);
 const predecessor=loadTermsBinding({read:overlay,model:baseline,exists});req(predecessor?.terms,'sealed Terms predecessor required');
 const artifacts=new Map();
 for(const artifact of registry.artifacts){
  keys(artifact,['id','path','sha256','kind','origin','source_label']);const id=artifact.id;
  req(!artifacts.has(id)&&artifact.path.startsWith('verification/evidence/'),'invalid artifact');
  const bytes=pinned(artifact.path,artifact.sha256),capture=JSON.parse(bytes);artifacts.set(id,{...artifact,bytes,capture});
  if(artifact.kind==='CONTEXT_REVIEW')req(id==='context-review'&&capture.record_type==='CONTEXTUAL_SOURCE_AND_ADVICE_REVIEW','invalid contextual review');
  else {
   req(capture.url===artifact.origin.url,'capture origin drift');
   if(Object.hasOwn(capture,'body'))req(capture.response_status===200&&hash(capture.body)===capture.body_sha256&&hash(capture.text)===capture.text_sha256,'public capture response/hash drift');
   else if(Object.hasOwn(capture,'source_text')){req(hash(capture.source_text)===capture.source_text_sha256,'provider/publication text hash drift');if(capture.raw_artifact_ref)pinned(capture.raw_artifact_ref,capture.raw_artifact_sha256)}
   else req(id==='agreement'&&capture.url==='https://cloud.vast.ai/host/agreement','unsupported capture');
  }
 }
 for(const item of registry.retained_raw_sources)pinned(item.path,item.sha256);
 const model=structuredClone(baseline),before=index(baseline),after=index(model),seen=new Set(),presentation=new Map(predecessor.presentation);
 const review=artifacts.get('context-review').capture;req(review.reviews.length===8,'eight contextual reviews required');
 for(const entry of registry.transitions){
  keys(entry,['claim_id','before_sha256','after','basis','review_rationale','limits']);const id=entry.claim_id;
  req(JURISDICTION_IDS.has(id)&&!seen.has(id)&&entry.before_sha256===objhash(before.get(id)),'claim identity/predecessor drift');seen.add(id);
  const prior=before.get(id),claim=after.get(id);keys(entry.after,AFTER);Object.assign(claim,structuredClone(entry.after));
  const expectedLanes=TAX.has(id)?[STATIC]:id===WORKLOAD?[STATIC,CITE]:[CITE];
  const classification=TAX.has(id)?'REVIEWED_ADVICE':id===WORKLOAD?'REVIEWED_ADVICE_WITH_GOVERNING_RULE':'PUBLISHED_SOURCE_CLAUSE';
  req(claim.status==='PASS'&&claim.classification===classification&&equal(claim.required_evidence_types,expectedLanes),'invalid bounded classification/status/lanes');
  req(equal(claim.headings,prior.headings)&&claim.spans.length===1,'heading/span scope drift');
  const span=claim.spans[0],withoutHash=s=>Object.fromEntries(Object.entries(s).filter(([k])=>k!=='text_sha256'));
  req(equal(withoutHash(span),withoutHash(prior.spans[0])),'span location drift');const ref=span.source_file,content=current.get(ref)||read(ref),sourceLines=lines(content);
  const literal=sourceLines.slice(span.start-1,span.end).join('\n');req(claim.text===literal&&span.text_sha256===hash(literal),'claim literal/span drift');
  if(id===WORKLOAD)req(claim.text===prior.text&&equal(claim.spans,prior.spans),'Workload wording/citation must remain unchanged');
  const rv=review.reviews.find(r=>r.claim_id===id);
  req(rv&&rv.before_claim_sha256===entry.before_sha256&&rv.text===literal&&rv.text_sha256===hash(literal)&&rv.source_sha256===hash(content)&&content.toString().includes(rv.context)&&equal(rv.headings,claim.headings),'contextual review identity drift');
  req(entry.basis.length&&entry.review_rationale===rv.finding&&entry.limits===rv.limits,'missing contextual rationale/limits');
  const basisLanes=new Set();
  for(const basis of entry.basis){
   keys(basis,['artifact_id','lane','text_pointer','excerpt','source_locator','support_rationale']);const artifact=artifacts.get(basis.artifact_id);req(artifact,'missing source artifact');basisLanes.add(basis.lane);
   req(basis.excerpt&&pointer(artifact.capture,basis.text_pointer).includes(basis.excerpt)&&basis.support_rationale,'source excerpt absent');
   req(basis.lane===(artifact.kind==='CONTEXT_REVIEW'?STATIC:CITE),'invalid source basis lane');
   req(claim.evidence_refs.some(r=>r.artifact_ref===artifact.path),'missing basis evidence reference');
   if(basis.lane===CITE)req(claim.source_refs.some(r=>equal(r,{repository:'official-publication',revision:'sha256:'+artifact.sha256,path:artifact.origin.url,locator:basis.text_pointer,source_kind:CITE})),'missing exact independent source reference');
  }
  req(expectedLanes.every(l=>basisLanes.has(l)),'required review/source basis missing');
  req(prior.evidence_refs.every(r=>claim.evidence_refs.some(x=>equal(x,r)))&&prior.source_refs.every(r=>claim.source_refs.some(x=>equal(x,r))),'prior evidence/source dropped');
  claim.history={...prior.history,carry_decision:JURISDICTION_DECISION,reason:(prior.history.reason||'')+HISTORY_REASON};claim.coverage_state='CHANGED';
  const earlier=presentation.get(id);
  presentation.set(id,{previous:structuredClone(prior),method:TAX.has(id)?'CONTEXTUAL_ADVICE_REVIEW':id===WORKLOAD?'CONTEXTUAL_ADVICE_AND_AGREEMENT_RULE':'PUBLISHED_PROGRAM_SOURCE',reviewRationale:entry.review_rationale,remaining:entry.limits+' '+claim.next_action,registryRef:JURISDICTION_PATH,baselineRef:JURISDICTION_BASELINE,
   basis:entry.basis.map(b=>{const a=artifacts.get(b.artifact_id);return {...b,artifactRef:a.path,kind:a.kind,origin:a.origin,sourceLabel:a.source_label,sourceLocator:b.source_locator,sourceUrl:a.origin.url||null}}),
   auditHistory:earlier?[structuredClone(earlier)]:[],jurisdiction:{reviewRationale:entry.review_rationale,remaining:entry.limits}});
 }
 req(seen.size===8&&[...JURISDICTION_IDS].every(id=>seen.has(id)),'eight exact transitions required');
 for(const page of model.pages){
  const ref=page.source_file;if(!current.has(ref))continue;page.source_sha256=hash(current.get(ref));page.coverage_state='CHANGED';
  const crosses=span=>{for(let n=span.start;n<=span.end;n++)if(edited.get(ref).has(n))return true;return false};
  for(const claim of page.claims)if(!seen.has(claim.id))req(!claim.spans.some(crosses),'unrelated claim crosses source edit');
  for(const p of page.procedures)for(const node of [p,...p.nodes])if(node.spans.some(crosses)){node.spans=[];node.status='STALE';node.coverage_state='CHANGED';node.limits=[...(node.limits||[]),NODE_LIMIT];node.history={...node.history,carry_decision:JURISDICTION_DECISION+'_SOURCE_CHANGED'}}
 }
 for(const source of model.source.source_manifest)if(current.has(source.path))source.sha256=hash(current.get(source.path));
 req([...before].filter(([id,c])=>equal(c,after.get(id))).length===2005,'unrelated claim drift');
 model.counts.claim_statuses={};for(const c of after.values())model.counts.claim_statuses[c.status]=(model.counts.claim_statuses[c.status]||0)+1;
 model.generated_at=registry.generated_at;model.corrections.push(correction(registry.sources));
 const artifactHashes=new Map(predecessor.artifactHashes);
 for(const source of registry.sources){artifactHashes.set(source.path,source.after_sha256);artifactHashes.set(source.before_artifact.path,source.before_artifact.sha256)}
 artifactHashes.set(JURISDICTION_PATH,JURISDICTION_SHA256);artifactHashes.set(JURISDICTION_BASELINE,JURISDICTION_BASELINE_SHA256);
 for(const a of artifacts.values())artifactHashes.set(a.path,a.sha256);for(const item of registry.retained_raw_sources)artifactHashes.set(item.path,item.sha256);
 const matches=new Map([...predecessor.matches].map(([id,match])=>[id,{...match,claim:after.get(id),jurisdiction:registry.transitions.find(e=>e.claim_id===id)||null}]));
 return {...predecessor,model,presentation,matches,artifactHashes,jurisdiction:{registry,registrySha256:JURISDICTION_SHA256,baseline:JURISDICTION_BASELINE,baselineSha256:JURISDICTION_BASELINE_SHA256,artifacts}};
}

export function loadJurisdiction({read,model,exists}){
 const present=exists?exists(JURISDICTION_PATH):(()=>{try{read(JURISDICTION_PATH);return true}catch{return false}})();
 const marked=(model.corrections||[]).some(c=>c.id===JURISDICTION_MARKER);
 if(!present){req(!marked,'jurisdiction-marked model has no registry');return null}
 const projected=projectJurisdiction({read,exists});
 req(equal(model,projected.model),'whole model differs from jurisdiction projection at '+difference(model,projected.model));
 return projected;
}
