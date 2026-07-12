# Investering Agent Skills v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** agent workflows / repository operating layer / reproducibility  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Related folders:** `.agents/skills/`, `00_ARCHIVE_CONTROL/`  
**Depends on:** `AGENTS.md`, Canonical Archive Index, Archive Map and Routing, GPT-5.6 Fresh Eyes Audit, Repository Safety and Backup Policy  
**Supersedes:** no framework rule; this adds a thin operational layer only

## 1. Executive decision

Investering Agent Skills v0.1 is approved as a small pilot operating layer for repository-aware agents.

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
stack_version: 0.1
status: PILOT_ACTIVE
skills: 3
trading_logic_changed: NO
framework_authority_changed: NO
new_engine_created: NO
new_shadow_layer_created: NO
new_score_created: NO
```

## 2. Problem addressed

The repository contains strong canonical governance, but agents can still fail operationally by:

- reading old files before current owner files;
- reactivating superseded rules;
- treating source material as doctrine;
- creating duplicate canonical documents;
- archiving entire discussions instead of durable learning;
- promoting explanatory research without rows;
- forgetting repository safety before writes;
- relying on conversation memory instead of GitHub state.

The Skill layer addresses procedure, not market intelligence.

## 3. Architecture

```text
Canonical repository files
= current truth and authority

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
- relevant addenda and ledgers;
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
- branch and PR workflow;
- high-impact safepoint requirements;
- index versus index-addendum decisions;
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

1. wrong context;
2. wrong archive behavior;
3. unsupported framework promotion.

DATA PING execution, weekly range audit, Master Monday and Cycle Navigator publication are not built in v0.1.

They remain possible later candidates only after the first stack demonstrates measurable value.

## 7. How it works across environments

### Repository-aware coding agents

Agents that support repository-local skills can discover `.agents/skills/` and load a matching `SKILL.md` on demand.

### ChatGPT with GitHub access

The same procedures can be read directly from GitHub and followed as repository runbooks. Automatic trigger behavior may differ by product surface, but the files remain the shared procedure source.

### Claude or other agents

The skill files can be provided as project instructions or read from the repository. Current canonical owner files still outrank the skills.

## 8. Authority boundary

```text
Skills define how to work.
Canonical files define what is true.
Automations define when work runs.
Ledgers show whether it worked.
```

A Skill must never copy live market rules and become a parallel doctrine source.

If a canonical owner changes, the Skill should continue pointing to the owner rather than requiring duplicated threshold updates.

## 9. Write safety

The implementation follows repository policy:

- isolated task branch;
- no direct push to `main`;
- no force operation;
- no deletion;
- no workflow or security modification;
- no change to `CANONICAL_INDEX.md` in v0.1;
- discoverability provided through a canonical registry and index addendum;
- pull request and read-back validation required.

Changing the canonical index directly remains a high-impact operation and must follow the immediate safepoint and vault contract.

## 10. Pilot evaluation

Review after 10 qualified tasks or 2026-08-09, whichever occurs first.

Primary metrics:

- correct trigger;
- correct owner files found;
- legacy-as-current errors;
- duplicate documents avoided;
- unsupported promotions blocked;
- manual corrections required;
- write-validation result.

Review states:

```text
KEEP
MODIFY
SUSPEND
KILL
```

## 11. Kill criteria

The stack or individual skills must be modified, suspended or killed if they:

- create parallel truth;
- repeatedly route to old authority;
- increase archive inflation;
- silently alter framework behavior;
- infer missing data;
- create unsupported promotions;
- write without explicit user intent;
- conflict with repository safety;
- fail to reduce manual correction after the pilot gate.

## 12. Expansion gate

A new skill requires a demonstrated repeated workflow gap, explicit inputs and outputs, a validation loop, an authority boundary and a kill criterion.

No skill is added merely because the workflow could theoretically be automated.

## 13. Expected benefit

The expected value is operational consistency:

- less context reconstruction;
- fewer version errors;
- fewer duplicate documents;
- safer GitHub writes;
- stronger cross-agent continuity;
- more reproducible Research Lab classification;
- clearer separation between procedure and framework truth.

No improvement in market performance is claimed from the infrastructure alone.
