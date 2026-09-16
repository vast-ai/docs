import fs from 'node:fs';import path from 'node:path';import {execFileSync}from'node:child_process';
const root=process.cwd(),worker=path.join(root,'.orchestra/payout-invoice/worker');
if(!fs.existsSync(path.join(worker,'.git')))throw Error('Expected isolated worktree');
const paths=[...new Set(execFileSync('git',['ls-files','-z','--cached','--others','--exclude-standard'],{encoding:'utf8',maxBuffer:32*1024*1024}).split('\0').filter(Boolean))];
for(const p of paths){if(p.startsWith('.orchestra/'))continue;const src=path.join(root,p),dest=path.join(worker,p);if(!fs.existsSync(src)||!fs.lstatSync(src).isFile())continue;fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(src,dest);}
console.log(JSON.stringify({copied:paths.length,worker:'.orchestra/payout-invoice/worker'}));
