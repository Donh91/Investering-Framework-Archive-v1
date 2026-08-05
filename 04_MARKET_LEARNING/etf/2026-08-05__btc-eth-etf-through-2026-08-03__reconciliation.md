# BTC and ETH ETF Reconciliation Through 3 August 2026

## Acceptance

```yaml
latest_eligible_settled_US_session: 2026-08-03
BTC_total_authority: DATA_PING_DIRECT_OWNER
ETH_total_authority: DATA_PING_DIRECT_OWNER
issuer_detail_authority: USER_SUPPLIED_CLAUDE_OTA_FRESH_PAYLOAD
rolling_sum_owner: REPOSITORY_DIRECT_ROW_LEDGER_PLUS_2026_08_03_DIRECT_TOTALS
canonical_state_change: NONE
portfolio_action: NONE
```

## Session result

```yaml
BTC_ETF_2026_08_03_usd_m: 170.1
ETH_ETF_2026_08_03_usd_m: -11.9
cross_asset_flow_spread_usd_m: 182.0
```

The session is a clear cross-asset divergence: BTC received broad positive ETF demand while ETH recorded a net outflow. This supports BTC-led absorption and weak ETH transmission.

## Issuer structure

Claude OTA supplied the following fresh-generation issuer detail:

```yaml
BTC_positive_tickers: 8
BTC_negative_tickers: 0
IBIT_usd_m: 111.4
FBTC_usd_m: 33.4
ETH_positive_tickers: 1
ETHA_usd_m: -9.0
ETHB_usd_m: 5.8
```

The direct totals are independently corroborated by DATA PING. Issuer detail is accepted as source evidence but remains tagged as not independently retrieved by the main thread.

ETHB was the sole positive ETH contributor on both 31 July and 3 August. This is a structural micro-observation, not an entry or rotation gate.

## Reproduced rolling windows

Calculations use the archived row payload through 31 July plus the direct 3 August totals.

```yaml
BTC_3_session_usd_m: 137.8
BTC_5_session_usd_m: 120.2
BTC_7_session_usd_m: -131.5
BTC_10_session_usd_m: -84.3
ETH_3_session_usd_m: 9.9
ETH_5_session_usd_m: -13.6
ETH_7_session_usd_m: -72.6
ETH_10_session_usd_m: 63.9
```

Interpretation:

- BTC's 3- and 5-session windows have turned positive.
- BTC's 7- and 10-session windows remain negative.
- ETH's 3-session window is only marginally positive.
- ETH's 5- and 7-session windows are negative.
- The current flow pattern is therefore BTC-led and anti-transmission rather than a confirmed ETH-led rotation.

## OTA rolling-sum discrepancy

The OTA values `BTC 5-session +108.3`, `BTC 20-session -100.8`, `ETH 3-session +10.6`, `ETH 5-session -13.7` and `ETH 7-session -16.9` do not reproduce from the current direct row ledger.

The 20-session claims also exceed the available 14-row owner history. These values are quarantined and do not overwrite the ETF owner status.

## Provenance updates

- BTC 31 July `-265.4M` is marked reverified against a fresh Farside generation, with no revision reported.
- `ETH-ETF 1/8` is removed as a phantom gap because 1 August 2026 was a Saturday.
- BTC and ETH 4 August remain pending until published.

## Framework boundary

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

The ETF update strengthens the existing BTC-led absorption / weak-transmission classification. It does not create a new policy event.