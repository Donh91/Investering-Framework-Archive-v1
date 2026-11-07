import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { buildFixture } from './fixture.mjs';
import {
  readOfficialGraphB,
  replayObservedUntil,
} from '../../premium-v2/graph-b/official-source-adapter.mjs';

const qa = asset => 'W46_GITHUB_ONLY_QA_' + asset;
const adapt = (fixture, asset) => readOfficialGraphB(
  fixture.snapshot, asset,
  { now_utc: fixture.nowUtc, publication_lineage: fixture.lineage }
);
const at = new URL('./index.html', import.meta.url);
const html = readFileSync(fileURLToPath(at), 'utf8');

test('Monday GitHub-native Graph B accepts exactly seven original fixture closes and daily ranges', () => {
  const monday = buildFixture('mandag');
  for (const asset of ['BTC', 'ETH']) {
    const m = adapt(monday, asset);
    assert.equal(m.source_status, 'SOURCE_BOUNDED', qa(asset));
    assert.equal(m.forecast_status, 'SOURCE_ISSUED', qa(asset));
    assert.equal(m.forecast.length, 7);
    assert.equal(m.daily_range_status, 'SOURCE_ISSUED');
    assert.equal(m.daily_ranges.length, 7);
    assert.equal(m.actual_quote_unit, 'USDT');
    assert.equal(m.forecast_declared_quote_unit, 'USDT');
    for (let i = 0; i < 7; i += 1) {
      assert.equal(m.forecast[i].day, i + 1);
      assert.equal(m.daily_ranges[i].day, i + 1);
      assert.equal(m.forecast[i].low, m.daily_ranges[i].low);
      assert.equal(m.forecast[i].high, m.daily_ranges[i].high);
    }
    assert.equal(m.hourly_observations.length, 12);
    assert.ok(m.forecast.every(p => p.expected_close > 0));
  }
});

test('Wednesday preserves exact frozen points, source identity and range descriptions, extends only actual', () => {
  const mon = buildFixture('mandag');
  const wed = buildFixture('onsdag');
  assert.deepEqual(mon.frozenForecast, wed.frozenForecast);
  assert.deepEqual(mon.frozenRanges, wed.frozenRanges);
  assert.equal(mon.issuedAt, wed.issuedAt);
  for (const asset of ['BTC', 'ETH']) {
    const m = adapt(mon, asset);
    const w = adapt(wed, asset);
    assert.equal(w.forecast_status, 'SOURCE_ISSUED');
    assert.deepEqual(m.forecast, w.forecast);
    assert.deepEqual(m.daily_ranges, w.daily_ranges);
    assert.equal(w.hourly_observations.length, 60);
    assert.equal(w.live_freshness, 'STALE');
    assert.equal(w.is_current_quote, false);
    assert.equal(replayObservedUntil(w, '2026-11-10T00:00:00Z').flat().length, 24);
    assert.ok(w.hourly_observations.every(row => row.observed_at_utc <= wed.observedThroughUtc));
  }
});

test('negative test: 0/7 original abstention does not show a blue daily closing-price path', () => {
  const f = buildFixture('afstaar');
  for (const asset of ['BTC', 'ETH']) {
    const m = adapt(f, asset);
    assert.equal(m.source_status, 'SOURCE_BOUNDED');
    assert.equal(m.forecast_status, 'UNAVAILABLE');
    assert.deepEqual(m.forecast, []);
    assert.equal(m.bands.length, 3); // Original ranges remain independent, not a fabricated 7-point curve.
  }
});

test('negative test: model USD versus actual USDT hides incomparable blue forecast', () => {
  const f = buildFixture('valutafejl');
  for (const asset of ['BTC', 'ETH']) {
    const m = adapt(f, asset);
    assert.equal(m.source_status, 'SOURCE_BOUNDED');
    assert.equal(m.forecast_comparison_quote_status, 'UNVERIFIED_OR_DIFFERENT_UNIT');
    assert.equal(m.forecast_status, 'SOURCE_ISSUED_QUOTE_INCOMPARABLE');
    assert.deepEqual(m.forecast, []);
  }
});

test('QA route fetches exact GitHub Pages HTML and never overwrites live data', () => {
  assert.match(html, /noindex,nofollow/);
  assert.match(html, /index\.html'/);
  assert.match(html, /graph-history\/index\.html/);
  assert.match(html, /function scriptFor\(fixture, history\)/);
  assert.match(html, /window\.fetch = async/);
  assert.match(html, /GITHUB_SITE_EXPECTED_COMPONENT_MISSING/);
  assert.match(html, /\/data\/latest\.json/);
  assert.doesNotMatch(html, /writeFile|localStorage|src=["']https:\/\/.*appdeploy/);
});
