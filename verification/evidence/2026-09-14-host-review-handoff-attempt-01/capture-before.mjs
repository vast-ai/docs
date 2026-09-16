import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const dir='verification/evidence/2026-09-14-host-review-handoff-attempt-01';
const file=dir+'/before-01.json';
if(fs.existsSync(file))throw Error('Refuse overwrite');
const commands=[];
const browser=(...args)=>{const output=execFileSync('agent-browser',['--session','host-handoff-before',...args],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});commands.push({args,output});return output;};
const evaluate=s=>JSON.parse(browser('eval',s));
const started_at=new Date().toISOString();
let error=null,api,ui;
try{
 browser('click','@e3');
 ui=evaluate(`(()=>{const s=document.querySelector('#__vast_review_host__').shadowRoot;return {url:location.href,badge:s.querySelector('#pill').textContent,panel:s.querySelector('#panel').textContent,filters:[...s.querySelectorAll('select')].map(x=>({id:x.id,value:x.value})),cards:[...s.querySelectorAll('[data-current-claim]')].map(x=>({id:x.getAttribute('data-current-claim'),status:x.getAttribute('data-current-status'),hidden:x.hidden}))}})()`);
 const response=await fetch('http://127.0.0.1:4000/__review__/api/context?path=%2Fhost%2Fdatacenter-status');
 const context=await response.json();
 const page=context.currentReview?.page;
 api={http_status:response.status,available:context.currentReview?.available,route:page?.route,claims:page?.claims?.map(c=>({id:c.id,status:c.status,headings:c.headings})),work_queue:context.currentReview?.workQueue};
 browser('screenshot',path.resolve(dir+'/before-datacenter-01.png'));
}catch(e){error=e.message;}
fs.writeFileSync(file,JSON.stringify({started_at,finished_at:new Date().toISOString(),ui,api,commands,error,finding:'Before implementation: inspect whether note badge, source-first order and heading filters obscure five known Datacenter corrections. This is reviewer UI evidence, not product proof.',limits:'No owner questions or new product evidence are created by this observation.'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({file,error,badge:ui?.badge,filters:ui?.filters,cards:ui?.cards,api_count:api?.claims?.length}));
process.exitCode=error?1:0;
