# H7 row 8 post-maturity extension adjudication

```yaml
experiment_id: H7_TRANSMISSION_RATE_CHALLENGER
source_run: CLAUDE_OTA_2026_07_30T19_04_13Z
adjudicated_at_utc: 2026-07-30T19:32:22Z
canonical_maturity_already_reached: YES
original_maturity_basis: FIVE_SETTLED_CEST_ROWS
current_extension_row: 8
extension_status: ACCEPTED_POST_MATURITY_OBSERVATION
extension_follow_through: WEAKENED
canonical_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
score_change: NONE
rotation_confirmation: NO
canonical_rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action_change: NONE
```

## 1. Condition 1 is not ambiguous

The canonical operational wording was frozen before original row 5 maturity. Condition 1 is the fixed historical test:

```text
C3 > C2
C4 > C3
C5 > C4
```

It passed at original maturity. Row 8 cannot make that historical result pass or fail again.

```yaml
canonical_COND1: ALREADY_MET_AT_ORIGINAL_MATURITY_NO_RESCORE
source_exists_anywhere_reading: NOT_APPLICABLE_TO_CANONICAL_SCORE
source_latest_three_reading: POST_MATURITY_DIAGNOSTIC_ONLY
```

The correct distinction is:

- original experiment score: unchanged;
- post-maturity follow-through: weakened.

## 2. Accepted row 8

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
absolute_direction_BTC: DOWN
absolute_direction_ETH: DOWN
qualitative_classification: BTC_LED_BY_SMALLER_LOSS_ETH_UNDERPERFORMED
```

Source-supplied raw-row hashes are retained but not independently byte-validated because the raw rows were not transmitted.

## 3. Extended diagnostics

```yaml
extended_log_diff_signs: "-+++++-"
latest_increment_sign: NEGATIVE
positive_run_before_row8: 5
rolling_5_session_OLS_log_slope_per_session: 0.00556
rolling_5_session_OLS_approx_pct_per_session: 0.557
previous_rolling_5_session_OLS_approx_pct_per_session: 1.046
slope_change: APPROX_HALVED
scoring_authority: NONE
```

The rolling slope remains positive because it still contains prior positive increments. It does not override the latest reversal or imply durable altcoin strength.

## 4. Threshold relationship

```yaml
2026_07_28_settled_ETHBTC_close: 0.03007
2026_07_29_settled_ETHBTC_close: 0.02986
2026_07_30_in_progress_high_as_of_retrieval: 0.02996
threshold: 0.0300
sequence: SINGLE_SESSION_ACCEPTANCE_THEN_REJECTION
persistence: FAILED
```

The source's H7 row uses the CEST close `0.02973`, while the threshold table uses the UTC daily close `0.02986`. Both are valid for their stated settlement conventions. They must not be mixed without labeling.

## 5. Confound treatment

Row 8 settled after the source-supplied FOMC timestamp. It is retained with:

```yaml
confound: POST_FOMC_ACTIVE
causal_attribution: NOT_CLAIMED
row_exclusion: NO
```

## 6. State effect

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
new_shadow_dual_run: NO
H7_score_change: NONE
F4_score_change: NONE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action_change: NONE
```

The row is useful because it shows that early transmission did not immediately become persistent rotation. It weakens near-term altcoin follow-through without erasing the historical H7 candidate result.
