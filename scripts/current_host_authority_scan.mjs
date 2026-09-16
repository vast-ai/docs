/** Independent reader gate for the frozen, explicitly reviewed authority scan.
 * A matching digest establishes integrity. Evidence lanes and origins below
 * establish the permitted interpretation; neither a model nor this registry
 * is a terminal source of product truth.
 */
import crypto from 'node:crypto';
import {loadClarificationTransition} from './current_host_clarification.mjs';

export const AUTHORITY_SCAN_PATH = 'verification/current-host-authority-scan.json';
export const AUTHORITY_SCAN_ATTEMPT = 'verification/evidence/2026-09-09-host-authority-scan-attempt-01';
export const AUTHORITY_SCAN_BASELINE_PATH = `${AUTHORITY_SCAN_ATTEMPT}/before-current-host-docs-review.json`;
export const AUTHORITY_SCAN_SNAPSHOT_PATH = `${AUTHORITY_SCAN_ATTEMPT}/source-snapshot-01.json`;
export const AUTHORITY_SCAN_REGISTRY_SHA256 = 'a0034595ea679605497106d8a8670bc068559d52441691c4128d7558b50de8c2';
export const AUTHORITY_SCAN_BASELINE_SHA256 = '6dfb73d8d4a4f3f110b1e81adb443db0913dd0ac47a876e0a4519d57bce9ca18';
export const AUTHORITY_SCAN_SNAPSHOT_SHA256 = 'a090667e08bfc4bcf1a9a85c407965bac686107f4ec6fb75162d5b3a9d6a12d2';
export const AUTHORITY_SCAN_DECISION = 'CURRENT_HOST_AUTHORITY_SCAN_TRANSITION';
export const AUTHORITY_SCAN_RELOCATION = 'CURRENT_HOST_AUTHORITY_SCAN_RELOCATION';
export const AUTHORITY_SCAN_SOURCE_CHANGED = 'CURRENT_HOST_AUTHORITY_SCAN_SOURCE_CHANGED';
const TRANSITION_REASON = ' Exact current source/taxonomy transition is recorded in verification/current-host-authority-scan.json; full previous claim is retained in the frozen scan baseline.';
const RELOCATION_REASON = ' Exact unchanged source spans were relocated against the frozen scan source snapshot; no product evidence was added.';
const STALE_REASON = ' The previous source span changed in the authority scan; no procedure execution or acceptance transfers.';
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export const canonical = value => Array.isArray(value) ? value.map(canonical) : value && typeof value === 'object'
  ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value;
export const canonicalHash = value => hash(JSON.stringify(canonical(value)));
const equal = (a,b) => JSON.stringify(canonical(a)) === JSON.stringify(canonical(b));
const requireThat = (condition, reason) => { if (!condition) throw new Error(`authority scan: ${reason}`); };
const text = (value, label) => requireThat(typeof value === 'string' && value.trim().length > 0, `missing ${label}`);
const keys = (value, required, optional=[], label='object') => {
  requireThat(value && typeof value === 'object' && !Array.isArray(value), `invalid ${label}`);
  requireThat(required.every(key=>Object.hasOwn(value,key)) && Object.keys(value).every(key=>required.includes(key)||optional.includes(key)), `invalid ${label} fields`);
};
const safePath = value => {
  requireThat(typeof value === 'string' && /^[A-Za-z0-9._/-]+$/.test(value) && !value.startsWith('/') && !value.split('/').some(p=>!p||p==='.'||p==='..'), 'unsafe path');
  return value;
};
const lines = bytes => {const value=bytes.toString('utf8');const result=value.split(/\r\n|[\n\r\v\f\u001c-\u001e\u0085\u2028\u2029]/);if(/[\n\r\v\f\u001c-\u001e\u0085\u2028\u2029]$/.test(value))result.pop();return result;};
const isDerived = ref => ref.startsWith('verification/current-') || /(?:\.orchestra\/|before-current-|current-host-docs-review|host-docs-(?:test-(?:sets|results)|command-scores)|current-.*(?:adjudications|transition)|graphify|sources-before|source-snapshot)/.test(ref);
const allowedAfter = ['classification','status','required_evidence_types','owner_role','rationale','next_action'];
const optionalAfter = ['text','headings','spans','evidence_refs','source_refs'];
const methods = new Set(['TAXONOMY_ONLY','EDITORIAL','SOURCE_ADJUDICATION','NAVIGATION_RETEST','PROVENANCE_DOWNGRADE']);
const statuses = new Set(['PASS','FAIL','UNVALIDATED','BLOCKED','NOT_APPLICABLE','STALE']);
const allowedKinds = new Set(['CONTEXT','GOVERNING_SOURCE','CANONICAL_SOURCE','OBSERVATION','STATIC_RETEST']);
const lanes = new Set(['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','ACCOUNTABLE_OWNER_CONFIRMATION','AUTHORITATIVE_DOCUMENTATION_CITATION','REPOSITORY_STATIC_CHECK','PRODUCT_PUBLICATION_SOURCE']);
const kindLanes = {
  GOVERNING_SOURCE: new Set(['AUTHORITATIVE_DOCUMENTATION_CITATION','PRODUCT_PUBLICATION_SOURCE']),
  CANONICAL_SOURCE: new Set(['CANONICAL_IMPLEMENTATION_SOURCE']),
  OBSERVATION: new Set(['RUNTIME_OR_UI_OBSERVATION']),
  STATIC_RETEST: new Set(['REPOSITORY_STATIC_CHECK','APPROVED_NON_EXECUTABLE_CLASSIFICATION']),
  CONTEXT: new Set(),
};
function pointer(value, selector) {
  requireThat(typeof selector === 'string' && (selector === '' || selector.startsWith('/')), 'invalid JSON pointer');
  for (const token of selector.split('/').slice(1)) {
    const key = token.replace(/~1/g,'/').replace(/~0/g,'~');
    requireThat(value !== null && typeof value === 'object' && Object.hasOwn(value,key), 'unresolved evidence pointer');
    value = value[key];
  }
  return value;
}
function plainNavigation(textValue) {
  // Navigation promotion accepts neutral references; material predicates cannot
  // hide in a handoff or in prose surrounding an otherwise valid local URL.
  const stripped=textValue.replace(/(?<!!)\[[^\]]+\]\(\/[A-Za-z0-9_./#-]+\)/g,'LINK');
  return /^(?:\s*(?:[-*]|\d+\.)?\s*LINK[\s,.;]*)+$/.test(stripped) || /^\s*See LINK(?: and LINK)*\.\s*$/.test(stripped) || stripped==='For the offer and rental lifecycle, see LINK.';
}
function resolveNavigation(value, sourceFile, read) {
  requireThat(plainNavigation(value), 'navigation promotion contains a material predicate');
  const links=[...value.matchAll(/\]\((\/[^)]+)\)/g)].map(m=>m[1]);
  requireThat(links.length>0,'navigation proof has no local destination');
  for(const href of links){const [route,fragment]=href.split('#');let bytes=null;for(const candidate of route?[`${route.slice(1)}.mdx`,`${route.slice(1)}.md`,`${route.slice(1)}/index.mdx`]:[sourceFile]){try{bytes=read(safePath(candidate));break}catch{}}
    requireThat(bytes,'navigation destination missing');
    if(fragment){const source=bytes.toString('utf8');const slug=s=>s.replace(/<[^>]*>/g,'').toLowerCase().replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-');requireThat(source.includes(`id="${fragment}"`)||source.includes(`id='${fragment}'`)||source.split('\n').some(l=>/^#+ /.test(l)&&slug(l.replace(/^#+ /,''))===fragment),'navigation fragment missing');}
  }
}
function sourceSpan(span, sourceBytes) {
  keys(span,['source_file','start','end','text_sha256'],[],'source span');
  const source=sourceBytes.get(span.source_file);
  requireThat(source && Number.isInteger(span.start)&&Number.isInteger(span.end)&&span.start>0&&span.end>=span.start&&span.end<=lines(source).length,'invalid source span');
  const value=lines(source).slice(span.start-1,span.end).join('\n');
  requireThat(hash(value)===span.text_sha256,'source span hash drift');
  return value;
}
function sameSpanContents(before, after, oldSources, currentSources) {
  requireThat(before.length===after.length,'relocation drops source spans');
  before.forEach((span,index)=>{const target=after[index];requireThat(span.source_file===target.source_file&&sourceSpan(span,oldSources)===sourceSpan(target,currentSources),'relocation changes source text');});
}
// Independently implemented equal-block mapper. Earliest old occurrence wins
// ties, then earliest new occurrence, matching the producer's explicit rule.
function equalityMap(before, after) {
  const positions=new Map();after.forEach((line,j)=>{if(!positions.has(line))positions.set(line,[]);positions.get(line).push(j)});
  const queue=[[0,before.length,0,after.length]],blocks=[];
  while(queue.length){const [alo,ahi,blo,bhi]=queue.pop();let bestI=alo,bestJ=blo,bestSize=0,previous=new Map();
    for(let i=alo;i<ahi;i++){const current=new Map();for(const j of positions.get(before[i])||[]){if(j<blo)continue;if(j>=bhi)break;const size=(previous.get(j-1)||0)+1;current.set(j,size);if(size>bestSize){bestI=i-size+1;bestJ=j-size+1;bestSize=size}}previous=current;}
    if(bestSize){blocks.push([bestI,bestJ,bestSize]);if(alo<bestI&&blo<bestJ)queue.push([alo,bestI,blo,bestJ]);if(bestI+bestSize<ahi&&bestJ+bestSize<bhi)queue.push([bestI+bestSize,ahi,bestJ+bestSize,bhi]);}
  }
  const map=new Map();for(const [a,b,size]of blocks)for(let k=0;k<size;k++)map.set(a+k+1,b+k+1);return map;
}
function relocatedSpan(span,oldSources,currentSources,maps){sourceSpan(span,oldSources);const map=maps.get(span.source_file),target=[];for(let i=span.start;i<=span.end;i++)target.push(map.get(i));if(target.some((n,i)=>n===undefined||n!==target[0]+i))return null;const result={...span,start:target[0],end:target.at(-1)};sourceSpan(result,currentSources);return result;}
const changedHistory=(old,decision,reason)=>({...old.history,carry_decision:decision,...(Object.hasOwn(old.history||{},'reason')?{reason:old.history.reason+reason}:{})});
function displayBasis(binding, artifact, claim) {
  const origin=artifact.origin||null;
  const source=claim.source_refs.find(ref=>origin?.url?ref.path===origin.url:origin&&['repository','revision','path'].every(key=>ref[key]===origin[key]));
  const sourceLabel=origin?.repository?origin.path:origin?.url==='https://cloud.vast.ai/host/agreement'?'Hosting Agreement':origin?.url?.includes('stripe.com')?'Stripe documentation':origin?.url?.includes('paypal.com')?'PayPal US help':'Retained source';
  let section;try{if(binding.text_pointer&&binding.text_pointer!=='/source_text')section=pointer(JSON.parse(artifact.bytes),binding.text_pointer.replace(/\/text$/,''));}catch{}
  const lineRange=origin?.repository&&Number.isInteger(section?.start)&&Number.isInteger(section?.end)&&section.start>0&&section.end>=section.start?`lines ${section.start}–${section.end}`:null;
  const sourceLocator=lineRange||section?.heading||section?.locator||source?.locator||'Exact claim-bound static navigation retest';
  const sourceUrl=origin?.url||(origin?.repository?`https://github.com/${origin.repository}/blob/${origin.revision}/${origin.path.split('/').map(encodeURIComponent).join('/')}${lineRange?`#L${section.start}-L${section.end}`:''}`:null);
  return {...binding,artifactRef:artifact.path,kind:artifact.kind,origin,sourceLabel,sourceLocator,sourceUrl};
}

/** Tests can pin isolated fixture bytes explicitly; application callers use the
 * production wrapper below and cannot choose pins from untrusted file fields. */
export function validateAuthorityScanInput({read,model,pins}) {
  const artifactHashes=new Map();
  const pinnedRead=(ref,wanted)=>{safePath(ref);requireThat(/^[a-f0-9]{64}$/.test(wanted),'unsealed trusted digest');const bytes=read(ref);requireThat(hash(bytes)===wanted,`digest drift: ${ref}`);artifactHashes.set(ref,wanted);return bytes;};
  const registryBytes=pinnedRead(AUTHORITY_SCAN_PATH,pins.registry);
  const registry=JSON.parse(registryBytes);
  keys(registry,['schema_version','record_type','generated_at','baseline','source_snapshot','artifacts','source_transitions','transitions'],[],'registry');
  requireThat(registry.schema_version==='1.0'&&registry.record_type==='HOST_AUTHORITY_SCAN_TRANSITION','wrong registry type');
  text(registry.generated_at,'generation time');
  keys(registry.baseline,['path','sha256'],[],'baseline');keys(registry.source_snapshot,['path','sha256'],[],'source snapshot');
  requireThat(registry.baseline.path===AUTHORITY_SCAN_BASELINE_PATH&&registry.baseline.sha256===pins.baseline&&registry.source_snapshot.path===AUTHORITY_SCAN_SNAPSHOT_PATH&&registry.source_snapshot.sha256===pins.snapshot,'baseline substitution');
  const baseline=JSON.parse(pinnedRead(registry.baseline.path,pins.baseline));
  const snapshot=JSON.parse(pinnedRead(registry.source_snapshot.path,pins.snapshot));
  requireThat(baseline.record_type==='HOST_DOCS_CURRENT_REVIEW'&&baseline.pages.length===44&&baseline.pages.flatMap(p=>p.claims).length===2013&&baseline.support_layers.length===33,'baseline population drift');
  requireThat(snapshot.type==='SOURCE_UNDER_REVIEW_SNAPSHOT'&&Array.isArray(snapshot.records)&&snapshot.records.length===144,'invalid source snapshot');
  const oldSources=new Map(),currentSources=new Map();
  for(const item of snapshot.records){keys(item,['path','sha256','snapshot'],[],'snapshot record');requireThat(!oldSources.has(item.path)&&item.snapshot===`${AUTHORITY_SCAN_ATTEMPT}/sources-before/${safePath(item.path)}`,'source snapshot substitution');oldSources.set(item.path,pinnedRead(item.snapshot,item.sha256));currentSources.set(item.path,read(item.path));}
  const changes=new Map();for(const item of registry.source_transitions){keys(item,['path','before_sha256','after_sha256'],[],'source transition');requireThat(oldSources.has(item.path)&&!changes.has(item.path)&&hash(oldSources.get(item.path))===item.before_sha256&&hash(currentSources.get(item.path))===item.after_sha256&&item.before_sha256!==item.after_sha256,'invalid source transition');changes.set(item.path,item);}
  for(const [ref,bytes]of oldSources)requireThat((hash(bytes)!==hash(currentSources.get(ref)))===changes.has(ref),`unrecorded source change: ${ref}`);
  // The online reader rechecks this complete set on every request, including
  // destinations outside the currently displayed page.
  for(const [ref,bytes]of currentSources)artifactHashes.set(ref,hash(bytes));
  const baselineManifest=new Map(baseline.source.source_manifest.map(item=>[item.path,item.sha256]));
  requireThat(oldSources.size===baselineManifest.size&&[...oldSources].every(([ref,bytes])=>baselineManifest.get(ref)===hash(bytes)),'snapshot inventory drift');
  const maps=new Map([...oldSources].map(([ref,bytes])=>[ref,equalityMap(lines(bytes),lines(currentSources.get(ref)))]));
  const artifacts=new Map(),artifactPaths=new Set();for(const artifact of registry.artifacts){keys(artifact,['id','path','sha256','kind'],['origin'],'artifact');text(artifact.id,'artifact ID');requireThat(!artifacts.has(artifact.id)&&!artifactPaths.has(artifact.path)&&allowedKinds.has(artifact.kind),'invalid artifact identity/kind');artifactPaths.add(artifact.path);const bytes=pinnedRead(artifact.path,artifact.sha256);if(artifact.kind!=='CONTEXT'){
    requireThat(!isDerived(artifact.path)&&!/^host\//.test(artifact.path),'derived terminal product proof');
    if(artifact.kind==='GOVERNING_SOURCE'){keys(artifact.origin,['url'],[],'governing origin');const url=new URL(artifact.origin.url);requireThat(url.protocol==='https:'&&['vast.ai','cloud.vast.ai','docs.stripe.com','www.paypal.com'].includes(url.hostname)&&!url.username&&!url.password&&!(url.hostname.endsWith('vast.ai')&&/\/docs(?:\/|$)/.test(url.pathname)),'unverified governing source origin');requireThat(JSON.parse(bytes).url===artifact.origin.url,'capture origin mismatch');}
    if(artifact.kind==='CANONICAL_SOURCE')requireThat(artifact.origin&&/^vast-ai\/(?:vast-cli|self-test|kaalia|backend|host-installer-wizard)$/.test(artifact.origin.repository||'')&&/^[a-f0-9]{40}$/.test(artifact.origin.revision||'')&&/\.(?:py|js|mjs|ts|json|ya?ml|sh)$/.test(artifact.origin.path||''),'unpinned canonical implementation origin');
    if(artifact.kind==='OBSERVATION'){let o;try{o=JSON.parse(bytes)}catch{}requireThat(o&&['observations','records','requests','metadata','stdout','instance'].some(k=>Object.hasOwn(o,k)),'observation lacks retained result');}
  }artifacts.set(artifact.id,{...artifact,bytes});}
  const beforeById=new Map();for(const page of baseline.pages)for(const claim of page.claims){requireThat(!beforeById.has(claim.id),'duplicate baseline claim');beforeById.set(claim.id,{claim,page});}
  const entries=new Map();for(const entry of registry.transitions){keys(entry,['claim_id','before_claim_sha256','method','after','basis','review_rationale'],[],'transition');const prior=beforeById.get(entry.claim_id);requireThat(prior&&!entries.has(entry.claim_id)&&methods.has(entry.method)&&canonicalHash(prior.claim)===entry.before_claim_sha256,'claim predecessor drift');keys(entry.after,allowedAfter,optionalAfter,'after patch');requireThat(statuses.has(entry.after.status)&&Array.isArray(entry.after.required_evidence_types)&&entry.after.required_evidence_types.every(lane=>lanes.has(lane))&&new Set(entry.after.required_evidence_types).size===entry.after.required_evidence_types.length,'invalid status/evidence lanes');for(const k of ['classification','owner_role','rationale','next_action'])text(entry.after[k],k);text(entry.review_rationale,'review rationale');requireThat(Array.isArray(entry.basis),'missing source basis');
    const supported=new Set(),bindings=new Set();
    for(const basis of entry.basis){
      keys(basis,['artifact_id','lane','support_rationale'],['text_pointer','excerpt'],'basis');
      const artifact=artifacts.get(basis.artifact_id);requireThat(artifact,'unknown evidence origin');
      requireThat(!isDerived(artifact.path)&&artifact.kind!=='CONTEXT','self/model/graph proof injected');
      text(basis.support_rationale,'source support limit');
      const identity=JSON.stringify([basis.artifact_id,basis.lane,basis.text_pointer]);requireThat(!bindings.has(identity),'duplicate proof binding');bindings.add(identity);
      requireThat((entry.after.evidence_refs||prior.claim.evidence_refs).some(ref=>ref.artifact_ref===artifact.path),'source proof not bound to claim');
      requireThat(['REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE','AUTHORITATIVE_DOCUMENTATION_CITATION','PRODUCT_PUBLICATION_SOURCE'].includes(basis.lane),'new runtime/owner proof is outside scan scope');
      requireThat(kindLanes[artifact.kind].has(basis.lane),'source kind does not support evidence lane');
      if(basis.lane==='REPOSITORY_STATIC_CHECK'){
        requireThat(entry.method==='NAVIGATION_RETEST','static report is not product source proof');
        const proof=JSON.parse(artifact.bytes),matching=(proof.checks||[proof]).filter(check=>check.claim_id===entry.claim_id);
        requireThat(matching.length===1&&matching[0].result==='PASS'&&matching[0].text_sha256===hash(entry.after.text??prior.claim.text)&&matching[0].source_sha256===hash(currentSources.get(prior.page.source_file)),'navigation retest binding drift');
        resolveNavigation(entry.after.text??prior.claim.text,prior.page.source_file,read);
      }else{
        text(basis.excerpt,'retained exact source excerpt');
        let retained=artifact.bytes.toString('utf8');
        if(basis.text_pointer!==undefined){
          requireThat(/^\/(?:sections|excerpts)\/[0-9]+\/text$|^\/source_text$/.test(basis.text_pointer),'pointer must select source text, not metadata');
          try{const capture=JSON.parse(artifact.bytes);retained=pointer(capture,basis.text_pointer);
            if(basis.text_pointer==='/source_text')requireThat(capture.source_text_sha256===hash(retained),'source_text hash drift');
            else{const parent=pointer(capture,basis.text_pointer.replace(/\/text$/,''));if(Object.hasOwn(parent,'text_sha256'))requireThat(parent.text_sha256===hash(retained),'excerpt text hash drift');if(capture.source_text!==undefined)requireThat(typeof capture.source_text==='string'&&capture.source_text.includes(retained)&&capture.source_text_sha256===hash(capture.source_text),'excerpt not derived from retained source text');}
          }catch(error){throw new Error(`authority scan: evidence pointer drift (${error.message})`)}
        }
        requireThat(typeof retained==='string'&&retained.includes(basis.excerpt),'excerpt absent from named source');
        if(artifact.kind==='GOVERNING_SOURCE'){
          requireThat(basis.text_pointer!==undefined,'governing proof needs exact captured-text pointer');
          {const capture=JSON.parse(artifact.bytes);if(capture.source_text!==undefined){const raw=[...artifacts.values()].find(item=>item.path===capture.raw_artifact_ref);requireThat(raw&&raw.path!==artifact.path&&raw.sha256===capture.raw_artifact_sha256&&!isDerived(raw.path),'extracted source lacks separately pinned raw body');text(capture.extraction_method,'source extraction method');}}
          requireThat((entry.after.source_refs||prior.claim.source_refs).some(ref=>ref.path===artifact.origin.url),'governing source origin not cited');
        }else{
          keys(artifact.origin,['repository','revision','path'],[],'canonical origin');
          if(artifact.path.endsWith('.json')){const capture=JSON.parse(artifact.bytes);requireThat(basis.text_pointer!==undefined&&['repository','revision','path'].every(key=>capture[key]===artifact.origin[key]),'canonical capture origin or pointer mismatch');}
          requireThat((entry.after.source_refs||prior.claim.source_refs).some(ref=>['repository','revision','path'].every(key=>ref[key]===artifact.origin[key])),'canonical source origin not cited');
        }
      }
      supported.add(basis.lane);
    }
    if(['TAXONOMY_ONLY','PROVENANCE_DOWNGRADE'].includes(entry.method))requireThat(entry.after.status!=='PASS'&&entry.after.status!=='NOT_APPLICABLE','classification cannot manufacture proof');
    if(entry.method==='PROVENANCE_DOWNGRADE')requireThat(prior.claim.status==='PASS'&&entry.after.status==='UNVALIDATED','invalid proof downgrade');
    if(entry.after.status==='PASS'){
      requireThat(['SOURCE_ADJUDICATION','NAVIGATION_RETEST'].includes(entry.method),'PASS needs source-suitable retest');
      requireThat(entry.after.required_evidence_types.length>0&&entry.after.required_evidence_types.every(lane=>supported.has(lane)),'PASS has unsupported evidence lane');
      if(entry.method==='NAVIGATION_RETEST'){requireThat(equal(entry.after.required_evidence_types,['REPOSITORY_STATIC_CHECK']),'navigation exceeds static lane');resolveNavigation(entry.after.text??prior.claim.text,prior.page.source_file,read);}
    }
    if(entry.after.status==='NOT_APPLICABLE'||entry.method==='EDITORIAL')requireThat(entry.after.status==='NOT_APPLICABLE'&&entry.method==='EDITORIAL'&&entry.after.required_evidence_types.length===0&&entry.basis.length===0,'N/A needs explicit editorial disposition');
    entries.set(entry.claim_id,entry);
  }
  for(const id of ['VOL-C06','VOL-C08','VOL-C10','VOL-C14','VOL-C16','VOL-C20','VOL-C21']){const entry=entries.get(id);requireThat(entry?.method==='PROVENANCE_DOWNGRADE'&&entry.after.status==='UNVALIDATED'&&entry.after.required_evidence_types.includes('CANONICAL_IMPLEMENTATION_SOURCE')&&entry.after.evidence_refs?.length&&entry.after.evidence_refs.every(e=>e.role.includes('PARTIAL')),'known broad scope overclaim not corrected');for(const prior of beforeById.get(id).claim.evidence_refs)requireThat(entry.after.evidence_refs.some(ref=>Object.keys(prior).filter(key=>!['role','limit'].includes(key)).every(key=>equal(ref[key],prior[key]))),'original narrow proof identity removed');}
  const expectedModel=structuredClone(baseline);
  requireThat(model.pages.length===44&&model.support_layers.length===33&&equal(model.support_layers,baseline.support_layers),'current population/support drift');
  const modelIds=new Set(),matches=new Map(),presentation=new Map();
  for(const page of model.pages){const oldPage=baseline.pages.find(p=>p.route===page.route);requireThat(oldPage&&page.source_file===oldPage.source_file&&page.title===oldPage.title&&page.claims.length===oldPage.claims.length,'current page drift');requireThat(hash(read(page.source_file))===page.source_sha256,'current page hash mismatch');
    for(const claim of page.claims){const old=beforeById.get(claim.id),entry=entries.get(claim.id);requireThat(old&&old.page.route===page.route&&!modelIds.has(claim.id),'current claim ID drift');modelIds.add(claim.id);let expected=structuredClone(old.claim);const pageChanged=changes.has(page.source_file)||page.dependencies.some(d=>changes.has(d.source_file));
      const relocation=old.claim.spans.map(span=>relocatedSpan(span,oldSources,currentSources,maps));
      if(entry){Object.assign(expected,structuredClone(entry.after));expected.history=changedHistory(old.claim,AUTHORITY_SCAN_DECISION,TRANSITION_REASON);expected.coverage_state=pageChanged?'CHANGED':old.page.coverage_state;if(!Object.hasOwn(entry.after,'spans')){requireThat(!relocation.includes(null),'changed occurrence needs explicit source spans');expected.spans=relocation;}}
      else {requireThat(!relocation.includes(null),'unreviewed changed source occurrence');expected.spans=relocation;if(pageChanged||!equal(relocation,old.claim.spans)){expected.coverage_state='CHANGED';expected.history=changedHistory(old.claim,AUTHORITY_SCAN_RELOCATION,RELOCATION_REASON);}}
      // A changed transition that does not replace text must preserve each exact
      // old source segment, while allowing its occurrence to move in the page.
      if(entry&&Object.hasOwn(entry.after,'spans')&&expected.text===old.claim.text)sameSpanContents(old.claim.spans,expected.spans,oldSources,currentSources);
      requireThat(equal(claim,expected),`unreviewed current claim fields: ${claim.id}`);
      claim.spans.forEach(s=>sourceSpan(s,currentSources));
      const literal=claim.spans.map(s=>sourceSpan(s,currentSources)).join('\n');if(claim.text!==old.claim.text)requireThat(claim.text===literal,`claim/literal mismatch: ${claim.id}`);
      for(const ref of claim.evidence_refs){keys(ref,['id','role','limit','artifact_ref'],[],'claim evidence');requireThat(artifactPaths.has(ref.artifact_ref)&&ref.artifact_ref!==AUTHORITY_SCAN_PATH&&!/current-host-docs-review\.json$/.test(ref.artifact_ref),'unbound or self-model claim evidence');}
      const expectedPage=expectedModel.pages.find(p=>p.route===page.route);expectedPage.claims[expectedPage.claims.findIndex(c=>c.id===claim.id)]=expected;
      matches.set(claim.id,{claim,page,previous:old.claim,entry:entry||null,pageChanged});
      if(entry)presentation.set(claim.id,{method:entry.method,previous:old.claim,reviewRationale:entry.review_rationale,remaining:claim.next_action,basis:entry.basis.map(b=>displayBasis(b,artifacts.get(b.artifact_id),claim)),registryRef:AUTHORITY_SCAN_PATH,baselineRef:AUTHORITY_SCAN_BASELINE_PATH});
    }
  }
  requireThat(modelIds.size===2013&&matches.size===beforeById.size,'current claim completeness drift');
  const covered=new Map([...currentSources.keys()].map(ref=>[ref,new Set()]));for(const {claim}of matches.values())for(const span of claim.spans)for(let line=span.start;line<=span.end;line++)covered.get(span.source_file).add(line);
  for(const [ref]of changes){const unchanged=new Set(maps.get(ref).values());lines(currentSources.get(ref)).forEach((line,index)=>requireThat(!line.trim()||unchanged.has(index+1)||covered.get(ref).has(index+1),'new nonblank source line lacks a claim occurrence'));}
  requireThat(matches.get('MCL-17c8031cb2c7e34a')?.claim.status!=='PASS'||!matches.get('MCL-17c8031cb2c7e34a').claim.text.includes('why terms lock'),'material lock predicate passing as navigation');
  for(const page of expectedModel.pages){const pageChanged=changes.has(page.source_file)||page.dependencies.some(d=>changes.has(d.source_file));page.source_sha256=hash(currentSources.get(page.source_file));if(pageChanged)page.coverage_state='CHANGED';for(const dep of page.dependencies)dep.source_sha256=hash(currentSources.get(dep.source_file));if(pageChanged)for(const procedure of page.procedures)for(const node of [procedure,...procedure.nodes]){const relocated=node.spans.map(span=>relocatedSpan(span,oldSources,currentSources,maps));if(relocated.includes(null)){node.spans=[];node.status='STALE';node.coverage_state='CHANGED';node.limits.push(STALE_REASON.trim());node.history=changedHistory(node,AUTHORITY_SCAN_SOURCE_CHANGED,STALE_REASON);}else{node.spans=relocated;node.coverage_state='CHANGED';node.history=changedHistory(node,AUTHORITY_SCAN_RELOCATION,RELOCATION_REASON);}}}
  for(const support of baseline.support_layers){for(const field of ['source_file','fragment_file','central_reference_file'])requireThat(!changes.has(support[field]),'unreviewed support source change');for(const ref of support.evidence_refs)requireThat(artifactHashes.has(ref.artifact_ref),'unbound support artifact');}
  for(const item of model.source.source_manifest)requireThat(currentSources.has(item.path)&&hash(currentSources.get(item.path))===item.sha256,'current manifest drift');
  requireThat(model.source.source_manifest.length===baseline.source.source_manifest.length,'source manifest population drift');
  const expectedStatuses={};for(const {claim}of matches.values())expectedStatuses[claim.status]=(expectedStatuses[claim.status]||0)+1;
  requireThat(equal(model.counts.claim_statuses,expectedStatuses)&&model.counts.claims===2013&&model.counts.primary_pages===44,'current counts drift');
  for(const item of expectedModel.source.source_manifest)item.sha256=hash(currentSources.get(item.path));
  expectedModel.counts.claim_statuses=expectedStatuses;expectedModel.counts.page_coverage_states={};for(const page of expectedModel.pages)expectedModel.counts.page_coverage_states[page.coverage_state]=(expectedModel.counts.page_coverage_states[page.coverage_state]||0)+1;
  expectedModel.generated_at=registry.generated_at;
  expectedModel.history.authority_scan={registry:AUTHORITY_SCAN_PATH,registry_sha256:pins.registry,baseline:registry.baseline,source_snapshot:registry.source_snapshot,limit:'Integrity and transition provenance only; not terminal product proof.'};
  expectedModel.corrections.push({id:'HOST-AUTHORITY-SOURCE-FIRST-SCAN-01',scope:'44 primary Host pages; all2013 claim IDs retained',history:'Frozen full before model and all144 source snapshots remain immutable.',current:`${entries.size} exact reviewed transitions; no taxonomy-only PASS.`,reason:'Existing independent source authority precedes any genuine decision escalation; narrow retained proof does not validate broader claims.'});
  requireThat(equal(model,expectedModel),'whole model differs from independent transition projection');
  return {registry,baseline,entries,matches,presentation,artifactHashes,artifacts,oldSources,currentSources,changes,registrySha256:hash(registryBytes)};
}
export function mergeClarificationScan(authority, clarification) {
  const matches=new Map([...authority.matches].map(([id,match])=>[id,{...match,
    claim:clarification.matches.get(id)?.claim||match.claim,
    clarification:clarification.entries.get(id)||null}]));
  const presentation=new Map(authority.presentation);
  for(const [id,detail] of clarification.presentation){
    const prior=presentation.get(id);
    // Existing authority basis remains the source-display authority.  The
    // clarification has no new terminal source and is displayed as context.
    presentation.set(id,prior?{...prior,clarification:detail}:{...detail,clarification:detail});
  }
  return {...authority,matches,presentation,
    artifactHashes:new Map([...authority.artifactHashes,...clarification.contextHashes]),clarification};
}
export function loadAuthorityScan({read,model,exists}) {
  const present=exists?exists(AUTHORITY_SCAN_PATH):(()=>{try{read(AUTHORITY_SCAN_PATH);return true}catch{return false}})();
  const pins={registry:AUTHORITY_SCAN_REGISTRY_SHA256,baseline:AUTHORITY_SCAN_BASELINE_SHA256,snapshot:AUTHORITY_SCAN_SNAPSHOT_SHA256};
  const clarification=loadClarificationTransition({read,model,exists,validatePredecessor: predecessor=>{
    requireThat(present,'clarification predecessor has no authority registry');
    return validateAuthorityScanInput({read,model:predecessor,pins});
  }});
  if(clarification)return mergeClarificationScan(clarification.authorityScan,clarification);
  const marked=model.pages.some(page=>page.claims.some(claim=>[AUTHORITY_SCAN_DECISION,AUTHORITY_SCAN_RELOCATION].includes(claim.history?.carry_decision)));
  if(!present){requireThat(!marked,'missing registry for transitioned model');return null;}
  return validateAuthorityScanInput({read,model,pins});
}
