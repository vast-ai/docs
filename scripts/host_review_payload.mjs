import {gzipSync} from 'node:zlib';

/** Lossless storage only; the decoded report and its artifact digests are unchanged. */
export function encodeHostReviewPayload(payload) {
  return {encoding:'gzip-base64',data:gzipSync(Buffer.from(JSON.stringify(payload),'utf8')).toString('base64')};
}

// This exact function is embedded in the offline HTML. Keep it browser-native
// and self-contained so tests and the single-file reader use the same decoder.
export async function decodeHostReviewPayload(envelope) {
  if (!envelope || envelope.encoding !== 'gzip-base64' || typeof envelope.data !== 'string' ||
      !envelope.data.length || envelope.data.length % 4 || /[^A-Za-z0-9+/=]/.test(envelope.data)) {
    throw new Error('Unsupported or malformed report encoding.');
  }
  if (typeof DecompressionStream !== 'function') throw new Error('This browser cannot decompress the offline report. Open it in a current Chrome, Edge, Firefox or Safari browser.');
  const bytes=Uint8Array.from(atob(envelope.data),character=>character.charCodeAt(0));
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(await new Response(stream).text());
}

export async function readEmbeddedHostReviewPayload(html) {
  const data=html.match(/<script id="report-data" type="application\/json">([\s\S]*?)<\/script>/)?.[1];
  if (!data) throw new Error('Embedded report data is missing.');
  return decodeHostReviewPayload(JSON.parse(data));
}
