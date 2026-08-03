# BTC and ETH ETF Reconciliation Through 31 July 2026

## Source status

```yaml
source: USER_SUPPLIED_DIRECT_JSON_PAYLOAD
received_at_local: 2026-08-03T09:51:00+02:00
latest_eligible_settled_US_session: 2026-07-31
BTC_latest_session: 2026-07-31
ETH_latest_session: 2026-07-31
session_gap_status: CLOSED_THROUGH_2026_07_31
```

The supplied direct JSON payloads close the BTC and ETH ETF gaps through Friday 31 July. At receipt time on Monday morning Copenhagen time, no 3 August US trading session had settled.

## BTC corrected rolling sums

```yaml
2026_07_30_total_usd_m: 233.1
2026_07_31_total_usd_m: -265.4
two_session_directional_swing_usd_m: 498.5
two_session_net_usd_m: -32.3
three_session_sum_usd_m: -0.2
five_session_sum_usd_m: -61.5
seven_session_sum_usd_m: -526.7
ten_session_sum_usd_m: -27.6
thirteen_session_sum_2026_07_15_to_2026_07_31_usd_m: 291.5
twenty_session_sum: NOT_VERIFIABLE_FROM_THIS_PAYLOAD_ONLY
```

### Correction to prior OTA

The OTA values `3-session +0.4`, `5-session -261.5` and `7-session -526.5` do not reproduce from the supplied daily totals. Correct arithmetic is:

- 3 sessions, 29–31 July: `32.1 + 233.1 - 265.4 = -0.2`.
- 5 sessions, 27–31 July: `-11.6 - 49.7 + 32.1 + 233.1 - 265.4 = -61.5`.
- 7 sessions, 23–31 July: `-225.1 - 240.1 - 11.6 - 49.7 + 32.1 + 233.1 - 265.4 = -526.7`.

The two-session **swing** of $498.5m is correct as the distance from +233.1 to -265.4, but the two-session **net** is -$32.3m.

## BTC issuer structure

```yaml
2026_07_30:
  positive_funds: 7
  negative_funds: 0
  main_driver: IBIT +183.4
2026_07_31:
  positive_funds: 0
  negative_funds: 5
  main_drivers:
    IBIT: -122.7
    FBTC: -54.8
    GBTC: -52.6
    BITB: -17.8
    ARKB: -17.5
```

The broad reversal description is supported. The 31 July GBTC movement is confirmed at -$52.6m in the supplied payload.

## ETH rolling sums

```yaml
2026_07_30_total_usd_m: 12.8
2026_07_31_total_usd_m: 9.0
two_session_net_usd_m: 21.8
three_session_sum_usd_m: -11.1
five_session_sum_usd_m: 10.0
seven_session_sum_usd_m: -34.4
ten_session_sum_usd_m: 113.8
thirteen_session_sum_2026_07_15_to_2026_07_31_usd_m: 176.4
```

Week 31 ended modestly positive for ETH ETFs at +$10.0m, while BTC ETFs ended at -$61.5m. The five-session relative ETF-flow spread was therefore +$71.5m in ETH's favour.

## ETH 31 July issuer structure

```yaml
ETHB: 15.4
FETH: -1.9
ETHW: -2.5
ETH: -2.0
session_total: 9.0
positive_funds: 1
negative_funds: 3
```

The positive ETH total was concentrated in ETHB rather than broad-based across issuers.

## Framework effect

```yaml
BTC_ETF_31_July_reverification: PASS_DIRECT_PAYLOAD
ETH_ETF_31_July_gap: CLOSED
prior_BTC_stale_generation_quarantine: RELEASED_FOR_SESSION_VALUES
prior_rolling_sum_claims: CORRECTED
rotation: NO_CHANGE
rebuy: LOCKED
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

ETF evidence is less negative at the five-session BTC horizon than the OTA claimed and mildly constructive for ETH over week 31. It does not override the latest DATA PING's 24.4% breadth, ETHBTC below 0.0300, rising open interest and crowded long positioning.