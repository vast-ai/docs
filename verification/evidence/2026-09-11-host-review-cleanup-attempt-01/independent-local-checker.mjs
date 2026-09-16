import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const ref=process.argv[2];
const raw=fs.readFileSync(ref),record=JSON.parse(raw);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const baseline=JSON.parse(fs.readFileSync('verification/evidence/2026-09-11-host-review-cleanup-attempt-01/before-current-host-docs-review.json'));
const claims=new Map(baseline.pages.flatMap(p=>p.claims.map(c=>[c.id,c])));
const slug=s=>s.toLowerCase().replace(/<[^>]+>/g,'').replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-');
const observations=[];
for(const row of record.results){
 const source=fs.readFileSync(row.source_file),claim=claims.get(row.claim_id);
 assert.equal(sha(source),row.source_sha256);assert(claim);
 if(row.kind==='EXECUTED_LOCAL_REPOSITORY_NAVIGATION_CHECK'){
  const hrefs=[...claim.text.matchAll(/\]\(([^)]+)\)/g)].map(x=>x[1]);
  const exactHref=x=>x.href.split('#')[0]+(x.fragment?'#'+x.fragment:'');
  assert.deepEqual(row.checks.map(exactHref).sort(),hrefs.sort());
  for(const check of row.checks){
   const u=new URL(exactHref(check),'http://local/'+row.source_file.replace(/\.mdx$/,''));
   assert.equal(u.host,'local');
   const destination=u.pathname.slice(1)+'.mdx';assert.equal(destination,check.resolved_path);
   const text=fs.readFileSync(destination,'utf8');
   const headingLines=text.split('\n').filter(x=>/^#{1,6} /.test(x)).map(x=>x.replace(/^#{1,6} /,''));
   const ids=[...text.matchAll(/\bid=["']([^"']+)["']/g)].map(x=>x[1]);
   if(u.hash)assert([...headingLines.map(slug),...ids].includes(decodeURIComponent(u.hash.slice(1))),check.href);
   observations.push({claim_id:row.claim_id,href:check.href,destination,sha256:sha(text),headings:headingLines,result:'PASS'});
  }
 }else if(row.kind==='EXECUTED_LOCAL_REPOSITORY_SECTION_CHECK'){
  assert.equal(row.target.resolved_path,row.source_file);
  assert(source.toString().split('\n').some(l=>l.replace(/^#{1,6} /,'').trim()===row.target.heading));
  observations.push({claim_id:row.claim_id,heading:row.target.heading,result:'PASS'});
 }else if(row.kind==='EXECUTED_LOCAL_ARITHMETIC_CHECK'){
  const operands=row.check.operands;
  for(const operand of operands)assert(claim.text.includes(operand));
  const number=operands.reduce((n,x)=>n*Number(x),1);
  const display=row.check.expected_display;
  assert(Math.abs(number-Number(display.replaceAll(',','')))<1e-8);
  assert(claim.text.includes(display));
  observations.push({claim_id:row.claim_id,operands,computed:number,display,result:'PASS'});
 }else{
  assert.equal(row.kind,'CONTEXTUAL_STATIC_FORMULA_INSPECTION');assert.equal(row.executed,false);
  assert(claim.text.includes('rentable GPUs x hourly GPU price x 720 x utilization'));
  observations.push({claim_id:row.claim_id,method:'Literal symbolic-factor inspection only',result:'PASS',executed_formula:false});
 }
}
assert.equal(record.results.length,45);
console.log(JSON.stringify({status:'PASS',input_sha256:sha(raw),records:record.results.length,observations,limits:'Independent local source/destination/arithmetic recheck. Not runtime behavior, current market rates, financial authority or human acceptance.'},null,2));
