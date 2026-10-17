# Agentic Maintenance & Efficiency v1.0
## Integrated architecture and implementation handoff, 2026-10-17

**Status:** DESIGN PROPOSAL / AGENT EXECUTION HANDOFF. **Not a live activation, authorization, new system owner, or claim of completed implementation.**
**Operational repair owner:** existing Framework Learning Supervisor / Automation Production Health / Remediation, issue #1156. This is task ownership only, **not** merge authority. Issue #1156's goal of end-to-end repair without user intervention means automated diagnosis, bounded preparation, testing and readback *within permissions already granted*; it does not override AGENTS.md §0.2a, grant bot self-merge or pre-authorize release.
**Evaluation owner:** existing Adaptive Evolution Scoreboard / Anti-False-Success Ledger, issue #1157.
**Code-intake authority:** existing Remediation Maturation Controller and CODEX_READY contracts.
**Reference:** https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family (OpenAI, 2026-10-14).
**Mandate:** Improve autonomous maintenance, uptime, CI efficiency, context efficiency and cost per verified outcome while preserving the current governance, source boundaries and evidentiary reliability.

> Design principle: reuse the existing machine, extend its reach only when required, and demonstrate real incremental value before expanding. No parallel supervisor, queue, scheduler, reviewer identity, model router, telemetry truth, payment authority, or autonomous integrator.

## 0. Authority and immediate preflight

This document is an *implementation proposal* subordinate to current main, AGENTS.md, canonical policies, GitHub branch/ruleset status, current domain owner contracts and authenticated owner instructions. A merged design document by itself grants **zero** new runtime permissions.

Read current:
1. AGENTS.md and 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md with CROSS_REPO_AGENT_CONTEXT_MAP.json.
2. LATEST_OPERATIONS_DASHBOARD.json, LATEST_HANDOFF.json, research/architecture_health/LATEST_AUTOMATION_HEALTH.json, research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json.
3. LATEST_REMEDIATION_QUEUE.json, LATEST_CODEX_READY_TASKS.json, LATEST_CODEX_EXECUTION_STATE.json.
4. 00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md, issue #1156, issue #1157, existing Codex-intake skill and execution ledger.
5. research/api_agent/API_TASK_REGISTRY_v1.json, CAPABILITY_ROUTING_POLICY_v1.json, API_INTELLIGENCE_POLICY_v2.json, exact target code, relevant runs, current GitHub review and release rules.

Control plane = public Investering-Framework-Archive-v1. Restricted provider payloads, private normalized values, and immutable private evidence = Donh91/secrets. Credentials = approved secret plane only. Public issue/PR/comment must not contain restricted values. Preserve Round 3 analysis firewall, frozen forecasts, original source timestamps, and recovery-plane separation. Fail closed if required private authority is unavailable. None of these safety barriers may be relaxed for model speed or maintenance gains.

The current API policy still has "code_write_executor: CODEX_ONLY" and "api_models_have_repository_write_authority: false"; issue #1156 proposes a broader qualified-executor route. **Treat this as a documented policy migration candidate, not implicit permission.** Until a narrowly reviewed authority change is genuinely approved and enforced, APIs may inspect/propose but not write where the active policy forbids it. Codex remains usable but is not the permanent conceptual default for future qualified executors.

**Governance review warning (Grok pilot F1, 2026-10-17):** a local mutation removing this document's hard stops and claiming self-merge left unrelated repository CI jobs green. Therefore a green `gate` or `storage-health` check on a docs-only PR is NOT evidence of governance-content safety. Until the existing owner has a sensitive, mutation-tested governance check, require a manual or independent semantic review of the exact diff and current policy. Do not call the check validated merely because it ran green. Prefer a robust contract-aware check in an existing gate to brittle magic-string matching; implement it only through a separate scoped, reviewed task.

## 1. Existing topology, not a replacement

The operating path remains:

AUTOMATION PRODUCTION HEALTH / EXISTING LIVENESS OWNERS
 -> CURRENT OPERATIONAL COCKPIT + FRESH EVIDENCE
 -> REMEDIATION MATURATION (#1156)
 -> SINGLE SIGNATURE/FINGERPRINT + ROOT CAUSE / PRIORITY
 -> EXISTING QUALIFIED EXECUTOR (deterministic / authorized API agent / Codex / Work-assisted agent)
 -> TARGETED TEST + NEGATIVE CONTROLS
 -> GOVERNED BRANCH/PR/CI/REVIEW/RELEASE
 -> EXACT MAIN AND PRODUCER/CONSUMER READBACK
 -> EXISTING REMEDIATION LEDGER AND #1157 MEASUREMENT
 -> VERIFIED RESOLVED / POST_FIX_OBSERVATION / ESCALATED / ROLLED BACK.

The existing LATEST_CODEX_READY_TASKS.json alone owns CODEX_READY state. Existing execution state and ledger are observability, not queue authority. Research or an external reviewer may submit a bounded candidate but cannot self-promote to CODEX_READY. Deduplicate new findings against health signatures and open PRs. Never manufacture a second queue simply for cleanup.

Work is a user-facing orchestration environment with whatever tools/models actually exist in that run. **Work is not synonymous with Astra**. A coding executor is an execution mode, not a brand or a model identifier. No Work-credit balance, Codex quota, reasoning effort, or model name grants release or source authority.

## 2. Maintenance lanes and safe opportunity discovery

A. INCIDENT/RELIABILITY (priority follows #1156): deterministic failures, broken pointers, CI regressions, integration errors, stale data health, readback and idempotency. Existing health/remediation authority owns this lane. Repeated identical deterministic fingerprints do not justify unbounded reruns.

B. TARGETED CODE HYGIENE (initial shadow discovery): repeated unused imports/functions, duplicated pure utilities, obsolete test fixtures, structurally dead code, stale experiments, docs/config drift. Discovery is advisory until every candidate has an exact owner and a deletion or modification proof. **Absence of calls in search is not proof of dead code.**

C. CI/EFFICIENCY: flaky tests, pathological test latency, redundant jobs, expensive matrices, nonessential repeated scans, AGENTS.md prompt/context inefficiency, API token usage. Preserve required coverage, guard-sensitive failure tests, producer/consumer verification, and protected critical workflows. Prefer efficient test execution over deleting tests.

D. EXPERIMENT/FLAG RETIREMENT: especially high-risk. Require complete direct/indirect and dynamic consumer census, history, state semantics, operational kill-switch/fallback checks, and authorized evidence of nonuse. Feature flag, fallback, archived parser, kill-switch, incident recovery path, dynamic import, historical lineage, or data-availability gate may **never** be deleted on static search alone. Missing live telemetry => INSUFFICIENT_EVIDENCE.

Each proposal attaches:
- stable fingerprint; owner/subsystem; changed-file scope; base/main SHA and exact target ref;
- observed defect/waste, true baseline, reproducible evidence and competing explanations;
- risk class, blast radius, private-boundary check, semantic and fallback impact;
- proposed minimal change, expected value, negative tests, mutation-sensitive tests and rollback;
- current authority/approval state and whether the target is a P0/P1 production owner.

Do not put general housekeeping into CODEX_RESEARCH_CANDIDATE unless it actually meets the current bounded code-remediation intake schema; otherwise track discovery in the already existing #1156 owner and evaluate via #1157. Never create a faux CODEX_READY task for speculative refactoring.

## 3. Executor selection, future-proof and cost-aware

Two distinct execution contexts:
- **Interactive ChatGPT preference (distinct user-facing context, OUTSIDE API routing):** use the newest strongest accessible chat model with highest supported reasoning effort when the product exposes it. The framework does not purport to control ChatGPT's host selector or verify a hidden effort configuration. This preference does not override background-task policy of cheapest qualified execution.
- **Work/Codex/API/background task:** dynamically choose the lowest expected end-to-end-cost *qualified and available* capability that meets quality/risk requirements, escalating directly for difficult or consequential tasks. Use newest models when beneficial; older/cheaper models may win on measured equal-quality tasks. Do not reserve any task for an Astra/Sol/Luna/Terra name. Re-evaluate when new models become available.

Selection inputs: task contract, risk/blast radius, tools actually available, context size, evidence boundary, prior failure, deadline, quota/credits, executor permissions, expected total cost (tokens + retries + Actions minutes + review + repair), and expected success quality. A cheaper first call that drives 4 retries is not a saving.

Selection order is capability-based, not model-name-based:
1. deterministic script/check for provably mechanical tasks;
2. qualified bounded executor for simple maintenance;
3. stronger qualified agent for cross-file causality, ambiguous artifacts, large-context audits or critical adversarial review;
4. Codex/Work execution where their runtime capabilities make them the best **authorized** executors;
5. existing independent governance escalation when no safe qualified path exists.

A fallback must not drop quality/permission/evidence constraints. When credits, API capacity or code-write permissions are unavailable: try another *authorized* qualified executor, or remain BLOCKED_WITH_REASON. Never pretend a task executed because its agent was assigned.

Model pricing/capability records are **dated observations**, not timeless rules. Runtime validate model availability and supported effort/tooling before selection. A configured historical ID is a backward-compatibility fallback, never a hard commitment. The current CAPABILITY_ROUTING_POLICY and task registry remain runtime authorities until revised through the normal governed process. Do not create a second router: modify those existing paths, if experiments warrant it. **Distinguish per-run selection from authority-changing policy edits:** ordinary selection among already authorized models within approved budget/permissions needs no new personal sign-off per call. Altering router authority, permissions, budget, security gates, supported executor write capability, or the approved policy's meaning requires a separately authenticated explicit approval from repository owner Donh91, then the normal PR, review and readback. Merely running an evaluation does not approve a config change.

Maximum useful delegation depth and redelegation remain governed by the active delegation policy. A specialist's opinion is advisory; author identity is never counted as independent GitHub approval. Keep API hard-stop and lane caps unchanged unless the owner separately authorizes a budget amendment.

## 4. Safety matrix and autonomous action envelope

**Read-only discovery:** safe with existing read access, current-source/time binding and public/private separation.

**Propose draft PR:** allowed only through currently authorized branch-writing executor and within a documented scoped task. No production behavior change before merge. Even a purely test-only fix must preserve negative controls.

**Small mechanical repairs:** candidate for greater unattended autonomy under existing #1156 only when all current permissions, task-specific scope, risk-adjusted tests, review and release gates permit it. Owner proposal #1156 is not blanket self-merge authorization. Specifically, #1156's acceptance claim of `end-to-end without user intervention` excludes release/integration unless AGENTS.md §0.2a is met by an authenticated owner mandate or a separately ratified bounded release policy. Executor failover carries the original task's permissions and cannot supply missing owner approval.

**Governed high-impact or semantic work:** explicit domain-owner escalation. No autonomously changed trade thresholds, forecast scoring, historical records, source hierarchy, API budget, credentials, branch/ruleset policy, recovery authority, payment semantics, portfolio action, scientific promotion or release policy.

**Merge:** obey AGENTS.md whether or not GitHub main is technically protected. **Verified 2026-10-17:** Archive `main` advertised `protected:false` and GitHub returned no repository rulesets; missing rules are a defense gap, not permission to merge. It cannot be assumed that GitHub mechanically enforces this document's release requirements. Introducing required-PR branch protection must first account for the existing direct-main scheduled publishers: migrate/validate them rather than breaking critical data/health pipelines by flipping the switch. Owner-directed single-account integration applies only within its documented authorization and exact-head controls; it is not fake APPROVED or general unattended bot permission. The current review-event TOCTOU limitation precludes treating a bot comment census as atomic authorization. No bypass, force push or direct-main integration of a PR. Before merge, verify exact HEAD SHA, actual CI, live review state, P0/P1 blockers, backup/recovery separation and domain requirements. After merge, prove exact main blob and natural producer/consumer observation. Green CI alone != HEALED.

**Fail-safe:** same fingerprint repair concurrency one; bounded retries; timeout; stop on root-cause expansion; independent observation on self-healing owner failure; rollback/quarantine when verification fails; never silently relax checks to turn RED green. GitHub Actions critical Class A duties remain protected by #1156 Actions budget guard.

## 5. Candidate and execution lifecycle

Discovery: OBSERVED -> DEDUPED -> EVIDENCE_READY / INSUFFICIENT_EVIDENCE -> OWNER_TRIAGED.

Execution (existing lifecycle): CODEX_READY or authorized equivalent existing owner task -> IN_REMEDIATION -> PR_READY -> VALIDATED -> owner/governance-authorized release -> POST_FIX_OBSERVATION -> RESOLVED; also BLOCKED, REJECTED, ROLLED_BACK, REOPENED. These are conceptual stages only; **do not add competing machine statuses or overwrite existing enums**. Map to the current Remediation/Codex contracts and ledger.

Critical invariants:
- exact input SHA, branch head, target file/contract hash and task signature are checked immediately before write;
- stale/colliding/prior-fix candidate => CLEAN_NOOP with receipt, not speculative repeat;
- if original repro is not observed, distinguish new diagnosis from an asserted fix;
- high-risk negative tests must demonstrate guard sensitivity with isolated guard mutation, then return guard intact;
- no test mocks away the payment, integrity, or permissions gate it claims to exercise;
- actual runtime costs and receipts are distinguished from provider invoice totals;
- repair closure requires exact released version and genuine downstream proof.

## 6. Experiment design under existing #1157

Pre-register each improvement family with one primary endpoint:
**verified maintenance closures per combined end-to-end USD-equivalent cost**, reported together with **absolute number of correct closures** so reduced spending cannot disguise reduced coverage. Dollars and Actions minutes are separate dimensions unless a grounded account-specific exchange rate is explicitly stated. No invented conversion.

Safety floors (zero allowed critical regressions): source provenance, original time, immutable first-seen evidence, market/forecast semantics, protected CI guard coverage, private/public data, payment/idempotency, recovery separation, owner release authority. No promotion with any unresolved P0/P1. Log missed important defects and false negatives, not only successful cleanups.

Secondary endpoints: confirmed false-removal proposals; recurring incident count; P50/P95 CI time; Actions minutes/day and burn projection; provider-reported/receipt-estimated API cost by task; token use; repair retries; time to diagnosis; time to *verified* closure; production reopens; PR review effort. Mark unmeasurable quantities UNKNOWN, not zero.

**Pilot economics and stop gate:** Before any paid A/B or multi-model experiment, #1157 must preregister the funding lane, fixed maximum USD spend per pilot (including retries and verification), actual provider/receipt-cost measurement, stop-on-cap behavior, and how it remains within *all* current monthly, per-run and lane hard stops. No pilot is authorized to spend merely because this design exists. If a fresh budget source is unavailable, use offline/replay fixtures or mark BLOCKED; do not guess remaining money.

Pilot A (quality): freeze a small verified set of actual recent flaky-test or low-risk static-code findings with a no-model baseline; compare existing executor against 1-2 qualified alternative model/effort configurations, using same snapshot/tools/evidence, order-balanced where feasible and independent scorer. Same input/output contract, randomized/blinded review if practical. Count correct accepted findings, omissions and damaging false positives, not raw suggestions.

Pilot B (CI): obtain per-workflow/job runtime and measured cost baseline; rank candidate improvements by evidence-backed minutes/day. Trial one non-semantic optimization while preserving original 100% mandatory negative/integrity gates. Compare actual before/after with equivalent workflow scope, avoiding confounding from differing loads.

Pilot C (agent instructions): select **one** demonstrably wasteful/confusing non-safety AGENTS instruction from an actual replay trace. Same snapshot, prompt, model/effort and tools; A/B replay instruction unchanged versus minimally revised. Measure solved task, tool calls, tokens, run time, cost and safety. **Do not remove mandatory governance/preflight/safety checks merely to shorten context.** No permanent change unless the revised condition is measurably noninferior in quality and better in expected total task cost.

The #1157 owner must freeze sample, metric, baseline, exclusion rules, required negative controls, evaluation window, kill rule and promotion threshold **before outcomes**. No illustrative number in this proposal constitutes a pre-approved promotion threshold.

## 7. Implementation plan: incremental and agent-executable

### Phase 0, topology and blocker audit (NO code writes)
- Read the mandatory current-state files and exact rulesets above.
- Diff current #1156 proposed executor authorization against current CAPABILITY_ROUTING_POLICY (including CODEX_ONLY and API code-write false), API gateway, runtime tool binding, and actual PR release path.
- Inventory overlaps with existing Work/Supervisor/Codex efforts, open PRs and remediation candidates.
- Inventory current workflow load + quotas/billing-source freshness; classify unknown vs verified. Capture current RED workflows and CODEX_READY count. Explicitly report missing main protection/rulesets, but plan a safe migration of direct-main publishers before branch-policy enforcement; owner-only settings changes remain out of agent scope.
- Deliver one concise gap table: already implemented / needs test / requires code / requires separate authority / not worth implementing.
**Exit:** source-grounded plan, no new workflows, no duplicate issue or policy mutation.

### Phase 1, smallest safe maintenance pilot
- Choose exactly one confirmed low-risk defect or measurable CI inefficiency from existing evidence, preferably flaky test/root-cause or redundant test invocation, not deletion of source or research history.
- Freeze a minimal failure matrix; reproduce baseline, positive and adversarial negative fixture, and guard-mutation sensitivity where applicable.
- Choose authorized executor per Section 3 and create smallest task branch/draft PR under existing owner. If no authority, submit precise existing-owner task packet instead.
- CI plus exact test/readback; independent advisory review; governed release only when explicitly authorized and actually permitted. Natural runtime verification after merge.
**Exit:** one end-to-end verified fix (or correctly documented blocked/failed pilot), with real before/after time/cost/error evidence.

### Phase 2, routing nonlock-in proof
- On 2-3 equivalent frozen research/maintenance tasks, compare one generalist with 2-3 narrow specialists only where task fit, quota and budgets permit; no invented model availability.
- Specifically replay capacity-blocked Codex, unavailable Work credits, cheaper-but-equivalent prior model, high-complexity direct escalation, nonexistent model, and provider transient failure.
- Validate no false claims of manual ChatGPT model/effort choice; no new independent router. Record failures and cost-per-verified result.
**Exit:** #1157 preregistered decision and concrete evidence whether any routing modification beats baseline. If inconclusive, keep current policy.

### Phase 3, integrate improvements into existing owners
- Under #1156: extend existing health/remediation diagnosis, duplicate suppression, failed-job targeting, and Actions-minute guard only where tests find a true gap.
- Under existing API routing owner: test proposed model/executor changes in shadow against frozen tasks. Non-semantic runtime choice **inside approved policy** may stay autonomous. Any change to CAPABILITY_ROUTING_POLICY/API_TASK_REGISTRY affecting permitted operations, executor write access, security, budget or policy interpretation requires authenticated **Donh91 owner approval** before governed branch/PR/release. Remove accidental model-name locks only after approval where it is required; preserve permission boundaries.
- Under existing Codex queue: retain exact transition/completion evidence, no substitute authority.
- Under #1157: store outcomes in existing experimental record/scoreboard; do not establish a new competing ledger.
**Exit:** merged bounded code and verified operational behavior, or named explicit blockers.

### Phase 4, expand only on evidence
- Candidate expansion: indirect dead-code/flag census, stale experiments, CI matrices, agent context efficiency, recurring maintenance.
- New candidates must show source-specific savings/value and strong false-deletion defense before selection.
- Preserve documented rollback mechanism, owner-aware scope and daily/Actions/API limits.
**Exit:** expanded lanes only after preregistered measured wins; otherwise maintain small scope or kill.

## 8. Acceptance matrix, must be executed

| Test | Positive case | Adversarial negative case |
|---|---|---|
| Deduplication | same incident one owner | fingerprint alias/concurrent run cannot double-repair |
| Executor | cheapest qualified available succeeds | quota, model missing, unsupported effort, unsafe permissions -> safe fallback/stop |
| Model nonlock-in | newer qualified model available | older cheaper model equal-quality is allowed; Astra unavailable in Work not blocking |
| Source deletion | proven direct + indirect nonuse | dynamic path, killswitch, historic reader, incident fallback -> preserve |
| CI optimization | before/after eligible job complete | a required negative/integrity gate cannot disappear or be mocked |
| AGENTS A/B | same input and quality | removed security preflight fails comparison |
| Retry | transient provider fault one bounded retry | deterministic fingerprint stops blind retries |
| Private data | public metadata only | raw private values and credentials never in public receipts |
| Billing | idempotent failure/retry stays bounded | prior paid failure cannot spuriously charge again |
| Merge | exact head, authenticated owner authority, real checks | missing GitHub rulesets/branch protection never count as authorization; latest pending/TOCTOU, changed head or self-review -> blocked |
| Closure | exact main blob + natural readback | green CI only remains POST_FIX_OBSERVATION |
| Budget | critical work prioritized | class C defers under CONSERVE/CRITICAL; UNKNOWN usage not fabricated |
| Scientific boundary | maintenance-only operation | no Round3 unsealing or forecast/outcome historical mutation |

A design review and passing unit tests are not proof of a live unattended system. Report independently: designed, implemented, CI-tested, merged, observed in production, cost-validated.

## 9. Hard stops and non-goals

NO_NEW_SUPERVISOR; NO_NEW_SCHEDULED_WORKFLOW; NO_NEW_ROUTER_OR_QUEUE; NO_MODEL_BRAND_REQUIREMENT; NO_AUTONOMOUS_SELF_APPROVAL; NO_UNGOVERNED_AUTO_MERGE; NO_API_BUDGET_INCREASE; NO_HISTORICAL_MUTATION; NO_TRADE_OR_PORTFOLIO_ACTION; NO_PRIVATE_DATA_PUBLICATION; NO_DESTRUCTIVE_RECOVERY_AUTHORITY; NO_BYPASS_OF_REAL_GITHUB_RULES.

If scope requires semantic policy, new permissions, new spending, separate source authority, trade decision logic, or cross-repository destructive keys: **stop and route to current owner**. Do not silently reinterpret this document as permission.

No claim of implementation, autonomy, production verification, or savings until proved by exact receipts and readback.

**Path owner verification:** `00_FMOS/WP00_PATH_OWNER_REGISTRY_v1.json` already maps `00_FMOS/**` to `FMOS_CONTROL` with PR-only write policy; this dated design inherits that owner class. No new registry row or authority class is required unless a subsequent source-of-truth review finds a stricter requirement.

## 10. Immediate next-agent execution packet

**Mission:** Implement one safe measurable slice of Agentic Maintenance & Efficiency v1.0 inside existing #1156/#1157, using the current canonical repository state, with minimal PR, no extra architecture.

**Do now:**
1. Reopen current AGENTS.md, operational cockpit, #1156/#1157, actual GitHub rules and executor/router config at fresh main SHA.
2. Compare this proposal against already merged work and identify the *single* largest safe, reproducible maintenance inefficiency that will not distract Task 2, Cycle Navigator production or P0/P1 remediation.
3. Freeze baseline, one primary metric, failure matrix, source/contract IDs, affected paths and negative-control proof. Deduplicate existing PR/issue/queue. Get #1157 preregistration through its current approved mechanism.
4. Run deterministic reproduction first. Select the best *actually available and authorized* executor/model, without version locks. Use bounded isolated branch and draft PR; preserve existing permissions.
5. Test, adversarially review, check exact-head release gates; do not merge without genuine authority. On authorized merge verify exact main and actual producer/consumer behavior.
6. Write concise evidence-based execution result under #1156 with linked #1157 outcome. State exactly what remains BLOCKED, POST_FIX_OBSERVATION, or UNPROVEN.
7. If no safe candidate exists, return an evidence-supported CLEAN_NOOP with a ranked next candidate. Do not invent work.

**Definition of done for design:** this document exists as a reviewable GitHub change with no runtime modification.
**Definition of done for pilot:** real issue fixed with negative tests and natural observed closure, or an honest, documented non-success.
**Definition of done for autonomous expansion:** only after a separately governed authorization and verified, preregistered superior outcomes.
