import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';
import { buildReport, sanitize } from './export_host_review_html.mjs';

const {html,payload,manifest}=buildReport();
const model=JSON.parse(fs.readFileSync(new URL('../verification/current-host-docs-review.json',import.meta.url)));
const inputClaims=model.pages.flatMap(p=>p.claims);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');

test('all current occurrences retain identity, status, source and bounded text',()=>{
 assert.equal(payload.claims.length,model.counts.claims);
 assert.equal(payload.pages.length,44);
 assert.equal(payload.support_layers.length,33);
 for(const [i,c] of payload.claims.entries()){
  const original=inputClaims[i];
  assert.equal(c.id,original.id);assert.equal(c.status,original.status);
  assert.equal(c.text,sanitize(original.text));
  assert.deepEqual(c.spans,original.spans);
  assert.equal(c.rationale,sanitize(original.rationale));
  assert.equal(c.next_action,sanitize(original.next_action));
  assert.deepEqual(c.required_evidence_types,original.required_evidence_types);
 }
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
});
test('workstream totals and historical PASS scopes agree with records',()=>{
 const open=payload.claims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status));
 assert.equal(open.length,inputClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status)).length);
 for(const type of ['RUNTIME_OR_UI_OBSERVATION','CANONICAL_IMPLEMENTATION_SOURCE','ACCOUNTABLE_OWNER_CONFIRMATION','AUTHORITATIVE_DOCUMENTATION_CITATION']) assert.equal(open.filter(c=>c.required_evidence_types.includes(type)).length,inputClaims.filter(c=>!['PASS','NOT_APPLICABLE'].includes(c.status)&&c.required_evidence_types.includes(type)).length);
 const pass=payload.claims.filter(c=>c.status==='PASS');
 assert.equal(pass.filter(c=>c.history.carry_decision==='CARRIED_FORWARD_EXACT_SOURCE').length,inputClaims.filter(c=>c.status==='PASS'&&c.history.carry_decision==='CARRIED_FORWARD_EXACT_SOURCE').length);
 assert.equal(pass.filter(c=>c.history.carry_decision!=='CARRIED_FORWARD_EXACT_SOURCE').length,inputClaims.filter(c=>c.status==='PASS'&&c.history.carry_decision!=='CARRIED_FORWARD_EXACT_SOURCE').length);
});
test('all citation-lane FAIL records are visibly distinct from the two documentation defects',()=>{
 const citation=c=>c.status==='FAIL'&&c.required_evidence_types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION');
 const citationClaims=payload.claims.filter(citation);
 const readonlyFindings=JSON.parse(fs.readFileSync(new URL('../verification/current-host-readonly-findings.json',import.meta.url)));
 assert.equal(citationClaims.length,149);
 assert.equal(readonlyFindings.findings.filter(f=>f.status==='FAIL'&&f.classification==='CONFIRMED_DOCUMENTATION_DEFECT').length,2);
 assert.ok(citationClaims.some(c=>!c.rationale.startsWith('CONFIRMED_CITATION_DEFECT:')),'alternate citation wording stays visible');
 assert.match(html,/const citationDefect=c=>c\.status==='FAIL'&&c\.required_evidence_types\.includes\('AUTHORITATIVE_DOCUMENTATION_CITATION'\)/);
 assert.match(html,/Missing authoritative citation \(\$\{citationDefects\.length\.toLocaleString\(\)\} FAIL\)/);
 assert.match(html,/lane==='citation'\?citationDefect\(c\)/);
 assert.match(html,/Obtain the authoritative source for this wording from the recorded owner, add its citation, and retain a source\/link retest\./);
 assert.match(html,/This is a documentation\/source defect, not a failed runtime check\./);
 assert.doesNotMatch(html,/c\.rationale\.startsWith\('CONFIRMED_CITATION_DEFECT:'/);
});
test('offline review exposes only the two pinned wording replacements with retained FAIL history',()=>{
 assert.match(html,/twoDefectTransitionSha256='14b51b3a15dc3f21c7c4fc7a911cb7c5f2964b07924d188e4d0c7e700124aea8'/);
 assert.match(html,/CURRENT-TWO-DEFECT-TRANSITION-01/);
 assert.match(html,/Wording corrected; further evidence needed\./);
 assert.match(html,/Original finding history \(FAIL\)/);
 assert.match(html,/c\.status!=='UNVALIDATED'\|\|c\.history\?\.carry_decision!=='TWO_DEFECT_REPLACEMENT_UNVALIDATED'/);
 assert.match(html,/Open immutable transition record and original finding/);
});
test('supplemental live checks retain exact versus partial scope without changing claim status',()=>{
 const supplemental=payload.supplemental_live_checks;
 assert.equal(supplemental.mapped_claims.length,20);
 assert.deepEqual(supplemental.summary,{host_checks:20,cli_checks:21,api_checks:6,total_checks:47,
  note:'Six direct API reads: three Market Metrics endpoints plus selected-machine, maintenance and reports reads. Only the three Market Metrics endpoint-description claims have separate API PASS adjudications. All 15 documented Market Metrics CLI examples also ran; those are separate command observations, not additional API-claim closures.'});
 assert.deepEqual(payload.counts.claim_statuses,model.counts.claim_statuses);
 const hardware=supplemental.mapped_claims.find(c=>c.claim_id==='MCL-a43d2c31e8cfcd4f');
 assert.equal(hardware.coverage.level,'PARTIAL');assert.equal(hardware.checks.length,9);
 const market=supplemental.mapped_claims.filter(c=>c.route==='/host/market-metrics');
 assert.deepEqual(market.map(c=>c.checks.length),[3,7,5]);
 assert.equal(market.reduce((total,c)=>total+c.checks.length,0),15);
 for(const record of supplemental.mapped_claims){
  assert.ok(!('status' in record));assert.ok(!('baseline_status' in record));
  for(const check of record.checks)assert.ok(payload.files[check.artifact_ref],check.artifact_ref);
 }
 assert.ok(payload.files['verification/evidence/2026-09-08-host-live-readonly-attempt-01/check-to-claim-map.json']);
});
test('supplemental map rejects current source-text drift',()=>{
 const original=fs.readFileSync;
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-live-readonly-attempt-01/check-to-claim-map.json')){
   const map=JSON.parse(original(file,'utf8'));map.records[0].text+=' drift';return Buffer.from(JSON.stringify(map));
  }
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Supplemental source text\/span drift/);}finally{fs.readFileSync=original;}
});
test('current read-only map binds exact claims and capture digests without adjudicating status',()=>{
 const current=payload.current_readonly_checks;
 assert.equal(current.mapped_claims.length,8);
 assert.equal(payload.current_result_ref,'verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/result.md');
 assert.equal(payload.claim_correction_history_ref,'verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/result.md');
 assert.equal(payload.historical_summary_ref,'verification/evidence/2026-09-08-host-client-unblocking-attempt-01/result.md');
 assert.equal(payload.earlier_baseline_summary_ref,'verification/evidence/2026-09-07-host-current-vv-attempt-01/result.md');
 assert.match(current.summary,/do not grant paid, self-test or VM-mutation authority/i);
 for(const record of current.mapped_claims){
  const claim=inputClaims.find(c=>c.id===record.claim_id);
  assert.ok(claim,record.claim_id);assert.ok(!('status' in record));assert.ok(!('baseline_status' in record));
  assert.equal(record.route,model.pages.find(p=>p.claims.some(c=>c.id===record.claim_id)).route);
  for(const check of record.checks)assert.ok(payload.files[check.artifact_ref],check.artifact_ref);
 }
 const defaultSearch=current.mapped_claims.find(c=>c.claim_id==='MCL-728ef13be833d21e');
 assert.deepEqual(defaultSearch.checks.map(c=>c.id),['HOST-05','CLIENT-03']);
 const rawSearch=current.mapped_claims.find(c=>c.claim_id==='MCL-a54378e7f20b92e9');
 assert.deepEqual(rawSearch.checks.map(c=>c.id),['HOST-06','CLIENT-04','CLIENT-07']);
 const local=current.mapped_claims.find(c=>c.claim_id==='MCL-9ad33b25fd88c5cb');
 assert.match(local.limit,/0644/);assert.match(local.limit,/No real credential/i);
 assert.equal(current.mapped_claims.some(c=>c.claim_id==='MCL-dfebca7edafe9c59'),false);
 const off=current.historical_superseded.find(c=>c.historical_claim_id==='MCL-dfebca7edafe9c59');
 assert.equal(off.status,'FAIL');assert.match(off.limit,/inconclusive/i);assert.doesNotMatch(off.limit,/VM support is disabled\.$/);
 assert.match(off.context,/Historical FAIL retained/);assert.equal(off.transition_ref,'verification/current-two-defect-transition.json');
 const vmCheck=current.mapped_claims.find(c=>c.claim_id==='MCL-53020aef5be19505');
 assert.equal(vmCheck.route,'/host/vms');assert.ok(!('status' in vmCheck));
 assert.match(html,/Historical VM finding \(FAIL\):/);assert.match(html,/historical context only; it does not prove VM support is disabled or bind to the corrected current wording/);
 const retry=current.mapped_claims.find(c=>c.claim_id==='MCL-60ec9280a68ab6d7');
 assert.match(retry.coverage.level,/PARTIAL_NOT_POST_ENABLE/);
 for(const ref of ['account-observations-01.json','vm-helper-source-retest-02.json','local-key-storage-limitations-02.json'])assert.ok(payload.files[`verification/evidence/2026-09-08-host-client-unblocking-attempt-01/${ref}`]);
});
test('current bounded result is explicit and the prior claim-correction result remains dated history',()=>{
 const latest='verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01';
 assert.ok(payload.files[`${latest}/result.md`]);
 const correction='verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01';
 assert.ok(payload.files[`${correction}/result.md`]);
 const sep8=fs.readFileSync(new URL('../verification/evidence/2026-09-08-host-client-unblocking-attempt-01/result.md',import.meta.url),'utf8');
 const [,python8,current8,initialJs8,legacy8]=sep8.match(/Final full Python suite: (\d+) passed\. Final current-review and HTML tests: (\d+) passed\. The initial full JavaScript run also passed all (\d+) tests, including (\d+) unchanged legacy review-context tests\./);
 assert.deepEqual([python8,current8,initialJs8,legacy8],['142','29','64','35']);
 const sep7=fs.readFileSync(new URL('../verification/evidence/2026-09-07-host-current-vv-attempt-01/result.md',import.meta.url),'utf8');
 const [,python7,legacy7,current7]=sep7.match(/\[(\d+) Python tests\].*\[(\d+) review-context tests\].*\[(\d+) current-package integrity tests\]/);
 assert.deepEqual([python7,legacy7,current7],['124','35','9']);
 assert.match(html,/Bounded operational evidence/);
 assert.match(html,/Dated September 9 claim-correction history/);
 assert.match(html,/retained 176 Python \/ 81 reviewer suite predates this bounded operational result/);
 assert.match(html,/Historical September 8 client-unblocking follow-up/);
 assert.match(html,new RegExp(`It recorded ${python8} full Python tests, ${current8} final current-review/HTML tests, and an initial ${initialJs8}-test JavaScript run that included ${legacy8} unchanged legacy review-context tests`));
 assert.match(html,new RegExp(`The ${python7} Python, ${legacy7} review-context and ${current7} current-package checks below belong to the September 7 result`));
 assert.ok(payload.files['verification/evidence/2026-09-07-host-current-vv-attempt-01/reviewer-failure-and-retest-chain.md']);
 assert.match(html,/See current result/);
 assert.match(html,/Open the dated claim-correction result/);
});

test('HTML payload keeps all six current connection rows exact and the historical search refs visible',()=>{
 const rows=new Map(payload.claims.filter(c=>[
  'COR-01-MCL-323c8fb8180f5f62-REPLACEMENT','MCL-4c49eaf437cfa29e','MCL-1ebb3e6e2b370757',
  'MCL-3fb43d8a410371df','MCL-da591d84b7d08317','MCL-eeaf6da83da9eca7',
 ].includes(c.id)).map(c=>[c.id,c]));
 assert.deepEqual([...rows].map(([id,c])=>[id,c.status]).sort(),[
  ['COR-01-MCL-323c8fb8180f5f62-REPLACEMENT','PASS'],['MCL-4c49eaf437cfa29e','PASS'],
  ['MCL-1ebb3e6e2b370757','BLOCKED'],['MCL-3fb43d8a410371df','UNVALIDATED'],
  ['MCL-da591d84b7d08317','UNVALIDATED'],['MCL-eeaf6da83da9eca7','BLOCKED'],
 ].sort());
 const search=rows.get('COR-01-MCL-323c8fb8180f5f62-REPLACEMENT');
 assert.equal(search.history.carry_decision,'CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION');
 assert.ok(search.evidence_refs.some(r=>r.id==='CLI-QUERY-SOURCE-INSPECTION-01'));
 assert.ok(search.evidence_refs.some(r=>r.id==='CONNECTION-COR-01-MCL-323c8fb8180f5f62-REPLACEMENT-01'));
 for(const row of rows.values())assert.ok(row.evidence_refs.some(r=>r.artifact_ref==='verification/current-host-connection-adjudications.json'));
});
test('current read-only map rejects source and capture drift',()=>{
 const original=fs.readFileSync;
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-client-unblocking-attempt-01/check-to-claim-map.json')){
   const map=JSON.parse(original(file,'utf8'));map.records[0].headings=['drift'];return Buffer.from(JSON.stringify(map));
  }
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Current source text\/span drift/);}finally{fs.readFileSync=original;}
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/evidence/2026-09-08-host-client-unblocking-attempt-01/cli-execution-01.json'))return Buffer.from('{"records":[]}');
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Current capture hash drift/);}finally{fs.readFileSync=original;}
 fs.readFileSync=(file,...args)=>{
  if(String(file).endsWith('/verification/current-two-defect-transition.json'))return Buffer.from(`${original(file,'utf8')}\n`);
  return original(file,...args);
 };
 try{assert.throws(()=>buildReport(),/Two-defect transition registry hash drift/);}finally{fs.readFileSync=original;}
});
test('offline inventory summary takes current counts from the embedded payload',()=>{
 const template=fs.readFileSync(new URL('./templates/host-docs-review.html',import.meta.url),'utf8');
 assert.match(template,/id="inventory-summary"/);
 assert.match(template,/report\.counts\.procedures/);assert.match(template,/report\.counts\.procedure_nodes/);
 assert.match(template,/report\.counts\.page_coverage_states\?\.CHANGED/);
 assert.doesNotMatch(template,/110 procedure records \/ 1,047 nodes/);
 assert.match(template,/Evidence update: 9 Sep 2026/);
 assert.match(template,/Updated 9 Sep 2026/);
 assert.match(template,/At the 8 Sep 2026 check/);
 assert.doesNotMatch(template,/signed payload/);
});
test('route and accessibility reconciliation is embedded, bounded, and readable',()=>{
 const attempt='verification/evidence/2026-09-09-host-repository-live-merge-attempt-01';
 const refs={
  generated_routes_ref:`${attempt}/generated-route-reconciliation-01.json`,
  mint_links_ref:`${attempt}/mint-links-post-exclusion-02.json`,
  mint_accessibility_ref:`${attempt}/mint-a11y-retest-01.json`,
  rendered_theme_ref:`${attempt}/rendered-theme-token-01.json`,
 };
 assert.deepEqual(payload.repository_reconciliation,refs);
 for(const ref of Object.values(refs))assert.ok(payload.files[ref],ref);
 const routes=JSON.parse(fs.readFileSync(new URL('../'+refs.generated_routes_ref,import.meta.url),'utf8'));
 const routeReport=JSON.parse(routes.stdout);
 assert.equal(routes.exit_code,0);assert.equal(routeReport.reportedTargetCount,85);
 assert.ok(routeReport.results.every(result=>result.status===200&&result.finalUrlMatchesCanonical&&result.canonicalTitleMatches&&result.passed));
 assert.equal(routeReport.negativeControl.status,404);assert.equal(routeReport.negativeControl.passed,true);
 const links=JSON.parse(fs.readFileSync(new URL('../'+refs.mint_links_ref,import.meta.url),'utf8'));
 assert.equal(links.exit_code,1);assert.match(links.stdout,/found 99 broken links in 10 files/i);
 const a11y=JSON.parse(fs.readFileSync(new URL('../'+refs.mint_accessibility_ref,import.meta.url),'utf8'));
 assert.equal(a11y.exit_code,1);assert.match(a11y.stdout,/4\.53:1[\s\S]*meets WCAG AA/i);assert.match(a11y.stdout,/Found 74 accessibility issues in 19 files/);
 const theme=JSON.parse(fs.readFileSync(new URL('../'+refs.rendered_theme_ref,import.meta.url),'utf8'));
 assert.equal(theme.exit_code,0);assert.deepEqual(JSON.parse(theme.stdout),{dark:true,primaryLight:'63 109 255',scope:'Rendered token adoption only; not a full accessibility audit'});
 for(const label of ['Open generated-route reconciliation','Open Mint static link report','Open accessibility retest','Open rendered color-token check'])assert.match(html,new RegExp(label));
 assert.match(html,/85 unique generated API routes/);assert.match(html,/99 generated-route findings/);assert.match(html,/4\.53:1/);assert.match(html,/74 missing-alt findings in 19 non-Host files/);
 assert.doesNotMatch(html,/99 inherited broken links/);
});
test('direct-install intake renders current bounded installation context while preserving historical pre-install cards',()=>{
 assert.match(html,/modified direct installation completed with retained warnings and failures/i);
 assert.match(html,/H100×4 direct-install observations/);
 assert.match(html,/Historical pre-install selected observation/);
 assert.match(html,/Pinned current installation context \(does not alter claim status\)/);
 assert.match(html,/four active services, four H100 GPUs, and XFS Project quota accounting\/enforcement ON/i);
 assert.match(html,/Earlier USD 1\/GB and USD 0\.10\/GB listing failures remain retained/);
 assert.match(html,/Client test instance 50364501 ran one tiny H100 result and was destroyed/);
 assert.match(payload.installation_evidence_intake.message,/USD 0\.01\/GB in both directions/);
 assert.doesNotMatch(payload.installation_evidence_intake.message,/remains unlisted/);
 assert.doesNotMatch(html,/No offer was published and no client rental was started/);
 assert.doesNotMatch(html,/waiting for sudo authentication/i);
 assert.doesNotMatch(html,/installation was not run/i);
});
test('four direct runtime adjudications select only their pinned post-install observations',()=>{
 const expected=[
  ['MCL-ead93c85c2ff4168','POST-03','GPU_INVENTORY_4_H100'],
  ['MCL-82fa8860fe3ef124','POST-01','FOUR_SERVICES_ACTIVE'],
  ['MCL-2f9f572d80e1e8f9','POST-05','DOCKER_XFS_PROJECT_QUOTA'],
  ['MCL-aa383ba37f55f306','POST-07','PROJECT_QUOTA_ON'],
 ];
 for(const [claim,post,predicate] of expected){assert.match(html,new RegExp(`${claim}.*${post}.*${predicate}`));}
 for(const label of ['View GPU visibility result','View service-status result','View Docker filesystem result','View project-quota result'])assert.ok(html.includes(label),label);
 assert.match(html,/directPostinstallRegistry/);
 assert.match(html,/if\(direct&&\(!c\.evidence_refs\.some/);
 assert.match(html,/checkId!==direct\.observationId/);
});
test('a current read-only PASS uses its current next action in either proof layer',()=>{
 // Historical maps are immutable observation records. A later current-status
 // adjudication must take precedence over their older “still adjudicate” next.
 assert.match(html,/const useCurrentNext=c\.status==='PASS'&&String\(c\.history\?\.carry_decision\|\|''\)\.startsWith\('CURRENT_HOST_READONLY_'\)/);
 assert.doesNotMatch(html,/kind==='current'&&c\.status==='PASS'/);
});
test('all evidence and source passage references are embedded with digests',()=>{
 for(const c of payload.claims){
  for(const e of c.evidence_refs)assert.ok(payload.files[e.artifact_ref],e.artifact_ref);
  for(const s of c.spans){const f=payload.files[s.source_file];assert.ok(f);assert.ok(s.start>=1&&s.end<=f.text.split('\n').length);}
 }
 for(const f of Object.values(payload.files)){
  const raw=fs.readFileSync(new URL('../'+f.ref,import.meta.url));
  assert.equal(f.sha256,hash(raw));assert.equal(f.display_sha256,hash(f.text));
  assert.equal(f.masked,raw.toString('utf8')!==f.text);
  if(f.ref.startsWith('host/')||f.ref.startsWith('snippets/'))assert.equal(raw.toString('utf8').split('\n').length,f.text.split('\n').length,'source line numbers must survive masking');
  assert.ok(!f.ref.includes('private-evidence')&&!f.ref.includes('.orchestra'));
 }
});
test('embedding is lossless JSON without executable data',()=>{
 const data=html.match(/<script id="report-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
 assert.deepEqual(JSON.parse(data),payload);
 assert.ok(!data.includes('<')&&!data.includes('>')&&!data.includes('&'));
 assert.equal((html.match(/<script\b/g)||[]).length,2);
 for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))assert.doesNotThrow(()=>new vm.Script(m[1]));
});
test('single-file report has no remote assets or network code',()=>{
 assert.doesNotMatch(html,/<(?:script|img|iframe)\b[^>]*\bsrc=/i);
 assert.doesNotMatch(html,/<link\b[^>]*\bhref=/i);
 const app=html.match(/<script>([\s\S]*?)<\/script>/)[1];
 assert.doesNotMatch(app,/\b(?:fetch|XMLHttpRequest|WebSocket|eval)\s*\(/);
 assert.match(html,/connect-src 'none'/);
});
test('display sanitizer removes selected restricted forms without changing source data',()=>{
 for(const s of ['/Users/reviewer/work/private.md','someone@internal.invalid','machine_id: 987654','10.1.2.3','Authorization: Bearer exampleCredentialValue']) assert.ok(sanitize(s).includes('[redacted'));
 assert.equal(sanitize('vastai set api-key <API_KEY>'),'vastai set api-key <API_KEY>');
 assert.equal(sanitize('http://127.0.0.1:4000'),'http://127.0.0.1:4000');
});
test('setup explains published PR versus local snapshot and nonpublic loopback review',()=>{
 for(const text of ['git fetch origin pull/185/head','git switch --detach FETCH_HEAD','npm ci','npm run dev:review','--host 127.0.0.1 --port 4000 --target http://127.0.0.1:3000','have <strong>not been pushed</strong>','Saving locally does not post to Jira or GitHub','Ctrl+C','Node.js 24'])assert.ok(html.includes(text),text);
 assert.equal(JSON.parse(fs.readFileSync(new URL('../package.json',import.meta.url))).scripts['dev:review'],'node scripts/mint-dev-loopback.mjs');
 assert.match(html,/fresh network clone\/install was not executed/);
});
test('the pending export is deterministic',()=>{
 const fresh=buildReport();
 assert.equal(fresh.html,html);
 assert.deepEqual(fresh.manifest,manifest);
});
test('generated HTML and manifest match the deterministic current export',()=>{
 assert.equal(fs.readFileSync(new URL('../verification/host-docs-review.html',import.meta.url),'utf8'),html);
 assert.deepEqual(JSON.parse(fs.readFileSync(new URL('../verification/host-docs-review-export.json',import.meta.url))),manifest);
});
