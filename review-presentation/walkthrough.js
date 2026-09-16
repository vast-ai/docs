'use strict';

(() => {
  const params = new URLSearchParams(location.search);
  const recordMode = params.get('record') === '1';
  document.body.classList.toggle('record', recordMode);
  const scenes = Array.isArray(window.walkthroughScenes) ? window.walkthroughScenes : [];
  const $ = id => document.getElementById(id);
  const image = $('scene-image');
  let activeIndex = 0;
  let renderToken = 0;
  let activeSentence = 1;

  window.walkthroughReady = false;
  window.walkthroughState = { ready: false, recordMode, sceneNumber: null, total: scenes.length };

  function usableUrl(value, { imagePath = false } = {}) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value, location.href);
      if (!['http:', 'https:', 'file:'].includes(url.protocol)) return null;
      if (imagePath && url.username) return null;
      return url.href;
    } catch { return null; }
  }

  function requestedIndex(value) {
    if (typeof value === 'string' && /^\d+$/.test(value)) {
      return Math.max(0, Math.min(scenes.length - 1, Number(value) - 1));
    }
    const match = scenes.findIndex(scene => String(scene.id) === String(value));
    return match < 0 ? 0 : match;
  }

  function setStatus(message, error = false) {
    $('capture-status').textContent = message;
    $('capture-status').classList.toggle('error', error);
    $('capture-status').hidden = false;
    image.hidden = true;
    $('attention-layer').setAttribute('hidden', '');
  }

  function updateLinks(scene, source) {
    const links = Array.isArray(scene.links) ? scene.links : [];
    const safeLinks = links.map(link => ({ label: String(link.label || 'Open linked page'), url: usableUrl(link.url) })).filter(link => link.url);
    $('scene-links').replaceChildren(...safeLinks.map(link => {
      const a = document.createElement('a');
      a.className = 'action-link';
      a.href = link.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = `${link.label} ↗`;
      return a;
    }));
    const live = safeLinks.find(link => {
      const url = new URL(link.url);
      return ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname) && url.port === '4000' && !url.pathname.startsWith('/__review__/');
    });
    $('open-overlay').href = live ? live.url : 'http://localhost:4000/';
    $('full-image').hidden = !source;
    if (source) $('full-image').href = source;
  }

  async function render(index, { updateUrl = true, sentenceNumber = 1 } = {}) {
    activeIndex = Math.max(0, Math.min(scenes.length - 1, index));
    const scene = scenes[activeIndex];
    if (!scene) return false;
    activeSentence = Number(sentenceNumber);
    const cue = window.guidanceFor(activeIndex + 1, activeSentence);
    const sceneCues = window.attentionCues?.scenes?.find(s => s.scene === activeIndex + 1)?.cues || [];
    $('cue-select').replaceChildren(...sceneCues.map(c => {
      const option = document.createElement('option');
      option.value = String(c.sentenceStart); option.textContent = c.label;
      option.selected = c.id === cue?.id; return option;
    }));
    if (!cue) {
      const option = document.createElement('option'); option.value = String(activeSentence);
      option.textContent = 'Full view — no highlight'; option.selected = true; $('cue-select').prepend(option);
    }
    const token = ++renderToken;
    window.walkthroughReady = false;
    const title = String(scene.title || 'Reviewer walkthrough');
    $('scene-ticket').textContent = scene.ticket ? String(scene.ticket) : 'Actual reviewer · localhost:4000';
    $('scene-title').textContent = title;
    $('scene-action').textContent = String(scene.action || '');
    $('scene-action').hidden = !scene.action;
    $('scene-number').textContent = String(activeIndex + 1).padStart(2, '0');
    $('scene-total').textContent = String(scenes.length).padStart(2, '0');
    $('scene-select').value = String(activeIndex);
    $('previous').disabled = activeIndex === 0;
    $('next').disabled = activeIndex === scenes.length - 1;
    $('scene-limit').textContent = String(scene.limit || '');
    $('scene-limit').hidden = !scene.limit;
    $('scene-voiceover').textContent = String(scene.voiceover || '');
    $('speaker-notes').hidden = !scene.voiceover;
    $('speaker-notes').open = false;
    document.title = `${title} — Host docs reviewer walkthrough`;
    document.body.dataset.scene = String(activeIndex + 1);
    document.body.dataset.sceneId = String(scene.id || activeIndex + 1);
    window.walkthroughState = { ready: false, recordMode, sceneNumber: activeIndex + 1, sceneIndex: activeIndex, sceneId: scene.id, total: scenes.length, sentenceNumber: activeSentence, cueId: cue?.id || null, image: cue?.image || scene.image, imageLoaded: false };
    if (updateUrl) {
      const nextUrl = new URL(location.href);
      nextUrl.searchParams.set('scene', String(activeIndex + 1));
      nextUrl.searchParams.set('sentence', String(activeSentence));
      history.replaceState(null, '', nextUrl);
    }

    const source = usableUrl(cue?.image || scene.image, { imagePath: true });
    updateLinks(scene, source);
    if (!source) {
      setStatus('No capture is supplied for this scene yet.', true);
      return false;
    }
    setStatus('Loading the retained capture…');
    image.alt = `Actual reviewer capture: ${title}`;
    const loaded = new Promise(resolve => {
      image.onload = () => resolve(true);
      image.onerror = () => resolve(false);
    });
    image.src = source;
    let ok = image.complete && image.naturalWidth > 0;
    if (!ok) ok = await loaded;
    if (token !== renderToken) return false;
    if (!ok) {
      setStatus('This capture could not be loaded. Keep the screenshot files with this walkthrough.', true);
      return false;
    }
    if (image.decode) { try { await image.decode(); } catch { /* onload already confirmed the image. */ } }
    if (token !== renderToken) return false;
    image.hidden = false;
    $('capture-status').hidden = true;
    await document.fonts.ready;
    window.drawGuidance(cue);
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    if (token !== renderToken) return false;
    window.walkthroughReady = true;
    window.walkthroughState = { ...window.walkthroughState, ready: true, imageLoaded: true, imageNaturalWidth: image.naturalWidth, imageNaturalHeight: image.naturalHeight };
    $('scene-announcement').textContent = `Scene ${activeIndex + 1} of ${scenes.length}: ${title}`;
    return true;
  }

  function initializeFinishedMedia() {
    // Media metadata works for both file:// and HTTP; no fetch or private browser state is needed.
    // Skip probing entirely during recording so the capture remains deterministic.
    if (recordMode) return;
    const section = $('finished-media');
    const badge = $('media-state');
    const video = $('finished-video');
    const audio = $('finished-audio');
    const available = { video: false, audio: false };
    function update() {
      section.hidden = !available.video && !available.audio;
      $('finished-video-panel').hidden = !available.video;
      $('finished-audio-panel').hidden = !available.audio;
      $('refresh-media').hidden = available.video && available.audio;
      badge.textContent = available.video ? 'Narrated video ready' : available.audio ? 'Audio ready — video not available yet' : 'Revised walkthrough — media not available yet';
    }
    for (const [name, element, link] of [['video', video, 'download-video'], ['audio', audio, 'download-audio']]) {
      element.addEventListener('loadedmetadata', () => {
        available[name] = Number.isFinite(element.duration) && element.duration > 0;
        update();
      });
      element.addEventListener('error', () => { available[name] = false; update(); });
      element.dataset.mediaUrl = $(link).href;
    }
    function refresh() {
      for (const [name, element] of [['video', video], ['audio', audio]]) {
        if (available[name]) continue; // Do not interrupt an active player when the window gains focus.

        element.src = element.dataset.mediaUrl;
        element.load();
      }
    }
    $('refresh-media').addEventListener('click', refresh);
    window.addEventListener('focus', refresh);
    refresh();
  }
  initializeFinishedMedia();

  $('previous').addEventListener('click', () => render(activeIndex - 1));
  $('next').addEventListener('click', () => render(activeIndex + 1));
  $('scene-select').addEventListener('change', event => render(Number(event.target.value)));
  $('cue-select').addEventListener('change', event => render(activeIndex, {sentenceNumber: Number(event.target.value)}));
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || ['INPUT', 'TEXTAREA', 'SELECT', 'VIDEO', 'AUDIO'].includes(event.target.tagName) || event.target.closest('.finished-media') || event.target.isContentEditable) return;
    const next = { ArrowLeft: activeIndex - 1, ArrowRight: activeIndex + 1, Home: 0, End: scenes.length - 1 }[event.key];
    if (next === undefined || !scenes.length) return;
    event.preventDefault();
    render(next);
  });
  window.addEventListener('popstate', () => render(requestedIndex(new URLSearchParams(location.search).get('scene')), { updateUrl: false }));

  // Optional capture-runner interface. Scene numbers are one-based, like ?scene=1.
  window.renderWalkthroughScene = sceneNumber => render(requestedIndex(String(sceneNumber)));
  window.renderWalkthroughMoment = (sceneNumber, sentenceNumber) => render(requestedIndex(String(sceneNumber)), {updateUrl: false, sentenceNumber});

  if (!scenes.length) {
    $('scene-title').textContent = 'Reviewer walkthrough';
    $('scene-action').textContent = 'The scene data has not been supplied yet.';
    setStatus('Add walkthrough-scenes.js with window.walkthroughScenes, then reload this page.', true);
    return;
  }
  $('scene-select').replaceChildren(...scenes.map((scene, index) => {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = `${String(index + 1).padStart(2, '0')} · ${String(scene.title || scene.id || 'Scene')}`;
    return option;
  }));
  $('scene-select').disabled = false;
  const requestedSentence = params.get('sentence');
  const firstSentence = requestedSentence !== null && /^\d+$/.test(requestedSentence) ? Number(requestedSentence) : 1;
  render(requestedIndex(params.get('scene')), { updateUrl: false, sentenceNumber: firstSentence });
})();
