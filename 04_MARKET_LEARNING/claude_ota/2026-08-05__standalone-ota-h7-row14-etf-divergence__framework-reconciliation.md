# Claude OTA Framework Reconciliation — H7 Row 14 and ETF Divergence

## Acceptance

```yaml
source_runs:
  - 2026-08-04T22:26:21.108Z
  - 2026-08-05T05:09:21.113Z
operating_mode: STANDALONE_OTA_NO_REFERENCE_BRIDGE
source_reference_data_ping_run_id: null
main_thread_reference_bounded_run_id: run_18f02b7aa0334c9e
acceptance: EXPERIMENT_EVIDENCE_ETF_STRUCTURE_PROVENANCE_RESOLUTION_AND_SOURCE_QA_WITH_ROLLING_SUM_CORRECTIONS
canonical_state_change: NONE
portfolio_effect: NONE
new_policy_event: false
new_A_class_receipt: false
new_shadow_dual_run: false
```

## H7 row 14

H7 row 14 is accepted as direct settled experiment evidence.

```yaml
latest_formed_extension_row: 14
post_maturity_extension_number: 6
row_14_BTC_close: 64194.00
row_14_ETH_close: 1872.32
row_14_ETHBTC_close: 0.02917
row_14_leader: BTC
row_14_ETH_minus_BTC_spread_pp: -0.48
COND2_last_3: 1_OF_3_NOT_MET
rolling_5_session_slope_pct_per_session: -0.296
prior_slope_pct_per_session: -0.177
first_close: 0.02933
latest_close: 0.02917
endpoint_change_pct: -0.55
post_maturity_follow_through: INACTIVE_CONFIRMED_CONTINUING
historical_score_change: NONE
```

The failed transmission signal weakened again. BTC rose more than ETH, ETH/BTC settled at 0.02917 and the five-session slope became more negative. The sixth post-maturity extension therefore reinforces the original classification: early transmission candidate, not rotation confirmation.

No lapse, retirement or retrigger rule is invented because those rules remain undefined.

## 4 August UTC settlement and F1

```yaml
BTC_UTC_close: 64106.56
BTC_UTC_low: 63322.01
ETH_UTC_close: 1869.75
ETHBTC_UTC_close: 0.02917
F1_post_window_sessions: 9
F1_settled_close_breaches_below_candidates: 0
F1_historical_score: NOT_FAILED
F1_score_change: NONE
H_WIN_01_status: UNPROVEN_LOW_MODERATE
```

BTC closed above 64K and remained well above both F1 candidates. This is constructive for BTC repair but does not reopen or rescore the closed F1 window.

The absence of a settled candidate breach for nine sessions remains weak counter-evidence to the sharpest H-WIN-01 formulation. The preregistered confidence-change threshold was not met.

## ETH/BTC threshold sequence

```yaml
latest_settled_Copenhagen_close: 0.02917
latest_settled_UTC_close: 0.02917
completed_sessions_without_0_0300_touch_claimed: 9
additional_in_progress_session_without_0_0300_touch: 1
combined_claimed_count: 10
0_0275_touched: false
rotation_permission: CLOSED
```

BTC reclaiming 64K is not sufficient while ETH/BTC continues to deteriorate and remains below 0.0300.

## ETF precedence and provenance

The direct DATA PING owner had already established the 3 August totals:

```yaml
BTC_ETF_usd_m: 170.1
ETH_ETF_usd_m: -11.9
```

The OTA adds fresh-generation issuer structure:

```yaml
BTC_positive_tickers: 8
BTC_negative_tickers: 0
IBIT_usd_m: 111.4
FBTC_usd_m: 33.4
ETH_positive_tickers: 1
ETHA_usd_m: -9.0
ETHB_usd_m: 5.8
```

This is a strong same-session divergence: broad BTC ETF absorption versus negative ETH ETF flow. It confirms the existing `BTC_LED_ABSORPTION_WEAK_TRANSMISSION` reading.

Issuer detail is retained as user-supplied fresh-payload evidence and was not independently retrieved by the main thread. Session totals retain DATA PING direct-owner authority.

The OTA also reports that the 31 July BTC value and issuer breakdown were reverified unchanged against a fresh generation. The prior reverification quarantine is therefore marked resolved as a user-supplied provenance result.

`ETH-ETF 1/8` is removed from unresolved provenance because 1 August was a Saturday and no US ETF session existed.

## Rolling-window correction

The repository direct row ledger through 31 July plus the direct 3 August totals reproduces:

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

The following OTA values are rejected from owner status because they do not reproduce from the direct row ledger:

```yaml
OTA_BTC_5_session_usd_m: 108.3
OTA_BTC_20_session_usd_m: -100.8
OTA_ETH_3_session_usd_m: 10.6
OTA_ETH_5_session_usd_m: -13.7
OTA_ETH_7_session_usd_m: -16.9
```

The BTC 20-session claim also exceeds the available 14-row owner history. These values remain quarantined rather than silently corrected.

## Source QA

```yaml
price_cache_guard: PASS_AS_SUPPLIED
H_SRC_01_status: FALSIFIED_UNCHANGED
H_SRC_02_status: RETIRED_OPERATIONALLY_RESOLVED
Farside_footer_gate: RETAINED_AS_ONLY_OPERATIONAL_FRESHNESS_GATE
phantom_ETH_ETF_2026_08_01: CANCELLED
```

H-SRC-02 is accepted as operationally resolved: eight observations did not support a stable time-of-day freshness rule. Footer-date and latest-session validation remain mandatory each run.

## Framework result

```yaml
market_cycle: EARLY_BULL_ATTEMPT_BTC_LED_EXTENDED_TRANSITION
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
rotation: NO_ROTATION
capital_lifecycle: WAIT
post_flush: MIXED_FRAGILE_REPAIR
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
risk_substate: BTC_LED_ABSORPTION_WEAK_TRANSMISSION
canonical_state_change: NONE
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_increment: 0
shadow_dual_run_valid_runs: 5
final_holdout_opened: false
```

BTC repair improved enough to close above 64K, but ETH/BTC weakened further and ETF flows diverged sharply in BTC's favor. Without current compatible v1.1 breadth and a confirmed ETH/BTC recovery above 0.0300, there is no selective-alt-rotation or entry upgrade.

**Top-up og købsvindue:** Afvent fortsat nye top-ups; BTC-reparationen er styrket over 64K, men H7 falder igen, ETH/BTC er 0,02917, ETF-flowet favoriserer klart BTC frem for ETH, og aktiv selektiv altcoin-positionering kræver stadig kompatibel breadth samt settled ETH/BTC-bekræftelse over 0,0300.