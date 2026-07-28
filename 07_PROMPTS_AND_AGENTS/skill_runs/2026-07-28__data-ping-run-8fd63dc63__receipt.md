# Skill-run receipt — DATA PING run 8fd63dc63

```yaml
run_id: run_8fd63dc63e47476086215a67dba27573
snapshot_utc: 2026-07-28T05:00:00Z
run_type: DATA_PING_INGEST_AND_FRAMEWORK_READ
branch: agent/data-ping-run-8fd63dc-20260728
```

## Work performed

- preserved the complete collector identity and source-health summary;
- linked the packet to predecessor `snap_0eaa11a7343641a68cd26e3e40c8fcab`;
- recorded 34 attempted Binance geo-restriction failures rather than treating them as skipped;
- accepted current settled Farside rows for 2026-07-27;
- superseded the earlier same-day ETF quarantine only from this later timestamp forward;
- compared all method-compatible fields with the predecessor;
- classified the breadth collapse and ETH deleveraging;
- separated derived ETH/BTC context from direct-gate authority;
- preserved OTA #24 authority for F1, low-vol and H7 row 6;
- withheld H7 row 7 adjudication until its exact settlement event;
- retained all framework and portfolio locks.

## Load-bearing observations

```yaml
BTC_change_since_predecessor_pct: -2.40
ETH_change_since_predecessor_pct: -2.91
ETHBTC_derived_change_pct: -0.52
breadth_advance_ratio: 5.62%
OKX_BTC_OI_change_pct: +1.88
OKX_ETH_OI_change_pct: -8.65
BTC_ETF_2026_07_27: -11.6_USDm
ETH_ETF_2026_07_27: +11.7_USDm
```

## Adjudication

```yaml
classification: BROAD_RISK_OFF_WITH_BREADTH_COLLAPSE_AND_ETH_DELEVERAGING
repair_structure: UNDER_MATERIAL_INTRADAY_PRESSURE_NOT_SETTLED_FAILED
H7_follow_through: UNDER_MATERIAL_STRESS
settled_0_0300: NOT_PROVEN
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```

## Explicit non-actions

- no derived ETH/BTC hard-gate score;
- no H7 row 7 score before settlement;
- no OKX swap substitution for Binance spot;
- no stablecoin total inferred from chain samples;
- no settled breakdown claim from intraday prices;
- no economic backtest;
- no portfolio action.
