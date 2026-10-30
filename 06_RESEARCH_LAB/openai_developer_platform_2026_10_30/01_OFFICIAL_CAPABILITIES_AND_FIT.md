# 01 · Official OpenAI developer capabilities and framework fit
**Research date:** 2026-10-30; official developer/help-center references verified on date noted. This is a **source-backed feature audit**, not proof that this exact project has entitlement, deployed code or benefits.

## High-value capability map
| Feature / exact public source | Official capability, availability | Existing owner / best bounded use | Cost, threat or blocker | Decision |
|---|---|---|---|---|
| [Agents API](https://developers.openai.com/api/docs/guides/agents-api/overview) | Durable managed Codex harness, sessions, context compaction, agents/subagents, code/shell and MCP tools, resumable sessions, hosted or owned environments; app remains responsible for tools, environment, input and follow-through | **#1156 Supervisor** / existing Codex & GitHub remediation; one original-owner PR defect reproduction with offline local tests and final exact-head handoff | Model tokens + hosted sandbox + tools and retries. **US-only data residency, no Zero Data Retention**, including self-hosted Agents session. Must not send private/restricted source or keys by default. Session-completed ≠ PR merged or real producer fixed | SHADOW_BOUNDED_PILOT_ONLY |
| [Agents observability](https://developers.openai.com/api/docs/guides/agents-api/observability), [tracing](https://developers.openai.com/api/docs/guides/agents-api/tracing), [events/items](https://developers.openai.com/api/docs/guides/agents-api/sessions/events) | Session/turn events, saved tool calls and errors, agent/subagent tokens & traces; trace may arrive after answer; blank tokens UNKNOWN | Existing #1156 audit and source-to-PR-to-consumer receipt join | OpenAI tracing of managed API sessions does NOT automatically observe existing ChatGPT Work host or GitHub Actions runs. Build a **cross-identifier join** where available; missing evidence remains UNKNOWN | ADOPT_METHOD |
| [Decisions API](https://developers.openai.com/api/docs/guides/decisions) | **GA** `POST /v1/decisions`, currently `gpt-6-luna` only; typed predicate/choice/score; JSON and multi-question input; one request up to 400 questions; official ~10x faster claim NOT a framework measurement | **Existing #1760**, canonical news #1563 and router; low-stakes news severity/ownership/research triage under 60 frozen cases+20 held-out | Exact model/endpoint/org entitlement must be tested in authorized pilot. Text/input billed; **Decisions output tokens not charged**; not calibrated finance probabilities, permissions or automated SELL | SHADOW_ONLY, EXISTING_OWNER |
| [Datasets](https://developers.openai.com/api/docs/guides/evaluation-getting-started) | Evaluate prompts and outputs with quick datasets; existing Evals becoming read-only **2026-10-31** and scheduled shutdown **2026-11-30** | **Task 2 #1596** methodological/evaluator mirrors; Supervisor defects & regression examples; use only public/sanitized prospective fixtures | Dataset evaluation does NOT prove original PIT or economic market edge; unknown price/availability of datasets-specific usage must be read from current account. Avoid uploading restricted data | ADOPT_EVAL_METHOD, NOT DATA_AUTHORITY |
| [Responses API](https://developers.openai.com/api/docs/guides/text) and models | Normal stateless/stateful controlled inference and tools; existing capability router and receipts already use API | Keep existing API lifecycle/model routing; Terra for bounded complex tasks, Sol for hard critical review when justified, Luna for cheap classification | Each extra tool/model/retry and reasoning output token may add cost. No public **Astra** API use without explicit owner rule change | MAINTAIN / OPTIMIZE |
| [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | GPT-5.6+ eligible shared prefixes >=1,024 tokens; 30m write 1.25x input, read 0.1x or 0.05x for GPT-6.1 Sol/Terra; 12h write 2.5x; cache is not free | Stable AGENTS/capability tool definitions in existing API worker, changing task payload at end; measure cache hit vs full task economics | Continuous prefix churn, different model/org/region, expiry, one-off calls can make caching pointless. Do not cache sensitive data contrary to custody requirements | MEASURE THEN ADOPT |
| [Batch API](https://developers.openai.com/api/docs/guides/batch) | Async jobs, target 24h turnaround, **50% model rate discount**; supported endpoints include Responses, Chat Completions, embeddings, images | Existing Research Lab offline nonurgent classification/dedup/QA on already admitted public data | **NOT for immediate Supervisor PR closure, emergency recovery, scheduled publications or live decisions**. Separate response retrieval, expiry and cost ledger | CONDITIONAL |
| [Playground](https://platform.openai.com/playground), [Logs](https://platform.openai.com/logs), [Usage](https://platform.openai.com/usage) | Manual API prototyping, traces where instrumented, request/cost comparison and project/org filtering | Owner manual review of classifications, request IDs, missing tool outputs, model mismatch/failed review | Playground may incur real API charges; a missing log is not necessarily a zero-call event and user-visible API usage filters can hide other projects | LOW_COST_MANUAL |
| [Model pricing](https://developers.openai.com/api/docs/pricing) | Different Standard/Batch/Flex/Fast prices and cached/write rates, long-context multiplier and tool/container fees | Model routing current implementation, not new router | Do not hard-code pricing forever; check rate/capabilities/available model before work. Cost-to-complete, not cheapest per token | ADOPT_BUDGET_GOVERNANCE |

## Why Agents API is compelling yet NOT a replacement for current Supervisor
**Known failure hypothesis:** a Supervisor reports 'task done' or a model receipt appears but there is no corresponding original-owner code diff, required CI, merge, deployment and natural consumer readback. The Agents API provides **session visibility and controlled shell/tools**, but cannot manufacture genuine GitHub authority. It may actually increase risk if the same agent has PR writer, bypass and independent Vault destructive authority.

A successful P0 experiment requires **two different proofs**:
1. **Runtime proof:** exact session/turn status, event ID, model/tool calls, exit statuses, available terminal test logs, token usage including subagents/retries, allowed environment network, source hashes and actual $ invoiced or estimate provenance.
2. **Delivery proof:** original issue ID, PR ID and 40-char head SHA, code/test diffs, exact-head CI result, genuine approver/owner release authorization, merged main SHA, natural producer & downstream consumer evidence. Unmerged PR or completed turn is **NOT** delivered.

**Hard stop** on high-impact writes, credentials, private source data, external HTTP actions, unknown sandbox security, a user-approval requirement or destructive authority separation. A read-only agent prototype can gather evidence; production merges follow `AGENTS.md` and existing #1156. No double-scheduler, no new bot reviewer or unrestricted tools.

**Security note:** official Agents API supports US data residency only and is not ZDR eligible as of 2026-10-30. For the restricted `Donh91/secrets` plane do **not** submit raw data to this hosted service just because a self-hosted sandbox option exists; server-side session retention still matters. Conduct only a consented, metadata-only or synthetic public pilot.

## Case studies suitable for a small independent controlled comparison
A. Source integrity / stale metadata issue with synthetic fixture and exactly defined pass/fail (route existing Task 2 P0, never modify original frozen rows).
B. Bounded PR defect where current Supervisor stalls after a completed analysis (run agent with **read-only clone**, compare time to reliable patch + tests, without automatic merge).
C. Closed issue with one known negative control for prompt injection/tool failure/invalid repository permission and stale model receipts.

Freeze 12 representative tasks (4 each), which include 3 deliberate failures/unknowns, and compare:
- B0: present deterministic owner + existing API workflow.
- B1: same owner with better event/request trace joins, no new Agents API.
- B2: single-turn Agents API in a sandbox on **one** publicly safe synthetic issue, only after budget/permission review.

Metrics: `verified_original_owner_diffs`, `tests_verified`, `merged_actual`, `consumer_readback`, true/false closure claims, unsafe tool events, first-known source truth, minutes elapsed, tokens + cache writes + hosted compute + tools + retry costs. **A high B2 token bill with no additional closed issue is negative value.**

## Decisions API - precise scientific scope
The current [#1760 pilot](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1760) and frozen `research/api_agent/AI_DEV_STACK_DECISIONS_SHADOW_EVAL_V1.md` already specify 60 examples in triage/news/Alpha metadata and 20 unseen matched holdouts. Keep it. Actual output `probability` means the model's predicate estimate, **not** an empirically calibrated probability of a token 5x, BTC down day or a real-world event. Don't use it as alpha or automated PR approval.

**Acceptance must include:** zero critical unauthorized actions or data leaks; no loss of accuracy against cheapest incumbent; pre-frozen >=20% lower USD/accepted-correct or >=30% lower p50 latency; sensible abstention on malformed/unknown sources; independent check; no Task 2 research population change.

## Datasets / Evals transition
Existing Evals moves to read-only **31 October 2026** and shutdown **30 November 2026** per official docs; starting a new old-Evals evaluation now creates migration work. Prefer local deterministic test fixtures plus Datasets for model-behavior comparison. Keep raw original market observations under their canonical existing owners and do not pretend Datasets gives reliable 'first known' issuance timestamps.

## Security, privacy and legal constraints
- API keys only in approved credential plane. No owner card screenshots, private wallet labels or restricted payloads in public repo, Datasets, prompts or tracing by default.
- Treat website/X/Grok/Claude and API tool data as **untrusted input**, not instructions to spend, merge, create keys or access network.
- Separate source/canonical repository authority and independently destructive backup/Vault authority.
- Do not copy proprietary third-party vendor code or API data contrary to license.
- External cloud agent must have minimum repo and network permissions and no permission to sign or trade.

## Verified sources (2026-10-30)
- Agents overview, observability, tracing, events, quickstart, OpenAI-hosted sandboxes: https://developers.openai.com/api/docs/guides/agents-api/overview
- Decisions GA and model: https://developers.openai.com/api/docs/guides/decisions
- Datasets and Evals migration: https://developers.openai.com/api/docs/guides/evaluation-getting-started
- Prompt cache write/read pricing: https://developers.openai.com/api/docs/guides/prompt-caching
- Batch: https://developers.openai.com/api/docs/guides/batch
- Pricing: https://developers.openai.com/api/docs/pricing
