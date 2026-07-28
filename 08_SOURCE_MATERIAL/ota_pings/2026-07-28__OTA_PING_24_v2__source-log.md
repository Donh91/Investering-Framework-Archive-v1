# OTA PING #24 v2 — source log

```yaml
source_run: OTA_PING_24_v2
run_type: SHADOW_NON_BINDING
observed_at_utc: 2026-07-28T04:30:08Z
observed_at_cest: 2026-07-28T06:30:08+02:00
binance_server_time_ms: 1785213008802
matured_items: 3
canonical_state_change: NONE
portfolio_action: NONE
```

## Source QA

### Price probes

```yaml
current_run_fresh: true
venues_reached_after_retry: 4_of_4
identical_payloads: 0
one_minute_reference_age_seconds: 9
venue_deviation_range_pct: -0.098_to_0.000
```

Kraken returned HTTP 503 during the first probe attempt. The call is recorded as `EXECUTED_FAIL`, not skipped. Retry succeeded.

### Farside BTC ETF page

```yaml
payload_status: SUSPECTED_STALE_CACHE
page_footer: 2026-07-27
actual_collection_date: 2026-07-28
edge_ip: 172.71.190.124
market_use: QUARANTINED
ETF_2026_07_27: UNVERIFIED_THIS_RUN
dash_semantics: MISSING_NOT_ZERO
```

The visible 2026-07-27 row contained dashes and a displayed total of 0.0. The dashes are not accepted as a verified zero-flow session. The prior settled BTC ETF rows remain unchanged:

- 2026-07-23: -225.1 USDm
- 2026-07-24: -240.1 USDm

The source reports a fourth observation of the edge pattern:

- 172.68.x and 172.70.x: fresh in observed runs;
- 104.22.x and 172.71.x: stale in observed runs.

This remains a source-QA hypothesis, not a canonical network rule.

## F1 death-zone window

Window: 2026-07-21 through 2026-07-27, closed at 2026-07-28T00:00:00Z.

| Session | BTC close | BTC low | Close vs 62,200 | Close vs 62,342 |
|---|---:|---:|---:|---:|
| 2026-07-21 | 66,556.16 | 65,148.75 | +7.00% | +6.76% |
| 2026-07-22 | 66,114.49 | 65,553.67 | +6.29% | +6.05% |
| 2026-07-23 | 65,098.97 | 64,650.00 | +4.66% | +4.42% |
| 2026-07-24 | 64,139.99 | 63,739.75 | +3.12% | +2.88% |
| 2026-07-25 | 64,375.00 | 63,810.00 | +3.50% | +3.26% |
| 2026-07-26 | 65,399.99 | 64,293.81 | +5.14% | +4.91% |
| 2026-07-27 | 63,755.86 | 63,605.56 | +2.50% | +2.27% |

```yaml
closes_below_62200: 0
closes_below_62342: 0
lowest_settled_close: 63755.86
lowest_intraday_low: 63605.56
primary_directional_score: NOT_FAILED
threshold_attribution: OPEN_62200_VS_62342
result_invariant_across_threshold_candidates: true
```

The post-window price must not be conflated with the F1 result. During the new 2026-07-28 in-progress session, BTC traded below every intraday low recorded inside the F1 window, reaching 63,059.39. F1 measured only its preregistered window.

## Low-vol forward log

Anchor: 2026-07-22 settled BTC close 66,114.49.

| Horizon | Date | Close | Return |
|---|---|---:|---:|
| 1D | 2026-07-23 | 65,098.97 | -1.54% |
| 3D | 2026-07-25 | 64,375.00 | -2.63% |
| 5D | 2026-07-27 | 63,755.86 | -3.57% |

```yaml
MAE_pct: -3.79
MFE_pct: 0.30
payoff_ratio: 0.08
sample_size: 1
status: FRAGILE
promotion: NONE
interpretive_weight: NONE
```

The sequence is complete and directionally negative, but it remains one forward observation. It does not override the prior overlap-controlled finding or create a new rule.

## H7 row 6

Preregistered basis: direct Binance ETH/BTC, settled Europe/Copenhagen close.

| CEST date | BTC | ETH | ETH/BTC | BTC 1D | ETH 1D | Spread | Leader |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-07-25 | 64,344.02 | 1,872.65 | 0.02910 | +0.29% | +0.82% | +0.52 pp | ETH |
| 2026-07-26 | 64,858.02 | 1,925.91 | 0.02969 | +0.80% | +2.84% | +2.05 pp | ETH |
| 2026-07-27 | 64,821.25 | 1,941.90 | 0.02995 | -0.06% | +0.83% | +0.89 pp | ETH |

```yaml
positive_increment_run: 4
condition_1: MET
condition_2_ETH_leads_final_3: 3_of_3_MET
condition_3: MET
five_session_OLS_log_slope_per_session: 0.00970
approx_slope_pct_per_session: 0.974
score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
label_change: NONE
```

### Basis sensitivity

The same 2026-07-27 session produces materially different readings:

| Basis | BTC | ETH/BTC |
|---|---:|---:|
| SETTLED_CEST | 64,821.25 (-0.06%) | 0.02995 (+0.88%) |
| SETTLED_UTC | 63,755.86 (-2.51%) | 0.02967 (-0.74%) |

Between 22:00Z and 24:00Z:

- BTC fell 1.64%;
- ETH/BTC fell 0.94%.

The CEST basis is valid because it was preregistered, but row 6 excludes the later risk-off move. This creates a material robustness warning and blocks any stronger label.

### Row 6 hashes

```text
BTCUSDT  raw close 64821.25000000  sha256 8df65d0b0f21f7b252f75fac089f7d3b0a6446708c7a21a79d9059fd2aadbeed
ETHUSDT  raw close 1941.90000000   sha256 5eabc18b78a14158cbe0b88bdf622797521d2b75619cd7be0fd59d4b1042e5e1
ETHBTC   raw close 0.02995000      sha256 d7b4eda0480003b833d31c5574f05daeb992ebd65a1638df404af0fd20b9643c
```

## Post-window market observation

```yaml
BTC_2026_07_27_settled_UTC_close: 63755.86
BTC_2026_07_27_settled_UTC_return_pct: -2.51
BTC_2026_07_28_in_progress_open: 63755.86
BTC_2026_07_28_in_progress_high: 63827.49
BTC_2026_07_28_in_progress_low: 63059.39
BTC_2026_07_28_observed: 63252.22
ETHBTC_2026_07_28_in_progress: 0.02970
ETHBTC_0_0275_margin_pct: 8.00
ETHBTC_distance_below_0_0300_pct: 1.01
```

The intraday move tests the 63.1K repair area but does not provide a settled break.

## Unchanged state

```yaml
F4: GATE_UNMET_SCORED_CLOSED
F5: TRIGGERED_SECOND_SESSION_CONFIRMED_NOT_RETRIGGERED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```

## Next event

`2026-07-28T22:00:00Z` — H7 row 7 CEST settlement.
