# Claude OTA Framework Reconciliation — BTC ETF 4 August and In-Progress ETHBTC

```yaml
ota_run_timestamp_utc: 2026-08-05T19:16:53.370Z
reference_data_ping_run_id: run-aebc326ae71e48109b9b
reference_data_ping_snapshot_id: snap-554c617f944e41ad91bf
maturity_event: NONE
canonical_state_change: NONE
portfolio_action: NONE
```

## Accepted incremental evidence

### BTC ETF 4 August total and issuer structure

The supplied BTC ETF total of +211.5M matches the direct DATA PING owner exactly. The issuer breakdown is accepted as user-supplied fresh-payload detail:

```yaml
IBIT: 170.3
FBTC: 19.6
ARKB: 9.2
BITB: 8.7
MSBT: 3.7
positive_tickers: 5
negative_tickers: 0
```

This strengthens the conclusion that the 4 August BTC inflow was broad enough to include five positive products but remained heavily concentrated in IBIT.

### Live ETHBTC repair attempt

The OTA running value of 0.02957 and high of 0.02975 are directionally consistent with the current DATA PING direct value of 0.02959. The move is material and represents the closest current approach to 0.0300 in the supplied sequence.

It is not a maturity event. The session is in progress, 0.0300 was not touched, and no settled close is available. H7 and the rotation gate remain unchanged.

### Source QA

The fresh payload served from IP 104.22.93.101 is accepted as additional evidence that IP range alone cannot classify a Farside payload as stale. Footer-date and latest-session validation remain the operational freshness gate.

## Main-thread corrections

### ETH ETF 4 August is not pending

The OTA did not retrieve ETH ETF 4 August and therefore carried ETH only through 3 August. The current DATA PING direct owner already records:

```yaml
ETH_ETF_2026_08_04_usd_m: 53.1
status: DIRECT_OWNER_PASS
```

Accordingly, the latest same-session ETF structure is dual-positive, not BTC-positive versus ETH-negative. BTC still dominates absolute dollar flow by +158.4M.

### Rolling-window claims remain quarantined

The repository direct-row owner currently reproduces:

```yaml
BTC_3_session_usd_m: 116.2
BTC_5_session_usd_m: 381.4
BTC_7_session_usd_m: 320.1
BTC_10_session_usd_m: -76.0
BTC_15_session_usd_m: 673.1
BTC_20_session_status: UNAVAILABLE_ONLY_15_OWNER_ROWS
```

The OTA claims 5-session +118.4M, 7-session +80.3M and 20-session +153.0M. These do not reconcile to the direct owner and are not promoted. The assertion that all four windows are positive is therefore not accepted by the main thread.

### Flow-versus-price interpretation

The OTA’s anti-transmission flow claim was based on stale cross-asset coverage because ETH 4 August had not been retrieved. The current direct owner shows positive 4 August flows for both BTC and ETH, while live ETH/BTC also rebounded.

The remaining constraint is not opposite flow direction; it is insufficient persistence and BTC’s much larger absolute flow dominance. ETHBTC taker-buy share is strong on 1h but below 50% on 4h and 12h, and the 0.0300 gate is still untouched.

## H7 and F1

```yaml
H7_latest_formed_extension_row: 14
H7_row_15_status: NOT_FORMED
H7_historical_score_change: NONE
F1_settled_post_window_sessions: 9
F1_additional_in_progress_session: 1
F1_settled_breach_count: 0
H_WIN_01_status: UNPROVEN_LOW_MODERATE
```

The OTA’s “ten sessions” wording is retained only as nine settled sessions plus one in-progress session. No closed-window score changes.

## Framework result

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REPAIR_WITH_EMERGING_ETH_RELATIVE_REBOUND_AND_DUAL_POSITIVE_ETF_FLOW_BUT_NO_SETTLED_0030_OR_MULTI_WINDOW_ETHBTC_PERSISTENCE
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

The evidence improves the near-term repair picture but remains below the framework’s confirmation threshold.