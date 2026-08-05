# Framework Operations Hardening v0.2 — Implementation Specification

**Date:** 2026-07-15  
**Status:** APPROVED_IMPLEMENTATION_SPEC  
**Scope:** repository integrity, operational durability, evidence-lifecycle visibility, archive hygiene, bounded Codex coordination  
**Authority boundary:** no market logic, threshold, score, test promotion, event state, portfolio action, new engine or new Skill

## 1. Objective

Strengthen the current framework around its existing architecture for a 4–8 week observation period. The implementation must improve error detection, durable logging and operational verification without redesigning or restarting the framework.

The existing four-Skill stack remains unchanged. The existing Agent Control Loop remains the governing procedure. This work is hardening of existing tools and operations only.

## 2. Required read order

Before implementation, read:

1. `AGENTS.md`
2. `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
3. `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`
4. `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`
5. `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
6. `.agents/skills/canonical-context-router/SKILL.md`
7. `.agents/skills/prospective-evidence-ledger/SKILL.md`
8. `.agents/skills/archive-governance/SKILL.md`
9. `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__agent-control-loop-v0-1__canonical.md`
10. `07_PROMPTS_AND_AGENTS/github_agent/tools/framework_integrity_canary.py`
11. `03_WEEKLY_OPERATIONS/master_monday/process/2026-07-14__master-monday-durable-handoff-contract-v1__canonical.md`
12. `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md` plus current registered addenda

Inspect all existing `.github/workflows/` files before creating or changing a workflow. Search before create. Reuse or extend an existing equivalent workflow instead of creating a duplicate.

## 3. Implementation priorities

### P1 — Framework Integrity Canary v0.2

Harden the existing deterministic, read-only Canary. Preserve existing `core`, `full` and `--self-test` behavior. Add an operations-level mode or equivalent bounded extension that can report:

- all `00_ARCHIVE_CONTROL/*index-addendum*.md` files are represented exactly once in `INDEX_ADDENDUM_REGISTRY.md` or explicitly excluded by an existing canonical rule;
- duplicate registry paths;
- missing registered addendum paths;
- declared owner/reference paths in registered addenda that are deterministically parseable and missing;
- active Skill paths;
- explicit canonical owner paths;
- Master Monday latest-pointer existence and minimum required fields;
- Master Monday pointer target existence;
- declared run-receipt path existence when present;
- agreement between ratified-final availability and forecast-lineage status where deterministically evaluable;
- no false claim of a deterministic check when a check is unavailable.

The Canary must remain:

```yaml
read_only: YES
network_access_required: NO
third_party_python_packages: NO
market_authority: ZERO
automatic_repair: NO
```

Use `PASS`, `WARN`, `FAIL` or an equivalent explicit classification. A warning must not be collapsed into a pass.

### P2 — Master Monday preflight/postflight visibility

Implement the deterministic subset of the existing Durable Handoff Contract as Canary checks or a small read-only helper. Do not create a second Master Monday engine.

The output must make these stages visible where evidence exists:

```text
POINTER_PRESENT
POINTER_TARGET_PRESENT
RECEIPT_PRESENT_OR_NOT_DECLARED
RATIFIED_FINAL_STATUS_CONSISTENT
FORECAST_LINEAGE_STATUS_EXPLICIT
DURABILITY_STATUS_EXPLICIT
```

Unknown or unavailable metadata remains `UNKNOWN` or `NOT_EVALUABLE`; it must not be inferred.

### P3 — Prospective maturity/status queue

Create a dependency-free, read-only helper under:

`07_PROMPTS_AND_AGENTS/github_agent/tools/`

It must read the current Active Test Registry and current registered addenda, then emit machine-readable JSON containing only repository-declared lifecycle information, including where available:

- `test_id`
- `status`
- `next_review`
- `blocked_by`
- row-count fields
- explicitly pending horizons or reconciliation markers
- owner
- current source path
- recommended queue class such as `NEEDS_ROWS`, `DATA_BLOCKED`, `REVIEW_DUE_BY_DECLARED_RULE`, `PENDING_RECONCILIATION`, `NO_ACTION`

It must not:

- create or rewrite a row;
- infer that a horizon has matured from market memory;
- attach an actual;
- score;
- promote;
- change test status;
- create a new test or schema.

### P4 — Archive hygiene scan

Include a bounded read-only hygiene result covering:

- broken registered paths;
- unregistered index addenda;
- duplicate registry rows;
- deterministically detectable owner-path gaps;
- explicit supersession conflicts where two files are both declared active in the same directly linked lineage;
- orphaned run receipts only where an owner/pointer contract makes the expected relationship explicit.

Do not move, rename, delete or automatically retire files. Report first.

### P5 — GitHub automation and Codex review

Implement or safely extend exactly one repository workflow for the pilot.

Preferred cadence:

```yaml
schedule: weekly
preferred_day: Tuesday
preferred_time_utc: 06:30
reason: post-Master-Monday operational check during 4–8 week pilot
```

The workflow must:

1. support `workflow_dispatch`;
2. use least-privilege permissions;
3. run Canary self-test;
4. run the strongest safe read-only Canary scope;
5. run the prospective status queue;
6. upload JSON outputs as workflow artifacts;
7. write a concise GitHub Actions job summary;
8. maintain or create one durable GitHub Issue titled `[FRAMEWORK OPS] Weekly integrity ledger` and append one compact run comment for measurement;
9. create a separate actionable Issue only on `WARN` or `FAIL`, avoiding duplicate open issues for the same unresolved condition;
10. never commit, push, modify repository files, create a branch, create a PR, merge or alter market/framework authority.

Use only well-established official GitHub actions where actions are necessary. Pin versions according to the repository’s existing convention. Do not add secrets or require an OpenAI API key.

Codex remains the automatic PR reviewer through the already enabled repository setting. The workflow itself must not impersonate or invoke Codex through undocumented mechanisms.

### P6 — 4–8 week operations metrics

The weekly ledger comment and artifacts must expose enough data to evaluate after 10 qualified runs or 2026-08-09, whichever comes first:

```yaml
canary_result:
check_count:
warn_count:
fail_count:
addendum_coverage:
duplicate_registry_paths:
broken_pointer_count:
master_monday_pointer_chain_status:
active_tests_needing_rows:
active_tests_data_blocked:
pending_reconciliation_count:
manual_action_required:
workflow_run_url:
```

Do not invent a composite score. Preserve individual metrics.

## 4. Change budget

Target a small implementation. Expected changed paths are limited to:

- this specification;
- the existing Canary script;
- one new read-only prospective status helper;
- one existing or new GitHub Actions workflow;
- focused tests or fixtures only when required;
- one implementation receipt only if existing archive-governance procedure requires it.

Maximum intended changed files: 6.  
Deletion allowed: NO.  
Rename/move allowed: NO.  
`CANONICAL_INDEX.md` change allowed: NO.  
`AGENTS.md` change allowed: NO.  
`SKILL_REGISTRY.md` change allowed: NO unless implementation is impossible without correcting a directly conflicting factual status; stop and report before doing so.  
New Skill or engine: FORBIDDEN.

## 5. Safety and branch assertion

Target branch:

`agent/task-20260715-framework-ops-hardening-v0-2`

Before every write, verify and report:

```yaml
target_branch_explicitly_supplied: YES
target_branch_verified_to_exist: YES
target_branch_is_default_branch: NO
target_branch_is_backup_branch: NO
write_path_and_operation_declared: YES
```

No direct write to `main`. No force push. No placeholder/probe files. No auto-merge.

## 6. Required validation

Run at minimum:

- Python syntax/compile checks for changed Python files;
- Canary self-test;
- Canary core/full/operations-equivalent against the repository;
- prospective status helper against the repository;
- workflow YAML parse or the strongest locally available structural validation;
- exact changed-file list;
- zero deletion check;
- verification that no market, threshold, score, portfolio, live-state or active-test authority file changed.

Tests must include at least one positive fixture and one deliberately broken fixture for each newly added deterministic check family where practical.

## 7. Completion output

Push implementation commits to the existing branch and update the draft PR. Do not merge.

Return in the PR:

1. exact changed paths;
2. implementation summary by P1–P6;
3. commands and results;
4. first repository scan result;
5. unresolved limitations and false-positive risks;
6. deviations from this spec;
7. explicit confirmation that framework and market authority did not change.

## 8. Stop conditions

Stop without implementing uncertain behavior if any of these occurs:

```text
UNRESOLVED_CANONICAL_CONFLICT
WORKFLOW_DUPLICATION_RISK
HIGH_IMPACT_SAFETY_GATE_BLOCKED
WRITE_BRANCH_UNVERIFIED
MARKET_OR_PORTFOLIO_AUTHORITY_REQUESTED
REQUIRED_OWNER_SCHEMA_UNAVAILABLE
DETERMINISTIC_CHECK_NOT_RELIABLE
```

A partial, honest implementation is preferable to a broad speculative one.
