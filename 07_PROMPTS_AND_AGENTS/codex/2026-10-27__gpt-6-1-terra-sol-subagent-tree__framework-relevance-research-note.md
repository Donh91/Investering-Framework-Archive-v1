# GPT-6.1 Terra / Sol Agent Tree — Framework Relevance Audit

**Date:** 2026-10-27  
**Classification:** SOURCE-VERIFIED RESEARCH NOTE / OPTIMIZATION CANDIDATE, NOT AN ACTIVE CONFIGURATION  
**Domain:** Existing Codex / API model routing and bounded execution  
**Relevance:** HIGH (8.5/10 as a *research candidate*, not a verified performance gain)  
**Source prompt:** User-provided X post / screenshot on 2026-10-27 describing a Sol high coordinator, Terra low explorers/researchers and Terra xhigh worker, with `fork_turns`-based context isolation. Original X post URL not supplied. Treat its assertions as third-party claims until verified.

## What is verified from primary documentation

1. OpenAI announced `gpt-6.1-terra` on 2026-10-26, usable via OpenAI API and rolling out in Codex / ChatGPT Work.
2. Standard API listed prices at review date: Terra $1/M input, $0.05/M cached input, $5/M output; Sol $2/M input, $0.10/M cached input, $10/M output. Nominal per-token Terra cost is 50% of Sol. Actual end-to-end cost per successful task is NOT necessarily halved.
3. OpenAI reports Terra completing certain computer-use / agent evaluations >3x faster than Sol/Astra. This is NOT a measured 3x speedup for this repository, for all coding tasks, or for Codex subagents specifically.
4. Terra has made a major coding improvement; OpenAI still identifies Sol/Astra as preferred for hardest software engineering tasks.
5. Responses API multi-agent documentation describes `fork_turns` as determining **how much conversation context is passed to a child**. The X claim that omitted/`all` **necessarily overrides explicitly configured child model/effort with Sol/high** is not substantiated by the primary docs reviewed. Different orchestration surfaces (Codex custom agents, Agents API, Responses multi-agent) may have different config and inheritance semantics. Do not assume compatibility or treat this as a settled bug.
6. OpenAI's Responses multi-agent beta describes children sharing the request's model and tools; do not assume that a mixed Sol/Terra model tree works on that surface without a demonstrated provider-supported route. In a separate agent/session orchestration surface, explicitly pinned model and effort must be verified by runtime trace, not merely named in `AGENTS.md`.

## Relevance to existing Investering architecture

**Most useful execution mapping:**

- **Sol high coordinator / independent final synthesis:** difficult diagnosis, scoping, scientific/methodology review and risk-aware integration; use existing owner paths only. Independent review and actual tests still required for consequential writes.
- **Terra low read-only explorer / researcher:** map affected files, reproduce known failures, inspect documentation, produce evidence pointers and minimal patches/specifications without writing.
- **Terra medium/high bounded worker:** implement well-defined changes and run tests in an existing task branch. Try xhigh only when measured gains justify the extra reasoning; xhigh is not automatically the economical default.
- **Deterministic no-model tooling or Luna:** remain first choice for mechanical repeated checks, source snapshots and simple classifications. Avoid paying Terra for tasks already handled reliably by scripts.
- **Sol/Astra escalation:** reserved for ambiguous root cause, multi-repository semantical conflicts, safety-critical tests, scientific falsification or after two genuinely different failed worker repair attempts on the same fingerprint. Do not generate endless retry/review cycles.

**High-priority relevance:**
1. Existing cross-repo PR remediation / closure (owner #1156). Cost per genuinely RESOLVED issue, not number of spawned agents or PRs.
2. Task 2 (#1596): deterministic point-in-time provenance, timestamp/cluster dedup, leakage controls, frozen experiment comparisons, science review. **A stronger model does not relax eligibility, first-known or baseline gates.**
3. Existing API agent/gateway routing: inspect current `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`, `API_TASK_REGISTRY_v1.json`, `API_INTELLIGENCE_POLICY_v2.json` and actual runtime receipts.
4. Site, Compass, CN: low-risk bounded code/test repair only, no source-authority, forecast-semantic or stale/degraded-status changes by a subagent.

**Concrete current code observation, not a complete registry audit:** `scripts/api_agent/api_gateway.py` has a cost table with `gpt-6.1-sol`, `gpt-6-sol`, `gpt-5.6-terra` and legacy values, but does not include `gpt-6.1-terra` as of this reading. `scripts/api_agent/meme_alpha_runtime.py` and `scripts/api_agent/pdlt_gateway.py` also contain legacy model/pricing references. Do NOT change estimated pricing or active routes without matching runtime configuration, source of pricing, compatibility tests and owner-authorized change control.

## Safe qualification experiment, reuse existing owners and scoreboards

Do **not** create a new supervisor, scheduler, research pipeline, authority plane, queue, autonomous merge policy or standing API spend. Route any implementation proposal through existing model routing / #1156 and improvement evidence through existing #1157 Adaptive Evolution Scoreboard.

Pre-register before experimentation:
- **Baseline A:** current production/qualified routing and exact task pack, frozen commit + task fingerprint.
- **Challenger B:** mixed Sol/high coordinator, Terra/low read-only, Terra/medium or xhigh bounded worker only if the chosen execution harness supports independently pinned child models/effort.
- **Control C:** one Sol/high agent where delegation adds no independent value; plus deterministic/no-model baseline for mechanical tasks.
- Same frozen cases with at least: easy PR, deterministic CI fix, multi-file code defect, Task 2 negative control, stale-data or PIT failure, and a blocked-authority case.
- Capture actual model ID, effort, effective per-agent config, `fork_turns`, input/output/cached/reasoning tokens, retries, end-to-end USD, wall time, changed files, positive/negative tests, exact-head review, merge/closure outcome, and natural producer/consumer readback where required.
- **Primary endpoint:** verified correctly RESOLVED cases per total dollar (or dollars per verified RESOLVED case), with no loss of correctness; latency and token usage secondary.
- Critical safety floors: zero unapproved authority change, zero private-data spill, zero provenance/PIT regression, zero unsupported self-merge, zero falsified success. Record blocked outcomes as blocked, not resolved.
- **Stop:** recurring same-fingerprint failure twice => escalate to Sol or owner; no speculative third retry without new evidence.
- **Decision:** ADOPT / REVISE_ONCE / RETAIN_UNPROVEN / REJECT based on outcome rows and existing governance, not headline benchmarks.

## Hard boundaries

- No new Codex agent definitions, changes to `AGENTS.md`, production model switching, API budget changes, supervisor handback, PR merges or new automation are authorized by *this note*.
- Codex/Work allowances and API billed usage are separate. Never treat a Codex prompt as evidence that an API mission was executed or charged, and do not switch host mode implicitly.
- Continue existing public canonical vs private restricted data separation. Root `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, current owner/task/queue and exact GitHub protections outrank this research note.
- Historical model-route source code is evidence, not necessarily actual active runtime; confirm effective config and execution receipts before proposing a migration.

## Primary source links reviewed on 2026-10-27

- OpenAI launch: https://openai.com/index/introducing-gpt-6-1-terra/
- OpenAI release notes: https://help.openai.com/en/articles/9624314-model-release-notes
- API model directory: https://developers.openai.com/api/docs/models
- Agents API multi-agent: https://developers.openai.com/api/docs/guides/agents-api/multi-agent
- Responses API multi-agent and `fork_turns`: https://developers.openai.com/api/docs/guides/responses-multi-agent
- Agent configuration: https://developers.openai.com/api/docs/guides/agents-api/configuration

## Existing framework anchors

- `AGENTS.md` (root governance and Codex release safeguards)
- `07_PROMPTS_AND_AGENTS/README.md` (role separation, qualification rather than new prompt inflation)
- `research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md`
- `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`
- `research/api_agent/API_TASK_REGISTRY_v1.json`
- `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`
- Issues #1156 (repair owner), #1157 (measured improvement), #1596 (Task 2)

**Archive verdict:** retain as a bounded, falsifiable model-routing hypothesis. Do not directly import the social post's ready-made agent tree into active operations.
