// Strict, package-free source integrity check for the premium CN vNext prototype.
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Script } from 'node:vm';
import assert from 'node:assert/strict';
const dir = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(dir, 'premium-index.html'), 'utf8');
const css = readFileSync(resolve(dir, 'premium.css'), 'utf8');
const js = readFileSync(resolve(dir, 'premium.js'), 'utf8');
const source = JSON.parse(readFileSync(resolve(dir, 'seed.json'), 'utf8'));
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
const unique = new Set(ids);
assert.equal(ids.length, unique.size, 'Duplicate HTML ids');
for (const expected of ['page-overblik', 'page-kompas', 'page-dokumentation', 'horizon-body', 'asset-body', 'range-visualization', 'history-full', 'source-dialog']) {
  assert.ok(unique.has(expected), 'Missing required UI section: ' + expected);
}
for (const match of [...js.matchAll(/\$\('([^']+)'\)/g), ...js.matchAll(/setText\('([^']+)'/g)]) {
  assert.ok(unique.has(match[1]), 'JavaScript targets nonexistent HTML ID: ' + match[1]);
}
assert.match(css, /prefers-reduced-motion: reduce/);
assert.match(css, /@media \(max-width: 580px\)/);
assert.doesNotMatch(js, /Math\.random\(/);
assert.doesNotMatch(js, /innerHTML\s*=/, 'No interpolation of untrusted HTML markup');
assert.match(html, /CycleNavigator-scores/);
assert.match(html, /KILDEFAST SNAPSHOT, IKKE LIVE TRADING/);
assert.match(js, /source_status !== 'POINT_IN_TIME_PREVIEW_ARCHIVE_NOT_LIVE'/);
assert.match(js, /compass\.data_status !== 'OK'/);
assert.match(js, /score\.market_structure_precision !== null/);
assert.match(js, /history\.records\.length !== 27/);
assert.match(js, /c\.sell_assessment\?\.state/);
assert.equal(source.contract, 'CN_VNEXT_PREVIEW_SOURCE_BUNDLE_v1');
assert.equal(source.source_status, 'POINT_IN_TIME_PREVIEW_ARCHIVE_NOT_LIVE');
assert.equal(source.weekly.public_issue_number, 28);
assert.equal(source.weekly.forecast_week, '2026-W41');
assert.equal(source.weekly.status, 'DEGRADED');
assert.equal(source.completed_score.public_issue_number, 27);
assert.equal(source.completed_score.forecast_week, '2026-W40');
assert.equal(source.completed_score.price_range_precision.formula, '70pct_containment_plus_30pct_jaccard');
assert.equal(source.completed_score.price_range_precision.rows.length, 6);
assert.equal(source.completed_score.market_structure_precision, null);
assert.equal(source.completed_score.combined_score, null);
assert.equal(source.history.policy.cross_era_aggregate, false);
assert.deepEqual(source.history.records.map((x) => x.cn), Array.from({length:27}, (_,i)=>i+1));
assert.equal(source.compass.horizons.NEXT_12H.expected_direction, 'UP');
assert.equal(source.compass.action_now, 'HOLD_WAIT');
assert.equal(source.compass.sell_assessment.state, 'UNAVAILABLE');
new Script(js, { filename: 'premium.js' });
console.log('PASS: premium CN source lineage, forecast/score semantics, UI IDs, safe DOM rendering, mobile CSS, JavaScript syntax');
console.log('Reminder: this is static smoke/contract QA. It does not certify iPhone visual quality or ex-ante cryptographic score proof.');
