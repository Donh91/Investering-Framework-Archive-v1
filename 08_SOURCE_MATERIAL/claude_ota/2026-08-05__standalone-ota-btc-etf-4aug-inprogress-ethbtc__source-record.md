# Claude OTA Source Record — BTC ETF 4 August and In-Progress ETHBTC

```yaml
run_timestamp_utc: 2026-08-05T19:16:53.370Z
run_timestamp_cest: 2026-08-05T21:16:53+02:00
operating_mode: STANDALONE_OTA
run_type: DELTA_ONLY_NO_MATURITY
reference_bridge_present: false
reference_data_ping_run_id: NOT_PROVIDED
main_thread_reference_data_ping_run_id: run-aebc326ae71e48109b9b
previous_claude_ota_reference: 2026-08-05T05:09:21.113Z
new_information_count: 3
matured_claude_experiment_count: 0
falsified_hypothesis_count: 0
source_qa_event_count: 2
```

## Supplied direct BTC ETF claim

```yaml
session: 2026-08-04
BTC_ETF_total_usd_m: 211.5
issuer_detail_authority: USER_SUPPLIED_CLAUDE_OTA_FRESH_PAYLOAD
positive_tickers: 5
negative_tickers: 0
IBIT_usd_m: 170.3
FBTC_usd_m: 19.6
ARKB_usd_m: 9.2
BITB_usd_m: 8.7
MSBT_usd_m: 3.7
footer_date: 05 August 2026
retrieval_ip: 104.22.93.101
```

The total matches the direct DATA PING ETF owner. Issuer detail is retained as user-supplied fresh-payload evidence and was not independently retrieved by the main thread.

## Supplied rolling-window claims

```yaml
BTC_3_session_usd_m: 116.2
BTC_5_session_usd_m: 118.4
BTC_7_session_usd_m: 80.3
BTC_20_session_usd_m: 153.0
```

Only the 3-session value matches the current repository direct-row owner. The 5-, 7- and 20-session values require quarantine pending row-level reconciliation.

## Supplied live ETHBTC observation

```yaml
session_date: 2026-08-05
status: IN_PROGRESS
running_value: 0.02957
high: 0.02975
low: 0.02904
touched_0_0300: false
touched_0_0275: false
claimed_intraday_change_pct: 1.37
```

The live value aligns closely with the contemporaneous DATA PING direct owner at 0.02959. It remains an in-progress observation without threshold touch or settled confirmation.

## No maturity

```yaml
H7_row_15: NOT_FORMED
H7_row_15_maturity_utc: 2026-08-05T22:00:00Z
UTC_daily_settle: 2026-08-06T00:00:00Z
H7_historical_score_change: NONE
F1_historical_score_change: NONE
```

## Supplied source QA

- Cache guard supplied as PASS.
- Footer date matched actual retrieval date.
- The fresh response from IP 104.22.93.101 further contradicts the previously falsified stale-node hypothesis.

## Main-thread reconciliation requirement

The OTA report must be read together with the current direct DATA PING owner. ETH ETF 4 August is not pending in the main thread: the direct owner already records +53.1M. The OTA flow-divergence interpretation based on ETH data only through 3 August is therefore stale relative to the main-thread owner.