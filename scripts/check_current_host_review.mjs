// Loopback-only browser audit of the additive current Host review package.
// Clicks review controls, never documentation commands or external links.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (name, fallback) => {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
};
const origin = new URL(arg('--origin', 'http://127.0.0.1:4000'));
if (origin.protocol !== 'http:' || !['127.0.0.1', 'localhost', '[::1]'].includes(origin.hostname) ||
    origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) {
  throw new Error('Only an HTTP loopback origin is supported');
}
const out = path.resolve(root, arg('--out', ''));
if (!arg('--out') || !out.startsWith(path.join(root, 'verification/evidence/'))) throw new Error('Use an evidence output directory');
fs.mkdirSync(out, { recursive: true });
const save = (name, value) => fs.writeFileSync(path.join(out, name), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex');
const packageFile = 'verification/current-host-docs-review.json';
const inventory = JSON.parse(fs.readFileSync(path.join(root, packageFile)));
const allRoutes = inventory.pages.map(page => page.route);
const selected = arg('--routes') ? arg('--routes').split(',') : allRoutes;
if (new Set(selected).size !== selected.length || selected.some(route => !allRoutes.includes(route))) throw new Error('Unknown/duplicate selected route');
const session = arg('--session', 'current-host-review');
const serverHash = hash('review-server.mjs');
const packageHash = hash(packageFile);
const browser = (...args) => execFileSync('agent-browser', ['--session', session, ...args], {
  encoding: 'utf8', cwd: root, timeout: 60000, maxBuffer: 20 * 1024 * 1024,
});
const evaluate = js => JSON.parse(browser('eval', '-b', Buffer.from(js).toString('base64')));
const api = async route => {
  const response = await fetch(new URL('/__review__/api/context?path=' + encodeURIComponent(route), origin));
  if (!response.ok || response.headers.get('x-vast-review-source-sha256') !== serverHash) throw new Error('Running server source mismatch');
  return response.json();
};
save('metadata.json', { started: new Date().toISOString(), origin: origin.origin, serverHash, packageHash,
  selected, population: allRoutes.length, method: 'Real rendered pages; section filters, exact-text locator, status fidelity, local heading links',
  limits: 'Browser interface only. No Host, API, network-probe, workload, or owner validation.' });
const results = [];
try {
  browser('set', 'viewport', '1600', '1000');
  for (const route of selected) {
    try {
      const context = await api(route);
      if (!context.currentReview?.available || !context.currentReview.page?.claims?.length) throw new Error('Current claim package unavailable');
      browser('open', origin.origin + route);
      browser('wait', '--fn', '!!document.querySelector("#__vast_review_host__")?.shadowRoot.querySelector("#current-section-filter")');
      const observation = evaluate(`(async () => {
        const shadow = document.querySelector('#__vast_review_host__').shadowRoot;
        const response = await fetch('/__review__/api/context?path=' + encodeURIComponent(location.pathname));
        if (response.headers.get('x-vast-review-source-sha256') !== ${JSON.stringify(serverHash)}) throw new Error('Server changed during check');
        const current = (await response.json()).currentReview;
        if (!current.available) throw new Error('Current review unavailable');
        if (!shadow.querySelector('#panel').classList.contains('open')) shadow.querySelector('#pill').click();
        const section = shadow.querySelector('.vv-current-reading');
        const filter = section.querySelector('#current-section-filter');
        const filters = [];
        for (const option of [...filter.options]) {
          filter.value = option.value; filter.dispatchEvent(new Event('change', { bubbles: true }));
          const actual = [...section.querySelectorAll('[data-current-claim]:not([hidden])')].map(el => el.dataset.currentClaim);
          const expected = current.page.claims.filter(claim => !option.value || claim.headings.includes(option.value)).map(claim => claim.id);
          filters.push({ heading: option.value, expected: expected.length, actual: actual.length, pass: JSON.stringify(expected) === JSON.stringify(actual) });
        }
        filter.value = ''; filter.dispatchEvent(new Event('change', { bubbles: true }));
        const queue=current.workQueue, queueFilters=[];
        if(!queue||queue.total!==current.page.claims.length||queue.buckets.reduce((sum,b)=>sum+b.count,0)!==queue.total)throw new Error('Incomplete page-local queue');
        for(const bucket of queue.buckets){const control=section.querySelector('#current-work-filter');control.value=bucket.id;control.dispatchEvent(new Event('change',{bubbles:true}));
          const actual=[...section.querySelectorAll('[data-current-claim]:not([hidden])')].map(el=>el.dataset.currentClaim);
          const expected=current.page.claims.filter(claim=>claim.reviewWork.bucket===bucket.id).map(claim=>claim.id);
          queueFilters.push({category:bucket.id,count:bucket.count,pass:bucket.count===actual.length&&JSON.stringify(actual)===JSON.stringify(expected)});}
        const workFilter=section.querySelector('#current-work-filter');workFilter.value='';workFilter.dispatchEvent(new Event('change',{bubbles:true}));
        const grouped=queue.groups.flatMap(group=>group.occurrenceIds);
        if(grouped.length!==queue.total||new Set(grouped).size!==queue.total)throw new Error('Shared-wording index lost passages');
        const claims = [];
        for (const claim of current.page.claims) {
          const card = [...section.querySelectorAll('[data-current-claim]')].find(el => el.dataset.currentClaim === claim.id);
          CSS.highlights.delete('vast-review-claim');
          const notice = section.querySelector('#current-location-notice');
          if (notice) notice.textContent = '';
          card?.querySelector('[data-show-current-claim]')?.click();
          const ranges = [...(CSS.highlights.get('vast-review-claim') || [])].map(range => range.toString());
          const links = [...(card?.querySelectorAll('.vv-reading-actions a') || [])].map(link => {
            const url = new URL(link.href); const anchor = decodeURIComponent(url.hash.slice(1));
            return { href: url.pathname + url.hash, exists: url.pathname === location.pathname && (!anchor || !!document.getElementById(anchor)) };
          });
          claims.push({ id: claim.id, headings: claim.headings, status: claim.status,
            cardStatus: card?.querySelector('[data-status]')?.dataset.status,
            readerCopyMatches: !!claim.readerCopy && card?.querySelector('.vv-reader-finding')?.textContent === claim.readerCopy.label + ': ' + claim.readerCopy.finding && card?.querySelector('.vv-reader-next')?.textContent === 'Next step: ' + claim.readerCopy.nextStep &&
              (!claim.readerCopy.statusLabel || card?.textContent.includes(claim.readerCopy.statusLabel)) &&
              card?.querySelector('.vv-reading-status')?.textContent === claim.reviewWork?.statusLabel &&
              card?.textContent.includes('Review type: ' + claim.reviewWork?.type) &&
              (!claim.readerCopy.pendingNote || card?.querySelector('.vv-policy-pending')?.textContent.includes(claim.readerCopy.pendingNote)) &&
              !!card?.querySelector('.vv-reading-audit')?.textContent.includes('Recorded status: ' + claim.status),
            checkingSummaryCount: card?.querySelectorAll('.vv-checking').length,
            passages: [...(card?.querySelectorAll('blockquote') || [])].map(el => el.textContent),
            ranges, notice: notice?.textContent || '', masked: !!claim.sourcePassages?.some(p => p.redacted), links,
            hasButton: !!card?.querySelector('[data-show-current-claim]'),
            evidenceLinks: [...(card?.querySelectorAll('a[href*="/__review__/evidence"],a[href*="/__review__/current-artifact"]') || [])].map(a => a.getAttribute('href')) });
        }
        return { route: location.pathname, currentAvailable: current.available, claims, filters, queueFilters, queue,
          cardCount: section.querySelectorAll('[data-current-claim]').length,
          emptyControls: [...section.querySelectorAll('button,a,select')].filter(el => !el.textContent.trim() && !el.getAttribute('aria-label')).length };
      })()`);
      save(route.split('/').at(-1) + '.json', observation);
      const failed = observation.claims.filter(claim => !claim.hasButton || !claim.readerCopyMatches || claim.status !== claim.cardStatus ||
        (claim.id === 'MCL-790d76c6e2bea8fa' && claim.checkingSummaryCount !== 0) ||
        !claim.links.length || claim.links.some(link => !link.exists) ||
        (!claim.ranges.length && !(claim.masked && /mask/i.test(claim.notice))));
      const row = { route, claims: observation.claims.length, located: observation.claims.filter(c => c.ranges.length).length,
        maskedFallback: observation.claims.filter(c => !c.ranges.length && c.masked && /mask/i.test(c.notice)).length,
        failed: failed.map(c => ({ id: c.id, notice: c.notice, links: c.links })),
        pass: !failed.length && observation.filters.every(f => f.pass) && observation.queueFilters.every(f => f.pass) && !observation.emptyControls && observation.cardCount === observation.claims.length };
      results.push(row); console.log(JSON.stringify(row));
    } catch (error) {
      const row = { route, pass: false, error: String(error.message).slice(0, 1500) };
      results.push(row); save(route.split('/').at(-1) + '-error.json', row); console.log(JSON.stringify(row));
    }
  }
} finally {
  try { browser('close'); } catch {}
  const unchanged = hash('review-server.mjs') === serverHash && hash(packageFile) === packageHash;
  save('summary.json', { finished: new Date().toISOString(), unchanged, results,
    pass: unchanged && results.length === selected.length && results.every(row => row.pass) });
  if (!unchanged || results.some(row => !row.pass)) process.exitCode = 1;
}
