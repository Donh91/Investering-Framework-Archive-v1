# Active Test Registry Addendum - T4 Execution Microstructure Repair

**Dato:** 2026-07-31  
**Last updated:** 2026-08-01  
**Status:** CANONICAL_REGISTRY_ADDENDUM  
**Område:** Active Test Registry / existing T4 repair  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `2026-07-10__active-test-registry__canonical.md`  

---

## Registry effect

```yaml
new_test_id_created: false
repaired_test_id: PULLBACK_EDGE_20260708_01_OUTCOMES
new_engine_created: false
new_score_created: false
new_engine_freeze_compliance: PASS
```

T4 remains the only test authority for this work.

Linked protocol:

```text
06_RESEARCH_LAB/forward_tests/2026-07-31__t4-execution-microstructure-repair-protocol-v0-1__forward-test.md
```

Live-readback receipt:

```text
06_RESEARCH_LAB/forward_tests/2026-08-01__t4-microstructure-two-live-readback-receipt.md
```

Source owner:

```text
scripts/data_terminal/binance_spot_microstructure_source.py
.github/workflows/binance-spot-owner-manual.yml
research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/WP04C5C_EXECUTION_STATE_v1.json
```

## T4 additive source fields

The following fields are optional source attachments to eligible future T4 events. They do not invalidate earlier T4 rows and are not required when source capture was not active.

```text
source_run_id
spread_bps
depth_imbalance_5
depth_imbalance_20
depth_imbalance_50
taker_quote_imbalance
aggressive_buy_quote
aggressive_sell_quote
aggtrade_window_start
aggtrade_window_end
point_in_time_depth_only
microstructure_interpretation
incremental_value_vs_price_only
```

## Registry status patch

```yaml
t4_microstructure_source_extension:
  status: PROSPECTIVE_SOURCE_CAPTURE_VERIFIED
  required_live_readbacks: 2
  verified_live_readbacks: 2
  source_readback_verified: true
  eligible_event_rows: 0
  valid_source_rows: 0
  valid_outcome_rows: 0
  benchmark: EXISTING_T4_PRICE_ONLY_AND_SETTLED_CANDLE_RECLAIM
  blocked_by:
    - NO_ELIGIBLE_FORWARD_EVENT_ROW
    - NO_MATURED_MICROSTRUCTURE_OUTCOME_ROW
  next_review: NEXT_ELIGIBLE_PRE_REGISTERED_T4_EVENT
  promotion_condition: protocol-defined benchmark outperformance with matured rows
  kill_condition: no incremental value, excess delay, redundancy or persistent source failure
  owner: DATA_PING_GOVERNANCE_RESEARCH_LAB
```

The source-operability gate is passed.

The execution-edge gate remains open and unproven.

This addendum changes no current T4 conclusion and no framework action.
