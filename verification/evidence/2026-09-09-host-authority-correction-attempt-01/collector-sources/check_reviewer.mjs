import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const name=process.argv[2];assert.match(name||'',/^[a-z0-9-]+$/);
const dir='verification/evidence/2026-09-09-host-authority-correction-attempt-01/'+name;fs.mkdirSync(dir);
const session='authority-'+name;
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const server=sha('review-server.mjs'),model=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json'));
const registry='verification/current-host-authority-adjudications.json';
const targets=model.pages.flatMap(p=>p.claims.filter(c=>c.evidence_refs.some(r=>r.artifact_ref===registry)).map(c=>({route:p.route,id:c.id,status:c.status,text:c.text})));
assert.equal(targets.length,13,'Frozen four controls, five narrowed obligations, three partials, one security atom');
const overview=model.pages.find(p=>p.route==='/host/hosting-overview');
const negative=overview.claims.find(c=>c.text.includes('The contract locks in the offer terms'));
assert.equal(negative?.status,'FAIL');targets.push({route:overview.route,id:negative.id,status:negative.status,text:negative.text,negative:true});
const browser=(...args)=>execFileSync('agent-browser',['--session',session,...args],{encoding:'utf8',timeout:60000,maxBuffer:30e6});
const evaluate=s=>JSON.parse(browser('eval','-b',Buffer.from(s).toString('base64')));
const rows=[],save=(n,v)=>fs.writeFileSync(dir+'/'+n,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
try {
 const contexts=[];
 for(const page of model.pages){const response=await fetch('http://127.0.0.1:4000/__review__/api/context?path='+encodeURIComponent(page.route));assert.equal(response.status,200);assert.equal(response.headers.get('x-vast-review-source-sha256'),server);const context=await response.json();assert.equal(context.currentReview.available,true,page.route);assert.equal(context.currentReview.page.claims.length,page.claims.length);contexts.push({route:page.route,claims:page.claims.length});}
 browser('set','viewport','1600','1050');let currentRoute='';
 for(const target of targets){
  const {route,id,status}=target;
  if(route!==currentRoute){browser('open','http://127.0.0.1:4000'+route);browser('wait','--fn','!!document.querySelector("#__vast_review_host__")?.shadowRoot.querySelector("#current-section-filter")');currentRoute=route;}
  const observed=evaluate(`(()=>{const s=document.querySelector('#__vast_review_host__').shadowRoot;if(!s.querySelector('#panel').classList.contains('open'))s.querySelector('#pill').click();const f=s.querySelector('#current-section-filter');f.value='';f.dispatchEvent(new Event('change',{bubbles:true}));const c=[...s.querySelectorAll('[data-current-claim]')].find(c=>c.dataset.currentClaim===${JSON.stringify(id)});if(!c)throw Error('Missing card');c.scrollIntoView({block:'center'});CSS.highlights.delete('vast-review-claim');c.querySelector('[data-show-current-claim]').click();return {id:c.dataset.currentClaim,status:c.querySelector('[data-status]').dataset.status,text:c.textContent,highlights:[...(CSS.highlights.get('vast-review-claim')||[])].map(r=>r.toString()),links:[...c.querySelectorAll('a[href*="/__review__/current-artifact"]')].map(a=>a.href),sources:[...c.querySelectorAll('a[href^="https://"]')].map(a=>({text:a.textContent,href:a.href}))};})()`);
  assert.equal(observed.status,status);assert.ok(observed.highlights.length,id);
  if(!target.negative){assert.ok(observed.links.some(l=>decodeURIComponent(l).includes(registry)),'Missing bound proof '+id);assert.ok(observed.sources.length,'Missing authoritative external source '+id);}
  const links=[];
  for(const link of [...new Set(observed.links)]){const url=new URL(link);assert.equal(url.origin,'http://127.0.0.1:4000');assert.equal(url.searchParams.get('claim'),id);assert.equal(url.searchParams.get('page'),route);const response=await fetch(link);assert.equal(response.status,200);const text=await response.text();assert.ok(text.includes('<blockquote>'+escape(target.text)+'</blockquote>'),'Wrong proof context '+id);assert.ok(text.includes('Statement status:</b> '+status));links.push({ref:url.searchParams.get('ref'),http_status:response.status,exact_claim_context:true});}
  rows.push({...observed,links});
  if(['MCL-508003945b6ef934','MCL-3cfe1a3c265f0223','MCL-8fe2020c0e7efe26'].includes(id)){
   evaluate(`(()=>{const s=document.querySelector('#__vast_review_host__').shadowRoot;[...s.querySelectorAll('[data-current-claim]')].find(c=>c.dataset.currentClaim===${JSON.stringify(id)}).scrollIntoView({block:'start'});return true;})()`);
   browser('screenshot',path.resolve(dir,id+'.png'));
  }
 }
 browser('open','file://'+path.resolve('verification/host-docs-review.html'));browser('wait','--fn','!!document.querySelector("#claim-list article")');
 const offline=evaluate(`(()=>{const results=[];for(const target of ${JSON.stringify(targets)}){const {id,negative}=target;document.querySelector('#clear').click();const select=document.querySelector('#status');select.value='ALL';select.dispatchEvent(new Event('change',{bubbles:true}));const q=document.querySelector('#search');q.value=id;q.dispatchEvent(new Event('input',{bubbles:true}));const card=document.querySelector('#claim-list article');if(!card)throw Error('Missing offline card '+id);card.querySelector('details').open=true;let modal='';if(!negative){const b=[...card.querySelectorAll('[data-artifact]')].find(b=>b.dataset.artifact===${JSON.stringify(registry)});if(!b)throw Error('Missing offline authority proof '+id);b.click();modal=document.querySelector('#viewer-body').textContent;if(!document.querySelector('#viewer').open)throw Error('Closed proof dialog '+id);if(document.querySelector('#viewer-body [data-passage]')?.dataset.passage!==id)throw Error('Wrong proof context '+id);document.querySelector('#close-viewer').click();}results.push({id,text:card.textContent,modal});card.querySelector('[data-passage]').click();if(!document.querySelector('.source-line.highlight'))throw Error('Missing exact source highlight '+id);document.querySelector('#close-viewer').click();}document.querySelector('#clear').click();const f=document.querySelector('#lane');f.value='citation';f.dispatchEvent(new Event('change',{bubbles:true}));return {results,citations:document.querySelector('#results-count').textContent,resources:performance.getEntriesByType('resource').filter(r=>/^https?:/.test(r.name)).map(r=>r.name)};})()`);
 save('observations.json',{contexts,online:rows,offline});assert.deepEqual(offline.resources,[]);for(const r of offline.results){if(r.id===negative.id){assert.match(r.text,/Missing authoritative citation/);continue;}assert.ok(r.modal.includes('Refers to:'));assert.doesNotMatch(r.modal,/Record not bundled/);}
 browser('screenshot',path.resolve(dir,'offline-citations.png'));
 save('result.json',{recorded_at:new Date().toISOString(),status:'PASS',server_sha256:server,model_sha256:sha('verification/current-host-docs-review.json'),html_sha256:sha('verification/host-docs-review.html'),contexts,online:rows,offline,limits:'Localhost/offline reviewer controls and exact proof-link observations only; not Host runtime, contractual compliance, legal advice or human acceptance.'});
 console.log(JSON.stringify({status:'PASS',contexts:contexts.length,claims:rows.length,proof_links:rows.reduce((n,r)=>n+r.links.length,0),offline_claims:offline.results.length,citations:offline.citations,remote_resources:offline.resources.length}));
} catch(e){save('failure.json',{recorded_at:new Date().toISOString(),error:e.message,completed:rows.length});throw e;}
finally{try{browser('close')}catch{}}
