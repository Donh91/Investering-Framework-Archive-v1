# Index Addendum - Investering Agent Skills v0.1

**Date:** 2026-07-12  
**Status:** CANONICAL_INDEX_ADDENDUM  
**Scope:** repository-wide agent instructions, skill routing and pilot governance

Read these files for repository-aware agent work:

```text
AGENTS.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/archive-governance/SKILL.md
.agents/skills/research-lab-red-team/SKILL.md
```

## Active stack

```yaml
stack_version: 0.1
stack_status: PILOT_ACTIVE
skills_active:
  - canonical-context-router
  - archive-governance
  - research-lab-red-team
review_gate: 10_qualified_uses_OR_2026-08-09
```

## Binding interpretation

```text
Skills = procedure
Canonical files = current truth
Automations = timing
Ledgers = evidence and accountability
```

Skills do not receive market, portfolio, promotion or scoring authority.

## Default read and execution order

```text
AGENTS.md
-> CANONICAL_INDEX.md
-> ARCHIVE_MAP_AND_ROUTING.md
-> SKILL_REGISTRY.md
-> relevant SKILL.md
-> current domain owner files
-> task execution
-> archive-governance before writes
```

## Current constraints

- no new engine;
- no new shadow layer;
- no live market thresholds copied into skills;
- no automatic portfolio action;
- no automatic scheduling;
- no write without explicit user intent;
- no direct push to canonical `main`;
- no direct `CANONICAL_INDEX.md` modification in this implementation;
- repository safety and high-impact safepoint rules remain binding.

## Discoverability note

This addendum is used instead of a direct `CANONICAL_INDEX.md` modification because changing the main index is a high-impact operation under the repository safety policy. The active registry and root `AGENTS.md` provide runtime discovery without bypassing that safety gate.
