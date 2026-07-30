# DATA PING framework read — run_6ed8dcf0ec6a4d62a429c7f10fcb5f5b

**Snapshot UTC:** 2026-07-30T05:14:00Z  
**Collector status:** PARTIAL, runtime budget exhausted  
**Main-framework acceptance:** SOURCE_QA_ONLY, not market-state ingest  
**Collector predecessor:** `snap_0e19c112413d471d8270cad1a18148a7`

## Adjudication

```yaml
classification: NO_NEW_MARKET_CLASSIFICATION_RUNTIME_BUDGET_EXHAUSTED
market_state_ingest: REJECTED_FAIL_CLOSED
source_QA_ingest: ACCEPTED
longitudinal_market_run: NOT_ACCEPTED
full_rerun_required: YES
new_deep_capture_request: NO
```

Only CoinGecko global, current BTC/ETH and the two Top-100 source pages were retrieved. The run attempted 6 of 60 planned core actions. Direct Binance owner feeds, OKX, ETF, CFGI, FRED, chain TVL, DEX and the breadth aggregate were not available.

The packet field `packet_usable_for_main_thread_ingest: true` is narrowed by the main framework to QA ingest only. It cannot authorize market-state replacement when mandatory direct feeds and breadth are missing.

## Available diagnostic fields

```yaml
BTC_CoinGecko_usd: 63904
ETH_CoinGecko_usd: 1900.11
ETHBTC_derived: 0.0297335065
total_market_cap_usd: 2268327470767.693
BTC_dominance_pct: 56.5303274244
ETH_dominance_pct: 10.1092647916
```

Compared with the previous accepted DATA PING fields:

```yaml
BTC_delta_pct: -0.115665
ETH_delta_pct: +0.280241
ETHBTC_derived_delta_pct: +0.395309
total_market_cap_delta_pct: +0.007296
```

These values show a nearly flat headline market during the comparison window. The derived ETHBTC ratio remained below 0.0300, but it is diagnostic only and cannot score the direct ETHBTC gate.

## Breadth replayability

```yaml
Top100_page1: PASS
Top100_page2: PASS
raw_rows: 100
deduped_rows: 100
filtered_aggregate: UNAVAILABLE
constituent_sidecar: NOT_EMITTED
breadth_replayability: FAIL
constituent_transition_analysis: NOT_PERMITTED
```

The run occurred after the canonical Point-in-Time Breadth Sidecar Retention Addendum became active. Page retrieval succeeded, but runtime exhaustion occurred before aggregation and no sidecar was preserved. This is recorded as the first live breach associated with issue #224.

## Collector semantics defect

```yaml
planned_core_actions: 60
attempted_core_actions: 6
reported_PASS: 4
reported_FAIL: 56
reported_SKIPPED_RUNTIME_LIMIT: 0
```

Most receipts labeled `FAIL` were never executed. They should be represented as `SKIPPED_RUNTIME_LIMIT`, while only invoked source failures may count as `FAIL`. The correction is tracked in issue #229.

## Framework state preservation

No valid evidence in this packet overturns the last accepted framework state:

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Prospective evidence

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

The next ordinary DATA PING must be a fresh full run. This packet must not be used as the predecessor for market-state scoring, although its source-QA failure record remains part of the audit trail.