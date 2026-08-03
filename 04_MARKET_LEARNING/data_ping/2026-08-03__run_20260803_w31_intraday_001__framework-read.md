# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_20260803_w31_intraday_001
snapshot_id: snap_20260803_w31_intraday_001
snapshot_utc: 2026-08-03T04:49:59.958Z
collector_status: PARTIAL_RUNTIME_LIMITED
planned_core_actions: 60
attempted_core_actions: 10
passed_core_actions: 10
skipped_runtime_limit: 50
supplemental_capture: BINANCE_SPOT_INTRADAY_BTC_ETH_ISO_WEEK_31_2026
main_framework_acceptance: SUPPLEMENTAL_WEEK31_RANGE_AND_CURRENT_SPOT_OBSERVATION_ONLY
latest_decision_bearing_bounded_observation_replaced: NO
accepted_as_next_market_predecessor: NO
```

The run is useful for the complete W31 intraday price range and current direct spot prices. It is not a full DATA PING because fifty core actions were not executed. It therefore cannot replace `run_f15a9c8e1d6b4a0f9e3c72b8145d6f20` as the latest decision-bearing bounded observation and cannot refresh the operational risk class.

## Current spot observation

```yaml
BTC_usd: 62932.01
ETH_usd: 1860.41
direct_ETHBTC: 0.02957
BTC_24h_pct: -0.941
ETH_24h_pct: -0.960
ETHBTC_24h_pct: 0.0
```

BTC and ETH are both approximately one percent lower over twenty-four hours. ETHBTC is flat over twenty-four hours and remains below 0.0300. This is a current spot observation only; without settled daily owner data, breadth, flow and derivatives it cannot establish a new rotation or rebuy conclusion.

## W31 completed price structure

```yaml
BTCUSDT:
  open: 64858.03
  high: 65744.60
  low: 62275.00
  close: 63578.00
  return_pct: -1.9736
  range_pct: 5.5714
ETHUSDT:
  open: 1925.91
  high: 1981.24
  low: 1822.06
  close: 1890.43
  return_pct: -1.8422
  range_pct: 8.7363
settled_hourly_rows_per_asset: 168
gaps: 0
duplicates: 0
```

Both assets closed W31 lower despite materially wider ETH volatility. ETH's high-low range was about 1.57 times BTC's range, while weekly returns were similar. This supplies a clean weekly calibration anchor but not a timing signal by itself.

## Missing decision coverage

```yaml
current_breadth: UNAVAILABLE_AGGREGATION_NOT_COMPLETED
funding: NOT_COLLECTED
open_interest: NOT_COLLECTED
taker_flow: NOT_COLLECTED
OKX_crosscheck: NOT_COLLECTED
ETF: NOT_COLLECTED
CFGI: NOT_COLLECTED
macro: NOT_COLLECTED
stablecoins: NOT_COLLECTED
chain_TVL: NOT_COLLECTED
```

The prior full observation's 51.1% absolute breadth reading must not be forward-filled. The prior operational class `WAIT_FOR_BETTER_WINDOW` remains the latest sensor-supported class, but its prior 3-6 hour reassessment horizon has expired. A new full run is required before any top-up decision.

## Framework decision

```yaml
classification: RUNTIME_LIMITED_SUPPLEMENTAL_W31_RANGE_WITH_CURRENT_SPOT_WEAKNESS_DIRECT_ETHBTC_BELOW_0030_NO_CURRENT_BREADTH_FLOW_OR_DERIVATIVES
rotation: NO_NEW_ASSESSMENT
rebuy: REMAINS_LOCKED_FROM_LATEST_FULL_RUN
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: WAIT_FOR_BETTER_WINDOW_CARRIED_FROM_LATEST_FULL_RUN_NOT_REASSESSED
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
new_shadow_dual_run: NO
latest_decision_bearing_bounded_run_remains: run_f15a9c8e1d6b4a0f9e3c72b8145d6f20
```

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_NEW_FULL_DATA_PING
required_next_object: FULL_60_CORE_ACTION_DATA_PING
reassessment_horizon: 0_TO_3_HOURS
```

**Top-up og købsvindue:** Afvent næste fulde DATA PING inden for 0–3 timer før top-ups, fordi denne runtime-begrænsede kørsel kun dækkede 10 af 60 kernehandlinger og derfor ikke kan genmåle breadth, flow eller derivatives, mens ETH/BTC fortsat ligger under 0,0300.