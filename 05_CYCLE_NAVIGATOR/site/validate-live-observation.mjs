import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, '../..');
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));
const numeric = (value) => value != null && value !== '' && Number.isFinite(Number(value));
const close = (a, b, eps = 0.11) => Math.abs(Number(a) - Number(b)) <= eps;

function isoWeekStartUtc(year, week) {
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const offset = (jan4.getUTCDay() + 6) % 7;
  return Date.UTC(year, 0, 4 - offset + (week - 1) * 7, 0, 0, 0, 0);
}

function expectedAverage(rows) {
  const values = rows.map((row) => row?.score).filter(numeric).map(Number);
  return values.length ? Number((values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)) : null;
}

function assert(condition, code) {
  if (!condition) throw new Error(code);
}

const pointer = await readJson(resolve(repoRoot, '05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json'));
const weekDir = String(pointer.week_dir || '');
assert(weekDir.startsWith('05_CYCLE_NAVIGATOR/weekly/') && !weekDir.includes('..'), 'invalid_week_dir');
const root = resolve(repoRoot, weekDir);
const publicFreeze = await readJson(resolve(root, 'CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
const scorecard = await readJson(resolve(root, 'CYCLE_NAVIGATOR_SCORECARD.json'));
const snapshot = await readJson(resolve(siteDir, 'dist/data/latest.json'));
const live = snapshot.live_observation || {};
const tests = Array.isArray(live.tests) ? live.tests : [];
const structuralCalls = Array.isArray(publicFreeze.structural_calls) ? publicFreeze.structural_calls : [];

assert(live.contract === 'CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v2', 'live_contract_mismatch');
assert(live.authority === 'NON_AUTHORITATIVE_OBSERVATION_ONLY', 'live_authority_leak');
assert(live.official_weekly_scores_mutable === false, 'official_score_mutability_leak');
assert(live.forecast_mutable === false, 'forecast_mutability_leak');
assert(Number(live.issue_number) === Number(pointer.issue_number), 'live_issue_mismatch');
assert(Number(live.frozen_claim_count) === structuralCalls.length, 'frozen_structural_count_mismatch');
assert(tests.length === structuralCalls.length, 'live_test_count_mismatch');

const allowed = new Map([['ON_TRACK', 100], ['MIXED', 50], ['OFF_TRACK', 0], ['OPEN', null]]);
tests.forEach((test, index) => {
  assert(test.source_parameter_id === `structural_call_${index + 1}`, `test_id_mismatch_${index + 1}`);
  assert(test.forecast === structuralCalls[index], `frozen_forecast_rewrite_${index + 1}`);
  assert(allowed.has(test.status), `invalid_live_status_${index + 1}`);
  const expected = allowed.get(test.status);
  if (expected == null) assert(test.score == null, `open_test_must_be_null_${index + 1}`);
  else assert(Number(test.score) === expected, `live_status_score_mismatch_${index + 1}`);
});

const expectedLive = expectedAverage(tests);
if (expectedLive == null) assert(live.provisional_score == null, 'live_score_without_evaluable_calls');
else assert(numeric(live.provisional_score) && close(live.provisional_score, expectedLive), 'live_score_average_mismatch');
assert(Number(live.evaluable_count || 0) === tests.filter((row) => numeric(row.score)).length, 'live_evaluable_count_mismatch');

const ranges = Array.isArray(live.frozen_numeric_ranges) ? live.frozen_numeric_ranges : [];
const frozenRangeCount = [
  [publicFreeze.btc_range_low, publicFreeze.btc_range_high],
  [publicFreeze.eth_range_low, publicFreeze.eth_range_high]
].filter(([low, high]) => numeric(low) && numeric(high)).length;
assert(ranges.length === frozenRangeCount, 'frozen_range_count_mismatch');
assert(Boolean(live.live_price_scoring_allowed) === (frozenRangeCount > 0), 'price_tracking_gate_mismatch');
const expectedPrice = expectedAverage(ranges);
if (!frozenRangeCount || expectedPrice == null) assert(live.price_tracking_score == null, 'price_score_without_frozen_observation');
else assert(numeric(live.price_tracking_score) && close(live.price_tracking_score, expectedPrice), 'price_tracking_score_mismatch');

const current = snapshot?.calibration?.current || {};
assert(Number(current.issue_number) === Number(pointer.issue_number), 'calibration_current_issue_mismatch');
assert(Number(current.evaluable_count || 0) === Number(live.evaluable_count || 0), 'calibration_current_coverage_mismatch');
if (live.provisional_score == null) assert(current.provisional_score == null, 'calibration_current_score_leak');
else assert(close(current.provisional_score, live.provisional_score), 'calibration_current_score_mismatch');

const bundle = snapshot.weekly_score_bundle || {};
assert(Number(bundle.issue_scored || 0) === Number(scorecard.issue_scored || 0), 'official_weekly_issue_changed');
if (scorecard.structural_score == null) assert(bundle.structural_score == null, 'official_weekly_score_changed');
else assert(close(bundle.structural_score, scorecard.structural_score, 0.001), 'official_weekly_score_changed');

const weekEnd = isoWeekStartUtc(Number(pointer.iso_year), Number(pointer.iso_week)) + 7 * 86400000;
if (Date.now() >= weekEnd) assert(live.maturity_state === 'HELD', 'mature_week_must_hold');
assert(['LIVE', 'HELD'].includes(live.maturity_state), 'invalid_maturity_state');

const index = await readFile(resolve(siteDir, 'dist/index.html'), 'utf8');
for (const script of ['./weekly-score.js', './live-observation.js', './public-copy.js']) {
  assert(index.includes(script), `public_widget_not_injected:${script}`);
}

console.log(JSON.stringify({
  status: 'PASS',
  issue_number: live.issue_number,
  live_score: live.provisional_score,
  evaluable: `${live.evaluable_count}/${live.frozen_claim_count}`,
  price_tracking_score: live.price_tracking_score,
  maturity_state: live.maturity_state,
  official_score_preserved: bundle.structural_score
}));
