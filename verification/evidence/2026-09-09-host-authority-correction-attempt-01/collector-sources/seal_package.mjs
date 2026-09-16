import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const dir='verification/evidence/2026-09-09-host-authority-correction-attempt-01';
const out=dir+'/final-integrity-01.json';assert.ok(!fs.existsSync(out));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const baseline=read(dir+'/baseline-01.json');
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:32e6});
assert.equal(git('rev-parse','HEAD').trim(),baseline.head);
const old=baseline.tracked_records.filter(r=>r.path.startsWith('verification/evidence/'));
for(const r of old)assert.equal(hash(r.path),r.sha256,r.path);
const checks=['python-integration-02','reviewer-integration-03','model-current-check-02',
 'cli-signatures-final-01','openapi-final-01','persona-final-01','anchors-final-01',
 'html-tests-final-03','browser-authority-final-03','browser-passages-current-01','package-final-02'];
const records=checks.map(n=>{const p=dir+'/'+n+'.json';const r=read(p);assert.equal(r.exit_code,0,n);assert.equal(r.source_identity_unchanged,true,n);return {path:p,sha256:hash(p),command:r.command,exit_code:r.exit_code,source_identity_unchanged:true};});
// Later changes are limited to final HTML template/test/output and textual handoff.
// All Python and server implementation tested by the full suites must still match.
for(const [record,names] of [['python-integration-02',p=>p.endsWith('.py')||p.startsWith('host/')||p.startsWith('verification/current-')],
 ['reviewer-integration-03',p=>p==='review-server.mjs'||p==='scripts/current-host-review.test.mjs'||p==='scripts/export_host_review_html.mjs'||p.startsWith('verification/current-')||p.startsWith('host/')],
 ['html-tests-final-03',p=>['scripts/templates/host-docs-review.html','scripts/host-review-html.test.mjs','verification/host-docs-review.html'].includes(p)]]) {
 for(const [p,sha] of Object.entries(read(dir+'/'+record+'.json').source_hashes_after))if(names(p))assert.equal(hash(p),sha,p+' drift since '+record);
}
const browser=read(dir+'/reviewer-browser-final-03/result.json');
assert.equal(browser.status,'PASS');assert.equal(browser.server_sha256,hash('review-server.mjs'));
assert.equal(browser.model_sha256,hash('verification/current-host-docs-review.json'));
assert.equal(browser.html_sha256,hash('verification/host-docs-review.html'));
const graph=read(dir+'/graph-navigation-refresh-02.json');assert.equal(graph.pass,true);
assert.equal(graph.new_graph_sha256,hash('graphify-out/graph.json'));
for(const p of graph.ast_replaced_sources)assert.equal(hash(p),graph.selected_source_hashes[p],p+' AST graph source drift');
const integrity=read(dir+'/final-scope-integrity-01.json');
assert.equal(integrity.historical_artifacts_unchanged,2247);
assert.equal(integrity.index.all_stage_zero_paths_modes_and_object_ids_match_starting_head,true);
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>{const n=p+'/'+e.name;assert.ok(!e.isSymbolicLink(),n);return e.isDirectory()?walk(n):[n];});
const newFiles=git('ls-files','--others','--exclude-standard','-z','scripts','verification').split('\0').filter(Boolean);
const changed=git('diff','--name-only','-z').split('\0').filter(Boolean);
const files=[...new Set([...changed,...newFiles,...walk(dir),'graphify-out/graph.json'])].sort();
const artifacts=files.filter(p=>p!==out).map(p=>({path:p,bytes:fs.statSync(p).size,sha256:hash(p)}));
assert.equal(git('diff','--cached','--binary'),'');
const model=read('verification/current-host-docs-review.json');
const result={recorded_at:new Date().toISOString(),status:'PASS',scope:'Repository-local authority/classification/citation correction and reviewer refresh only',starting_head:baseline.head,current_head:git('rev-parse','HEAD').trim(),historical_evidence_unchanged:old.length,index:integrity.index,current_counts:model.counts,checks:records,artifacts,source_limits:'Full195Python and102reviewer tests precede the final HTML-label/test-only follow-up; final24HTML tests and byte-current browser check cover that follow-up. Exact source pins verified above. No new Host/API/SSH/paid runtime, server enforcement, compliance, Product/Finance/Legal approval, publication, or human acceptance.',external_workstreams_complete:false,staged_content_changed:false};
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'PASS',sealed_files:artifacts.length,historical_evidence_unchanged:old.length,checks:records.length,counts:model.counts.claim_statuses}));
