# Skill-run receipt — DATA PING 0bc8 breadth relapse

```yaml
run_id: run_0bc8a5d0d0464542b29b4d50f2f8e19c
source_snapshot_utc: 2026-07-29T16:51:00.829Z
processed_at_utc: 2026-07-29T17:02:00Z
branch: agent/task-20260729-data-ping-0bc8-breadth-relapse
write_layer: BRANCH_FIRST
predecessor_run_id: run_49cf4c174e254c4ebabb6cf2042109ea
lineage_status: PASS
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_append: 1
shadow_dual_run_valid_runs: 5
source_recovery_observation: BINANCE_OWNER_RECOVERED
deep_capture_request_id: DCR-20260729-EVENT-002
deep_capture_status: PREPARED
canonical_state_change: NONE
portfolio_action: NONE
final_holdout_opened: NO
```

Validation required before completion:
- JSON parse for all machine artifacts;
- unchanged breadth membership hash verified;
- no duplicate A-class receipt;
- shadow ledger run count equals accumulation status;
- branch readback;
- PR and CI;
- merge and main readback.
