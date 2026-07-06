# Master Monday v3.1 Raw Archive - 2026-W28

**Dato:** 2026-07-06  
**Status:** RAW_MASTER_MONDAY_ARCHIVE  
**Run type:** FIRST_MASTER_MONDAY_AFTER_GITHUB_EXTENDED_ARCHIVE_IMPLEMENTATION  
**Engine:** Master Monday v3.1 LOCKED, Canonical-aware, Range/Breakout-aware, Forecast Ledger-aware, DATA PING Shadow-Ledger-aware  
**GitHub archive status:** ARCHIVED  
**Live feed:** DATA PING V4  
**Run status:** MANUAL_BACKFILL_PASS  

---

## Pre-flight

```yaml
live_feed: DATA PING V4
expected_live_feed: DATA PING V4, with highest active DATA PING version wins rule
highest_active_data_ping_version: V4
archive_feed_status: V1-V3 = ARCHIVE_CONTEXT
GitHub_access_status: ACCESSIBLE
shadow_ledger_status: PARTIAL
latest_valid_date: NOT_AVAILABLE_AT_RUN_TIME
expected_snapshot_date: 2026-07-06
price_source: USER_VERIFIED for 2026-W27 actual range
sanity_flags:
  - ETHBTC_CURRENT_CONFLICT
  - latest_valid_json_missing_at_run_time
  - backbone_history_csv_missing_at_run_time
action: Master Monday produced as MANUAL_BACKFILL_PASS because machine-readable pointers were missing at run time.
```

---

## Verified weekly range ledger loaded after user backfill

```yaml
RUN_ID: WEEKLY_RANGE_2026_27_20260705_2010
WEEK: 2026-W27
PERIOD: 2026-06-29 to 2026-07-05
SOURCE: USER VERIFIED, CoinGecko / Yahoo OHLC
BTC_HIGH: 63403.77
BTC_LOW: 57778.72
ETH_HIGH: 1802.38
ETH_LOW: 1549.83
BTC_RANGE_USD: 5625.05
ETH_RANGE_USD: 252.55
```

Interpretation:

```text
Post-flush recovery attempt survived.
Weekend repair was real.
ETH had higher beta than BTC.
This validated de-escalation candidate, not confirmed recovery or confirmed rotation.
```

---

## Weekly evaluation

```yaml
classification: PARTIAL_DIRECTIONAL_HIT
reason: recovery attempt survived and no-confirmation discipline remained valid
range_accuracy_status: VERIFIED_ACTUAL_AVAILABLE_BUT_PRIOR_FORECAST_LEDGER_NOT_FOUND_AT_RUN_TIME
learning: Do not mark PRICE_UNVERIFIED when actual range exists but prior forecast ledger is missing. Correct status is ACTUAL_RANGE_VERIFIED + FORECAST_LEDGER_MISSING + RANGE_SCORE_PARTIAL.
```

---

## 1-3 day pulse

```yaml
main_direction: Neutral-to-constructive, but vulnerable
tempo: High-vol compression after recovery spike
btc_range:
  low: 61900
  high: 64200
upper_break_trigger: 4H accept above 63400 followed by daily close above 64200
lower_break_trigger: daily loss of 61900; under 60900 repair weakens
fakeout_definition: break above 63400, then close back below 62900 same day or next 4H session
```

---

## 5-7 day movement type

```yaml
highest_probability_structure: Recovery range with upside test, not clean breakout regime
btc_range:
  low: 60900
  high: 65400
range_strength_score: 6.5
breakout_condition: daily close above 64200 and hold above 63400 as support
breakout_target: 65400 to 66800
breakdown_condition: daily close below 60900
breakdown_target: 59400 then 57800 retest
```

---

## Tight weekly price range forecast

```yaml
btc_weekly_range:
  low: 60900
  high: 65400
eth_weekly_range:
  low: 1540
  high: 1760
btc_upper_break_target: 66800
btc_lower_break_target: 59400 then 57800
eth_upper_break_target: 1850
eth_lower_break_target: 1500 then 1470
btc_upside_invalidation: daily close above 66800
btc_downside_invalidation: daily close below 59400
eth_downside_invalidation: daily close below 1500
price_source: USER_VERIFIED_PREVIOUS_RANGE_PLUS_LIVE_ANCHOR
```

---

## 2-3 week forecast

```yaml
direction_bias: Constructive but not confirmed
structure_bias: BTC-led recovery first
timing_expectation: 1-2 more weeks of repair/confirmation likely before broad alt deployment is justified
break_scenario: BTC holds 61900, reclaims 64200, ETF trend improves, ETHBTC returns above 0.0275
failure_scenario: BTC loses 60900, ETHBTC stays below 0.0275, breadth weakens from 24H into 7D
```

---

## 8 week compass

```yaml
cycle_phase: BTC-led early bull / recovery attempt phase
base_case: market attempts to build higher-low structure, broad altseason not confirmed
btc_8_week_range:
  low: 57800
  high: 72000
macro_liquidity_implication: FRED is production macro-shadow, but current macro read is mixed/cautious-neutral. Macro supports context, not execution unlock.
```

---

## Altcoin phase map

```yaml
rotation_status: EARLY_NOT_CONFIRMED
alt_prepare_score: 5.5
btcd_status: NEEDS_DATA_PING_CONFIRMATION
ethbtc_status: CONFLICT_NEEDS_CONFIRMATION
breadth_status: 7D constructive enough to keep Early Rotation Watch alive. 24H breadth must repair before upgrade.
segments:
  large: HOLD_WATCH
  mid: WAIT
  small: WAIT_AVOID
  micro: AVOID
  memes: AVOID
```

Cycle Navigator language:

```text
Early Rotation Watch -> Selective Rotation -> Broad Altseason.
Current stage: Early Rotation Watch, not confirmed.
```

---

## Market regime and liquidity

```yaml
macro_regime: Mixed / cautious-neutral
liquidity_regime: Not a clean tailwind, liquidity proxy mixed
etf_flow_trend:
  btc_latest_print: +223.5M on 2026-07-02
  btc_w27_net: -526.1M
  btc_trailing_status: 3D/5D/7D still negative
  eth_latest_print: +29.0M on 2026-07-02
  eth_w27_net: -13.7M
  eth_relative_status: stronger than BTC, but not rotation confirmation
stablecoin_deployment_status: Not confirmed
data_quality_impact: Medium
simple_conclusion: De-escalation candidate validated. Recovery not confirmed. Rotation not confirmed. Rebuy locked.
```

---

## Model calibration and scorecard

```yaml
direction_accuracy: HIT_PARTIAL
range_accuracy: VERIFIED_ACTUAL_AVAILABLE_BUT_PRIOR_FORECAST_LEDGER_NOT_FOUND
breakout_fakeout_accuracy: PARTIAL
timing_quality: Good on repair alive, cautious on no confirmation
raw_1_3d_score: 6.5
raw_5_7d_score: 6.0
ptr_sequence_evaluation: F1/F2-watch alive, not clean F2
source_conflict_review: ETHBTC conflict between archived DATA PING state and live anchor
fnp_opportunity_cost_review: FNP ARMED/WATCH, not upgrade
precision_score:
  short_term: 70
  swing: 64
  macro: 68
low_sample: YES for range score because prior Forecast Ledger exact range was missing
```

Forecast IDs logged:

```text
MM_2026_W28_BTC_RANGE_60900_65400
MM_2026_W28_ETH_RANGE_1540_1760
MM_2026_W28_ALT_PREPARE_55
MM_2026_W28_RECOVERY_FRAGILE
```

---

## Cycle Navigator final section

```yaml
weekly_precision_score: 67
altcoin_cycle: Early Rotation Watch, not confirmed
market_cycle: BTC-led recovery attempt
rotation_roadmap: Early Rotation Watch -> Selective Rotation -> Broad Altseason
market_outlook: BTC must hold 61900 and reclaim 64200 for continuation. Below 60900, recovery quality deteriorates. ETH needs ETHBTC confirmation before alt risk broadens.
intraday_price_map:
  btc_support: [61900, 60900, 59400]
  btc_resistance: [63400, 64200, 65400]
  eth_support: [1540, 1500]
  eth_resistance: [1700, 1760, 1850]
key_takeaway: Recovery attempt survived. Rebuy did not unlock. The edge is discipline, not FOMO.
```

---

## Post-run patch note

This Master Monday was generated before the following files existed:

```text
data/canonical/latest_valid.json
data/canonical/backbone_history.csv
03_WEEKLY_OPERATIONS/range_audits/latest_verified_weekly_range.json
03_WEEKLY_OPERATIONS/forecast_ledger/latest_forecast_ledger.json
03_WEEKLY_OPERATIONS/shadow_ledger/latest_shadow_ledger_manifest.json
```

These files were created immediately after the run to prevent the same retrieval failure next week.
