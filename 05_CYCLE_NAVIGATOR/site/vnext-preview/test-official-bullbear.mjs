import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { officialBullBear } from './official-bullbear.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const seed = JSON.parse(readFileSync(resolve(root, 'seed.json'), 'utf8'));
const original = seed.compass;
const adapt = (mutate, horizon = '1_3d') => {
  const copy = structuredClone(original);
  mutate(copy);
  return officialBullBear(copy, horizon);
};
const test = (name, fn) => { fn(); console.log('PASS ' + name); };

// Authentic source evidence, not synthetic browser classification.
test('Archived Official Compass uses neutral Bull 5 Bear 5 1–3d', () => {
  assert.deepEqual(officialBullBear(original, '1_3d'), { bull: 5, bear: 5, bias: 'NEUTRAL' });
});
test('All 3 horizons read original source without inventing values', () => {
  for (const h of ['1_3d','5_7d','2_3w']) {
    assert.deepEqual(officialBullBear(original, h), {
      bull: original.bull_bear_scale.horizons[h].bull,
      bear: original.bull_bear_scale.horizons[h].bear,
      bias: original.bull_bear_scale.horizons[h].bias
    });
  }
});
test('Governed bullish and bearish categorical fixtures are passed through verbatim', () => {
  assert.deepEqual(adapt(c => Object.assign(c.bull_bear_scale.horizons['1_3d'], {
    bull: 7, bear: 3, bias: 'BULLISH'
  })), { bull: 7, bear: 3, bias: 'BULLISH' });
  assert.deepEqual(adapt(c => Object.assign(c.bull_bear_scale.horizons['1_3d'], {
    bull: 3, bear: 7, bias: 'BEARISH'
  })), { bull: 3, bear: 7, bias: 'BEARISH' });
});
test('Missing scale, owner or market contract results in no number', () => {
  for (const mutation of [
    c => { delete c.bull_bear_scale; },
    c => { c.bull_bear_scale.contract = 'WRONG'; },
    c => { c.bull_bear_scale.owner = 'CN_BROWSER'; },
    c => { c.bull_bear_scale.source_of_truth_contract = 'BROWSER_INFERRED'; },
    c => { c.bull_bear_scale.mapping_version = 'UNAPPROVED_RICH_SCALE'; },
    c => { c.bull_bear_scale.semantics = 'MARKET_PROBABILITY'; },
    c => { c.bull_bear_scale.resolution = 'DETAILED_PROBABILITY'; },
    c => { c.bull_bear_scale.authority.site_synthesis_allowed = true; },
    c => { c.bull_bear_scale.authority.new_market_classifier = true; },
    c => { c.bull_bear_scale.authority.probability_model = true; },
    c => { c.bull_bear_scale.authority.portfolio_execution = true; },
    c => { c.data_status = 'DEGRADED'; }
  ]) assert.equal(adapt(mutation), null);
});
test('Invalid or premature numeric claims are never shown', () => {
  for (const mutation of [
    c => { c.bull_bear_scale.horizons['1_3d'].status = 'UNAVAILABLE'; },
    c => { c.bull_bear_scale.horizons['1_3d'].bull = null; },
    c => { c.bull_bear_scale.horizons['1_3d'].bear = null; },
    c => { c.bull_bear_scale.horizons['1_3d'].bull = 11; },
    c => { c.bull_bear_scale.horizons['1_3d'].bull = 4.5; },
    c => { c.bull_bear_scale.horizons['1_3d'].bear = NaN; },
    c => { c.bull_bear_scale.horizons['1_3d'].bear = 4; },
    c => { c.bull_bear_scale.horizons['1_3d'].bias = 'BULLISH'; },
    c => { c.bull_bear_scale.horizons['1_3d'].bias = 'SELL_NOW'; }
  ]) assert.equal(adapt(mutation), null);
});
test('Unknown horizon and ungoverned 4–8w never generated', () => {
  assert.equal(officialBullBear(original, '4_8w'), null);
  assert.equal(officialBullBear(original, 'NEXT_12H'), null);
  assert.equal(officialBullBear(original, 'unknown'), null);
  assert.equal(officialBullBear(null, '1_3d'), null);
});
test('Bull/Bear input is not mutated', () => {
  const before = JSON.stringify(original);
  officialBullBear(original, '1_3d');
  assert.equal(JSON.stringify(original), before);
});
console.log('SUCCESS: official source-led Bull/Bear display contract; no independent probability or trade signal');
