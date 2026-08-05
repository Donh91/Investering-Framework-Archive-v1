# Claude OTA Source Record — 4 August UTC Settle and ETH ETF

```yaml
source_run_timestamp_utc: 2026-08-05T05:09:21.113Z
source_run_timestamp_cest: 2026-08-05T07:09:21+02:00
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
new_information_count: 5
matured_claude_experiment_count: 1
source_qa_event_count: 3
```

## 4 August UTC settlement as supplied

```yaml
BTCUSDT_open: 63520.00
BTCUSDT_high: 64549.16
BTCUSDT_low: 63322.01
BTCUSDT_close: 64106.56
ETHUSDT_close: 1869.75
ETHBTC_high: 0.02940
ETHBTC_low: 0.02912
ETHBTC_close: 0.02917
F1_post_window_sessions: 9
F1_settled_closes_below_candidates: 0
historical_F1_score_change_claimed: NONE
```

The OTA reported that 4 August was the tenth session without a 0.0300 touch when the new 5 August in-progress session was included. The main-thread record separates nine completed sessions from one in-progress session.

## ETH ETF 3 August evidence as supplied

The OTA reported a fresh Farside generation with footer `04 August 2026`.

```yaml
session: 2026-08-03
total_usd_m: -11.9
positive_tickers: 1
ETHA: -9.0
ETHE: -7.8
FETH: -0.9
ETHB: 5.8
```

The total matches the direct ETF owner value already captured by DATA PING. Issuer-level rows are preserved as user-supplied fresh-payload evidence and were not independently retrieved by the main thread.

The OTA identified the same-session cross-asset divergence:

```yaml
BTC_total_usd_m: 170.1
ETH_total_usd_m: -11.9
IBIT_usd_m: 111.4
ETHA_usd_m: -9.0
BTC_positive_tickers: 8
ETH_positive_tickers: 1
```

The OTA also reported ETHB as the sole positive ETH contributor for two consecutive settled sessions:

```yaml
2026_07_31_ETHB_usd_m: 15.4
2026_07_31_ETH_total_usd_m: 9.0
2026_08_03_ETHB_usd_m: 5.8
2026_08_03_ETH_total_usd_m: -11.9
```

## Rolling sums as supplied

```yaml
ETH_3_session_usd_m: 10.6
ETH_5_session_usd_m: -13.7
ETH_7_session_usd_m: -16.9
BTC_3_session_usd_m: 137.8
BTC_5_session_usd_m: 108.3
BTC_7_session_usd_m: -131.5
```

These values require reconciliation against the repository's direct row ledger before owner use.

## Source QA correction

The source corrected its own outstanding item `ETH-ETF 1/8`. 1 August 2026 was a Saturday and no ETF session existed. The item is cancelled as a phantom session, not resolved as a retrieved row.

The source also retired H-SRC-02 as operationally resolved after eight observations showed no stable time-of-day freshness rule. Footer-date versus actual-date validation remains the operational gate.

## Source boundary

This record preserves the Claude OTA report as user-supplied research evidence. Framework state, portfolio permissions and canonical effects were not assessed by the source and require main-thread reconciliation.