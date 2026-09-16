import fs from 'node:fs';import path from 'node:path';import{execFileSync}from'node:child_process';
const root=process.argv[2],name=process.argv[3],session='payout-review-20260914';
const out=path.join(root,'verification/evidence/2026-09-14-payout-provider-correction-attempt-01',name+'.json');
if(fs.existsSync(out))throw Error('Refuse overwrite');
execFileSync('agent-browser',['--session',session,'open','http://127.0.0.1:4000/host/payment'],{cwd:root,encoding:'utf8'});
execFileSync('agent-browser',['--session',session,'wait','--fn','!!document.querySelector("#__vast_review_host__")?.shadowRoot.querySelector("#current-section-filter")'],{cwd:root,encoding:'utf8'});
const js= `(async()=>{const ids=['MCL-77f72f0e0ac77e54','MCL-a04f3ef2f5a7d5fd','MCL-cc62439b0f816902','MCL-9826b26393329d27'];
const response=await fetch('/__review__/api/context?path=%2Fhost%2Fpayment'); const current=(await response.json()).currentReview;
const shadow=document.querySelector('#__vast_review_host__')?.shadowRoot;
if(shadow&&!shadow.querySelector('#panel').classList.contains('open'))shadow.querySelector('#pill').click();
const selected=ids.map(id=>current.page.claims.find(c=>c.id===id));
const cards=ids.map(id=>shadow?.querySelector('[data-current-claim="'+id+'"]'));
const main=document.querySelector('main')||document.body;
const checks={
 fourSelectedPresent:selected.every(Boolean),
 fourCorrectedStatuses:selected.every(c=>c?.status==='PASS'),
 exactNewIntro:main.innerText.includes('The payout providers shown under Earnings > Payout Account are:'),
 setupHeading:!!document.getElementById('how-do-i-set-up-payouts'),
 oldShortAlias:!!document.getElementById('direct-bank-transfer'),
 oldLongAlias:!!document.getElementById('can-vast-send-direct-bank-transfers'),
 unsupportedExclusionRemoved:!main.innerText.includes('Direct bank transfers, ACH, wire, and SWIFT payouts are not available.'),
 sourceLinks:[...main.querySelectorAll('a[href="https://cloud.vast.ai/earnings/"]')].length>=2,
 fourRenderedPass:cards.every(c=>c?.querySelector('[data-status]')?.dataset.status==='PASS')
};
const evidence=[];for(let i=0;i<cards.length;i++){for(const link of cards[i]?.querySelectorAll('a[href*="basis="]')||[]){const u=new URL(link.href,location.href);if(u.origin!==location.origin)throw Error('External evidence request refused');const r=await fetch(u);const t=await r.text();evidence.push({id:ids[i],href:u.pathname+u.search,status:r.status,hasProvenance:/user.supplied|user.attributed|supplied.*screenshot/i.test(t),hasLimit:/capture.time|capture time|unknown|not.*payment/i.test(t)});}}
checks.fourEvidenceControls=ids.every(id=>evidence.some(e=>e.id===id&&e.status===200&&e.hasProvenance&&e.hasLimit));
return{checks,evidence,statuses:selected.map(c=>({id:c?.id,status:c?.status,text:c?.text})),sourceHeader:response.headers.get('x-vast-review-source-sha256')};})()`;
const started_at=new Date().toISOString();let observation,error;try{observation=JSON.parse(execFileSync('agent-browser',['--session',session,'eval','-b',Buffer.from(js).toString('base64')],{cwd:root,encoding:'utf8',maxBuffer:10000000}));}catch(e){error=e.message;}
const result={started_at,finished_at:new Date().toISOString(),method:'Read-only localhost rendered UI and exact local evidence-link checks; no external source or account action',expected:'Corrected bounded provider claims, both fragment aliases, citations and exact evidence controls',result:!error&&Object.values(observation.checks).every(Boolean)?'PASS':'FAIL',observation,error:error||null};fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({artifact:out,result:result.result,checks:observation?.checks,error}));process.exitCode=result.result==='PASS'?0:1;
