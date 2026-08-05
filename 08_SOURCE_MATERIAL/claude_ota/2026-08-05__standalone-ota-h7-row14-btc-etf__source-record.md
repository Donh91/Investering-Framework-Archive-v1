# Claude OTA Source Record — H7 Row 14 and BTC ETF

```yaml
source_run_timestamp_utc: 2026-08-04T22:26:21.108Z
source_run_timestamp_cest: 2026-08-05T00:26:21+02:00
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
new_information_count: 5
matured_claude_experiment_count: 1
source_qa_event_count: 3
```

## H7 row 14 as supplied

```yaml
latest_formed_extension_row: 14
post_maturity_extension_number: 6
BTC_close_CEST: 64194.00
ETH_close_CEST: 1872.32
ETHBTC_close_CEST: 0.02917
BTC_1D_pct: 0.95
ETH_1D_pct: 0.47
ETH_minus_BTC_spread_pp: -0.48
leader: BTC
COND2_last_3: 1_OF_3_NOT_MET
COND1_last_3: NOT_MET_AS_SUPPLIED
COND3: MET_AS_SUPPLIED
rolling_5_session_OLS_slope_pct_per_session: -0.296
prior_slope_pct_per_session: -0.177
arc_first_close: 0.02933
arc_latest_close: 0.02917
arc_net_change_pct: -0.55
historical_score_change_claimed: NONE
```

Raw-row hashes supplied:

```yaml
BTCUSDT_sha256: 300d9c8cb7fb90ad9b1642ad812472f9742973e9d9bca52e0df2609948895b9e
ETHUSDT_sha256: df58dc704494b1312975237dba7c88e89170b46648d02af04b5c8009614814e7
ETHBTC_sha256: 50235e4b2613ed1af586defb842ddfb68045eaab109a74955d4597dcfe199966
```

## BTC ETF evidence as supplied

The OTA reported a fresh Farside generation with footer `04 August 2026`.

```yaml
session: 2026-08-03
total_usd_m: 170.1
positive_tickers: 8
negative_tickers: 0
IBIT: 111.4
FBTC: 33.4
EZBC: 9.2
BTCO: 6.7
HODL: 4.5
BITB: 2.8
ARKB: 2.1
```

The total matches the direct ETF owner value already captured by DATA PING. Issuer-level rows are preserved as user-supplied fresh-payload evidence and were not independently retrieved by the main thread.

The OTA also reported that 31 July BTC ETF `-265.4M` and the issuer breakdown were reverified unchanged against the fresh payload. This is accepted as a provenance-resolution claim.

## Rolling sums as supplied

```yaml
BTC_3_session_usd_m: 137.8
BTC_5_session_usd_m: 108.3
BTC_7_session_usd_m: -131.5
BTC_20_session_usd_m: -100.8
```

These values require reconciliation against the repository's direct row ledger before owner use.

## Threshold and source QA claims

```yaml
ETHBTC_0_0300_touch: false
claimed_sessions_without_0_0300_touch: 9
0_0275_touch: false
H_SRC_02_status: TIME_OF_DAY_REJECTED_AS_GATE_BUT_USEFUL_AS_PLANNING_HEURISTIC
Farside_generation: FRESH_AS_SUPPLIED
BTC_2026_07_31_reverification: RESOLVED_NO_REVISION_AS_SUPPLIED
```

## Source boundary

This record preserves the Claude OTA report as user-supplied research evidence. Framework state, portfolio permissions and canonical effects were not assessed by the source and require main-thread reconciliation.