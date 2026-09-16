'use strict';
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  let activeCue = null;
  const make = (tag, attrs = {}, text = null) => {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (text !== null) el.textContent = text;
    return el;
  };
  window.guidanceFor = (scene, sentence) => (window.attentionCues?.scenes?.find(s => s.scene === scene)?.cues || []).find(c => sentence >= c.sentenceStart && sentence <= c.sentenceEnd) || null;
  function paint() {
    const layer = document.getElementById('attention-layer'), image = document.getElementById('scene-image');
    if (!activeCue || image.hidden || !image.naturalWidth) { layer.setAttribute('hidden', ''); return; }
    const outer = document.getElementById('capture').getBoundingClientRect(), box = image.getBoundingClientRect();
    const W = image.naturalWidth, H = image.naturalHeight, scale = Math.min(box.width / W, box.height / H);
    Object.assign(layer.style, {left: `${box.left - outer.left + (box.width - W * scale) / 2}px`, top: `${box.top - outer.top + (box.height - H * scale) / 2}px`, width: `${W * scale}px`, height: `${H * scale}px`});
    layer.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const cue = activeCue, color = cue.kind === 'click' ? '#ed591f' : '#087e8b';
    const [x, y, w, h] = cue.rect.map((v, i) => v * (i % 2 ? H : W));
    const measure = document.createElement('canvas').getContext('2d');
    measure.font = '700 23px "Avenir Next", "Segoe UI", sans-serif';
    const labelWidth = Math.min(W - 24, Math.max(190, Math.ceil(measure.measureText(cue.label).width) + 36)), labelHeight = 48;
    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
    let lx = clamp(cue.labelAt[0] * W, 12, W - labelWidth - 12), ly = clamp(cue.labelAt[1] * H, 12, H - labelHeight - 12);
    const overlaps = (a, b) => a < x + w + 10 && a + labelWidth > x - 10 && b < y + h + 10 && b + labelHeight > y - 10;
    if (overlaps(lx, ly)) {
      const candidates = [[lx, y - labelHeight - 20], [lx, y + h + 20], [x - labelWidth - 22, ly], [x + w + 22, ly]];
      const candidate = candidates.find(([a,b]) => a >= 12 && b >= 12 && a + labelWidth <= W - 12 && b + labelHeight <= H - 12 && !overlaps(a,b));
      if (candidate) [lx,ly] = candidate;
    }
    const defs = make('defs'), mask = make('mask', {id:'attention-mask', maskUnits:'userSpaceOnUse', x:0,y:0,width:W,height:H});
    mask.append(make('rect',{width:W,height:H,fill:'white'}), make('rect',{x:x-5,y:y-5,width:w+10,height:h+10,rx:6,fill:'black'}));
    const marker = make('marker',{id:'attention-arrow',viewBox:'0 0 12 12',refX:10,refY:6,markerWidth:14,markerHeight:14,orient:'auto',markerUnits:'userSpaceOnUse'});
    marker.append(make('path',{d:'M 1 1 L 11 6 L 1 11 Z',fill:color})); defs.append(mask,marker);
    const children = [defs,make('rect',{width:W,height:H,fill:'#061b24',opacity:.16,mask:'url(#attention-mask)'}),make('rect',{x:x-4,y:y-4,width:w+8,height:h+8,rx:6,fill:'none',stroke:'white','stroke-width':8}),make('rect',{x:x-4,y:y-4,width:w+8,height:h+8,rx:6,fill:'none',stroke:color,'stroke-width':4})];
    // Keep the pointer outside highlighted text; arrowTo determines its direction.
    const aim = cue.arrowTo ? [cue.arrowTo[0]*W,cue.arrowTo[1]*H] : [x+w/2,y+h/2];
    const center = [lx+labelWidth/2,ly+labelHeight/2];
    const edgePoint = (cx,cy,tx,ty,bx,by,bw,bh) => {
      const dx=tx-cx,dy=ty-cy, hits=[];
      for(const px of [bx,bx+bw])if(dx){const t=(px-cx)/dx, py=cy+t*dy;if(t>=0&&t<=1&&py>=by&&py<=by+bh)hits.push([t,px,py]);}
      for(const py of [by,by+bh])if(dy){const t=(py-cy)/dy, px=cx+t*dx;if(t>=0&&t<=1&&px>=bx&&px<=bx+bw)hits.push([t,px,py]);}
      hits.sort((a,b)=>a[0]-b[0]);return hits.length?hits[0].slice(1):[tx,ty];
    };
    const start=edgePoint(...aim,...center,lx,ly,labelWidth,labelHeight), end=edgePoint(...center,...aim,x-10,y-10,w+20,h+20);
    children.push(make('path',{d:`M ${start[0]} ${start[1]} L ${end[0]} ${end[1]}`,fill:'none',stroke:'white','stroke-width':8,'stroke-linecap':'round'}),make('path',{d:`M ${start[0]} ${start[1]} L ${end[0]} ${end[1]}`,fill:'none',stroke:color,'stroke-width':4,'marker-end':'url(#attention-arrow)'}));
    children.push(make('rect',{x:lx,y:ly,width:labelWidth,height:labelHeight,rx:8,fill:color,stroke:'white','stroke-width':2}),make('text',{x:lx+18,y:ly+31,fill:'white','font-size':23,'font-weight':700,'font-family':'Avenir Next, Segoe UI, sans-serif'},cue.label));
    layer.replaceChildren(...children); layer.removeAttribute('hidden');
    layer.dataset.cueId = cue.id;
    layer.dataset.labelOverlapsTarget = String(overlaps(lx,ly));
  }
  window.drawGuidance = cue => {
    activeCue = cue;
    const text = document.getElementById('focus-description');
    if (text) text.textContent = cue ? `${cue.kind === 'click' ? 'Click target' : 'Look here'}: ${cue.label}` : 'Full view';
    paint();
  };
  window.addEventListener('resize', paint);
})();
