# Astra Reviewer & Failure Learning Addendum v1

**Status:** BINDING_EXTENSION_TO_EXISTING_AUDIT_MISSION  
**Parent mission:** `07_PROMPTS_AND_AGENTS/astra/ASTRA_SKILLS_AND_AGENTS_AUDIT_MISSION_v1.md`  
**Authority:** NONE_BY_ITSELF  
**Mode:** READ_ONLY_ANALYSIS_FIRST  
**Purpose:** Add evidence-based reviewer/failure learning to the existing Astra Skills & Agents audit without creating a new agent system, governance owner or automatic self-modification loop.

## Why this addendum exists

The repository already has mature agent instructions, Skills, routing, CI, governance and remediation paths. The useful idea is therefore not to copy reviewer comments into `AGENTS.md`.

The useful task is to learn from repeated real failures and determine the smallest correct prevention mechanism.

A repeated review finding may belong in:

```text
ROOT_AGENTS
NESTED_AGENTS
EXISTING_SKILL
CI_OR_TEST
EXISTING_OWNER_DOC
CODEX_INTAKE
NO_CHANGE
```

Frequency alone is not authority. Reviewer prose is not truth. A permanent instruction is not the default answer.

## Integration with the parent mission

Run this addendum as **Pass 8** of `ASTRA_SKILLS_AND_AGENTS_AUDIT_MISSION_v1` after the existing metadata, skill-body, composition, orchestration, fresh-context, security and evidence-of-value passes.

Do not treat this as a separate Astra mission or a new framework subsystem.

The parent mission's read-only first-run ceiling remains binding.

## Pass 8 - Historical reviewer and failure learning

### 8.1 Build an evidence set from real repository history

Inspect, where available:

- substantive Codex or other reviewer findings;
- human review findings;
- CI failures and regression failures;
- remediation PRs;
- abandoned or superseded PRs where the reason reflects an implementation or governance failure;
- post-merge defects;
- production-readback failures;
- documented write-safety incidents;
- workflow/runtime failures that required corrective PRs;
- issues or receipts that prove a failure survived review and reached later stages.

A PR body or review comment is a lead, not proof by itself. Prefer corroboration from code diff, test failure, CI result, production receipt, main readback or a later bounded remediation.

### 8.2 Adaptive history window

Do not scan a fixed number of PRs merely because a prompt says so.

Use this bounded strategy:

```yaml
initial_recent_pr_window: 100
expansion_batch_size: 50
stop_when: TWO_CONSECUTIVE_EXPANSION_BATCHES_ADD_NO_NEW_MATERIAL_ROOT_CAUSE_CLUSTER
ordinary_hard_cap_prs: 300
beyond_cap: REQUIRE_EXPLICIT_JUSTIFICATION_IN_AUDIT_REPORT
```

Targeted older PRs may be inspected outside the recent window when current evidence references a known historical incident, regression family or superseded implementation.

The objective is root-cause saturation, not archive exhaustion.

### 8.3 Mandatory noise filter

Exclude from failure counts:

- Codex quota or usage-limit notices;
- bot boilerplate;
- generic status messages;
- merge acknowledgements;
- non-actionable praise or acknowledgements;
- duplicate copies of the same finding on the same underlying defect;
- comments unrelated to implementation quality;
- automated comments whose only content is availability, billing or service state.

A comment is eligible as a reviewer finding only when it identifies or supports a concrete defect, risk, incorrect assumption, missing guardrail, validation gap or reproducible behavior.

Explicitly classify excluded material as `NOISE_EXCLUDED`, so filtering itself remains auditable.

### 8.4 Cluster by root cause, not wording

Do not count paraphrases as independent findings.

For each candidate cluster, determine:

```yaml
cluster_id:
root_cause:
independent_occurrences:
first_seen:
last_seen:
severity:
affected_surfaces:
reviewer_sources:
ci_or_runtime_evidence:
remediation_refs:
existing_rule_or_guardrail_found:
why_existing_guardrail_did_or_did_not_prevent_recurrence:
```

Examples of distinct root-cause families may include schema drift, temporal provenance, write-target ambiguity, stale-state assumptions, branch-safety violations, weak exact-head verification, authority confusion or brittle workflow assumptions. These are examples only. Do not force findings into a predefined taxonomy when the evidence supports a different root cause.

### 8.5 Existing-rule-first test

Before proposing any new instruction, search current:

```text
AGENTS.md
nested AGENTS.md files
.agents/skills/*/SKILL.md
current canonical/operational owner documents
existing CI/tests/validators
```

Then classify:

```text
RULE_ABSENT
RULE_PRESENT_BUT_HARD_TO_DISCOVER
RULE_PRESENT_BUT_NOT_MACHINE_ENFORCED
RULE_PRESENT_AND_ENFORCED_BUT_BYPASSED
RULE_PRESENT_AND_WORKING
```

If the rule already exists, **do not duplicate it merely because the failure recurred**.

Prefer fixing discoverability, routing, deterministic enforcement or the actual implementation defect.

### 8.6 Placement decision

For each root-cause cluster choose exactly one primary disposition:

```text
NO_CHANGE
ROOT_AGENTS
NESTED_AGENTS
EXISTING_SKILL
CI_OR_TEST
EXISTING_OWNER_DOC
CODEX_INTAKE
```

Use these defaults:

- `ROOT_AGENTS` only for repository-wide operating invariants that materially affect many task classes.
- `NESTED_AGENTS` for directory/domain-specific behavior that should not burden unrelated work.
- `EXISTING_SKILL` for reusable procedural guidance already owned by a current Skill.
- `CI_OR_TEST` whenever the rule is machine-checkable with acceptable false-positive risk.
- `EXISTING_OWNER_DOC` for domain semantics, contracts or authority rules that belong to an existing canonical/operational owner.
- `CODEX_INTAKE` when the current problem is a bounded reproducible code defect, using the existing governed intake path.
- `NO_CHANGE` for one-offs, stale incidents, already-fixed behavior, insufficient evidence or lessons that would create more instruction cost than prevention value.

Do not create a new Skill, agent or governance owner from this pass unless the parent mission's existing repeated-gap rule independently justifies it.

### 8.7 Deterministic enforcement beats reminder prose

Use this preference order when a real gap is found:

```text
1. Fix the implementation defect
2. Add or strengthen a deterministic test / validator / CI gate
3. Improve routing or discoverability to an existing owner
4. Tighten an existing Skill or local instruction
5. Add root AGENTS prose only when the rule is truly repository-wide and cannot be enforced sufficiently elsewhere
```

Do not convert machine-checkable failures into permanent natural-language reminders merely because prose is easier to write.

### 8.8 Recurrence and materiality threshold

A permanent instruction change normally requires:

```yaml
independent_real_occurrences: AT_LEAST_2
same_root_cause_not_same_event: REQUIRED
generalizes_beyond_one_file_or_one_incident: REQUIRED
existing_owner_checked: REQUIRED
counterfactual_prevention_plausible: REQUIRED
validation_plan: REQUIRED
false_stop_risk_assessed: REQUIRED
```

Exception: one high-severity structural failure may justify deterministic enforcement after one occurrence when recurrence could cause material source, recovery, evidence-integrity or production harm. Even then, new prose is not automatically justified.

Do not inflate recurrence counts by counting the original defect, its review comment, its remediation PR and its regression test as four independent events.

### 8.9 Anti-bloat rule

Treat instruction context as a scarce resource.

For every proposed instruction edit, report:

```yaml
instruction_bytes_before:
instruction_bytes_after:
net_instruction_bytes:
rule_replaced_or_consolidated:
why_net_growth_is_necessary:
why_ci_or_existing_owner_is_insufficient:
```

Prefer net-zero or negative instruction footprint where correctness is preserved.

No audit wave should make root `AGENTS.md` a historical incident log.

Archive durable principles, not every past failure.

### 8.10 Historical replay before recommending an instruction change

For each proposed instruction/routing change, replay against real historical tasks where practical.

Use:

- the independent real failure cases supporting the cluster;
- at least two relevant negative controls where the proposed rule should **not** fire;
- current repository authority and current Skill composition;
- the same expected output/behavior criteria for before/after comparison.

Record:

```yaml
historical_failures_prevented:
historical_failures_not_prevented:
negative_controls_false_stopped:
routing_regressions:
new_manual_approval_burden:
context_cost_change:
result: IMPROVES | NEUTRAL | REGRESSES | INSUFFICIENT_EVIDENCE
```

Do not claim improvement from synthetic examples alone when real repository cases exist.

### 8.11 Reviewer disagreement and reviewer fallibility

Treat reviewers as evidence sources, not canonical authorities.

When reviewers disagree, or when a reviewer finding conflicts with current code/tests/governance:

1. reproduce the behavior if possible;
2. resolve current owner and authority;
3. inspect the exact code/CI/runtime evidence;
4. classify the reviewer claim as `SUPPORTED`, `PARTIAL`, `NOT_REPRODUCED`, `STALE` or `WRONG`;
5. do not institutionalize a wrong or stale reviewer preference.

A frequent reviewer preference that does not improve correctness, safety, reproducibility or maintenance is not a framework rule.

### 8.12 Safety and authority firewall

This pass grants no new authority.

It must not:

- automatically edit `AGENTS.md`;
- automatically edit Skills;
- weaken existing CI or safety gates;
- create self-modifying agent loops;
- grant Astra write access;
- combine source-destructive and recovery-destructive authority;
- change market thresholds, weights, portfolio logic or scientific promotion rules;
- rewrite historical evidence;
- treat reviewer frequency as canonical truth.

First-run output remains analysis and candidate diffs only under the parent mission.

## Required Pass 8 deliverable

Add this section to the parent mission's audit report:

```markdown
## Historical Reviewer & Failure Learning

### Evidence window
- recent PRs inspected
- targeted older PRs inspected
- expansion batches used
- saturation / stop reason
- noise excluded

### Root-cause clusters
For each cluster:
- cluster_id
- root cause
- independent occurrences
- severity
- evidence refs
- current guardrail status
- disposition

### Placement matrix
- NO_CHANGE
- ROOT_AGENTS
- NESTED_AGENTS
- EXISTING_SKILL
- CI_OR_TEST
- EXISTING_OWNER_DOC
- CODEX_INTAKE

### Candidate improvements
For each candidate:
- minimal change
- why this placement is correct
- historical replay result
- negative-control result
- instruction/context delta
- new risk introduced
- revert/kill condition

### Rejected lessons
List recurring-looking patterns that were excluded as noise, stale reviewer preference, duplicate evidence, already-enforced behavior or insufficiently generalizable incidents.
```

Rank candidate improvements by expected marginal prevention value, not raw frequency.

## Success condition

This addendum succeeds when Astra can turn messy historical review/failure evidence into a small number of validated prevention improvements while leaving most of the repository unchanged.

A valid outcome may be:

```text
NO AGENT-INSTRUCTION CHANGE REQUIRED
```

That is preferable to adding prose without evidence.
