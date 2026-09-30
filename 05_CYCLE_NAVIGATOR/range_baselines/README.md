# Deterministic Cycle Navigator Range Baselines

Status: PROSPECTIVE SHADOW BENCHMARK

Purpose: benchmark AI-generated weekly BTC/ETH ranges against a deliberately simple deterministic method.

## Forecast method

`MEDIAN_4W_ASYMMETRIC_WEEKLY_EXCURSION_FROM_PRIOR_CLOSE_v1`

For each asset:

1. Use only completed, READY 168-hour weekly calibration packs strictly before the target ISO week.
2. Take at most the latest four eligible weeks.
3. For each week calculate:
   - upside excursion = `high / open - 1`;
   - downside excursion = `1 - low / open`.
4. Take the median upside and downside excursion independently.
5. Anchor the next forecast at the last completed week's close.
6. Freeze:
   - `low = anchor * (1 - median downside)`;
   - `high = anchor * (1 + median upside)`.

Crypto trades continuously, so the completed-week close is used as the transparent next-week anchor. This is a benchmark, not a calibrated confidence interval.

## Independence

The deterministic baseline is generated before the weekly Cycle Navigator model call and is deliberately **not** supplied to the LLM context.

This allows later comparison between:
- the public/AI Cycle Navigator range;
- the continuity baseline where applicable;
- this deterministic historical-volatility baseline.

## Outcome metrics

No aggregate score is created.

For BTC and ETH separately record:
- full-range containment;
- lower miss as % of actual weekly open;
- upper miss as % of actual weekly open;
- predicted width as % of actual weekly open;
- actual width as % of actual weekly open;
- midpoint error as % of actual weekly open.

A very wide interval is therefore visible rather than being rewarded merely for containment.

## Files

- `forecasts/YYYY/Wxx.json` - immutable prospective baseline.
- `scores/YYYY/Wxx.json` - immutable post-week outcome.

## Authority

Shadow benchmark only.

No portfolio execution.
No Official Cycle Navigator range override.
No market-threshold or model-weight change.
No automatic promotion.
