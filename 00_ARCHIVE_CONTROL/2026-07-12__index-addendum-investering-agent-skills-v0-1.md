# Index Addendum - Investering Agent Skills v0.2

**Date:** 2026-07-12  
**Status:** CANONICAL_INDEX_ADDENDUM  
**Scope:** repository-wide agent instructions, skill routing, prospective evidence lifecycle, write hardening and pilot governance

Read these files for repository-aware agent work:

```text
AGENTS.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/prospective-evidence-ledger/SKILL.md
.agents/skills/archive-governance/SKILL.md
.agents/skills/research-lab-red-team/SKILL.md
```

## Active stack

```yaml
stack_version: 0.2
stack_status: PILOT_ACTIVE_HARDENED
skills_active:
  - canonical-context-router
  - prospective-evidence-ledger
  - archive-governance
  - research-lab-red-team
stack_qualified_uses_completed: 1
prospective_evidence_ledger_qualified_uses: 0
review_gate: 10_qualified_uses_OR_2026-08-09
```

## Binding interpretation

```text
Skills = procedure
Canonical files = current truth
Automations = timing
Ledgers = evidence and accountability
Validators = row and coverage integrity
Governance = promotion and authority
```

Skills do not receive market, portfolio, promotion or scoring authority.

## Default read and execution order

For general work:

```text
AGENTS.md
-> CANONICAL_INDEX.md
-> INDEX_ADDENDUM_REGISTRY.md
-> ARCHIVE_MAP_AND_ROUTING.md
-> SKILL_REGISTRY.md
-> relevant SKILL.md
-> current domain owner files
-> task execution
-> archive-governance before writes
```

For active test and ledger work:

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing domain validator or scorer
-> research-lab-red-team only for interpretation or promotion review
-> archive-governance before writes
```

## Prospective Evidence Ledger v0.1

The Skill governs prospective evidence-row lifecycle for already registered tests and owner-defined ledgers.

It may:

- resolve the active test and ledger owner;
- verify causal pre-registration;
- protect frozen input fields;
- determine outcome maturity;
- verify source lineage;
- detect duplicates and event-window overlap;
- delegate to existing validators and scorers;
- report owner-defined coverage deltas.

It may not:

- create a test, engine, schema, ledger or scoring method;
- rewrite a frozen forecast after outcomes;
- count a source row as an outcome row;
- treat validator or coverage PASS as edge;
- promote a rule;
- make a market call or portfolio action;
- create recurring automation.

Required result separation:

```yaml
row_validity:
coverage_readiness:
edge_or_promotion_status:
```

## v0.1.1 write hardening controls retained

```text
EXPLICIT_BRANCH_ON_EVERY_WRITE: REQUIRED
DEFAULT_BRANCH_WRITE: FORBIDDEN
BACKUP_BRANCH_AS_WORKSPACE: FORBIDDEN
PLACEHOLDER_OR_TOOL_PROBE_FILE: FORBIDDEN
ADDENDUM_REGISTRATION: REQUIRED
REMEDIATED_WRITE_INCIDENT: PARTIAL_REMEDIATED, not PASS
PRE_MERGE_BACKUP_EQUALS_POST_MERGE_BACKUP: NO
```

## Current constraints

- no new engine;
- no new shadow layer;
- no new test or ledger from this Skill;
- no live market thresholds copied into Skills;
- no automatic portfolio action;
- no automatic scheduling;
- no write without explicit user intent;
- no write without an explicit verified non-default task branch;
- no direct push to canonical `main`;
- no direct `CANONICAL_INDEX.md` modification without the high-impact safepoint sequence;
- repository safety and backup governance remain binding.

## Pilot specification

```text
07_PROMPTS_AND_AGENTS/github_agent/skill_evals/2026-07-12__prospective-evidence-ledger-v0-1__eval-cases.md
```

The new Skill is reviewed after 10 qualified stack uses or 2026-08-09, whichever occurs first, and requires at least three real uses before a KEEP decision is justified.

## Discoverability note

This addendum remains the safe discovery pointer for the Skill stack. It is registered in `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.

`CANONICAL_INDEX.md` is not modified by this implementation because direct index changes remain high-impact operations under the repository safety policy.
