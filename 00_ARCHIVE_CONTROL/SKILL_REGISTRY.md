# Investering Agent Skill Registry v0.3

**Dato:** 2026-08-22  
**Status:** CANONICAL_OPERATIONAL_REGISTRY  
**Område:** agent routing / reproducible workflows / archive control  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`, `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`  
**Implementation references:** `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md`, `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`

## 1. Purpose

This registry defines the active repository-local agent skills, their routing order, authority boundaries, validation requirements and pilot status.

Skills are process instructions. They do not own market truth, framework doctrine, live thresholds, scoring logic or portfolio authority.

## 2. Active stack

| Skill | Path | Status | Primary triggers | Authority |
|---|---|---|---|---|
| canonical-context-router | `.agents/skills/canonical-context-router/SKILL.md` | PILOT_ACTIVE_V0_1_1 | framework, DATA PING, Master Monday, Cycle Navigator, active version, current rule, precedence | Read and resolve context only |
| prospective-evidence-ledger | `.agents/skills/prospective-evidence-ledger/SKILL.md` | PILOT_ACTIVE_V0_1 | freeze input, forward row, actual, maturity, M3, FRLP, FNP, Transmission Matrix, lineage, coverage | Govern evidence-row lifecycle; no scoring or promotion authority |
| archive-governance | `.agents/skills/archive-governance/SKILL.md` | PILOT_ACTIVE_V0_1_1 | archive, save, GitHub update, canonical, index, place this, preserve this | Classify and govern writes, subject to repository policy |
| research-lab-red-team | `.agents/skills/research-lab-red-team/SKILL.md` | PILOT_ACTIVE | audit, red team, Claude/Grok review, framework proposal, evidence, falsify | Evaluate and classify, no self-promotion |
| codex-intake | `.agents/skills/codex-intake/SKILL.md` | ACTIVE_OPERATIONAL_V1 | queue for Codex, bounded code defect, research-to-code handoff, CODEX candidate | Prepare/deduplicate bounded research intake only; no CODEX_READY, merge, market or framework authority |

## 3. Default composition

For general framework work:

```text
canonical-context-router
-> task-specific reasoning or extraction
-> research-lab-red-team when claims or changes are evaluated
-> codex-intake only when a reproducible bounded code defect should enter remediation
-> archive-governance before repository writes
```

For active test and ledger work:

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing domain validator or scorer
-> research-lab-red-team only for interpretation, test survival or promotion review
-> codex-intake only for bounded implementation defects, never for test promotion
-> archive-governance before repository writes
```

The router resolves current authority. Prospective Evidence Ledger governs causal row lifecycle and evidence integrity. The red-team skill evaluates decision value and test survival. Codex Intake converts reproducible code-local research findings into governed candidates without granting research code authority. Archive Governance controls placement, duplication, discoverability, write safety and backup-scope truth.

## 4. Global constraints

All skills must comply with:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
01_CORE_FRAMEWORK/governance/2026-07-10__gpt-5-6-fresh-eyes-audit-implementation__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-10__rule-and-evidence-registry__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
```

Binding rules:

- skills do not create a new engine or shadow layer;
- skills do not copy live market thresholds into their own body;
- skills point to canonical owner files;
- missing data remains unknown;
- source rows are not outcome rows;
- frozen prospective inputs cannot be rewritten after outcomes;
- no schema or scoring invention;
- no automatic portfolio action;
- no canonical promotion without evidence, behavior, valid rows and governance review;
- no repository write without explicit user intent;
- no write call without an explicit verified non-default task branch;
- no placeholder or tool-probe files in production repositories;
- no direct write to canonical `main`;
- valid index addenda must be represented in `INDEX_ADDENDUM_REGISTRY.md`;
- canonical index changes require the high-impact safepoint workflow;
- backup claims must distinguish frozen source, current merged version and post-merge delta status.

## 5. Prospective evidence contract

`prospective-evidence-ledger` may:

- resolve the registered active test and ledger owner;
- verify pre-registration and exact timestamps;
- preserve frozen inputs;
- determine outcome maturity;
- verify source lineage;
- detect duplicates and event-window overlap;
- delegate to existing validators and scorers;
- calculate owner-defined coverage deltas;
- prepare a safe write manifest.

It may not:

- create a new test;
- create a new ledger schema;
- define or change a scorer;
- reinterpret a coverage PASS as edge;
- promote a rule;
- change live market state;
- produce a market call or portfolio action;
- schedule recurring collection.

Required three-layer result separation:

```yaml
row_validity: PASS | PARTIAL | FAIL | NOT_APPLICABLE
coverage_readiness: READY | NOT_READY | BLOCKED | NOT_APPLICABLE
edge_or_promotion_status: NO_CHANGE | GOVERNANCE_REVIEW_PERMITTED | NOT_APPLICABLE
```

## 6. Codex intake contract

`codex-intake` may:

- detect an explicit research-to-Codex handoff request;
- read and deduplicate against the current Codex/remediation queue;
- package reproducible evidence into `CODEX_RESEARCH_CANDIDATE_v1`;
- link a research finding to an existing health signature instead of duplicating authority;
- request `NORMAL` or `EXPEDITED` queue priority;
- persist the candidate through normal isolated-branch and PR governance when write authority exists.

It may not:

- set `CODEX_READY` itself;
- change code as part of research intake;
- bypass fresh-state binding, CI, PR review or post-fix gates;
- broaden `allowed_change_scope` beyond the evidence;
- modify market gates, model weights, canonical authority, portfolio logic, API budget or new policy semantics;
- create a parallel Codex queue in Experiments or Cycle Navigator;
- claim a candidate was queued when it was not durably persisted.

The machine queue authority remains `LATEST_CODEX_READY_TASKS.json`. Execution history is observable in `LATEST_CODEX_EXECUTION_STATE.json` and `research/codex/CODEX_EXECUTION_LEDGER.jsonl` but those surfaces have no promotion authority.

## 7. Shared pilot metrics

Each qualified use should be assessed against these fields:

```yaml
skill_name:
run_date:
trigger_correct: YES | NO | PARTIAL
correct_owner_files_found: YES | NO | PARTIAL
registered_addenda_found: YES | NO | PARTIAL | NOT_APPLICABLE
legacy_as_current_error: YES | NO
unnecessary_new_document_avoided: YES | NO | NOT_APPLICABLE
unsupported_promotion_blocked: YES | NO | NOT_APPLICABLE
branch_assertion: PASS | FAIL | NOT_APPLICABLE
explicit_branch_on_every_write: YES | NO | NOT_APPLICABLE
manual_corrections_required: integer
incident_count: integer
write_governance_result: PASS | PARTIAL_REMEDIATED | FAIL | NOT_APPLICABLE
final_repository_state: PASS | PARTIAL | FAIL | NOT_APPLICABLE
backup_product: FULL_GIT_MIRROR | CANONICAL_SNAPSHOT | TARGETED_SNAPSHOT | DELTA_SNAPSHOT | NONE
snapshot_frozen_source_sha:
current_owner_or_merge_sha:
current_version_in_snapshot: YES | NO | PARTIAL | UNKNOWN | NOT_APPLICABLE
post_merge_delta_status: PASS | PENDING | NOT_REQUIRED | UNKNOWN | NOT_APPLICABLE
notes:
```

A qualified use is a real framework, archive, Research Lab or active-ledger task, not a synthetic prompt.

A remediated default-branch or unintended-write incident must be recorded as `PARTIAL_REMEDIATED`, never an unqualified write-governance `PASS`.

## 8. Prospective Evidence Ledger pilot metrics

For each qualified use of the new Skill, additionally record:

```yaml
test_id:
operation:
correct_test_owner_found: YES | NO | PARTIAL
correct_ledger_found: YES | NO | PARTIAL
ledger_contract_complete: YES | NO
causal_pre_registration_correct: YES | NO | NOT_APPLICABLE
frozen_fields_preserved: YES | NO | NOT_APPLICABLE
maturity_classification_correct: YES | NO | NOT_APPLICABLE
source_lineage_complete: YES | NO | PARTIAL
duplicate_prevented: YES | NO | NOT_APPLICABLE
event_window_classification_correct: YES | NO | NOT_APPLICABLE
validator_executed: YES | NO | NOT_APPLICABLE
invalid_forward_row_blocked: YES | NO | NOT_APPLICABLE
unsupported_score_blocked: YES | NO | NOT_APPLICABLE
false_eligible_incidents: integer
```

## 9. First qualified-use correction

The first archive-governance live run is recorded at:

```text
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-12__archive-governance-full-sensor-backtest__receipt.md
```

Corrected pilot interpretation:

```yaml
qualified_use_number: 1
trigger_correct: YES
correct_owner_files_found: YES
unnecessary_new_document_avoided: YES
unsupported_promotion_blocked: YES
branch_assertion: PARTIAL
explicit_branch_on_every_write: NO
manual_corrections_required: 1
incident_count: 1
write_governance_result: PARTIAL_REMEDIATED
final_repository_state: PASS
research_package_backup: PASS_TARGETED_RESEARCH_SNAPSHOT
current_owner_version_in_snapshot: NO
post_merge_delta_status: PENDING
```

## 10. Review gate

Review the skill stack after either:

- 10 additional qualified uses after v0.3 activation, or
- 2026-09-22,

whichever occurs first.

`prospective-evidence-ledger` must also accumulate at least three real uses before a KEEP decision is justified. `codex-intake` must accumulate at least three real research-origin candidates or deduplicated handoffs before a KEEP decision is justified.

Review classifications:

```text
KEEP
MODIFY
SUSPEND
KILL
```

## 11. Kill and modification criteria

A skill must be modified, suspended or killed if any of the following occurs:

- it repeatedly routes to superseded or legacy authority;
- it misses valid registered addenda;
- it creates parallel truth instead of reading canonical owner files;
- it increases duplicate documents or archive inflation;
- it silently changes framework behavior;
- it produces unsupported promotions or inferred data;
- it causes repository writes without explicit user intent;
- it omits or misroutes the write branch;
- it creates placeholder or tool-probe files in production repositories;
- it overstates backup coverage;
- it adds more manual correction than the prior workflow;
- it conflicts with repository safety or backup governance;
- its value cannot be demonstrated after the pilot review gate.

`prospective-evidence-ledger` must be immediately modified or suspended if it:

- marks a retrospective row as forward eligible;
- changes a frozen forecast or decision;
- creates a duplicate evidence row;
- treats a source row as an outcome row;
- overstates event-window independence;
- scores with an unfrozen method;
- treats coverage readiness as edge or promotion;
- creates market or portfolio authority.

`codex-intake` must be immediately modified or suspended if it:

- self-promotes a research candidate to CODEX_READY;
- creates duplicate Codex authority instead of linking a current health task;
- accepts framework-owner changes into code-remediation authority;
- weakens fresh-state binding or PR/CI/post-fix requirements;
- claims fast execution when only queue publication is evidenced.

## 12. Expansion rule and v0.3 exception

No additional skill should be added without a demonstrated repeated workflow gap.

A candidate skill must state:

```text
failure mode observed
repeated task frequency
why existing skills cannot cover it
inputs
outputs
validation loop
authority boundary
kill criterion
```

The original v0.2 exception was `prospective-evidence-ledger`, justified by repeated active-test row-production, source-lineage, maturity and coverage gaps.

The v0.3 exception is `codex-intake`, justified by repeated research threads identifying code-remediable defects while the existing Codex queue accepted only health-origin findings and the maturation workflow otherwise depended on fixed cadence. Existing research and archive skills cannot safely create, deduplicate, bind and expose a source-agnostic Codex queue. The new skill adds routing only, not market or code authority.

Potential later candidates such as DATA PING execution, weekly range audit, Master Monday, Cycle Navigator publication and automated agent loops remain `NOT_AUTHORIZED_FOR_BUILD` unless separately governed.

## 13. Current status

```yaml
stack_version: 0.3
stack_status: PILOT_ACTIVE_HARDENED
skills_active: 5
stack_qualified_uses_completed_before_v0_3: 1
prospective_evidence_ledger_version: 0.1
codex_intake_version: 1
codex_intake_authority: ROUTING_ONLY
codex_queue_authority: LATEST_CODEX_READY_TASKS.json
codex_execution_observability: LATEST_CODEX_EXECUTION_STATE.json
trading_logic_changed: NO
framework_authority_changed: NO
new_engine_created: NO
new_shadow_layer_created: NO
new_test_created: NO
new_score_created: NO
automatic_portfolio_action_added: NO
research_codex_event_trigger_added: YES
write_branch_assertion_active: YES
addendum_registry_active: YES
incident_aware_scoring_active: YES
post_merge_backup_scope_active: YES
```
