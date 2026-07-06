# Farside ETF Flow Ledger — DATA PING Integration

**Dato:** 2026-07-06  
**Status:** CANONICAL  
**Primær placering:** `02_DATA_PING/source_integrations/`  
**Sekundær relevans:** `03_WEEKLY_OPERATIONS/master_monday/`, `04_MARKET_LEARNING/etf_era_absorption/`, `04_MARKET_LEARNING/rotation_survival/`  
**Formål:** Arkivere de seneste Farside API-indskud og fastlægge, hvordan BTC-, ETH- og SOL-ETF-flow skal indgå i DATA PING, RAW 1–3D, RAW 5–7D og Master Monday.

---

## Executive conclusion

Farside API er nu relevant nok til at blive brugt som fast ETF-flow sensor i DATA PING.

Den vigtigste skelnen er:

```text
FLOW PRINT = seneste verificerede handelsdags flow
FLOW TREND = 3D / 5D / 7D / weekly persistens
```

Aktuel W27/Master Monday-læsning:

```text
BTC ETF:
Latest print positive, but weekly/trailing trend still negative.

ETH ETF:
Latest print positive, 2 positive trading-days in a row, weekly near neutral.

SOL ETF:
Small positive weekly flow, useful only as selective L1-risk shadow.

Framework state:
Validated de-escalation candidate,
not confirmed recovery,
not confirmed rotation,
rebuy remains locked pending persistence.
```

---

## Source hierarchy

### Accepted source

```yaml
ETF_FLOW_PRIMARY_SOURCE:
  provider: Farside API
  status: PRIMARY_MACHINE_READABLE_SOURCE
  use_case: ETF flow ledger / print-vs-trend / persistence
```

### Cross-check sources

```yaml
ETF_FLOW_CROSS_CHECK:
  sources:
    - CoinDesk / SoSoValue
    - The Block / SoSoValue
  use_case: independent confirmation of major flow events
```

### Conflict handling

```yaml
CONFLICT_POLICY:
  if_farside_and_sosovalue_minor_delta: PASS_WITH_MINOR_PROVIDER_DELTA
  if_direction_matches_but_size_differs: PASS_WITH_PROVIDER_DELTA
  if_direction_conflicts: SOURCE_CONFLICT / manual review
  if_bitbo_or_holdings_table_conflicts: methodology_conflict / non-blocking unless supported by primary flow table
```

---

## BTC ETF flow — latest archive state

Farside BTC ETF API confirms the critical flow print:

```yaml
BTC_ETF_FLOW_LATEST:
  latest_trading_day: 2026-07-02
  total_flow_usd_m: +223.5
  components:
    IBIT: -40.4
    FBTC: +166.0
    ARKB: +91.8
    BRRR: +1.7
    HODL: +4.4
  source: Farside API
  flow_print_status: PASS
```

Cross-check:

```yaml
BTC_ETF_CROSS_CHECK:
  Farside: +223.5M
  CoinDesk_SoSoValue: +221.7M
  delta: +1.8M
  status: PASS_WITH_MINOR_PROVIDER_DELTA
```

W27 / Master Monday window:

```yaml
BTC_ETF_W27:
  2026-06-29: -231.0M
  2026-06-30: -222.6M
  2026-07-01: -296.0M
  2026-07-02: +223.5M
  weekly_net: -526.1M
```

Trailing flow ledger:

```yaml
BTC_ETF_TRAILING:
  latest_3_trading_day_net: -295.1M
  latest_5_trading_day_net: -970.6M
  latest_7_trading_day_net: -2131.3M
  latest_consecutive_inflow_days: 1
  previous_outflow_streak_days: 10
  previous_outflow_streak_volume: approx -2.71B
```

Framework read:

```yaml
BTC_ETF_FRAMEWORK_READ:
  latest_print: POSITIVE
  flow_trend: IMPROVING_BUT_NOT_CONFIRMED
  weekly_status: NEGATIVE
  use_in_framework: DATA_ONLY
```

Interpretation:

```text
BTC ETF-flow no longer counts as missing/pending.
The first positive print is verified.
But trailing 3D/5D/7D and weekly net are still negative.
Therefore the correct label is:

FLOW PRINT: VERIFIED POSITIVE
FLOW TREND: NOT CONFIRMED
```

---

## ETH ETF flow — latest archive state

Farside ETH ETF API confirms constructive ETH-specific flow repair.

Latest print:

```yaml
ETH_ETF_FLOW_LATEST:
  latest_trading_day: 2026-07-02
  total_flow_usd_m: +29.0
  components:
    ETHA: +29.7
    FETH: +0.8
    ETHV: +1.2
    ETHE: -2.7
  source: Farside API
  flow_print_status: PASS
```

Core flow split:

```yaml
ETH_ETF_CORE_FLOW:
  total_flow: +29.0M
  ETHE_legacy_drag: -2.7M
  core_flow_ex_ETHE: +31.7M
  read: CORE_DEMAND_POSITIVE_LEGACY_DRAG_SMALL
```

W27 / Master Monday window:

```yaml
ETH_ETF_W27:
  2026-06-29: -29.9M
  2026-06-30: -27.6M
  2026-07-01: +14.8M
  2026-07-02: +29.0M
  weekly_net: -13.7M
```

Trailing flow ledger:

```yaml
ETH_ETF_TRAILING:
  latest_2_trading_day_net: +43.8M
  latest_3_trading_day_net: +16.2M
  latest_5_trading_day_net: -26.5M
  latest_7_trading_day_net: -138.7M
  consecutive_positive_trading_days: 2
```

Framework read:

```yaml
ETH_ETF_FRAMEWORK_READ:
  latest_print: POSITIVE
  short_term_flow: IMPROVING
  weekly_status: NEAR_NEUTRAL_BUT_STILL_NEGATIVE
  ethbtc_support: YES_PARTIAL
  rotation_flow_status: EARLY_WATCH_NOT_CONFIRMED
  use_in_framework: DATA_ONLY
```

Interpretation:

```text
ETH ETF-flow is more constructive than BTC ETF-flow on a relative basis.
It supports ETH/BTC >0.0275 as an Early Rotation Watch input,
but it does not confirm rotation because ETH/BTC remains below 0.0300 and broader flow trend is not fully confirmed.
```

---

## SOL ETF flow — latest archive state

Farside SOL ETF API is relevant as a low-weight selective L1-risk sensor.

Important rule:

```text
The row "Staking fee" is metadata and must not be counted as daily flow.
```

Latest print:

```yaml
SOL_ETF_FLOW_LATEST:
  latest_trading_day: 2026-07-02
  total_flow_usd_m: +2.2
  source: Farside API
  flow_print_status: PASS
```

W27 / Master Monday window:

```yaml
SOL_ETF_W27:
  2026-06-29: +5.5M
  2026-06-30: -2.5M
  2026-07-01: +0.5M
  2026-07-02: +2.2M
  weekly_net: +5.7M
```

Trailing flow ledger:

```yaml
SOL_ETF_TRAILING:
  latest_2_trading_day_net: +2.7M
  latest_3_trading_day_net: +0.2M
  latest_5_trading_day_net: +7.7M
  consecutive_positive_trading_days: 2
```

Framework read:

```yaml
SOL_ETF_FRAMEWORK_READ:
  latest_print: SMALL_POSITIVE
  trend_status: SMALL_POSITIVE_EARLY
  confidence: MEDIUM_LOW
  use_in_framework: SOL_SPECIFIC / ALT_RISK_SHADOW_ONLY
```

Interpretation:

```text
SOL ETF-flow can support Selective L1 Watch, but cannot confirm broad rotation or altseason.
It should not unlock small caps, microcaps or memes.
```

---

## Relative ETF-flow snapshot

Current W27 relative flow structure:

```yaml
ETF_RELATIVE_FLOW_W27:
  BTC_weekly_net: -526.1M
  ETH_weekly_net: -13.7M
  SOL_weekly_net: +5.7M
  relative_read: ETH_AND_SOL_RELATIVELY_STRONGER_THAN_BTC
  rotation_flow_status: EARLY_SELECTIVE_WATCH_NOT_CONFIRMED
```

Framework implication:

```text
This improves the quality of the de-escalation candidate.
It does not confirm recovery.
It strengthens Early Rotation Watch, but does not confirm rotation.
The correct state is still:

No Rotation.
Rebuy Locked.
Conditional plan due.
FNP active watch.
```

---

## Farside NAV metadata endpoint

A separate Farside / FS Investors NAV endpoint was supplied:

```yaml
FARSIDE_FUND_NAV:
  nav_date: 2026-07-06
  nav: £177.05
  launch_price: £100.00
  launch_date: 2022-03-29
  total_return_since_launch: +77.05%
  investment_advisor: FS Investors Ltd
  director_of_investment_advisor: Jonathan Bier FCA
  FCA_host: Brooklands Fund Management Ltd
  fund_administrator: Abacus Financial Services Ltd
  auditor: BDO
  registration: Gibraltar Financial Services Commission
```

Classification:

```yaml
FARSIDE_NAV_CLASSIFICATION:
  use_in_raw: NO
  use_in_recovery: NO
  use_in_rotation: NO
  use_in_rebuy: NO
  use_in_etf_flow: NO
  use_case: SOURCE_CONTEXT_ONLY / API_HEALTH / PROVENANCE
```

Interpretation:

```text
NAV metadata is not a market signal and must not affect Master Monday, RAW forecasts or framework state.
```

---

## DATA PING implementation patch

Custom GPT / DATA PING should add these blocks permanently.

### BTC ETF flow block

```yaml
BTC_ETF_FLOW:
  source: Farside API
  latest_trading_day:
  latest_total_flow:
  previous_total_flow:
  3d_net:
  5d_net:
  7d_net:
  weekly_net:
  consecutive_positive_trading_days:
  consecutive_negative_trading_days:
  previous_outflow_streak_days:
  previous_outflow_streak_volume:
  flow_print_status:
  flow_trend_status:
  framework_use: DATA_ONLY
```

### ETH ETF flow block

```yaml
ETH_ETF_FLOW:
  source: Farside API
  latest_trading_day:
  latest_total_flow:
  previous_total_flow:
  2d_net:
  3d_net:
  5d_net:
  7d_net:
  weekly_net:
  consecutive_positive_trading_days:
  consecutive_negative_trading_days:
  core_flow_ex_ETHE:
  ETHE_legacy_drag:
  flow_print_status:
  flow_trend_status:
  ethbtc_support:
  framework_use: DATA_ONLY
```

### SOL ETF flow block

```yaml
SOL_ETF_FLOW:
  source: Farside API
  latest_trading_day:
  latest_total_flow:
  2d_net:
  3d_net:
  5d_net:
  weekly_net:
  consecutive_positive_trading_days:
  consecutive_negative_trading_days:
  trend_status:
  confidence:
  framework_use: SOL_SPECIFIC / ALT_RISK_SHADOW_ONLY
```

### Relative ETF flow block

```yaml
ETF_RELATIVE_FLOW:
  btc_weekly_net:
  eth_weekly_net:
  sol_weekly_net:
  eth_vs_btc_flow_read:
  sol_vs_btc_flow_read:
  rotation_flow_status:
```

### Market calendar / holiday rules

```yaml
ETF_MARKET_CALENDAR_RULES:
  holiday_zero_rows_count_as_flow: false
  zero_rows_on_known_market_holidays: IGNORE_FOR_STREAKS
  staking_fee_rows: METADATA_ONLY
  nav_rows: SOURCE_CONTEXT_ONLY
```

### Allowed status labels

```yaml
FLOW_PRINT_STATUS:
  - PASS
  - PASS_WITH_MINOR_PROVIDER_DELTA
  - PARTIAL_VERIFIED
  - SOURCE_CONFLICT
  - MISSING

FLOW_TREND_STATUS:
  - CONFIRMED_POSITIVE
  - IMPROVING
  - MIXED
  - NEGATIVE
  - NOT_CONFIRMED
  - MISSING

ROTATION_FLOW_STATUS:
  - NO_ROTATION
  - EARLY_WATCH_NOT_CONFIRMED
  - SELECTIVE_WATCH
  - SELECTIVE_CONFIRMED
  - BROAD_CONFIRMED
```

---

## RAW and Master Monday effect

### RAW 1–3D

ETF print data is useful for near-term repair/de-escalation checks.

Current read:

```text
BTC first positive ETF print + ETH 2-day positive sequence + SOL small positive flow
supports short-term repair continuation,
but BTC 63.3K reclaim and ETH/BTC 0.0300 remain unconfirmed.
```

### RAW 5–7D

Trailing ETF trend is decisive.

Current read:

```text
BTC 3D/5D/7D still negative.
ETH 5D/7D still negative but improving.
SOL small positive but low-weight.
Therefore RAW 5–7D remains conditional, not confirmed recovery.
```

### Master Monday

Recommended state line:

```text
ETF missing blocker removed.
BTC ETF first positive print verified, but weekly/trailing trend still negative.
ETH ETF flow is relatively stronger and near-neutral weekly.
SOL ETF flow is small positive, shadow-only.
This validates de-escalation candidate, not confirmed recovery or rotation.
```

---

## Governance boundary

Farside ETF-flow is a sensor layer. It must not directly determine portfolio action.

```text
Farside can support:
- DATA PING flow ledger
- RAW 1–3D / 5–7D confidence
- Master Monday flow calibration
- Early Rotation Watch diagnostics
- FNP opportunity-cost visibility

Farside cannot alone determine:
- Recovery confirmed
- Rotation confirmed
- Rebuy unlocked
- Deployment
- Official row
- Cycle Navigator score
```

---

## Canonical summary for future threads

```text
As of 2026-07-06, Farside API is accepted as the primary machine-readable ETF-flow source for DATA PING. BTC, ETH and SOL ETF-flow must be logged as print-vs-trend ledgers using latest print, 3D/5D/7D net, weekly net and consecutive trading-day persistence. BTC 2026-07-02 flow is verified positive at +223.5M but BTC W27 remains negative at -526.1M. ETH 2026-07-02 flow is +29.0M, with 2 positive trading-days and W27 near neutral at -13.7M. SOL W27 is small positive at +5.7M and should be treated only as SOL-specific / selective L1 shadow. Farside NAV metadata is source context only and not a market signal. The framework state is validated de-escalation candidate, not confirmed recovery, not confirmed rotation, rebuy locked pending persistence.
```
