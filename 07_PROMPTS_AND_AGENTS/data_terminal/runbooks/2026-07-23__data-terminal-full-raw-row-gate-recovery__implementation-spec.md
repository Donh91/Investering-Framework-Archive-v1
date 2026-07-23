# Data Terminal Full Raw Row Gate Recovery

**Date:** 2026-07-23  
**Status:** APPROVED_BRANCH_EXECUTION_TASK  
**Classification:** SHADOW_ONLY  
**Repository:** `Donh91/Investering-Framework-Archive-v1`  
**Branch:** `agent/task-20260723-data-terminal-full-raw-row-gate-v2`  
**Source main SHA:** `c8fa47180889a4fe4e5b11b979f4acedc3cc26d3`

## Purpose

Restart the approved Data Terminal Phase 1 implementation from current `main` because the prior Codex result was reported locally but never appeared on the remote branch.

The complete functional contract remains the prior approved specification:

```text
branch: agent/task-20260721-data-terminal-full-raw-row-gate
path: 07_PROMPTS_AND_AGENTS/data_terminal/runbooks/2026-07-21__data-terminal-phase1-full-raw-row-preservation-and-cross-run-gate__implementation-spec.md
blob_sha: 6437264c3a13c119f17ccb214e65ffe0cd75a847
```

Read and implement that specification in full. Current repository authority overrides stale copied context only.

## Current authority

```yaml
active_data_ping_version: 6
latest_accepted_log_id: DATA_PING_V6_20260719T200033Z
v7_status: PREPARED_NOT_ACTIVE
phase1_completion: NO
```

## Required result

- exact FRED raw payload bytes preserved;
- complete deterministic NDJSON row spool including `UNKNOWN` rows;
- immutable-path conflict guard;
- verified row counts and hashes;
- deterministic two-spool comparator with all six required classifications;
- fixed-fixture, negative and replay regression tests;
- Data Terminal contracts, README and implementation receipt updated as required.

## Allowed implementation paths

```text
scripts/data_terminal/fred_csv_collector.py
scripts/data_terminal/compare_fred_row_spools.py
tests/data_terminal/test_fred_csv_collector.py
tests/data_terminal/test_fred_row_spool_comparator.py
tests/data_terminal/fixtures/fred_csv_macro_core_revised.csv
02_DATA_PING/data_terminal/contracts/data_terminal_contracts.schema.json
02_DATA_PING/data_terminal/README.md
07_PROMPTS_AND_AGENTS/data_terminal/implementation_receipts/2026-07-23__data-terminal-full-raw-row-gate-recovery__verification-receipt.md
```

Do not modify workflows, schedules, canonical indexes, registries, active DATA PING pointers, accepted payloads, framework state or portfolio state. Do not delete, move or rename files.

## Remote delivery requirement

Completion requires an actual commit pushed to this branch. Before reporting completion:

1. push all changes to GitHub;
2. read back the remote head SHA;
3. list the exact remote changed files;
4. verify each expected implementation file resolves remotely;
5. report exact tests and limitations;
6. stop before merge.

A local-only commit is not completion.

## Required final status

```text
PHASE1_COMPLETION: NO_PENDING_TWO_POST_UPGRADE_LIVE_RUNS
```
