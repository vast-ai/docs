import fs from 'node:fs';
import {describeHostReview,buildHostReviewQueue} from '../../../scripts/host_review_work_queue.mjs';
const dir='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01',name=process.argv[2];
if(!/^queue-[0-9]+$/.test(name))throw Error('Unique name required');
const file=dir+'/'+name+'.json';if(fs.existsSync(file))throw Error('Refuse overwrite');
const model=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json')),claims=model.pages.flatMap(p=>p.claims),payment=model.pages.find(p=>p.route==='/host/payment').claims.filter(c=>c.status==='PASS');
const observed=payment.map(c=>({id:c.id,classification:c.classification,status:c.status,work:describeHostReview(c)})),queue=buildHostReviewQueue(claims);
const checks={elevenSupportedPaymentRecords:observed.length===11,noCompletedPaymentTriage:observed.every(c=>c.work.completed&&c.work.bucket==='completed'&&!c.work.needsTriage),countsUnchanged:queue.total===2013&&queue.statuses.PASS===319&&queue.statuses.FAIL===26,unknownStillTriage:describeHostReview({id:'fixture',status:'PASS',classification:'UNKNOWN_FUTURE_TYPE',required_evidence_types:['AUTHORITATIVE_DOCUMENTATION_CITATION']}).needsTriage};
const result={recorded_at:new Date().toISOString(),result:Object.values(checks).every(Boolean)?'PASS':'FAIL',checks,observed,buckets:queue.buckets,limitations:'Presentation taxonomy only. No claim adjudication or proof changes.'};fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({artifact:file,result:result.result,checks}));process.exitCode=result.result==='PASS'?0:1;
