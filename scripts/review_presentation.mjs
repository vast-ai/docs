import fs from 'node:fs';
import path from 'node:path';

export const PRESENTATION_ROUTE = '/__review__/presentation/';
const PAGES = new Set([
  'index.html', 'owner-questions.html', 'host-docs-review.html', 'reviewer-setup.html',
  'review-resources.html', 'retained-cleanup.html', 'walkthrough.css', 'reviewer-setup.css',
  'walkthrough.js', 'walkthrough-scenes.js', 'attention-cues.js', 'guidance.js',
  'guidance-timing.js', 'owner-questions-data.json', 'speaker-script.md',
  'runtime-account-evidence.md',
  'attention-cues.json', 'README.md', 'START-HERE.txt',
  'references/original-rental-cleanup.json', 'references/github-locations.json',
  'references/github-locations.md',
]);
const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.png': 'image/png', '.webp': 'image/webp',
  '.txt': 'text/plain; charset=utf-8',
  '.mp4': 'video/mp4', '.wav': 'audio/wav',
  '.vtt': 'text/vtt; charset=utf-8', '.srt': 'application/x-subrip; charset=utf-8',
};

function allowedFile(file) {
  return PAGES.has(file)
    || /^assets\/[A-Za-z0-9][A-Za-z0-9._-]*\.png$/.test(file)
    || /^deliverables\/host-docs-review-walkthrough\/[A-Za-z0-9][A-Za-z0-9._-]*\.(?:mp4|wav|vtt|srt)$/.test(file);
}

function reply(req, res, status, message, headers = {}) {
  res.writeHead(status, { 'content-type': 'text/plain; charset=utf-8',
    'x-content-type-options': 'nosniff', 'cache-control': 'no-store', ...headers });
  res.end(req.method === 'HEAD' ? undefined : message);
}

// A single byte range is sufficient for native video/audio seeking. Unsupported
// or unsatisfiable ranges fail explicitly instead of returning incorrect bytes.
function byteRange(value, size) {
  const match = /^bytes=(\d*)-(\d*)$/.exec(value);
  if (!match || (!match[1] && !match[2]) || !size) return null;
  let start = match[1] ? Number(match[1]) : null;
  let end = match[2] ? Number(match[2]) : null;
  if ((start !== null && !Number.isSafeInteger(start)) ||
      (end !== null && !Number.isSafeInteger(end))) return null;
  if (start === null) {
    if (end === 0) return null;
    start = Math.max(0, size - end);
    end = size - 1;
  } else {
    end = end === null ? size - 1 : Math.min(end, size - 1);
  }
  return start < size && start <= end ? { start, end } : null;
}

export async function serveReviewPresentation(req, res, directory) {
  // Inspect the raw path before URL normalization can erase a traversal segment.
  const rawPath = String(req.url || '').split('?')[0];
  if (rawPath !== PRESENTATION_ROUTE.slice(0, -1) && !rawPath.startsWith(PRESENTATION_ROUTE)) return false;
  if (!['GET', 'HEAD'].includes(req.method)) {
    reply(req, res, 405, 'Presentation files are read-only.', { allow: 'GET, HEAD' });
    return true;
  }
  if (rawPath === PRESENTATION_ROUTE.slice(0, -1)) {
    reply(req, res, 308, 'Use the presentation directory URL.', { location: PRESENTATION_ROUTE });
    return true;
  }
  let file;
  try { file = decodeURIComponent(rawPath.slice(PRESENTATION_ROUTE.length)) || 'index.html'; }
  catch { reply(req, res, 400, 'Invalid presentation path.'); return true; }
  if (!allowedFile(file)) {
    reply(req, res, 404, 'Presentation file not found.');
    return true;
  }
  let fd;
  try {
    let current = path.resolve(directory);
    const rootStat = fs.lstatSync(current);
    if (rootStat.isSymbolicLink() || !rootStat.isDirectory()) throw new Error('invalid presentation directory');
    const parts = file.split('/');
    for (let i = 0; i < parts.length; i += 1) {
      current = path.join(current, parts[i]);
      const stat = fs.lstatSync(current);
      if (stat.isSymbolicLink() || (i < parts.length - 1 ? !stat.isDirectory() : !stat.isFile())) {
        throw new Error('invalid presentation file');
      }
    }
    fd = fs.openSync(current, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW || 0));
    const stat = fs.fstatSync(fd);
    if (!stat.isFile()) throw new Error('invalid presentation file');
    const headers = {
      'content-type': MIME[path.extname(file)], 'content-length': stat.size,
      'accept-ranges': 'bytes', 'x-content-type-options': 'nosniff', 'cache-control': 'no-store',
    };
    let range = null;
    if (req.method === 'GET' && req.headers.range !== undefined) {
      range = byteRange(req.headers.range, stat.size);
      if (!range) {
        fs.closeSync(fd); fd = undefined;
        reply(req, res, 416, 'Requested range is not satisfiable.', { 'content-range': `bytes */${stat.size}` });
        return true;
      }
      headers['content-range'] = `bytes ${range.start}-${range.end}/${stat.size}`;
      headers['content-length'] = range.end - range.start + 1;
    }
    res.writeHead(range ? 206 : 200, headers);
    if (req.method === 'HEAD' || stat.size === 0) {
      fs.closeSync(fd); fd = undefined; res.end();
    } else {
      const stream = fs.createReadStream(current, { fd, autoClose: true, ...(range || {}) });
      fd = undefined; // The stream now owns the descriptor.
      stream.on('error', () => res.destroy());
      res.on('close', () => stream.destroy());
      stream.pipe(res);
    }
  } catch {
    if (fd !== undefined) fs.closeSync(fd);
    if (res.headersSent) res.destroy();
    else reply(req, res, 404, 'Presentation file not found.');
  }
  return true;
}
