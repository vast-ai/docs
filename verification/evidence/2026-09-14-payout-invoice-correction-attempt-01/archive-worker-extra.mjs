import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import{execFileSync}from'node:child_process';
const root=process.cwd(),dir='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01',worker=path.join(root,'.orchestra/payout-invoice/worker'),output=dir+'/worker-extra-archive-check-01.json',archive=dir+'/worker-extra-01.tar.gz';
if(fs.existsSync(output)||fs.existsSync(archive))throw Error('Refuse overwrite');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const first=JSON.parse(fs.readFileSync(dir+'/worker-delta-manifest.json')),firstArchive=path.resolve(dir+'/worker-delta-01.tar.gz');
for(const e of first.entries){if(sha(execFileSync('tar',['-xOf',firstArchive,e.path],{maxBuffer:128*1024*1024}))!==e.sha256)throw Error('First archive drift '+e.path);}
const paths=['scripts/test_current_host_vv_overlay.py','scripts/host-review-html.test.mjs','scripts/current-host-authority-integration.test.mjs','scripts/host-review-reader-copy.test.mjs'];
const guard='verification/evidence/2026-09-14-payout-invoice-guard-browser-attempt-01';
paths.push(...fs.readdirSync(path.join(worker,guard)).filter(p=>fs.lstatSync(path.join(worker,guard,p)).isFile()).map(p=>guard+'/'+p));
const entries=paths.map(p=>({path:p,sha256:sha(fs.readFileSync(path.join(worker,p))),root_equal:p.startsWith('scripts/')?sha(fs.readFileSync(path.join(root,p)))===sha(fs.readFileSync(path.join(worker,p))):null}));
if(entries.some(e=>e.root_equal===false))throw Error('Fixture code mismatch');
execFileSync('tar',['-czf',path.resolve(archive),'-C',worker,...paths]);
const listed=execFileSync('tar',['-tzf',path.resolve(archive)],{encoding:'utf8'}).trim().split('\n');
if(JSON.stringify(listed)!==JSON.stringify(paths))throw Error('Entry mismatch');
for(const e of entries){if(sha(execFileSync('tar',['-xOf',path.resolve(archive),e.path],{maxBuffer:16*1024*1024}))!==e.sha256)throw Error('Extra archive drift');}
fs.writeFileSync(output,JSON.stringify({recorded_at:new Date().toISOString(),result:'PASS',archive,archive_sha256:sha(fs.readFileSync(archive)),first_archive_verified_entries:first.entries.length,entries,limits:'Task-created fixture and worker-only browser evidence preserved before disposable checkout removal. Worker browser report 02 withdraws the earlier human-activation conclusion; root-visible-check-02 supplies the root visible-click retest.'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({artifact:output,result:'PASS',first_entries:first.entries.length,extra_entries:entries.length}));
