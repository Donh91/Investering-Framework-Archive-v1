---
name: research-parallel-lanes
description: 'Coordinate multiple bounded, independent research tracks in one Investering conversation and, when available, in parallel read-only GitHub Actions jobs or existing authorized AI-agent lanes. Use for explicit Research Parallel Lanes, parallel deep research, Task 2 multi-track studies, 5-10 research tracks, or a request to repeat the Ironflow parallel-job method. Does not create agents, workflows, schedules, API authorization, new reviewers or trading authority by itself.'
---

# Research Parallel Lanes v1.0 (repository-local, explicit invocation)

## Purpose and repeatable entrypoint

Turn one large research objective into **2-10 falsifiable research tracks** whose outputs can be read and synthesized in **the same conversation**. Optimize real progress, not agent count. One lead thread owns the objective, source snapshot, synthesis and completion claim. Multiple independent jobs may execute concurrently where a real runtime supports it; multiple independent **AI agents** exist only when an authorized, verifiably callable agent runtime is separately invoked. A GitHub job is not an AI agent, a GitHub PR is not an agent execution, and multiple tracks in a chat are not proof of parallel execution.

Owner shortcut in another repository-aware thread:

> **Kør Research Parallel Lanes v1 på [originalt domæne/issue]. Brug [N] uafhængige spor, genbrug eksisterende ejere og data, paralleliser kun faktiske jobs, valider output, syntetiser alle spor og log i det oprindelige arkiv. Ingen nye automations.**

Canonical method: `.agents/skills/research-parallel-lanes/SKILL.md`; discovery: `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`. This is **not** an automatically installed ChatGPT-wide skill. The chat must actually fetch the repository file, and GitHub Actions/AI runtimes must be connected and separately authorized to do work.

## Activation and nontriggers

- **Explicit trigger:** `Research Parallel Lanes`, `/research-parallel-lanes`, `parallel research`, `flere forskningsspor i samme tråd`, `10 dybe spor`, or explicit reference to Ironflow's two/three independent Actions jobs. Require a substantial research objective, multiple materially different hypotheses and one existing scientific owner.
- **Do not invoke** for a quick factual answer, plain status, routine DATA PING, one small code fix, ordinary PR merge, current market signal, request for new automation, or a generic list of ideas without intent to research. Do not split a task merely to produce more tracks.
- **No implicit invocation**: this candidate can initiate research/PR writes only under **existing explicit owner approval, verified non-default branch, budget and repository governance**. User's invocation is not GitHub/paid API permission when existing owners require extra gates.

## Preflight: one mission, no duplicate control plane

1. Read `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, current cockpit, `canonical-context-router`, `SKILL_REGISTRY.md`, and exact existing task/PR/Research Lab owner. Respect the current repository rules, restricted/private vs public data plane and locked Round 3 analysis firewall.
2. Inventory the existing experiments, queues, recurring jobs, source manifests and prior negative results. Do not create a new supervisor/strategist, scheduling service, canonical engine, research owner, agent identity, private source mirror, secrets or parallel writer. Prefer adding distinct jobs to **one already-owned PR workflow** over many new workflows. If no workflow is needed, use multiple direct independent tool reads in the thread.
3. Freeze the mission's decision question, no-skill/simplest incumbent baseline, data class, source **first-known time**, temporal clock, shared immutable snapshot, allowed writes, maximum money/minutes, main release boundary and concrete stop criterion **before** viewing outcomes. Distinguish `OUTCOME_TRUTH` from `ORIGINAL_PIT_FEATURE`.
4. Choose 2-10 **independent questions**, not ten correlated rephrasings. One lane per hypothesis, explicit falsifier, owner, raw inputs, baseline, destination, max duration, budget and failure condition. A **serial dependency** stays serial: source qualification before modelling, observation maturity before scoring, synthesis after results. Do not fork mutually dependent work merely to show parallelism.
5. Persist a small `RESEARCH_PARALLEL_LANES_V1` plan in the original domain's research folder only if warranted and authorized. Example: `references/EXAMPLE_MISSION.json`; deterministic validator: `scripts/research/validate_parallel_research_manifest_v1.py`. This plan is **coordination metadata only**, not a new queue/scheduler or permission manifest.

## Three real execution modes

### A. Parallel investigation from one chat (default, no GitHub job necessary)
Call independent connected read-only tools concurrently where supported, inspect their receipts, then synthesize here. If tools execute sequentially, mark execution `SERIAL_TOOL_CALLS`; do not call it parallel agents. The model is still one coordinating assistant, not multiple separately running AI minds. Do not promise background work after this turn.

### B. Parallel GitHub Actions jobs (Ironflow-proven pattern)
Within an **existing authorized PR-only / on-demand** research workflow, add independent jobs or a bounded `strategy.matrix` (prefer `fail-fast: false` so one failure does not suppress other scientific evidence). GitHub launches independent runners; by default jobs run concurrently subject to its runner quota. Cap `max-parallel` based on actual account minutes, network source limits and expected compute (default research **2-4 active compute jobs**, even if the study has ten lanes). Do not launch ten identical source downloads if one shared immutable dataset or staged artifact can safely feed bounded independent jobs. Every job has read-only minimum permissions and isolated temp paths, its own logs, test receipts and artifact ID with retention class. Use `needs` only for true prerequisites; synthesis waits for all relevant results, including failures. **Actual job completion** requires GitHub run ID, job ID, conclusion, exact commit SHA, downloaded source digests and artifact readback. A green workflow alone does not prove scientific correctness.
Reference pattern: `references/GITHUB_ACTIONS_PATTERN.md`. Real precedent: Archive PR #1988 runs `public-source-replay` and `tick-hip4-source-qa` independently; #1989 added `full18m-history-walkforward`. Those are computational jobs, **not AI subagents**.

### C. Multiple actual AI researcher lanes (conditional, separately authorized)
Use only **existing connected and authorized** Research Lab/Strategist/Sol/Codex/agent routes, following their current owners, API quotas, budgets and original native execution receipts. A model requested, planned or mentioned in a prompt is **not** proof it ran. Never invent `spawn_agent` support, add a new ChatGPT automation, convert read-only GitHub Actions to an unrestricted model executor, create extra GitHub identities, or assume the chat can keep processes alive after completion. If no confirmed agent runner exists, use A or B and report `AI_AGENT_CONCURRENCY_UNAVAILABLE`. Existing shared Sol MAX runbook applies to any paid run; do not spend merely to make all lanes "AI".

## Evidence and safety boundaries

- Each track gets `lane_id`, immutable `source_snapshot_sha`, `original_owner`, `hypothesis`, `simplest_baseline`, `falsifier`, `start_time/first_known`, `outputs`, `executor_kind`, `run_and_artifact_ref`, `status`, `cost`, `claim_class` and `next`. Forbidden `PASSED` based only on source existence or PR creation.
- No new market, portfolio, trading, risk threshold, forecast or promotion authority. Read-only/shadow research is not automatically Round 3 eligible. Keep all restricted/provider-private payloads in their governed data plane, not public logs or portable prompts.
- Share **source identity** without sharing mutable outcome-labelled caches between experimental arms. Protect PIT, complete-horizon maturity, purged time-boundary labels, delisted assets, survivorship bias, slippage and same-day correlated observations when applicable.
- If a lane fails, retain `FAILED_EVIDENCED` with smallest reproducible blocker while other independent lanes complete. Never relabel a failed required lane `SUCCESS`, or pretend successful independent jobs imply an overall PASS.
- Put output in its original owner archive using a compact **lane ledger + synthesis** with immutable links. `COMPLETE_VERIFIED` requires actual evidence readback. Failed, null and contradictory findings have equal right to survive. The lead must describe which lanes were **not performed**.
- For changes, follow `archive-governance`, explicit non-default branch, exact-HEAD CI, owner-approved PR merge/main blob readback, and existing S1 limits. A manual chat merge is never credited to unattended S1. Existing Supervisor may consume an owner-linked issue/PR, not a new queue.
- Avoid wasted cost: use a stop rule for each lane, no idle polling loops, and reuse deterministic computations before asking paid models. If the best answer is that a source has no incremental edge, close the test rather than force model tuning.

## Concrete end-state checklist

A qualified mission ends with one synthesis keyed to original task, counting: `PLANNED`, `RUNNING`, `COMPLETE_VERIFIED`, `FAILED_EVIDENCED`, `BLOCKED`, `NOT_EXECUTED`. Record **actual simultaneous job evidence** when claiming parallel execution. Distinguish (1) source QA, (2) simulation/replay validity, (3) prediction/causal edge, (4) economic utility and (5) production admission, never collapse them to a single green CI status.

Use `references/INVOCATION_AND_HANDOFF.md` for owner-ready prompts and a one-screen synthesis contract.

For historical 2020-2026 crisis/rotation/CN replay, also load `references/HRE_REPLAY_SOURCE_CLOCK_FAILSAFE.md`. The HRE Task2 pilot actually caught vendor intrabar `close_time` values, missing hourly buckets, 2025 timestamp-unit conversion and 72h overlapping label pseudo-independence. This is an observed **source/time safety method**, not a separately installed skill or evidence of investment edge. Before activating a replay lane freeze the native source revision, true completed-bar clock, original-vs-retrospective classification, missingness abstentions, era-specific feature availability, matched controls and interval sharpness. Reuse the existing original HRE Task2 research owner and `research/historical_reality_engine/` evidence archive, rather than creating a new research/agent owner. When work cannot actually be continued in the current tool session, leave an exact PR/issue/run/blocker handoff under existing owners, not an assertion of silent background execution.

## Validation / retire

This skill is an **operational-helper pilot**, not a proven increase in scientific edge. The independent `skill-quality-gate` compares frozen no-skill/manual-split baseline with representative Task 2, Alpha, blocked-source, data-leakage and simple-task negative cases. Required: zero permission increases, no duplicate scheduler/owner, no unsupported multi-agent or success claims, fewer duplicate source downloads, fewer missed failure receipts, bounded minutes; otherwise MODIFY_AND_RETEST or RETIRE_REVIEW. A static manifest validator and passing CI show document correctness, **not** actual multi-agent autonomy or reduced end-to-end research time.

For an **explicit Kompas Pro all-14-horizon retrospective/forward research request**, also read `references/KOMPAS_PRO_14_HORIZONS.md` and the existing Task2 v2.1 H14 research foundation and crosswalk. This specializes the same Research Parallel Lanes owner and outputs; it creates no new skill actor, model, scheduler, original horizon authority, automatic research run or production score. Do not apply it to plain current-state `Kompas` rendering.
