# Data Terminal Phase 1 Full Raw Row Preservation and Cross-Run Gate - Codex Implementation Specification

**Date:** 2026-07-21  
**Status:** APPROVED_BRANCH_EXECUTION_TASK  
**Classification:** SHADOW_ONLY  
**Repository:** `Donh91/Investering-Framework-Archive-v1`  
**Branch:** `agent/task-20260721-data-terminal-full-raw-row-gate`  
**Source main SHA:** `86466f142fd59a8e8dd0e26e38c5b5b6846768de`  
**Authority boundary:** collection, immutable raw evidence, row persistence, source-QA and deterministic replay only; no market, DATA PING acceptance, framework-state or portfolio authority  
**Depends on:** existing Data Terminal owner, collector, replay verifier, PR #105 bounded materialization diagnostic and the standing Phase 1 mandate

## 1. Mission

Close the implementation gap exposed by the second live bounded diagnostic:

1. preserve the complete authoritative FRED CSV response bytes for every future collector run;
2. persist every source row in an authoritative deterministic NDJSON row spool;
3. make missing rows explicit as `UNKNOWN`, never zero;
4. provide a deterministic comparator for two post-upgrade live row spools;
5. produce a complete row-level revision ledger without overwriting either source run;
6. keep the existing manual workflow unchanged and schedule-free.

This is a persistence and source-QA change. It must not create a signal engine, score, market state, gate, permission, forecast, portfolio action or active DATA PING schema redesign.

## 2. Verified current context

```yaml
run_id: DT_PHASE1_FULL_RAW_ROW_GATE_20260721_01
active_data_ping_version: 6
latest_accepted_log_id: DATA_PING_V6_20260719T200033Z
v7_status: PREPARED_NOT_ACTIVE
first_live_terminal_run_id: DT_FRED_20260721T115849Z_b080365d0c23
first_live_artifact_sha256: ac3e2ad49f265b1cd9ae8b16d97051b875d90974ad7199cd7105143a9bd7cd89
bounded_second_capture_run_id: DT_FRED_WEB_BOUNDED_20260721T172619Z_e053de3a2119
bounded_package_sha256: 775c82da645244ba983af219f4e126f526eb229243dc4de49d8dd5e38ae591a8
phase1_completion: NO
blocking_reason: TWO_POST_UPGRADE_COMPLETE_LIVE_ROW_SPOOLS_REQUIRED_FOR_FULL_CROSS_RUN_PARITY
workflow_change_required: false
canonical_index_change: false
schedule_enabled: false
vault_access: none
framework_state_change: false
portfolio_action: none
```

The pre-upgrade live artifact does not contain complete historical non-missing rows or raw CSV bytes. Therefore it cannot serve as one side of a complete row-level historical comparison. After this implementation is merged, Phase 1 requires **two fresh post-upgrade live runs** before final cross-run parity can be evaluated.

## 3. Mandatory read order before implementation

Read in this exact order:

```text
AGENTS.md
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/archive-governance/SKILL.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
02_DATA_PING/version_governance/2026-07-19__data-ping-v6-raw-collector-contract-v1__canonical.md
02_DATA_PING/data_terminal/README.md
02_DATA_PING/data_terminal/contracts/data_terminal_contracts.schema.json
scripts/data_terminal/fred_csv_collector.py
scripts/data_terminal/verify_archived_run.py
tests/data_terminal/test_fred_csv_collector.py
.github/workflows/data-terminal-shadow-manual.yml
02_DATA_PING/data_terminal/validation/phase1_row_gate_report.json
02_DATA_PING/data_terminal/runtime/shadow/artifacts/2026-07-21/second-live-bounded/phase1_closeout_candidate.json
```

Then read directly referenced current paths where needed. Repository sources override this specification if authority has changed.

## 4. Branch and write safety

All writes must target only:

```text
agent/task-20260721-data-terminal-full-raw-row-gate
```

Before every write verify:

```yaml
target_branch_explicitly_supplied: YES
target_branch_verified_to_exist: YES
target_branch_is_default_branch: NO
target_branch_is_backup_branch: NO
write_path_and_operation_declared: YES
```

Rules:

- no direct write to `main`;
- no merge or auto-merge;
- no force push;
- no deletion, move or rename;
- no placeholder or connector-probe files;
- no canonical index or addendum-registry change;
- no active DATA PING pointer or accepted payload change;
- no workflow file change;
- no schedule or cron;
- no Vault access;
- no secrets, tokens, personal data or premium dependencies;
- read back every changed file;
- stop on `WRITE_BRANCH_UNVERIFIED`.

## 5. Existing owner and allowed implementation paths

The existing owner is `02_DATA_PING/data_terminal/`. Update it; do not create a parallel owner.

Preferred bounded paths:

```text
scripts/data_terminal/fred_csv_collector.py
scripts/data_terminal/compare_fred_row_spools.py

tests/data_terminal/test_fred_csv_collector.py
tests/data_terminal/test_fred_row_spool_comparator.py
tests/data_terminal/fixtures/fred_csv_macro_core_revised.csv

02_DATA_PING/data_terminal/contracts/data_terminal_contracts.schema.json
02_DATA_PING/data_terminal/README.md
07_PROMPTS_AND_AGENTS/data_terminal/implementation_receipts/2026-07-21__data-terminal-full-raw-row-preservation-and-cross-run-gate__verification-receipt.md
```

The exact final set may be smaller. Do not exceed these owners without explicit, evidenced necessity. `.github/workflows/data-terminal-shadow-manual.yml` must remain byte-identical.

## 6. Collector output extension

### 6.1 Raw payload preservation

For every successful fixture or network run, preserve the exact payload bytes at:

```text
raw/<run_id>__fred.csv
```

Requirements:

- bytes must be identical to the payload used for parsing;
- raw file SHA-256 must equal the existing payload SHA-256;
- file name must derive from the deterministic run ID;
- no normalization, newline conversion or re-encoding before write;
- no raw response content printed to stdout;
- no overwrite of an existing immutable raw path with different bytes.

### 6.2 Authoritative row spool

Write all CSV data rows, including missing rows, to:

```text
row_spools/<run_id>__rows.ndjson
```

Each NDJSON line must be canonical JSON and contain at minimum:

```yaml
row_schema: DATA_TERMINAL_FRED_SOURCE_ROW
row_schema_version: "0.1"
run_id:
source_id: FRED_CSV_MACRO_CORE
series: DGS10
row_number:
source_date: YYYY-MM-DD
source_timestamp: YYYY-MM-DDT00:00:00Z
retrieval_timestamp:
raw_value:
value: number | null
status: OBSERVED | UNKNOWN
direct_or_derived: DIRECT
source_convention: FRED_REPORTED_DAILY_OBSERVATION
payload_sha256:
authority:
  binding: false
  canonical_acceptance: false
  state_change: false
  portfolio_action: false
```

Rules:

- retain source row order;
- one CSV data row equals exactly one NDJSON line;
- missing values use `value: null`, `status: UNKNOWN`;
- missing values are never omitted from the spool;
- missing values are never converted to zero;
- `raw_value` preserves the trimmed source token, including `.` where applicable;
- duplicate source dates are rejected as `SCHEMA_DRIFT`;
- row count is an integer verified from iteration of the complete parsed collection;
- no derived market interpretation is permitted.

### 6.3 Receipt and source-health additions

Add deterministic metadata without removing existing fields:

```yaml
raw_payload_path:
raw_payload_size_bytes:
raw_payload_sha256:
row_spool_path:
row_spool_size_bytes:
row_spool_sha256:
returned_row_count:
returned_row_count_verified: true
observed_row_count:
unknown_row_count:
row_schema_version: "0.1"
```

Required invariants:

```text
returned_row_count = observed_row_count + unknown_row_count
raw_payload_sha256 = payload_sha256
receipt_sha256 recomputes over the complete receipt material
```

### 6.4 Snapshot and handoff behavior

Keep snapshots and handoff candidates compact. They may continue to expose the latest direct observation and explicit missing list, but their `artifacts` or source-lineage blocks must reference the immutable raw payload and row spool.

Do not turn the full row spool into the DATA PING handoff payload. DATA PING may ingest verified fields by reference; Data Terminal owns persistence.

### 6.5 Immutable write behavior

Immutable paths are:

```text
raw/<run_id>__fred.csv
row_spools/<run_id>__rows.ndjson
receipts/<run_id>__receipt.json
snapshots/<run_id>__snapshot.json
```

If an immutable path exists:

- identical bytes may be accepted as deterministic idempotence;
- different bytes must fail explicitly with `IMMUTABLE_PATH_CONFLICT`;
- no previous artifact may be silently overwritten.

`latest_terminal_state.json` and `latest_data_ping_handoff.json` remain sanitized temporary output pointers inside the workflow artifact only. Do not write repository pointers.

## 7. Deterministic cross-run comparator

Create:

```text
scripts/data_terminal/compare_fred_row_spools.py
```

The comparator accepts two authoritative NDJSON row spools and emits one deterministic JSON summary plus an NDJSON revision ledger.

Required classifications:

```text
UNCHANGED
NEW
REVISED
MISSING_STILL_UNKNOWN
MISSING_RESOLVED
REMOVED_OR_SOURCE_CONFLICT
```

Classification rules by `source_date`:

- observed in both with equal numeric value -> `UNCHANGED`;
- absent in baseline and present in candidate -> `NEW`;
- observed in both with unequal numeric value -> `REVISED`;
- unknown in both -> `MISSING_STILL_UNKNOWN`;
- unknown in baseline and observed in candidate -> `MISSING_RESOLVED`;
- present in baseline but absent in candidate, or observed becoming unknown -> `REMOVED_OR_SOURCE_CONFLICT`.

Comparator requirements:

- reject mismatched source ID or series;
- reject duplicate dates;
- reject malformed JSON or non-canonical row semantics;
- validate authority flags remain false;
- validate each spool has one consistent run ID and payload hash;
- sort ledger deterministically by source date;
- include baseline/candidate run IDs and hashes;
- include integer counts for every classification;
- produce no market interpretation, score or recommendation;
- never alter either input spool.

Suggested CLI:

```text
python scripts/data_terminal/compare_fred_row_spools.py \
  --baseline <baseline.ndjson> \
  --candidate <candidate.ndjson> \
  --summary-output <summary.json> \
  --ledger-output <revision_ledger.ndjson>
```

## 8. Required deterministic tests

All tests must be standard-library-only and network-independent.

### Collector tests

Add tests for:

- exact raw payload byte preservation;
- raw payload hash equals source payload hash;
- full row spool count including missing rows;
- `returned_row_count_verified` is true;
- observed plus unknown equals total;
- missing row uses null/`UNKNOWN`, never zero;
- deterministic NDJSON ordering and hash;
- receipt hash includes new metadata;
- raw and row-spool artifact references resolve;
- duplicate source date rejection;
- immutable path identical replay accepted;
- immutable path different-content conflict rejected;
- CLI writes the expected expanded artifact set;
- no secret-like fields or source payload printed to stdout;
- existing shadow authority remains all false.

### Comparator tests

Use fixed fixtures to cover every classification:

- unchanged observed row;
- new row;
- revised row;
- missing still unknown;
- missing resolved;
- removed/source conflict;
- duplicate date rejection;
- source/series mismatch rejection;
- malformed row rejection;
- deterministic repeat output;
- input spools remain byte-identical after comparison.

### Regression tests

Verify:

- existing five top-level JSON artifacts remain present;
- existing replay verifier tests still pass;
- first archived live artifact remains reproducible;
- `.github/workflows/data-terminal-shadow-manual.yml` is unchanged, dispatch-only, read-only and schedule-free;
- no canonical pointer or framework owner is touched.

## 9. Workflow boundary

Do **not** modify `.github/workflows/data-terminal-shadow-manual.yml`.

The current workflow already:

- runs all `tests/data_terminal/test_*.py` tests;
- invokes the collector with `--output-dir data-terminal-output`;
- uploads the complete output directory.

The expanded collector output will therefore be included automatically. A workflow modification would be high-impact and is outside this task because Vault/safepoint actions are explicitly excluded.

## 10. Two-run closeout protocol after merge

Do not execute live network runs inside this implementation PR.

After merge, two separate manual `mode: live` workflow runs are required:

```yaml
post_upgrade_live_run_1:
  role: AUTHORITATIVE_ROW_SPOOL_BASELINE
post_upgrade_live_run_2:
  role: AUTHORITATIVE_ROW_SPOOL_CANDIDATE
```

The final Phase 1 closeout gate may run only after both artifacts are independently verified and archived. The old pre-upgrade live run remains valid historical evidence but is not eligible as a complete row-spool baseline.

## 11. Hard exclusions

Do not implement:

- workflow changes;
- schedules or cron;
- automated workflow dispatch;
- new data sources;
- paid API, API key, card or free-trial dependency;
- Custom GPT, gateway or public snapshot repository;
- active DATA PING schema redesign;
- canonical index or addendum changes;
- accepted DATA PING pointer changes;
- framework interpretation, market state, gate, signal or score;
- portfolio action;
- Vault access;
- destructive cleanup or history rewriting.

## 12. Required validation commands

Run and report exact output for the strongest available equivalents of:

```text
python -m unittest discover -s tests/data_terminal -p 'test_*.py'
python -m py_compile scripts/data_terminal/fred_csv_collector.py scripts/data_terminal/compare_fred_row_spools.py tests/data_terminal/test_fred_csv_collector.py tests/data_terminal/test_fred_row_spool_comparator.py
python scripts/data_terminal/fred_csv_collector.py --fixture tests/data_terminal/fixtures/fred_csv_macro_core.csv --retrieval-timestamp 2026-07-19T12:00:00Z --output-dir <temp-dir>
python scripts/data_terminal/compare_fred_row_spools.py --baseline <fixture-spool-a> --candidate <fixture-spool-b> --summary-output <temp-summary> --ledger-output <temp-ledger>
```

Also verify:

- exact changed-file list;
- zero deletions;
- branch readback;
- no workflow diff;
- no schedule or cron;
- no active pointer, accepted payload, registry or canonical-index diff;
- no secret-like content;
- no generated artifact committed unless it is the implementation receipt.

## 13. Definition of done

```yaml
raw_payload_preservation: PASS
complete_row_spool: PASS
returned_row_count_verified: PASS
missing_unknown_not_zero: PASS
immutable_path_guard: PASS
cross_run_comparator: PASS
all_six_classifications_tested: PASS
existing_replay_tests: PASS
unit_tests: PASS
negative_tests: PASS
compile: PASS
workflow_changed: false
schedule_enabled: false
new_source_added: false
canonical_index_changed: false
active_data_ping_pointer_changed: false
active_data_ping_schema_changed: false
framework_state_changed: false
portfolio_action: none
vault_access: none
branch_readback: PASS
unintended_files_changed: 0
draft_pr: OPEN_NOT_MERGED
phase1_completion: NO_PENDING_TWO_POST_UPGRADE_LIVE_RUNS
```

## 14. Completion report

Update the draft PR with:

- exact branch and head SHA;
- exact changed paths;
- implementation decisions;
- artifact layout after the change;
- test commands and outputs;
- row-count and hash invariants;
- comparator classification test coverage;
- branch readback and exact-diff validation;
- blockers and limitations;
- explicit confirmation that the workflow was unchanged;
- explicit confirmation of no schedule, new source, canonical change, Vault access, framework-state change or portfolio action;
- the required next human gate: merge review only.

Stop before merge.