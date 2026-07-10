# W28 RAW Ledger — PULLBACK_EDGE_20260708_01

**Dato:** 2026-W28  
**Status:** RAW_LEDGER / APPEND_ONLY / NOT_CANONICAL_LEARNING  
**Område:** weekly RAW / DATA PING edge-event calibration  
**Primary folder:** `03_WEEKLY_OPERATIONS/weekly_raw/`  
**Related folders:** `02_DATA_PING/live_state_handover/`, `04_MARKET_LEARNING/stress_flush/`  
**Depends on:** DATA PING truth-layer runs; framework event anchors

---

## Governance

```text
EDGE_EVENT_ID: PULLBACK_EDGE_20260708_01
RAW_SOURCE: CUSTOM_GPT_DATA_PING_TRUTH_LAYER
FRAMEWORK_INTERPRETATION: SEPARATE
SHADOW_ROWS: NOT_USED_AS_TRUTH_LAYER
MISSING_VALUES: DATA_MISSING
SILENT_INFERENCE: FORBIDDEN
```

This ledger preserves calibration-relevant run rows. It does not score the signal or create canonical learning.

---

## Compact RAW rows

### 2026-07-08T11:15:00Z

```yaml
run_id: DATA_PING_V4_20260708T111500Z
edge_event_id: PULLBACK_EDGE_20260708_01
row_role: EARLIEST_SOURCE_BACKED_NEAR_PRESENT_CANDIDATE
btc_current: 62114.00
eth_current: 1737.55
ethbtc_current: 0.027980
btc_survival_gate_distance_pct: 0.35
btc_reclaim_gate_status: BELOW_63300
ethbtc_repair_status: HOLDS_0275
breadth_1h_pct: 82
breadth_24h_pct: 12
breadth_7d_pct: 76
btc_etf_latest_completed_m: 21.5
btc_etf_3d_m: 510.7
btc_etf_5d_m: -7.9
btc_etf_7d_m: -683.4
eth_etf_latest_completed_m: 26.9
btc_funding_pct: 0.002898
btc_oi_24h_change_pct: -0.8
btc_oi_3d_change_pct: -5.0
taker_ratio_latest: 1.1086
sensor_candidate: NEAR_PRESENT
framework_acceptance: CANDIDATE_ONLY
```

### 2026-07-08T14:03:00Z

```yaml
run_id: DEEP_DATA_PING_V4_20260708T140300Z
edge_event_id: PULLBACK_EDGE_20260708_01
row_role: CANONICAL_FIRST_PRESENT_ANCHOR
btc_current: 61784.48
eth_current: 1735.39
ethbtc_current: 0.028090
btc_survival_status: LOST_INTRADAY_CURRENT_BELOW
btc_daily_close_below_survival: NO
ethbtc_repair_status: HOLDS_REPAIR
breadth_1h_pct: 44
breadth_24h_pct: 9
breadth_7d_pct: 76
btc_etf_latest_completed_m: 21.5
btc_etf_3d_m: 510.7
btc_etf_5d_m: -7.9
btc_etf_7d_m: -683.4
eth_etf_latest_completed_m: 26.9
eth_etf_3d_m: 76.6
eth_etf_5d_m: 63.8
eth_etf_7d_m: 21.1
btc_funding_pct: 0.004691
btc_oi_24h_change_pct: APPROX_FLAT
btc_oi_3d_change_pct: -4.4
taker_ratio_latest: 0.7657
cfgi_btc_1d: 44
cfgi_btc_4h: 34
cfgi_btc_1h: 35
cfgi_btc_15m: 31
sensor_candidate: PRESENT
framework_accepted_state: PRESENT
```

### 2026-07-08T16:33:00Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260708T163300Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 61886.18
eth_current: 1729.52
ethbtc_current: 0.027960
btc_survival_status: LOST_INTRADAY_CURRENT_BELOW
ethbtc_repair_status: HOLDS_REPAIR
breadth_1h_pct: 91
breadth_24h_pct: 6
breadth_7d_pct: 62
btc_funding_pct: 0.008253
btc_oi_24h_change_pct: 1.15
btc_oi_3d_change_pct: -3.22
taker_ratio_latest: 0.9001
sensor_candidate: PRESENT
alert_status: STILL_ACTIVE
downgrade_result: NO_DOWNGRADE
```

### 2026-07-08T20:06:00Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260708T200600Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 62303.99
eth_current: 1740.13
ethbtc_current: 0.027930
btc_survival_status: RECLAIMED_CURRENT_CLOSE_NOT_CONFIRMED
ethbtc_repair_status: HOLDS_REPAIR
breadth_1h_pct: 71
breadth_24h_pct: 9
breadth_7d_pct: 71
btc_funding_pct: 0.010000
btc_oi_24h_change_pct: 0.76
btc_oi_3d_change_pct: -3.48
taker_state: SELL_SKEW_FADED_TO_MIXED
sensor_candidate: NEAR_PRESENT
alert_status: RESOLVING
downgrade_result: DOWNGRADE_TO_NEAR_PRESENT
```

### 2026-07-09T06:32:00Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260709T063200Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 62756.00
btc_completed_close: 62187.17
eth_current: 1752.35
ethbtc_current: 0.027920
btc_survival_status: RECLAIMED_CURRENT_DAILY_CLOSE_HELD
btc_reclaim_status: BELOW_63300
ethbtc_repair_status: HOLDS_REPAIR
breadth_1h_pct: 94
breadth_24h_pct: 74
breadth_7d_pct: 65
btc_etf_latest_completed_m: -84.9
eth_etf_latest_completed_m: 70.5
btc_oi_3d_change_pct: -3.44
taker_state: SELL_SKEW_FADED_TO_MIXED
sensor_candidate: WATCH
alert_status: RESOLVING
downgrade_result: DOWNGRADE_TO_WATCH
```

### 2026-07-09T17:48:00Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260709T174800Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 63075.86
eth_current: 1749.19
ethbtc_current: 0.027760
btc_survival_status: RECLAIMED_CURRENT_DAILY_CLOSE_HELD
btc_reclaim_status: APPROACH_ONLY_NOT_RECLAIMED
ethbtc_repair_status: HOLDS_REPAIR_NEAR_GATE
breadth_1h_pct: 100
breadth_24h_pct: 76
breadth_7d_pct: 44
btc_etf_latest_completed_m: -84.9
eth_etf_latest_completed_m: 70.5
btc_funding_pct: 0.007253
btc_oi_24h_change_pct: -1.1
btc_oi_3d_change_pct: -3.5
taker_state: MIXED_TO_BUY_DEFENSE
sensor_candidate: WATCH
alert_status: WATCH
```

### 2026-07-10T04:39:00Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T043900Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 64081.00
btc_completed_close: 63274.59
eth_current: 1775.33
ethbtc_current: 0.027700
btc_survival_status: RECLAIMED_CURRENT_DAILY_CLOSE_HELD
btc_reclaim_status: CURRENT_RECLAIMED_CLOSE_NOT_CONFIRMED
ethbtc_repair_status: HOLDS_REPAIR_NEAR_GATE
breadth_1h_pct: 62
breadth_24h_pct: 94
breadth_7d_pct: 59
btc_etf_latest_completed_m: -95.3
eth_etf_latest_completed_m: -52.2
btc_funding_pct: 0.004856
btc_oi_24h_change_pct: 1.1
btc_oi_3d_change_pct: 2.2
taker_state: BUY_DEFENSE_ON_RECLAIM
sensor_candidate: WATCH_FADING
alert_status: RESOLVING
```

### 2026-07-10T09:45:53Z

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T094553Z
edge_event_id: PULLBACK_EDGE_20260708_01
btc_current: 64463.99
eth_current: 1793.72
ethbtc_current: 0.027820
btc_reclaim_status: CURRENT_AND_HOURLY_HELD_DAILY_CLOSE_PENDING
ethbtc_repair_status: GATE_TEST_DEFENDED
breadth_1h_pct: 69
breadth_24h_pct: 83
breadth_7d_pct: 57
btc_etf_latest_completed_m: -95.3
btc_etf_3d_m: -158.7
btc_etf_5d_m: 330.5
btc_etf_7d_m: -188.1
eth_etf_latest_completed_m: -52.2
eth_etf_3d_m: 45.2
eth_etf_5d_m: 94.9
eth_etf_7d_m: 82.1
btc_funding_pct: 0.009287
btc_oi_24h_change_pct: 4.1
btc_oi_3d_change_pct: 0.1
taker_state: BUY_DEFENSE
sensor_candidate: WATCH_FADING
alert_status: RESOLVING
```

### 2026-07-10T11:59:38Z

```yaml
RAW_CALIBRATION_ROW:
  run_id: DATA_PING_HYBRID_v0_5_1_20260710T115938Z
  edge_event_id: PULLBACK_EDGE_20260708_01
  timestamp: 2026-07-10T11:59:38Z
  sensor_edge_candidate: WATCH
  framework_edge_state_baseline: WATCH
  alert_status: RESOLVING
  btc_current: 64425.18
  btc_completed_close: 63274.59
  btc_active_survival_status: CURRENT_AND_CLOSE_ABOVE_61900
  btc_active_reclaim_status: CURRENT_AND_HOURLY_ABOVE_63300_DAILY_CLOSE_UNCONFIRMED
  ethbtc_current: 0.027960
  ethbtc_repair_status: HOLDS_0275
  breadth_1h_pct: 34
  breadth_24h_pct: 89
  breadth_7d_pct: 54
  btc_etf_latest_m: -95.3
  btc_etf_3d_m: -158.7
  btc_etf_5d_m: 330.5
  btc_etf_7d_m: -188.1
  eth_etf_latest_m: -52.2
  eth_etf_3d_m: 45.2
  eth_etf_5d_m: 94.9
  eth_etf_7d_m: 82.1
  btc_funding_pct: 0.007810
  btc_oi_24h_change_pct: 4.10
  btc_oi_3d_change_pct: 2.21
  taker_ratio_latest: 1.0035
  taker_state: NEUTRAL_AFTER_BUY_DEFENSE
  cfgi_market_1d: 51
  cfgi_btc_1d: 52
  cfgi_eth_1d: 54
  deployment_status: UNKNOWN
  data_quality: MEDIUM
  missing_critical_inputs:
    - STABLECOIN_OFFICIAL_MCAP
    - STABLECOIN_7D
    - STABLECOIN_30D
    - CVD
    - BTC_DAILY_CLOSE_GT_63300
    - OUTCOME_72H_PENDING
    - OUTCOME_7D_PENDING
```

---

## Weekly RAW status

```text
RAW_ROWS_ARCHIVED: YES
STATE_TRANSITIONS_LINKED: YES
24H_OUTCOME: STORED_IN_CALIBRATION_V3
72H_OUTCOME: PENDING
7D_OUTCOME: PENDING
EVENT_CLOSE: PENDING
FINAL_WEEKLY_LEARNING: NOT_RATIFIED
```
