import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const dir='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01',file=dir+'/root-visible-check-02.json';
if(fs.existsSync(file))throw Error('Refuse overwrite');
const commands=[],started_at=new Date().toISOString();
const browser=(...args)=>{const output=execFileSync('agent-browser',['--session','payout-invoice-review',...args],{encoding:'utf8',maxBuffer:4*1024*1024,timeout:30000});commands.push({args,output});return output;};
const evaluate=js=>JSON.parse(browser('eval',js));
let error=null,results=[];
try{
 const target=evaluate('({url:location.href,claim:document.querySelector("#search").value,open:document.querySelector(".claim details").open})');
 if(target.url.split('#')[0]!=='file://'+path.resolve('verification/host-docs-review.html')||target.claim!=='MCL-3afd93ae0b6cf8a4'||!target.open)throw Error('Unexpected target');
 evaluate('document.querySelector(".claim summary").scrollIntoView({block:"center",behavior:"instant"}); ({rect:document.querySelector(".claim summary").getBoundingClientRect().toJSON()})');
 browser('click','.claim summary');
 const closed=evaluate('({open:document.querySelector(".claim details").open})');
 browser('click','.claim summary');
 const opened=evaluate('({open:document.querySelector(".claim details").open})');
 if(closed.open||!opened.open)throw Error('Visible selector activation did not toggle');
 for(const basis of [0,1]){
  const selector='.claim [data-basis="'+basis+'"]';
  evaluate('document.querySelector('+JSON.stringify(selector)+').scrollIntoView({block:"center",behavior:"instant"}); ({rect:document.querySelector('+JSON.stringify(selector)+').getBoundingClientRect().toJSON()})');
  browser('click',selector);
  const observed=evaluate('({open:document.querySelector("#viewer").open,text:document.querySelector("#viewer-body").textContent})');
  const expected=basis===0?'Published Host Payouts guidance':'Hosting Agreement';
  const pass=observed.open&&observed.text.includes(expected)&&observed.text.includes('SHA-256');
  browser('screenshot',path.resolve(dir+'/root-visible-basis-'+basis+'-01.png'));
  results.push({basis,pass,...observed});browser('click','#close-viewer');
 }
}catch(e){error=e.message;}
const result={started_at,finished_at:new Date().toISOString(),result:!error&&results.length===2&&results.every(r=>r.pass)?'PASS':'FAIL',html_path:path.resolve('verification/host-docs-review.html'),html_sha256:crypto.createHash('sha256').update(fs.readFileSync('verification/host-docs-review.html')).digest('hex'),method:'DOM scrollIntoView positions observed controls; agent-browser click activates them. No element.click() or synthetic click event is used. DOM reads inspect outcomes.',commands,results,error,limits:'One root offline timing card, its disclosure and two exact-source dialogs. No account, payment, backend, external source or human acceptance check.'};
fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({artifact:file,result:result.result,error}));process.exitCode=result.result==='PASS'?0:1;
