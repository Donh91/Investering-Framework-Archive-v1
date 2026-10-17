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
assert.match(html, /CN_PUBLIC_SERIES_INDEX_v1/, 'Public series owner contract missing');
// Runtime adversarial source-join check: a fresh but wrong-week Compass is NOT actionable.
const authorityStart = html.indexOf('var sourceFresh=deliveryFresh&&compassFresh');
const authorityEnd = html.indexOf('set("compassHealth",', authorityStart);
assert.ok(authorityStart >= 0 && authorityEnd > authorityStart, 'Compass authority gate not found');
const authorityScript = new Script(html.slice(authorityStart, authorityEnd) + '\n({sourceFresh,aligned,valid})');
const source = {
  data_status:'OK', compass_id:'CMP-TEST',
  weekly_context:{status:'ALIGNED',forecast_week:'2026-W42',public_issue_number:29}
};
const projection = {forecast_week:'2026-W42',public_issue_number:29};
const checkAuthority = (c, pub, deliveryFresh=true, compassFresh=true) =>
  authorityScript.runInNewContext({c,pub,deliveryFresh,compassFresh}).valid;
assert.equal(checkAuthority(source,projection),true,'Matching fresh public source should pass');
assert.equal(checkAuthority({...source,weekly_context:{...source.weekly_context,forecast_week:'2026-W41'}},projection),false,'Wrong week must fail');
assert.equal(checkAuthority({...source,weekly_context:{...source.weekly_context,public_issue_number:28}},projection),false,'Wrong issue must fail');
assert.equal(checkAuthority({...source,weekly_context:undefined},projection),false,'Missing join must fail');
assert.equal(checkAuthority({...source,data_status:'UNAVAILABLE'},projection),false,'Unavailable Compass must fail');
assert.equal(checkAuthority({...source,compass_id:''},projection),false,'Missing source ID must fail');
assert.equal(checkAuthority(source,projection,false,true),false,'Stale CN delivery must fail');
assert.equal(checkAuthority(source,projection,true,false),false,'Stale Compass must fail');
assert.ok(html.includes('set("actionNow",valid?'), 'actionNow must use joined source authority');
assert.ok(html.includes('set("sellState",valid?'), 'sellState must use joined source authority');
assert.ok(html.includes('set("riskStatus",valid?'), 'riskStatus must use joined source authority');
assert.doesNotMatch(html, /id="actionNow">AFVENT</, 'Unverified initial action must not look like official WAIT');

// Regression: unavailable source must never be presented as an official WAIT/HOLD decision.
assert.ok(html.includes('addRow(aroot,[x,"Ukendt","UTILGÆNGELIG"])'), 'Missing source must be unavailable in asset rows');
assert.ok(html.includes('set("actionNow","UTILGÆNGELIG")'), 'Failed source fetch must clear the current action');
assert.ok(html.includes('set("sellState","UNAVAILABLE")'), 'Failed source fetch must clear SELL authority');
assert.ok(!html.includes('set("actionNow",valid?(safe(c.action_now)||"AFVENT"):"AFVENT")'), 'Missing Compass must not look like an official WAIT');

for(const guard of ['weeklyAligned', 'deliveryFresh', 'compassFresh', 'scoreValid', 'actuals_hourly_coverage===168', 'candidate.public_issue_number<pub.public_issue_number']){
  assert.ok(html.includes(guard), 'Public preview must fail closed on missing integrity gate: '+guard);
}
assert.match(html, /\/\^FINAL/, 'Only final source scores may be displayed');
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
