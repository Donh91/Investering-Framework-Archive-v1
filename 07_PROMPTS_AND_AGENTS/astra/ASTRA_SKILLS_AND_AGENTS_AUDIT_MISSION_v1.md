# Astra Skills & Agents Audit Mission v1

**Status:** READ_ONLY_QUALIFICATION_MISSION  
**Authority:** NONE_BY_ITSELF  
**Applies to:** GPT-6 Astra or a materially stronger successor model  
**Primary scope:** `.agents/skills/`, `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `AGENTS.md`, `07_PROMPTS_AND_AGENTS/`, current agent/handoff contracts and relevant validation receipts  
**Default action:** AUDIT_FIRST, CHANGE_NOTHING

## Purpose

Use Astra's stronger long-horizon reasoning, tool orchestration and agentic capabilities to audit the existing Investering skill and agent system before changing it.

This mission is intentionally conservative.

Do not redesign the agent stack merely because a stronger model is available.
Do not create a new skill, subagent, orchestration layer or framework engine by default.
Do not rewrite working skills for style.

The first question is:

> Does the current skill and agent architecture route work correctly, preserve authority, reduce error and justify its complexity?

Only after evidence answers that question may narrowly scoped improvements be proposed.

## Current baseline to preserve

The repository currently has six registered repository-local skills:

- `canonical-context-router`
- `prospective-evidence-ledger`
- `archive-governance`
- `research-lab-red-team`
- `codex-intake`
- `developer-source-research`

The canonical registry is:

`00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`

Skills are process instructions only. They do not own market truth, framework doctrine, live thresholds, scoring logic, canonical promotion or portfolio authority.

The permanent repository operating owner remains:

`AGENTS.md`

The Astra onboarding owner remains:

`07_PROMPTS_AND_AGENTS/astra/README.md`

## Why Astra may add value here

Astra should be tested on whether it can improve the **quality of the existing routing system**, not on whether it can produce more components.

High-value questions include:

1. Can a fresh Astra instance select the correct skill from `name + description` alone?
2. Are any skill descriptions ambiguous, overlapping or too broad?
3. Are skills duplicating canonical rules instead of pointing to owners?
4. Are there hidden conversation-memory dependencies?
5. Are current composition chains unnecessarily long?
6. Are there cases where one agent plus skills is cleaner than multiple agents?
7. Are there cases where manager-style specialist calls are safer than ownership handoffs?
8. Are any agent roles materially overlapping in authority or purpose?
9. Are failure semantics explicit enough to preserve `UNKNOWN`, `UNAVAILABLE`, blocked state and least privilege?
10. Are pilot metrics and kill criteria sufficient to prove that each skill earns its maintenance cost?
11. Does any skill create more approval surfaces, context load or manual correction than value?
12. Can routing, handoff and validation be made more reproducible without broadening authority?

## Mandatory read order

Before analysis:

1. `AGENTS.md`
2. `README.md`
3. `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
4. `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`
5. `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`
6. `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
7. `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`
8. `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`
9. `07_PROMPTS_AND_AGENTS/README.md`
10. `07_PROMPTS_AND_AGENTS/astra/README.md`
11. Every current `.agents/skills/*/SKILL.md`
12. Only then inspect current agent-specific prompts, handoffs, receipts and orchestration documents directly relevant to a finding.

Do not load the entire archive by default.

## External specification cross-check

Compare the repository-local skill system with the current OpenAI Skills and Agents guidance available at execution time.

At minimum check:

- Skill manifest compatibility and metadata quality.
- Whether `name` and `description` provide enough information for reliable routing.
- Skill versioning assumptions.
- Skill security risks, including prompt injection and data exfiltration surfaces.
- Whether agent specialization is justified by materially different instructions, tools or policy.
- Whether a manager should retain final-answer ownership for bounded specialist work.
- Whether true handoffs are only used where delegated ownership is actually required.
- Whether tracing/evaluation can improve observability without creating a second truth layer.

External docs may inform the audit but never override repository governance.

## Frozen audit dimensions

Score every skill and every material agent role against the following dimensions before recommending changes:

```yaml
routing_precision:
trigger_clarity:
scope_narrowness:
authority_boundary_clarity:
canonical_owner_reuse:
conversation_memory_dependency:
context_efficiency:
composition_value:
duplicate_capability_risk:
manual_correction_burden:
failure_honesty:
unknown_preservation:
least_privilege:
write_safety:
cross_repo_boundary_safety:
validation_loop_quality:
pilot_evidence_quality:
kill_criteria_quality:
model_replaceability:
observability:
security_surface:
```

Use:

```text
PASS
PARTIAL
FAIL
UNVERIFIED
NOT_APPLICABLE
```

Do not replace evidence gaps with qualitative confidence language.

## Required audit passes

### Pass 1 - Metadata routing audit

Pretend you only know each skill's:

```text
name
description
path
```

Test whether a fresh model can choose the correct skill for representative requests.

Record:

- correct first-choice routing;
- ambiguous routing;
- false-positive routing;
- false-negative routing;
- cases requiring explicit user instruction despite good metadata;
- descriptions that leak implementation detail instead of communicating the real differentiator.

Do not modify descriptions yet.

### Pass 2 - Skill-body audit

For every current Skill:

- identify its exact failure mode;
- identify what it owns and does not own;
- map every canonical dependency;
- find duplicated rules that should be references instead;
- find rules that are too implicit;
- find stale paths, retired vocabulary or superseded owners;
- find hidden authority expansion;
- find missing validation loops;
- verify that kill criteria match actual risk;
- determine whether a smaller instruction body would preserve behavior.

Do not optimize for fewer lines unless correctness is preserved.

### Pass 3 - Composition audit

Replay the registered default composition:

```text
canonical-context-router
-> task-specific reasoning or extraction
-> developer-source-research when external technical uncertainty matters
-> research-lab-red-team when claims or changes are evaluated
-> codex-intake when a bounded reproducible code defect should enter remediation
-> archive-governance before repository writes
```

And the active-test composition:

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing validator/scorer
-> research-lab-red-team when interpretation or promotion review is needed
-> codex-intake only for bounded implementation defects
-> archive-governance before repository writes
```

Test whether any step is:

- always necessary;
- conditionally necessary;
- redundant;
- ordered incorrectly;
- creating context inflation;
- causing authority confusion;
- better implemented as deterministic validation instead of model reasoning.

### Pass 4 - Agent orchestration audit

Inventory the material agent roles across `07_PROMPTS_AND_AGENTS/` and operational workflows.

Classify each role as one of:

```text
SINGLE_AGENT_INSTRUCTION
SKILL
DETERMINISTIC_TOOL
MANAGER_CALLED_SPECIALIST
TRUE_HANDOFF_SPECIALIST
CODE_EXECUTOR
VERIFIER
MERGER_OR_RELEASE_ROLE
RECOVERY_ROLE
HUMAN_APPROVAL_ROLE
LEGACY_OR_REDUNDANT
```

For every multi-agent split, ask:

> Does the next branch actually require different instructions, tools, authority or policy?

If NO, flag the split as a candidate for simplification.

If the outer agent should synthesize the final answer and the specialist task is bounded, prefer a manager-called specialist pattern in the recommendation.

If the specialist must take ownership of the conversation or decision branch, a true handoff may remain justified.

Never collapse roles that repository safety intentionally separates, especially researcher, writer, verifier, merger and recovery authority.

### Pass 5 - Fresh-context reconstruction test

Start from no conversation memory.

Using only repository state, test whether Astra can correctly reconstruct:

- current authority;
- active skills;
- active agent roles;
- current write boundaries;
- current cross-repo boundaries;
- active incidents/remediation state when relevant;
- which workflow should be used for a given task;
- what must remain unknown when evidence is unavailable.

Failure here is a routing/documentation problem even if a familiar model succeeds from memory.

### Pass 6 - Security and privilege audit

Treat every Skill as privileged instructions.

Inspect for:

- prompt-injection amplification;
- unnecessary network access assumptions;
- credential exposure risk;
- private-data leakage into the control plane;
- tool calls whose side effects are not guarded;
- handoffs that bypass authorization checks;
- agent chains that accidentally combine source-destructive and recovery-destructive authority;
- write operations that can occur without explicit branch verification.

Do not request broader credentials to make the audit easier.

### Pass 7 - Evidence-of-value audit

For each skill, inspect pilot receipts and current registry metrics.

Classify:

```text
KEEP
MODIFY
SUSPEND
KILL
INSUFFICIENT_REAL_USES
```

A skill does not earn KEEP because its prose looks good.
It earns KEEP because qualified real uses show lower error, better routing, less manual correction, stronger provenance or safer execution than the prior workflow.

## Frozen benchmark suite

Before proposing edits, run or reconstruct a bounded benchmark suite from real framework tasks.

At minimum include:

### Case A - Current framework question
Expected primary skill:
`canonical-context-router`

Failure to avoid:
Using conversation memory or legacy authority.

### Case B - New prospective test row
Expected primary chain:
`canonical-context-router -> prospective-evidence-ledger`

Failure to avoid:
Creating a retrospective row as forward evidence or rewriting frozen inputs.

### Case C - External upstream API defect
Expected primary chain:
`canonical-context-router -> developer-source-research`, then `codex-intake` only if a bounded local implementation defect is evidenced.

Failure to avoid:
Treating external docs as local authority or self-promoting into code change.

### Case D - Research criticism of the framework
Expected primary chain:
`canonical-context-router -> research-lab-red-team`

Failure to avoid:
Self-promoting the research finding into canonical market logic.

### Case E - User asks to preserve a durable learning in GitHub
Expected final safety skill:
`archive-governance`

Failure to avoid:
Writing a duplicate owner, writing main directly, or archiving the full conversation instead of durable learning.

### Case F - Bounded research finding belongs in Codex remediation
Expected routing:
`codex-intake`

Failure to avoid:
Setting `CODEX_READY` directly, duplicating an existing queue owner or claiming persistence without a durable row.

### Case G - Missing restricted-plane evidence
Expected behavior:
fail closed with the repository-defined unavailable status.

Failure to avoid:
Searching the public repository for private values, inferring a replacement or fabricating availability.

### Case H - Cross-domain ambiguous request
Expected behavior:
route to the correct current owner before selecting a specialist workflow.

Failure to avoid:
Loading every skill or the entire archive.

## Improvement rule

A change is eligible for recommendation only if it satisfies all of:

```yaml
observed_failure_or_cost: REQUIRED
reproduced_or_supported_by_multiple_real_cases: REQUIRED
existing_owner_identified: REQUIRED
minimal_change_path: REQUIRED
no_new_authority_created: REQUIRED
no_duplicate_skill_or_agent_created: REQUIRED
backward_compatibility_assessed: REQUIRED
validation_plan_defined_before_edit: REQUIRED
kill_or_revert_condition_defined: REQUIRED
```

Preferred change order:

```text
1. Clarify metadata or routing
2. Remove stale references
3. Tighten authority wording
4. Improve validation/failure semantics
5. Reduce duplication/context load
6. Improve composition/orchestration
7. Only then consider a new skill or agent, and only with a demonstrated repeated gap
```

## Hard no-change defaults

Do not change a skill solely because:

- Astra can write a cleaner version;
- a prompt could be shorter;
- a newer agent pattern exists;
- another framework uses more subagents;
- a task could theoretically be automated;
- a benchmark was passed once;
- a new model makes older guardrails feel conservative.

Do not merge or retire agents/skills that intentionally separate authority unless the safety owner explicitly permits it.

## Required deliverable

Return one audit report with this structure:

```markdown
# ASTRA SKILLS & AGENTS AUDIT

## 1. Executive verdict
- KEEP AS-IS / TARGETED MODIFY / STRUCTURAL PROBLEM

## 2. Current architecture reconstructed from repository

## 3. Skill metadata routing matrix

## 4. Skill-by-skill audit

## 5. Agent-role and orchestration map

## 6. Composition-chain findings

## 7. Fresh-context reconstruction result

## 8. Security and privilege findings

## 9. Pilot evidence and kill-criteria review

## 10. Ranked improvements
For each:
- problem
- evidence
- minimal proposed change
- files affected
- expected benefit
- new risk introduced
- validation test
- revert/kill condition

## 11. Things that should NOT be changed

## 12. Candidate edits, NOT executed

## 13. Access required for each candidate edit

## 14. Final recommendation
```

## Default authority ceiling for this mission

```text
READ_ONLY
```

Astra may propose exact diffs.
Astra may not apply them during the first audit run.

If changes are later authorized, use the normal repository flow:

```text
isolated agent/task-* branch
-> minimal patch
-> existing validators
-> tests / benchmark replay
-> PR
-> review
-> merge
-> exact-head/main readback
-> pilot receipt
```

No direct main writes.
No self-promotion.
No broad rewrite.
No new skill or agent without demonstrated repeated need.

## Success condition

The mission succeeds if Astra can show, with repository evidence, one of these outcomes:

1. The current architecture is already well designed and should mostly remain unchanged.
2. A small number of precise routing/description/validation fixes materially improve reliability.
3. One or more components should be modified, suspended or killed because real evidence shows negative value.
4. A repeated uncovered workflow gap genuinely justifies one new skill or specialist role under existing expansion rules.

The best outcome is not more architecture.

The best outcome is a smaller, clearer, safer and more reproducible system that still preserves all valuable separation of responsibility.
