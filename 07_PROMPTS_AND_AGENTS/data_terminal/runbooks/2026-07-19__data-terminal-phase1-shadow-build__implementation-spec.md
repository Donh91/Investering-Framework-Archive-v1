# Data Terminal Phase 1 Shadow Build - Codex Implementation Specification

**Date:** 2026-07-19  
**Status:** APPROVED_BRANCH_EXECUTION_TASK  
**Classification:** SHADOW_ONLY  
**Repository:** `Donh91/Investering-Framework-Archive-v1`  
**Branch:** `agent/data-terminal-phase1-shadow-20260719`  
**Authority boundary:** no market authority, no DATA PING acceptance authority, no framework-state authority and no portfolio authority  
**Depends on:** activation kit v0.3 and `07_PHASE1_SHADOW_BUILD_SPEC.yaml`

## 1. Mission

Implement the smallest reviewable vertical slice of a shadow-only Data Terminal source, persistence, source-QA and replay subsystem.

This is infrastructure and evidence-lineage work. It is not a new signal engine, score, market state, shadow market layer or portfolio-action system.

## 2. Verified preflight context

```yaml
run_id: DT_PHASE1_20260719_ACTIVATION_01
preflight_status: PASS_WITH_WORKFLOW_COLLISION_GUARD
repository_access: PASS
activation_package_checksums: PASS_45_OF_45
active_data_ping_version: 5
latest_accepted_log_id: DATA_PING_V5_20260717T162231Z
v6_status: PREPARED_NOT_ACTIVE
new_engine_freeze_compatibility: PASS_SOURCE_LINEAGE_MISSING_DATA_REPRODUCIBILITY
existing_data_terminal_owner: NOT_FOUND
canonical_index_change: FORBIDDEN
schedule_enabled: false
custom_gpt_created: false
active_framework_state_changed: false
portfolio_action: none
```

Resolved live pointers:

```text
02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
```

Resolved active targets include:

```text
02_DATA_PING/live_state_handover/registries/2026-07-17T162231Z__active-gate-and-edge-event-registry__canonical.md
02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-17T162231Z__data-ping-v5__accepted-payload.json
```

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
01_CORE_FRAMEWORK/governance/2026-07-10__gpt-5-6-fresh-eyes-audit-implementation__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
```

Then read every current path referenced by the three live pointers. Repository sources win over this task where they have changed.

## 4. Branch and write safety

All writes must target only:

```text
agent/data-terminal-phase1-shadow-20260719
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
- no delete, move or rename;
- no canonical index modification;
- no secrets, tokens, holdings, private framework actions or personal data;
- search for an existing owner before creating every new path;
- read back all created or changed files;
- stop on `WRITE_BRANCH_UNVERIFIED`.

## 5. Phase 1 implementation scope

Implement only the following:

### A. Common contracts

- source observation;
- source health;
- immutable receipt;
- shadow snapshot;
- DATA PING handoff candidate;
- cross-project latest pointer.

Contracts must explicitly represent:

- source timestamp;
- retrieval timestamp;
- payload SHA-256;
- freshness seconds;
- direct versus derived;
- source convention;
- venue-specific status where applicable;
- missing fields;
- conflicts;
- source substitution;
- non-binding authority.

### B. Source registry

Register one free public primary source and one validation source where realistic.

Required semantics:

- direct and derived values separated;
- source timestamps distinguished from retrieval timestamps;
- no silent fallback;
- source substitution explicitly recorded;
- missing is `UNKNOWN`, never zero or negative evidence;
- historical observations are append-only across source revisions.

### C. One collector pilot

Preferred collector:

```text
FRED_CSV_MACRO_CORE
```

Fallback only if repository evidence shows a stronger lower-risk existing owner:

```text
DIRECT_ETHBTC_WITH_VALIDATION
```

Collector requirements:

- deterministic HTTP client;
- explicit timeout;
- bounded retry with backoff;
- stable user-agent;
- raw payload hash;
- source and retrieval timestamps;
- schema validation;
- explicit stale, empty, drift and network failure outputs;
- no paid dependency and no card or trial dependency.

### D. Validation and QA

Test at minimum:

- freshness pass and stale failure;
- empty response;
- schema drift;
- malformed timestamp;
- payload hash determinism;
- conflict representation;
- explicit missing;
- no silent fallback;
- direct versus derived labels;
- authority flags remain false.

Tests must be fixed-fixture and network-independent.

### E. Shadow outputs

Produce test or fixture-backed examples of:

- immutable shadow snapshot;
- immutable receipt;
- source-health output;
- latest shadow pointer;
- DATA PING handoff candidate;
- implementation receipt.

The DATA PING candidate must contain:

```yaml
authority:
  binding: false
  canonical_acceptance: false
  state_change: false
  portfolio_action: false
source_lineage:
quality:
observations:
missing:
conflicts:
artifacts:
```

It must never determine recovery, rotation, entry, trim, alert state, gate state or portfolio action.

### F. GitHub Action

Create or extend exactly one manual workflow:

```yaml
on:
  workflow_dispatch:
```

Requirements:

- no `schedule` or cron;
- `permissions: contents: read` initially;
- least privilege;
- run deterministic tests;
- run collector in dry-run/artifact mode;
- upload a sanitized result artifact;
- no repository commit, push or pointer write from the workflow;
- no secret echo.

## 6. Routing, adapt after owner search

Preferred new owner paths, only if no existing owner is found:

```text
02_DATA_PING/data_terminal/
  README.md
  contracts/
  source_registry/
  runtime/shadow/snapshots/
  runtime/shadow/receipts/
  runtime/shadow/latest_terminal_state.json
  runtime/shadow/latest_data_ping_handoff.json

07_PROMPTS_AND_AGENTS/data_terminal/
  runbooks/
  implementation_receipts/

scripts/data_terminal/
tests/data_terminal/
.github/workflows/data-terminal-shadow-manual.yml
```

Do not modify the three existing authoritative DATA PING pointers.

## 7. Open-PR collision guard

Open PR #49, `Framework operations hardening v0.2`, plans a separate operational workflow and must be inspected before the Data Terminal workflow is added.

Required handling:

- list all `.github/workflows/` files on `main` and relevant open PR branches;
- confirm the Data Terminal manual workflow has a unique purpose, filename, concurrency group and trigger;
- do not copy or alter the weekly operations workflow from PR #49;
- stop with `WORKFLOW_DUPLICATION_RISK` if overlap cannot be resolved deterministically.

Open PR #37 is a Research Lab sensor-pair run and must not be used as a Data Terminal owner.

## 8. Hard exclusions

Do not implement:

- schedule or cron;
- Custom GPT;
- public snapshot repository;
- self-hosted gateway;
- paid API;
- Farside HTML collector;
- CSDI;
- market-wide CVD proxy or claim;
- broad source expansion;
- active DATA PING schema redesign;
- active gate, threshold, score, signal or market-state change;
- portfolio action;
- canonical index change.

## 9. Required validation

Run and report exact commands and results for:

```text
unit tests
schema tests
negative tests
stale tests
Python compile or syntax checks
workflow YAML parse or strongest available structural check
exact changed-file list
zero deletion check
branch readback
```

Verify the diff contains no change to:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
AGENTS.md
active DATA PING pointers
active registry
accepted payloads
portfolio or market-action owners
```

## 10. Definition of done

```yaml
paid_dependencies: 0
schedule_enabled: false
custom_gpt_created: false
active_market_rules_changed: false
active_data_ping_schema_changed: false
active_framework_state_changed: false
portfolio_action: none
unit_tests: pass
schema_tests: pass
negative_tests: pass
stale_tests: pass
manual_workflow_parse: pass
branch_readback: pass
unintended_files_changed: 0
draft_pr: open
```

## 11. Completion report

Update the draft PR with:

- exact branch and commit SHAs;
- all changed paths;
- routing decisions and owner-search evidence;
- test commands and outputs;
- workflow status;
- source-lineage and failure-mode summary;
- readback status;
- unresolved blockers;
- explicit confirmation of no schedule, no Custom GPT, no active state change and no portfolio action.

Stop before merge and wait at the Phase 1 review gate.
