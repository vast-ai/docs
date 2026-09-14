import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const [root,name]=process.argv.slice(2),session='payout-offline-20260914';
const attempt=path.join(root,'verification/evidence/2026-09-14-payout-provider-correction-attempt-01');
const out=path.join(attempt,name+'.json');if(fs.existsSync(out))throw Error('Refuse overwrite');
const started_at=new Date().toISOString(),html=path.join(root,'verification/host-docs-review.html');
const run=args=>JSON.parse(execFileSync('agent-browser',['--session',session,'--json',...args],{encoding:'utf8',timeout:45000,maxBuffer:4000000}));
let observation,error;
try{
 run(['open',pathToFileURL(html).href]);run(['set','offline','on']);
 const js=`(()=>{const ids=['MCL-77f72f0e0ac77e54','MCL-a04f3ef2f5a7d5fd','MCL-cc62439b0f816902','MCL-9826b26393329d27'];const data=JSON.parse(document.getElementById('report-data').textContent),rows=[];
 for(const id of ids){document.getElementById('clear').click();document.getElementById('status').value='ALL';document.getElementById('search').value=id;document.getElementById('search').dispatchEvent(new Event('input'));const c=data.claims.find(c=>c.id===id),card=document.querySelector('.claim');if(!card||c.status!=='PASS')throw Error('Missing corrected card '+id);
 card.querySelector('[data-passage]').click();const passage=document.getElementById('viewer-body').textContent;if(!document.getElementById('viewer').open||!document.querySelector('.source-line.highlight')||!passage.includes('Earnings'))throw Error('Wrong passage '+id);document.getElementById('close-viewer').click();
 const sources=[];for(const b of card.querySelectorAll('[data-basis]')){b.click();const body=document.getElementById('viewer-body').textContent;sources.push({context:body.includes(c.reader_copy?.statementText||c.text),hasLimit:/not.*payment|not.*financial|capture time|user.attributed|user.supplied/i.test(body),hasCanonicalLabel:body.includes('Open canonical source'),hasEarningsLink:body.includes('Open Earnings page')});document.getElementById('close-viewer').click();}
 if(!sources.length||sources.some(s=>!s.context||!s.hasLimit)||!sources.some(s=>s.hasEarningsLink&&!s.hasCanonicalLabel))throw Error('Wrong proof or limits '+id);rows.push({id,status:c.status,sources});}
 const checks={fourCards:rows.length===4,remainingCorrections:data.counts.claim_statuses.FAIL===31,allClaims:data.claims.length===2013,currentResult:data.current_result_ref==='verification/evidence/2026-09-14-payout-provider-correction-attempt-01/result.md',noResourceDependencies:performance.getEntriesByType('resource').length===0,evidenceDate:document.getElementById('evidence-update-label').textContent==='Evidence update: 14 Sep 2026'};
 if(Object.values(checks).some(x=>!x))throw Error('Report counts/result/resources mismatch');document.querySelector('.claim').scrollIntoView({block:'start'});return {checks,rows,url:location.protocol};})()`;
 const r=run(['eval','-b',Buffer.from(js).toString('base64')]);if(!r.success)throw Error(JSON.stringify(r.error));observation=r.data.result;
 run(['screenshot',path.join(attempt,name+'.png')]);
}catch(e){error=e.message;}finally{try{run(['close']);}catch{}}
const result={started_at,finished_at:new Date().toISOString(),method:'Offline supplied-UI/provider correction review; no account or payment access',html_sha256:crypto.createHash('sha256').update(fs.readFileSync(html)).digest('hex'),result:error?'FAIL':'PASS',observation,error:error||null};
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({artifact:out,result:result.result,error:error||null,observation}));process.exitCode=error?1:0;
