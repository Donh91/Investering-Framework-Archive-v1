# Claude OTA Framework Reconciliation

## Authority

```yaml
operating_mode: STANDALONE_OTA_NO_REFERENCE_BRIDGE
canonical_authority: NONE
portfolio_authority: NONE
accepted_use: SHADOW_EXPERIMENT_EVIDENCE_SOURCE_QA_AND_PROVISIONAL_ETF_RESEARCH
```

## H7 row 12 adjudication

The source wording `fourth maturity` is corrected. H7 matured once under the preregistered rule. Row 12 is the **fourth consecutive post-maturity extension**, following rows 9–11, and does not reopen or rescore the historical experiment.

```yaml
historical_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
historical_score_change: NONE
latest_formed_extension_row: 12
post_maturity_extension_number: 4
row_12_leader: ETH
COND2_last_3: 1_OF_3_NOT_MET
rolling_5_session_slope_pct_per_session: -0.091
prior_slope_pct_per_session: -0.517
slope_direction: FIRST_IMPROVEMENT_AFTER_FOUR_DECLINES
post_maturity_follow_through: INACTIVE_CONFIRMED_WITH_ONE_SESSION_RECOVERY
formal_lapse_rule: UNDEFINED_NOT_INVENTED
formal_retrigger_rule: UNDEFINED_NOT_INVENTED
```

The concurrent DATA PING independently reports the same settled Copenhagen closes: BTC 63,578.00, ETH 1,890.43 and ETHBTC 0.02973. H7 row 12 therefore passes value-level crosscheck. ETH led one session and the slope improved, but COND2 remains below its 2-of-3 requirement and ETHBTC remains below 0.0300.

The endpoint change from 0.02933 to 0.02973 is approximately +1.36%. It is retained as a derived arc feature, not as a new policy signal.

## ETHBTC threshold sequence

The source phrase `six sessions without touch` is normalized as:

```yaml
settled_sessions_without_0_0300_touch_since_last_touch: 5
additional_in_progress_session_without_0_0300_touch: 1
total_observed_sessions_without_touch_including_in_progress: 6
latest_settled_UTC_close_supplied: 0.02965
latest_settled_Copenhagen_close_crosschecked: 0.02973
current_direct_ETHBTC_at_DATA_PING: 0.02960
settled_status: SEQUENCE_TERMINATED_SUSTAINED
```

UTC and Copenhagen sessions are kept separate. The in-progress 3 August session has no settled threshold authority.

## F1 and H-WIN-01

F1 remains final `NOT_FAILED`. The 2 August UTC close was well above both threshold candidates, and no new boundary stress occurred. H-WIN-01 remains `UNPROVEN / LOW_MODERATE` with no confidence change.

## BTC ETF evidence

The reported 30 and 31 July rows are accepted only as **provisional historical ETF research evidence**:

```yaml
2026-07-30_total_usd_m: 233.1
2026-07-31_total_usd_m: -265.4
two_session_swing_usd_m: 498.5
seven_session_sum_usd_m: -526.5
source_generation_status: ONE_GENERATION_STALE
fresh_generation_corroboration: MISSING
framework_ledger_overwrite: FORBIDDEN_PENDING_REVERIFICATION
```

The terminal date of 31 July is structurally plausible because 1–2 August were weekend days, but payload-generation staleness prevents promotion to the current reconciled ETF ledger. The issuer breadth, GBTC -52.6 observation and rolling sums remain quarantined as provisional until reverified.

## H-SRC-02

The fifth observation weakens the time-of-day hypothesis further. A similar morning retrieval produced fresh content on one date and stale content on another. The accepted operational conclusion is narrower than statistical falsification:

```yaml
time_of_day_as_freshness_gate: NOT_SUPPORTED_FOR_OPERATIONAL_USE
required_gate: FOOTER_DATE_AND_LATEST_SESSION_VALIDATION_EACH_RUN
further_scheduled_time_hypothesis_testing_required: NO
```

## Effect on current framework state

The OTA cannot override the concurrent DATA PING. The DATA PING's 24.4% breadth, rising OI, elevated long positioning and BTC funding dominate the one-session H7 improvement.

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
new_policy_event: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_valid_runs: 5
```

Open items remain: fresh BTC ETF 31 July verification; ETH ETF 31 July and next published session; H7 lapse/retire/retrigger rule; breadth membership hash and constituent sidecar; and execution of DCR-20260730-EVENT-003-EXT-95C5.