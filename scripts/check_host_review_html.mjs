/** Retain bounded verification of the offline report, not Host behavior. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {sanitize} from './export_host_review_html.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const destination=process.argv[2];
if(!destination||!/^verification\/evidence\/2026-09-08-host-(?:html-export|live-readonly|client-unblocking)-attempt-01\/checks-\d+\.json$/.test(destination))throw new Error('Provide a new checks-NN.json in an allowlisted retained HTML/evidence attempt');
if(fs.existsSync(path.join(root,destination)))throw new Error('Refuse to overwrite retained check');
const session='host-html-export';
const capturePrefix=path.basename(destination,'.json');
const captureDir=path.dirname(destination);
const currentModel=JSON.parse(fs.readFileSync(path.join(root,'verification/current-host-docs-review.json'),'utf8'));
const currentClaims=currentModel.pages.flatMap(p=>p.claims),openClaims=currentClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status));
const expectedCounts={...currentModel.counts.claim_statuses,OPEN:openClaims.length,ALL:currentClaims.length};
const runtimeCount=openClaims.filter(c=>c.required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION')).length;
const result={timestamp:new Date().toISOString(),scope:'Standalone HTML presentation and setup-source inspection; no product behavior or fresh network installation',html_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'verification/host-docs-review.html'))).digest('hex'),checks:[]};
function run(args){return JSON.parse(execFileSync('agent-browser',['--session',session,'--json',...args],{encoding:'utf8',maxBuffer:5000000,timeout:45000}));}
function evaluate(script){const response=run(['eval','-b',Buffer.from(`(()=>{${script}})()`).toString('base64')]);if(!response.success)throw new Error(JSON.stringify(response.error));return response.data.result;}
function check(name,fn){try{result.checks.push({name,status:'PASS',observation:fn()});}catch(e){result.checks.push({name,status:'FAIL',error:sanitize(e.message)});}}
check('deterministic data and setup-source tests',()=>sanitize(execFileSync(process.execPath,['--test','scripts/host-review-html.test.mjs'],{cwd:root,encoding:'utf8',maxBuffer:1000000}).trim()));
run(['open',pathToFileURL(path.join(root,'verification/host-docs-review.html')).href]);
run(['set','offline','on']);
check('offline initial load and no resource dependencies',()=>evaluate(`
 if(document.getElementById('results-count').textContent!=='${openClaims.length.toLocaleString()} matching occurrences · showing 1–20')throw Error('Initial count');
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
 const refs=[...new Set(data.claims.flatMap(c=>c.evidence_refs.map(e=>e.artifact_ref)))];
 for(const ref of refs){const c=data.claims.find(c=>c.evidence_refs.some(e=>e.artifact_ref===ref));document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=c.id;document.getElementById('search').dispatchEvent(new Event('input'));document.querySelector('.claim>details').open=true;const button=[...document.querySelectorAll('.claim [data-artifact]')].find(b=>b.dataset.artifact===ref);button.click();
  const body=document.getElementById('viewer-body').textContent;if(!body.includes(c.page_title)||!body.includes('Limit:')||!body.includes(data.files[ref].sha256))throw Error('Evidence context '+ref);document.getElementById('close-viewer').click();}
 document.getElementById('clear').click();return {passages:observations,contextualEvidenceRecords:refs.length};`));
check('selected proof opens only its exact check with passage context and product sources stay separate',()=>evaluate(`
 const data=JSON.parse(document.getElementById('report-data').textContent),groups=[data.supplemental_live_checks.mapped_claims,data.current_readonly_checks.mapped_claims];let checks=0;
 for(const mapped of groups)for(const m of mapped){document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=m.claim_id;document.getElementById('search').dispatchEvent(new Event('input'));
 const card=document.querySelector('.claim');if(!card)throw Error('Missing mapped claim '+m.claim_id);card.querySelector('details').open=true;
 if(!card.textContent.includes('What we actually tested:')||!card.textContent.includes(m.coverage.level))throw Error('Coverage label');
 for(const target of m.checks){const b=[...card.querySelectorAll('[data-check]')].find(b=>b.dataset.check===target.id);if(!b)throw Error('Missing check control');b.click();
 const body=document.getElementById('viewer-body');const selected=JSON.parse(body.querySelector('pre').textContent);
 if(selected.check_id!==target.id||!body.textContent.includes(m.page_title)||!body.textContent.includes('Limit:')||!body.textContent.includes(data.files[target.artifact_ref].sha256)||!body.textContent.includes('Back to the page passage'))throw Error('Wrong proof/context '+target.id);
 document.getElementById('close-viewer').click();checks++;}}
 document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value='MCL-e12ac9f6be2ce502';document.getElementById('search').dispatchEvent(new Event('input'));
 const product=document.querySelector('.claim');product.querySelector('details').open=true;
 const hrefs=[...product.querySelectorAll('a[href]')].map(a=>a.href);
 for(const u of ['https://vast.ai/hosting','https://vast.ai/products/gpu-cloud','https://vast.ai/article/vast-ai-startup-program'])if(!hrefs.includes(u))throw Error('Missing product source link');
 if(!product.textContent.includes('not a runtime test'))throw Error('Product/runtime distinction');
 document.getElementById('clear').click();return {mappedClaims:groups.reduce((n,m)=>n+m.length,0),exactCheckControls:checks,publicSources:3};`));
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
run(['set','offline','off']);
result.status=result.checks.every(c=>c.status==='PASS')?'PASS':'FAIL';
fs.writeFileSync(path.join(root,destination),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:result.status,checks:result.checks.map(c=>({name:c.name,status:c.status,error:c.error})),evidence:destination},null,2));
if(result.status!=='PASS')process.exitCode=1;
