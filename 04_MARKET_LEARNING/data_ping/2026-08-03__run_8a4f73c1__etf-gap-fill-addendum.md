# ETF Gap-Fill Addendum — DATA PING run_8a4f73c1

## New post-run evidence

Direct JSON payloads supplied after the DATA PING close the BTC and ETH ETF ledgers through 31 July 2026.

```yaml
BTC_2026_07_31_usd_m: -265.4
ETH_2026_07_31_usd_m: 9.0
BTC_week31_five_session_sum_usd_m: -61.5
ETH_week31_five_session_sum_usd_m: 10.0
ETH_minus_BTC_week31_flow_spread_usd_m: 71.5
```

## Corrections to external OTA calculations

```yaml
BTC_3_session:
  OTA: 0.4
  corrected: -0.2
BTC_5_session:
  OTA: -261.5
  corrected: -61.5
BTC_7_session:
  OTA: -526.5
  corrected: -526.7
BTC_20_session:
  OTA: -240.7
  status: NOT_VERIFIABLE_FROM_SUPPLIED_13_SESSION_PAYLOAD
```

The $498.5m BTC figure is a two-session directional swing, not the net. Net flow over 30–31 July was -$32.3m.

## Effect on DATA PING interpretation

ETF evidence is mixed rather than uniformly negative. BTC five-session flow is moderately negative, BTC seven-session flow remains strongly negative, and ETH five-session flow is modestly positive. This provides relative ETF support for ETH but does not offset the run's 24.4% breadth, ETHBTC below 0.0300, elevated long positioning and rising open interest.

```yaml
operational_risk_class: DO_NOT_ADD_RISK
risk_class_change_from_original_framework_read: NONE
rotation: NO_ROTATION
rebuy: LOCKED
portfolio_action: NONE
canonical_state_change: NONE
```

Source and calculations are stored in `04_MARKET_LEARNING/etf/LATEST_ETF_FLOW_STATUS_v1.json`.