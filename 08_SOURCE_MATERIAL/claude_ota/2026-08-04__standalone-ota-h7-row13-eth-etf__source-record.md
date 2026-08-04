# Claude OTA Source Record — H7 Row 13 and ETH ETF

```yaml
run_timestamp_utc: 2026-08-04T07:32:46.629Z
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
previous_claude_ota_reference: 2026-08-03T15:38:36.441Z
new_information_count: 5
matured_claude_experiment_count: 1
falsified_hypothesis_count: 0
source_qa_event_count: 3
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## H7 row 13 supplied evidence

```yaml
row: 13
date_cest: 2026-08-03
BTC_close: 63590.15
ETH_close: 1863.60
ETHBTC_close: 0.02931
BTC_1d_pct: 0.02
ETH_1d_pct: -1.42
ETH_minus_BTC_spread_pp: -1.44
leader: BTC
COND2_last_3: 1_OF_3_NOT_MET
COND3: MET
rolling_5_session_OLS_slope_pct_per_session: -0.177
arc_rows: 13
arc_first_close: 0.02933
arc_latest_close: 0.02931
arc_endpoint_change_pct: -0.07
arc_min: 0.02889
arc_max: 0.03007
historical_score_change_claimed: NONE
```

Supplied raw-row SHA-256 receipts:

```yaml
BTCUSDT: 0acad8b9409ec844df445b9ec70f2dda18d36be1009de87967d29b259aed302d
ETHUSDT: 73e8ab0c0710b7c95cedf05f84addb2fb40a7149f69255b0771044854c1f79bb
ETHBTC: a319cc281d945f52556d153cb17ecfe33b0fd986d27a4d3aac0d18095aa7a789
```

## F1 post-window observation

```yaml
session_date_utc: 2026-08-03
BTC_intraday_low: 62300.00
BTC_settled_close: 63520.00
close_vs_62342_pct: 1.89
low_vs_62342_pct: -0.07
historical_F1_score_change_claimed: NONE
H_WIN_01_status: UNPROVEN
H_WIN_01_confidence: LOW_MODERATE
```

This was supplied as the second settled session after the F1 window where the intraday low crossed below 62,342 but the settled close remained above both candidates.

## ETH/BTC threshold sequence

```yaml
2026_08_03_UTC_close: 0.02929
2026_08_03_UTC_high: 0.02966
2026_08_04_running_value: 0.02922
sessions_without_0_0300_touch_claimed: 8
0_0275_touched: false
lowest_low_supplied: 0.02913
sequence_classification_claimed: SEQUENCE_TERMINATED_SUSTAINED
```

## ETH ETF supplied evidence

```yaml
source: farside.co.uk/eth
payload_footer_date: 2026-08-03
actual_retrieval_date: 2026-08-04
payload_generation_status: ONE_GENERATION_STALE
2026_07_31_total_usd_m: 9.0
2026_07_31_ETHB_usd_m: 15.4
2026_07_31_ETHA_usd_m: 0.0
2026_07_31_FETH_usd_m: -1.9
2026_07_31_ETHW_usd_m: -2.5
2026_07_31_ETH_usd_m: -2.0
supplied_3_session_sum_usd_m: -11.1
supplied_5_session_sum_usd_m: 9.3
supplied_7_session_sum_usd_m: -4.4
supplied_20_session_sum_status: UNKNOWN_ONLY_13_ROWS
2026_08_03_row_status_in_stale_payload: NOT_PUBLISHED_ALL_DASHES
```

## Source QA supplied

- Price cache guard: CURRENT_RUN_FRESH.
- Farside payload: one generation stale; historical 31 July row used with explicit reasoning.
- ETHB was reported as the sole positive contributor on 31 July while ETHA contributed zero.

## Source boundaries

The report had no reference bridge and did not know current framework state. Its H7 settled rows and F1 settled-close observation are eligible for reconciliation. ETF historical row-level evidence is eligible only where consistent with the direct reconciled ETF ledger. Rolling ETF sums and current-publication claims require main-thread precedence checks.

The complete user-supplied packet remains in the originating conversation transport.