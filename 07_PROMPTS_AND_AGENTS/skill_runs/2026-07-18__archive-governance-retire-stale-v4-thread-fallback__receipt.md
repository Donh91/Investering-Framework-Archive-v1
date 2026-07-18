# Archive Governance Receipt: Retire Stale V4 Thread-Derived Fallback

**Date:** 2026-07-18  
**Status:** `PENDING_PR_MERGE_AND_MAIN_READBACK`  
**Authority:** source-routing safety only

## Finding

`02_DATA_PING/operational_handoffs/latest_thread_source_state.json` still reported `READY_THREAD_DERIVED` for DATA PING V4 even though V5 is active and the accepted-log/decision-context owners have advanced to `DATA_PING_V5_20260717T162231Z`.

The stale V4 artifact is older than its 36-hour new-row window and must not serve as live fallback after an accepted V5 owner exists.

## Repair

```yaml
active_canonical_version: 5
archived_thread_version: 4
V4_live_market_source: false
V4_new_forecast_rows: false
V4_new_prospective_rows: false
V4_canonical_state_update: false
superseding_owner: latest_accepted_log_state.json
```

The archived V4 payload and history are preserved. No market value is changed or reconstructed.

## Branch safety

```yaml
branch: agent/task-20260718-retire-stale-v4-thread-fallback
base_main_sha: 9bd1da86e61e296de76d9248777364a2cdbfd552
direct_main_write: NO
changed_paths: 2
file_deletions: 0
market_authority_change: NO
portfolio_action: NONE
```
