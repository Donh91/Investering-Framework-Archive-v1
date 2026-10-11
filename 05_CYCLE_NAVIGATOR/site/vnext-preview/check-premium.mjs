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
const i18n = readFileSync(resolve(dir, 'premium-i18n.js'), 'utf8');
const source = JSON.parse(readFileSync(resolve(dir, 'seed.json'), 'utf8'));
const motionLibrary = readFileSync(resolve(dir, 'MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md'), 'utf8');
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
assert.equal(source.compass.protection_tracker.pullback_risk_state, 'BUILDING');
assert.equal(source.compass.protection_tracker.distribution_risk, 'UNKNOWN');
assert.equal(source.compass.sell_assessment.state, 'UNAVAILABLE');
assert.equal(source.compass.protection_tracker.reentry_state, 'INACTIVE');
assert.equal(source.compass.capitalization_ladder.find((x) => x.segment === 'MEMES')?.action, 'UNAVAILABLE');
assert.equal(source.compass.compass_id, 'CMP-20261011-7d14a9ee5914');
assert.equal(source.compass.issued_at_utc, '2026-10-11T13:15:27Z');
assert.equal(source.compass.sell_assessment.state, 'UNAVAILABLE');
assert.match(html, /data-lang="da"/);
assert.match(html, /data-lang="en"/);
assert.match(js, /import \{ initializeLanguage, translateInterface, selectLanguage \} from '\.\/premium-i18n\.js'/);
assert.match(i18n, /document\.documentElement\.lang = language/);
assert.match(html, /id="range-replay"/);
assert.match(html, /data-motion-step="frozen"/);
assert.match(html, /data-motion-step="actual"/);
assert.match(html, /data-motion-step="score"/);
assert.match(html, /class="edge-legacy-fold"/);
assert.match(js, /function playRangeComparison\(\)/);
assert.match(js, /setRangeRevealPhase\('frozen'\)/);
assert.match(js, /setRangeRevealPhase\('actual'\)/);
assert.match(js, /setRangeRevealPhase\('score'\)/);
assert.match(js, /prefers-reduced-motion: reduce/);
assert.match(js, /\.edge-legacy-fold/);
assert.match(css, /\.range-compare-panel\[data-reveal-phase="frozen"\]/);
assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
assert.match(i18n, /Replay comparison/);
assert.equal([...motionLibrary.matchAll(/^\| (?:0[1-9]|1[0-9]|20) \|/gm)].length, 20, 'All 20 image-sourced design repositories must be preserved');

new Script(js.replace(/^import .*from .*;\s*$/m, ''), { filename: 'premium.js' });
new Script(i18n.replace(/export (?=function)/g, ''), { filename: 'premium-i18n.js' });

assert.match(html, /aria-controls="cycle-details"/);
assert.ok(html.includes('<div class="hero-action-line"><span>OFFICIAL ACTION</span>'));
]*OFFICIAL ACTION/);
assert.ok(css.indexOf('.hero-action-line { display: flex') > css.indexOf('@media (max-width: 580px)'), 'Action summary must remain mobile-only');
assert.match(js, /setText\('hero-action-summary', actionView\(c\.action_now\)\.text\)/);
assert.match(html, /NEXT SERIES · ISSUE ID PENDING · 2026-W42/);
assert.doesNotMatch(html, /Public CN #29/);
assert.match(js, /KILDEFAST SNAPSHOT · ' \+ c\.issued_at_utc\.slice\(0, 16\)/);
assert.match(js, /compass\.compass_id !== 'CMP-20261011-7d14a9ee5914'/);
assert.match(js, /compass\.issued_at_utc !== '2026-10-11T13:15:27Z'/);
assert.match(js, /if \(dialog\.hidden\) return;/);
assert.match(js, /event\.key !== 'Tab'/);
assert.match(js, /e\.currentTarget\.setAttribute\('aria-expanded', String\(!details\.hidden\)\)/);
const requiredLocalizedText = [
  'The near-term market direction is positive, but expanding broad altcoin exposure is not authorized.',
  'ORDINARY RETEST WATCH; DEPTH AND SEVERITY UNQUANTIFIED. · Possible W41 retest, particularly Day 3–7; timing and occurrence unconfirmed.',
  'No governed sell/trim decision owner is bound. Protection and distribution risk are not sell instructions.',
  'THE NEW CN TRACK RECORD',
  'OFFICIAL ACTION',
  'NEXT SERIES · ISSUE ID PENDING · 2026-W42'
];
for (const phrase of requiredLocalizedText) assert.ok(i18n.includes(JSON.stringify(phrase) + ':'), 'Missing Danish translation: ' + phrase);


const sourceFn = js.match(/function getTrustedSeed\(raw\) \{[\s\S]*?\n\}/)?.[0];
const rangeFn = js.match(/function completePriceRows\(score, asset\) \{[\s\S]*?\n\}/)?.[0];
assert.ok(sourceFn, 'Trusted-source validation function exists');
assert.ok(rangeFn, 'Price-range eligibility function exists');
const getTrustedSeed = new Function(sourceFn + '; return getTrustedSeed;')();
const completePriceRows = new Function('safeNumber', rangeFn + '; return completePriceRows;')((n) => typeof n === 'number' && Number.isFinite(n));
assert.equal(getTrustedSeed(source), source);
for (const mutate of [
  (x) => { x.source_status = 'LIVE'; },
  (x) => { x.weekly.public_issue_number = 29; },
  (x) => { x.compass.compass_id = 'CMP-WRONG-WEEK'; },
  (x) => { x.compass.issued_at_utc = '2026-10-11T20:19:43Z'; },
  (x) => { x.completed_score.combined_score = 100; },
  (x) => { x.history.records.pop(); }
]) {
  const invalid = structuredClone(source);
  mutate(invalid);
  assert.throws(() => getTrustedSeed(invalid), 'Invalid or misaligned source must fail closed');
}
const priceScore = structuredClone(source.completed_score);
const btcRows = priceScore.price_range_precision.rows.filter((row) => row.asset === 'BTC');
assert.equal(completePriceRows(priceScore, 'BTC').length, 3, 'Valid BTC intervals remain eligible');
assert.equal(completePriceRows({ price_range_precision: { rows: [] } }, 'BTC').length, 0, 'Missing price rows fail closed');
assert.equal(completePriceRows({ price_range_precision: { rows: [btcRows[0]] } }, 'BTC').length, 1, 'Partial intervals remain incomplete');
const damaged = structuredClone(priceScore);
damaged.price_range_precision.rows[0].actual_high = null;
assert.equal(completePriceRows(damaged, 'BTC').length, 2, 'Missing actual bar is excluded');

console.log('PASS: premium CN source lineage, fail-closed fixtures, bilingual copy, score semantics, modal keyboard and JavaScript syntax');
console.log('Reminder: this is static smoke/contract QA. It does not certify iPhone visual quality or ex-ante cryptographic score proof.');
