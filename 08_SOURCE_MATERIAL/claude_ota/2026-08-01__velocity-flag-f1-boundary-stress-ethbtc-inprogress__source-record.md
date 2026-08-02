# Claude OTA source record — velocity flag

```yaml
source_run_timestamp_utc: 2026-08-01T19:20:42.768Z
operating_mode: STANDALONE_OTA
run_type: VELOCITY_FLAG_NOT_FULL_RUN
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
matured_experiments: 0
canonical_authority: NONE
portfolio_authority: NONE
```

## Supplied point-in-time observations

- BTCUSDT 2026-08-01 in-progress intraday low: 62,275.00.
- Higher F1 threshold candidate 62,342: low was 0.11% below.
- Lower F1 threshold candidate 62,200: low remained 0.12% above.
- Supplied running BTC value at retrieval: 62,564.01, above both candidates.
- ETHBTC 2026-08-01 in-progress running value: 0.02938; low 0.02923; high 0.02974.
- No 0.0300 touch was reported for the in-progress session.
- H7 row 11 was explicitly NOT_FORMED at retrieval.
- Coinbase returned HTTP 503; three of four venues remained reachable with close parity.

## Source wording correction

The source headline says BTC traded below both F1 threshold candidates. The supplied numbers do not support that wording. The low of 62,275 was below 62,342 but above 62,200. The accepted description is therefore: first post-window intraday passage below the higher threshold candidate only.

## Boundaries

All market observations in this source record were in-progress and non-settled. F1's scoring window was already closed and its rule used settled closes. No experiment score, framework state or portfolio permission can be changed by this record.
