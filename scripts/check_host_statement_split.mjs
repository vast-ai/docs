// Presentation checks only. No external page, Host operation or user feedback write.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const out = process.argv[2];
assert.match(out || '', /^verification\/evidence\/2026-09-10-host-split-review-attempt-01\/split-browser-\d{2}$/);
assert(!fs.existsSync(out), 'Do not overwrite a retained attempt');
fs.mkdirSync(out);
const session = 'host-statement-split-' + crypto.randomUUID().slice(0,8);
const browser = (...args) => execFileSync('agent-browser',['--session',session,...args],{encoding:'utf8',timeout:60000,maxBuffer:5e6});
const evaluate = code => JSON.parse(browser('eval','-b',Buffer.from(code).toString('base64')));
const rows = [], started = new Date().toISOString();
try {
  browser('set','viewport','1500','1050');
  browser('open',pathToFileURL(process.cwd()+'/verification/host-docs-review.html').href);
  rows.push({surface:'offline', result:evaluate(`(() => {
    const data=JSON.parse(document.getElementById('report-data').textContent),rows=[];
    for(const c of data.claims.filter(c=>c.reader_copy?.statementText)){
      document.getElementById('clear').click();document.getElementById('search').value=c.id;
      document.getElementById('search').dispatchEvent(new Event('input'));
      const card=document.querySelector('.claim'),partial=card.querySelector('.partial');
      if(card.querySelector('h3').textContent!==normalizeWording(c.reader_copy.statementText).text)throw Error('Wrong child wording '+c.id);
      if(!partial||partial.open||card.querySelector('section.callout'))throw Error('Misleading source styling '+c.id);
      if(!card.querySelector('.raw-details pre').textContent.includes(c.text))throw Error('Lost audit '+c.id);
      card.querySelector('[data-passage]').click();
      const highlights=[...document.querySelectorAll('.source-line.highlight .number')].map(n=>Number(n.textContent));
      if(JSON.stringify(highlights)!==JSON.stringify([c.spans[1].start]))throw Error('Wrong highlighted lines '+c.id);
      document.getElementById('close-viewer').click();
      for(const button of card.querySelectorAll('[data-basis]')){
        button.click();const body=document.getElementById('viewer-body');
        if(!body.textContent.includes(c.reader_copy.sourceContextLabel)||body.querySelector('pre').textContent!==c.reader_copy.statementText)throw Error('Mixed source dialog '+c.id);
        document.getElementById('close-viewer').click();
      }
      card.querySelector('[data-related-claim]').click();
      const related=document.querySelector('#viewer-body .claim');
      if(related?.id!=='claim-'+c.reader_copy.relatedClaimId||!related.querySelector('.PASS'))throw Error('Related finding '+c.id);
      document.getElementById('close-viewer').click();
      rows.push({id:c.id,status:c.status,highlightedLines:highlights,bases:card.querySelectorAll('[data-basis]').length,related:c.reader_copy.relatedClaimId});
    }
    if(rows.length!==4)throw Error('Wrong cohort');
    document.getElementById('search').value='MCL-470bf8ec992a342e';document.getElementById('search').dispatchEvent(new Event('input'));
    document.documentElement.style.scrollBehavior='auto';
    document.getElementById('claim-list').scrollIntoView({behavior:'instant',block:'start'});return rows;
  })()`)});
  browser('screenshot',out+'/offline-end-date.png');
  browser('open','http://127.0.0.1:4000/host/hosting-overview#the-rental-contract');
  browser('wait','--fn','!!document.querySelector("#__vast_review_host__")?.shadowRoot.querySelector("#current-section-filter")');
  rows.push({surface:'localhost',result:evaluate(`(async () => {
    const shadow=document.querySelector('#__vast_review_host__').shadowRoot;
    if(!shadow.querySelector('#panel').classList.contains('open'))shadow.querySelector('#pill').click();
    const current=(await (await fetch('/__review__/api/context?path=%2Fhost%2Fhosting-overview')).json()).currentReview;
    const rows=[];
    for(const c of current.page.claims.filter(c=>c.readerCopy?.statementText)){
      const card=shadow.querySelector('[data-current-claim="'+c.id+'"]');
      const section=shadow.querySelector('#current-section-filter');section.value='';section.dispatchEvent(new Event('change',{bubbles:true}));
      const filter=shadow.querySelector('#current-citation-filter');filter.value='ALL';filter.dispatchEvent(new Event('change',{bubbles:true}));
      const partial=card.querySelector('.vv-source-partial');
      if(card.querySelectorAll('blockquote').length!==1||card.querySelector('.vv-checking')||!partial||partial.open||card.querySelector('.vv-source-transition'))throw Error('Mixed live card '+c.id);
      if(!card.querySelector('.vv-reading-audit pre').textContent.includes(c.text))throw Error('Lost live audit '+c.id);
      card.querySelector('[data-show-current-claim]').click();
      const ranges=[...(CSS.highlights.get('vast-review-claim')||[])].map(r=>r.toString());
      if(!ranges.length||ranges.some(r=>r.includes('When editing an offer')))throw Error('Mixed page highlighting '+c.id);
      const basisLinks=[...partial.querySelectorAll('a')];
      for(const link of basisLinks){const response=await fetch(link.href),text=await response.text();if(!response.ok||!text.includes(c.readerCopy.sourceContextLabel)||!text.includes('Full recorded wording'))throw Error('Live source context '+c.id);}
      filter.value='CITATION';filter.dispatchEvent(new Event('change',{bubbles:true}));
      card.querySelector('[data-related-current-claim]').click();
      const parent=shadow.querySelector('[data-current-claim="'+c.readerCopy.relatedClaimId+'"]');
      if(parent.hidden||parent.querySelector('[data-status]').dataset.status!=='PASS'||filter.value!=='ALL'||shadow.activeElement!==parent.querySelector('[data-show-current-claim]'))throw Error('Related live finding hidden '+c.id);
      rows.push({id:c.id,status:c.status,ranges,bases:basisLinks.length,related:c.readerCopy.relatedClaimId});
    }
    if(rows.length!==4)throw Error('Wrong live cohort');
    const card=shadow.querySelector('[data-current-claim="MCL-470bf8ec992a342e"]');
    card.scrollIntoView({block:'start'});card.querySelector('[data-show-current-claim]').click();
    return rows;
  })()`)});
  browser('screenshot',out+'/localhost-end-date.png');
} catch(error) { rows.push({status:'FAIL',error:String(error.message).replaceAll(process.cwd(),'<DOCS_REPO>')}); process.exitCode=1; }
finally {
  try {browser('close');}catch{}
  const result={started,finished:new Date().toISOString(),status:process.exitCode?'FAIL':'PASS',scope:'Four split reviewer cards and related existing source-only PASS; no runtime or claim adjudication.',rows};
  fs.writeFileSync(out+'/result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}
