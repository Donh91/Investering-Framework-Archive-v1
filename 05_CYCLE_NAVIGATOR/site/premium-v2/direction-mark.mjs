/**
 * Directional Vector v1 · presentation only.
 * Maps already source-issued direction ENUMS to a stable decorative glyph.
 * It has no forecast, confidence, permission, timing or scoring authority.
 * Glyphs are always aria-hidden; visible text stays the accessible reading.
 */
const NS='http://www.w3.org/2000/svg';
const KINDS=Object.freeze({
 UP:'up', BULLISH:'up', DOWN:'down', BEARISH:'down',
 MIXED:'mixed', SIDEWAYS:'flat', NEUTRAL:'flat',
 LEAN_BULLISH:'lean-up', LEAN_BEARISH:'lean-down',
 UNAVAILABLE:'missing'
});
const PATHS=Object.freeze({
 up:['M5 18L18 5','M10.5 5H18v7.5'],
 down:['M5 5L18 18','M10.5 18H18v-7.5'],
 mixed:['M4.5 8H19','M14.5 4l4.5 4-4.5 4','M19.5 16H5','M9.5 12L5 16l4.5 4'],
 flat:['M5.5 12h13','M14.5 8l4 4-4 4'],
 missing:['M7 12h10']
});
export function vectorKind(source){
 return typeof source==='string'&&Object.hasOwn(KINDS,source)?KINDS[source]:null;
}
function svg(doc,kind){
 const output=doc.createElementNS(NS,'svg');
 output.setAttribute('viewBox','0 0 24 24');
 output.setAttribute('width','21');
 output.setAttribute('height','21');
 output.setAttribute('fill','none');
 output.setAttribute('stroke','currentColor');
 output.setAttribute('stroke-width','1.8');
 output.setAttribute('stroke-linecap','round');
 output.setAttribute('stroke-linejoin','round');
 output.setAttribute('focusable','false');
 output.setAttribute('aria-hidden','true');
 output.setAttribute('class','cn-direction-svg');
 const stem=kind.startsWith('lean-')?(kind==='lean-up'?'up':'down'):kind;
 for(const [index,d] of PATHS[stem].entries()){
  const p=doc.createElementNS(NS,'path');p.setAttribute('d',d);
  if(kind.startsWith('lean-')&&index===0)
   p.setAttribute('stroke-dasharray','3 3');
  output.append(p);
 }
 return output;
}
export function makeDirectionMark(doc,source){
 const kind=vectorKind(source);
 if(!kind)return null;
 const node=doc.createElement('span');
 node.className='cn-direction-mark';
 node.dataset.directionMark=kind;
 node.setAttribute('aria-hidden','true');
 node.append(svg(doc,kind));
 return node;
}
/** Called AFTER legacy arrow text is written; preserves textContent for QA. */
export function enhanceLegacyArrow(doc,node,source){
 if(!node)return false;
 const kind=vectorKind(source);
 if(!kind)return false;
 node.dataset.directionMark=kind;
 node.append(svg(doc,kind)); // SVG has NO text, textContent stays original.
 return true;
}
/** Split visible label from prior arrow text, preserving textContent byte order. */
export function enhanceLegacyLabel(doc,node,source,legacyArrow){
 if(!node)return false;
 const mark=makeDirectionMark(doc,source);
 if(!mark)return false;
 const original=node.textContent??'';
 const prefix=legacyArrow!=='?'&&original.startsWith(legacyArrow+' ')?
  legacyArrow+' ':'';
 const visible=original.slice(prefix.length);
 if(!visible)return false;
 const text=doc.createElement('span');
 text.className='cn-direction-readable';
 text.textContent=visible;
 const hidden=doc.createElement('span');
 hidden.className='cn-direction-legacy';
 hidden.setAttribute('aria-hidden','true');
 hidden.textContent=prefix;
 node.classList.add('cn-direction-inline');
 node.replaceChildren(hidden,mark,text);
 return node.textContent===original;
}
