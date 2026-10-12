# Official Daily Compass — outcome scoring v3 (proposed)

Status: DRAFT / REVIEW_REQUIRED; NOT CANONICAL UNTIL GOVERNED MERGE.
Contract ID: `OFFICIAL_DAILY_COMPASS_SCORING_v3`.
Supersedes v2 **only for newly materialized outcomes after approved deployment**; it does not change frozen forecasts or prior outcomes.

## Reproduced v2 defect
The hourly CSV uses `timestamp_utc` for an individual candle OPEN. Its `source_window_end_utc` is a **collection/batch window end**, sometimes shared by several different candles. The v2 loader incorrectly used that batch end as each candle's close, permitting the wrong endpoint and a false `time_basis.PASS`. Existing affected outcomes must be flagged for independent reconciliation, not silently rewritten.

## v3 endpoint contract
- Preserve the immutable forecast's frozen start value and existing start-reference time rule; target = start reference + 12h/72h/168h.
- For each hourly price row, **candle close = timestamp_utc + 1h**. `source_window_end_utc` must never replace candle close.
- If the collection boundary exists and predates the candle close, quarantine the row. If candle close or collection boundary is later than evaluation `now`, do not score from that row.
- Choose the nearest completed candle close within existing ±1h tolerance; otherwise keep `PENDING_TARGET_EVIDENCE`. No interpolation or future candle.
- Preserve v2 direction thresholds, event triggers, action utility proxy, frozen input, and portfolio authority. The output explicitly records target candle open/close, collection boundary, and the fact that first-knowledge time is **UNKNOWN**; batch end is not proof of point-in-time availability.
- This is an outcome measurement correction, not an investment signal, execution recommendation or proof of trading edge.

## Scientific firewall
Historical v1/v2 outcomes remain immutable and must not be used as v3-calibrated evidence without a separately versioned, source-bound reconciliation with independent review. Do not silently backfill or inflate accuracy. Pairing and performance comparisons must disclose scoring versions; no auto-promotion, thresholds or SELL changes.

Acceptance: Official + Shadow positive/negative synthetic batch-clock regression; existing suites; independent exact-head review; nonauthoring merge; main byte readback; natural post-fix outcome with consumer proof. Until then RESEARCH_ONLY.
