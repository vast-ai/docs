/** Retain bounded verification of the offline report, not Host behavior. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {sanitize} from './export_host_review_html.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const destination=process.argv[2];
if(!destination||!/^verification\/evidence\/(?:2026-09-08-host-(?:html-export|live-readonly|client-unblocking)-attempt-01\/checks-\d+|2026-09-09-host-(?:authority-scan|review-plain-language)-attempt-01\/checks-\d{2}|2026-09-10-host-(?:policy-acknowledgement|clarification-sweep|terms-binding|split-review)-attempt-01\/checks-\d{2}|2026-09-11-host-(?:jurisdiction-authority|review-cleanup)-attempt-01\/checks-\d{2})\.json$/.test(destination))throw new Error('Provide a new checks-NN.json in an allowlisted retained HTML/evidence attempt');
if(fs.existsSync(path.join(root,destination)))throw new Error('Refuse to overwrite retained check');
const session=`host-authority-html-${path.basename(destination,'.json')}-${crypto.randomUUID().slice(0,8)}`;
const capturePrefix=path.basename(destination,'.json');
const captureDir=path.dirname(destination);
for(const view of ['desktop','mobile'])if(fs.existsSync(path.join(root,`${captureDir}/${capturePrefix}-${view}.png`)))throw new Error('Refuse to overwrite retained screenshot');
const currentModel=JSON.parse(fs.readFileSync(path.join(root,'verification/current-host-docs-review.json'),'utf8'));
const currentClaims=currentModel.pages.flatMap(p=>p.claims),openClaims=currentClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status));
const expectedCounts={...currentModel.counts.claim_statuses,OPEN:openClaims.length,ALL:currentClaims.length};
const runtimeCount=openClaims.filter(c=>c.required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION')).length;
const result={timestamp:new Date().toISOString(),scope:'Standalone HTML presentation and setup-source inspection; no product behavior or fresh network installation',html_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'verification/host-docs-review.html'))).digest('hex'),checks:[]};
function run(args){return JSON.parse(execFileSync('agent-browser',['--session',session,'--json',...args],{encoding:'utf8',maxBuffer:5000000,timeout:45000}));}
function evaluate(script){const response=run(['eval','-b',Buffer.from(`(()=>{${script}})()`).toString('base64')]);if(!response.success)throw new Error(JSON.stringify(response.error));return response.data.result;}
function check(name,fn){try{result.checks.push({name,status:'PASS',observation:fn()});}catch(e){result.checks.push({name,status:'FAIL',error:sanitize(e.message)});}}
check('deterministic data and setup-source tests',()=>sanitize(execFileSync(process.execPath,['--test','scripts/host-review-html.test.mjs'],{cwd:root,encoding:'utf8',maxBuffer:1000000}).trim()));
try {
run(['open',pathToFileURL(path.join(root,'verification/host-docs-review.html')).href]);
run(['set','offline','on']);
check('plain-language account finding, next step and exact raw details',()=>evaluate(`
 document.getElementById('search').value='MCL-790d76c6e2bea8fa';document.getElementById('search').dispatchEvent(new Event('input'));
 const card=document.querySelector('.claim'),data=JSON.parse(document.getElementById('report-data').textContent),claim=data.claims.find(c=>c.id==='MCL-790d76c6e2bea8fa');
 if(!card.innerText.includes(claim.reader_copy.finding)||!card.innerText.includes(claim.reader_copy.nextStep))throw Error('Plain copy missing');
 if(/permission enforcement|state transition|terminal proof|Remaining gap/.test(card.innerText))throw Error('Audit jargon visible');
 const raw=card.querySelector('.raw-details');if(raw.open||!raw.textContent.includes(claim.rationale)||!raw.textContent.includes(claim.next_action))throw Error('Raw details lost or expanded');
 document.getElementById('clear').click();return {id:claim.id,status:claim.status,finding:claim.reader_copy.finding,next:claim.reader_copy.nextStep};`));
check('policy requests preserve open citations and basic descriptions need no rental',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent),seen=[];
 const selectedIds=new Set(['MCL-b61d15c0282ef567','MCL-c59caa4cd52bcc1f','MCL-af1c482a08b09316','MCL-393941d0e9be9d31','MCL-03c73e4182b1e7fe','MCL-3b10b5e64ee55003','MCL-e12ac9f6be2ce502']);
 const selected=data.claims.filter(c=>selectedIds.has(c.id));
 for(const claim of selected){
  document.getElementById('clear').click();document.getElementById('status').value='ALL';
  document.getElementById('search').value=claim.id;document.getElementById('search').dispatchEvent(new Event('input'));
  const card=document.querySelector('.claim'),copy=claim.reader_copy;
  if(!card.innerText.includes(copy.finding)||!card.innerText.includes(copy.nextStep))throw Error('Wrong request '+claim.id);
  if(copy.statusLabel&&!card.innerText.includes(copy.statusLabel))throw Error('Wrong label '+claim.id);
  if(copy.pendingNote&&!card.querySelector('.policy-pending')?.innerText.includes(copy.pendingNote))throw Error('Lost pending citation '+claim.id);
  if(!card.querySelector('.raw-details').textContent.includes('Recorded status: '+claim.status)||card.querySelector('.raw-details').open)throw Error('Lost raw status '+claim.id);
  seen.push({id:claim.id,status:claim.status,label:copy.statusLabel||'Supported within scope',finding:copy.finding});
 }
 if(selected.length!==selectedIds.size||selected.some(c=>!selectedIds.has(c.id))||selected.filter(c=>c.reader_copy.reviewKind==='policy-acknowledgement').length!==5)throw Error('Wrong scope');
 document.getElementById('clear').click();return seen;`));
check('offline initial load and no resource dependencies',()=>evaluate(`
 if(document.getElementById('results-count').textContent!=='${openClaims.length.toLocaleString()} matching passages · ${Math.min(20,openClaims.length).toLocaleString()} on this view')throw Error('Initial count');
 if(performance.getEntriesByType('resource').length)throw Error('Network resources');
 return {initial:document.getElementById('results-count').textContent,resources:0,location:location.protocol};`));
check('all current pages and claims reachable by page filter and pagination',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent),seen=[];
 document.getElementById('status').value='ALL';
 for(const p of data.pages){document.getElementById('page').value=p.route;document.getElementById('page').dispatchEvent(new Event('change'));
 do{seen.push(...[...document.querySelectorAll('.claim')].map(el=>el.id.slice(6)));if(document.getElementById('next').disabled)break;document.getElementById('next').click();}while(true);}
 if(new Set(seen).size!==data.claims.length||seen.length!==data.claims.length)throw Error('Missing or duplicated claims');
 document.getElementById('clear').click();return {pages:data.pages.length,uniqueClaims:new Set(seen).size};`));
check('all status totals and both evidence registers',()=>evaluate(`
 const expected=${JSON.stringify(expectedCounts)},counts={};
 for(const [status,n]of Object.entries(expected)){document.getElementById('status').value=status;document.getElementById('status').dispatchEvent(new Event('change'));const text=document.getElementById('results-count').textContent;if(!text.startsWith(n.toLocaleString()+' matching'))throw Error(status);counts[status]=n;}
 document.querySelector('[data-workstream="runtime"]').click();if(!document.getElementById('results-count').textContent.startsWith('${runtimeCount.toLocaleString()} matching'))throw Error('Runtime register');
 document.querySelector('[data-workstream="source"]').click();const sourceCount=document.getElementById('results-count').textContent;
 document.getElementById('clear').click();return {statuses:counts,runtime:${runtimeCount},source:sourceCount};`));
check('actionable categories partition every passage and shared wording retains individual controls',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent),queue=data.work_queue,seen=[];
 if(queue.total!==data.claims.length||queue.buckets.reduce((sum,b)=>sum+b.count,0)!==data.claims.length)throw Error('Queue partition');
 document.getElementById('status').value='ALL';
 for(const bucket of queue.buckets){const input=document.getElementById('work-category');input.value=bucket.id;input.dispatchEvent(new Event('change'));const ids=[];
  do{ids.push(...[...document.querySelectorAll('article.claim[id]')].map(el=>el.id.slice(6)));if(document.getElementById('next').disabled)break;document.getElementById('next').click();}while(true);
  const expected=data.claims.filter(c=>c.review_work.bucket===bucket.id).map(c=>c.id);
  if(ids.length!==bucket.count||JSON.stringify(ids)!==JSON.stringify(expected))throw Error('Category lost passages '+bucket.id);seen.push(...ids);}
 if(seen.length!==data.claims.length||new Set(seen).size!==seen.length)throw Error('Category overlap');
 document.getElementById('work-category').value='';document.getElementById('queue-view').value='shared';document.getElementById('queue-view').dispatchEvent(new Event('change'));const grouped=[];
 do{document.querySelectorAll('.shared-wording').forEach(el=>el.open=true);for(const card of document.querySelectorAll('article.claim[id]')){if(!card.querySelector('[data-passage]')||!card.querySelector('details'))throw Error('Lost individual controls');grouped.push(card.id.slice(6));}if(document.getElementById('next').disabled)break;document.getElementById('next').click();}while(true);
 if(grouped.length!==data.claims.length||new Set(grouped).size!==data.claims.length)throw Error('Grouped queue lost passages');
 document.getElementById('clear').click();return {passages:seen.length,groups:queue.sharedWordingGroups,groupedPassages:grouped.length};`));
check('search, empty state, priority action and owner selection',()=>evaluate(`
 const s=document.getElementById('search');s.value='support-bundle';s.dispatchEvent(new Event('input'));const search=document.getElementById('results-count').textContent;if(!document.querySelector('.claim'))throw Error('Search empty');
 s.value='no_such_claim_7d8f';s.dispatchEvent(new Event('input'));if(!document.querySelector('.empty'))throw Error('Empty state');
 document.querySelector('[data-page="/host/guide-to-taxes"]').click();if(document.getElementById('page').value!=='/host/guide-to-taxes')throw Error('Priority target');
 const role=document.getElementById('owner');role.value='Product, Finance, and Legal owner';role.dispatchEvent(new Event('change'));
 document.getElementById('clear').click();return {search,emptyState:true,priorityPage:true,ownerFilter:true};`));
check('self-test, VM and verification passage locations; evidence dialogs preserve context',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent);const observations=[];
 for(const route of ['/host/how-to-self-test','/host/vms','/host/verification-stages']){
  document.getElementById('status').value='ALL';document.getElementById('page').value=route;document.getElementById('page').dispatchEvent(new Event('change'));
  const first=document.querySelector('.claim'),id=first.id.slice(6),c=data.claims.find(c=>c.id===id);first.querySelector('[data-passage]').click();
  if(!document.getElementById('viewer').open||!document.querySelector('.source-line.highlight')||!document.getElementById('viewer-title').textContent.includes(c.page_title))throw Error('Passage context '+route);
  observations.push({route,id,highlightedLines:document.querySelectorAll('.source-line.highlight').length});document.getElementById('close-viewer').click();
 }
 const visible=(c,e)=>!bookkeepingEvidence(e)&&!data.authority_scan?.transitions[c.id]?.basis.some(b=>b.artifactRef===e.artifact_ref);
 const refs=[...new Set(data.claims.flatMap(c=>c.evidence_refs.filter(e=>visible(c,e)).map(e=>e.artifact_ref)))];
 for(const ref of refs){const c=data.claims.find(c=>c.evidence_refs.some(e=>e.artifact_ref===ref&&visible(c,e)));document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=c.id;document.getElementById('search').dispatchEvent(new Event('input'));document.querySelector('.claim>details').open=true;const button=[...document.querySelectorAll('.claim [data-artifact]')].find(b=>b.dataset.artifact===ref);if(!button)throw Error('Missing direct evidence control '+ref);button.click();
  const body=document.getElementById('viewer-body').textContent;if(!body.includes(c.page_title)||!body.includes('Limit:')||!body.includes(data.files[ref].sha256))throw Error('Evidence context '+ref);document.getElementById('close-viewer').click();}
 document.getElementById('clear').click();return {passages:observations,contextualEvidenceRecords:refs.length};`));
check('selected proof opens only its exact check with passage context and product sources stay separate',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent),groups=[data.supplemental_live_checks.mapped_claims,data.current_readonly_checks.mapped_claims,data.readonly_command_proofs||[]];let checks=0;
 for(const mapped of groups)for(const m of mapped){document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=m.claim_id;document.getElementById('search').dispatchEvent(new Event('input'));
 const card=document.querySelector('.claim');if(!card)throw Error('Missing mapped claim '+m.claim_id);card.querySelector(':scope>details').open=true;
 if(!card.textContent.includes('What we actually tested:')||!card.textContent.includes(m.coverage.level))throw Error('Coverage label');
 for(const target of m.checks){const b=[...card.querySelectorAll('[data-check]')].find(b=>b.dataset.check===target.id);if(!b)throw Error('Missing check control');b.click();
 const body=document.getElementById('viewer-body');const selected=JSON.parse(body.querySelector('pre').textContent);
 if(selected.check_id!==target.id||!body.textContent.includes(m.page_title)||!body.textContent.includes('Limit:')||!body.textContent.includes(data.files[target.artifact_ref].sha256)||!body.textContent.includes('Back to the page passage'))throw Error('Wrong proof/context '+target.id);
 document.getElementById('close-viewer').click();checks++;}}
 document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value='MCL-e12ac9f6be2ce502';document.getElementById('search').dispatchEvent(new Event('input'));
 const product=document.querySelector('.claim');product.querySelector(':scope>details').open=true;
 const hrefs=[...product.querySelectorAll('a[href]')].map(a=>a.href);
 for(const u of ['https://vast.ai/hosting','https://vast.ai/products/gpu-cloud','https://vast.ai/article/vast-ai-startup-program'])if(!hrefs.includes(u))throw Error('Missing product source link');
 if(!product.textContent.includes('not a runtime test'))throw Error('Product/runtime distinction');
 document.getElementById('clear').click();return {mappedClaims:groups.reduce((n,m)=>n+m.length,0),exactCheckControls:checks,publicSources:3};`));
check('authority scan source controls select each exact excerpt and foreground the human source locator',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent);if(!data.authority_scan)return {scope:'No authority scan in this dated input',controls:0};
 let count=0,sameSourcePairs=0;
 for(const [id,transition]of Object.entries(data.authority_scan.transitions)){
  if(!transition.basis.length)continue;document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=id;document.getElementById('search').dispatchEvent(new Event('input'));
  const card=document.getElementById('claim-'+id);if(!card)throw Error('Missing current source claim '+id);
  for(const [index,basis]of transition.basis.entries()){
   const button=[...card.querySelectorAll('[data-basis]')].find(button=>button.dataset.basis===String(index));if(!button)throw Error('Missing exact source control '+id+'/'+index);button.click();
   const body=document.getElementById('viewer-body'),content=body.textContent;
   if(!basis.sourceLabel||!basis.sourceLocator||!content.includes(basis.sourceLabel)||!content.includes(basis.sourceLocator)||!content.includes(basis.support_rationale)||!content.includes(transition.remaining)||/Original finding|transition history|Open frozen/.test(content))throw Error('Missing human source/scope/context '+id+'/'+index);
   if(basis.excerpt&&!content.includes(basis.excerpt))throw Error('Wrong selected source excerpt '+id+'/'+index);
   if(basis.sourceUrl&&![...body.querySelectorAll('a[href]')].some(link=>link.href===basis.sourceUrl))throw Error('Missing canonical origin link '+id+'/'+index);
   if(![...body.querySelectorAll('details')].some(detail=>detail.textContent.includes(data.files[basis.artifactRef].sha256)))throw Error('Audit fingerprint not expandable');
   if(transition.basis.slice(0,index).some(prior=>prior.artifactRef===basis.artifactRef))sameSourcePairs++;count++;document.getElementById('close-viewer').click();
  }
 }
 document.getElementById('clear').click();if(!count)throw Error('Active scan has no source controls');return {controls:count,sameSourceDistinctBindings:sameSourcePairs,scope:'Presentation and exact bindings only; no product runtime was executed.'};`));
check('print selection renders all filtered claims and restores pagination',()=>evaluate(`
 document.getElementById('search').value='support-bundle';document.getElementById('search').dispatchEvent(new Event('input'));const count=parseInt(document.getElementById('results-count').textContent.replaceAll(',',''));
 window.dispatchEvent(new Event('beforeprint'));if(document.querySelectorAll('.claim').length!==count)throw Error('Print truncation');window.dispatchEvent(new Event('afterprint'));if(document.querySelectorAll('.claim').length>20)throw Error('Pagination not restored');document.getElementById('clear').click();return {printSelectionCount:count,restored:true,limit:'Print preparation inspected; no OS print dialog or PDF pagination certification.'};`));
check('desktop layout, named controls and safe links',()=>{run(['set','viewport','1440','1000']);return evaluate(`
 if(document.documentElement.scrollWidth>innerWidth)throw Error('Horizontal overflow');
 const unnamed=[...document.querySelectorAll('button,input,select')].filter(e=>!e.textContent.trim()&&!e.getAttribute('aria-label')&&!document.querySelector('label[for="'+e.id+'"]'));
 if(unnamed.length)throw Error('Unnamed controls');const invalid=[...document.querySelectorAll('a[href]')].filter(a=>!/^https?:|^#/.test(a.getAttribute('href')));if(invalid.length)throw Error('Unsafe links');
 return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,unnamedControls:unnamed.length,unsafeLinks:invalid.length};`);});
run(['eval','window.scrollTo(0,0)']);run(['screenshot',path.join(root,`${captureDir}/${capturePrefix}-desktop.png`)]);
check('mobile 390px layout and exact-passage dialog',()=>{run(['set','viewport','390','844']);return evaluate(`
 if(document.documentElement.scrollWidth>innerWidth)throw Error('Mobile overflow');document.querySelector('.claim [data-passage]').click();const rect=document.getElementById('viewer').getBoundingClientRect();if(rect.right>innerWidth||rect.left<0)throw Error('Dialog overflow');document.getElementById('close-viewer').click();window.scrollTo(0,0);return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,dialogWidth:rect.width};`);});
run(['screenshot',path.join(root,`${captureDir}/${capturePrefix}-mobile.png`)]);
check('page errors and offline resource check after interaction',()=>{
 const errors=run(['errors']),resources=evaluate('return performance.getEntriesByType("resource").map(r=>r.name);');
 if(!errors.success||errors.data.errors.length||resources.length)throw new Error(JSON.stringify({errors,resources}));
 return {errors,resources};
});
} catch(error) {
 result.checks.push({name:'browser session execution',status:'FAIL',error:sanitize(error.message)});
} finally {
 check('isolated browser session closes',()=>{const response=run(['close']);if(!response.success)throw Error(JSON.stringify(response.error));return {session,closed:true};});
}
result.status=result.checks.every(c=>c.status==='PASS')?'PASS':'FAIL';
fs.writeFileSync(path.join(root,destination),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:result.status,checks:result.checks.map(c=>({name:c.name,status:c.status,error:c.error})),evidence:destination},null,2));
if(result.status!=='PASS')process.exitCode=1;
