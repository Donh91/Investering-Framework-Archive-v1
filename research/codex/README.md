# Codex control-plane observability

This folder is the durable research-to-Codex intake and execution-observability surface.

Machine authority remains `LATEST_CODEX_READY_TASKS.json` at repository root.

## Cross-repository preflight

Codex must read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json` before any task involving source data, provenance or Round 3. If reproduction needs restricted evidence, Codex must also read the authorized immutable binding in `Donh91/secrets`.

Restricted payloads and normalized private values must never be pasted into a public candidate, issue, PR, test fixture, log or completion receipt. Public code-remediation evidence uses private commit/path/bytes/SHA-256/source-contract/time/schema/completeness bindings. Credentials remain in the credential plane. If access is unavailable, return `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` instead of fabricating a public fixture.

Read order for Codex work:

1. `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`
2. `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`
3. `LATEST_CODEX_READY_TASKS.json`
4. `LATEST_CODEX_EXECUTION_STATE.json`
5. `research/codex/LATEST_CODEX_INTAKE_STATUS.json`
6. `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
7. exact candidate, transition/completion receipt, PR, commit, workflow run and tests

Research candidates are stored under `research/codex/intake/YYYY/MM/` and must satisfy `CODEX_RESEARCH_CANDIDATE.schema.json`.

A merged candidate triggers the non-writing `codex-intake-dispatch.yml` path listener, which immediately dispatches the guarded Remediation Maturation Controller on `main`. The main writer itself remains free of push triggers. The normal twice-daily schedule is only reconciliation/recovery cadence, not a waiting requirement for research intake.

Research threads may submit evidence but cannot declare `CODEX_READY`. The controller may classify a candidate as `CODEX_READY`, `NEEDS_MORE_EVIDENCE`, `DEDUPED_TO_HEALTH_TASK` or `REJECTED`.

Standalone research tasks bind fresh state under `research/codex/transitions/`. Verified completion receipts live under `research/codex/completions/`.

Full agent instructions: `.agents/skills/codex-intake/SKILL.md`.
Full operational contract: `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`.
