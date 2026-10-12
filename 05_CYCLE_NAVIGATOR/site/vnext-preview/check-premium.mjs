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

new Script(js.replace(/^import .*from .*;\s*$/gm, ''), { filename: 'premium.js' });
new Script(i18n.replace(/export (?=function)/g, ''), { filename: 'premium-i18n.js' });

assert.match(html, /aria-controls="cycle-details"/);
assert.match(html, /<article class="hero-main" aria-labelledby="overview-title">/);
assert.match(html, /id="hero-action-summary"/);
assert.match(html, /id="hero-now"/);
assert.match(html, /id="overview-risk"/);
assert.match(html, /id="overview-risk-window"/);
assert.match(html, /id="compass-risk-window"/);
assert.match(html, /PULLBACK · TID/);
assert.match(js, /import \{ officialPullbackDisplay \} from '\.\/official-pullback-eta\.mjs'/);
assert.match(js, /paintPullback\(d, currentLanguage\(\)\)/);
assert.match(js, /setText\('overview-risk-window', p\.headline\)/);
assert.match(js, /setText\('compass-risk-window', p\.headline\)/);
assert.match(js, /button\.dataset\.lang, \(\) => \{/);
assert.match(css, /\.pullback-brief\{display:flex/);

assert.match(html, /id="source-time"/);
assert.doesNotMatch(html, /CN \/ MARKET INSTRUMENT|hero-instrument|instrument-geometry|path-compass|corridor-track|01 \/ DECISION DESK/, 'Ornamental radar, duplicate action cards and fabricated price corridors must not return');
assert.match(css, /\.hero-key-metrics\s*\{display:grid/);
assert.match(css, /\.hero-detail-list\s*\{display:grid/);
assert.match(css, /\.hero-action-line\s*\{display:flex/);
assert.match(js, /setText\('hero-deck', localizedPulse\(c\)\)/);
assert.match(js, /\.dataset\.direction = currentDirection/);
assert.match(i18n, /"OFFICIELT MARKEDSBILLEDE": "OFFICIAL MARKET OUTLOOK"/);
assert.match(i18n, /"Markedet lige nu": "The market right now"/);
assert.match(i18n, /"BTC og ETH steg i det seneste officielle sammenligningsvindue\./);
assert.match(i18n, /"Retest-watch under opbygning\./);
assert.match(i18n, /content\.startsWith\('KILDEFAST SNAPSHOT · '\)/);
assert.match(i18n, /content\.startsWith\('WEEKLY: '\)/);
assert.match(i18n, /12H/);
assert.match(js, /setText\('hero-action-summary', actionView\(c\.action_now\)\.text\)/);
assert.match(html, /NEXT SERIES · ISSUE ID PENDING · 2026-W42/);
assert.doesNotMatch(html, /Public CN #29/);
assert.match(js, /KILDEFAST SNAPSHOT · ' \+ c\.issued_at_utc\.slice\(0, 16\)/);
assert.match(js, /compass\.compass_id !== 'CMP-20261011-7d14a9ee5914'/);
assert.match(js, /compass\.issued_at_utc !== '2026-10-11T13:15:27Z'/);
assert.match(js, /if \(dialog\.hidden\) return;/);
assert.match(js, /event\.key !== 'Tab'/);
assert.match(js, /e\.currentTarget\.setAttribute\('aria-expanded', String\(!details\.hidden\)\)/);
// Kompas vNext must keep immediate decisions above the fold while all explanatory
// source prose starts behind native, keyboard-accessible closed <details> controls.
const compassStart = html.indexOf('<section class="page" id="page-kompas"');
const compassEnd = html.indexOf('<section class="page" id="page-dokumentation"', compassStart);
assert.ok(compassStart >= 0 && compassEnd > compassStart, 'Kompas navigation must remain its own page');
const compassHtml = html.slice(compassStart, compassEnd);
assert.match(compassHtml, /id="compass-primary-action"/);
assert.match(compassHtml, /id="compass-primary-direction"/);
assert.match(compassHtml, /id="compass-risk-inline"/);
assert.match(compassHtml, /id="compass-sell-inline"/);
assert.match(compassHtml, /id="compass-distribution-inline"/);
assert.match(compassHtml, /id="compass-updated"/);
assert.match(compassHtml, /id="horizon-body"/);
assert.match(compassHtml, /id="asset-body"/);
assert.equal((compassHtml.match(/<details class="compass-disclosure">/g) || []).length, 2, 'Exactly two closed, accessible contextual disclosures');
assert.equal((compassHtml.match(/<summary>/g) || []).length, 2, 'Use native summary instead of custom JS toggle');
assert.doesNotMatch(compassHtml, /<details[^>]*open(?:\s|>)/, 'Analytical details remain folded by default');
assert.doesNotMatch(compassHtml, /compass-two-up|compass-primary-copy|interpret-more|risk-more|compass-summary.*#0b1f39/, 'No old giant interpretation and risk cards');
assert.ok(compassHtml.indexOf('id="compass-primary-action"') < compassHtml.indexOf('id="horizon-body"'), 'Action first');
assert.ok(compassHtml.indexOf('id="compass-risk-inline"') < compassHtml.indexOf('id="horizon-body"'), 'Time-critical risk visible before tables');
assert.ok(compassHtml.indexOf('id="asset-body"') < compassHtml.indexOf('<details class="compass-disclosure">'), 'Detailed analysis moved beneath both decision tables');
assert.match(js, /setText\('compass-risk-inline', riskState\)/);
assert.match(js, /setText\('compass-sell-inline', sellState\)/);
assert.match(js, /setText\('compass-distribution-inline', clean\(c\.protection_tracker\?\.distribution_risk/);
assert.match(js, /c\.sell_assessment\?\.state/);
assert.match(js, /\.compass-urgent, \.compass-table-block, \.compass-disclosure-group/);
assert.doesNotMatch(js, /\$\('interpret-more'\)|\$\('risk-more'\)/, 'Native disclosure requires no extra click handler');
assert.match(css, /#page-kompas \.compass-summary \{ display:grid/);
assert.match(css, /\.compass-disclosure\[open\] \.compass-chevron/);
assert.match(css, /\.compass-urgent \{ margin-top:/);
for (const [danish, english] of [
  ['HANDLING NU','ACTION NOW'],
  ['Tidshorisonter','Time horizons'],
  ['Aktivklasser','Asset classes'],
  ['Min fortolkning','My interpretation'],
  ['Pullback, beskyttelse & re-entry','Pullback, protection & re-entry']
]) {
  assert.ok(i18n.includes(JSON.stringify(danish) + ': ' + JSON.stringify(english)), 'DA/EN glossary missing '+danish);
}

// Bull/Bear stays a tiny source-governed evidence display, never a probability.
assert.match(js, /import \{ officialBullBear \} from '\.\/official-bullbear\.mjs'/);
assert.match(js, /officialBullBear\(c, '1_3d'\)/);
assert.match(js, /officialBullBear\(c, key\)/);
assert.match(js, /paintBullBear\(c\)/);
assert.match(js, /\.compass-weather, \.compass-urgent/);
assert.match(css, /\.compass-weather-track \{height:5px/);
assert.match(css, /\.compass-weather-track\[hidden\] \{display:none!important\}/);
assert.match(i18n, /Evidensbalance · ikke sandsynlighed eller købssignal\./);
assert.ok(compassHtml.includes('id="compass-bullbear"'), 'Compact scale must remain in Compass');
assert.ok(compassHtml.includes('id="bullbear-bull"'));
assert.ok(compassHtml.includes('id="bullbear-bear"'));
assert.ok(compassHtml.includes('id="bullbear-bias"'));
assert.ok(compassHtml.includes('id="bullbear-track"'));
assert.ok(compassHtml.indexOf('id="compass-primary-action"') < compassHtml.indexOf('id="compass-bullbear"'));
assert.ok(compassHtml.indexOf('id="compass-bullbear"') < compassHtml.indexOf('id="compass-risk-inline"'));
assert.ok(compassHtml.indexOf('id="bullbear-other-horizons"') > compassHtml.indexOf('<details class="compass-disclosure">'));
assert.equal(source.compass.bull_bear_scale.contract, 'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1');
assert.equal(source.compass.bull_bear_scale.semantics, 'EVIDENCE_BALANCE_NOT_PROBABILITY');
assert.equal(source.compass.bull_bear_scale.horizons['1_3d'].bull, 5);
assert.equal(source.compass.bull_bear_scale.horizons['1_3d'].bear, 5);

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
