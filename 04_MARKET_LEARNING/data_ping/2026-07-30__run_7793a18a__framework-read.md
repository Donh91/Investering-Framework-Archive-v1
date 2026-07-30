# DATA PING Framework Read

## Identity

```yaml
run_id: run_7793a18aa7e94ab7b31edc60f74d928a
snapshot_id: snap_610937bd8f6c4be3adf836a2281c9328
snapshot_utc: 2026-07-30T10:42:00Z
collector_status: PARTIAL_RUNTIME_BUDGET_EXHAUSTED
main_framework_acceptance: SOURCE_QA_ONLY
```

## Acceptance

This run is not accepted as a market-state observation and must not replace the last accepted market run.

```yaml
market_state_ingest: REJECTED
source_QA_ingest: ACCEPTED
longitudinal_market_run_accepted: NO
accepted_as_next_market_predecessor: NO
full_rerun_required: YES
```

Only 8 of 60 core actions were attempted. Mandatory direct market feeds, direct ETHBTC, breadth aggregation, ETF, CFGI, VIX, dollar index, Binance context, OKX crosscheck and most downstream features are unavailable.

## Lineage defect

The collector declared `snap_83dbf24776894d07be9b506858820563` as predecessor. That snapshot belongs to the prior runtime-exhausted QA-only run and was explicitly marked:

```yaml
accepted_as_collector_predecessor_for_next_run: false
accepted_as_market_state_predecessor: false
```

The correct market predecessor remains:

```yaml
run_id: run_0bc8a5d0d0464542b29b4d50f2f8e19c
snapshot_id: snap_0e19c112413d471d8270cad1a18148a7
snapshot_utc: 2026-07-29T16:51:00.829Z
```

No delta in this packet may be treated as a canonical longitudinal market delta because the declared predecessor was not accepted.

## Limited diagnostics

```yaml
BTC_CoinGecko_usd: 64502
ETH_CoinGecko_usd: 1917.40
ETHBTC_derived: 0.02972621
total_market_cap_usd: 2286020160072.0195
BTC_dominance_pct: 56.6072935885
ETH_dominance_pct: 10.1229841542
DGS2_pct: 4.26
DGS10_pct: 4.61
yield_curve_10y_minus_2y_pct_points: 0.35
```

Relative to the immediately preceding QA-only attempt, BTC and ETH prices rose about 0.94% and 0.91%, while the derived ETHBTC ratio was nearly unchanged. These values are diagnostic only. The derived ratio cannot score the direct 0.0300 gate.

## Runtime semantics defect

```yaml
planned_core_actions: 60
attempted_core_actions: 8
reported_PASS: 6
reported_PARTIAL: 1
reported_FAIL: 53
reported_SKIPPED_RUNTIME_LIMIT: 0
```

Unexecuted actions were again serialized as `FAIL`. Correct audit semantics require `SKIPPED_RUNTIME_LIMIT`. Recurrence is tracked in issue #229.

## Breadth replayability

```yaml
Top100_page_1: PASS
Top100_page_2: PASS
raw_rows: 100
deduped_rows: 100
breadth_aggregate: UNKNOWN
membership_hash: UNKNOWN
constituent_sidecar: NOT_EMITTED
breadth_replayability: FAIL
```

This is the second consecutive live breach of the point-in-time breadth-sidecar retention rule. It is tracked in issue #224.

## Framework state

The last accepted framework state remains unchanged:

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
chase_ETH_or_large_caps: NO
add_new_risk: WAIT
```

This is not a new market instruction. It preserves the last accepted action state because the current collector run is incomplete.

## Required next run

Run a fresh full DATA PING and force the comparison predecessor to `snap_0e19c112413d471d8270cad1a18148a7`. Preserve both rejected attempts only in the QA lineage.
