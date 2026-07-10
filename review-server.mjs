#!/usr/bin/env node
/*
 * Vast.ai docs review server — annotate the local Mintlify preview (PR #185)
 * ---------------------------------------------------------------------------
 * Zero dependencies. Node 18+.
 *
 * What it does:
 *   - Reverse-proxies the Mintlify dev preview (default http://localhost:3000)
 *     and injects a review overlay into every page.
 *   - Reviewers highlight text and leave comments; feedback autosaves to
 *     ./review-feedback/feedback-<reviewer>.json on this machine.
 *   - Exports Jira-importable CSV, plus Markdown and JSON, at any time.
 *
 * Usage:
 *   Terminal 1:  npm run dev -- --no-open     (Mintlify preview on :3000)
 *   Terminal 2:  node review-server.mjs       (review overlay on :4000)
 *   Browse:      http://localhost:4000/host/hosting-overview
 *
 * Options:
 *   --port 4000                port for this review server
 *   --target http://localhost:3000   where the Mintlify preview runs
 *   --dir ./review-feedback    where feedback JSON files are written
 *
 * Status & exports: http://localhost:4000/__review__/
 */

import http from 'node:http';
import net from 'node:net';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

// ------------------------------------------------------------------ config
const argv = process.argv.slice(2);
function argValue(name, dflt) {
  const i = argv.indexOf(name);
  return i !== -1 && argv[i + 1] ? argv[i + 1] : dflt;
}
const PORT = parseInt(argValue('--port', '4000'), 10);
const TARGET = new URL(argValue('--target', 'http://localhost:3000'));
const FEEDBACK_DIR = path.resolve(argValue('--dir', './review-feedback'));
const PR_URL = 'https://github.com/vast-ai/docs/pull/185';
const PR_LABEL = 'docs-pr185-review';

fs.mkdirSync(FEEDBACK_DIR, { recursive: true });

// ------------------------------------------------------------- feedback io
function reviewerSlug(name) {
  const raw = String(name || '').trim();
  const s = raw.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  // short hash keeps distinct names ("Ana B" vs "ana-b", non-ASCII names) in distinct files
  const h = crypto.createHash('sha1').update(raw).digest('hex').slice(0, 6);
  return (s || 'reviewer') + '-' + h;
}
function feedbackFile(reviewer) {
  return path.join(FEEDBACK_DIR, `feedback-${reviewerSlug(reviewer)}.json`);
}
function readReviewerState(reviewer) {
  try {
    const raw = fs.readFileSync(feedbackFile(reviewer), 'utf8');
    const data = JSON.parse(raw);
    return Array.isArray(data.items) ? data.items : [];
  } catch {
    return [];
  }
}
function mergeById(existing, incoming) {
  const byId = new Map();
  for (const it of existing) if (it && typeof it.id === 'string') byId.set(it.id, it);
  for (const it of incoming) {
    if (!it || typeof it.id !== 'string') continue;
    const cur = byId.get(it.id);
    if (!cur || String(it.updatedAt || '') >= String(cur.updatedAt || '')) byId.set(it.id, it);
  }
  return [...byId.values()];
}
function writeReviewerState(reviewer, items) {
  // per-item merge (newest updatedAt wins) so concurrent tabs/late writers never clobber each other
  const merged = mergeById(readReviewerState(reviewer), items);
  const file = feedbackFile(reviewer);
  const payload = { reviewer, updatedAt: new Date().toISOString(), pr: PR_URL, items: merged };
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(payload, null, 2));
  fs.renameSync(tmp, file);
  return merged.length;
}
function readAllItems() {
  const byId = new Map();
  const reviewers = [];
  for (const f of fs.readdirSync(FEEDBACK_DIR)) {
    if (!/^feedback-.*\.json$/.test(f)) continue;
    try {
      const data = JSON.parse(fs.readFileSync(path.join(FEEDBACK_DIR, f), 'utf8'));
      if (Array.isArray(data.items)) {
        // dedupe across files by item id (a reviewer renaming mid-session leaves copies in
        // both files) — keep the newest version, tombstones included so deletes win
        for (const it of data.items) {
          if (!it || typeof it.id !== 'string') continue;
          const cur = byId.get(it.id);
          if (!cur || String(it.updatedAt || '') >= String(cur.updatedAt || '')) byId.set(it.id, it);
        }
        reviewers.push(data.reviewer || f);
      }
    } catch { /* skip unreadable file */ }
  }
  const all = [...byId.values()].filter((it) => !it.deleted);
  all.sort((a, b) => (a.page || '').localeCompare(b.page || '') || (a.createdAt || '').localeCompare(b.createdAt || ''));
  return { items: all, reviewers };
}

// ---------------------------------------------------------------- exports
const PRIORITY_MAP = { Blocker: 'Highest', Major: 'High', Minor: 'Medium', Nit: 'Low' };

function csvCell(v) {
  let s = String(v ?? '');
  // formula-injection guard; +/- only when they can start a formula/number so that
  // ordinary quoted text like "--target http://..." is not corrupted by the apostrophe
  if (/^[=@\t\r]/.test(s) || /^[+-][\d.=]/.test(s)) s = "'" + s;
  if (/[",\r\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
  return s;
}
function firstLine(s) {
  return String(s || '').split(/\r?\n/)[0].trim();
}
function itemSummary(it) {
  const page = (it.page || '/').replace(/^\/host\//, '').replace(/^\//, '') || 'home';
  let head = firstLine(it.comment).slice(0, 90);
  if (!head) head = (it.quote || '').slice(0, 90);
  return `[${page}] ${it.category || 'Feedback'}: ${head}`;
}
function itemDescription(it) {
  const lines = [];
  lines.push(`Docs review feedback on PR 185 (${PR_URL})`);
  lines.push('');
  lines.push(`Page: ${it.page || '/'}${it.pageTitle ? ' — ' + it.pageTitle : ''}`);
  if (it.heading) lines.push(`Section: ${it.heading}`);
  if (it.quote) {
    lines.push('');
    lines.push('Quoted text:');
    lines.push(`"${it.quote}"`);
  }
  lines.push('');
  lines.push('Comment:');
  lines.push(it.comment || '(no comment)');
  lines.push('');
  lines.push(`Category: ${it.category || '-'} | Severity: ${it.severity || '-'} | Status: ${it.status || 'open'}`);
  lines.push(`Reviewer: ${it.reviewer || '-'} | Created: ${it.createdAt || '-'}`);
  return lines.join('\n');
}
function toCsv(items) {
  const header = ['Summary', 'Issue Type', 'Priority', 'Labels', 'Description', 'Page', 'Section', 'Quote', 'Category', 'Severity', 'Status', 'Reviewer', 'Created'];
  const rows = [header.map(csvCell).join(',')];
  for (const it of items) {
    rows.push([
      itemSummary(it),
      'Task',
      PRIORITY_MAP[it.severity] || 'Medium',
      PR_LABEL,
      itemDescription(it),
      it.page || '',
      it.heading || '',
      it.quote || '',
      it.category || '',
      it.severity || '',
      it.status || 'open',
      it.reviewer || '',
      it.createdAt || '',
    ].map(csvCell).join(','));
  }
  return '﻿' + rows.join('\r\n') + '\r\n';
}
function toMarkdown(items, reviewers) {
  const out = [];
  out.push('# Vast.ai docs review feedback — PR 185');
  out.push('');
  out.push(`Generated ${new Date().toISOString()} · ${items.length} item(s) · reviewers: ${reviewers.join(', ') || '—'}`);
  out.push(`PR: ${PR_URL}`);
  const byPage = new Map();
  for (const it of items) {
    const key = it.page || '/';
    if (!byPage.has(key)) byPage.set(key, []);
    byPage.get(key).push(it);
  }
  for (const [page, list] of byPage) {
    out.push('');
    out.push(`## ${page}${list[0].pageTitle ? ' — ' + list[0].pageTitle : ''}`);
    let n = 0;
    for (const it of list) {
      n += 1;
      out.push('');
      out.push(`### ${n}. [${it.severity || '-'} · ${it.category || '-'}]${it.heading ? ' ' + it.heading : ''}${it.status === 'resolved' ? ' (resolved)' : ''}`);
      if (it.quote) out.push(`> ${String(it.quote).replace(/\r?\n/g, '\n> ')}`);
      out.push('');
      out.push(it.comment || '(no comment)');
      out.push('');
      out.push(`*— ${it.reviewer || 'unknown'}, ${it.createdAt || ''}*`);
    }
  }
  out.push('');
  return out.join('\n');
}

// ------------------------------------------------------------ status page
function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function statusPage() {
  const { items, reviewers } = readAllItems();
  const open = items.filter((i) => i.status !== 'resolved').length;
  const byReviewer = {};
  for (const it of items) byReviewer[it.reviewer || '?'] = (byReviewer[it.reviewer || '?'] || 0) + 1;
  const rows = Object.entries(byReviewer)
    .map(([r, n]) => `<tr><td>${esc(r)}</td><td>${n}</td></tr>`).join('') || '<tr><td colspan="2">No feedback yet</td></tr>';
  return `<!doctype html><html><head><meta charset="utf-8"><title>PR 185 review feedback</title>
<style>body{font:15px/1.5 system-ui,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;color:#1a1a2e}
h1{font-size:22px} table{border-collapse:collapse;margin:12px 0}td,th{border:1px solid #ccc;padding:6px 14px;text-align:left}
a.btn{display:inline-block;margin:4px 8px 4px 0;padding:8px 14px;border:1px solid #4a5cf0;border-radius:8px;color:#4a5cf0;text-decoration:none;font-weight:600}
code{background:#f0f0f6;padding:2px 5px;border-radius:4px}</style></head><body>
<h1>Vast.ai docs review — PR 185 feedback</h1>
<p><b>${items.length}</b> item(s), <b>${open}</b> open. Feedback files live in <code>${esc(FEEDBACK_DIR)}</code>.</p>
<table><tr><th>Reviewer</th><th>Items</th></tr>${rows}</table>
<p>
<a class="btn" href="/__review__/export/feedback.csv">Download CSV (Jira import)</a>
<a class="btn" href="/__review__/export/feedback.md">Download Markdown</a>
<a class="btn" href="/__review__/export/feedback.json">Download JSON</a>
</p>
<p><b>The 8 blocking questions</b> the team needs answered live at <a href="/review-questions">/review-questions</a> — comment on them there like any other page.</p>
<p>When you're done reviewing, send back the CSV <i>or</i> the JSON file — either can be imported into Jira for record keeping.</p>
<p><a href="/host/hosting-overview">← Back to the docs preview</a></p>
</body></html>`;
}

// ---------------------------------------------------------------- overlay
// Client-side overlay source. Served at /__review__/overlay.js.
// NOTE: written without backticks or "$"+"{" so it can live in String.raw.
const OVERLAY_JS = String.raw`
(function () {
  'use strict';
  if (window.__vastReviewLoaded) return;
  window.__vastReviewLoaded = true;

  var API = '/__review__/api';
  var LS_REVIEWER = 'vastReview.reviewer';
  var LS_ITEMS = 'vastReview.items';
  var CATEGORIES = ['Error', 'Unclear', 'Missing', 'Outdated', 'Suggestion', 'Question', 'Praise'];
  var SEVERITIES = ['Blocker', 'Major', 'Minor', 'Nit'];
  var SEV_COLOR = { Blocker: '#d92d20', Major: '#e8590c', Minor: '#b58a00', Nit: '#5c677d' };

  // ---------------- state ----------------
  var reviewer = '';
  var items = [];
  var pending = null;      // selection captured but not yet saved
  var editingId = null;
  var showAllPages = false;
  var saveStatus = 'idle'; // idle | saving | saved | offline
  var saveTimer = null;
  var anchorTimer = null;

  try { reviewer = localStorage.getItem(LS_REVIEWER) || ''; } catch (e) {}
  try { items = JSON.parse(localStorage.getItem(LS_ITEMS) || '[]'); } catch (e) { items = []; }
  if (!Array.isArray(items)) items = [];

  function uid() { return 'fb-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }
  function nowIso() { return new Date().toISOString(); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pageTitle() {
    var t = document.title || '';
    return t.replace(/\s*[-|–—]\s*Vast.*$/i, '').trim() || t;
  }
  function visibleItems() { return items.filter(function (it) { return !it.deleted; }); }
  function pageItems() {
    return visibleItems().filter(function (it) { return it.page === location.pathname; });
  }

  // ---------------- persistence ----------------
  function persistLocal() {
    try { localStorage.setItem(LS_ITEMS, JSON.stringify(items)); } catch (e) {}
  }
  function scheduleSave() {
    persistLocal();
    renderBadge();
    if (saveTimer) clearTimeout(saveTimer);
    saveStatus = 'saving';
    renderSaveStatus();
    saveTimer = setTimeout(pushToServer, 700);
  }
  function pushToServer() {
    if (!reviewer) { saveStatus = 'offline'; renderSaveStatus(); return; }
    fetch(API + '/state', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ reviewer: reviewer, items: items })
    }).then(function (r) {
      saveStatus = r.ok ? 'saved' : 'offline';
      renderSaveStatus();
    }).catch(function () {
      saveStatus = 'offline';
      renderSaveStatus();
    });
  }
  function mergeServerState() {
    if (!reviewer) return;
    fetch(API + '/state?reviewer=' + encodeURIComponent(reviewer))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var server = (data && Array.isArray(data.items)) ? data.items : [];
        var byId = {};
        items.forEach(function (it) { byId[it.id] = it; });
        server.forEach(function (s) {
          var mine = byId[s.id];
          if (!mine || String(s.updatedAt || '') > String(mine.updatedAt || '')) byId[s.id] = s;
        });
        items = Object.keys(byId).map(function (k) { return byId[k]; });
        persistLocal();
        scheduleAnchor();
        renderAll();
        scheduleSave(); // push items that so far existed only in this browser back to disk
      })
      .catch(function () {});
  }
  function flushNow() {
    // best-effort synchronous save on tab close / navigation away
    if (!reviewer || !items.length) return;
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    persistLocal();
    try {
      var blob = new Blob([JSON.stringify({ reviewer: reviewer, items: items })], { type: 'application/json' });
      navigator.sendBeacon(API + '/state', blob);
    } catch (e) {}
  }
  window.addEventListener('pagehide', flushNow);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') flushNow();
  });

  // ---------------- text index + anchoring ----------------
  function skipNode(el) {
    if (!el) return false;
    var tag = el.nodeName;
    return tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT' || tag === 'TEMPLATE' || el.id === '__vast_review_host__';
  }
  function buildTextIndex() {
    var nodes = [];
    var text = '';
    var visCache = new Map();
    function isRendered(el) {
      if (visCache.has(el)) return visCache.get(el);
      var ok = false;
      if (el.getClientRects().length > 0) {
        var r = el.getBoundingClientRect();
        // zero/1px boxes catch sr-only clip patterns as well as display:none
        ok = r.width > 1.5 && r.height > 1.5 && getComputedStyle(el).visibility !== 'hidden';
      }
      visCache.set(el, ok);
      return ok;
    }
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var p = node.parentNode;
        while (p && p !== document.body) {
          if (p.nodeType === 1 && skipNode(p)) return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        var el = node.parentElement;
        if (el && node.data.trim() && !isRendered(el)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = walker.nextNode())) {
      nodes.push({ node: n, start: text.length, end: text.length + n.data.length });
      text += n.data;
    }
    return { text: text, nodes: nodes };
  }
  function globalOffsetOf(container, offset, index) {
    if (container.nodeType === 3) {
      for (var i = 0; i < index.nodes.length; i++) {
        if (index.nodes[i].node === container) return index.nodes[i].start + offset;
      }
    }
    return -1;
  }
  function nodeAt(index, globalPos, preferStart) {
    // binary search for the text node containing globalPos
    var lo = 0, hi = index.nodes.length - 1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      var e = index.nodes[mid];
      if (globalPos < e.start) hi = mid - 1;
      else if (globalPos > e.end || (globalPos === e.end && preferStart && mid + 1 < index.nodes.length)) lo = mid + 1;
      else return { node: e.node, offset: globalPos - e.start };
    }
    return null;
  }
  function commonSuffixLen(a, b) {
    var n = 0;
    while (n < a.length && n < b.length && a[a.length - 1 - n] === b[b.length - 1 - n]) n++;
    return n;
  }
  function findQuote(index, quote, prefix) {
    if (!quote) return null;
    var hits = [];
    var from = 0, at;
    while ((at = index.text.indexOf(quote, from)) !== -1) {
      hits.push({ start: at, end: at + quote.length });
      from = at + 1;
      if (hits.length > 50) break;
    }
    if (!hits.length) {
      // whitespace-tolerant fallback
      var pattern = quote.replace(/[.*+?^$()\[\]{}|\\]/g, '\\$&').replace(/\s+/g, '\\s*');
      try {
        var m = new RegExp(pattern).exec(index.text);
        if (m) hits.push({ start: m.index, end: m.index + m[0].length });
      } catch (e) {}
    }
    if (!hits.length) return null;
    if (hits.length === 1 || !prefix) return hits[0];
    var best = hits[0], bestScore = -1;
    hits.forEach(function (h) {
      var before = index.text.slice(Math.max(0, h.start - prefix.length), h.start);
      var score = commonSuffixLen(before, prefix);
      if (score > bestScore) { bestScore = score; best = h; }
    });
    return best;
  }
  function makeRange(index, start, end) {
    var s = nodeAt(index, start, true);
    var e = nodeAt(index, end, false);
    if (!s || !e) return null;
    try {
      var r = document.createRange();
      r.setStart(s.node, s.offset);
      r.setEnd(e.node, e.offset);
      return r;
    } catch (err) { return null; }
  }

  var anchoredRanges = {}; // id -> Range
  function anchorAll() {
    anchoredRanges = {};
    var list = pageItems().filter(function (it) { return it.type === 'inline'; });
    if (list.length) {
      var index = buildTextIndex();
      list.forEach(function (it) {
        var hit = findQuote(index, it.quote, it.prefix);
        if (hit) {
          var r = makeRange(index, hit.start, hit.end);
          if (r) anchoredRanges[it.id] = r;
        }
      });
    }
    paintHighlights();
    renderList();
  }
  function scheduleAnchor() {
    if (anchorTimer) clearTimeout(anchorTimer);
    anchorTimer = setTimeout(anchorAll, 400);
  }
  function paintHighlights() {
    if (typeof Highlight === 'undefined' || !CSS.highlights) return;
    var ranges = Object.keys(anchoredRanges).map(function (k) { return anchoredRanges[k]; });
    if (ranges.length) {
      var hl = new Highlight();
      ranges.forEach(function (r) { hl.add(r); });
      CSS.highlights.set('vast-review', hl);
    } else {
      CSS.highlights.delete('vast-review');
    }
  }
  function flashRange(r) {
    if (typeof Highlight === 'undefined' || !CSS.highlights) return;
    CSS.highlights.set('vast-review-flash', new Highlight(r));
    setTimeout(function () { CSS.highlights.delete('vast-review-flash'); }, 1600);
  }

  // ---------------- selection capture ----------------
  var selBtnData = null;
  function hideSelBtn() { selBtn.style.display = 'none'; selBtnData = null; }
  function onSelectionSettled() {
    var sel = document.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) { hideSelBtn(); return; }
    var anchor = sel.anchorNode;
    if (anchor && host.contains(anchor.nodeType === 1 ? anchor : anchor.parentNode)) { hideSelBtn(); return; }
    if (anchor === host) { hideSelBtn(); return; }
    var quote = sel.toString().replace(/\s+$/,'').replace(/^\s+/,'');
    if (quote.length < 2 || quote.length > 2000) { hideSelBtn(); return; }
    var range = sel.getRangeAt(0);
    var rect = range.getBoundingClientRect();
    if (!rect || (rect.width === 0 && rect.height === 0)) { hideSelBtn(); return; }

    var index = buildTextIndex();
    var s = globalOffsetOf(range.startContainer, range.startOffset, index);
    var e = globalOffsetOf(range.endContainer, range.endOffset, index);
    var prefix = '', suffix = '';
    if (s >= 0) prefix = index.text.slice(Math.max(0, s - 40), s);
    if (e >= 0) suffix = index.text.slice(e, e + 40);

    selBtnData = {
      quote: quote, prefix: prefix, suffix: suffix,
      heading: nearestHeading(range)
    };
    var x = Math.min(rect.right + 6, window.innerWidth - 130);
    var y = Math.min(Math.max(rect.bottom + 6, 10), window.innerHeight - 44);
    selBtn.style.left = Math.max(8, x) + 'px';
    selBtn.style.top = y + 'px';
    selBtn.style.display = 'flex';
  }
  function nearestHeading(range) {
    var hs = document.querySelectorAll('h1, h2, h3, h4');
    var best = '';
    for (var i = 0; i < hs.length; i++) {
      var pos = range.startContainer.compareDocumentPosition(hs[i]);
      if (pos & Node.DOCUMENT_POSITION_PRECEDING) best = hs[i].textContent.trim();
    }
    return best;
  }

  // ---------------- item ops ----------------
  var composerCtx = null; // page identity captured when the composer opens, so a
                          // back/forward navigation mid-typing cannot mislabel the item
  function saveItem(fields) {
    var it;
    if (editingId) {
      it = items.filter(function (x) { return x.id === editingId; })[0];
      if (!it) return;
      it.category = fields.category;
      it.severity = fields.severity;
      it.comment = fields.comment;
      it.updatedAt = nowIso();
    } else {
      it = {
        id: uid(),
        reviewer: reviewer,
        page: composerCtx ? composerCtx.page : location.pathname,
        pageTitle: composerCtx ? composerCtx.pageTitle : pageTitle(),
        type: pending && pending.quote ? 'inline' : 'page',
        quote: pending ? (pending.quote || '') : '',
        prefix: pending ? (pending.prefix || '') : '',
        suffix: pending ? (pending.suffix || '') : '',
        heading: pending ? (pending.heading || '') : '',
        category: fields.category,
        severity: fields.severity,
        comment: fields.comment,
        status: 'open',
        createdAt: nowIso(),
        updatedAt: nowIso()
      };
      items.push(it);
    }
    pending = null;
    editingId = null;
    scheduleSave();
    scheduleAnchor();
    renderAll();
    toast('Feedback saved');
  }
  function deleteItem(id) {
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    it.deleted = true;
    it.updatedAt = nowIso();
    scheduleSave();
    scheduleAnchor();
    renderAll();
  }
  function toggleResolve(id) {
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    it.status = it.status === 'resolved' ? 'open' : 'resolved';
    it.updatedAt = nowIso();
    scheduleSave();
    renderAll();
  }

  // ---------------- UI ----------------
  var host = document.createElement('div');
  host.id = '__vast_review_host__';
  var shadow = host.attachShadow({ mode: 'open' });

  // document-level styles (::highlight can't live in shadow DOM)
  var docStyle = document.createElement('style');
  docStyle.textContent = '::highlight(vast-review){background:rgba(255,200,50,.45);}' +
    '::highlight(vast-review-flash){background:rgba(74,92,240,.35);}';
  document.head.appendChild(docStyle);

  var css = '' +
    ':host{all:initial}' +
    '*{box-sizing:border-box;font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}' +
    '#pill{position:fixed;right:18px;bottom:18px;z-index:2147483000;display:flex;align-items:center;gap:8px;' +
      'padding:10px 16px;border:none;border-radius:999px;background:#4a5cf0;color:#fff;font-size:14px;font-weight:600;' +
      'cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.25)}' +
    '#pill:hover{background:#3a49d6}' +
    '#pill .count{background:rgba(255,255,255,.25);border-radius:999px;padding:1px 8px;font-size:12px}' +
    '#selbtn{position:fixed;z-index:2147483001;display:none;align-items:center;gap:6px;padding:7px 12px;' +
      'border:none;border-radius:8px;background:#1a1a2e;color:#fff;font-size:13px;font-weight:600;cursor:pointer;' +
      'box-shadow:0 4px 14px rgba(0,0,0,.3)}' +
    '#panel{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:95vw;z-index:2147483002;display:none;' +
      'flex-direction:column;background:#fff;color:#1a1a2e;border-left:1px solid #d5d9e4;box-shadow:-6px 0 24px rgba(0,0,0,.12);font-size:13px}' +
    '#panel.open{display:flex}' +
    '#panel header{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#1a1a2e;color:#fff}' +
    '#panel header b{font-size:14px}' +
    '#panel header button{background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1}' +
    '.meta{display:flex;align-items:center;gap:8px;padding:8px 14px;border-bottom:1px solid #e7eaf1;color:#5c677d}' +
    '.meta b{color:#1a1a2e}' +
    '.meta button,.filters button{background:#f0f2f8;border:1px solid #d5d9e4;border-radius:6px;padding:3px 9px;cursor:pointer;font-size:12px}' +
    '.filters{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 14px;border-bottom:1px solid #e7eaf1}' +
    '.filters label{display:flex;align-items:center;gap:6px;cursor:pointer;color:#5c677d}' +
    '.filters .primary{background:#4a5cf0;border-color:#4a5cf0;color:#fff;font-weight:600}' +
    '#list{flex:1;overflow-y:auto;padding:10px 14px}' +
    '.pagegroup{margin:14px 0 6px;font-weight:700;font-size:12px;color:#5c677d;text-transform:uppercase;letter-spacing:.4px}' +
    '.card{border:1px solid #e0e4ee;border-radius:10px;padding:10px 12px;margin-bottom:10px;background:#fbfcfe}' +
    '.card.resolved{opacity:.55}' +
    '.card .chips{display:flex;gap:6px;align-items:center;margin-bottom:6px;flex-wrap:wrap}' +
    '.chip{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;color:#fff}' +
    '.chip.cat{background:#5c677d}' +
    '.chip.orphan{background:#fff;color:#b58a00;border:1px dashed #b58a00}' +
    '.card blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid #ffd166;background:#fffbeb;color:#5c5233;' +
      'font-style:italic;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}' +
    '.card .comment{white-space:pre-wrap;margin:6px 0}' +
    '.card .byline{color:#8a93a6;font-size:11px;margin-top:4px}' +
    '.card .acts{display:flex;gap:10px;margin-top:8px}' +
    '.card .acts button{background:none;border:none;padding:0;color:#4a5cf0;font-size:12px;cursor:pointer;font-weight:600}' +
    '.card .acts button.danger{color:#d92d20}' +
    '.empty{color:#8a93a6;text-align:center;padding:30px 10px}' +
    '#panel footer{border-top:1px solid #e7eaf1;padding:10px 14px;display:flex;flex-direction:column;gap:8px;background:#f7f8fc}' +
    '.exports{display:flex;gap:8px;align-items:center;flex-wrap:wrap}' +
    '.exports a{color:#4a5cf0;font-weight:600;text-decoration:none;font-size:12px;border:1px solid #c9d0f5;border-radius:6px;padding:4px 9px}' +
    '#saveStatus{font-size:11px;color:#8a93a6}' +
    '#composer,#nameModal{position:fixed;z-index:2147483003;top:50%;left:50%;transform:translate(-50%,-50%);width:420px;max-width:92vw;' +
      'display:none;flex-direction:column;gap:10px;background:#fff;color:#1a1a2e;border-radius:14px;padding:18px;box-shadow:0 12px 48px rgba(0,0,0,.3);font-size:13px}' +
    '#composer.open,#nameModal.open{display:flex}' +
    '#composer h3,#nameModal h3{margin:0;font-size:15px}' +
    '#composer blockquote{margin:0;padding:6px 10px;border-left:3px solid #ffd166;background:#fffbeb;color:#5c5233;font-style:italic;' +
      'max-height:70px;overflow:auto}' +
    '.row{display:flex;gap:10px}' +
    '.row label{flex:1;display:flex;flex-direction:column;gap:4px;font-weight:600;color:#5c677d;font-size:11px;text-transform:uppercase}' +
    'select,textarea,input[type=text]{border:1px solid #c9cfdd;border-radius:8px;padding:8px;font-size:13px;width:100%;background:#fff;color:#1a1a2e}' +
    'textarea{min-height:90px;resize:vertical}' +
    '.btnrow{display:flex;justify-content:flex-end;gap:8px}' +
    '.btnrow button{border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid #c9cfdd;background:#fff;color:#1a1a2e}' +
    '.btnrow button.primary{background:#4a5cf0;border-color:#4a5cf0;color:#fff}' +
    '#overlaybg{position:fixed;inset:0;z-index:2147483002;background:rgba(10,12,30,.35);display:none}' +
    '#overlaybg.open{display:block}' +
    '#toast{position:fixed;bottom:80px;right:24px;z-index:2147483004;background:#1a1a2e;color:#fff;padding:8px 16px;border-radius:8px;' +
      'font-size:13px;display:none}';

  var wrap = document.createElement('div');
  wrap.innerHTML =
    '<style>' + css + '</style>' +
    '<button id="pill" type="button">&#128172; Review <span class="count" id="pillCount">0</span></button>' +
    '<button id="selbtn" type="button">&#128172; Comment on selection</button>' +
    '<div id="overlaybg"></div>' +
    '<div id="panel">' +
      '<header><b>Docs review &mdash; PR 185</b><button id="closePanel" title="Close">&times;</button></header>' +
      '<div class="meta">Reviewer: <b id="who">&mdash;</b> <button id="editWho">change</button></div>' +
      '<div class="filters">' +
        '<label><input type="checkbox" id="allPages"> all pages</label>' +
        '<button id="addPageNote" class="primary">+ Page note</button>' +
      '</div>' +
      '<div id="list"></div>' +
      '<footer>' +
        '<div class="exports" style="border-bottom:1px solid #e7eaf1;padding-bottom:8px">' +
          '<a href="/review-questions" style="background:#4a5cf0;color:#fff;border-color:#4a5cf0">&#9888; The 8 blocking questions &mdash; answer here</a>' +
        '</div>' +
        '<div class="exports">Export: ' +
          '<a href="/__review__/export/feedback.csv">CSV (Jira)</a>' +
          '<a href="/__review__/export/feedback.md">Markdown</a>' +
          '<a href="/__review__/export/feedback.json">JSON</a>' +
          '<a href="/__review__/" target="_blank">Status</a>' +
        '</div>' +
        '<div id="saveStatus"></div>' +
      '</footer>' +
    '</div>' +
    '<div id="composer">' +
      '<h3 id="composerTitle">Add feedback</h3>' +
      '<blockquote id="composerQuote" style="display:none"></blockquote>' +
      '<div class="row">' +
        '<label>Category<select id="fCategory"></select></label>' +
        '<label>Severity<select id="fSeverity"></select></label>' +
      '</div>' +
      '<label style="display:flex;flex-direction:column;gap:4px;font-weight:600;color:#5c677d;font-size:11px;text-transform:uppercase">Comment' +
        '<textarea id="fComment" placeholder="What should change, and why?"></textarea></label>' +
      '<div class="btnrow"><button id="composerCancel">Cancel</button><button id="composerSave" class="primary">Save feedback</button></div>' +
    '</div>' +
    '<div id="nameModal">' +
      '<h3>Who is reviewing?</h3>' +
      '<p style="margin:0;color:#5c677d">Your name is attached to each comment so feedback can be tracked in Jira.</p>' +
      '<input type="text" id="fName" placeholder="e.g. Ana">' +
      '<div class="btnrow"><button id="nameSave" class="primary">Start reviewing</button></div>' +
    '</div>' +
    '<div id="toast"></div>';
  shadow.appendChild(wrap);
  document.body.appendChild(host);

  function $(id) { return shadow.getElementById(id); }
  var pill = $('pill'), selBtn = $('selbtn'), panel = $('panel'), composer = $('composer'),
      nameModal = $('nameModal'), overlaybg = $('overlaybg'), toastEl = $('toast');

  CATEGORIES.forEach(function (c) {
    var o = document.createElement('option'); o.value = c; o.textContent = c; $('fCategory').appendChild(o);
  });
  SEVERITIES.forEach(function (s) {
    var o = document.createElement('option'); o.value = s; o.textContent = s; $('fSeverity').appendChild(o);
  });
  $('fCategory').value = 'Suggestion';
  $('fSeverity').value = 'Minor';

  var toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.style.display = 'block';
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.style.display = 'none'; }, 1800);
  }

  function renderBadge() {
    var n = pageItems().filter(function (i) { return i.status !== 'resolved'; }).length;
    var total = visibleItems().length;
    $('pillCount').textContent = n + '/' + total;
  }
  function renderSaveStatus() {
    var map = {
      idle: '', saving: 'Saving…',
      saved: 'Saved to disk ✓',
      offline: reviewer ? 'Review server unreachable — stored in browser only' : 'Set your name to save feedback'
    };
    $('saveStatus').textContent = map[saveStatus] || '';
  }
  function cardHtml(it) {
    var eid = esc(it.id); // ids can arrive from shared feedback files — never trust them in markup
    var found = !!anchoredRanges[it.id];
    var sev = '<span class="chip" style="background:' + (SEV_COLOR[it.severity] || '#5c677d') + '">' + esc(it.severity) + '</span>';
    var cat = '<span class="chip cat">' + esc(it.category) + '</span>';
    var orphan = (it.type === 'inline' && !found && it.page === location.pathname)
      ? '<span class="chip orphan" title="The quoted text was not found on this page">not found</span>' : '';
    var quote = it.quote ? '<blockquote>' + esc(it.quote) + '</blockquote>' : '';
    var headline = it.heading ? '<div class="byline">&sect; ' + esc(it.heading) + '</div>' : '';
    var goBtn = (it.page === location.pathname && found) ? '<button data-act="go" data-id="' + eid + '">Go to</button>' : '';
    var openBtn = (it.page !== location.pathname) ? '<button data-act="open" data-id="' + eid + '">Open page</button>' : '';
    return '<div class="card ' + (it.status === 'resolved' ? 'resolved' : '') + '" data-card="' + eid + '">' +
      '<div class="chips">' + sev + cat + orphan + '</div>' +
      quote + headline +
      '<div class="comment">' + esc(it.comment) + '</div>' +
      '<div class="byline">' + esc(it.reviewer) + ' &middot; ' + esc(String(it.createdAt || '').slice(0, 16).replace('T', ' ')) + '</div>' +
      '<div class="acts">' + goBtn + openBtn +
        '<button data-act="edit" data-id="' + eid + '">Edit</button>' +
        '<button data-act="resolve" data-id="' + eid + '">' + (it.status === 'resolved' ? 'Reopen' : 'Resolve') + '</button>' +
        '<button data-act="delete" data-id="' + eid + '" class="danger">Delete</button>' +
      '</div></div>';
  }
  function renderList() {
    var listEl = $('list');
    var data = showAllPages ? visibleItems() : pageItems();
    if (!data.length) {
      listEl.innerHTML = '<div class="empty">No feedback ' + (showAllPages ? 'yet' : 'on this page yet') +
        '.<br><br>Select any text on the page and click<br><b>&#128172; Comment on selection</b>,<br>or add a page-level note above.</div>';
      return;
    }
    var html = '';
    if (showAllPages) {
      var byPage = {};
      data.forEach(function (it) { (byPage[it.page] = byPage[it.page] || []).push(it); });
      Object.keys(byPage).sort().forEach(function (pg) {
        html += '<div class="pagegroup">' + esc(pg) + '</div>';
        byPage[pg].forEach(function (it) { html += cardHtml(it); });
      });
    } else {
      data.forEach(function (it) { html += cardHtml(it); });
    }
    listEl.innerHTML = html;
  }
  function renderWho() { $('who').textContent = reviewer || '—'; }
  function renderAll() { renderBadge(); renderList(); renderWho(); renderSaveStatus(); }

  function openPanel() { panel.classList.add('open'); renderAll(); }
  function closePanel() { panel.classList.remove('open'); }
  function openComposer(title, quote) {
    if (!reviewer) { pendingAfterName = function () { openComposer(title, quote); }; openNameModal(); return; }
    composerCtx = { page: location.pathname, pageTitle: pageTitle() };
    $('composerTitle').textContent = title;
    var q = $('composerQuote');
    if (quote) { q.textContent = quote; q.style.display = 'block'; } else { q.style.display = 'none'; }
    composer.classList.add('open');
    overlaybg.classList.add('open');
    $('fComment').focus();
  }
  function closeComposer() {
    composer.classList.remove('open');
    overlaybg.classList.remove('open');
    $('fComment').value = '';
    pending = null;
    editingId = null;
  }
  var pendingAfterName = null;
  function openNameModal() {
    nameModal.classList.add('open');
    overlaybg.classList.add('open');
    $('fName').value = reviewer;
    $('fName').focus();
  }
  function closeNameModal() {
    nameModal.classList.remove('open');
    if (!composer.classList.contains('open')) overlaybg.classList.remove('open');
  }

  // ---------------- events ----------------
  pill.addEventListener('click', function () {
    if (panel.classList.contains('open')) closePanel(); else openPanel();
  });
  $('closePanel').addEventListener('click', closePanel);
  $('editWho').addEventListener('click', openNameModal);
  $('allPages').addEventListener('change', function (e) { showAllPages = e.target.checked; renderList(); });
  $('addPageNote').addEventListener('click', function () {
    pending = null; editingId = null;
    openComposer('Page note — ' + location.pathname, '');
  });
  selBtn.addEventListener('click', function () {
    pending = selBtnData;
    hideSelBtn();
    var sel = document.getSelection();
    if (sel) sel.removeAllRanges();
    editingId = null;
    openComposer('Comment on selection', pending ? pending.quote : '');
  });
  $('composerCancel').addEventListener('click', closeComposer);
  $('composerSave').addEventListener('click', function () {
    var comment = $('fComment').value.trim();
    if (!comment) { $('fComment').focus(); return; }
    saveItem({ category: $('fCategory').value, severity: $('fSeverity').value, comment: comment });
    closeComposer();
  });
  $('nameSave').addEventListener('click', function () {
    var v = $('fName').value.trim();
    if (!v) { $('fName').focus(); return; }
    reviewer = v;
    try { localStorage.setItem(LS_REVIEWER, reviewer); } catch (e) {}
    closeNameModal();
    renderWho();
    mergeServerState();
    if (pendingAfterName) { var f = pendingAfterName; pendingAfterName = null; f(); }
  });
  $('fName').addEventListener('keydown', function (e) { if (e.key === 'Enter') $('nameSave').click(); });
  overlaybg.addEventListener('click', function () { closeComposer(); closeNameModal(); });
  $('list').addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-act]');
    if (!btn) return;
    var id = btn.getAttribute('data-id');
    var act = btn.getAttribute('data-act');
    var it = items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (act === 'delete') { if (confirm('Delete this feedback item?')) deleteItem(id); }
    else if (act === 'resolve') toggleResolve(id);
    else if (act === 'open') {
      // only same-origin paths — pages can arrive from shared feedback files
      if (/^\/([^\/]|$)/.test(String(it.page || ''))) location.href = it.page;
    }
    else if (act === 'go') {
      var r = anchoredRanges[id];
      if (r) {
        var el = r.startContainer.nodeType === 1 ? r.startContainer : r.startContainer.parentElement;
        if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        flashRange(r);
      }
    }
    else if (act === 'edit') {
      editingId = id;
      pending = null;
      $('fCategory').value = it.category || CATEGORIES[0];
      $('fSeverity').value = it.severity || 'Minor';
      openComposer('Edit feedback', it.quote || '');
      $('fComment').value = it.comment || '';
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeComposer(); closeNameModal(); hideSelBtn(); }
  });
  document.addEventListener('pointerup', function (e) {
    var path = e.composedPath ? e.composedPath() : [];
    if (path.indexOf(host) !== -1) return;
    setTimeout(onSelectionSettled, 30);
  });
  document.addEventListener('keyup', function (e) {
    if (e.shiftKey || e.key === 'Shift') setTimeout(onSelectionSettled, 30);
  });
  // click on a highlight opens the panel scrolled to that card
  document.addEventListener('click', function (e) {
    var path = e.composedPath ? e.composedPath() : [];
    if (path.indexOf(host) !== -1) return;
    var ids = Object.keys(anchoredRanges);
    for (var i = 0; i < ids.length; i++) {
      var rects = anchoredRanges[ids[i]].getClientRects();
      for (var j = 0; j < rects.length; j++) {
        var rc = rects[j];
        if (e.clientX >= rc.left && e.clientX <= rc.right && e.clientY >= rc.top && e.clientY <= rc.bottom) {
          openPanel();
          var card = shadow.querySelector('[data-card="' + CSS.escape(ids[i]) + '"]');
          if (card) { card.scrollIntoView({ block: 'center' }); card.style.outline = '2px solid #4a5cf0'; }
          return;
        }
      }
    }
  }, true);

  // SPA navigation: re-anchor highlights when the route or DOM changes
  function onNavigate() {
    hideSelBtn();
    scheduleAnchor();
    setTimeout(renderAll, 450);
  }
  var origPush = history.pushState;
  history.pushState = function () { origPush.apply(this, arguments); onNavigate(); };
  var origReplace = history.replaceState;
  history.replaceState = function () { origReplace.apply(this, arguments); onNavigate(); };
  window.addEventListener('popstate', onNavigate);
  new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      if (muts[i].target === host || host.contains(muts[i].target)) continue;
      scheduleAnchor();
      return;
    }
  }).observe(document.body, { childList: true, subtree: true });

  // ---------------- boot ----------------
  renderAll();
  scheduleAnchor();
  if (reviewer) { mergeServerState(); saveStatus = 'saved'; }
  renderSaveStatus();
})();
`;

// ------------------------------------------------------------------ proxy
const INJECT_TAG = '<script src="/__review__/overlay.js" defer></script>';

function injectOverlay(html) {
  const lower = html.toLowerCase();
  let at = lower.lastIndexOf('</body>');
  if (at === -1) at = lower.lastIndexOf('</html>');
  if (at === -1) return html + INJECT_TAG;
  return html.slice(0, at) + INJECT_TAG + html.slice(at);
}

function readBody(req, limitBytes) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on('data', (c) => {
      size += c.length;
      if (size > limitBytes) { reject(new Error('body too large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function sendJson(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { 'content-type': 'application/json', 'cache-control': 'no-store' });
  res.end(body);
}

async function handleReviewRoute(req, res, url) {
  const p = url.pathname;
  if (p === '/__review__/' || p === '/__review__') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' });
    res.end(statusPage());
    return;
  }
  if (p === '/__review__/overlay.js') {
    res.writeHead(200, { 'content-type': 'application/javascript; charset=utf-8', 'cache-control': 'no-store' });
    res.end(OVERLAY_JS);
    return;
  }
  if (p === '/__review__/api/state' && req.method === 'GET') {
    const reviewer = url.searchParams.get('reviewer') || '';
    sendJson(res, 200, { reviewer, items: readReviewerState(reviewer) });
    return;
  }
  if (p === '/__review__/api/state' && req.method === 'POST') {
    try {
      const body = JSON.parse((await readBody(req, 8 * 1024 * 1024)).toString('utf8'));
      if (!body || typeof body.reviewer !== 'string' || !body.reviewer.trim() || !Array.isArray(body.items)) {
        sendJson(res, 400, { error: 'expected { reviewer, items[] }' });
        return;
      }
      writeReviewerState(body.reviewer.trim(), body.items);
      sendJson(res, 200, { ok: true, saved: body.items.length });
    } catch (e) {
      sendJson(res, 400, { error: String(e.message || e) });
    }
    return;
  }
  if (p.startsWith('/__review__/export/')) {
    const { items, reviewers } = readAllItems();
    const kind = p.split('/').pop();
    if (kind === 'feedback.csv') {
      res.writeHead(200, {
        'content-type': 'text/csv; charset=utf-8',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.csv"',
        'cache-control': 'no-store',
      });
      res.end(toCsv(items));
      return;
    }
    if (kind === 'feedback.md') {
      res.writeHead(200, {
        'content-type': 'text/markdown; charset=utf-8',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.md"',
        'cache-control': 'no-store',
      });
      res.end(toMarkdown(items, reviewers));
      return;
    }
    if (kind === 'feedback.json') {
      res.writeHead(200, {
        'content-type': 'application/json',
        'content-disposition': 'attachment; filename="pr185-docs-feedback.json"',
        'cache-control': 'no-store',
      });
      res.end(JSON.stringify({ generatedAt: new Date().toISOString(), pr: PR_URL, reviewers, items }, null, 2));
      return;
    }
  }
  res.writeHead(404, { 'content-type': 'text/plain' });
  res.end('not found');
}

function badGateway(res, err) {
  if (res.headersSent) { try { res.destroy(); } catch { /* already gone */ } return; }
  res.writeHead(502, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><body style="font:15px/1.6 system-ui;max-width:560px;margin:60px auto;padding:0 16px">
<h2>Docs preview is not running</h2>
<p>The review server could not reach the Mintlify preview at <code>${esc(TARGET.origin)}</code>.</p>
<p>In the repo folder, start it first:</p>
<pre style="background:#f0f2f8;padding:12px;border-radius:8px">npm run dev -- --no-open</pre>
<p>then reload this page. If the preview started on a different port, restart this server with
<code>node review-server.mjs --target http://localhost:&lt;port&gt;</code>.</p>
<p style="color:#888">(${esc(err.message || err)})</p></body></html>`);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  if (url.pathname.startsWith('/__review__')) {
    try { await handleReviewRoute(req, res, url); } catch (e) { sendJson(res, 500, { error: String(e.message || e) }); }
    return;
  }

  const headers = { ...req.headers, host: TARGET.host, 'accept-encoding': 'identity' };
  const upstream = http.request(
    { hostname: TARGET.hostname, port: TARGET.port || 80, path: req.url, method: req.method, headers },
    (up) => {
      const outHeaders = { ...up.headers };
      delete outHeaders['content-security-policy'];
      delete outHeaders['content-security-policy-report-only'];
      if (outHeaders.location && outHeaders.location.startsWith(TARGET.origin)) {
        outHeaders.location = outHeaders.location.slice(TARGET.origin.length) || '/';
      }
      const ctype = String(up.headers['content-type'] || '');
      if (ctype.includes('text/html') && req.method !== 'HEAD') {
        const chunks = [];
        up.on('data', (c) => chunks.push(c));
        up.on('end', () => {
          const html = injectOverlay(Buffer.concat(chunks).toString('utf8'));
          delete outHeaders['content-length'];
          delete outHeaders['transfer-encoding'];
          outHeaders['content-length'] = Buffer.byteLength(html);
          res.writeHead(up.statusCode, outHeaders);
          res.end(html);
        });
        up.on('error', () => { try { res.destroy(); } catch {} });
      } else {
        res.writeHead(up.statusCode, outHeaders);
        up.pipe(res);
        up.on('error', () => { try { res.destroy(); } catch { /* already gone */ } });
      }
    }
  );
  upstream.on('error', (err) => badGateway(res, err));
  req.pipe(upstream);
});

// websocket passthrough (Next.js HMR etc.)
server.on('upgrade', (req, socket, head) => {
  const upstream = net.connect(Number(TARGET.port || 80), TARGET.hostname, () => {
    let raw = `${req.method} ${req.url} HTTP/1.1\r\n`;
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      const k = req.rawHeaders[i];
      const v = k.toLowerCase() === 'host' ? TARGET.host : req.rawHeaders[i + 1];
      raw += `${k}: ${v}\r\n`;
    }
    raw += '\r\n';
    upstream.write(raw);
    if (head && head.length) upstream.write(head);
    socket.pipe(upstream);
    upstream.pipe(socket);
  });
  upstream.on('error', () => socket.destroy());
  socket.on('error', () => upstream.destroy());
});

server.listen(PORT, () => {
  console.log('');
  console.log('  Vast.ai docs review server (PR #185)');
  console.log('  ------------------------------------');
  console.log(`  Review the docs at:   http://localhost:${PORT}/host/hosting-overview`);
  console.log(`  Proxying preview at:  ${TARGET.origin}  (start it with: npm run dev -- --no-open)`);
  console.log(`  Feedback saved to:    ${FEEDBACK_DIR}`);
  console.log(`  Status & exports:     http://localhost:${PORT}/__review__/`);
  console.log('');
});
