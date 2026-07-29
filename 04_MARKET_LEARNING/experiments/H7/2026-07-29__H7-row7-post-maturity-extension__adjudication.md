# H7 row 7, post-maturity extension adjudication

```yaml
experiment_id: H7_TRANSMISSION_RATE_CHALLENGER
source_run: CLAUDE_OTA_2026_07_29T17_00_49Z
adjudicated_at_utc: 2026-07-29T20:58:00Z
canonical_maturity_already_reached: YES
original_maturity_basis: FIVE_SETTLED_CEST_ROWS
current_extension_row: 7
extension_status: ACCEPTED_POST_MATURITY_OBSERVATION
score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
score_change: NONE
rotation_confirmation: NO
canonical_rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action: NONE
```

## 1. Correction to the source maturity wording

H7 was already matured and scored after five settled CEST rows. Row 7 therefore does not newly mature H7. It extends the post-maturity observation path.

The immutable original adjudication remains authoritative for scoring:

```text
C3 > C2
C4 > C3
C5 > C4
```

The five-session OLS log slope is diagnostic only and has no scoring authority. Row 7 cannot retroactively alter the original score.

## 2. Accepted row 7

```yaml
CEST_date: 2026-07-28
settlement_close_utc: 2026-07-28T21:59:59.999Z
BTCUSDT_close: 63972.44
ETHUSDT_close: 1923.95
ETHBTC_close: 0.03007
BTC_1D_pct: -1.31
ETH_1D_pct: -0.92
ETH_minus_BTC_pp: 0.39
relative_leader: ETH
absolute_direction_BTC: DOWN
absolute_direction_ETH: DOWN
qualitative_classification: RELATIVE_OUTPERFORMANCE_BY_SMALLER_LOSS
```

The source supplied raw-row hashes, but the raw rows themselves were not uploaded to the main framework. Those hashes are preserved as source claims and not independently byte-validated.

The ETHBTC close of `0.03007` is independently consistent with the already validated DCR-20260729-EVENT-001 settlement evidence.

## 3. Extended diagnostics

```yaml
extended_log_diff_signs: "-+++++"
longest_positive_increment_run_after_row7: 5
five_session_OLS_log_slope_per_session: 0.01040
five_session_OLS_approx_pct_per_session: 1.046
previous_Claude_OLS_approx_pct_per_session: 0.974
scoring_authority: NONE
```

The positive slope does not distinguish:

- ETH rising faster than BTC;
- ETH falling less than BTC;
- a mixture of both states.

That limitation must accompany future slope-based output. Relative leadership is not equivalent to positive absolute market strength.

## 4. Condition treatment

```yaml
canonical_COND1: ALREADY_MET_AT_ORIGINAL_MATURITY_NO_RESCORE
extended_pairwise_path: CONTINUES_POSITIVE
Claude_alternative_COND1_reading: DIAGNOSTIC_ONLY
COND2_final_three_relative_leaders: ETH_3_OF_3
COND2_caveat: ROW7_IS_SMALLER_LOSS_NOT_GAIN
COND3_row7_source_completeness: ACCEPTED_WITH_SOURCE_HASHES_UNVERIFIED_BY_RAW_BYTES
```

## 5. Threshold relationship

Row 7 is also the first settled ETHBTC close at or above `0.0300`.

```yaml
first_settled_acceptance: YES
settled_close: 0.03007
settlement_basis_agreement: UTC_AND_CEST_AGREE_FOR_THIS_SESSION
persistence: FAILED_AFTER_SETTLEMENT
latest_valid_framework_sequence: FIRST_ACCEPTANCE_FAILED_PERSISTENCE
```

The first acceptance and failed persistence were already adjudicated through DCR-20260729-EVENT-001 and the subsequent direct DATA PING. This H7 extension corroborates that evidence but does not create a second policy event or receipt.

## 6. Evidence and state effect

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
portfolio_action: NONE
canonical_state_change: NONE
```

## 7. Next observation discipline

Rows after 2026-07-29T18:00:00Z may be exposed to the source-supplied FOMC confound. Preserve catalyst timing beside rows 8 and 9, but do not erase or down-weight row 7 retrospectively because its settlement preceded the cited event.
