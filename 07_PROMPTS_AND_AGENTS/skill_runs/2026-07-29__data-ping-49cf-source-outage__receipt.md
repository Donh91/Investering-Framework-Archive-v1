# Skill-run receipt — DATA PING 49cf source-outage ingest

```yaml
run_id: run_49cf4c174e254c4ebabb6cf2042109ea
source_snapshot_utc: 2026-07-29T09:18:00Z
processed_at_utc: 2026-07-29T10:15:00Z
branch: agent/task-20260729-data-ping-49cf-source-outage
write_layer: BRANCH_FIRST
predecessor_run_id: run_b5988607a8f349558a19f78198fdfde2
Binance_owner_status: UNAVAILABLE_GEO_RESTRICTION
direct_ETHBTC_gate: UNKNOWN
breadth_advance_ratio: 0.4157303371
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_valid_increment: 0
deep_capture_request_created: NO
conditional_deep_capture_watch: ACTIVE
canonical_state_change: NONE
portfolio_action: NONE
final_holdout_opened: NO
```

Validation requirements:
- JSON parse for machine artifacts;
- no unexpected deletions;
- direct/derived authority separation preserved;
- no duplicate A-class row;
- CI, merge and main readback before completion.
