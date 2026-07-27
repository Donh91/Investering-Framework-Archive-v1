# H7 transmission-rate challenger — matured adjudication

```yaml
experiment_id: H7_TRANSMISSION_RATE_CHALLENGER
adjudicated_at_utc: 2026-07-27T05:39:20Z
maturity_basis: FIVE_SETTLED_CEST_ROWS
status: MATURED_SCORED
score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
score_ceiling_applied: YES
rotation_confirmation: NO
canonical_rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action: NONE
```

## Governing interpretation

The canonical Condition 1 is the settled direct ETH/BTC sequence test:

```text
C3 > C2
C4 > C3
C5 > C4
```

The alternative OLS wording is diagnostic only and has no scoring authority. The current outcome also happens to be positive under that diagnostic, but the score does not depend on it.

## Accepted rows

| CEST date | Direct ETH/BTC close | ETH minus BTC 1D | leader |
|---|---:|---:|---|
| 2026-07-22 | 0.02933 | +1.22 pp | ETH |
| 2026-07-23 | 0.02889 | -1.52 pp | BTC |
| 2026-07-24 | 0.02896 | +0.22 pp | ETH |
| 2026-07-25 | 0.02910 | +0.52 pp | ETH |
| 2026-07-26 | 0.02969 | +2.05 pp | ETH |

## Condition evaluation

### Condition 1 — three consecutive positive settled increments

```yaml
C3_gt_C2: 0.02896_gt_0.02889_PASS
C4_gt_C3: 0.02910_gt_0.02896_PASS
C5_gt_C4: 0.02969_gt_0.02910_PASS
longest_positive_increment_run: 3
result: MET
```

### Condition 2 — ETH leads in at least two of the final three rows

```yaml
2026_07_24: ETH
2026_07_25: ETH
2026_07_26: ETH
ETH_lead_count_last_three: 3
required: 2
result: MET
```

### Condition 3 — complete reproducible prospective rows

```yaml
prospective_rows: 5_of_5
source_pair: DIRECT_BINANCE_ETHBTC
session_basis: SETTLED_CEST
row_status: PROSPECTIVE_VALID
result: MET
receipt_hash_completion: FOLLOW_UP_NON_BLOCKING
```

The row-5 request parameters, source close and receipt IDs were supplied. Full response and row hashes were stated as generated but omitted from the transmitted text. They should be attached to the long-form receipt archive when available, but the deterministic pairwise adjudication is not blocked.

## Diagnostic only

```yaml
OLS_log_slope_per_session: 0.00316
OLS_approx_percent_per_session: 0.317
scoring_authority: NONE
```

## Counterevidence and confidence limits

The H7 label is intentionally capped because:

- the largest increment occurred in the Sunday session;
- the price move lacked supporting ETF-flow confirmation;
- the supplied AUM-normalised ETH outflow was worse than BTC's;
- the source's prior classification of the move as price-led rather than flow-led remains valid counterevidence;
- five observations do not establish a durable rotation regime.

## Relationship to other gates

```yaml
F4: CLOSED_GATE_UNMET_NOT_REOPENED
0_0300_future_test_basis: MUST_BE_PREREGISTERED_UTC_OR_CEST
0_0275_load_bearing_gate: HOLDS
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
```

## Source-QA defect treatment

The producing script's run-length helper contained a false-block bug. The current H7 adjudication bypasses that helper and uses explicit pairwise comparisons. Future automated H7 scoring remains blocked until the helper is patched and regression-tested.

## Final decision

```yaml
H7_final_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
mechanical_conditions: MET
interpretive_weight: LIMITED
state_effect: NONE
next_observation: FIRST_POST_SIGNAL_SETTLED_CEST_ROW
```
