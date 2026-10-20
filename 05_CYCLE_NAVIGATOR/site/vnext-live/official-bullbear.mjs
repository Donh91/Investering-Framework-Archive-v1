/**
 * Read-only Official Compass Bull/Bear evidence display adapter.
 * Based on MARKET_WEATHER_SOURCE_OF_TRUTH_v1 and the existing CN production
 * site/market-compass-premium.js contract. This DOES NOT infer directions,
 * probabilities, market probabilities, sell permission or forecasting edge.
 */
export function officialBullBear(c, horizon) {
  if (c?.data_status !== 'OK') return null;
  const scale = c?.bull_bear_scale;
  if (scale?.contract !== 'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1' ||
      scale.semantics !== 'EVIDENCE_BALANCE_NOT_PROBABILITY' ||
      scale.resolution !== 'COARSE_CATEGORICAL_DIRECTION' ||
      scale.mapping_version !== 'DIRECTION_ONLY_COARSE_v1' ||
      scale.owner !== 'OFFICIAL_COMPASS' ||
      scale.source_of_truth_contract !== 'MARKET_WEATHER_SOURCE_OF_TRUTH_v1' ||
      scale.authority?.site_synthesis_allowed !== false ||
      scale.authority?.new_market_classifier !== false ||
      scale.authority?.probability_model !== false ||
      scale.authority?.portfolio_execution !== false) return null;
  if (!['1_3d', '5_7d', '2_3w'].includes(horizon)) return null;
  const row = scale.horizons?.[horizon];
  if (row?.status !== 'OK' ||
      !Number.isInteger(row.bull) || !Number.isInteger(row.bear) ||
      row.bull < 0 || row.bull > 10 || row.bear < 0 || row.bear > 10 ||
      row.bull + row.bear !== 10 ||
      !['BULLISH', 'LEAN_BULLISH', 'NEUTRAL', 'LEAN_BEARISH', 'BEARISH'].includes(row.bias)) return null;
  // Check the upstream published bias is internally consistent. This is
  // validation, not creation of a browser-side market classification.
  const delta = row.bull - row.bear;
  const expectedBias = delta >= 4 ? 'BULLISH' : delta >= 2 ? 'LEAN_BULLISH'
    : delta <= -4 ? 'BEARISH' : delta <= -2 ? 'LEAN_BEARISH' : 'NEUTRAL';
  if (row.bias !== expectedBias) return null;
  return { bull: row.bull, bear: row.bear, bias: row.bias };
}
