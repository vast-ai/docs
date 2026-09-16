import fs from 'node:fs';import crypto from 'node:crypto';import {execFileSync,spawn} from 'node:child_process';
const dir='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01',name=process.argv[2];
if(!/^final-audit-[0-9]+$/.test(name))throw Error('Unique audit name required');
const file=dir+'/'+name+'.json';if(fs.existsSync(file))throw Error('Refuse overwrite');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p));
const git=args=>execFileSync('git',args,{encoding:'utf8'}).trim();
const gitHash=args=>new Promise((resolve,reject)=>{const h=crypto.createHash('sha256'),p=spawn('git',args);p.stdout.on('data',b=>h.update(b));p.on('error',reject);p.on('close',c=>c===0?resolve(h.digest('hex')):reject(Error('git exited '+c)));});
const canon=x=>JSON.stringify(sort(x)),sort=x=>Array.isArray(x)?x.map(sort):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x;
const baseline=read(dir+'/baseline.json'),before=read(dir+'/pre-correction-model.json'),after=read('verification/current-host-docs-review.json');
const claims=m=>new Map(m.pages.flatMap(p=>p.claims.map(c=>[c.id,c]))),old=claims(before),now=claims(after);
const expected=['MCL-e2b956d14494e470','MCL-df7b287adb0df683','MCL-5936430d1b2d8de9','MCL-bbd64c772e9b4693','MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4'].sort();
const changed=[...old].filter(([id,c])=>canon(c)!==canon(now.get(id))).map(([id])=>id).sort();
const oldLines=fs.readFileSync(dir+'/pre-correction-payment.mdx','utf8').split('\n'),newLines=fs.readFileSync('host/payment.mdx','utf8').split('\n');
const lineChanges=oldLines.flatMap((s,i)=>s===newLines[i]?[]:[i+1]);
const prior=baseline.files.filter(f=>f.path.startsWith('verification/evidence/')&&!f.path.startsWith(dir+'/')&&f.type==='file');
const priorDrift=prior.filter(f=>!fs.existsSync(f.path)||sha(fs.readFileSync(f.path))!==f.sha256).map(f=>f.path);
const agreementIds=['MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4'];
const source=dir+'/published-invoice-guidance-01.json',sourceHash=sha(fs.readFileSync(source)),page=after.pages.find(p=>p.route==='/host/payment');
const checks={
 sameHead:git(['rev-parse','HEAD'])===baseline.head,
 sameIndex:await gitHash(['diff','--cached','--binary'])===baseline.index_diff_sha256,
 exactInventory:old.size===2013&&now.size===2013&&[...old.keys()].every(id=>now.has(id)),
 exactChanges:canon(changed)===canon(expected),
 fourFailuresAndTwoPending:expected.filter(id=>old.get(id).status==='FAIL').length===4&&expected.filter(id=>old.get(id).status==='UNVALIDATED').length===2,
 counts:canon(after.counts.claim_statuses)===canon({PASS:319,FAIL:26,BLOCKED:23,NOT_APPLICABLE:87,UNVALIDATED:1558}),
 sixScopedPass:expected.every(id=>now.get(id)?.status==='PASS'&&/published|guidance/i.test(now.get(id).text)),
 exactSourceLines:oldLines.length===newLines.length&&canon(lineChanges)===canon([53,54,55,58,84,106]),
 priorEvidenceUnchanged:priorDrift.length===0,
 sourceUnchanged:sourceHash==='9e4a9ff965510e9c08f6c45c929ab5a180d882e7dfe6c14bd65b7b30cef5814c',
 publicationBindings:expected.every(id=>now.get(id).source_refs.some(r=>r.path.startsWith('https://docs.vast.ai/host/payment#')&&r.revision==='sha256:'+sourceHash)),
 agreementPreserved:agreementIds.every(id=>old.get(id).source_refs.every(r=>now.get(id).source_refs.some(x=>canon(x)===canon(r)))),
 sourceSpans:page.claims.every(c=>c.spans.every(s=>s.text_sha256===sha(newLines.slice(s.start-1,s.end).join('\n')))),
 pageHash:page.source_sha256===sha(fs.readFileSync('host/payment.mdx')),
 noUnsupportedTiming:!newLines.join('\n').includes('12:00 PM Pacific')&&!newLines.join('\n').includes('2 to 4 weeks'),
 preservedProviderAndTerms:['MCL-06956d724f70d2a3','MCL-9826b26393329d27','MCL-77f72f0e0ac77e54','MCL-a04f3ef2f5a7d5fd','MCL-cc62439b0f816902'].every(id=>canon(old.get(id))===canon(now.get(id)))
};
const result={recorded_at:new Date().toISOString(),result:Object.values(checks).every(Boolean)?'PASS':'FAIL',checks,changed_claims:changed,unchanged_claims:old.size-changed.length,source_line_changes:lineChanges,prior_evidence_files:prior.length,prior_drift:priorDrift,counts:after.counts,model_sha256:sha(fs.readFileSync('verification/current-host-docs-review.json')),payment_sha256:sha(fs.readFileSync('host/payment.mdx')),html_sha256:sha(fs.readFileSync('verification/host-docs-review.html')),limitations:'Repository integrity and source-binding checks only; not execution of invoices, payments or reviewer acceptance.'};
fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({artifact:file,result:result.result,checks,unchanged:result.unchanged_claims,priorEvidence:prior.length}));process.exitCode=result.result==='PASS'?0:1;
