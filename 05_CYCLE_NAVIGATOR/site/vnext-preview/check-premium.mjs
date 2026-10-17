// Strict, package-free source integrity check for the premium CN vNext prototype.
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Script } from 'node:vm';
import assert from 'node:assert/strict';
import { summarizeCurrentPublic, loadCanonicalPublicFeeds, CANONICAL_PUBLIC_DATA_ROOT } from './current-public-panel.mjs';
const dir = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(dir, 'premium-index.html'), 'utf8');
const css = readFileSync(resolve(dir, 'premium.css'), 'utf8');
const js = readFileSync(resolve(dir, 'premium.js'), 'utf8');
const i18n = readFileSync(resolve(dir, 'premium-i18n.js'), 'utf8');
const source = JSON.parse(readFileSync(resolve(dir, 'seed.json'), 'utf8'));
const motionLibrary = readFileSync(resolve(dir, 'MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md'), 'utf8');
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
const unique = new Set(ids);
// The path replay SVG is created after source validation; its clip rectangle
// must be declared in chartElement, never assumed to exist in static HTML.
const dynamicSvgId = 'cn-path-actual-clip-rect';
assert.match(js, /id:'cn-path-actual-clip-rect'/);
assert.equal(ids.length, unique.size, 'Duplicate HTML ids');
for (const expected of ['page-overblik', 'page-kompas', 'page-dokumentation', 'horizon-body', 'asset-body', 'range-visualization', 'history-full', 'source-dialog']) {
  assert.ok(unique.has(expected), 'Missing required UI section: ' + expected);
}
for (const match of [...js.matchAll(/\$\('([^']+)'\)/g), ...js.matchAll(/setText\('([^']+)'/g)]) {
  assert.ok(unique.has(match[1]) || match[1] === dynamicSvgId,
    'JavaScript targets nonexistent HTML or declared dynamic SVG ID: ' + match[1]);
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
assert.match(js, /import \{ initializeLanguage, translateInterface, selectLanguage, currentLanguage \} from '\.\/premium-i18n\.js'/);
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

// PATH v3 is structural context, never a time forecast or new action engine.
assert.match(html, /<section class="section-block section-path" aria-labelledby="path-main-title">/);
assert.match(html, /id="path-current"/);
assert.match(html, /id="path-next"/);
assert.match(html, /id="path-next-gate"/);
assert.match(html, /id="path-eta"/);
assert.match(html, /id="path-rotation-rail"/);
assert.match(html, /id="path-alt-status"/);
assert.match(html, /id="path-all-phases"/);
assert.match(html, /<details class="path-disclosure" id="cycle-details">/);
assert.doesNotMatch(html, /<details class="path-disclosure"[^>]*open(?:\\s|>)/);
assert.doesNotMatch(html, /id="expand-cycle"/);
assert.match(js, /import \{ officialPathView \} from '\.\/official-path\.mjs'/);
assert.match(js, /function paintPath\(d, lang = 'da'\)/);
assert.match(js, /officialPathView\(d, \{ lang, mode:'archived' \}\)/);
assert.match(js, /paintPath\(data, currentLanguage\(\)\)/);
assert.match(js, /paintPath\(data, button\.dataset\.lang\)/);
assert.doesNotMatch(js, /\$\('expand-cycle'\)/);
assert.match(css, /PATH vNext: source-bound phase route/);
assert.match(css, /\.path-rotation-rail\{display:grid/);
assert.match(i18n, /"Hvor er vi": "Where are we"/);
assert.match(i18n, /"Hele markedsrejsen": "The full market cycle"/);
assert.doesNotMatch(html, /<h3>BTC leder\./);
assert.doesNotMatch(html, /Observeret W40/);

assert.match(html, /<article class="hero-main" aria-labelledby="overview-title">/);
assert.match(html, /id="hero-action-summary"/);
assert.match(html, /id="hero-now"/);
assert.match(html, /id="overview-risk"/);
assert.match(html, /id="overview-risk-window"/);
assert.match(html, /id="overview-risk-stage"/);
assert.match(html, /id="compass-risk-stage"/);
assert.match(html, /id="pullback-stage-ruler"/);
assert.match(html, /id="pullback-investor-facts"/);
assert.equal((html.match(/data-risk-stage="(?:NORMAL|BUILDING|ELEVATED|HIGH|CONFIRMED)"/g)||[]).length,5,'Show all 5 owner risk classes exactly once');
assert.equal((html.match(/<details class="compass-disclosure">/g)||[]).length,2,'Do not add extra expanded cards');
assert.match(js, /import \{ officialPullbackInvestorView \} from '\.\/official-pullback-investor-view\.mjs'/);
assert.match(js, /const facts = officialPullbackInvestorView\(d\.compass, d\.weekly, language\)/);
assert.match(js, /function paintPullbackEscalator\(/);
assert.match(js, /function paintPullbackInvestorFacts\(/);
assert.match(js, /segment\.classList\.toggle\('is-current'/);
assert.match(js, /paintPullbackEscalator\(stage, lang\)/);
assert.match(js, /paintPullbackInvestorFacts\(d, lang\)/);
assert.match(css, /Five discrete OFFICIAL risk classes, NOT time\/probability/);
assert.match(css, /\.pullback-facts-grid \{display:grid/);
assert.match(i18n, /"Risikoklasse · ikke en 1–10 sandsynlighed": "Risk category · not a 1–10 likelihood"/);

assert.match(js, /import \{ officialPullbackStage \} from '\.\/official-pullback-stage\.mjs'/);
assert.match(js, /const stage = officialPullbackStage\(d\.compass, d\.weekly, lang\);/);
assert.match(js, /setText\('overview-risk-stage', stage\.stageLabel\)/);
assert.match(js, /setText\('compass-risk-stage', stage\.stageLabel\)/);
assert.match(js, /stage\.proximityLabel/);
assert.match(js, /stage\.qualityLabel/);
assert.match(js, /id = 'risk-evidence-quality'/);
assert.match(css, /Progressive risk is one factual line, NOT a progress bar or probability/);

assert.match(html, /id="compass-risk-window"/);
assert.match(html, /PULLBACK · TID/);
assert.match(js, /import \{ officialPullbackDisplay \} from '\.\/official-pullback-eta\.mjs'/);
assert.match(js, /paintPullback\(d, currentLanguage\(\)\)/);
assert.match(js, /setText\('overview-risk-window', p\.headline\)/);
assert.match(js, /setText\('compass-risk-window', p\.headline\)/);
assert.match(js, /selectLanguage\(button\.dataset\.lang\);/);
assert.match(js, /paintPullback\(data, button\.dataset\.lang\);/);
assert.match(js, /selectLanguage\(button\.dataset\.lang\);[\s\S]{0,180}paintPullback\(data, button\.dataset\.lang\);/, 'Dynamic ETA render must happen after general translation and before PATH repaint');
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


const readback = source.completed_score.daily_observations_w40;
assert.equal(readback.contract, 'CN_W40_OBSERVED_DAILY_OHLC_READBACK_v1');
assert.equal(readback.basis, 'UTC_ISO_WEEK');
assert.equal(readback.observed_hours, 168);
const frozen = source.completed_score.frozen_weekly_expectation_w40;
assert.equal(frozen.contract,'CN_W40_ORIGINAL_FROZEN_INTRADAY_PATH_CONTEXT_v1');
assert.equal(frozen.source_git_blob_sha,'4f867d594c355c31ede8a3718638c6e72249a5a8');
assert.equal(frozen.original_forecast_freeze_sha256,'e64e4c52af960220f03fa69a86cbd9853888d085c99d5b2c7ff061aa3aa8471f');
assert.equal(frozen.frozen_at_utc,'2026-09-28T05:53:37Z');
assert.ok(Date.parse(frozen.frozen_at_utc)>Date.parse('2026-09-28T00:00:00Z'),
  'Must disclose Monday pre-freeze observations when showing daily actual low/high');
for (const window of ['day_1_2','day_3_4','day_5_7']) {
  assert.ok(typeof frozen.intraday_map[window] === 'string' &&
    frozen.intraday_map[window].includes('BTC') &&
    frozen.intraday_map[window].includes('ETH'),
    'All original source windows must be recorded, not fabricated');
}
assert.equal(readback.days.length, 7);
assert.equal(readback.source_git_blob_sha, '33e0d1366c8de7e69ea1bd9655a96764aeabc70f');
for (const asset of ['BTC','ETH']) {
  const dayRows = readback.days;
  assert.ok(dayRows.every((d) => d.observed_hours === 24 && Number.isFinite(d[asset].close) &&
    d[asset].low <= d[asset].close && d[asset].close <= d[asset].high));
  const sourceRows = source.completed_score.price_range_precision.rows.filter((r) => r.asset === asset);
  for (let i=0; i<3; i++) {
    const [start,end] = [[0,2],[2,4],[4,7]][i];
    assert.ok(Math.abs(sourceRows[i].actual_low-Math.min(...dayRows.slice(start,end).map((d) => d[asset].low))) < .011);
    assert.ok(Math.abs(sourceRows[i].actual_high-Math.max(...dayRows.slice(start,end).map((d) => d[asset].high))) < .011);
  }
}
assert.match(js, /function completeDailyHistory\(score, asset\)/);
assert.ok(js.includes('function monotoneClosePath(points) {'), 'Expected SVG spline helper');
// Regression: reverse-x range boundary must not disappear silently.
const splineStart = js.indexOf('function monotoneClosePath(points) {');
const splineEnd = js.indexOf('\nfunction renderRangeChart()', splineStart);
assert.ok(splineStart >= 0 && splineEnd > splineStart, 'Spline and chart functions found');
const splineSource = js.slice(splineStart,splineEnd);
assert.ok(splineSource, 'Readable pure SVG interpolation helper');
const spline = new Function(splineSource + '; return monotoneClosePath;')();
const asc = [{x:0,y:5},{x:10,y:8},{x:20,y:6},{x:40,y:9}];
const desc = [...asc].reverse();
for (const [name,pts] of [['forward',asc],['reverse',desc]]) {
  const d=spline(pts);
  assert.ok(d.startsWith('M ') && (d.match(/ C /g)||[]).length===pts.length-1,
    name + ' spline must preserve all windows and be visibly complete');
  assert.ok(!d.includes('NaN') && !d.includes('Infinity'),name+' spline remains finite');
}
assert.equal(spline([{x:0,y:1},{x:0,y:2}]),'', 'Duplicate x is invalid');
assert.equal(spline([{x:0,y:1},{x:3,y:2},{x:2,y:3}]),'',
  'Nonmonotone x cannot form an unambiguous smooth SVG boundary');
// The pure spline supports both directions, but the production chart now
// intentionally shows just two comparable price paths; full forecast bands
// are in the explicit source-backed range table.
assert.ok(!js.includes('const ribbon=upperPath'), 'No resurrected heavy forecast band');

// The Quiet Precision design specification explicitly rejects a duplicate
// ornamental gauge. Only Official Compass owns action; the UI merely renders
// separate source-owned direction and official action, once each.
assert.ok(!html.includes('id="cn-instrument-svg"')&&!html.includes('cn-gauge-needle'),
  'No decorative gauge or invented needle in decision-first editorial preview');
assert.ok(!js.includes('paintSourceInstrument')&&!js.includes('const degrees = { WAIT:'),
  'No obsolete client-side market/action position inference');
assert.ok(!css.includes('.cn-gauge-')&&!css.includes('.cn-instrument'),
  'No dead gauge selectors in CSS bundle');
assert.match(html, /id="hero-now"/);
assert.match(html, /id="hero-action-summary"/);
const heroStart=html.indexOf('class="hero-key-metrics cn-overview-posture"');
const horizonStart=html.indexOf('class="cn-overview-decision"');
assert.ok(heroStart>0&&horizonStart>heroStart&&
  html.indexOf('id="hero-now"',heroStart)<horizonStart&&
  html.indexOf('id="hero-action-summary"',heroStart)<horizonStart,
  'Direction and Official Compass action precede all horizon/phase/pullback exposition');
assert.match(css, /\.cn-chart-table/);


// Approved visual-reference hierarchy and source-only action safety.
const sourceChartStart=html.indexOf('id="cn-path-week"');
const sourceChartMarkup=html.indexOf('id="range-visualization"');
const legacyFoldStart=html.indexOf('class="edge-legacy-fold"');
const prospectiveStart=html.indexOf('class="edge-era"');
const summaryStart=html.indexOf('class="cn-results-evidence"');
assert.ok(sourceChartStart > 0 && sourceChartMarkup > sourceChartStart &&
  sourceChartMarkup < prospectiveStart && prospectiveStart < summaryStart && summaryStart < legacyFoldStart,
  'One weekly price journey belongs to PATH; Results contains score receipts only');
assert.equal((html.match(/id="cn-source-chart"/g)||[]).length,1);
assert.equal((html.match(/id="cn-path-window-table"/g)||[]).length,1);
assert.equal((html.match(/id="cn-path-daily-table"/g)||[]).length,1);
assert.equal((html.match(/id="cn-path-week-open"/g)||[]).length,1);
// Desktop/phone coordinate spaces must remain readable and replay must
// share exact axes with the SVG rather than hard-coded stale desktop pixels.
const geometryStart=js.indexOf('function rangeChartGeometry() {');
const geometryEnd=js.indexOf('\nfunction renderRangeChart()',geometryStart);
assert.ok(geometryStart>=0 && geometryEnd>geometryStart, 'Mobile source geometry exists');
const geometryFnSource=js.slice(geometryStart,geometryEnd);
const getGeometry=new Function('window', geometryFnSource+'; return rangeChartGeometry();');
const phone=getGeometry({matchMedia:()=>({matches:true})});
const desktop=getGeometry({matchMedia:()=>({matches:false})});
assert.equal(phone.width,480); assert.equal(phone.height,380);
assert.equal(desktop.width,820);assert.equal(desktop.height,396);
for (const size of [phone,desktop]) {
  assert.ok(size.left>55 && size.right<size.weekX && size.weekX<size.width,
    'Y labels, seven observed points and week label fit inside responsive SVG');
  assert.ok(size.top>0 && size.bottom<size.height-30, 'Price path and weekday labels fit');
  assert.equal((size.right-size.left)/6>25,true, 'Seven observed days are distinguishable');
}
assert.match(js,/const \{left,right\}=rangeChartGeometry\(\)/);
assert.match(js,/window\.matchMedia\('\(max-width: 580px\)'\)\.addEventListener/);
assert.match(css,/\.cn-history-chart\{aspect-ratio:480\/380/);

assert.match(js,/function revealActualThrough\(dayIndex\)/);
assert.match(js,/cn-path-actual-clip-rect/);
assert.match(js,/const forecastCenters=\[\.5,2\.5,5\]/);
assert.match(js,/const midpointGuide=guide\('midpoint'\)/);
assert.match(js,/cn-chart-forecast-midpoint/);
assert.ok(!js.includes("svg.append(chartElement('path',{d:monotoneClosePath(highGuide),class:'cn-chart-boundary'}))"),
  'Do not show heavy forecast boundary strokes on the main chart');
assert.equal((html.match(/class="cn-legend-line cn-legend-line-forecast"/g)||[]).length,1);
assert.equal((html.match(/class="cn-legend-line cn-legend-line-observed"/g)||[]).length,1);
assert.ok(html.includes('FORECAST <small>(afledt)</small>'), 'Derived forecast distinction required');
assert.ok(html.indexOf('id="range-visualization"') < html.indexOf('id="range-replay"'),
  'Users should see the actual 2-line price chart before playback controls');
assert.match(js,/cn-chart-forecast-midpoint/);
assert.ok(!js.includes("class:'cn-chart-forecast-ribbon'"),
  'The wide three-window range is a separate exact-value disclosure, not a visually dominant/ambiguous price band');
assert.match(js,/windows\.map\(r => \(r\.forecast_low\+r\.forecast_high\)\/2\)/);
for(const asset of ['BTC','ETH']) {
  const windows=source.completed_score.price_range_precision.rows.filter(x=>x.asset===asset);
  const days=source.completed_score.daily_observations_w40.days;
  const step=asset==='BTC'?1000:100;
  const values=[...windows.map(w=>(w.forecast_low+w.forecast_high)/2),
    ...days.flatMap(d=>[d[asset].low,d[asset].high])];
  const lo=Math.floor(Math.min(...values)/step)*step-step;
  const hi=Math.ceil(Math.max(...values)/step)*step+step;
  assert.ok(hi>lo && values.every(x=>x>=lo && x<=hi),
    asset+' observed daily extrema and forecast midpoint must all be fully in viewport');
  assert.ok(hi-lo < (asset==='BTC'?12000:700),
    asset+' must not let wide forecast uncertainty flatten the comparable observed path');
}
assert.equal((html.match(/id="range-visualization"/g)||[]).length,1);
assert.equal((html.match(/data-overview-horizon="/g)||[]).length,5);
assert.equal((html.match(/id="cn-overview-market-body"/g)||[]).length,1);
assert.ok(html.includes('id="cn-range-official-scorecards"'));
assert.match(js,/function paintOverviewSnapshot\(c\)/);
assert.match(js,/const label = \(\{ NEXT_12H:/);
assert.match(js,/function completeDailyHistory\(score, asset\)/);
assert.ok(!html.includes('Updated just now'), 'Archive preview must never claim freshly updated LIVE status');

// User-discoverable PATH navigation and real deep-link regression.
assert.equal((html.match(/data-open-path/g)||[]).length,3,
  'Desktop PATH button, iPhone dock PATH button and immediate Overview CTA required');
assert.match(js, /function openPathGraph\(\{ updateHash = true \} = \{\}\)/);
assert.match(js, /route === 'cn-path-week'/);
assert.match(js, /initial === 'cn-path-week'/);
assert.match(js, /location\.hash === '#cn-path-week'/);
assert.match(js, /target\.scrollIntoView\(\{ behavior:'instant', block:'start' \}\)/);
assert.match(css, /\.mobile-dock \.dock-link\{width:25%;/);
assert.match(html, /class="cn-path-jump-banner"/);


// Two-line visual hierarchy must be immediate: switching assets cannot
// automatically start a replay that hides ACTUAL behind a frozen phase.
const assetHandlerStart=js.indexOf("document.querySelectorAll('[data-asset]').forEach");
const explicitReplayButton=js.indexOf("  $('range-replay')?.addEventListener('click', playRangeComparison)",assetHandlerStart);
assert.ok(assetHandlerStart>=0&&explicitReplayButton>assetHandlerStart);
const assetHandler=js.slice(assetHandlerStart,explicitReplayButton);
assert.ok(!assetHandler.includes('playRangeComparison()'), 'BTC/ETH switch cannot autoplay or hide ACTUAL');
assert.match(assetHandler,/cancelRangeReveal\(\)/);
assert.match(assetHandler,/renderRangeChart\(\)/);
assert.match(assetHandler,/setRangeRevealPhase\('score'\)/);

// Replay must finish after day seven in both DA and EN without referring
// to a block-scoped renderRangeChart variable. Exercise the real function.
const replayStart=js.indexOf('function playRangeComparison() {');
const replayEnd=js.indexOf('\nconst overviewHorizonKeys',replayStart);
assert.ok(replayStart>0 && replayEnd>replayStart,'Extract replay logic');
const replaySource=js.slice(replayStart,replayEnd);
const replayEvents=[],replayHandles=[],replayCallbacks=[];
let replayLanguage='da';
const runReplay=new Function(
  'completeDailyHistory','data','selectedAsset','cancelRangeReveal',
  '$','window','setRangeRevealPhase','revealActualThrough',
  'rangeRevealTimers','setTimeout','setText','currentLanguage',
  replaySource+'; return playRangeComparison;'
)(
  ()=>({days:Array(7)}),{completed_score:{}},'BTC',()=>{},
  ()=>({disabled:false}),{matchMedia:()=>({matches:false})},
  phase=>replayEvents.push('phase:'+phase),day=>replayEvents.push('day:'+day),
  replayHandles,
  (callback)=>{replayCallbacks.push(callback);return replayCallbacks.length;},
  (id,value)=>replayEvents.push(id+':'+value),()=>replayLanguage
);
for(const lang of ['da','en']){
  replayLanguage=lang;replayHandles.length=0;replayCallbacks.length=0;replayEvents.length=0;
  runReplay();
  assert.equal(replayHandles.length,8,'Seven daily replay handles plus completion handle');
  assert.equal(replayCallbacks.length,8,'Seven callbacks plus final completion callback');
  for(const timer of [...replayCallbacks]) timer();
  assert.equal(replayEvents.filter(x=>x.startsWith('day:')).length,9,
    'Initial frozen state, seven dated actual frames, and final readback');
  assert.ok(replayEvents.includes('day:6'),'Sunday must be revealed');
  assert.ok(replayEvents.some(x=>x.includes(lang==='da'?'Faktisk uge':'Observed week')),
    'Replay completion translated safely for '+lang);
}

// P0: the first-viewport CURRENT panel must never be populated from the old
// W40/W41 preview archive. These are typed public-build fixtures, not markets.
for (const id of ['cn-current-public-panel','cn-current-status','cn-current-action',
 'cn-current-direction','cn-current-risk','cn-current-phase','cn-current-gate',
 'cn-current-provenance','cn-current-delivery']) {
  assert.ok(ids.includes(id), 'Missing first viewport public source readback: '+id);
}
assert.match(html, /HISTORISK DESIGNARKIV · CN #28 \/ W41/);
assert.match(js, /import \{ initializeCurrentPublicPanel, paintCurrentPublicPanel \} from '\.\/current-public-panel\.mjs'/);
assert.match(js, /void initializeCurrentPublicPanel\(currentLanguage\(\)\)/);
assert.match(js, /paintCurrentPublicPanel\(button\.dataset\.lang\)/);
assert.equal(CANONICAL_PUBLIC_DATA_ROOT,'https://donh91.github.io/Investering-Framework-Archive-v1/data/');
const fixtureNow='2026-10-17T12:00:00Z';
const publicLatest={
 schema:'CN_PUBLIC_SNAPSHOT_V2', generated_at:'2026-10-17T11:55:00Z',
 pointer:{iso_year:2026,iso_week:42,issue_number:30,status:'DEGRADED'},
 package:{issue_number:30,status:'DEGRADED',forecast_freeze:{}},
 public_series:{contract:'CN_PUBLIC_SERIES_INDEX_v1',
   current_public_projection:{public_issue_number:29,forecast_week:'2026-W42'}}
};
const publicCompass={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
 compass_id:'CMP-TEST-17OCT',issued_at_utc:'2026-10-17T11:50:00Z',
 weekly_context:{status:'ALIGNED',forecast_week:'2026-W42',public_issue_number:29},
 full_stack:{official_freshness:{
   contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
   status:'VERIFIED_OWNER_POLICY',source_asof_utc:'2026-10-17T11:30:00Z',
   valid_until_utc:'2026-10-17T13:00:00Z',
   semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA'}},
 action_now:'HOLD_WAIT',horizons:{NEXT_12H:{expected_direction:'UP'}}
};
const summarize=(l=publicLatest,c=publicCompass,nowUtc=fixtureNow)=>
 summarizeCurrentPublic(l,c,{nowUtc});
const accepted=summarize();
assert.equal(accepted.status,'CURRENT_VERIFIED');
assert.equal(accepted.action,'HOLD_WAIT');
assert.equal(accepted.direction,'UP');
assert.equal(accepted.forecast_week,'2026-W42');
assert.equal(accepted.issue,29);
assert.equal(accepted.phase,'UNKNOWN','No inferred live PATH checkpoint');
const cloned=(lMutate,cMutate)=>{const l=structuredClone(publicLatest);
 const c=structuredClone(publicCompass);lMutate?.(l);cMutate?.(c);return summarize(l,c);};
for(const out of [
 cloned(null,c=>{c.weekly_context.forecast_week='2026-W41';}),
 cloned(null,c=>{c.full_stack.official_freshness.valid_until_utc='2026-10-17T11:59:00Z';}),
 cloned(null,c=>{c.full_stack.official_freshness=null;}),
 cloned(l=>{l.generated_at='2026-10-15T11:55:00Z';}),
 cloned(null,c=>{c.horizons.NEXT_12H.expected_direction='UP';c.action_now='SELL';}),
 cloned(l=>{l.public_series.current_public_projection.forecast_week='2026-W41';}),
 summarize(publicLatest,publicCompass,'2026-10-18T12:00:00Z')
]) {
 assert.equal(out.status,'UNAVAILABLE','Invalid public owner source cannot be marked current');
 assert.equal(out.action,'UNAVAILABLE','No unverified action');
 assert.equal(out.direction,'UNKNOWN','No leaked historical/expired 12h direction');
 assert.equal(out.risk,'UNKNOWN','No leaked risk from expired source');
 assert.equal(out.gate,'UNKNOWN','No invented next gate');
}
const observedUrls=[];
const joined=await loadCanonicalPublicFeeds(async(url,options)=>{
 observedUrls.push(url);
 assert.equal(options.cache,'no-store');
 assert.equal(options.redirect,'error');
 return {ok:true,url,json:async()=>url.endsWith('/latest.json')?publicLatest:publicCompass};
});
assert.deepEqual(observedUrls,[CANONICAL_PUBLIC_DATA_ROOT+'latest.json',
 CANONICAL_PUBLIC_DATA_ROOT+'compass.json']);
assert.equal(joined.compass,publicCompass);
await assert.rejects(()=>loadCanonicalPublicFeeds(async(url)=>({
 ok:true,url:'https://untrusted.example/data/latest.json',json:async()=>publicLatest
})),/CANONICAL_PUBLIC_FEED_UNAVAILABLE/);
console.log('PASS: canonical public first viewport, W42 joined source, expiry and missing-source fail-closed controls');

console.log('PASS: premium CN source lineage, fail-closed fixtures, bilingual copy, score semantics, modal keyboard and JavaScript syntax');
console.log('Reminder: this is static smoke/contract QA. It does not certify iPhone visual quality or ex-ante cryptographic score proof.');
