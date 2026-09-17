# Cycle Navigator Dual Precision Contract v1

Status: proposed canonical repair
Effective target: next Cycle Navigator freeze after merge

## Purpose

Cycle Navigator must preserve two independently auditable precision tracks:

1. PRICE RANGE PRECISION - how well frozen BTC/ETH price envelopes match realized OHLC.
2. MARKET/STRUCTURE PRECISION - regime, ETH/BTC, breadth, leadership/rotation, altseason and deployment/decision structure.

A combined score may be displayed only when both component scores are available under an explicit aggregation rule. Never silently convert a missing component to zero or infer a range after the outcome.

## Mandatory prospective freeze

Every weekly CN publication must freeze, before outcome observation, for BTC and ETH:

- day_1_2 range_low/range_high
- day_3_4 range_low/range_high
- day_5_7 range_low/range_high
- forecast timestamp and ISO week
- source/anchor timestamp used to generate the ranges
- methodology/version identifier

A publication with missing numeric ranges is `RANGE_FREEZE_INCOMPLETE`. It may still publish structural analysis, but it must not present a complete precision score.

## Outcome ingestion

After each scoring window closes, ingest realized BTC/ETH OHLC for the exact matching window and preserve source plus verification timestamp. Do not overwrite the frozen forecast.

For each asset/window preserve:

- forecast_low / forecast_high
- actual_low / actual_high
- lower_breach and upper_breach
- containment status
- overlap/Jaccard
- width ratio where supported

## Score outputs

The scorecard must expose at minimum:

- `price_range_score_btc`
- `price_range_score_eth`
- `price_range_score` (documented aggregation of BTC/ETH)
- `structural_score`
- `combined_score` only when an explicit stable aggregation contract exists
- `score_status`

Public output must show PRICE RANGES and MARKET / STRUCTURE separately before any overall score.

## Fail-closed rules

- No retrospective invention of a forecast range.
- A range recovered from an immutable published CN post may be backfilled, but must retain its publication source and timestamp.
- Missing outcome data => `OUTCOME_PENDING`, not zero.
- Missing frozen ranges => `RANGE_FREEZE_INCOMPLETE`, not zero.
- Current-week partial scoring must be labelled `PRELIMINARY` and never replace the final close-based score.
- Final scoring must use the same frozen ranges that were published prospectively.

## Ledger requirement

`05_CYCLE_NAVIGATOR/forward_range_ledger/` is the canonical machine-readable range audit trail. New forecasts must be written there at freeze time, not reconstructed by a later chat or agent.

## Publication contract

Every future weekly CN should contain a compact precision block in this order:

- Price ranges: BTC x% | ETH y% | Range aggregate z%
- Market / structure: s%
- Overall: c% only if aggregation is supported
- Status: FINAL or PRELIMINARY

This contract fixes the September 2026 failure mode where public posts contained prospective ranges but the machine freeze stored null range fields, making later automated scoring unnecessarily difficult.