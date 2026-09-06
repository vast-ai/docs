#!/usr/bin/env node
// Retained, loopback-only browser audit. This never executes documented commands.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (key, fallback) => {
  const index = process.argv.indexOf(key);
  return index < 0 ? fallback : process.argv[index + 1];
};
const origin = new URL(arg('--origin', 'http://127.0.0.1:4000'));
if (origin.protocol !== 'http:' || !['127.0.0.1', 'localhost', '[::1]'].includes(origin.hostname) ||
    origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) {
  throw new Error('Only an HTTP loopback origin is supported.');
}
const shard = Number(arg('--shard', '0'));
const shards = Number(arg('--shards', '1'));
if (!Number.isInteger(shard) || !Number.isInteger(shards) || shard < 0 || shard >= shards) throw new Error('Invalid shard');
const session = arg('--session', `host-reading-${shard}`);
const out = path.resolve(arg('--out', ''));
if (!arg('--out') || !out.startsWith(path.join(root, 'verification/evidence/'))) throw new Error('An evidence output directory is required');
fs.mkdirSync(out, { recursive: true });
const write = (name, data) => fs.writeFileSync(path.join(out, name), JSON.stringify(data, null, 2) + '\n', { flag: 'wx' });
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex');
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const inventory = JSON.parse(fs.readFileSync(path.join(root, 'verification/host-docs-test-sets.json')));
const routes = inventory.pages.map(page => page.route).sort().filter((_, index) => index % shards === shard);
const requested = arg('--routes');
const requestedRoutes = requested ? requested.split(',') : null;
if (requestedRoutes && (new Set(requestedRoutes).size !== requestedRoutes.length || requestedRoutes.some(route => !routes.includes(route)))) {
  throw new Error('Requested routes must be unique inventory routes belonging to this shard; none may be silently omitted.');
}
const selected = requestedRoutes || routes;
if (!selected.length) throw new Error('No selected pages');
const sourceHash = hash('review-server.mjs');
const identityResponse = await fetch(new URL('/__review__/api/context?path=' + encodeURIComponent(selected[0]), origin));
const servedSourceHash = identityResponse.headers.get('x-vast-review-source-sha256');
const sourceIdentityMatches = identityResponse.ok && servedSourceHash === sourceHash;
write(`metadata-${shard}.json`, { started: new Date().toISOString(), origin: origin.origin,
  method: 'agent-browser real local pages; activate each rendered Show on page button; inspect CSS ranges and notices',
  gitHead: git('rev-parse', 'HEAD'), gitStatus: git('status', '--short'),
  reviewServerSha256: sourceHash, servedSourceSha256: servedSourceHash, sourceIdentityMatches,
  runnerSha256: hash('scripts/check_host_review_reading.mjs'),
  inventorySha256: hash('verification/host-docs-test-sets.json'), shard, shards, routes: selected });
if (!sourceIdentityMatches) {
  write(`summary-${shard}.json`, { result: 'FAIL', reason: 'Running review server does not identify the current source. Restart it before auditing.',
    servedSourceSha256: servedSourceHash, expectedSourceSha256: sourceHash, results: [] });
  console.error('Running review server source mismatch; no browser results attributed to this source.');
  process.exit(1);
}

const browser = (...args) => execFileSync('agent-browser', ['--session', session, ...args], {
  cwd: root, encoding: 'utf8', timeout: 90000, maxBuffer: 12 * 1024 * 1024,
});
const evaluate = script => JSON.parse(browser('eval', '-b', Buffer.from(script).toString('base64')));
const results = [];
try {
  browser('set', 'viewport', '1600', '1000');
  for (const route of selected) {
    const started = new Date().toISOString();
    try {
      browser('open', origin.origin + route);
      browser('wait', '--fn', `!!document.querySelector('#__vast_review_host__')?.shadowRoot.querySelector('.vv-reading')`);
      const observation = evaluate(`(async () => {
        const shadow = document.querySelector('#__vast_review_host__').shadowRoot;
        const response = await fetch('/__review__/api/context?path=' + encodeURIComponent(location.pathname));
        if (response.headers.get('x-vast-review-source-sha256') !== ${JSON.stringify(sourceHash)}) throw new Error('Served source changed during audit');
        const context = await response.json();
        const vv = context.verification;
        if (!shadow.querySelector('#panel').classList.contains('open')) shadow.querySelector('#pill').click();
        const filter = shadow.querySelector('#vv-section-filter');
        filter.value = ''; filter.dispatchEvent(new Event('change', { bubbles: true }));
        const filters = [];
        for (const option of [...filter.options]) {
          filter.value = option.value; filter.dispatchEvent(new Event('change', { bubbles: true }));
          const visible = [...shadow.querySelectorAll('[data-review-claim]:not([hidden])')].map(el => el.dataset.reviewClaim);
          const expected = vv.materialClaims.filter(c => !option.value || c.checkedContent.sections.includes(option.value)).map(c => c.id);
          filters.push({ section: option.value, count: visible.length, matches: JSON.stringify(visible) === JSON.stringify(expected) });
        }
        filter.value = ''; filter.dispatchEvent(new Event('change', { bubbles: true }));
        const rows = [];
        for (const claim of vv.materialClaims) {
          const card = shadow.querySelector('[data-review-claim="' + claim.id + '"]');
          const button = card?.querySelector('[data-show-claim]');
          CSS.highlights.delete('vast-review-claim');
          shadow.querySelector('#vv-location-notice').textContent = '';
          if (button) button.click();
          const ranges = [...(CSS.highlights.get('vast-review-claim') || [])].map(range => range.toString());
          const notice = shadow.querySelector('#vv-location-notice')?.textContent || '';
          const links = [...(card?.querySelectorAll('.vv-reading-actions a') || [])].map(a => {
            const url = new URL(a.href); let anchor = '';
            try { anchor = decodeURIComponent(url.hash.slice(1)); } catch {}
            return { href: url.pathname + url.hash, exists: url.pathname === location.pathname && (!anchor || !!document.getElementById(anchor)) };
          });
          rows.push({ id: claim.id, sections: claim.checkedContent.sections, claim: claim.claim.text,
            claimStatus: claim.current.status, cardStatus: card?.querySelector('[data-status]')?.dataset.status,
            spans: claim.sourceLocation.spans, renderedDependency: claim.renderedDependency,
            sourcePassages: claim.sourcePassages,
            displayedWording: [...(card?.querySelectorAll('blockquote') || [])].map(el => el.textContent), ranges, notice, links,
            highlightCountMatches: !ranges.length || ranges.length === claim.sourcePassages?.length,
            selectedClaimMatches: !ranges.length || card?.classList.contains('vv-selected-claim'),
            result: !button ? 'MISSING_CARD' : ranges.length ? 'LOCATED' :
              claim.sourcePassages?.some(p => p.redacted) && /masked in review data/.test(notice) && links.length && links.every(l => l.exists)
                ? 'MASKED_SECTION_FALLBACK' : 'UNLOCATED' });
        }
        return { route: context.path || ${JSON.stringify(route)}, available: vv.available,
          primary: !vv.supportLayer, claims: rows, filters,
          technicalClosed: !shadow.querySelector('.vv-technical')?.open,
          cardCount: shadow.querySelectorAll('[data-review-claim]').length };
      })()`);
      write(route.split('/').at(-1) + '.json', { started, finished: new Date().toISOString(), ...observation });
      const row = { route, claims: observation.claims.length,
        located: observation.claims.filter(c => c.result === 'LOCATED').length,
        maskedSectionFallbacks: observation.claims.filter(c => c.result === 'MASKED_SECTION_FALLBACK').length,
        unlocated: observation.claims.filter(c => !['LOCATED', 'MASKED_SECTION_FALLBACK'].includes(c.result)).length,
        cardsPass: observation.available && observation.primary && observation.claims.length > 0 && observation.cardCount === observation.claims.length && observation.technicalClosed,
        statusesPreserved: observation.claims.every(c => c.claimStatus === c.cardStatus),
        highlightCountsPass: observation.claims.every(c => c.highlightCountMatches && c.selectedClaimMatches),
        filtersPass: observation.filters.every(f => f.matches),
        sectionLinksPass: observation.claims.every(c => c.links.length > 0 && c.links.every(l => l.exists)) };
      results.push(row); console.log(JSON.stringify(row));
    } catch (error) {
      const message = String(error.stderr || error.message).replaceAll(root, '<docs-repository>');
      write(route.split('/').at(-1) + '-error.json', { route, started, error: message });
      results.push({ route, error: message }); console.log(JSON.stringify({ route, error: message.slice(0, 400) }));
    }
  }
} finally {
  try { browser('close'); } catch {}
  write(`summary-${shard}.json`, { finished: new Date().toISOString(), sourceUnchanged: hash('review-server.mjs') === sourceHash, results });
}
if (hash('review-server.mjs') !== sourceHash || results.some(r => r.error || r.unlocated || !r.cardsPass ||
    !r.statusesPreserved || !r.highlightCountsPass || !r.filtersPass || !r.sectionLinksPass)) process.exitCode = 1;
