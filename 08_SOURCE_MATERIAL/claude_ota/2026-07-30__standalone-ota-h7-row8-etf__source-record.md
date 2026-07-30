# Claude OTA source record, H7 row 8 and ETF structure

```yaml
record_type: EXTERNAL_AUDITOR_OTA_INPUT
source_model: Claude
source_run_timestamp_utc: 2026-07-30T19:04:13.143Z
operating_mode: STANDALONE_OTA
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
previous_source_reference: CLAUDE-OTA-2026-07-29T17:00:49.245Z
new_information_count_claimed: 6
matured_experiment_count_claimed: 1
source_qa_event_count_claimed: 3
main_framework_authority: NONE_UNTIL_RECONCILED
```

## Transmitted H7 row 8

```yaml
CEST_date: 2026-07-29
settlement_close_utc: 2026-07-29T21:59:59.999Z
BTCUSDT_close: 63860.00
ETHUSDT_close: 1898.38
ETHBTC_close: 0.02973
BTC_1D_pct: -0.18
ETH_1D_pct: -1.33
ETH_minus_BTC_pp: -1.15
relative_leader: BTC
extended_log_diff_signs: "-+++++-"
rolling_5_session_OLS_log_slope_per_session: 0.00556
rolling_5_session_OLS_approx_pct_per_session: 0.557
source_classification: SIGNAL_WEAKENED
```

Source-supplied raw-row SHA-256 claims:

```json
{
  "BTCUSDT": "c676e05c033a6ae54ab0cb0e6c6f69a14053e1a5609b0b80646b078696e788e3",
  "ETHUSDT": "41699b115f3c51211aa87f33571f0f6342cdfcd99c8b3abb248448487b150487",
  "ETHBTC": "58d8ebbcbcf82b5c11a0a79be44dda2193f118f7cfe0ccaa1dd4d0cf2a74d390"
}
```

The raw rows were not transmitted to the main framework, so the hashes are retained as source claims and were not independently byte-validated.

## ETHBTC threshold sequence

Source: Binance public data mirror, daily ETHBTC rows, retrieved `2026-07-30T19:04:22.233Z`.

| UTC session | high | settled close | 0.0300 result |
|---|---:|---:|---|
| 2026-07-28 | 0.03012 | 0.03007 | settled acceptance |
| 2026-07-29 | 0.03008 | 0.02986 | settled rejection |
| 2026-07-30 in progress | 0.02996 | — | no touch as of retrieval |

```yaml
source_sequence_classification: SINGLE_SESSION_ACCEPTANCE_THEN_REJECTION
consecutive_settled_closes_at_or_above_0_0300: 0
source_response_sha256_prefix: caaa840f26979a15bea10a45758ad884
```

## BTC ETF structure transmitted

Source: Farside BTC table, footer `30 July 2026`, edge `172.68.138.166`, retrieved approximately `2026-07-30T19:04Z`.

```yaml
2026-07-28_net_flow_usd_m: -49.7
2026-07-29_net_flow_usd_m: 32.1
negative_session_streak_before_2026-07-29: 4
2026-07-29_IBIT_usd_m: 89.8
2026-07-29_FBTC_usd_m: -43.1
2026-07-29_ARKB_usd_m: -14.6
issuer_structure: OPPOSING_MAJOR_ISSUERS
three_session_sum_usd_m: -29.2
five_session_sum_usd_m: -494.4
seven_session_sum_usd_m: -222.1
twenty_session_sum_usd_m: 205.1
```

The source decomposed the change in the 20-session sum from `-230.9` to `+205.1` as:

```yaml
total_change_usd_m: 436.0
roll_off_component_usd_m: 453.6
new_session_component_usd_m: -17.6
interpretation: SIGN_FLIP_DRIVEN_BY_WINDOW_COMPOSITION_NOT_NEW_POSITIVE_INFORMATION
```

ETH ETF sessions for 28 and 29 July were not retrieved in this run and remain unknown, not zero.

## Hypothesis and QA claims

- `H-SRC-02`: source counted this as observation 3 of minimum 10, with Farside fresh after approximately 16:00Z.
- `H-WIN-01`: source retained low-moderate confidence but logged the one-session rejection as evidence against the too-short-window interpretation.
- `H-ETF-01`: weakened and blocked on missing AUM denominator and missing new ETH ETF rows.
- Cache guard: source claimed current-run freshness and three of four venue parity; OKX returned HTTP 503.
- FOMC time was source-supplied as `2026-07-29T18:00:00Z`; outcome was not independently verified in the OTA and no causal attribution was claimed.

## Source-stated authority boundary

```yaml
framework_state_known_by_source: false
canonical_state_change_claimed: NOT_ASSESSED
portfolio_action_claimed: NOT_ASSESSED
new_entry_permission_claimed: NOT_ASSESSED
```
