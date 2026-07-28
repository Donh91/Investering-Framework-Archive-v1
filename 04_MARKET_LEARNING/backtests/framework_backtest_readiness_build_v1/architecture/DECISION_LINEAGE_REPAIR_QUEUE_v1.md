# Decision Lineage Repair Queue v1

```yaml
ledger_rows: 3
A_FULLY_REPLAYABLE: 0
B_PARTIALLY_RECONSTRUCTABLE: 3
C_QUARANTINED: 0
actual_policy_replay_unlocked: NO
```

## Priority 1: FT-1

Recover the original pre-registration timestamp, exact policy text, final closeout timestamp, explicit action or no-action receipt, actual transaction-cost basis and settled outcome rows.

FT-1 is the best candidate for the first A-class row because its policy version, freeze date, expected confirmation cost and evaluation deadline are already documented.

## Priority 2: FNP-001

Recover the original frozen forecast, fixed label horizon, decision timestamp, rule version, no-trim receipt, owner prices and cost contract. The final retrospective summary is insufficient for actual-policy replay.

## Priority 3: TD-97

TD-97 remains a claim and shadow-forward-test row. Link its evaluation receipts, but do not force it into a portfolio-policy ledger because deployment, rebuy and rotation authority were explicitly none.

## Gate

```yaml
minimum_A_rows: 1
preferred_A_rows_per_policy_family: 5
temporal_contract: knowledge_at <= decision_at <= execution_at < label_end
cost_contract: FROZEN_BEFORE_SCORING
overlap_clusters: REQUIRED
```
