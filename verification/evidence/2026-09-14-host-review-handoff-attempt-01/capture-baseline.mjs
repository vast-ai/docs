import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const dir='verification/evidence/2026-09-14-host-review-handoff-attempt-01';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=args=>execFileSync('git',args,{maxBuffer:256*1024*1024}).toString();
const files=git(['ls-files','-z']).split('\0').filter(Boolean).filter(p=>p.startsWith('verification/evidence/')||p.startsWith('host/')||[
  'verification/current-host-docs-review.json','verification/host-docs-review.html','verification/host-docs-review-export.json',
  'review-server.mjs','scripts/host_review_work_queue.mjs','scripts/host_review_reader_copy.mjs','scripts/templates/host-docs-review.html','scripts/export_host_review_html.mjs',
].includes(p)).map(p=>{const b=fs.readFileSync(p);return{path:p,bytes:b.length,sha256:sha(b)}});
const result={at:new Date().toISOString(),head:git(['rev-parse','HEAD']).trim(),branch:git(['branch','--show-current']).trim(),
  index_diff:git(['diff','--cached','--stat']),working_tree_status:git(['status','--porcelain=v1','--untracked-files=all']),
  note:'Initial observed tree/index were clean; the only new paths at capture are this plan and capture script. No implementation or task-plan edit has occurred.',files};
fs.writeFileSync(dir+'/baseline.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({head:result.head,files:files.length,index_diff:result.index_diff,status:result.working_tree_status}));
