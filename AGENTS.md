# Investering Framework - Agent Operating Instructions

These instructions apply to all agent work in this repository.

## 0. Operational cockpit before repository work

Before automation, incident, API-agent, Codex, scheduled delivery or remediation work, read in this order:

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. `LATEST_REMEDIATION_QUEUE.json`
6. `LATEST_CODEX_READY_TASKS.json` when code remediation is relevant
7. `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`
8. the exact workflow, receipt, pointer, run and job logs

A health report may be RED while its observer workflow correctly succeeds after durable publication. `CODEX_READY` is a bounded task package, not proof that Codex has run, changed code or merged. Do not work from conversation memory or an issue summary when newer hash-bound operational files exist.

## 1. Read order

Before framework, DATA PING, weekly operations, Cycle Navigator, Research Lab, evidence-ledger, archive, governance or automation work:

1. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
2. Read `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.
3. Read `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`.
4. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
5. Load the relevant skill from `.agents/skills/`.
6. Read only the current canonical and operational files identified by those anchors.

Do not rely on conversation memory when repository sources are available.

## 2. Source and version governance

- The highest explicitly active DATA PING version wins.
- Newer operational patches override older conflicting documents in the same domain.
- Historical, legacy, superseded, shadow and source material remain context, not current authority.
- `DATA_MISSING` means `UNKNOWN`. It is not negative evidence.
- Source-backed claims are not outcome rows.
- Written governance is not functioning governance without behavior, valid rows or a documented blocked state.
- Never infer, interpolate or backfill missing market values unless a canonical rule explicitly permits it.

## 3. Framework roles

- DATA PING captures verified evidence and state.
- The main framework owns interpretation, permissions, action and ratification.
- Shadow and Research Lab challenge, test and learn. They do not self-promote.
- Prospective evidence ledgers preserve pre-registered inputs, verified outcomes and test accountability.
- Master Monday is the weekly official synthesis after ratification.
- Cycle Navigator is public output and pre-registered accountability.
- GitHub is versioned memory and the governance control plane.

### 3.1 DATA PING supplemental capture

- Read `02_DATA_PING/protocols/2026-07-28__data-ping-deep-capture-escalation-protocol-v1__canonical.md` for DATA PING analysis, weekly reconciliation, experiment maturity and event-driven evidence gaps.
- The standard DATA PING remains bounded. Do not enlarge it by default.
- When the weekly record is incomplete or a material event needs higher-resolution evidence, prepare one targeted copy-ready Custom GPT prompt under the protocol.
- Check `02_DATA_PING/operational_handoffs/deep_capture_request_ledger_v1.json` before preparing a prompt.
- Weekly and event-driven requests must be deduplicated by ISO week, method scope and event cluster.
- A prepared prompt is not evidence, and a returned package is not accepted until source, time, method, settlement and duplication checks pass.
- Every DATA PING thread handover must preserve pending deep-capture requests and active event windows.

## 4. Current architecture constraints

- Tighten and simplify before expanding.
- Respect the active new-engine freeze.
- Do not create a new engine, shadow layer, scoring concept or duplicate forward test without an explicit canonical exception.
- Prefer rows, source-lineage repair, missing-data completion, reproducibility, retirement and compression over new theory.
- Keep BTC permission and alt permission as separate evidence lanes.
- No portfolio action may be produced from DATA PING alone.

## 5. Prospective evidence discipline

For active forward tests and ledgers:

- the target test must exist in the Active Test Registry;
- the owner defines the schema, horizon, benchmark, validator and scorer;
- forecasts, decisions, horizons and invalidators must be frozen before outcomes;
- frozen inputs may not be rewritten after outcomes become observable;
- source rows, initialization rows and schemas are not outcome evidence;
- incomplete horizons remain pending, not failed;
- duplicate and overlapping event-window status must be explicit;
- use existing validators and scorers rather than reproducing their logic;
- row validity, coverage readiness and promotion status must remain separate;
- a coverage gate may permit governance review but never automatic promotion.

Use `.agents/skills/prospective-evidence-ledger/SKILL.md` for prospective row creation, maturity checks, outcome attachment, lineage reconciliation and coverage validation.

## 6. Repository write safety

- Work on an isolated `agent/task-YYYYMMDD-short-purpose` branch.
- Use pull requests for canonical changes.
- Never force-push, rewrite history, delete backup branches or use backup branches as workspaces.
- Search before creating a file.
- Prefer updating or appending to the existing owner file over creating a duplicate document.
- Preserve historical files unless an approved retirement workflow applies.
- Follow `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md` before any high-impact operation.
- Changing `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, archive routing, precedence or source governance is high-impact and requires the policy safepoint sequence first.

### Mandatory branch assertion before every write

Before any `create_file`, `update_file` or `delete_file` operation:

```yaml
target_branch_explicitly_supplied: REQUIRED
target_branch_verified_to_exist: REQUIRED
target_branch_is_default_branch: MUST_BE_NO
target_branch_is_backup_branch: MUST_BE_NO
write_path_and_operation_declared: REQUIRED
```

If any field cannot be verified, stop with:

```text
WRITE_BRANCH_UNVERIFIED
```

Never omit the branch argument and rely on the tool default. Never create placeholder or test files to probe connector behavior in a production repository.

## 7. Archive discipline

Classify material before writing:

- framework governance or architecture -> `01_CORE_FRAMEWORK/`
- DATA PING protocol or source QA -> `02_DATA_PING/`
- weekly operations or automation -> `03_WEEKLY_OPERATIONS/`
- market and regime learning -> `04_MARKET_LEARNING/`
- Cycle Navigator product -> `05_CYCLE_NAVIGATOR/`
- Research Lab synthesis or tests -> `06_RESEARCH_LAB/`
- prompts and agent workflows -> `07_PROMPTS_AND_AGENTS/`
- raw external evidence -> `08_SOURCE_MATERIAL/`
- unclear temporary material -> `09_ARCHIVE_INBOX/`

Archive the durable learning, not every intermediate conversation or report.

Every valid index addendum must also be discoverable through `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md` unless it is already directly listed in `CANONICAL_INDEX.md`.

## 8. Validation before completion

Before declaring work complete:

- verify every referenced path exists;
- verify active versions against the canonical index and addendum registry;
- verify no legacy file was treated as current authority;
- verify output status and evidence status are explicit;
- verify no hidden interpolation or unsupported scoring occurred;
- verify prospective inputs predate outcomes;
- verify frozen fields were preserved;
- verify source rows were not counted as outcomes;
- verify validator result, coverage readiness and promotion status are separate;
- verify the diff contains only intended files;
- verify every write used an explicit non-default task branch;
- report unresolved paths, blocked data and manual interventions honestly.

A remediated write incident cannot receive an unqualified `PASS`. Use `PARTIAL_REMEDIATED` for the write layer and report the final repository state separately.

## 9. Skill composition

Default composition order:

1. `canonical-context-router` to resolve current authority.
2. `prospective-evidence-ledger` for active test and ledger row lifecycle work.
3. The existing domain validator or scorer when applicable.
4. `research-lab-red-team` when interpreting evidence, testing survival or considering promotion.
5. `archive-governance` before any repository write.

Skills define procedure. Canonical repository files define current truth. A skill must never become a parallel source of market rules.
