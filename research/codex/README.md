# Codex control-plane observability

This folder is the durable research-to-Codex intake and execution-observability surface.

Machine authority remains `LATEST_CODEX_READY_TASKS.json` at repository root.

Read order for Codex work:

1. `LATEST_CODEX_READY_TASKS.json`
2. `LATEST_CODEX_EXECUTION_STATE.json`
3. `research/codex/LATEST_CODEX_INTAKE_STATUS.json`
4. `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
5. exact candidate, transition/completion receipt, PR, commit, workflow run and tests

Research candidates are stored under `research/codex/intake/YYYY/MM/` and must satisfy `CODEX_RESEARCH_CANDIDATE.schema.json`.

A merged candidate triggers the Remediation Maturation Controller immediately through a path-restricted `push` trigger. The normal twice-daily schedule is only reconciliation/recovery cadence, not a waiting requirement for research intake.

Research threads may submit evidence but cannot declare `CODEX_READY`. The controller may classify a candidate as `CODEX_READY`, `NEEDS_MORE_EVIDENCE`, `DEDUPED_TO_HEALTH_TASK` or `REJECTED`.

Standalone research tasks bind fresh state under `research/codex/transitions/`. Verified completion receipts live under `research/codex/completions/`.

Full agent instructions: `.agents/skills/codex-intake/SKILL.md`.
Full operational contract: `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`.
