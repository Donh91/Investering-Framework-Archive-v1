# Index Addendum - Investering Agent Skills v0.1.1

**Date:** 2026-07-12  
**Status:** CANONICAL_INDEX_ADDENDUM  
**Scope:** repository-wide agent instructions, skill routing, write hardening and pilot governance

Read these files for repository-aware agent work:

```text
AGENTS.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/archive-governance/SKILL.md
.agents/skills/research-lab-red-team/SKILL.md
```

## Active stack

```yaml
stack_version: 0.1.1
stack_status: PILOT_ACTIVE_HARDENED
skills_active:
  - canonical-context-router
  - archive-governance
  - research-lab-red-team
qualified_uses_completed: 1
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
-> INDEX_ADDENDUM_REGISTRY.md
-> ARCHIVE_MAP_AND_ROUTING.md
-> SKILL_REGISTRY.md
-> relevant SKILL.md
-> current domain owner files
-> task execution
-> archive-governance before writes
```

## v0.1.1 hardening controls

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
- no live market thresholds copied into skills;
- no automatic portfolio action;
- no automatic scheduling;
- no write without explicit user intent;
- no write without an explicit verified non-default task branch;
- no direct push to canonical `main`;
- no direct `CANONICAL_INDEX.md` modification without the high-impact safepoint sequence;
- repository safety and backup governance remain binding.

## First live-run interpretation

```yaml
archive_content_result: PASS
write_governance_result: PARTIAL_REMEDIATED
final_repository_state: PASS
incident_count: 1
research_package_backup: PASS_TARGETED_RESEARCH_SNAPSHOT
current_owner_version_in_snapshot: NO
post_merge_delta_status: PENDING
```

The live-run receipt is:

```text
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-12__archive-governance-full-sensor-backtest__receipt.md
```

## Discoverability note

This addendum remains the safe discovery pointer for the Skill stack. It is also registered in `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.

`CANONICAL_INDEX.md` is not modified by this hardening patch because direct index changes remain high-impact operations under the repository safety policy.
