# Investering Agent Skills v0.1.1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** agent workflows / repository operating layer / reproducibility  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Related folders:** `.agents/skills/`, `00_ARCHIVE_CONTROL/`  
**Depends on:** `AGENTS.md`, Canonical Archive Index, Index Addendum Registry, Archive Map and Routing, GPT-5.6 Fresh Eyes Audit, Repository Safety and Backup Policy  
**Supersedes:** v0.1 behavior where contradicted by the v0.1.1 hardening controls in this owner

## 1. Executive decision

Investering Agent Skills v0.1.1 is the active hardened pilot operating layer for repository-aware agents.

It is not:

- a new framework engine;
- a new shadow layer;
- a market model;
- a source of live thresholds;
- an automation scheduler;
- a portfolio-action system;
- evidence of trading edge.

It converts repeated repository procedures into on-demand, version-controlled instructions.

```yaml
stack_version: 0.1.1
status: PILOT_ACTIVE_HARDENED
skills: 3
qualified_uses: 1
trading_logic_changed: NO
framework_authority_changed: NO
new_engine_created: NO
new_shadow_layer_created: NO
new_score_created: NO
```

## 2. Problem addressed

The repository contains strong canonical governance, but agents can still fail operationally by:

- reading old files before current owner files;
- overlooking valid index addenda not directly listed in the canonical index;
- reactivating superseded rules;
- treating source material as doctrine;
- creating duplicate canonical documents;
- archiving entire discussions instead of durable learning;
- promoting explanatory research without rows;
- relying on a connector default and writing to `main`;
- creating placeholder files while probing tool behavior;
- overstating targeted or pre-merge backup coverage;
- relying on conversation memory instead of GitHub state.

The Skill layer addresses procedure, not market intelligence.

## 3. Architecture

```text
Canonical repository files
= current truth and authority

CANONICAL_INDEX.md
= primary canonical navigation

INDEX_ADDENDUM_REGISTRY.md
= low-impact discovery for valid addenda

AGENTS.md
= repository-wide non-negotiable operating rules

SKILL_REGISTRY.md
= active skill inventory, routing and pilot governance

.agents/skills/*/SKILL.md
= task-specific procedures loaded when relevant

GitHub branches and pull requests
= reviewed execution and receipts
```

Default composition:

```text
canonical-context-router
-> task reasoning or extraction
-> research-lab-red-team when a claim or change is evaluated
-> archive-governance before repository writes
```

## 4. Implemented files

```text
AGENTS.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/archive-governance/SKILL.md
.agents/skills/research-lab-red-team/SKILL.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md
00_ARCHIVE_CONTROL/2026-07-12__index-addendum-investering-agent-skills-v0-1.md
```

## 5. Skill responsibilities

### canonical-context-router

Resolves:

- task domain;
- current canonical owner;
- highest active version;
- operational runtime registry;
- directly index-listed addenda;
- registry-discoverable addenda;
- relevant ledgers;
- explicit overrules;
- unresolved conflicts.

It is read-only and cannot make portfolio decisions or write files.

### archive-governance

Controls:

- archive-worthiness;
- existing-owner search;
- create versus update versus append;
- placement and naming;
- status classification;
- explicit branch assertion before every write;
- branch and PR workflow;
- high-impact safepoint requirements;
- index versus index-addendum decisions;
- addendum registry maintenance;
- incident-aware result classification;
- backup-product and frozen-SHA truth;
- read-back and diff validation.

It cannot write without explicit user intent.

### research-lab-red-team

Tests:

- evidence class;
- decision divergence;
- false-positive and false-negative cost;
- baselines;
- redundancy;
- falsifiers;
- promotion and kill criteria;
- authority boundaries;
- new-engine-freeze compliance.

It cannot self-promote findings or create live execution authority.

## 6. Why only three skills

The framework is under an active simplify-before-expanding and new-engine freeze.

The first skill set therefore targets the highest-frequency operational failure modes:

1. wrong or incomplete context;
2. wrong archive behavior;
3. unsupported framework promotion.

DATA PING execution, weekly range audit, Master Monday and Cycle Navigator publication are not built in v0.1.1.

They remain possible later candidates only after the first stack demonstrates measurable value.

## 7. v0.1.1 hardening

The first qualified archive-governance run successfully found an existing owner, avoided a duplicate, preserved negative research evidence and used an existing index addendum. It also exposed four control gaps.

### 7.1 Explicit branch assertion

Before every write call:

```yaml
target_branch_explicitly_supplied: REQUIRED
target_branch_verified_to_exist: REQUIRED
target_branch_is_default_branch: MUST_BE_NO
target_branch_is_backup_branch: MUST_BE_NO
```

Missing verification produces `WRITE_BRANCH_UNVERIFIED`.

Connector-default branch behavior is forbidden. Placeholder and tool-probe files are forbidden in production repositories.

### 7.2 Incident-aware scoring

A remediated write incident cannot receive an unqualified write-governance `PASS`.

Required separation:

```yaml
archive_content_result: PASS | PARTIAL | FAIL
write_governance_result: PASS | PARTIAL_REMEDIATED | FAIL
final_repository_state: PASS | PARTIAL | FAIL
incident_count:
remediation_commits:
```

### 7.3 Addendum registry

`INDEX_ADDENDUM_REGISTRY.md` is now read after the canonical index.

It improves discoverability without forcing frequent high-impact modifications to `CANONICAL_INDEX.md`. A registry row remains navigation only and does not grant authority.

### 7.4 Backup-scope truth

Every backup claim must distinguish:

```text
backup product
snapshot frozen source SHA
current owner or merge SHA
whether the current version is inside the snapshot
post-merge delta status
```

A pre-merge targeted snapshot may protect the research package while leaving the later owner update pending backup.

## 8. How it works across environments

### Repository-aware coding agents

Agents that support repository-local skills can discover `.agents/skills/` and load a matching `SKILL.md` on demand.

### ChatGPT with GitHub access

The same procedures can be read directly from GitHub and followed as repository runbooks. Automatic trigger behavior may differ by product surface, but the files remain the shared procedure source.

### Claude or other agents

The skill files can be provided as project instructions or read from the repository. Current canonical owner files still outrank the skills.

## 9. Authority boundary

```text
Skills define how to work.
Canonical files define what is true.
Automations define when work runs.
Ledgers show whether it worked.
```

A Skill must never copy live market rules and become a parallel doctrine source.

If a canonical owner changes, the Skill should continue pointing to the owner rather than requiring duplicated threshold updates.

## 10. Write safety

The active implementation requires:

- isolated task branch;
- explicit branch argument on every write;
- branch existence verification;
- no default or backup branch as target;
- no direct push to `main`;
- no placeholder or tool-probe files;
- no force operation;
- no hidden deletion;
- no workflow or security modification without high-impact governance;
- no direct `CANONICAL_INDEX.md` change without the safepoint and vault sequence;
- pull request and read-back validation.

## 11. First live-run learning

The first qualified use is recorded at:

```text
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-12__archive-governance-full-sensor-backtest__receipt.md
```

Corrected result:

```yaml
archive_content_result: PASS
context_routing: PASS
duplicate_avoidance: PASS
authority_boundary: PASS
write_governance_result: PARTIAL_REMEDIATED
final_repository_state: PASS
incident_count: 1
research_package_backup: PASS_TARGETED_RESEARCH_SNAPSHOT
current_owner_version_in_snapshot: NO
post_merge_delta_status: PENDING
```

The incident is retained as pilot evidence and is not hidden by the clean final repository state.

## 12. Pilot evaluation

Review after 10 qualified tasks or 2026-08-09, whichever occurs first.

Primary metrics:

- correct trigger;
- correct owner files found;
- valid addenda found;
- legacy-as-current errors;
- duplicate documents avoided;
- unsupported promotions blocked;
- explicit branch assertion;
- write incidents;
- manual corrections required;
- backup-scope accuracy;
- final repository state.

Review states:

```text
KEEP
MODIFY
SUSPEND
KILL
```

## 13. Kill criteria

The stack or individual skills must be modified, suspended or killed if they:

- create parallel truth;
- repeatedly route to old authority;
- miss valid registered addenda;
- increase archive inflation;
- silently alter framework behavior;
- infer missing data;
- create unsupported promotions;
- write without explicit user intent;
- omit the explicit task branch;
- create placeholder files in production repositories;
- overstate backup coverage;
- conflict with repository safety;
- fail to reduce manual correction after the pilot gate.

## 14. Expansion gate

A new skill requires a demonstrated repeated workflow gap, explicit inputs and outputs, a validation loop, an authority boundary and a kill criterion.

No skill is added merely because the workflow could theoretically be automated.

## 15. Expected benefit

The expected value is operational consistency:

- less context reconstruction;
- fewer version and addendum-discovery errors;
- fewer duplicate documents;
- safer GitHub writes;
- stronger cross-agent continuity;
- more reproducible Research Lab classification;
- accurate incident and backup reporting;
- clearer separation between procedure and framework truth.

No improvement in market performance is claimed from the infrastructure alone.
