# H7 row 9 post-maturity follow-through adjudication

```yaml
experiment_id: H7_TRANSMISSION_RATE_CHALLENGER
source_run: CLAUDE_OTA_2026_07_31T16_43_14Z
adjudicated_at_utc: 2026-07-31T18:55:00Z
canonical_maturity_already_reached: YES
original_maturity_basis: FIVE_SETTLED_CEST_ROWS
current_extension_row: 9
extension_status: ACCEPTED_POST_MATURITY_OBSERVATION
canonical_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
canonical_score_change: NONE
post_maturity_follow_through: INACTIVE
retired_or_lapsed_rule_created: NO
rotation_confirmation: NO
canonical_rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action_change: NONE
```

## 1. Original score remains frozen

H7 matured and was scored after five settled CEST rows. The frozen historical Condition 1 remains:

```text
C3 > C2
C4 > C3
C5 > C4
```

That historical condition passed at original maturity and cannot be rescored by row 9. The source's alternative readings of Condition 1 are therefore not applicable to the canonical score.

## 2. Row 9 accepted as extension evidence

```yaml
CEST_date: 2026-07-30
BTCUSDT_close: 64735.53
ETHUSDT_close: 1918.67
ETHBTC_close: 0.02965
BTC_1D_pct: 1.37
ETH_1D_pct: 1.07
ETH_minus_BTC_pp: -0.30
relative_leader: BTC
```

## 3. Post-maturity transmission is no longer active

```yaml
COND2_last_3_ETH_lead_count: 1
COND2_requirement: AT_LEAST_2
COND2_post_maturity_status: NOT_MET
rolling_5_session_OLS_approx_pct_per_session: -0.101
previous_rolling_5_session_OLS_approx_pct_per_session: 0.557
slope_sign: NEGATIVE
post_maturity_joint_conditions: NOT_SATISFIED
```

The outcome is invariant to the source's Condition 1 wording question because Condition 2 fails unambiguously. This does not erase the original candidate result; it means the candidate did not persist into durable follow-through.

## 4. No invented lapse rule

The original experiment contract defines how the candidate was scored at maturity, not a permanent live-state machine. The framework therefore records:

```yaml
historical_experiment_result: PRESERVED
current_post_maturity_diagnostic: INACTIVE
formal_lapse_rule: UNDEFINED
retirement_status: NOT_ASSIGNED
retrigger_rule: UNDEFINED
```

A future governance revision may define live activation, lapse and retrigger semantics prospectively. No retrospective rule is introduced here.

## 5. Threshold relationship

```yaml
2026_07_28_UTC_settled_close: 0.03007
2026_07_29_UTC_settled_close: 0.02986
2026_07_30_UTC_settled_close: 0.02962
2026_07_30_UTC_high: 0.02996
threshold: 0.0300
sequence: SEQUENCE_TERMINATED
settled_persistence: FAILED
```

The H7 CEST close and UTC threshold close use different settlement conventions and remain separately labeled.

## 6. Confound and state effect

Rows 8 and 9 remain post-FOMC confounded. They are retained without causal attribution.

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
new_shadow_dual_run: NO
H7_score_change: NONE
F1_score_change: NONE
F4_score_change: NONE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action_change: NONE
```

The correct combined reading is: H7 historically identified an early transmission candidate, but that candidate did not develop into sustained rotation and is currently inactive as a post-maturity diagnostic.
