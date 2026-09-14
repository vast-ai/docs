import fs from 'node:fs';import {spawnSync}from'node:child_process';
const [name,command,...args]=process.argv.slice(2),dir='verification/evidence/2026-09-14-payout-terms-correction-attempt-01';
if(!/^[a-z0-9-]+$/.test(name))throw Error('Safe unique check name required');
const out=dir+'/'+name+'.json';if(fs.existsSync(out))throw Error('Refuse overwrite');
const started_at=new Date().toISOString(),r=spawnSync(command,args,{encoding:'utf8',maxBuffer:64*1024*1024,timeout:300000});
const result={started_at,finished_at:new Date().toISOString(),command:[command,...args],exit_code:r.status,error:r.error?.message||null,stdout:r.stdout||'',stderr:r.stderr||'',limit:'Repository or explicitly named local-interface check only; not payment behavior, legal approval or product acceptance.'};
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({artifact:out,exit_code:r.status,stdout_tail:result.stdout.slice(-2000),stderr_tail:result.stderr.slice(-2000)}));process.exitCode=r.status===0?0:1;
