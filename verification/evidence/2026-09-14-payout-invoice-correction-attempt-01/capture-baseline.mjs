import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync, spawn} from 'node:child_process';
const dir='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=args=>execFileSync('git',args,{encoding:'utf8',maxBuffer:32*1024*1024});
const gitHash=args=>new Promise((resolve,reject)=>{const h=crypto.createHash('sha256'),p=spawn('git',args);p.stdout.on('data',b=>h.update(b));p.on('error',reject);p.on('close',c=>c===0?resolve(h.digest('hex')):reject(Error('git exited '+c)));});
const files=[...new Set(git(['ls-files','-z','--cached','--others','--exclude-standard']).split('\0').filter(Boolean))].sort().map(p=>{
 if(!fs.existsSync(p))return {path:p,type:'missing'};
 return fs.lstatSync(p).isSymbolicLink()?{path:p,type:'symlink',target:fs.readlinkSync(p)}:{path:p,type:'file',sha256:hash(fs.readFileSync(p))};
});
const write=(p,v)=>fs.writeFileSync(`${dir}/${p}`,v,{flag:'wx'});
write('baseline.json',JSON.stringify({recorded_at:new Date().toISOString(),head:git(['rev-parse','HEAD']).trim(),branch:git(['branch','--show-current']).trim(),git_status:git(['status','--porcelain=v1','--untracked-files=all']),index_diff_sha256:await gitHash(['diff','--cached','--binary']),working_diff_sha256:await gitHash(['diff','--binary']),files},null,2)+'\n');
write('pre-correction-model.json',fs.readFileSync('verification/current-host-docs-review.json'));
write('pre-correction-payment.mdx',fs.readFileSync('host/payment.mdx'));
const m=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json'));
const claims=m.pages.flatMap(p=>p.claims.filter(c=>p.route==='/host/payment').map(c=>({page:p.route,...c})));
write('payment-inventory.json',JSON.stringify({recorded_at:new Date().toISOString(),counts:m.counts,claims},null,2)+'\n');
console.log(JSON.stringify({files:files.length,claims:claims.length,counts:m.counts.claim_statuses}));
