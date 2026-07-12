# Investering Agent Control Loop v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_PILOT  
**Område:** agent workflows / automation / integrity / mobile control plane  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Related folders:** `00_ARCHIVE_CONTROL/`, `.agents/skills/`, `.github/ISSUE_TEMPLATE/`, `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`, Repository Safety and Backup Policy v1.0  
**Authority boundary:** procedure and repository integrity only; no market, threshold, score, promotion or portfolio authority

## 1. Executive decision

A narrow agent-control pilot is authorized without creating a fifth Skill or a new framework engine.

The pilot contains five connected components:

```text
1. Framework Integrity Canary
2. Machine-readable run state
3. Standard implementation receipt
4. Bounded maximum-two-iteration agent loop
5. GitHub Issue command bus and research-intake workflow
```

The existing four-Skill stack remains unchanged:

```text
canonical-context-router
prospective-evidence-ledger
archive-governance
research-lab-red-team
```

The control loop composes those Skills. It does not replace them and does not become a parallel truth layer.

## 2. Why this is allowed now

The repeated operational gap is not missing market theory. It is missing execution accountability:

- agents can perform useful work without a standard state object;
- the same model can implement and judge without an independent deterministic check;
- failures can remain silent between scheduled runs;
- the user needs an iPhone-native command surface;
- X research needs triage before it becomes architecture;
- a long-running loop needs explicit stop conditions.

This pilot is therefore an infrastructure and governance layer, not a new analytical engine.

## 3. Runtime architecture

```text
iPhone
-> GitHub Issue command
-> scheduled ChatGPT Agent Queue Runner
-> canonical-context-router
-> task-specific existing Skill(s)
-> archive-governance before writes
-> task branch
-> implementation iteration 1
-> deterministic or owner-defined verifier
-> optional correction iteration 2
-> final stop
-> draft PR
-> receipt + run state
-> human or explicit main-framework merge decision
```

The phone is the control plane. GitHub is durable state. Scheduled ChatGPT is the orchestrator. Existing Skills define procedure. Canonical repository files define truth.

A Custom GPT may help create or interpret commands interactively, but Scheduled Tasks do not execute a Custom GPT as the scheduler. Durable instructions therefore live in GitHub and in the scheduled task prompt.

## 4. Framework Integrity Canary

Primary executable:

```text
07_PROMPTS_AND_AGENTS/github_agent/tools/framework_integrity_canary.py
```

The Canary is deterministic, read-only and dependency-free.

### Core checks

- required repository control files exist;
- `AGENTS.md` retains write-safety and portfolio-boundary rules;
- every active Skill path in `SKILL_REGISTRY.md` exists;
- every active addendum path in `INDEX_ADDENDUM_REGISTRY.md` exists;
- optional full mode verifies explicit path references in `CANONICAL_INDEX.md`;
- output is machine-readable JSON;
- any missing mandatory path produces `FAIL`.

### Execution modes

```text
CORE
= fixed governance, active Skills and registered addenda

FULL
= CORE plus every explicit canonical-index path that can be checked deterministically

CONNECTOR_EQUIVALENT
= scheduled agent performs the same manifest checks when code execution is unavailable
```

The scheduled agent must never call a connector-equivalent checklist a deterministic script run. The receipt records the actual execution mode.

## 5. Run state contract

Schema owner:

```text
07_PROMPTS_AND_AGENTS/github_agent/schemas/agent-run-state.schema.json
```

Each material run receives one state object containing:

- stable `run_id`;
- originating issue number when applicable;
- task class;
- requested action;
- explicit write-intent status;
- branch and base SHA;
- iteration count;
- verifier mode and result;
- changed paths;
- PR number;
- stop reason;
- incident count;
- final repository state;
- unresolved items.

State transitions:

```text
QUEUED
-> CONTEXT_RESOLVED
-> IMPLEMENTING
-> VERIFYING
-> CORRECTING, optional once
-> DRAFT_PR_OPEN
-> COMPLETE | PARTIAL | BLOCKED
```

A run may never exceed two implementation-verification iterations.

## 6. Standard receipt contract

Template owner:

```text
07_PROMPTS_AND_AGENTS/github_agent/templates/agent-run-receipt-template.md
```

A receipt must distinguish:

```text
task_result
write_governance_result
verifier_result
final_repository_state
backup_product
```

A successful content result does not erase a write incident. A blocked or partial verifier result cannot be rewritten as `PASS`.

## 7. Bounded loop rules

The loop may process at most one GitHub Issue per scheduled run.

### Mandatory sequence

1. Read repository operating anchors.
2. Resolve current authority with `canonical-context-router`.
3. Confirm the issue contains explicit write intent before mutation.
4. Select existing task-specific Skills.
5. Invoke `archive-governance` before every write sequence.
6. Create or reuse one isolated `agent/task-*` branch.
7. Implement iteration 1.
8. Run the independent verifier.
9. If verifier fails and a safe correction is clear, perform iteration 2.
10. Run the verifier again.
11. Stop unconditionally.
12. Open or update a draft PR.
13. Write run state and receipt.
14. Comment on the Issue with the PR and result.

### Hard stop conditions

```text
MAX_ITERATIONS_REACHED
WRITE_BRANCH_UNVERIFIED
HIGH_IMPACT_SAFETY_GATE_BLOCKED
UNRESOLVED_CANONICAL_CONFLICT
VERIFIER_UNAVAILABLE
SOURCE_LINEAGE_INCOMPLETE
USER_WRITE_INTENT_MISSING
SECRET_OR_CREDENTIAL_RISK
MARKET_OR_PORTFOLIO_AUTHORITY_REQUESTED
```

### Forbidden

- auto-merge;
- direct write to `main`;
- force push;
- deletion of backup branches;
- self-promotion of a rule;
- automatic threshold or scoring changes;
- portfolio action;
- more than one Issue per run;
- more than two implementation-verification iterations;
- spawning an unbounded subagent tree;
- treating the implementer model as the sole verifier when a deterministic or owner-defined validator exists.

## 8. iPhone GitHub Issue command bus

Issue form owner:

```text
.github/ISSUE_TEMPLATE/investering-agent-command.yml
```

Queue grammar:

```text
title prefix: [AGENT QUEUE]
required: task class
required: requested action
required: source links or repository paths
required: write intent
required: expected output
optional: deadline or priority
```

The command bus is intentionally simple. It must work from the GitHub iOS app without a terminal.

The runner processes the oldest actionable open Issue and leaves all others queued.

## 9. Research intake workflow

Prompt owner:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__research-intake-workflow-v0-1__operational.md
```

Research intake classifies external posts before implementation:

```text
SOURCE_EVIDENCE
PRACTITIONER_ANECDOTE
ARCHITECTURE_INSPIRATION
MARKETING_OR_UNVERIFIED
DUPLICATE_OF_EXISTING_OWNER
REPEATED_GAP_CANDIDATE
NOT_RELEVANT
```

It must map every useful idea to an existing owner or an explicit repeated gap.

It may recommend a test. It may not directly create a new engine, Skill, score, threshold or portfolio rule.

## 10. Scheduled-task integration

One narrow scheduled Agent Queue Runner is authorized as a pilot:

```text
frequency: daily evening
maximum issues per run: 1
maximum iterations: 2
write mode: task branch only
PR mode: draft only
merge authority: none
notification: only on action, block or failure
```

The existing GitHub Archive Sync + Backup task should include one weekly Canary check.

No additional generic loop is authorized.

## 11. Pilot evaluation

Review after:

```text
10 queue runs
or 2026-08-09
whichever occurs first
```

Required metrics:

```yaml
issues_seen:
issues_actionable:
issues_processed:
issues_skipped_missing_write_intent:
context_resolution_pass_rate:
correct_skill_routing_rate:
branch_assertion_pass_rate:
canary_pass_rate:
verifier_first_pass_rate:
second_iteration_rate:
max_iteration_breaches:
auto_merge_incidents:
unsupported_authority_blocks:
duplicate_documents_avoided:
manual_corrections_required:
incident_count:
average_paths_changed:
```

## 12. Kill or suspend criteria

Suspend the runner immediately if it:

- writes to a default or backup branch;
- exceeds two iterations;
- processes more than one Issue per run;
- opens non-draft PRs without explicit approval;
- merges automatically;
- misses a broken canonical pointer that Canary should detect;
- creates new Skills or engines to solve a one-off task;
- changes market thresholds, scoring or portfolio logic;
- hides a failed verifier;
- creates more archive inflation or manual correction than the prior workflow;
- cannot demonstrate useful output after the pilot gate.

## 13. Current authority status

```yaml
control_loop_version: 0.1
status: CANONICAL_OPERATIONAL_PILOT
new_skill_created: NO
active_skill_count_changed: NO
new_engine_created: NO
market_logic_changed: NO
thresholds_changed: NO
score_changed: NO
portfolio_authority_added: NO
auto_merge_enabled: NO
max_iterations: 2
max_issues_per_run: 1
scheduled_runner_authorized: YES_ONE_NARROW_PILOT
weekly_canary_authorized: YES
```
