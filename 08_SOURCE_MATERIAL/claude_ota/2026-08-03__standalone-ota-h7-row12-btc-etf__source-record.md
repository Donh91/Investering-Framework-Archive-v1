# Claude OTA Source Record

```yaml
source_run_timestamp_utc: 2026-08-03T06:19:02.958Z
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: NOT_PROVIDED
previous_OTA_timestamp_utc: 2026-08-02T06:14:13.076Z
new_information_count: 5
matured_claude_experiment_count_source_label: 1
source_QA_event_count: 3
framework_authority: NONE
```

## Supplied H7 row 12

```yaml
settled_Copenhagen_session_date: 2026-08-02
BTC_close: 63578.00
ETH_close: 1890.43
ETHBTC_close: 0.02973
BTC_return_pct: 1.22
ETH_return_pct: 2.42
ETH_minus_BTC_spread_pp: 1.20
leader: ETH
COND2_last_3: 1_OF_3_NOT_MET
rolling_5_session_slope_pct_per_session: -0.091
arc_first_close: 0.02933
arc_latest_close: 0.02973
arc_endpoint_change_pct_supplied: 1.36
```

Raw row hashes supplied:

```yaml
BTCUSDT: 1059d8ac670f905c6c64229dd0756db9f3b43083c72d8e15ca95c83dd9128f01
ETHUSDT: 514ff2f62efcf4f2a035b0b1a2779b16315c31523b12c428ace1d9644f7f6546
ETHBTC: 1657d8cfdb23843c8d24d3f0acad2627adff3e5e5fb94115760169d7324813dd
```

## Supplied provisional BTC ETF structure

The OTA reported Farside historical rows from a payload whose footer was dated 2 August while retrieval occurred 3 August. Supplied values:

```yaml
2026-07-30_total_usd_m: 233.1
2026-07-31_total_usd_m: -265.4
two_session_swing_usd_m: 498.5
three_session_sum_usd_m: 0.4
five_session_sum_usd_m: -261.5
seven_session_sum_usd_m: -526.5
twenty_session_sum_usd_m: -240.7
2026-07-31_GBTC_usd_m: -52.6
source_authority: DIRECT_STALE_GENERATION
reverification_required: true
```

## Source boundary

The OTA is an external shadow-audit input without reference bridge or canonical authority. H7 settled closes can be crosschecked against the concurrent DATA PING. ETF values remain provisional until fresh-generation or independent corroboration.