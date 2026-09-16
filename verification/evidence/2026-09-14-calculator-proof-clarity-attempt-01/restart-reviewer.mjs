import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
const name=process.argv[2]||'reviewer-restart-01';assert.match(name,/^reviewer-restart-[0-9]+$/);
const root=process.cwd(),out='verification/evidence/2026-09-14-calculator-proof-clarity-attempt-01/'+name+'.json';
assert(!fs.existsSync(out));
const sh=b=>crypto.createHash('sha256').update(b).digest('hex');
const pids=spawnSync('lsof',['-tiTCP:4000','-sTCP:LISTEN'],{encoding:'utf8'}).stdout.trim().split(/\s+/).filter(Boolean);
assert.equal(pids.length,1,'Expected exactly one localhost reviewer');const oldPid=Number(pids[0]);
const args=spawnSync('ps',['-p',String(oldPid),'-o','command='],{encoding:'utf8'}).stdout.trim();
const suffix=' review-server.mjs --host 127.0.0.1 --port 4000 --target http://127.0.0.1:3000';
assert(args==='node'+suffix||args===process.execPath+suffix,'Unexpected local reviewer command');
const cwd=spawnSync('lsof',['-a','-p',String(oldPid),'-d','cwd','-Fn'],{encoding:'utf8'}).stdout;
assert(cwd.split('\n').includes('n'+root),'Refuse to restart another workspace');
const started=new Date().toISOString();process.kill(oldPid,'SIGTERM');
for(let i=0;i<50;i++){try{process.kill(oldPid,0)}catch{break}await new Promise(r=>setTimeout(r,100));}
const child=spawn(process.execPath,['review-server.mjs','--host','127.0.0.1','--port','4000','--target','http://127.0.0.1:3000'],{cwd:root,detached:true,stdio:'ignore'});child.unref();
const expected=sh(fs.readFileSync('review-server.mjs'));let observation;
for(let i=0;i<40;i++){
 try{const response=await fetch('http://127.0.0.1:4000/__review__/api/context?path=%2Fhost%2Fearning');const body=await response.json();if(response.headers.get('x-vast-review-source-sha256')===expected&&body.currentReview?.available){observation={http_status:response.status,server_sha256:expected,current_available:true,page:body.currentReview.page.route,claims:body.currentReview.page.claims.length};break;}}
 catch{}await new Promise(r=>setTimeout(r,250));
}
const result={started,finished:new Date().toISOString(),status:observation?'PASS':'FAIL',old_pid:oldPid,new_pid:child.pid,observation:observation||null,limits:'Only the exact local review overlay was restarted. The Mint preview, feedback files and Host machines were not changed.'};
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));if(!observation)process.exitCode=1;
