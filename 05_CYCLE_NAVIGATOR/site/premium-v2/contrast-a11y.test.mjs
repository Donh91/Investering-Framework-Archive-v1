// Static WCAG AA guard for NEXT header label and language controls.
// Presentation-only: no source or Graph B forecast logic changes.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const css=readFileSync(new URL('./premium-overhaul.css',import.meta.url),'utf8');
function rule(selector) {
  const at=css.indexOf(selector+' {');
  assert.ok(at>=0,'MISSING_STYLE_RULE: '+selector);
  const open=css.indexOf('{',at),close=css.indexOf('}',open);
  assert.ok(close>open,'MALFORMED_STYLE_RULE: '+selector);
  return css.slice(open+1,close);
}
function foreground(selector) {
  const declaration=rule(selector).match(/(?:^|[;\s])color:\s*(#[0-9a-fA-F]{6})\s*;/);
  assert.ok(declaration,'MISSING_EXPLICIT_TEXT_COLOR: '+selector);
  return declaration[1];
}
function luminance(hex) {
  const c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255)
    .map(n=>n<=0.04045?n/12.92:((n+0.055)/1.055)**2.4);
  return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2];
}
function contrast(a,b) {
  const [light,dark]=[luminance(a),luminance(b)].sort((x,y)=>y-x);
  return (light+0.05)/(dark+0.05);
}
test('NEXT 9px header identity is WCAG AA normal text on light backgrounds',()=>{
  const color=foreground('.premium-next .dev-brand span');
  for(const surface of ['#ffffff','#f2f4f7'])
    assert.ok(contrast(color,surface)>=4.5,
      'NEXT_BRAND_CONTRAST_BELOW_4_5 '+color+' on '+surface);
  assert.ok(contrast('#68819c','#f2f4f7')<4.5,
    'NEGATIVE_CONTROL_MUST_DETECT_PREVIOUS_BRAND_COLOR');
});
test('NEXT language controls maintain WCAG AA contrast in inactive state',()=>{
  const color=foreground('.premium-next .dev-lang button');
  for(const surface of ['#ffffff','#f2f4f7','#e9eef4'])
    assert.ok(contrast(color,surface)>=4.5,
      'NEXT_LANGUAGE_CONTRAST_BELOW_4_5 '+color+' on '+surface);
  assert.ok(contrast('#657e99','#e9eef4')<4.5,
    'NEGATIVE_CONTROL_MUST_DETECT_PREVIOUS_LANGUAGE_COLOR');
});
