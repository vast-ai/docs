import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const root='verification/evidence/2026-09-09-host-authority-correction-attempt-01';
const name=process.argv[2];assert.match(name||'',/^[a-z0-9-]+$/);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const baseline=JSON.parse(fs.readFileSync(root+'/baseline-01.json'));
const historic=baseline.tracked_records.filter(r=>r.path.startsWith('verification/evidence/'));
const changes=historic.filter(r=>!fs.existsSync(r.path)||sha(fs.readFileSync(r.path))!==r.sha256);
assert.deepEqual(changes,[],'Historical evidence must not be rewritten');
const indexPath=execFileSync('git',['rev-parse','--git-path','index'],{encoding:'utf8'}).trim();
const indexSha=sha(fs.readFileSync(indexPath));
const stagedDiff=execFileSync('git',['diff','--cached','--binary']);
assert.equal(sha(stagedDiff),baseline.staged_diff_sha256,'Staged content changed without scope');
const staged=execFileSync('git',['ls-files','--stage','-z'],{encoding:'utf8'}).split('\0').filter(Boolean).map(row=>{
 const m=row.match(/^(\d+) ([a-f0-9]+) (\d)\t(.*)$/s);assert.ok(m);assert.equal(m[3],'0');return [m[4],m[1],m[2]];
}).sort((a,b)=>a[0].localeCompare(b[0]));
const tree=execFileSync('git',['ls-tree','-r','-z',baseline.head],{encoding:'utf8'}).split('\0').filter(Boolean).map(row=>{
 const m=row.match(/^(\d+) \w+ ([a-f0-9]+)\t(.*)$/s);assert.ok(m);return [m[3],m[1],m[2]];
}).sort((a,b)=>a[0].localeCompare(b[0]));
assert.deepEqual(staged,tree,'Index paths, modes or object IDs changed from the initially clean tree');
const before=JSON.parse(execFileSync('git',['show',baseline.head+':verification/current-host-docs-review.json'],{maxBuffer:20e6}));
const after=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json'));
const scope=JSON.parse(fs.readFileSync(root+'/candidate-inventory-01.json'));
const routes=new Set(scope.records.map(r=>r.route));
const unaffected=[];
for(const page of before.pages){if(routes.has(page.route))continue;const current=after.pages.find(p=>p.route===page.route);assert.deepEqual(current,page,page.route+' changed outside inventory');unaffected.push({route:page.route,claims:page.claims.length});}
const count={};for(const p of after.pages)for(const c of p.claims)count[c.status]=(count[c.status]||0)+1;
assert.deepEqual(count,after.counts.claim_statuses);
const oldById=new Map(before.pages.flatMap(p=>p.claims.map(c=>[c.id,{route:p.route,...c}])));
const changed=after.pages.flatMap(p=>p.claims.flatMap(c=>{const old=oldById.get(c.id);return !old||old.status!==c.status||old.text!==c.text||JSON.stringify(old.evidence_refs)!==JSON.stringify(c.evidence_refs)?[{route:p.route,id:c.id,old_status:old?.status??null,status:c.status,headings:c.headings,text:c.text,history:c.history}]:[]}));
const record={recorded_at:new Date().toISOString(),status:'PASS',method:'Independent immutable-history, index path/mode/object identity and whole-page out-of-scope comparison',index:{baseline_bytes_sha256:baseline.index_sha256,current_bytes_sha256:indexSha,bytes_unchanged:indexSha===baseline.index_sha256,staged_diff_unchanged:true,all_stage_zero_paths_modes_and_object_ids_match_starting_head:true,entries:staged.length,limit:'Index cache/metadata bytes changed during local work; no staged content change. No index restoration was performed.'},historical_artifacts_unchanged:historic.length,unaffected_pages:unaffected,baseline_counts:before.counts,current_counts:after.counts,changed,limitations:'Identity, scope and status accounting only. Exact changed-claim authority matching and browser proof-link validation are separate checks.'};
fs.writeFileSync(root+'/'+name+'.json',JSON.stringify(record,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({historical_artifacts_unchanged:historic.length,unaffected_pages:unaffected.length,changed_claims:changed.length,counts:count}));
