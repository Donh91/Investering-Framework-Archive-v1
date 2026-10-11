// Cycle Navigator vNext draft prototype smoke checks. No npm packages required.
import { readFileSync } from 'node:fs';
import { Script } from 'node:vm';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';

const root = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(root, 'index.html'), 'utf8');

for (const id of ['view-overview', 'view-compass', 'view-proof', 'horizonRows', 'assetRows', 'score', 'riskStatus', 'sellState']) {
  assert.match(html, new RegExp('id="' + id + '"'), 'Missing critical semantic target: ' + id);
}
for (const view of ['overview', 'compass', 'proof']) {
  assert.match(html, new RegExp('data-view="' + view + '"'), 'Missing tab ' + view);
}
assert.match(html, /prefers-reduced-motion:reduce/, 'Reduced-motion mode required');
assert.match(html, /390px|720px/, 'Mobile breakpoint missing');
assert.match(html, /CycleNavigator-scores/, 'Independent proof navigation missing');
assert.match(html, /CN_PUBLIC_SNAPSHOT_V2/, 'Public snapshot contract missing');
assert.match(html, /PUBLIC_COMPASS_PROJECTION_v1/, 'Public Compass contract missing');
assert.match(html, /status==="ALIGNED"/, 'Compass/CN binding guard missing');
const marketPath = html.match(/id="phase"[\s\S]*?<div class="rule"/)?.[0] || '';
assert.ok(marketPath, 'Missing market timeline section');
assert.doesNotMatch(marketPath, /<div class="step present">/, 'Market timeline cannot pretend a current checkpoint');
assert.doesNotMatch(html, /\bMath\.random\(/, 'No fictitious motion/random signal');
assert.doesNotMatch(html, /<script[^>]+src=/, 'Prototype must remain self-contained');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length, 1, 'One bounded runtime script');
new Script(scripts[0][1], { filename: 'index.html inline script' });
console.log('PASS: vNext draft prototype markup, authority guards and JavaScript syntax');
console.log('NOTE: Browser interaction, iPhone Safari, screenshots, contrast and performance are NOT tested here.');
