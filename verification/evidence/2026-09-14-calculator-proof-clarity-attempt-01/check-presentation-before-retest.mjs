import fs from 'node:fs';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {hostReviewReaderCopy} from '../../../scripts/host_review_reader_copy.mjs';
const root=process.cwd(),dir='verification/evidence/2026-09-14-calculator-proof-clarity-attempt-01';
const id='MCL-18f04c2ae7ee95b4',session='calculator-proof-clarity';
const result={started:new Date().toISOString(),checks:[],limits:'Local reader presentation only. No visit to the public calculator, output validation or status change.'};
const run=(...args)=>JSON.parse(execFileSync('agent-browser',['--session',session,'--json',...args],{encoding:'utf8',timeout:45000,maxBuffer:8e6}));
const evaluate=source=>{const r=run('eval','-b',Buffer.from(source).toString('base64'));assert.equal(r.success,true,JSON.stringify(r));return r.data.result;};
const record=(name,observation)=>result.checks.push({name,status:'PASS',observation});
try{
 run('open','file://'+root+'/verification/host-docs-review.html#claims');
 run('set','viewport','1280','1100');
 record('Offline card and separate calculator-output guidance',evaluate(`(()=>{
  const input=document.getElementById('search');input.value=${JSON.stringify(id)};input.dispatchEvent(new Event('input'));
  const card=document.getElementById('claim-${id}');if(!card)throw Error('Missing card');
  card.querySelector('.proof-guide').open=true;card.scrollIntoView();
  const text=card.innerText;for(const expected of ['Check calculator link','final URL, date and time, screenshot, and outcome','does not record a visit','Calculations','Market history','not requirements for closing this link entry'])if(!text.includes(expected))throw Error(expected);
  const raw=JSON.parse(document.getElementById('report-data').textContent).claims.find(c=>c.id==='${id}');if(raw.status!=='UNVALIDATED')throw Error('Status changed');
  return {id,status:raw.status,text};
 })()`));
 run('screenshot',root+'/'+dir+'/offline-card.png');
 record('Offline exact documentation-check modal',evaluate(`(()=>{
  document.querySelector('#claim-${id} [data-basis]').click();
  const dialog=document.querySelector('dialog[open]');if(!dialog)throw Error('No modal');
  const text=dialog.innerText;for(const expected of ['does not record a visit','final URL, date and time, screenshot, and outcome','Whole retained documentation check'])if(!text.includes(expected))throw Error(expected);
  if(text.includes('no external retrieval was authorized'))throw Error('Historical rationale leaked into main copy');
  return {text};
 })()`));
 const response=await fetch('http://127.0.0.1:4000/__review__/api/context?path=%2Fhost%2Fearning');
 assert.equal(response.status,200);const body=await response.json();assert(body.currentReview.available);
 const claim=body.currentReview.page.claims.find(c=>c.id===id);
 assert.equal(claim.readerCopy.reviewKind,'calculator-link-review');
 assert.deepEqual(claim.readerCopy,hostReviewReaderCopy(claim));
 const model=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json'));
 assert.deepEqual(claim.readerCopy,hostReviewReaderCopy(model.pages.flatMap(p=>p.claims).find(c=>c.id===id)));
 const basis=claim.authorityScan.basis[0];
 const href='http://127.0.0.1:4000/__review__/current-artifact?'+new URLSearchParams({ref:basis.artifactRef,page:'/host/earning',claim:id,basis:'0'});
 const source=await fetch(href);assert.equal(source.status,200);const html=await source.text();
 assert.match(html,/does not record a visit/);assert.match(html,/final URL, date and time, screenshot, and outcome/);
 assert.match(html,/Whole retained documentation check/);assert.match(html,/no external retrieval was authorized/);
 assert.equal((await fetch(href.replace('basis=0','basis=99999'))).status,404);
 record('Live API and exact source selector',{id,status:claim.status,readerCopy:claim.readerCopy,sourceHTTP:source.status,invalidSelectorHTTP:404});
 run('open','http://127.0.0.1:4000/host/earning#market-data');
 run('wait','--fn','!!document.querySelector("#__vast_review_host__")?.shadowRoot.querySelector("#current-section-filter")');
 record('Live rendered card',evaluate(`(()=>{
  const shadow=document.querySelector('#__vast_review_host__').shadowRoot;
  if(!shadow.querySelector('#panel').classList.contains('open'))shadow.querySelector('#pill').click();
  const filter=shadow.querySelector('#current-section-filter');filter.value='Market Data';filter.dispatchEvent(new Event('change',{bubbles:true}));
  const card=shadow.querySelector('[data-current-claim="${id}"]');if(!card||card.hidden)throw Error('Missing card');
  card.querySelector('.proof-guide').open=true;card.scrollIntoView();
  const text=card.innerText;for(const expected of ['Check calculator link','final URL, date and time, screenshot, and outcome','does not record a visit','Calculations','Market history','not requirements for closing this link entry'])if(!text.includes(expected))throw Error(expected);
  return {id,status:card.dataset.currentStatus,text};
 })()`));
 run('screenshot',root+'/'+dir+'/localhost-card.png');
 result.status='PASS';
}catch(e){result.status='FAIL';result.error=String(e.stack);process.exitCode=1;}
finally{try{run('close');result.browserClosed=true;}catch(e){result.browserClosed=false;result.cleanupError=String(e);process.exitCode=1;}result.finished=new Date().toISOString();fs.writeFileSync(dir+'/presentation-01.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));}
