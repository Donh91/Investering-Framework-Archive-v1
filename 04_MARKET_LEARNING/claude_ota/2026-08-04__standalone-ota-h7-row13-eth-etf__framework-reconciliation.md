# Claude OTA Framework Reconciliation — H7 Row 13 and ETH ETF

## Acceptance

```yaml
source_run_timestamp_utc: 2026-08-04T07:32:46.629Z
operating_mode: STANDALONE_OTA_NO_REFERENCE_BRIDGE
source_reference_data_ping_run_id: null
main_thread_reference_data_ping_run_id: DP-20260804T062759033Z-R1
acceptance: EXPERIMENT_EVIDENCE_AND_DESIGN_OBSERVATION_WITH_ETF_PRECEDENCE_CORRECTIONS
canonical_state_change: NONE
portfolio_effect: NONE
new_policy_event: false
new_A_class_receipt: false
new_shadow_dual_run: false
```

The OTA source did not contain a reference bridge and could not assess framework state. Main-thread reconciliation uses the latest decision-bearing bounded DATA PING, `DP-20260804T062759033Z-R1`, whose snapshot preceded the OTA by approximately 65 minutes.

## H7 row 13

H7 row 13 is accepted as direct settled experiment evidence.

```yaml
latest_formed_extension_row: 13
post_maturity_extension_number: 5
row_13_leader: BTC
row_13_ETH_minus_BTC_spread_pp: -1.44
COND2_last_3: 1_OF_3_NOT_MET
rolling_5_session_slope_pct_per_session: -0.177
prior_slope_pct_per_session: -0.091
first_close: 0.02933
latest_close: 0.02931
endpoint_change_pct: -0.0682
post_maturity_follow_through: INACTIVE_CONFIRMED_CONTINUING
historical_score_change: NONE
```

The one-session ETH recovery in row 12 did not survive. Row 13 returned leadership to BTC, steepened the rolling slope and moved the 13-row arc slightly below its starting point. H7 therefore remains an early-transmission candidate that failed to become rotation confirmation.

The experiment's original determination remains unchanged. No lapse, retirement or retrigger rule is invented because the source rule still leaves those fields undefined.

## ETH/BTC sequence

```yaml
latest_settled_Copenhagen_close: 0.02931
latest_settled_UTC_close_supplied: 0.02929
latest_bounded_DATA_PING_direct_ETHBTC: 0.02923
settled_status: SEQUENCE_TERMINATED_SUSTAINED
sessions_without_0_0300_touch_claimed: 8
0_0275_touched: false
rotation_permission: CLOSED
```

The OTA and DATA PING agree on the direction: ETH/BTC has returned below the H7 starting area and remains materially below 0.0300. This strengthens the current framework classification of BTC-led absorption with weak transmission. It does not add a new state because the latest DATA PING already encoded that conclusion.

## F1 and H-WIN-01

```yaml
F1_historical_score: NOT_FAILED
F1_score_change: NONE
F1_rule_basis: SETTLED_CLOSES
post_window_intraday_breach_instances: 2
post_window_settled_close_breaches_below_candidates: 0
H_WIN_01_status: UNPROVEN_DESIGN_HYPOTHESIS
H_WIN_01_confidence: LOW_MODERATE
confidence_change: NONE
framework_authority: NONE
```

The 3 August low below 62,342 is accepted as a second post-window boundary-stress observation. The session closed well above both candidates. Because F1 was a closed-window, settled-close experiment, the observation cannot reopen or rescore F1.

Eight post-window sessions without a settled close below either candidate are retained as weak counter-evidence to the sharpest version of H-WIN-01, but the preregistered threshold for changing the hypothesis was not met. Confidence remains unchanged.

## ETF precedence reconciliation

The 31 July ETH ETF total of +9.0M and issuer composition are already consistent with the direct ETF reconciliation in the repository and are accepted as corroboration, not a new ledger row.

```yaml
ETH_ETF_2026_07_31_total_usd_m: 9.0
ETHB_usd_m: 15.4
ETHA_usd_m: 0.0
issuer_composition_note: ETHB_SOLE_POSITIVE_CONTRIBUTOR
ledger_increment: 0
```

The OTA rolling sums are not allowed to overwrite the direct reconciled ETF ledger:

```yaml
OTA_supplied_ETH_5_session_usd_m: 9.3
canonical_reconciled_ETH_5_session_usd_m: 10.0
OTA_supplied_ETH_7_session_usd_m: -4.4
canonical_reconciled_ETH_7_session_usd_m: -34.4
rolling_sum_authority: CANONICAL_DIRECT_RECONCILIATION
OTA_rolling_sums_accepted: false
```

The mismatch reflects incomplete or differently bounded source rows in the stale-generation OTA payload. The row-level 31 July total is retained; the derived rolling sums are quarantined.

The OTA statement that the 3 August ETF rows were not published is superseded for current framework use by the later direct-owner DATA PING evidence:

```yaml
latest_settled_ETF_session: 2026-08-03
BTC_ETF_2026_08_03_usd_m: 170.1
ETH_ETF_2026_08_03_usd_m: -11.9
current_ETF_authority: DATA_PING_DIRECT_OWNER
```

Therefore the current ETF interpretation is BTC absorption with negative ETH flow, not a publication gap.

The OTA's issuer-level observation that ETHB was the sole positive contributor on 31 July is retained as a structural micro-observation only. It does not affect rotation, entry or portfolio state.

## Source QA

```yaml
price_cache_guard: PASS_AS_SUPPLIED
H_SRC_01: FALSIFIED_UNCHANGED
H_SRC_02: TIME_OF_DAY_REJECTED_AS_OPERATIONAL_FRESHNESS_PREDICTOR_UNCHANGED
Farside_payload_generation: ONE_GENERATION_STALE
historical_row_use: ALLOWED_WITH_REASONING
current_session_use: REJECTED_SUPERSEDED_BY_DIRECT_OWNER
```

## Framework result

```yaml
market_cycle: EARLY_BULL_ATTEMPT_BTC_LED_EXTENDED_TRANSITION
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

The OTA strengthens experiment accountability but does not alter the active decision. H7 supplies a fifth failed post-maturity follow-through row, ETH/BTC remains below 0.0300, and current ETF evidence favors BTC over ETH. The latest Master Monday and Cycle Navigator #19 remain unchanged.

**Top-up og købsvindue:** Afvent mindst næste settled København-close og undlad nye top-ups, fordi H7 igen falder, ETH/BTC forbliver under 0,0300, den direkte 3/8 ETF-session favoriserer BTC frem for ETH, og den aktuelle v1.1-breadth stadig ikke er verificeret.