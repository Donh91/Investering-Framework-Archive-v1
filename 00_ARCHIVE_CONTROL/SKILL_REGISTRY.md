# Investering Agent Skill Registry v0.1.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_REGISTRY  
**Område:** agent routing / reproducible workflows / archive control  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`, `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`  
**Implementation reference:** `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md`

## 1. Purpose

This registry defines the active repository-local agent skills, their routing order, authority boundaries, validation requirements and pilot status.

Skills are process instructions. They do not own market truth, framework doctrine, live thresholds or portfolio authority.

## 2. Active stack

| Skill | Path | Status | Primary triggers | Authority |
|---|---|---|---|---|
| canonical-context-router | `.agents/skills/canonical-context-router/SKILL.md` | PILOT_ACTIVE_V0_1_1 | framework, DATA PING, Master Monday, Cycle Navigator, active version, current rule, precedence | Read and resolve context only |
| archive-governance | `.agents/skills/archive-governance/SKILL.md` | PILOT_ACTIVE_V0_1_1 | archive, save, GitHub update, canonical, index, place this, preserve this | Classify and govern writes, subject to repository policy |
| research-lab-red-team | `.agents/skills/research-lab-red-team/SKILL.md` | PILOT_ACTIVE | audit, red team, Claude/Grok review, framework proposal, evidence, falsify | Evaluate and classify, no self-promotion |

## 3. Default composition

```text
canonical-context-router
-> task-specific reasoning or extraction
-> research-lab-red-team when claims or changes are evaluated
-> archive-governance before repository writes
```

The router resolves current authority first. The red-team skill evaluates decision value and evidence. Archive governance controls placement, duplication, discoverability, write safety and backup-scope truth.

## 4. Global constraints

All skills must comply with:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
01_CORE_FRAMEWORK/governance/2026-07-10__gpt-5-6-fresh-eyes-audit-implementation__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
```

Binding rules:

- skills do not create a new engine or shadow layer;
- skills do not copy live market thresholds into their own body;
- skills point to canonical owner files;
- missing data remains unknown;
- no automatic portfolio action;
- no canonical promotion without evidence, behavior or valid rows;
- no repository write without explicit user intent;
- no write call without an explicit verified non-default task branch;
- no placeholder or tool-probe files in production repositories;
- no direct write to canonical `main`;
- valid index addenda must be represented in `INDEX_ADDENDUM_REGISTRY.md`;
- canonical index changes require the high-impact safepoint workflow;
- backup claims must distinguish frozen source, current merged version and post-merge delta status.

## 5. Pilot metrics

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

A qualified use is a real framework, archive or Research Lab task, not a synthetic prompt.

A remediated default-branch or unintended-write incident must be recorded as `PARTIAL_REMEDIATED`, never an unqualified write-governance `PASS`.

## 6. First qualified-use correction

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

## 7. Review gate

Review the v0.1.1 stack after either:

- 10 qualified uses, or
- 2026-08-09,

whichever occurs first.

Review classifications:

```text
KEEP
MODIFY
SUSPEND
KILL
```

## 8. Kill and modification criteria

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

## 9. Expansion rule

No additional skill should be added until a repeated workflow gap is demonstrated.

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

Potential later candidates such as DATA PING execution, weekly range audit, Master Monday and Cycle Navigator publication remain `NOT_AUTHORIZED_FOR_BUILD` in v0.1.1. They require evidence from the first three skills and a separate implementation decision.

## 10. Current status

```yaml
stack_version: 0.1.1
stack_status: PILOT_ACTIVE_HARDENED
skills_active: 3
qualified_uses_completed: 1
trading_logic_changed: NO
framework_authority_changed: NO
new_engine_created: NO
new_shadow_layer_created: NO
automatic_scheduling_added: NO
automatic_portfolio_action_added: NO
write_branch_assertion_added: YES
addendum_registry_added: YES
incident_aware_scoring_added: YES
post_merge_backup_scope_added: YES
```
