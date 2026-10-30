# 03 · Execution, implementation roadmap and evaluation matrix
**Date:** 2026-10-30. **Artifact type:** owner-approved research execution plan under the existing Research Lab folder. **NOT** a new operational source of truth or automatic dispatch. No paid execution, new external vendor, new queue/scheduler, new PR beyond this documentation archive.

## Grounding: actual framework bottlenecks
- Existing #1156 Supervisor and FMOS have extensive workflow, API, Codex and route governance; **more agent sessions are not equivalent to more merged safe PRs**. At current main the operational architecture explicitly reports `automatic_code_write=false` and `automatic_merge=false` for scoped remediation; verify original repo/head before treating a particular agent's result as integrated.
- Existing #1596 Task 2 requires original issue/capture/first-known source times, PIT admission, matched-baseline scoring and error controls. No AI service/dataset can retroactively create truth from absent source.
- Existing #1760 Decisions news triage pilot and `research/api_agent/AI_DEV_STACK_DECISIONS_SHADOW_EVAL_V1.md` already define 60 frozen cases +20 unseen controls, three arms and release/stop requirements; **do not overwrite** that preregistration.
- Existing `06_RESEARCH_LAB/architecture/2026-09-23__agent-invocation-contribution-ledger-shadow-contract-v1.md` maps cost of invocations to real changed information and later outcomes; reuse it for agentic unit economics.
- GitHub actions minutes are finite; October exhaustion has been reported but current runtime receipts show some successful owner workflows while some scheduled event gaps persist. Do not equate a historic quota screenshot with an absolute present block; verify exact workflow capability at every start.
- Hosted Agents API currently **not ZDR and US-only residency**, so hard legal/privacy blockers may be greater than technical convenience.

## R0 - no-spend audit (first owner work, highest priority)
**Owner:** Existing API accounting owner + Supervisor #1156. **Spend:** $0 new API.

1. Resolve account capabilities *without exposing user credentials*: whether API org, linked ChatGPT Pro grant, model availability, sandbox use, project vs org spending and rates are actually permitted. API Build usage tier != Pro subscription tier.
2. Reconcile two cost truth planes: provider org/project Usage and existing `LATEST_OPERATIONS_DASHBOARD.json` internal RECEIPT ESTIMATES at exactly identical UTC windows. A financial screenshot or model cost estimate is not a bill; investigate project scope, cached writes, tools/retries and evolving prices. Output aggregate-only provider-value-free status.
3. Review existing `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`, `scripts/api_agent/capability_router.py`, source-aware model routing and budget guards. Identify any duplicate work and stale model aliases; avoid fresh routing engine.
4. Build one **read-only original task execution lineage table** `run_id→paid/estimated model request→actual tool result→original PR/head→CI→merged/main→natural readback` for three bounded case studies (one successful, one failure, one unknown). Where no task can be traced, report UNVERIFIED; no inference.
5. Produce owner-visible delta: source + exact commit + owner + single next existing change, nothing else.

**R0 pass gate:** cash and credit terminology reconciled, cost and lineage classes honest, 3 actual cases covered with source refs, no API calls or permissions changed.

## R1 - observability first, no hosted new agent
**Owner:** #1156 existing Supervisor and API-agent owner. **Incremental budget:** preferably $0 new model calls (deterministic receipts).
- Inspect actual existing GitHub Actions model work, receipts, job results, PR patch/head, and original ownership. Add only missing **join** identifiers or tests through existing Codex intake if a reproducible defect emerges.
- For one original task, demonstrate that every "COMPLETE" action has verified immutable output and no duplicate paid invocation. Require explicit `NOOP`, `UNKNOWN`, `BLOCKED_SOURCE` and `PENDING_READBACK`, not fabricated closure.
- Build no new dashboard when current `LATEST_OPERATIONS_DASHBOARD.json` and contribution-ledger sidecar can be extended. In particular, avoid creating a new permanent Supervisor or an always-on paid agent.

**Acceptance:** lower false-complete reports and fewer duplicate reworks; exact source-level model, request and cost; tests cover missing receipt, stale HEAD, revoked tool access, private/public boundary and failed merge with graceful no-op. Evidence stored only in already authorized owner paths.

## R2 - Decisions API shadow evidence
**Owner:** #1760 with Situation Room #1563 and capability router; user approval for spending remains separate where original gate says so.
- Maintain frozen 60-example +20-unseen cohort, 3 arms: deterministic, existing Luna Responses, Luna Decisions. Use public/sanitized test data only, no restricted provider values.
- Use structured `choice` for low-stakes news labels and owner routing; `predicate` for source-actionable classification only. Model `probability` is not economic event probability; `UNKNOWN` must remain UNKNOWN.
- Compare wrong owner/critical false escalation, missing severe news, malicious external-text injection, p50/p95 latency, accepted-correct USD, schema errors and first-known provenance.
- Only run paid requests with explicit owner-limited approval and actual project spend remaining.

**Acceptance from preexisting protocol:** zero critical unauthorized action or leakage; no reduction against best baseline; >=20% lower accepted-correct cost OR >=30% lower p50 latency, with fixed negative controls and heldout; otherwise `REJECT/INCONCLUSIVE`. No live model route or market action promotion.

## R3 - Agents API as bounded engineering challenger (NOT full Supervisor migration)
**Owner:** Existing Supervisor #1156, original PR defect owner, GitHub code/security policy.
- Prerequisites: current API org and model/key permissions verified, US-only/no-ZDR retention accepted for synthetic/public-only test, real sandbox + tool/container prices and metered caps reviewed, branch protection/safepoint/backup separation checked.
- One 1GB hosted isolated sandbox or owner-managed equivalent, ideally with **read-only public test repo fixture**; 1 nontrading original-owner defect. No private secrets or restricted market data, no write to canonical main, no auto-merges or credential creation, no nondeterministic infinite task cycling, exact session max turn/tool/budget.
- Use separate agent as a **proposal coder** that returns a minimal diff + test receipt + safe classification. Supervisor's existing owner path alone handles original PR review and merges under actual platform rules.
- Compare deterministic incumbent + existing API vs single Agents API job: time to verified patch, compute cost including sandbox+tools+retry+subagents, reproducible tests and failure handling.
- **No self-certified speedup** from provider's "agents can do X"; direct per-task evidence and holdout required.

**Acceptance:** exactly one original defect from frozen source is reproduced and repaired in isolated fixture; security tests pass and a human/repo-authorized owner reads back original PR/new main where appropriate; no budget creep, no private retention violation. For real production use later, require 3 independent bounded examples and demonstrable higher completed-ticket/actual-$ ratio. If it mostly creates another PR needing closure or is more expensive without better proofs: `REJECT/DEFER`.

## R4 - selective datasets and cheap offline intelligence
**Owner:** Research Lab #1512 / Task 2 #1596; no new Task 2 mandate.
- Maintain 12-30 original, source-admissible *synthetic or already public* examples of stale data, leap-ahead source times, schema drift, duplicate forecast events, missingness, owner collisions, blocked live merge and fake provider "done" receipts.
- Use local deterministic tests as truth. Use OpenAI Datasets only to compare model outputs; never upload sensitive restricted source or market raw data. Evals legacy deprecates 2026-10-31 and shuts 2026-11-30, so no new legacy Evals implementation.
- Nonurgent regression rechecks can use Batch 50% discount if real net cost, urgency and current support align; no async market forecasts delayed by 24h.

**Acceptance:** measurable reduction in false-positive safe/complete classifications, traceable regression tests, no difference in frozen original Task 2 data. Stop if source proof unavailable or benchmark only improves language style.

## R5 - minimum viable release and economic verdict
**Owner:** Existing #1156 + #1596 + #1512 as relevant.
- Single final matrix of tested alternatives: `KEEP_EXISTING`, `IMPROVE_TRACE`, `ADOPT_DECISIONS_TRIAGE`, `ADOPT_BOUNDED_AGENT_SESSION`, `REJECT`.
- Report **one** cost figure per completed original task with full token+cache-write+tools+sandbox+retry/subagents, and scientific error savings. No newly approved market prediction unless original first-known/economic outcome supports it.
- If tests fail / are blocked: close specific research question with evidence, do not keep a paid agent or an issue open forever.

## Exact framework ownership and what may be safely produced now
| Purpose | Current owner/source | May do now | Cannot claim without independent proof |
|---|---|---|---|
| Supervisor PR closure & self-healing | #1156 + FMOS and current queue | Read issue/PR/CI/receipts; focused docs tests/bug fixes through original owners | Agent DONE means merged / actual Pages site works |
| Task 2 scientific validation | #1596 | Synthetic fixed adverse cases, clock/packet/horizon consistency test | Past data was visible at original decision time |
| Decisions routing | #1760 (already registered) | Official docs, no-spend fixtures; paid only with explicit gate | Luna predicate probability = market probability |
| AI dev-stack watch | existing weekly #1156 / `research/api_agent/AI_DEV_STACK_WEEKLY_INTELLIGENCE_V1.md` | Identify truly new official features only | New research report creates a scheduler |
| Alpha REA | Alpha #22/#88, Research Lab #1512 | Birdeye-like clean-room principles, wallet/pool/source evidence | Third-party vendor smart-money labels are PIT-admissible |
| Spend controls | OpenAI org/project owner + existing accounting | Compare screenshots privately with sanitized receipts | Internal estimate equals provider invoice or all filters match |

## GitHub acceptance + review discipline for this documentation archive
- This research folder belongs in a **new documentation-only PR**, not a direct push to protected main or a second engine. Main only after actual rules/checks and independent technical review; draft state may remain open when CI is unavailable.
- Original production PR issue/HEAD, branch protections and recovery safeguards override this research plan. No merge merely because model says confident.
- Post-merge **main SHA + blob readback** required to call a document *published*. An open PR is discoverable research draft only.

## Optional post-merge Owner handoff
Only when this doc PR is merged, reference it once from existing #1512 and #1156. Do not spam multiple old PRs, make new task/scheduler or assume existing Supervisor reads comments. If no real trigger, mark `HANDOFF_NOT_DISPATCHED`.

## Research failure/kill rules
1. Logs/traces alone with no downstream closed work -> method retained for debugging, no Agents adoption.
2. Validated typed classifier is slower/more costly or has higher miss rate than deterministic champion -> reject despite GA.
3. API cost increase over current cap or exposure to private data/US-only retention -> stop.
4. AI developer feature that violates as-of source custody, policy separation or freeze -> stop.
5. No access to account/credit entitlement -> document `ACCOUNT_READBACK_REQUIRED`; no new subscription/upgrade guess.
6. Competing PR, issue or workflow already solves problem -> close as `DUPLICATE_NO_ACTION`.
