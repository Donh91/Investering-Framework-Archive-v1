# Index Addendum - Investering Agent Control Loop v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_ADDENDUM  
**Område:** agent workflows / automation / integrity  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Owner:** `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__agent-control-loop-v0-1__canonical.md`  
**Depends on:** `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`

## Purpose

Make the narrow Agent Control Loop v0.1 pilot discoverable without changing `CANONICAL_INDEX.md`.

## Authorized exception

`00_ARCHIVE_CONTROL/SKILL_REGISTRY.md` v0.2 states that automated agent loops are not authorized for build.

This addendum creates one narrower, later and explicit exception:

```text
AUTHORIZED:
- one scheduled Agent Queue Runner;
- maximum one GitHub Issue per run;
- maximum two implementation-verification iterations;
- existing Skills only;
- task branch only;
- draft PR only;
- no auto-merge;
- no market, threshold, scoring, promotion or portfolio authority;
- weekly read-only Framework Integrity Canary.

NOT AUTHORIZED:
- generic self-improvement loops;
- autonomous architecture expansion;
- unbounded subagents;
- automatic rule or threshold tuning;
- automatic canonical promotion;
- automatic portfolio action;
- additional new Skills.
```

The exception is a workflow pilot, not a fifth Skill.

## Owner paths

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__agent-control-loop-v0-1__canonical.md
07_PROMPTS_AND_AGENTS/github_agent/tools/framework_integrity_canary.py
07_PROMPTS_AND_AGENTS/github_agent/schemas/agent-run-state.schema.json
07_PROMPTS_AND_AGENTS/github_agent/templates/agent-run-receipt-template.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__agent-queue-runner-prompt-v0-1__operational.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__research-intake-workflow-v0-1__operational.md
.github/ISSUE_TEMPLATE/investering-agent-command.yml
```

## Review and supersession

Review after 10 queue runs or 2026-08-09, whichever occurs first.

If the pilot is suspended or superseded, this addendum must be updated in `INDEX_ADDENDUM_REGISTRY.md`.
