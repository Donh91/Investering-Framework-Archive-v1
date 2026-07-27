# Source QA incident: DATA PING run b43a7f8d

## Scope

Run `run_b43a7f8d213c4e63a5e60ca9cb19d764`, snapshot `2026-07-27T17:10:00Z`.

## Findings

1. All 34 Binance core actions failed under geo restriction.
2. Direct ETH/BTC and all Binance-derived feature families are unavailable.
3. All three CFGI values are unavailable.
4. BTC ETF shows a stale 2026-07-23 row even though an accepted 2026-07-24 row exists in prior archive state. The stale row must not regress the owner value.
5. Global stablecoin total remains unavailable; chain distribution is not a valid substitute.
6. Breadth membership hash is unavailable because post-freeze computation was correctly prohibited.
7. `max_final_source_timestamp_utc` is null, while `max_nonfinal_source_timestamp_utc` is correctly populated as `2026-07-27T17:07:45.592Z`.

## Severity

```yaml
source_degradation: HIGH
packet_usability: PARTIAL_WITH_STRICT_LIMITS
canonical_harm: NONE
```

No failed or stale field is allowed to overwrite a fresher accepted owner value.