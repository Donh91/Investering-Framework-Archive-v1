# Sol 6.1 MAX: S1 Autonomous Steward V2/V3 Adversarial Architecture Mission

**Disposition:** PREPARED_NOT_DISPATCHED. Owner granted full bounded permission to seek one Sol 6.1 MAX audit on 16 Nov 2026, but active, source-pinned paid code explicitly blocks release. Do **not** manually post a paid trigger or call the API until current gates pass. No API request, response ID, usage or bill was produced by this package.

## 1. Why Sol MAX, what question is worth paying for?

Use Sol 6.1 MAX as an *independent code/architecture falsifier*, not a second S1 builder. The goal is to find up to **three concrete, independently reproducible architectural defects** in Claude's existing v2.0 steward design that materially affect unattended closure, source/security or the owner's workload. The method must compare the cheaper no-new-code baseline and refuse trivial stylistic enhancements. Success is a patch-ready, source-bound, testable specification that Claude or Codex can implement IN THE EXISTING v2 PACKAGE. A finding without a reproducible source link should be rejected or labeled UNKNOWN, not turned into a PR.

Sol's strongest value is independent analysis of the system's hardest contradictory states: **how to run without Claude while never permitting self review**, how to close work without age/forged-comment false positives, how to isolate write-token and secret jobs, and how to continue after scheduler or partial GitHub failure without duplicate writes. Sol should challenge both Claude's solution and this ChatGPT reference package.

## 2. Activation controls, currently blocking

Native source on Archive main at snapshot: `research/api_agent/coordination/S1_SOL_MAX_ELITE_BOUNDED_BATCH_20261104.json`, registration blob `e518bb4e90f6c9bdf3eaebfa6809f32fe8cfedc9`. The existing adapter is `scripts/api_agent/sol_max_elite_dispatch.py`, transport `scripts/api_agent/sol_max_elite_transport.py`, existing `framework-learning-supervisor.yml` issue-comment job.

Existing `require_paid_authority` explicitly requires:
- `state=OWNER_APPROVED_DISPATCH`, `dispatch_enabled=true` recorded on current reviewed main,
- explicit `public_storage_consent_30_days=true` for background/store provider use,
- legacy `billing_liability_for_run_41870364609=RECONCILED`, including the source of the reconciliation,
- `payment_policy.no_auto_paid_trigger_until_reconciled=false`, and verified live budget reconciliation.

Observed registration instead: `state=REGISTERED_NOT_EXECUTING`, `dispatch_enabled=false`, previous liability UNKNOWN, no auto paid trigger. The code hardcodes **five** registered mission definitions from 4 Nov, restricted ID pattern ending `-20261104`; this new S1 vNext mission is NOT among them. Sending an unregistered trigger or changing dates by chat would fail. The source-backed paid lane is therefore NOT EXECUTABLE for this mission today. The user's latest mandate records a high-level preference but cannot prove native payment/budget/history/source consent or supersede current fail-closed code.

The locked budget caps of the existing lane are owner hard stop USD 30/month, global reserve USD 12 and USD 3/call. Historical unknown paid spend must never be treated as zero. No second POST after an ambiguous provider response. Background `store=true` requires informed 30-day public-only data processing consent and strictly public source allowlist; do not copy private provider research, secrets, personal data, holdings or wallet details. Re-check CURRENT price/model entitlement and actual provider usage rather than relying on old price constants. No Astra.

## 3. Safe plan to make a future paid call possible, without a second workflow

**Not to execute until independent reviewed source and owner requirements pass:** reuse the existing `framework-learning-supervisor.yml` one-shot workflow, and create a reviewed new mission entry / adapter contract in its existing source owner. Prefer a dedicated bounded architectural-review source manifest over the old five patch-only targets. If the owner instead chooses the registered `S1-CLOSURE-ENGINE-20261104`, that mission can only assess its PRE-EXISTING scoped source and must not be advertised as a full v2 audit. Preserve a single call/work ID, durable claim before HTTP, native payload digest, immutable response handle, GET-only collection, and no GitHub writes by the model. The existing adapter has `response format` limited to `PATCH/ABSTAIN` and a diff within registered files; new architecture findings require independent reviewed output schema changes, not raw prompt injection into runtime.

No new scheduler, bot, issue listener, autonomous payment authority, branch protection bypass or production S1 contract change merely for this review. Do not add provider credentials to any agent or Bridge. Owner-present governance PR is required if activation touches payment/workflow/contract files.

## 4. Immutable public input set, SHA/source pinned at dispatch time

Provide these **actual current bytes** from authenticated sources, not only their paths or summaries:

1. Active Archive `AGENTS.md` §§0.2c/e, native rules, `00_FMOS/S1/ACTION_LOOP.md`, contract/switch/bootstrap, S1 existing #1156, full current branch/main and HEAD. Model must be explicitly told that AGENTS/pins supersede package proposals.
2. Claude's actual v2 build: `reports/claude/automated/2026/11/CLAUDE-S1-V2-BUILD-20261116T0716Z/README.md` blob `ebec773a4e510f16fbe7801abbcb077cbee92595` and all source `v2_0/files` and `v2_0_github/files` with their `blobs.txt`. Recipe `RECIPE.md` blob `30089f5e6332708a31b07682d0338dd6549758cf`. These are research input, not production authority.
3. All R1, R2, R3 detached REQUEST_CHANGES reviews and last post-R3 diff/probe, including the `sys.path` `parents[k]/"dir"` correction not independently R4-approved.
4. Urgent original #2190 exact HEAD, Codex and Claude P2 fork-main finding, updated source HEAD, if any, and original owner merge status.
5. `00_FMOS/CHAT_S1_ELITE_RUNBOOK.md`, `00_FMOS/TASK3_S1_VERIFIED_AUTONOMY_CLOSURE_WIP.md`, `00_FMOS/S1/MISSION.md`, `00_FMOS/S1_V4_3_DIRECTOR_INTEGRATION.md`, `00_FMOS/S1_CLOSURE_ASSURANCE_STRATEGIC_RECOVERY_V1.md`, #1157 anti-false-success registry and current operational skill routing.
6. This package's `DESIGN.md`, `REVIEW_MATRIX.md`, reference code and 104 tests. Sol must attempt to invalidate it too, not simply agree.
7. Native task-liveness timestamps and S1 actual run ID, with scheduler delays recorded separately from GitHub workflows; avoid private task internals in public API packet unless policy expressly permits.

If input cannot fit within existing public source/size/cost limits, select representative current-source files by pre-registered risk priority and set `coverage=PARTIAL`; do not quote unavailable code as audited.

## 5. Freeze the exact mission statement

**Model:** `gpt-6.1-sol`, **reasoning effort:** `max`, ONE background one-shot only after release. **Mission ID proposal:** `S1-STEWARD-EVOLUTION-20261116` (NOT currently accepted by the registered hardcoded 4 Nov schema). No retry under a new ID after ambiguous acceptance.

> Audit the source-pinned Claude S1 v2.0 Autonomous Steward build and ChatGPT vNext reference adversarially. Design an in-house-only S1 with one existing scheduled task and no compulsory Claude. The system must support autonomous original-PR repair and qualified exact-HEAD merges when release policy permits, while delivering concise owner-present HIGH_IMPACT approval cards through ChatGPT/GitHub. Source/recovery, privacy, GitHub protections, PIT market evidence and billing are immutable. Return the three most important real architectural defects, minimal patches to the EXISTING v2 source (no duplicate module/service/queue), strong positive and adversarial tests, an explicit independence reviewer matrix, an end-to-end partial-failure state graph, and a 7/28-day prospective measurement/rollback plan. A clean 'no new patch' is valid. All code proposals are advisory and must go to Claude or Codex independent review, never straight to main.

## 6. Questions Sol MUST answer, with falsifiable negative controls

Q1. In-house independence: Codex-authored code cannot be validated by the authoring Codex instance, and S1 cannot turn its own rubric into an independent review. Find a legitimate ChatGPT/Codex/GitHub-only mode with strong technical separation, or explicitly route to owner/hold without any vendor Claude dependency.

Q2. Forced dispositions: Is Claude v2's `max_parks`/`triage_cycles` plus forged S1_ITEM counter monotonicity actually safe? Construct a case causing deletion-by-closure of valuable work without an objectively independent source finding. Propose a source-bound, reversible alternative and test it.

Q3. Workflow isolation: execute an adversarial import/call-graph argument against `S1_WORKFLOW_ISOLATION_V1.json`, `.github` isolated jobs, `sys.path` parent-dir imports, plugin/dependency loading, write-token residuals and job checkout trust. Give 1-3 minimal gates with a real negative source case and no false GREEN.

Q4. Tool feasibility: C7 workflow-scoped Actions endpoint rejected by connected GitHub fetch, but repo-wide `/actions/runs` accepted. Design bounded native pagination and freshness test that cannot accidentally count a fork, PR run, older success or incomplete latest run.

Q5. Liveness and exactly-once: S1 starts up to 57m late, after-write API result missing, duplicate `@codex address`, concurrent main advancement, 405/409 merge conflict. Provide a safe state machine with authentic intent/one native write/readback/recovery; precise error types and escalation.

Q6. Owner interaction: design 1-screen Danish HIGH_IMPACT card with exact HEAD, CI, pending review, Vault requirement and owner decision, a stale-head token invalidation, and no auto-merge from ordinary untrusted comment.

Q7. Real outcome: propose a preregistered small v1.6.9-vs-v2 shadow cohort, same current-source snapshots and eligible denominator, safety zero-tolerance, time/cost per complete original outcome. No claims of financial trading edge or arbitrary 10/10 scores.

Q8. Migration: four of seven base SHA in old v2 package no longer match main; #2190 modifies the same pin chain. Provide a deterministic non-force rebuild order, R4 independent review and rollback, with the minimum owner-paste tasks and NO half-activated lanes.

## 7. Required response format and review gates

Return one public-safe JSON or Markdown report with:

- `source_coverage` exact paths/commits/blobs actually read, missing evidence and clocks.
- `root_cause_graph`, not vague system optimism, with severity, current effective guard, missing edge, exploit input, affected decision and native reproduction.
- `findings` at most three P0/P1/P2, each with direct file/function/line and minimum diff, tests, negative and guard-removal mutation, and an alternate `NO_PATCH` verdict where appropriate.
- `review_independence_matrix`: who authored, who reviews, actual independent identity, required native proof, owner-only fallbacks.
- `failure_recovery_protocol` for bad API, unknown write, stale SHA, fork, delayed task, Codex outage and missing Claude.
- `final_patch_spec`: existing Claude v2 source path and test path only; no new task, public API writer, GitHub secret or separate service.
- `activation_gate`: exactly what remains OWNER_ONLY, what can be done by S1, what cannot be proven in this session, and which offline tests are *not* native hosted CI.
- `measurement_plan`: frozen primary endpoint, cohort denominator, adverse case list, 7/28-day evaluation and rollback.
- `decision`: `PATCH_READY_FOR_CLAUDE_REVIEW`, `SOURCE_BLOCKED`, `NO_MATERIAL_PATCH` or `REQUEST_CHANGES`, never `MERGE_AUTHORIZED`.

Model should not claim it executed unit tests without actual tool/hosted results. `PASS` is unsupported unless source evidence exists. No extra model call to self-review; the next independent reviewer is Codex/Claude/owner under current AGENTS.

## 8. Review and resulting artifacts

When a genuinely qualifying Sol call occurs, original workflow must publish native immutable `work_id`, context bytes SHA-256, source HEAD, issue-comment claim ID, Actions run/jobs/steps, provider response ID or `POST_OUTCOME_UNKNOWN`, actual usage (or unknown), error and cost ledger, and a non-authoritative output artifact. No manual paraphrase may substitute. Existing S1/Research Lab owner then attaches the public-safe result to Bridge #173 for **Claude review when available** and to #1156/Research Lab as a source-bound proposed change. A missing Claude response must not halt normal S1 work; it only leaves this *advisory scientific review* unadjudicated until an eligible in-house reviewer route is qualified.

## 9. Status and explicit stop reason

`SOL_MAX_NOT_EXECUTED = TRUE`. `reason = EXISTING_MAIN_REGISTRY_DISPATCH_DISABLED_AND_LEGACY_BILLING_UNKNOWN_AND_MISSION_NOT_REGISTERED`. `paid_usd_spent_by_this_packet = 0`. The offline code/test/requirements work remains useful now. Do not interpret this as a promise to launch tomorrow or as authorization to bypass the current platform safeguard.
