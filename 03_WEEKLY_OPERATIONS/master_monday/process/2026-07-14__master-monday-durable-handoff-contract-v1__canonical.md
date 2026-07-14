# Master Monday Durable Handoff Contract v1

**Dato:** 2026-07-14  
**Status:** CANONICAL  
**Område:** Weekly Operations / Master Monday durability / pointer integrity  
**Primary folder:** `03_WEEKLY_OPERATIONS/master_monday/process/`  
**Related folders:** `03_WEEKLY_OPERATIONS/master_monday/`, `03_WEEKLY_OPERATIONS/forecast_ledger/`, `05_CYCLE_NAVIGATOR/`, `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Depends on:** `03_WEEKLY_OPERATIONS/master_monday/process/2026-07-06__master-monday-archive-version-chain-protocol__canonical.md`, `AGENTS.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md`

## 1. Purpose

This contract closes the gap between a Master Monday automation run and a durable, machine-readable GitHub handoff.

A generated report is not considered durable merely because an automation executed or displayed a result. Durability requires a complete write, read-back, merge and pointer chain.

## 2. Binding state chain

```text
DIRECT_PROJECT_THREAD / ACCEPTED_LOG_RECEIPT / THREAD_DERIVED_HANDOFF / SOURCE_UNAVAILABLE
→ GENERATED_RUN
→ TASK_BRANCH_WRITES
→ BRANCH_READBACK_PASS
→ RUN_RECEIPT_STAGED
→ POINTERS_STAGED
→ PULL_REQUEST
→ MERGE
→ MAIN_READBACK_PASS
→ DURABLE_GITHUB_ARTIFACT
```

No later stage may be claimed when an earlier stage failed.

## 3. Required weekly artifacts

For week `YYYY-W##`, a successful combined run must preserve:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/01_system_generated_pre_data_ping.md
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/02_data_ping_derived_raw.md        # when applicable
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/03_framework_ratified_final.md
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/04_cycle_navigator_handoff_notes.md
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/run_receipt.json
```

The official weekly forecast must remain under the current Forecast Ledger owner and be referenced by exact path and forecast IDs from `run_receipt.json`.

A stage that does not apply must be recorded as `NOT_APPLICABLE`; it must not be silently omitted.

## 4. Transaction order

1. Resolve current authority through `AGENTS.md`, the canonical index, registered addenda and current owners.
2. Freeze one `run_id`, ISO week, source-resolution mode, source timestamp and source hash.
3. Generate Master Monday, Cycle Navigator handoff and forecast lineage from the same frozen state.
4. Create and verify an isolated `agent/task-*` branch.
5. Write all dated artifacts to that branch.
6. Read back every written artifact and record its blob SHA.
7. Write `run_receipt.json` only after the dated artifacts pass branch read-back.
8. Stage current pointers only after the receipt itself passes branch read-back.
9. Open and validate a pull request. No direct default-branch write is permitted.
10. Merge only when the diff contains the intended files and no deletion or lineage drift.
11. Re-read every merged artifact and pointer from `main`.
12. Mark the run `DURABLE_PASS` only after main-branch read-back and pointer-target verification.

## 5. Pointer contract

Current pointer:

```text
03_WEEKLY_OPERATIONS/master_monday/latest_master_monday.json
```

The pointer must contain at least:

```text
schema_version
pointer_status
latest_durable_week
latest_durable_stage
latest_durable_path
latest_durable_source_commit_sha
latest_durable_blob_sha
run_receipt_path
framework_ratified_final_available
forecast_lineage_status
cycle_navigator_handoff_status
previous_valid_pointer
observed_at_utc
```

Pointer rules:

- The pointer may advance only to a path that exists and passed read-back.
- A `DATA_PING_DERIVED` file may be the latest durable artifact but must not be presented as a ratified final.
- A failed new run preserves the prior valid pointer.
- A missing ratified final preserves `forecast_lineage_status=INCOMPLETE` and scoring remains blocked.
- The pointer never upgrades authority. It reports the authority already held by the target file.
- Same-week revisions must preserve prior files and use the version-chain protocol.

## 6. Run receipt contract

Schema owner:

```text
03_WEEKLY_OPERATIONS/master_monday/process/master_monday_run_receipt.schema.json
```

The receipt must distinguish:

```text
generation_status
branch_write_status
branch_readback_status
pull_request_status
merge_status
main_readback_status
pointer_update_status
standalone_delivery_status
overall_durability_status
```

Required final classifications:

```text
DURABLE_PASS
PARTIAL_REPORT_DELIVERED_POINTER_PRESERVED
FAIL_GENERATION
FAIL_WRITE
FAIL_READBACK
FAIL_MERGE
SOURCE_UNAVAILABLE
```

## 7. Failure behavior

When generation succeeds but archiving fails:

- deliver the generated report visibly;
- set archive status to `PARTIAL` or `FAIL`;
- preserve the previous pointer;
- write no false success receipt;
- record the exact failed stage and paths;
- do not claim forecast durability or scoring eligibility.

When source resolution fails:

- do not fetch substitute market data;
- preserve `DATA_MISSING=UNKNOWN`;
- create no retrospective forecast row;
- delivery may report the blocked state, but the pointer remains unchanged.

## 8. Historical gap treatment

An observed automation execution without a readable durable report is classified:

```text
RUN_OBSERVED_NOT_DURABLY_AVAILABLE
```

It may receive a gap receipt, but it may not be reconstructed, ratified or scored from memory.

## 9. Validation and monitoring

The active Master Monday automation must enforce this contract on every run.

The Integrity Canary and GitHub Archive Sync must verify:

- pointer path exists;
- pointer target exists;
- receipt path exists when declared;
- target blob SHA matches the pointer;
- ratified-final and forecast-lineage statuses agree;
- a failed run did not replace the prior pointer;
- no automation claims durability without main read-back.

## 10. Authority boundary

This contract changes archive durability only. It creates no market call, forecast value, portfolio action, scoring result, rule promotion, threshold change or new framework engine.
