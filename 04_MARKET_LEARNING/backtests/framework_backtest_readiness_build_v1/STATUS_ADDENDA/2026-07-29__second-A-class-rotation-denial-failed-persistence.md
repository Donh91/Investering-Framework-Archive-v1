# Second prospective A-class rotation event — failed persistence after first settled acceptance

```yaml
receipt_id: PDR-20260729-52aa8a0a9bf2
receipt_class: A_FULLY_REPLAYABLE
policy_family: ROTATION_PERMISSION
receipt_kind: DENIAL
event_id: ROTATION-2026-W31-ETHBTC-0030-FIRST-SETTLED-ACCEPTANCE-FAILED-PERSISTENCE-001
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_unique_overlap_cluster: NO
A_rows_total: 2
rotation_A_rows: 2
rotation_unique_overlap_clusters: 1
economic_ranking_ready: NO
actual_policy_replay_unlocked: NO
```

The validated owner row closed at 0.03007 on the Europe/Copenhagen daily boundary, the first settled close above 0.0300 in the active attempt. The post-settlement path immediately fell below the level and the new DATA PING showed 0.02982 live, negative 1h/4h/12h ETHBTC returns and breadth of 37.08%, below the 50% and 55% gates.

The receipt does not retroactively claim a decision at the settlement timestamp. It freezes the main framework's current no-action denial after the deep-capture package was received and validated. Temporal order, source IDs, source hashes, owner authority, no-trade cost contract, label horizon and overlap cluster are preserved.

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
final_holdout_opened: NO
```
