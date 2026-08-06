# Claude OTA Source Record — H7 Row 15 and 5 August UTC Settlement

```yaml
run_timestamp_utc: 2026-08-06T07:49:36.027Z
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
previous_ota_timestamp_utc: 2026-08-05T19:16:53.370Z
new_information_count: 4
matured_experiment_count: 2
canonical_effect_claimed: NONE
portfolio_effect_claimed: NONE
```

## H7 row 15 — direct settled evidence

```yaml
settlement_basis: SETTLED_CEST
row_number: 15
BTCUSDT_close: 64733.13
ETHUSDT_close: 1908.75
ETHBTC_close: 0.02950
BTC_1D_pct: 0.84
ETH_1D_pct: 1.95
spread_pp: 1.11
leader: ETH
COND2: 1_of_3_NOT_MET
COND3: MET
COND1_latest_three: NOT_MET
five_session_OLS_slope_pct_per_session: -0.109
arc_rows: 15
arc_net_change_pct: 0.58
historical_score_change: NONE
```

Raw row hashes supplied by Claude:

```yaml
BTCUSDT_raw_row_sha256: 7b0412a99c8de5df7f9ac379b9c0f2cc0ebc02faccc03a8b7dd314326db3d656
ETHUSDT_raw_row_sha256: cec0bff85c5bd4ba120515b14c2ec8810a46127597f4559ca7d82c378f66fe4b
ETHBTC_raw_row_sha256: e64f75867171019bf7f0413aec6ff36cc2185e3ac43efd032360b91790a6e8ae
```

The previously withheld in-progress ETH leadership survived settlement, but H7 remained inactive because joint conditions were not satisfied. This is the seventh consecutive maturity with the signal fallen.

## 5 August UTC settlement

```yaml
BTC_close: 64665.23
BTC_high: 65025.22
BTC_low: 63880.00
ETHBTC_close: 0.02951
ETHBTC_high: 0.02975
ETHBTC_low: 0.02904
touched_0_0300: false
closed_above_0_0300: false
sessions_without_0_0300_touch: 12
F1_settled_post_window_sessions: 11
F1_settled_breaches: 0
H_WIN_01: UNPROVEN_LOW_MODERATE_UNCHANGED
```

## ETF status in OTA

Claude did not retrieve ETF data in this run. Any carried-forward ETF values are non-owner context only. The main thread separately received a validation-failed DATA PING with unaccepted 2026-08-05 candidates of BTC `+244.4M` and ETH `+60.8M`; these remain quarantined pending direct valid retrieval.

## Creative extension — quarantined governance candidate

Claude proposed an exploratory H8 concept based on a null-frequency test for H7-style conditions. The proposal is explicitly post-hoc, based on only 14 spread observations and was not executed.

```yaml
status: EXPLORATORY_NOT_PREREGISTERED
merge_into_H7: FORBIDDEN
retroactive_rescoring: FORBIDDEN
candidate_future_use: GOVERNANCE_DESIGN_FOR_NEXT_TRANSMISSION_TEST
```
