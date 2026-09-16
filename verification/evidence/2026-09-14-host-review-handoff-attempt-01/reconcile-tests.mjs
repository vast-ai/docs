import fs from 'node:fs';
const dir='verification/evidence/2026-09-14-host-review-handoff-attempt-01';
const refs=['reader-regression-01.json','reader-focused-retest-02.json','reader-final-core.json','historical-fixtures-retest.json'];
const alias=name=>name==='sealed cleanup projects the actual current 151-transition model'?'sealed cleanup projects the pinned 151-transition model':name;
const outcomes=new Map(),runs=[];
for(const ref of refs){const record=JSON.parse(fs.readFileSync(dir+'/'+ref));let n=0;for(const line of record.stdout.split('ℹ tests')[0].split('\n')){const match=line.match(/^([✔✖]) (.+) \([0-9.]+ms\)$/);if(!match)continue;n++;const name=alias(match[2]);if(!outcomes.has(name))outcomes.set(name,[]);outcomes.get(name).push({ref,status:match[1]==='✔'?'PASS':'FAIL'});}runs.push({ref,exit_code:record.exit_code,recorded_cases:n});}
const results=[...outcomes].map(([name,attempts])=>({name,attempts,status:attempts.at(-1).status}));
const unresolved=results.filter(row=>row.status!=='PASS');
const result={at:new Date().toISOString(),result:results.length===209&&!unresolved.length?'PASS':'FAIL',unique_cases:results.length,runs,unresolved,results,limits:'Coverage across the retained full run and focused retests, not a claim that one final full run passed. One test was renamed to identify its pinned historical model; the exact 151-transition and model-equality assertions remain. Browser checks separately bind the final loaded server SHA. No Host claim status is changed.'};
fs.writeFileSync(dir+'/test-outcome-reconciliation.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({result:result.result,unique_cases:results.length,runs,unresolved}));process.exitCode=result.result==='PASS'?0:1;
