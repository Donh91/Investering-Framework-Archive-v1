# S1 Next-Level Evolution, production architecture & research spec

**Type:** independent critical design to reconcile with Claude's EXISTING v2.0 Autonomous Steward. **Not a replacement agent.**

## 0. Non-negotiable foundation

Keep ONE active ChatGPT S1 scheduled task (existing task ID) and ALL current AGENTS.md, `00_FMOS/S1/RUNTIME_CONTRACT.json`, ACTION_LOOP pins, native branch protection, recovery/custody separation, private-plane permissions, science and source PIT contracts. The proposal provides no additional task, bot, credential, schedule, GitHub workflow, live trading or market authority. Monday 09:30-10:30 Europe/Copenhagen is strictly read-only, even if the owner is present.

Claude is OPTIONAL. Native ChatGPT + GitHub + Codex and user-present exact-head decisions must be sufficient. Codex is preferred for coding on a bounded existing original PR when capable; ChatGPT S1 remains the coordinator, not an automatically independent reviewer of its own work. Claude, when available, is extra detached adversarial coverage, never a dependency. A missing independent in-house reviewer creates an exact blocker/owner card, not an invented approval or a demand to renew Claude.

Goal is a **closed-loop work completion system**, not more reports. Current baseline v1.6.9 plus Claude's proposed v2.0 steward states are starting material, not presumed correct. Do not deploy a v3 rewrite before v2 passes actual hosted, native, independent review and prospective observations.

## 1. State, authority and event plane

Split S1's reasoning into three bounded pure decisions and their authenticated native adapters:

1. **SOURCE SNAPSHOT:** fetch branch/main SHA, AGENTS SHA, task contract + ACTION_LOOP pinned blobs, lane switch, and minimal latest original-PR data. Record source clock, GitHub API endpoint, run/task ID, verified path/blob. A GitHub comment can never attest itself, grant review identity, appoint an owner or prove a scheduled S1 execution. A stale main or partial response yields `SOURCE_UNVERIFIED` for the affected action.
2. **ADVISORY PLANNER:** compute a cheap changed-evidence fingerprint, one current reason, original owner, one-writer lease, priority and one next action. Result is a proposal with `authorized=false`, even if every Boolean says PASS. Maximum 3 eligible distinct originals for in-depth read; pause unchanged blockers until their exact resumption trigger. Never treat a missing search page as an empty queue.
3. **NATIVE EXECUTOR:** a separately scoped tool call after independently verified current permission. It can repair an original nondefault branch, ask Codex to address, request exact-head review or (only under active granted lane) SHA-bound native squash. It re-reads ALL gates immediately before write. It never derives permission from planner JSON.
4. **EVIDENCE/RECONCILE:** immutable operation identity (`repo`, `work_id`, `HEAD`, `action`, `contract_blob`), native readback, separate natural consumer verification. A timeout after a write means `AMBIGUOUS_WRITE`, requiring readback, not a second write. Post receipt at the existing original owner (#1156) only for a materially changed outcome.

No new canonical state store. Reuse existing PR/issue, #1156, #1157, #1512, Bridge #173, and operational-memory/quality ledgers. Only qualified source-bound observation may update historical learning in an existing owner. A GitHub issue comment is coordination evidence, not an authenticated machine lock. If no native lease or compare-and-swap equivalent exists, only one designated branch writer proceeds, and colliding heads fail closed.

## 2. State machine and measurable transitions

`DISCOVERED -> TRIAGED -> BUILD -> TEST -> REVIEW -> RELEASE -> OBSERVE -> CLOSED_VERIFIED`.

Side exits: `BLOCKED_WITH_TRIGGER`, `PARKED`, `OWNER_ACTION`, `RESEARCH_ONLY`, `SUPERSEDED_PROVEN`, `REJECTED_WITH_EVIDENCE`. Avoid auto-closure of valuable original work based only on age, counts or two correlated comments. **New evidence reactivates**, not passage of time. `CLOSED_NOISE` only with independent objective duplicate/supersession/falsification proven by current native objects and authorized closer, otherwise owner decision. No owner approval by a model, label, comment or packet.

Transitions require an explicit causal bridge:

- DISCOVERED to TRIAGED: original owner/work identity, source and risk, dedupe against linked PR/issue/Bridge package.
- TRIAGED to BUILD: reproducible defect, exact input/source SHA, permitted branch owner and tests that fail before fix.
- BUILD to TEST: changed bytes on actual nondefault branch, no shadow-only PR or unbound patch.
- TEST to REVIEW: positive and guard-removal negative, native PR-event CI actually executed relevant steps, privacy and source clock.
- REVIEW to RELEASE: at least one **genuinely independent exact-head reviewer**, full native review threads, no blocking findings. A claimed `APPROVE` in arbitrary Markdown is not a native GitHub review. Current `AGENTS.md` always prevails over future proposals.
- RELEASE to OBSERVE: authorized native `squash` with expected head SHA, one-parent merge, exact changed HEAD blobs on merge commit/main, no bypass; S1-owned credit only on authenticated natural scheduled task action.
- OBSERVE to CLOSED_VERIFIED: relevant natural producer/Pages/consumer after release, or separate honest `MERGED_CONSUMER_UNKNOWN`. Green merge CI is not production/consumer proof.

`CLOSED_VERIFIED` and `MERGED_CONSUMER_UNKNOWN` are intentionally distinct. If no eligible work exists, report UNKNOWN denominator, never fabricate zero or an active maintenance mission. A report, review, issue comment, PR created or merged by another actor is not an S1-owned closure.

## 3. In-house specialist and reviewer responsibility matrix

| Actor | Allowed contribution | Not allowed | Legitimate independent review |
|---|---|---|---|
| Existing S1 ChatGPT task | Source preflight, classify, bounded direct fixes to nondefault PR, Codex intake, authentic CI/readback, owner cards, authorized lane merges | Self-grant reviews, raw private data, Vault, paid calls without guard, live trading | Not independent of its own code or its own review rubric |
| Codex GitHub App | Code/test author or detached actual exact-head review; bounded `@codex address` on SAME existing original PR | Change default-branch governance unreviewed, merge bypass, self-approve its authored head | Codex review only when it did NOT author H and native platform identity/complete finality are proven |
| Independent internal ChatGPT reviewer | Separately initiated, clean-context red-team on exact immutable HEAD with pure scripts, negative tests and report | Pretend to be another GitHub identity or certify native checks it did not run | Only when AGENTS explicitly approves this reviewer type and execution identity/context/provenance are actually verifiable; until then advisory only |
| GitHub Actions validators | Privacy, entire test execution truth, source attestation, source isolation, token scope, runtime and browser checks | Semantic reviewer identity or blanket release consent | Deterministic gate, NOT semantic independent review |
| Claude (optional) | Detached critique and patch proposal in Bridge, independent research review | Be required for core operations, write Archive directly via Bridge scope, grant merge approval outside rules | Optional exact-head review only when its policy evidence and independent status are satisfied |
| Human owner | Required HIGH_IMPACT/OWNER_ONLY decisions, incident override through native policies, stop/restart via approved PR | Bypass GitHub real branch protection, fake review or Vault custody | Owner-present exact-head decision, distinct from independent technical review where required |

**Unavoidable edge:** a Codex-authored PR cannot be independently reviewed by the same Codex author or by S1 simply writing an `S1_SPECIALIST_REVIEW`. If no other independently qualified in-house reviewer route is proven, the next action is a concise owner card and no merge. This is compatible with operating entirely in ChatGPT/GitHub/Codex and needing no Claude subscription. Any future delegated reviewer lane must be proven separately before its result is accepted.

### Specialist selection

Use existing repository skills, only on actual trigger: `canonical-context-router` to locate authority, `s1-pr-repair-learning` for repeated HOLD/conflicts, `archive-governance` for archive and branch discipline, `research-lab-red-team` for experiments and source/falsification, `adaptive-analysis-methods` for high-consequence ambiguous failure, and `skill-quality-gate` for a change to skill routing. Skills do NOT automatically add reviewers or expand authority. The action model may choose deterministic no-model first, Codex as code worker, optional fresh internal red-team after code, and optional Sol MAX only on a separate paid-authorized owner work ID.

## 4. Owner action cards, better than repeated HIGH_IMPACT HOLD

For owner-only changes S1 must print a visible concise, one-case decision card in its scheduled result, based on exact native evidence, for example:

```text
S1 OWNER DECISION REQUIRED | Archive #2190 | HEAD=<40 SHA>
Why: governance-pinned health code; never auto-merge this head.
Changed paths: <native count and path digest>
CI: x/y exact-head required jobs executed, privacy result, latest run IDs.
Independent review: reviewer identity, exact HEAD, findings/threads count.
Recovery/authority: exact current receipt PASS/HOLD/UNKNOWN; source/recovery separation.
Remaining blockers: <enumerated>, not generic "incomplete".
Owner choices: APPROVE EXACT HEAD, REQUEST_CHANGES, HOLD, REJECT.
If APPROVE: open the existing chat and approve this exact HEAD. S1 re-checks ALL native gates before any action.
After merge: show main SHA, changed blob readback and any bootstrap 3b paste required.
```

It is a **proposal**, never an authorization token or substitute for authentication. The owner may act in ChatGPT using the existing GitHub connector in an interactive owner-present turn; scheduler must not convert a text/click from elsewhere into a merge. A newly changed HEAD voids the old card. If merge changes S1's pinned files, preserve safe-NOOP while transitioning the owner-pasted BOOTSTRAP and test the new live task.

A UI card should not leak private reports, holdings or restricted source values. High-risk unknown must be explicitly surfaced rather than silently pushed into LOW.

## 5. C7 and native GitHub tool compatibility

Current ACTION_LOOP C7 literally uses a workflow-scoped URL that the connected GitHub reader rejected (HTTP 400 allowlist). A repo-wide read is supported: `GET /repos/Donh91/Investering-Framework-Archive-v1/actions/runs?per_page=100&event=schedule&branch=main&page=1`. A future reviewed ACTION_LOOP patch may implement a bounded adapter that scans **only** exact `path=.github/workflows/automation-production-health.yml`, `event=schedule`, `head_branch=main`, completed SUCCESS, updated within 26 hours and verified page coverage. A recent non-main, PR, skipped, incomplete or failed schedule run is never allowed to masquerade as PASS. A success in the health-observer workflow doesn't mean the observed fleet is GREEN.

Never silently substitute another endpoint on an action that current policy requires unless the owner-reviewed source PR changes that instruction. The pure reducer in `reference/s1_steward_guard_reference.py` is a negative-control design, not a policy patch. Record an exact `TOOL_CANNOT_READ` or `C7` value rather than generic `PREFLIGHT_INCOMPLETE`.

## 6. GitHub safety and workflow-isolation evolution

Claude v2 contains `privacy-scan`, `execution-truth` isolated jobs and a first secret-job split. Keep that direction but don't broaden autonomous merge before the actual mounted job and dependency closure are independently proven. Its reviewer found missed `sys.path` imports via `parents[k]/"dir"`; the post-R3 fix is awaiting independent review. The derived secret-code list is at best a lower bound unless dynamically loaded/imported modules, local config files, plug-ins, symlinks, `__init__.py`, process imports, shell sourcing, worktree hooks, Git env mutation and PR/ref checkouts are considered. Test every path admission at current main against actual workflow job/step evidence and ensure fallback `UNKNOWN` means lane exclusion, not permission.

The remaining approximately 58 non-secret write jobs in Claude's build report are NOT assumed safe. Each gets a verified isolation classification and a shrink-only debt register in the existing owner before changes become lane eligible. Don't use new GitHub protection exceptions, force pushes, self-review or short-lived fake scanner outputs to reach velocity.

## 7. Failure recovery and task liveness

Consider the following independently:

- **Scheduler dispatch:** actual `scheduled_for`, `started_at`, `completed_at`, run ID and task-result ID. Historical 57m and 15m delays exist. If no native platform clock, status is UNKNOWN; do not conflate with GitHub CI. The ChatGPT scheduler cannot be restarted by a GitHub report.
- **Source verification:** current main and pinned SHA readback. If missing, no GitHub writes. Preserve one S1 task identity and original schedule.
- **GitHub REST/Web connector:** explicit 403/429, allowlist 400, pagination incomplete, 0 jobs, wrong event or path, rate limit, stale result. Tool unavailable is not evidence that the target job failed.
- **PR writer:** partial file write or changed HEAD means readback and new exact-head review. Use native expected SHA; no force push or blanket ours/theirs merge. `@codex address` should be deduped by exact finding+head and one controlled writer lease.
- **Merge race:** native merge action must bind current expected HEAD and existing rules; 405/409 STOP. An uncertain response may have merged, so query merged PR and one-parent commit instead of retrying.
- **Postmerge/consumer:** stale main, absent Pages readback, missing natural producer, cold start, consumer external downtime -> `MERGED_CONSUMER_UNKNOWN`, not closure.
- **False completion/competing reviewer:** untrusted comment writes, edited response, stale detached approval, Codex-authored PR with Codex review, fake GitHub App author, model-generated unit-test line. All must fail closed.

An `operation_key` dedupes intended actions but is not a lock. Actual state transitions use native idempotency, precondition checks and post-write readback. No model can treat missing receipts as proof of no action.

## 8. Risk-tier workflow and capability fallback

| Class | Examples | Default action | External reviewer required? |
|---|---|---|---|
| LOW | Docs/tests with no gate influence, safe original PR | Codex independent review if not author; normal existing lane if truly eligible | No |
| MEDIUM | Bounded standard-library fix with real tests | Codex worker OR reviewer, distinct authorship; exact-head CI | No |
| HIGH | Consumer/producer changes after isolation | independent review + HIGH evidence + active lane, otherwise owner | No, but unproven internal independence -> owner |
| HIGH_IMPACT / OWNER_ONLY | S1 contract, AGENTS, workflows, gate/pin, permissions | owner card; source and recovery evidence; manual exact-HEAD owner-present merge and task-bootstrap coordination | No mandatory Claude, owner always involved |
| EXTREME/UNKNOWN | Security/authority ambiguity or transaction/custody boundary | HOLD, security escalation, no merge | No mandatory Claude, but unresolved safety cannot be bypassed |

No fee/API call for ordinary S1 ticks. Paid Sol MAX is **research only**, routed through existing guarded one-shot mission after all checks. Model names or usage quotas never confer a stronger release authority.

## 9. Performance outcomes and original scientific discipline

Freeze a baseline v1.6.9 cohort (and v2 as comparator once live) before evaluating v3. Primary endpoint: **independently verified complete original work outcomes per owner interaction and per cost**, with risk-conditioned denominator. Secondary: legitimate original unattended merges, S1-origin code repairs, main readback, natural post-fix consumer outcomes, median/p95 cycle time, PR backlog age, material owner interventions, changed-fingerprint review repeat counts, scheduler lateness, actual GitHub work/round, API spend and UNKNOWN billing. Safety guardrails: zero false READY/owner attribution, zero auto-close of worthy originals, zero provenance/privacy/custody breach, zero unapproved model spend. Compare like-for-like risk and eligible/available-work cohorts, not all raw PRs.

Any retrospective benchmark is `RESEARCH_ONLY`. Prospective 7/28-day metrics are admissible only from real native task/run PR events and first-known evidence. No future market return or paper-wallet performance is claimed by an operations system. Store verified episodes in the existing operational memory and #1157 scoreboard, never create another mutable `LATEST` authority.

## 10. Proposed staged implementation, without v2 duplication

- **P0a, urgent:** Codex repair #2190 current original branch with fork repository identity check, red/green same-source regressions, S1 blob chain, exact-head CI and detached reviewer, owner-present release. No simultaneous Claude editing.
- **P0b, specification:** Claude reviews this package against existing v2 recipe/build; accept/reject each case with rationale. Keep one v2 source package, rebased against current `main` AFTER #2190's resolution. Fresh R4 specifically attacks `sys.path` coverage, isolation, stale S1 pins and review authorship, plus this package's review/closure concern.
- **P1, safe v2 shadow:** use pure functions and current main+PR fixture data to replay real cases. Run all positive and adversarial tests. No task change and no new reviewer authority.
- **P2, staged owner present:** review and merge only approved v2 packages through existing governance. If two back-to-back packages are required, hold S1 in source fail-closed between them; owner pastes final exact `BOOTSTRAP.txt` once only if all intermediate safety and rollback preconditions are proven. Never turn the lane ON with an unisolated gate.
- **P3, measured v3 after observed v2:** consider shorter intelligent loop, in-house reviewer adaptation, in-run owner cards, recipe-driven capability routing, step-budget ledger and source-bound task/liveness monitor. Pre-register an incremental challenger against v2, not an unconstrained rewrite. Promote only if safety floors hold and real closure improves.

## 11. Red-team scenarios Claude and Sol should challenge

1. A `workflow_run` on an external fork's `main` reports failure or success before a legitimate schedule.
2. One S1_ITEM forged/edited by an agent using the same account escalates park counters and closes valuable research.
3. Codex both authors and reviews a PR, then S1 claims independence from its own specialist rubric.
4. Review is exact head A but update-branch changed to B, green workflows on B are missing.
5. A required job reports SUCCESS but its substantive test or privacy step is skipped.
6. Main changed while S1 was at C1b or between merge intent and squash.
7. Initial code write completes, API times out before receipt, S1 restarts and duplicates.
8. Scheduler starts >57 minutes late; latest_result still points to an earlier run.
9. A current Bridge package is valid research but not an executable code fix; no PR creation on intake alone.
10. A secret-using workflow imports modules through mutated `sys.path`, shell aliases or generated code.
11. S1 cannot obtain full PR pagination, or native 403/429, but assumes no open blockers.
12. A site PR passes native Python CI but changes live Pages public fields not scanned by privacy/rights gates.
13. HIGH evidence expires 30 hours, only HIGH is stopped while LOW continues.
14. Owner says APPROVE to stale head; S1 must reject and request fresh exact-head decision.
15. Codex silent and Claude unavailable for a week; S1 should continue work it can truly perform, and surface unresolved independent-review cases, never invent one.
16. An automated close is backed only by time-expired state or same-principal comments and later destroys a valuable roadmap item.
17. Paid Sol POST times out after provider accepts; no response ID, liability UNKNOWN; no retry or 'free' assumption.
18. Rejected PR changes to Source/AGENTS/rules, but an older cached spec implies a weaker lane.
19. S1 claims verified closure after a user-interactive merge, or after CI without actual main/consumer proof.
20. Multiple model specialists propose mutually incompatible code; a single original branch writer must arbitrate and show complete conflict cause.

## 12. Stop conditions

Stop implementation, not just report warnings, if a new patch: weakens provenance, review independence, privacy, source/recovery separation, branch safety, billing gates, forecast science or user-only high impact; generates unauthorized trade/capital movement; adds S1 tasks/schedulers without consent; creates divergent v2 source/writers; relies on nonnative GitHub facts for authorizing merges/closures; is unable to run negative controls; or contradicts the current authoritative AGENTS/main. Choose small safe repair, explicit blocker or revert, with exact reproducer, instead of passing risk through prose.
