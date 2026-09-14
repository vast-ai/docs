import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const dir='verification/evidence/2026-09-09-host-authority-correction-attempt-01';
const selfRecord=process.argv[2];if(selfRecord)assert.match(selfRecord,/^package-final-\d+\.json$/);
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>{const n=p+'/'+e.name;assert.ok(!e.isSymbolicLink(),n);return e.isDirectory()?walk(n):[n];});
const changed=execFileSync('git',['diff','--name-only','-z'],{encoding:'utf8'}).split('\0').filter(Boolean);
const untracked=execFileSync('git',['ls-files','--others','--exclude-standard','-z','scripts','verification'],{encoding:'utf8'}).split('\0').filter(Boolean);
const files=[...new Set([...walk(dir),...changed,...untracked])].filter(p=>/\.(json|md|mdx|txt|html|py|mjs)$/.test(p));
const flagged=[],fixtures=[];
for(const p of files){let text=fs.readFileSync(p,'utf8');if(p==='scripts/host-review-html.test.mjs'){const fixture='Authorization: Bearer exampleCredentialValue';assert.equal(text.split(fixture).length-1,1);text=text.replace(fixture,'[known synthetic sanitizer fixture]');fixtures.push({path:p,fixture:'exampleCredentialValue only'});}if(/--api-key[=\s]+[a-f0-9]{40,}|Authorization["':\s]+Bearer\s+[A-Za-z0-9_-]{20,}|-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----/i.test(text))flagged.push(p);}
assert.deepEqual(flagged,[],'Selected credential-pattern scan failed');
const localLinks=[],pending=[];
for(const p of walk(dir).filter(p=>p.endsWith('.md'))){for(const m of fs.readFileSync(p,'utf8').matchAll(/\[[^\]]*\]\(([^)]+)\)/g)){if(/^(?:https?:|#)/.test(m[1]))continue;const destination=path.resolve(path.dirname(p),m[1].split('#')[0]);if(!fs.existsSync(destination)){const allowed=[path.resolve(dir,'final-integrity-01.json'),...(selfRecord?[path.resolve(dir,selfRecord)]:[])];assert.ok(allowed.includes(destination),'Missing local link '+p+' '+m[1]);pending.push({path:p,ref:m[1],reason:destination.endsWith('/'+selfRecord)?'This active command record is written by its retaining wrapper after the check returns.':'Final integrity record is written after closeout, then checked again.'});}else localLinks.push({path:p,ref:m[1]});}}
execFileSync('git',['diff','--check'],{stdio:'pipe'});execFileSync('git',['diff','--cached','--check'],{stdio:'pipe'});
console.log(JSON.stringify({status:'PASS',scannedTextFiles:files.length,syntheticFixtures:fixtures,credentialPatternFindings:flagged,existingLocalLinks:localLinks.length,pendingSeal:pending,whitespace:'PASS',limits:'Selected credential-pattern, link existence and whitespace checks only. No credential lookup, exhaustive privacy guarantee, publication authorization or claim truth.'},null,2));
