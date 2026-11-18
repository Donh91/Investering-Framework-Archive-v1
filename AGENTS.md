# Investering Framework - Agent Operating Instructions

These instructions apply to all agent work in this repository.

## Permanent safety invariant - separation of destructive authority

Canonical owner:

`01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md`

Permanent mnemonic:

```text
IMPROVE THE AIRCRAFT.
PROTECT THE PARACHUTE.
NEVER HOLD BOTH DESTRUCTIVE KEYS.
```

No autonomous or semi-autonomous principal may simultaneously hold sufficient destructive authority to irreversibly damage both the canonical source system and its independent recovery layer. Do not broaden credentials, disable safeguards, or acquire recovery-destructive authority to complete a source task. If a task would require both destructive authorities, fail closed and split or escalate the task.

This rule is model-agnostic and permanent. Model capability, benchmark performance, seniority, prior success, qualification status, Codex/Astra/Sol/API identity or future "golden key" status never overrides it.

For destructive or high-impact work, if separation cannot be verified, stop with:

```text
SEPARATION_OF_DESTRUCTIVE_AUTHORITY_UNVERIFIED
```

## 0. Cross-repository preflight

**Visibility invariant (effective 2026-09-29): `Donh91/Investering-Framework-Archive-v1` is the PUBLIC canonical/control plane and `Donh91/secrets` remains the PRIVATE restricted data plane.** Visibility does not merge their roles. Public control-plane reads may use anonymous/public GitHub access. Restricted-plane reads require explicitly authorized access and must fail closed when unavailable. Never assume a repository-scoped `GITHUB_TOKEN` from the public control plane can read the private restricted repository.

The repository estate has three separate planes:

- `Donh91/Investering-Framework-Archive-v1` is the public canonical/control plane.
- `Donh91/secrets` is the restricted data plane for raw/restricted payloads, private normalized market data, immutable capture receipts and restricted source health.
- GitHub Actions Secrets or an explicitly approved runtime secret manager/workload identity is the credential plane. Credentials never belong in ordinary files in either repository.

Before work that may touch source data, Round 3, provenance, automation, research or cross-repository state, read:

1. `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.
2. `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`.
3. the current control-plane domain contract/status.
4. if restricted evidence is required and access is authorized, `Donh91/secrets/AGENTS.md`, its two boundary files and the exact immutable binding/health receipt.

Private evidence must be bound by private commit SHA, exact path, bytes, SHA-256, source-contract ID, timestamps, schema and completeness. Never copy raw or normalized private values into this public control-plane repository, logs, issues, PRs or prompts. If private authority is required but unavailable, stop with `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` rather than infer, proxy or search the public control-plane repository.

Round 3 remains `PROSPECTIVE_COLLECTION_ONLY`; hypothesis testing and outcome scoring remain `OFF`. Round 1 and Round 2 are closed evidence. Historical findings can reach at most `FORWARD_TEST`. The legacy standalone Cycle Navigator repository identifier is historical only and must not be used as a current route.

### 0.1 Selective Shared Experience Layer

Cross-agent reusable memory is owned privately by `Donh91/secrets` and is exposed to the control plane only through the value-free binding `00_ARCHIVE_CONTROL/SEL_SELECTIVE_OPERATIONAL_BINDING_v1.json` and the `SHARED_EXPERIENCE_MEMORY` machine route.

SEL is optional support, not authority. Always resolve current canonical/current source authority first. Route to SEL only for repeated failures, non-local environment constraints, reusable procedures, bounded handovers or historically expensive rediscovery. Do not route current market forecasts, portfolio actions, simple source-local tasks, credentials or unverified investment hypotheses through SEL.

Global automatic memory retrieval remains `HOLD`. If SEL is unavailable, continue source-first under `SEL_OPTIONAL_CONTEXT_UNAVAILABLE`; do not block an otherwise executable task. If a recalled memory materially affects the work and the outcome later becomes observable, append one evidence-bound SEL outcome through the private owner. `MEMORY != TRUTH`.

## 0. Operational cockpit before repository work

Before automation, incident, API-agent, Codex, scheduled delivery or remediation work, read in this order:

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. `LATEST_REMEDIATION_QUEUE.json`
6. `LATEST_CODEX_READY_TASKS.json` when code remediation is relevant
7. `LATEST_CODEX_EXECUTION_STATE.json` when Codex, remediation or research-to-code handoff is relevant
8. `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`
9. the exact workflow, receipt, pointer, run and job logs

A health report may be RED while its observer workflow correctly succeeds after durable publication. `CODEX_READY` is a bounded task package, not proof that Codex has run, changed code or merged. `LATEST_CODEX_EXECUTION_STATE.json` is observability only and never overrides `LATEST_CODEX_READY_TASKS.json`. Do not work from conversation memory or an issue summary when newer hash-bound operational files exist.

### Shared Sol MAX lane for ANY owner-authorized ChatGPT thread

If the user in any conversation requests `Sol API MAX`, `GPT-6.1 Sol MAX`
or successor Sol research, read
`07_PROMPTS_AND_AGENTS/api/SHARED_SOL_MAX_CROSS_THREAD_RUNBOOK_V1.md`
and `research/api_agent/coordination/SOL_MAX_SHARED_MODEL_POLICY_V1.json`
before proposing or triggering an API run. The chat thread itself is never
an API authorization identity: use authenticated native owner GitHub
comments, the SAME existing Research Lab Sol workflow and original
owner issues #1156 and #1476, a new frozen public-only packet, its
exact SHA-256 in the native signed trigger, budget/unknown-liability guards,
one-use pre-HTTP bot claim, and immutable receipts. No background
cron/new supervisor/extra secrets/automatic paid retry. A thread without
GitHub write capability can draft but must NOT claim dispatch.

Prefer the newest OFFICIALLY VERIFIED, PRICED and account-accessible Sol
version, currently 6.1 Sol, with future 6.2 selected only after official
documentation, gateway price, model-cap, source-reviewed CI and
non-billable project GET evidence. If not verified, use 6.1 Sol.
**Astra is MANUAL OWNER REQUEST AND APPROVAL ONLY, for all model
routers/agent roles. NEVER select or fall back to Astra automatically.**
If no safe Sol route exists, fail closed, never switch to Astra.

### 0.1 Current production data authority - binding

Canonical owner:

`00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`

Machine mirror:

`00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json`

For **current-state** Master Monday, Cycle Navigator, CN site, short-horizon navigation, or market-state tasks, the default route is:

```text
current operational cockpit
-> exact current autonomous GitHub Actions / governed collector pointers
-> hash-bound machine outputs
-> main-framework accepted interpretation / ratification
-> current Master Monday / Cycle Navigator output
```

Manual user-submitted DATA PING is no longer the default upstream feed and is not a prerequisite for current Master Monday or Cycle Navigator production.

`02_DATA_PING/` remains valid for explicit DATA PING/RAW packet interpretation, replay/correction, historical lineage, source QA, collector diagnostics and protocol compatibility. When the task is explicitly a DATA PING/RAW task, its current packet contracts still apply.

Hard routing rules:

```text
CURRENT STATE -> FOLLOW CURRENT AUTONOMOUS POINTERS.
EXPLICIT DATA PING TASK -> USE DATA PING CONTRACTS.
DATA_PING IN A FILENAME/PATH -> DOES NOT MAKE IT CURRENT AUTHORITY.
```

Historical `data_ping_derived_*` files, old Custom GPT collector references, and `03_WEEKLY_OPERATIONS/master_monday/latest_master_monday.json` must not be promoted to current production authority unless a current operational surface explicitly routes to them.

For website fields such as `NEXT DAYS`, consume an existing current autonomous canonical output only when fresh, eligible and safe for the intended output surface. If none exists, fail closed rather than creating a parallel forecast engine.

### 0.2 Research to Codex fast intake

When a research thread, Deep Research review, audit or external review finds a reproducible bounded code defect, or the user says an equivalent of `sæt dette i Codex-køen`, load `.agents/skills/codex-intake/SKILL.md`.

Research may submit evidence but may not self-declare `CODEX_READY`. The governed path is:

```text
research finding
-> deduplicate against LATEST_CODEX_READY_TASKS.json
-> CODEX_RESEARCH_CANDIDATE_v1 on isolated branch/PR
-> research/codex/intake/YYYY/MM/<candidate_id>.json on main
-> event-driven Remediation Maturation Controller
-> CODEX_READY / NEEDS_MORE_EVIDENCE / DEDUPED_TO_HEALTH_TASK / REJECTED
-> fresh-state binding
-> bounded Codex PR
-> CI and review
-> merge
-> verification/completion receipt
-> execution ledger
```

A candidate merged to the intake path triggers remediation maturation immediately. It does not need to wait for the normal 05:45/17:45 reconciliation schedule. `EXPEDITED` affects queue ordering only and never bypasses evidence, authority, CI, review or post-fix gates.

The operational contract is `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`. If a research thread lacks GitHub write capability, it must return a schema-complete candidate payload and explicitly state that it was not persisted.

### 0.2a Development quality and PR release authority — owner-approved 2026-10-16

This is a constraint on the EXISTING Codex intake, Supervisor and GitHub PR/CI process, not a new executor, reviewer account, scheduler, queue or authority plane. For consequential code work, freeze owner/source contract, failure matrix, positive and adversarial negative cases before implementation; prove critical tests catch removed guards. No fabricated GitHub `APPROVED`, model-as-human impersonation, silent budget increase, portfolio action or private-data leak.

**Single-owner release rule (specific explicit owner override on 2026-10-16):** The repository owner has expressly withdrawn the requirement for an additional human GitHub reviewer/integrator as a universal condition for these already nominated PRs: #1622, #1626, #1627, #1629, #1644, #1645 and #1649. A release may be executed by the existing GitHub identity `Donh91` following the owner's authenticated authorization, with the exact resulting operation recorded as `SINGLE_ACCOUNT_OWNER_AUTHORIZED_MERGE`. This is not a formal nonauthor GitHub approval or autonomous self-merge permission. An automated queue, reviewer, Codex or Supervisor cannot authorize its own work; future releases require explicit owner mandate or a separately approved bounded release policy.

**Before an owner-authorized release:**
1. Re-read current `main`, exact 40-character PR head, actual GitHub rule/required-review/status state, changed files, active domain policies and required CI. Never bypass a real GitHub protection rule, push code directly onto main for the purpose of integrating a PR, grant extra permissions, or use a fake approval. Invoke only an existing integrator with the expected HEAD SHA.
2. Examine available non-writing technical review from independent models/agents as advisory evidence, including current/previous Codex findings; record any unavailable quota or pending review truthfully. The read-only `scripts/governance/check_codex_review_finality.py` may show `FINAL_TECHNICAL_REVIEW`, but `merge_authorized=false` remains correct and its two-pass census is NOT atomic with a GitHub merge. The owner's explicit authorization and real platform rules, not a mutable bot comment, control the release. Any concrete unmitigated P0/P1, reproducible evidence-corruption defect, unpaid/repeated billing exposure or absent required original evidence STOPS release regardless of consent. Record residual P2 issues rather than conceal them.
3. Enforce risk-adjusted existing tests, negative controls, integrity/policy authority and source-recovery separation. High-impact governance, source, workflow and payment changes require verified immediate safepoint and stronger evidence; no relaxation of canonical repository safety or the public/private data boundary. Keep `SEPARATION_OF_DESTRUCTIVE_AUTHORITY_UNVERIFIED` fatal for affected high-impact actions.
4. After merge, read back exact new main SHA, changed blobs and genuine scheduled producer/consumer evidence. Green CI is not a natural production readback; an unfinished follow-up remains `POST_FIX_OBSERVATION`.

**Automated merge policy:** A bot or unattended agent can never take a `COMMENTED`, stale exact-head review, earlier positive receipt or double-read comment census as release authorization. Existing review-event TOCTOU in PR #1649 remains a known limitation. Owner-directed integration does not claim to make it atomic; it simply does not base its authorization on those mutable bot events. No `gh pr merge --match-head-commit` can lock same-SHA comments, so purely bot-authorized merging remains blocked. After a separately HIGH_IMPACT-reviewed, explicitly owner-present-interactive-authorized and native-merged section 0.2c becomes effective, that **one** bounded S1 LOW original-PR policy is the explicit exception to the *per-PR owner mandate* requirement, not an exception to any native review, privacy, CI, recovery or source gate. Until that exact policy is on `main`, section 0.2a continues to prohibit unattended integration. An exact-head advisory model comment never grants authority by itself.

**Independent recovery invariant is unchanged.** The canonical `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md` still prohibits jointly destructive source/Vault authority, force pushing, branch/ruleset/credential changes by agents, destructive history rewriting and unreviewed source governance escalation. Internal safepoints are not independent external backups. Protecting main with a required-PR GitHub rule remains a separate project: current scheduled direct-main publishers must be migrated first; never silently give writers a bypass.

**Learning:** Use existing #1156 and operational receipts to record advisory code review defects, test evidence, exact head, owner authorization, actual merge, postmerge defects, real cost and producer/consumer closure. No new parallel metric or autonomous integrator.

### 0.2b S1 original-PR root-cause recovery and compounding learning (2026-11-05)

When the EXISTING Chat S1 Supervisor or an authorized operator is handling an original PR that repeatedly HOLDs, a genuine branch merge conflict, an unverified code/production closure, or an owner-scoped Sol MAX patch handoff, load `.agents/skills/s1-pr-repair-learning/SKILL.md` after `canonical-context-router` and before further repair or release claims. Use its source-pinned historical-fix retrieval, conflict-preserving branch repair, positive/adversarial tests, native merge/main/consumer readback, and procedural learning casebook. Existing #1156, S1 saved automation, GitHub review/merge rules and `AGENTS.md` remain authoritative. This routing creates no new executor, paid request, schedule, merge permission, CODEX_READY status, market authority or self-promotion. Record verified learning through the existing Operational Memory owner, not by editing generated LATEST or a chat-only summary.

### 0.2c Bounded unattended S1 LOW original-PR release, native rule proof (2026-11-12)

**Effective only after this policy is independently reviewed, qualified as HIGH_IMPACT, owner-authorized on its exact HEAD, merged through the existing native PR process and read back on `main`.** A draft, PR, comment, chat mandate or advisory classifier result does not activate it. This is the separately bounded release policy contemplated in section 0.2a, not an exception to GitHub or independent-recovery safeguards.

- **Principal and scope:** the SINGLE existing scheduled Chat S1 task `6ae5fd466b48819187abc224ec0f1c5f` may integrate qualified ORIGINAL Archive PRs classified LOW by independently authenticated exact-HEAD changed paths and domain impact. Exclude every release-sensitive path from `s1_release_evidence_classifier_v1.py`, all workflow/governance/security/source custody/credentials/private-boundary/public-private publication, wallet/trading/order/capital or paid changes, plus any unclear risk. The recipe named here, **all `00_FMOS/**`, `.agents/**`, `CLAUDE.md`, every file §0.2c relies on, `schemas/S1_*` and S1 governance classifiers/tests** are GOVERNANCE regardless of extension, NEVER unattended. So is **every file that a required job of `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` executes**: the two workflow files and the manifest's `required_job_executed_paths`, a list derived from those workflow files and their local imports and kept equal to the derivation by `scripts/governance/s1_standing_policy_v1.py --check` in native CI (Fable R4 B2: otherwise the lane could rewrite its own gates without touching `.github/`). A `.md` suffix cannot downgrade policy. Before any unattended release, the executable sensitive-path classifier update on original #2088 must be merged and verified; a proposed branch-only fix is not authority. These remain owner-specific HIGH_IMPACT or HOLD. No new bot, identity, approval, privilege, job, schedule or writer. Monday 09:30–10:30 Europe/Copenhagen stays strictly READ-ONLY.
- **Standing decisions are blobs on main (Fable R4 A2):** the rollout stage and every review waiver exist ONLY as the fields `lane_state` (`SHADOW` | `DOCS_ONLY` | `LOW_CODE`) and `review_optional_classes` of the manifest blob `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` reachable from current `main`. Scheduled S1 reads exactly those fields at the current main blob SHA and records that SHA. Only blobs on main carry standing decisions: an issue or PR comment, chat mandate, relay, PR-branch copy or model summary never does, whoever wrote it. A missing, unknown or unparsable value reads as `SHADOW` and no optional review. Changing either field is a HIGH_IMPACT governance PR whose exact HEAD needs the owner-present interactive decision below, so the owner factor is needed exactly once per change and never per LOW release.
- **Fresh native rules, no invented protection evidence:** use the source recipe in `00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md`. Read `GET /repos/Donh91/Investering-Framework-Archive-v1/branches/main` and paginated `GET /repos/Donh91/Investering-Framework-Archive-v1/rulesets?includes_parents=true&per_page=100&page=N` with current authenticated GitHub API connection. Read details for any potentially applicable active rule; distinguish `active`, `evaluate` and `disabled`. If `protected=false` and branch protection object explicitly says `enabled=false`, a 403 on the separate classic-protection detail endpoint does not, by itself, invalidate the branch-status evidence. A branch may report `protected=true` because of an active ruleset even when classic protection is ABSENT. Distinguish ruleset-only protection from classic branch protection: when `protection.enabled=false` AND a readable classic-protection GET returns an explicit `404 Branch not protected`, no classic settings are binding, but every active applicable ruleset remains binding and MUST be independently enumerated and complied with. If `protection.enabled=true`, fetch and enforce actual classic requirements. A `403`, ambiguous `404`, contradictory flags, incomplete ruleset details or unavailable actually binding protection ⇒ HOLD/owner escalation, not an invented empty census. Missing/partial pagination, malformed responses, non-main target, unknown inheritance, changing rules or 403 on a *needed* source means HOLD, never `native_rules_verified=true`. Disabled rule contents are not enforced.
- **Review/authorization (D2 variant S, proposed, owner selection pending):** only this policy (once effective) supplies the bounded unattended owner mandate for eligible LOW originals. Verify source/policy/current HEAD/conditional main fingerprints, native review count/threads, current applicable rules and unresolved P0/P1. EVERY unattended DOCS_ONLY or LOW_CODE PR requires an admissible independent *advisory* review at the exact HEAD (`requested_head_sha` must equal current HEAD) until BOTH (a) that class has at least three independently audited, verified, genuine unattended S1 merges with zero identified false READY and (b) the tested `S1_DIFF_SCAN_V1` privacy scanner is merged and effective, AND the owner explicitly makes a new owner-present interactive class-specific review-optional decision naming the effective AGENTS policy blob SHA and independently verified auditor receipt. That decision takes effect only when a HIGH_IMPACT PR carrying it is merged and the class appears in `review_optional_classes` of the manifest blob on main; the #1156 log entry is a record, never the authority (a GitHub app/PAT comment proves nothing). Until that blob is on main the independent review is mandatory. A nonblocking review is never a native GitHub APPROVED review; native required reviews and unresolved threads continue to bind. Claude or Codex comments are advisory; a missing/stale `requested_head_sha`, or an unresolved adverse independent finding, fails closed. No fabricated GitHub review, approval or release permission.
- **CI proportionality:** obtain required native `pull_request` event check/workflow/job/step receipts bound to the exact current HEAD (or a governed verified merge ref), with verified job identities and substantive executed test steps. For DOCS_ONLY require the existing applicable generic gates, not nonexistent newly added tests. For CODE require proof that any changed runnable tests execute on hosted CI; if absent HOLD (IC-1/#2088 must pass its own HIGH_IMPACT qualification first). Green `workflow_dispatch` or combined status alone never establishes this. A queued/unstable run means WAIT or a specific CI repair, never READY.
- **Action and readback:** `mergeable_state=clean` plus non-draft and no unresolved thread is necessary, never sufficient. Re-read current rules, PR HEAD/main, CI, review, source/custody and writer lease in the same eligible tick. Merge only through existing GitHub API with `sha=expected_head`, no bypass, and classify a 405/409/failed response as STOP with its actual reason. After success read back native merge actor, commit, current main ancestry, all changed blobs, and separately the natural producer/site/consumer outcome. `POST_FIX_OBSERVATION` is not `PROD_VERIFIED`.
- **Owner-authenticity gate (Fable Round3 F1 + Codex P1):** NO GitHub REST issue comment can independently prove a human clicked the UI: `performed_via_github_app:null` also occurs for owner personal-access-token API calls, so a matching `user.login=Donh91`/`author_association=OWNER`/body hash is **only NON_APP_COMMENT_CANDIDATE, never proof of owner consent**. The one-time activation of §0.2c, each HIGH_IMPACT release, and any later D2 independent-review waiver **must occur only in an explicitly owner-present INTERACTIVE authorization context** (a fresh direct user-role decision identifying exact PR HEAD, proposed AGENTS policy blob, variant and scope, evaluated by the interactive operator; never a Grok/Claude/ChatGPT-generated relay) OR through independently validated offline owner-key signed attestation whose signing key is inaccessible to the scheduled S1 principal. The current scheduled S1 must NOT infer/verify human presence from GitHub metadata, a boolean, another bot's summary or remembered chat. Human owner may authorize a one-time HIGH_IMPACT merge interactively under current §0.2a, with the decision transparently labeled OWNER_INTERACTIVE in #1156. The advisory `scripts/governance/s1_owner_ui_attestation_v1.py` validates only syntax/native non-App provenance; its result remains `authorized:false` and `human_only_factor_verified:false`. Once an owner-interactively authorized §0.2c is actually merged and read back on main, the *standing bounded policy*, not a new owner comment, covers its qualified LOW releases. D2 class-specific waivers require the same new owner-interactive choice and a native auditor-evidence URL, with real audit and three independent scheduled merges checked separately. If no independent human interaction is available, HOLD/OWNER, never invent approval.
- **Receipts and evaluation:** on a genuinely material transition add one deduplicated source-bound receipt in existing original #1156, including scheduled task run ID when independently available, request/comment source IDs, native rule GET source/UTC, review/CI HEAD, selected action, exact merge/main blobs, truthful actor class and objective next trigger. Never count owner-interactive merges as scheduled. Repeated identical HOLD does not create a receipt. Run one docs-only LOW safe positive trial with no owner prompting, then compare 7/28-day qualified original S1 closure and false READY/HOLD using real task-run provenance. If no authenticated scheduled trial exists, adoption remains UNPROVEN.
- **Complete diff and privacy gate, required for EVERY unattended LOW release:** authenticate the original PR's complete paginated changed-file list and `GET /pulls/{n}` `changed_files` bound to the same current HEAD, require equal length, no duplicates and at most 3,000 files; partial/unknown enumeration cannot become READY. `S1_DIFF_SCAN_V1` must be MERGED, native exact-HEAD run-bound, assess the entire diff plus PR title/body and generated public output when implicated, and return `NO_RESTRICTED_CONTENT`, including tests against leaked private design without token-like patterns. Binary/oversize/inaccessible or unknown public/private provenance → HOLD. Neither a model assertion nor generic green CI substitutes for the scan. The scanner is NOT BUILT at proposal time, so no RP1 READY may be claimed before implementation and test evidence.
- **D3, conservative review reuse across main drift:** independent review evidence is tied to exact PR HEAD and review-time main SHA. For DOCS_ONLY it may be reused iff ALL hold: (a) the complete native change census from review-time main to current main is proven disjoint from all PR paths and rename sources; (b) no policy file is in that census and each policy blob is proven identical at both mains: `AGENTS.md`, the recipe, the manifest, the S1 release classifier, the `S1_DIFF_SCAN_V1` scanner and the standing-policy reader (`review_reuse.policy_blob_paths`); (c) the same holds for the required-job workflow files and every `required_job_executed_paths` entry. The class of the unrelated drift paths is NOT tested (Fable R4 K1/G3: a class test rejected 36–67 % of honest attempts on producer commits and its ordering masked unclassified paths). LOW_CODE never reuses: re-review on current main. `review_reuse_decision` in `scripts/governance/s1_standing_policy_v1.py` evaluates the rule and is advisory. An incomplete census, an unproven blob, unknown or conflicting history, or a changed review comment ⇒ re-review on current material fingerprint; do not silently waive a required native GitHub approval.
- **D4, honest optimistic concurrency (NOT an exclusive lease):** record `active_writer_lease:null` when no authenticated lease registry exists. In the eligible tick obtain two identical live current PR HEAD reads, no observed foreign active conflicting writer, and call native merge with exact expected HEAD. `active_writer_lease:false` may be recorded only with authenticated lease evidence. A stale HEAD or 405/409 rejects the action; no blind retry, assumed exclusive writer or admin bypass.
- **D5/D6, proportionate executable CI:** `source_science_gate:NOT_APPLICABLE_BY_PATH` is permitted only for genuinely DOCS_ONLY, NON-scientific documentation; research/market/forecast publications under `04_MARKET_LEARNING/`, `04_RESEARCH_LAB/`, `05_CYCLE_NAVIGATOR/`, `06_RESEARCH_LAB/`, `research/` (the manifest's `science_gated_prefixes`) require their original source/science owner gate regardless of `.md` suffix. Changed runnable tests need either exact executed test IDs or an authenticated non-collect-only, unmasked native PR-event job step whose source was read at that run's commit SHA and whose scope covers the test. Shell `.sh` tests need an exact executed ID, not only directory scope; nested conftest/fixtures cannot be silently treated as executed tests. All required CI remains exact HEAD.
- **D7/D8/D9 and rollout:** `.agents/**` always GOVERNANCE_WORKFLOW, never unattended. An advisory review comment used as evidence must be re-read immediately before merge with identical `updated_at` and SHA256(exact body). Three identical evidence-dependent RECHECK outcomes at the same PR HEAD trigger ONE deduplicated escalation to original #1156, not another identical hourly HOLD. RP1 opt-in and only after separate governed merge of classifier/receipt patches and production evidence connectors: at least 24 hours SHADOW (no merges), then independent owner go for DOCS_ONLY (a merged `lane_state: DOCS_ONLY` on main) only after a genuine qualified positive candidate and 95% receipt completeness, then at least one truly unattended DOCS_ONLY merge + independent audit and seven days of zero false READY before any owner decision on LOW_CODE; HIGH_IMPACT/public-data-integrity/private-paid/unknown remain owner-interactive. No docs-only original available today means `NO_POSITIVE_TRIAL`, not invented work.
- **Fable F3 bypass and rule-race control:** `current_user_can_bypass=always` is *not* authorization to bypass any rule; use only native merge without a bypass argument. Immediately before a merge read all ruleset pages **twice through an explicit empty final page**, normalize each `(id,target,enforcement,updated_at)` into a sorted SHA-256 snapshot and verify no change from the earlier qualification snapshot. Re-read branch protection and current HEAD; if any active applicable rule exists for which the integrator has bypass authority but complete compliance cannot be independently proven, HOLD/OWNER. GitHub 405/409 is not a trusted safety net for a bypass-capable owner identity. Two API reads are not atomic, so do not claim they eliminate a rule-race; after merge inspect native rule evaluation/bypass evidence, and classify any bypass or source drift as false READY, STOP further unattended releases, and execute the kill rule. Only the human repository owner may change bypass permissions/rulesets.
- **Fable F5/F7 CI and rule evidence mapping:** require the current-main blob of `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` for DOCS_ONLY/LOW_CODE. It supplies the unique workflow path + job ID tuples (not ambiguous names); all listed jobs must have native PR-event SUCCESS and substantive executed steps on the exact HEAD, and runnable changed code/tests require additional source-bound affected-test execution. Missing manifest, path-trigger mismatch, duplicate job identity or unexecuted job ⇒ HOLD, never assume that no GitHub-required status checks means no tests. Bind ruleset census to `rule_census`: disabled/evaluate entries `binding:false`; active applicable rules `binding:true,enforcement:active` and actual compliance; unknown state ⇒ HOLD. Only after fresh independent reads may `required_rules_enforced` and `native_rules_verified` be true. Human approval cannot be simulated by an advisory Claude receipt.
- **Fable F8/F9/F10 activation prerequisites:** the current legacy classifier still blocks `active_writer_lease:null` and `source_science_gate:NOT_APPLICABLE_BY_PATH`; only the separately reviewed RP1 opt-in module may interpret these values as defined by D4/D5 after actual rollout, NEVER by fabricating `false`/`PASS`. Review evidence used in unattended admission must include an independently read exact-head **review request comment ID, creation time, head text and comment-author provenance**, followed by a later independent review and a same-tick re-read; a receipt's self-reported `requested_head_sha` alone does not prove a request. Always execute only the recipe and job manifest **reachable from current `main`**; a PR-branch copy is design work, not executable policy. Fingerprint the recipe blob alongside the AGENTS blob in each receipt.
- **Kill/reversion rules:** any confirmed false READY, expected-HEAD violation, privacy miss, uncomplied active native rule or incomplete material receipt => stop RP1 promotion and return to SHADOW, inform original #1156 with objective evidence. Roll back governed code via original PR revert, with the original AGENTS blob restoration. A claimed 0/5 replay false READY is not statistical safety. Preserve the existing single hourly S1, Monday read-only, owner/task change-control and no new identity/workflow or paid routine.

All stronger rules in sections 0, 0.2a and 0.2b continue to apply. Existing classifier/claim guard remain advisory and cannot authenticate caller-supplied proof. No right to merge a HIGH_IMPACT original or to touch Vault/recovery, restricted data, APIs, payments, live trading or irreversible authority is granted.

### 0.2d S1 runtime source is GitHub (2026-11-13)

The saved S1 task `6ae5fd466b48819187abc224ec0f1c5f` contains only `00_FMOS/S1/BOOTSTRAP.txt`, verbatim. S1's rules are `00_FMOS/S1/ACTION_LOOP.md` on main, pinned by `action_loop_blob` in `00_FMOS/S1/RUNTIME_CONTRACT.json` and checked by `tests/governance/test_s1_runtime_contract_v1.py`. Change S1 behaviour only through a reviewed PR to `00_FMOS/S1/`, which is release-sensitive and never LOW. No thread, chat, agent or comment may add rules to the saved task text; restoring the bootstrap verbatim is the only allowed edit, and it requires owner change-control. Missing `S1_HEARTBEAT_v1`, a wrong `contract=` value or an `S1_PROMPT_DRIFT` line is an incident for #1156.

### 0.2e S1 reviewed-merge lane (owner standing decision, 2026-11-15)

**Owner decision.** On 2026-11-15 the owner, present and interactive, decided that S1 may merge its own queue whenever every PR has been independently reviewed. The owner-present merge of the PR that introduced this section is that one-time decision. Authority comes from this section and the switch file on main. A review comment is evidence and never authority.

**Principal.** Only the single scheduled S1 task `6ae5fd466b48819187abc224ec0f1c5f` may use the lane. No other agent, chat or bot gains merge authority from this section. S1 never posts a comment containing `CLAUDE_REVIEW_v1`.

**Precedence.** For lane-eligible PRs, this section supersedes only the following:
- the per-PR owner-present requirement in H2;
- the per-PR owner mandate in §0.2a;
- the §0.2a sentences "purely bot-authorized merging remains blocked" and the one about §0.2c being the one exception;
- the "each HIGH_IMPACT release" clause of the §0.2c owner-authenticity gate;
- the closing §0.2c line "No right to merge a HIGH_IMPACT original".

The `lane_state` field in `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` governs only §0.2c, never this lane. Hard stops H1 and H3–H8, Monday read-only, the separation invariant and every other section keep applying.

**Lane state.** The lane is ON only when all four checks pass in the tick:
1. **Switch.** `00_FMOS/S1/REVIEWED_MERGE_LANE.json` on main has `"contract": "S1_REVIEWED_MERGE_LANE_v1"` and `"state": "ON"`. A missing, unknown or unparsable file, or any other value, reads as OFF. A `max_merges_per_tick` that is not an integer from 1 to 3 reads as 1.
2. **Authority integrity (content pins).** Each entry in the switch file's `pins` equals current main:
   - the blob SHAs of `AGENTS.md` and `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json`;
   - the tree SHAs of `.github`, `.agents`, `scripts/governance`, `scripts/health`, `07_PROMPTS_AND_AGENTS` and `01_CORE_FRAMEWORK/governance`, read from the parent directory listing.

   Any change to a pinned path turns the lane OFF, however the change arrived (direct push, backdated commit, or a PR merged by a token) and whatever the commit order. A legitimate change to a pinned path is lane-excluded. It needs an owner-present PR that also updates `pins`, and the CI test `test_s1_reviewed_merge_lane_v1.py` fails any PR whose pins do not match its own tree.
   - Every PR touching `00_FMOS/S1/` or a pinned path is squash-merged from a branch that is up to date with main.
   - `00_FMOS/S1/**` is protected by the S1 bootstrap.
   - **Accepted residual risk:** `00_ARCHIVE_CONTROL/**` is lane-excluded but not pinned, because it changes often.
3. **No standing halt.** #1156 holds no `S1_LANE_HALTED` by `Donh91` newer than the lane's last enable. A re-enable is only a squash-merged PR, merged by `Donh91` (type User) but not by S1, whose switch file sets `"clears_halt"` to the comment id of the newest halt. The switch path is lane-excluded, so S1 can never merge it. Any other commit to the switch file is not a re-enable.
4. **Main health.** The most recent completed scheduled run of `automation-production-health.yml` on main concluded SUCCESS, and it completed within the last 26 h.

**Owner decision 2026-11-16: only OWNER_GATED changes need the owner.** The owner decided that S1 merges every reviewed PR itself, except OWNER_GATED changes (shown to the owner as HIGH_IMPACT). The lane-excluded list below is exactly the OWNER_GATED list, and it includes the gates' own code: every file that a required gate job executes, imports or reads. S1 never merges an OWNER_GATED change; it announces it to the owner as OWNER APPROVAL REQUIRED (see `00_FMOS/S1/OWNER_VISIBILITY.md`). The risk classes HIGH and HIGH_IMPACT of §0.2a keep their meaning.

**Lane-excluded (OWNER_GATED) changes.** These still need an owner-present decision at the exact head. A rename counts as a change to both `filename` and `previous_filename`.
1. **Authority, governance and canonical policy:**
   - every path matching the manifest's `governance_prefixes`, `governance_exact_paths` or `required_job_executed_paths`. That covers `.github/`, `.agents/`, `00_FMOS/`, `scripts/governance/`, `research/api_agent/`, private, vault and secrets paths, `AGENTS.md`, `CLAUDE.md`, and every file a required job executes. Research code and tests that only run in workflows outside the required gate jobs stay lane-eligible unless another item applies;
   - **Gate isolation (owner addition 2026-11-16).** While `00_FMOS/S1_WORKFLOW_ISOLATION_V1.json` on main reads `"gate_isolation": "LIVE"` (true only when the privacy scan and the execution-truth check run in their own isolated jobs, as `tests/governance/test_s1_workflow_isolation_v1.py` proves), the `required_job_executed_paths` entries outside `governance_prefixes` and `governance_exact_paths` are lane-eligible, because the gates' evidence no longer comes from a job that runs them. Every other item still applies;
   - `07_PROMPTS_AND_AGENTS/**` and `**/*__canonical.*`;
   - any path containing `BOUNDARY` or `AUTHORITY`.
2. **The lane's own CI and what the gate jobs read:** `scripts/health/**`, the storage gate's own code and policy (`scripts/data_governance/**`, `scripts/data_storage/**`, `tests/data_governance/**`, `tests/data_storage/**`, `research/data_governance/**`), `**/conftest.py`, pytest configuration (`pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`), `requirements*` files, and every Python import-shadowing surface: any root-level `*.py`, any `sitecustomize.py`, `usercustomize.py` or `*.pth`, and any added or changed `__init__.py` under `tests/` or `scripts/`; any added Python file whose module name equals a Python standard-library module or an installed top-level package (for example `csv.py`, `json.py`, `pytest.py`), and any added Python file in a directory that holds a `required_job_executed_paths` file or that a gate-job test puts on `sys.path` (for example `scripts/research/`, `tests/research/`).
3. **Secret-using code:** every path in the `secret_job_executed_paths` derived at the PR head and at main by `scripts/governance/s1_workflow_isolation_derive_v1.py` (the union of both derivations of the code that every workflow job receiving a secret runs or imports, published per PR in the S1_TICK_BRIEF_V1 field `isolation`) and, as before, any other file that such a job runs, imports (also through a `sys.path` insert) or reads as config; without that derivation for main and for the head, unknown is OWNER_GATED. A job that receives no secret does not make its files secret-using, even when another job of the same workflow does (isolate instead of exclude).
   - Accepted residual risk: code that write-token data-writer jobs run without secrets stays lane-eligible after independent review, provided exclusion 10 does not apply. Several controls stop it from changing S1's rules:
     - the content pins and the bootstrap catch any rule change, however it arrives;
     - exclusion 10 stops it from gaining new repository-write calls;
     - the reviewer checks for token abuse.

     It could still damage data. Independent review and the halt triggers are the controls for that.
4. **Custody:** credentials or secrets, Vault, recovery or backup, rulesets, branch protection, repository settings.
5. **Money:** live trading, order execution, wallets, fund movement, a new paid API call, any raise of a spend cap or cut of a budget reserve.
6. **Privacy:** the public/private boundary, or publication of private-plane data.
7. **Deletion:** deleting, moving away or truncating any tracked file outside `scripts/` and `tests/`. This covers data, ledgers, receipts and episode history.
8. **Round 3:** Round 3 data or analysis.
9. **Risk class:** EXTREME risk, or any change whose class is unclear.
10. **Repository writers:** any added or changed line that runs `git` write commands (`push`, `commit`, `tag`, `branch`, `merge`) or `gh`, or that calls the GitHub API (`api.github.com`, `/pulls`, `/merges`, `/git/refs`, a contents `PUT`), or that reads `GITHUB_TOKEN`, `GH_TOKEN` or the checkout credential, or that invokes an existing helper or workflow step that does so, or that reads or writes anything under `.git/` or sets `core.hooksPath`, `git config` or a `GIT_` environment variable. Code may not gain repository-write abilities through the lane.
11. **Gate forgery:** any added or changed line that contains `S1_NATIVE_PRIVACY_SCAN_STEP_V1`, `GITHUB_STEP_SUMMARY`, `GITHUB_OUTPUT`, `GITHUB_EVENT_PATH`, `full-repository-tests.xml` or `junitxml`, or a text file whose patch S1 cannot read. Code may not print, write or redirect the evidence the gates produce.

**Gates.** All are checked natively in the merge tick, and all are required.
- **(a) Head and diff.**
  - The PR is non-draft and its head is read twice, identically.
  - The complete paginated changed-file list matches `changed_files` for that head, and no change on it is lane-excluded.
- **(b) Privacy.** The job log of the isolated job `data-architecture-gate.yml` / `privacy-scan` (no fallback: without that job on main, HOLD) for the exact head contains EXACTLY ONE line beginning with `S1_NATIVE_PRIVACY_SCAN_STEP_V1`, and that line begins with `S1_NATIVE_PRIVACY_SCAN_STEP_V1 result=NO_RESTRICTED_CONTENT head=<exact head>`. Zero or several such lines mean HOLD.
  - If S1 cannot read job logs, the CLAUDE_REVIEW_v1 must carry `privacy_scan: NO_RESTRICTED_CONTENT run=<run id>` for that head. S1 then confirms that the run belongs to the head.
  - Any other result, or no evidence, means HOLD.
- **(c) CI.**
  - Every check run on the exact head is SUCCESS, NEUTRAL or SKIPPED, and none is pending or failed.
  - These three jobs are SUCCESS:
    - `data-architecture-gate.yml` / `gate`;
    - `storage-health-gate.yml` / `storage-health`;
    - `automation-production-health-gate.yml` / `test`, with its full-suite step having run;
    - the isolated job `automation-production-health-gate.yml` / `execution-truth` (no fallback: without that job on main, HOLD).
- **(d) Review.** An admissible independent review of the exact 40-character head under §0.2f: a Codex review, a `CLAUDE_REVIEW_v1`, or (within the §0.2f limits) an `S1_SPECIALIST_REVIEW_v1`, in that order. When it is a `CLAUDE_REVIEW_v1`, the newest one for that head meets all of the following:
  - it is on Bridge #173 and authored by `Donh91`;
  - its verdict is APPROVE;
  - it answers an earlier exact-head `S1_REVIEW_REQUEST_v1` and cites that request's comment id;
  - it states `lane_eligible: YES`, which is the reviewer's own check against the exclusions above;
  - it states `INDEPENDENT_DETACHED` when the head implements a Claude-authored package, meaning a separately launched reviewer that did not author the content;
  - it is unedited (`updated_at` equals `created_at`);
  - it cites `report_blob` and `bridge_commit`, and the report at that blob on Bridge `claude/log` names the same head with verdict APPROVE and `lane_eligible: YES`;
  - it is re-read immediately before the merge with an identical body.

  A native GitHub `CHANGES_REQUESTED` review on that head voids the review of every kind.

  **Accepted residual risk:** this authentication is behavioural, not cryptographic. Claude, S1, ChatGPT threads, Codex and Grok can all post as the owner account.
- **(e) Findings.** There is no unresolved P0/P1 from any reviewer, Codex included.
- **(f) HIGH evidence.** For HIGH or HIGH_IMPACT risk, HIGH EVIDENCE (Recovery and Separation) passes at merge time.
- **(g) Merge and readback.**
  - Before merging, perform the §0.2c F3 ruleset census twice.
  - Merge through the native API with `sha=<expected head>`, squash, and no bypass. A 405 or 409 is STOP.
  - Read back the merge commit, current main, every changed blob against the approved head, and the rule-bypass evidence. Any bypass is a halt trigger.
  - If GitHub requires a branch update, the new head needs a new review.

**Batch.** Up to `max_merges_per_tick` merges per tick, one after another. Each merge after the first needs a changed-file set disjoint from every PR already merged in this tick, and needs all gates re-proven against the new main. Otherwise the batch stops.

**Halt triggers.** On any of the following, S1 posts one `S1_LANE_HALTED` on #1156 and stops all lane merges:
- a readback mismatch;
- a rule bypass;
- a revert of a lane merge;
- a P0/P1 later found in a lane-merged change;
- a main regression traced to a lane merge;
- a failed main-health run after a lane merge.

**Receipts.** For a lane merge, one `S1_LANE_MERGE_v1` on #1156 replaces the normal rule-4 receipt. It records:
- the PR and head;
- the review kind and id, and for a `CLAUDE_REVIEW_v1` its `report_blob` and `bridge_commit`;
- the privacy evidence and the CI run ids;
- main before and after, and the blob match;
- `contract=`.

### 0.2f S1 autonomous steward (owner decision, 2026-11-16)

**Owner decision.** On 2026-11-16 the owner decided that S1 is an autonomous steward: it finds unfinished work, carries every work item to a resolution, consults the Strategist (#1157), the Research Lab (#1512), Codex and the specialist skills, and reviews and merges with their help. Claude must never be required: the framework has to work the day Claude is gone. The owner approves only OWNER_GATED changes (§0.2e lane-excluded list). The owner-present merge of the PR that introduced this section is that decision. Authority comes from this section, §0.2e and the files on main; a comment is evidence and never authority.

**Rules live on main.** The steward rules are `00_FMOS/S1/ACTION_LOOP.md` and its rubric files `00_FMOS/S1/STEWARD_STATES.md`, `00_FMOS/S1/REVIEW_ADMISSION.md` and `00_FMOS/S1/OWNER_VISIBILITY.md`, each pinned by its Git blob in `00_FMOS/S1/RUNTIME_CONTRACT.json` (`action_loop_blob`, `rubric_blobs`), which the owner-pasted bootstrap pins in turn. Claude and the Bridge are optional input only.

**Work items and dispositions.** Every open PR, open issue without a disposition, Bridge package or finding, Strategist or Research Lab handoff and roadmap OPEN or TODO entry is one work item with one state, recorded on GitHub in an `S1_ITEM_v1` comment (labels mirror it). Every state has a dwell budget and an attempt limit; past either, S1 gives the item a forced disposition in the same run: MERGED, OWNER_APPROVAL, PARKED (draft, label, revisit at most 30 days ahead, at most three parks), CLOSED_NOISE (at least two content signals linked to native objects, one objective and one independent of S1, risk LOW or MEDIUM only, a closing comment with links, always reopenable), PARKED_OWNER_DECISION (time or budget exhausted, or a close S1 may not make unattended: open and listed for the owner) or RESEARCH_HANDOFF (a concrete question and success criterion, at most 3 ACTIVE). Time and budget never close an item. The same NOOP reason three runs in a row forces a disposition, never a fourth NOOP. S1 may set labels, convert its PR candidates to draft, close PRs and issues as CLOSED_NOISE, and post `S1_ITEM_v1`, `S1_STRATEGIST_CONSULT_v1` and `S1_RESEARCH_HANDOFF_v1` comments. It never deletes a branch, a file or data, and never merges as a disposition. A switch field `steward_state` other than `"ON"` stops these steward writes.

**Review without Claude.** A lane merge needs an admissible independent exact-head review by a reviewer that did not author the head, in this order: (i) a completed Codex review with no P0/P1/P2 finding, under the rule of `scripts/governance/check_codex_review_finality.py`, inadmissible when Codex authored the head; (ii) a `CLAUDE_REVIEW_v1` as in §0.2e gate (d); (iii) an `S1_SPECIALIST_REVIEW_v1` that applies a named `.agents/skills/` rubric item by item; it is a preflight by the merging agent and counts as the review only for risk LOW documentation or research-note changes with green CI, only when Codex is silent past its budget or inadmissible, and never for a head that S1 authored. Risk MEDIUM, HIGH and HIGH_IMPACT need Codex on a head it did not author or a detached `CLAUDE_REVIEW_v1`. S1 authorship is mechanical: an `s1/` branch, an `S1-Authored-By: 6ae5fd466b48819187abc224ec0f1c5f` commit line, or an S1 receipt naming the commit; an unreadable commit list counts as S1-authored. No author reviews its own work. Risk HIGH and HIGH_IMPACT need Codex or Claude and HIGH EVIDENCE. No independent review within the review budget leads to a disposition, never a merge. Direction changes (a new research program, a feature removal, a change of priorities) also need a Strategist `CONCUR` on #1157 at the head. A specialist receipt is only a record: S1 re-derives every rubric item itself in the merge run. A forged comment can never cause a merge or a close: S1 never lowers a risk or kind that any comment states, and reads counters only from receipt-backed S1 items.

**Isolate instead of exclude (owner addition 2026-11-16).** The owner wants harmless changes to code that shares a workflow with a secret (the #2145 case) to merge without the owner. The rule is isolation: secret-receiving steps run in their own jobs on main, gate evidence comes from isolated jobs, and `tests/governance/test_s1_workflow_isolation_v1.py` keeps that true and keeps every write-scoped job that can run on `pull_request` on a shrink-only debt list. Exclusions 1 and 3 above then shrink mechanically. A HIGH EVIDENCE hold blocks only HIGH and HIGH_IMPACT risk merges, never LOW or MEDIUM lane merges. After a halt S1 opens the re-enable switch PR itself; the owner's step is one squash merge and one bootstrap paste.

**Owner visibility.** Every S1 run starts with three lines: `OWNER APPROVAL REQUIRED:` (entries, `NONE` or `UNKNOWN (<why>)`, including `LANE_OFF(...)` and `pkg<id>:manual_only` entries), `HIGH_IMPACT BLOCKED:` and `DISPOSITIONS TODAY:`. `OWNER_APPROVAL_REQUIRED_v1` on #1156 is posted when the set changes, with the exact owner click. A separate owner-created ChatGPT task, the only new schedule this section allows, posts one Danish `S1_DAILY_SUMMARY_v1` on #1156 at 20:40 Copenhagen, read-only otherwise, following `00_FMOS/S1/OWNER_VISIBILITY.md` through `00_FMOS/S1/DAILY_SUMMARY_BOOTSTRAP.txt`.

**Unchanged.** Hard stops H1 and H3–H8, Monday 09:30–10:30 read-only, the Round 3 firewall, the separation invariant, one S1 identity, no Vault or recovery dispatch or write, no live trading, no publication of private-plane data, no credentials, and every §0.2e gate. **Accepted residual risk:** every agent except Codex posts as the owner account, so authorship and answers are behavioural evidence; Codex and S1 are both OpenAI models, and Codex counts as independent because it is a separate agent with its own context and a platform-authenticated identity.

**Kill switch and rollback.** An owner-present switch PR that sets `"state": "OFF"` stops lane merges and `"steward_state": "OFF"` stops steward writes. Rollback is a revert of the PR that introduced this section plus a re-paste of the previous `00_FMOS/S1/BOOTSTRAP.txt`.

### 0.2g S1 v3 evidence bindings and edge ledger (owner release of S1 v3)

**Effective only by the owner-present squash merge of the PR that adds this section.** It changes no gate of §0.2c, §0.2e or §0.2f and grants S1 no new merge, write target, schedule, identity or waiver. It adds proofs S1 must hold before it acts and records S1 must leave after it acts. The rules are `00_FMOS/S1/EVIDENCE_BINDINGS.md` and `00_FMOS/S1/EDGE_LEDGER.md`, pinned in `rubric_blobs` like every other S1 rubric. Source: the Astra S1 vNext review archived under `06_RESEARCH_LAB/astra_program_20261116/results/s1_vnext/` (fixes 4, 6, 7, 9, 12, 14) and the edge plan.

- **Identity before writes.** S1 proves the repository id, the PR's base and head repository ids, the exact head ref and the full head SHA before any write or merge. A fork PR is never written to and never lane-merged; it is OWNER_GATED.
- **One writer, Codex first.** One writer per PR branch. Codex is the default writer for repairs on branches S1 did not create. S1 writes only under a visible `S1_WRITER_LEASE_v1` that the rubric allows it to claim, with an expected-parent precondition. H7 is unchanged: an unanswered `@codex address` request blocks S1 without a time limit, silence releases nothing, and no comment by another party releases a writer's lease. A lease is an agreement, not a lock.
- **Durable operations.** Every multi-write operation posts an intent first and an outcome after its readback. An intent without an outcome stays open and is reconciled from native state under its own binding, however old it is and whatever contract posted it. Reconciliation only reads and posts receipts: it never creates a branch, a commit or a PR and never merges. A reconciled merge is natively verified but is never credited as S1's own scheduled merge; a missing receipt field is an evidence gap, not a closure.
- **CI identity.** A required job is proven as workflow path + job + latest run attempt + head SHA + executed must-run steps in this repository on the `pull_request` event, never by a display name or a combined status.
- **Privileged execution closure.** `00_FMOS/S1_WORKFLOW_ISOLATION_V1.json` also lists writer and token jobs, artifact inputs of privileged jobs and action references. What secret, writer and token jobs execute, the non-code files they name and unresolved dynamic edges are derived at the PR head and at main by `scripts/governance/s1_workflow_isolation_derive_v1.py` (the union), published per PR in the S1_TICK_BRIEF_V1 field `isolation`. Exclusion 3 includes at least the secret lists; writer-run code and the files writers name are risk HIGH at least; the judgment rule of §0.2e exclusion 3 still applies on top, an unknown edge is never read as an empty closure, and unknown is OWNER_GATED.
- **Consumer closure.** A merge is not a closure. Each lane merge gets an `S1_CLOSURE_v1`; only an `S1_CONSUMER_COMPLETION_v1` receipt of the natural producer run, the persisted object and the consumer readback makes it VERIFIED. S1 never dispatches or reruns a workflow to obtain that observation (§4a stays binding for producer incidents).
- **Main health route and containment (first live audit of v2.2, Bridge #173 comment 6948786347).** The two main-health facts of §0.2e (lane state 4, and the halt trigger of a failed main-health run after a lane merge) are unchanged. When S1's tool cannot fetch the workflow-specific route, S1 may prove the same two facts over the repository-wide scheduled-run list, with a complete pagination census, the same strict path, event, branch and repository filters and a direct re-read of the run; an incomplete reading is NOT PROVEN. S1 checks the lane state once per run before the first candidate, and a tool error inside one step is that step's NOT PROVEN reason, never the end of the run: the non-merging rules still run while the lane is off.
- **Edge ledger.** A research stream counts only with a preregistration on main before its window, an identical-clock baseline, weekly anytime-valid evidence and mechanical gates (minimum sample, minimum effect, futility, harm, maximum sample). S1 posts one `S1_EDGE_DECISION_v1` per stream per week on #1512 and never states an edge the ledger has not decided. No stream reads Round 3 data, and a promotion that touches a product surface is its own gated PR.

S1 may post the comment types these rubrics name (`S1_OP_INTENT_v1`, `S1_OP_DONE_v1`, `S1_WRITER_LEASE_v1`, `S1_WRITER_RELEASE_v1`, `S1_CLOSURE_v1`, `S1_CONSUMER_COMPLETION_v1`, `S1_EDGE_DECISION_v1`). **Rollback:** revert the PR that added this section and re-paste the previous `00_FMOS/S1/BOOTSTRAP.txt`; open intents posted meanwhile stay on #1156 as evidence and are simply no longer reconciled.

### 0.2h S1 v3.1 tick brief (owner release of S1 v3.1)

**Effective only by the owner-present squash merge of the PR that adds this section.** It grants S1 no new merge class, write target, schedule or identity and removes no gate of §0.2c, §0.2e, §0.2f or §0.2g. It changes WHO performs some reads: a GitHub-native workflow prepares them, and S1 verifies that workflow's output and re-reads the facts below itself before it acts. Reason: the scheduled v3 ticks of 2026-11-17 ended `PREFLIGHT_INCOMPLETE` because the S1 runtime spent its tool budget on reading before its first decision. The procedure is `00_FMOS/S1/TICK.md`, pinned as `tick_blob`.

- **Tick brief.** `.github/workflows/s1-tick-brief.yml` runs only on schedule and manual dispatch on main and uses no secret. Its reading job holds read permissions only and never executes PR code; its second job holds `issues: write` and writes one issue. It runs `scripts/governance/s1_tick_brief_v1.py` and publishes one `S1_TICK_BRIEF_V1` as the body of the single open issue labelled `s1-tick-brief`. Read natively with complete pagination, it holds: main and the S1 pin chain; the four lane-state checks of §0.2e; the F3 ruleset census (two reads); and for every open non-draft PR the exact head, the job tuples and must-run steps of §0.2g, the single privacy line, the §0.2e exclusions that are a function of the diff (1, 2, 3, 7, 10 and 11), the Codex review state, and one ranked next action.
- **Evidence, never authority.** A brief is used only when all hold: its issue is the only open one with the label and is authored by `github-actions[bot]`; its `run_id` is a successful run of that workflow path on main at the brief's main SHA; the issue was last written inside that run (`run_started_at` ≤ `generated_at` ≤ issue `updated_at` ≤ run `updated_at`, so a later edit by anyone is visible); it is at most 45 minutes old; its pins are intact. The drift rule of the lane (ACTION_LOOP C1b) is applied to the commits between the brief's main and current main.
- **What S1 still reads itself in the merge run.** For gates (b) and (c) of §0.2e the workflow's read is the native read, bound to the head by run and SHA. S1 additionally reads, itself: the head (twice, the second time immediately before the merge); every check run on the head, with the five required jobs; the admissible review of §0.2f in full (the brief never carries a `CLAUDE_REVIEW_v1`; the workflow cannot read the private Bridge); no `CHANGES_REQUESTED`; the review threads, for an unresolved P0/P1 (gate (e)); main once more immediately before the merge, with the drift rule; the pins of `AGENTS.md`, `.github`, `.agents`, `07_PROMPTS_AND_AGENTS`, `scripts/governance` and `scripts/health` at current main; the ruleset census once more, equal to the brief's two; halts and open intents on #1156; HIGH EVIDENCE for risk HIGH; and the complete gate (g) readback after the merge. The pins of `01_CORE_FRAMEWORK/governance` and of the two `00_FMOS` policy files are attested by the brief at its main and covered by the drift rule after it. The judgment exclusions (the judgment half of 3, and 4, 5, 6, 8 and 9, and a truncation the diff counts do not show) stay with the reviewer's `lane_eligible: YES` and with S1.
- **Site readback.** For a PR that changes `05_CYCLE_NAVIGATOR/site/`, the untrusted job `site-public-build` (no secret, no write scope, no persisted credential) builds the site with the Pages workflow's own steps at the PR merge commit and uploads the bundle; the isolated `privacy-scan` job executes none of it and scans every published byte with the scanner's own rules (`scripts/governance/s1_site_public_readback_v1.py`, `S1_SITE_PUBLIC_READBACK_V1`). A site path is no longer UNKNOWN only for `PUBLIC_OUTPUT_CLEAN` bound to the same head, merge commit, run and attempt; a missing, failed or foreign bundle keeps UNKNOWN, and a finding is `RESTRICTED_CONTENT`. Exclusion 6 (privacy boundary) and risk HIGH for site paths are unchanged. Limit: the readback sees the bytes this build produced; build code that behaves differently on main than on a pull request is for the reviewer, not for the readback.
- **One merge per run** from the brief.
- **No brief, no census.** A missing, stale or unverified brief makes the run a NOOP with reason `BRIEF_STALE` or `BRIEF_UNVERIFIED` and no write of any kind. S1 never falls back to rebuilding the reads itself.
- **Accepted residual risk.** For the step-level CI proof, the privacy line, the diff-derived exclusions and lane check 4 (main health, read at most 45 minutes before the tick against its 26 h window) S1 relies on the brief. Forging a brief needs write access to this repository's issues or workflows inside the run's own time window; the producer code is under the `.github` and `scripts/governance` pins, which S1 reads natively before a merge. The authentication is behavioural plus the run binding, not cryptographic.

### 0.3 Global Action Compass invocation - all Investering threads

Canonical owner:

`07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md`

Machine route:

`07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json`

In any repository-aware Investering thread, an exact prompt of `kompas`, `handlekompas` or `compass` is a hard current-state invocation. The same route applies when one of those words is clearly used as the primary imperative, such as `send kompas` or `kompas nu`.

Do not ask which thread, DATA PING version, workflow or agent the user means. Resolve current authority from the operational cockpit and autonomous production-data route, then apply the global compass contract.

This is not an instruction to reactivate manual DATA PING. A plain compass invocation is a current-state render/decision-translation request. It must not create a new prospective receipt merely because the user requested the view.

**Permanent complete KOMPAS mandate (2026-10-08):** Plain `Kompas` means cross-read and integrate all applicable Official, Native, Shadow v2 (research only), Strategic, Master Monday/Cycle Navigator and risk/SELL/Swing/re-entry evidence, with every relevant asset/horizon and a final assistant-owned time-labelled interpretation. The public CN site must consume a sanitized composite readback of that same evidence, with official action ownership unchanged. Apply Global Action Compass contract Section 3.1 and `full_stack_compass_default` machine routing; unavailable sources remain explicit.

**Owner override (2026-10-27), DEFAULT KOMPAS = KOMPAS PRO:** An unqualified `Kompas` (including `send kompas`, `kompas nu` and `Kompas PRO`) requests the latest source-bound **KOMPAS PRO** presentation, not the former shortened Kompas view. Retain the required two compact tables, then present current market conditions, PRO pullback radar (ordinal 1-5 and evidence quality, distinct from probability), source-supported ETA/depth or explicit unavailable, frozen Price Range Navigator, separately owned SELL/Swing/distribution/re-entry, `Your Action Now`, source age/limitations and independent time-labelled interpretation. Use the existing merged Kompas PRO presentation contract, not a second signal, price, or trading engine. A shorter legacy answer requires an explicit user request. An explicit `handlekompas` request retains its specialized contract. Never upgrade stale sources, invent probabilities/prices/ETA or imply a SELL signal from a pullback warning.

User-facing compass output is **TEXT_ONLY** by default. APIs, connectors, repository tools and web retrieval may be used internally when needed, but do not intentionally render widgets, market cards, interactive charts, API/connector result cards, raw JSON, raw tool output or provider diagnostics in the compass response. Keep the authored output compact, phone-first and action-oriented.

The tactical compass must preserve the existing short-horizon owner semantics and controlled action vocabulary, add ETA where actionable, fail stale/unsupported lanes closed, keep warnings separate from actions, and avoid repeated rotation sections. For explicit month-ahead / 21-30D / 4-8W requests, also resolve `04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json` when present and hash-bound. The 21-30D lane may only come from the governed weekly strategic projection, and 4-8W remains Cycle Navigator-owned; never stretch 2-3W into a month forecast or create a parallel long-cycle engine.

When present and eligible, `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json` is the pointer-first machine owner for a current Compass render. Read and hash-verify its immutable target before bounded live context. Never replace a missing, stale or mismatched official pointer with inherited chat prose. The pointer render itself creates no new freeze or prospective receipt.

## 1. Read order

Before framework, DATA PING, weekly operations, Cycle Navigator, Research Lab, evidence-ledger, archive, governance or automation work:

1. Read `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`.
2. Read `00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json`.
3. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
4. Read `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.
5. Read `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`.
6. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
7. Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.
8. Read `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`.
9. Load the relevant skill from `.agents/skills/`.
10. Read only the current canonical and operational files identified by those anchors, plus the restricted-plane authority when the map requires it.

The 2026-09-14 transition owner explicitly supersedes older archive/index prose **only for current production data routing**. Older sections remain valid historical architecture records for their frozen periods.

Do not rely on conversation memory when repository sources are available.

## 2. Source and version governance

- For current-state work, the newest eligible current autonomous pointer/output chain named by the operational cockpit wins within its governed domain.
- For an explicit DATA PING/RAW packet task, the highest explicitly active packet/protocol version applicable to that task wins.
- A historical DATA PING version never overrides a newer current autonomous production pointer solely because it is called a truth-layer or active feed in an older document.
- Newer operational patches override older conflicting documents in the same domain.
- Historical, legacy, superseded, shadow and source material remain context, not current authority.
- `DATA_MISSING` means `UNKNOWN`. It is not negative evidence.
- Source-backed claims are not outcome rows.
- Written governance is not functioning governance without behavior, valid rows or a documented blocked state.
- Never infer, interpolate or backfill missing market values unless a canonical rule explicitly permits it.

## 3. Framework roles

- Autonomous collectors, GitHub Actions and governed source owners produce the current production evidence/machine-output chain.
- DATA PING is an explicit packet/protocol, replay, diagnostic and historical-lineage surface unless a current pointer explicitly routes to it.
- The main framework owns interpretation, permissions, action and ratification.
- Shadow and Research Lab challenge, test and learn. They do not self-promote.
- Prospective evidence ledgers preserve pre-registered inputs, verified outcomes and test accountability.
- Master Monday is the weekly official synthesis after ratification and consumes the current autonomous evidence chain.
- Cycle Navigator is public output and pre-registered accountability and does not require manual DATA PING submission.
- GitHub is versioned memory and the governance control plane.
- The public `Donh91/Investering-Framework-Archive-v1` repository is the control plane; `Donh91/secrets` is the private restricted data plane and has no independent market-rule authority.

### 3.1 DATA PING supplemental capture - explicit/legacy packet contexts only

This section applies when a task is explicitly about DATA PING analysis, replay, compatibility, a frozen historical period that used DATA PING, or a current pointer that explicitly routes to DATA PING. It does not make manual DATA PING the normal upstream feed for current CN or Master Monday.

- Read `02_DATA_PING/protocols/2026-07-28__data-ping-deep-capture-escalation-protocol-v1__canonical.md` for eligible DATA PING analysis, weekly reconciliation, experiment maturity and event-driven evidence gaps within that task class.
- The standard DATA PING remains bounded. Do not enlarge it by default.
- When an eligible historical/packet record is incomplete or a material event needs higher-resolution evidence under the protocol, prepare one targeted copy-ready Custom GPT prompt under the protocol.
- Check `02_DATA_PING/operational_handoffs/deep_capture_request_ledger_v1.json` before preparing a prompt.
- Weekly and event-driven requests must be deduplicated by ISO week, method scope and event cluster.
- A prepared prompt is not evidence, and a returned package is not accepted until source, time, method, settlement and duplication checks pass.
- Every explicit DATA PING thread handover must preserve pending deep-capture requests and active event windows.

### 3.2 DATA PING / RAW main-thread action compass - explicit packet tasks only

This section applies only when the primary input really is a DATA PING packet or RAW market-data ingest/replay. It does **not** define the normal production upstream for current Master Monday, Cycle Navigator or the CN website.

For every Main-Framework response whose primary input is a DATA PING packet or RAW market-data ingest, including duplicate/replay packets, corrected packets, replacement threads and future DATA PING thread versions:

1. resolve current repository authority first;
2. read `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md` as a mandatory current owner for that explicit packet task;
3. apply the contract after evidence interpretation, never inside the collector wire format;
4. end the human-facing response with the mandatory three-lane `HANDLEKOMPAS` covering the evidence-supported near-term action, the 5-7 day action window and the adaptive 3-4+ week altcoin market compass;
5. do not rely on conversation memory, prior-thread prose or inherited summaries as a substitute for the current contract;
6. keep Lane-3 warning and action separate; never infer `REDUCE` or `EXIT` from a warning alone;
7. treat Three-Horizon Action Compass v1.1 as the sole current decision vocabulary for that task class; the historical E0-E7 Exit Ladder is `RETIRED_UNIMPLEMENTED`;
8. for each fresh explicit ingest, persist exactly one immutable Action Compass receipt through the owner implementation when repository write capability exists;
9. for a duplicate or replay, emit no new receipt and do not extend an expired action horizon;
10. if persistence is unavailable or fails, state `persistence_status: NOT_PERSISTED`; do not count the interpretation as prospective evidence;
11. never persist full chat text, conversation summaries, holdings, quantities, account data, credentials or restricted provider values in the public receipt.

This requirement is cross-thread bootstrap governance for explicit DATA PING/RAW packet tasks. It changes decision translation and accountability only and does not increase DATA PING collector authority or automatic portfolio-execution authority.

For a fresh explicit ingest with repository write capability, create a private temporary candidate and run:

```bash
python scripts/learning/action_compass_accountability.py persist \
  --candidate <private-temporary-candidate-path> \
  --receipt-root research/framework_memory/action_compass_receipts \
  --repo-root . \
  --expected-canonical-commit <exact-main-commit-used-for-interpretation>
```

The temporary candidate must not be committed. Commit only the generated receipt on an isolated `agent/task-*` branch, validate it with `validate-repository`, use a pull request, pass checks, merge and verify readback. This is automatic agent work, not a request for manual user GitHub work. Replays stop at `DUPLICATE_NOOP`.

## 4. Current architecture constraints

- Tighten and simplify before expanding.
- Respect any currently active engine-freeze or equivalent governance discovered from current owners; do not infer an old freeze is still active solely from historical prose.
- Do not create a new engine, shadow layer, scoring concept or duplicate forward test without an explicit canonical exception.
- Prefer rows, source-lineage repair, missing-data completion, reproducibility, retirement and compression over new theory.
- Keep BTC permission and alt permission as separate evidence lanes.
- No portfolio action may be produced from DATA PING alone.
- No public website may create an independent market-state or short-horizon forecast engine.

### Bounded canonical exception: Kompas live research display

The prohibitions on new engines and independent website forecasts in this section have one narrowly scoped exception for the Kompas live research display. The only registered owner is `scripts/cycle_navigator/build_kompas_live_path.py`. It may use only formulas registered in the Challenger A/B pre-registrations, the verified Official Compass pointer under its original source-expiry clock, and public hourly spot data. No other packet may influence the line. Missing, invalid, stale or expired inputs retain their fail-closed handling; the source deadline must never be extended. Retain the existing "live formula" labels.

This display is research-only. It is never an official forecast, never scored, and never an input to decisions, promotion or trading. The exception is void and the display must be disabled if any of the following occurs:

- A tilt is shown after `official_source_valid_until_utc`.
- Any packet other than the verified pointer influences the line.
- Any number reaches a decision or scoring lane.
- Private data reaches the public JSON.

This exception changes no other rule, including Vault, credentials, trading, publication, private-data boundaries or paid API rules. It takes effect only after this policy change is reviewed and merged to main; a PR or relay is not authority.

### 4a. Producer growth, idempotency and active sets (FRAMEWORK_INCIDENT_LEARNING_v1, Archive #2152)

Origin: on 2026-11-14 an experiment producer re-dispatched 319 candidates about 4×/day until its hot manifest held 63,219 rows (26.3 MB). That broke `storage-health` on every PR. Fixed by #2155/#2156. Each rule below is marked **[ENFORCED: <blocking CI check>]**, **[DETECTED: <non-blocking CI signal>]** or **[POLICY]**. ENFORCED means a check that a PR workflow actually executes and that fails the PR. DETECTED means a CI signal that is visible on every PR but never blocks. A POLICY rule binds reviewers but is not automatically checked. Neither DETECTED nor POLICY may be described as enforced.

1. Any PR that adds or changes a producer, writer, collector, forecast, dispatch or receipt path must map producer → persisted data → manifest/index → receiver → final consumer → CI gate → retention, across repositories. The review checks that consumption actually happens end to end. **[POLICY; reviewer checklist]**
2. Such a PR states the expected growth at 7, 30 and 90 days: bytes, distinct entities, records per run, duplicate ratio and pending backlog. **[POLICY]**
3. Immutable history and the compact active set are separate. A `LATEST_*` file holds the active set, not the full history. No silent cap, truncation, deletion, fake PASS, raised limit or CI bypass. **[DETECTED: storage-health early warning `HOT_ACTIVE_SET_OVER_BUDGET` for `LATEST_*` files above 5 MiB, non-blocking. ENFORCED only at the unchanged hard limit `FILE_OVER_HARD_LIMIT`. A full-history `LATEST_*` below 5 MiB is not detected: POLICY]**
4. Work is semantically idempotent. A clock or source tick alone never creates new work; dispatch needs a semantic change or a documented state transition, proven by negative tests. **[POLICY. The regression test `tests/experiments/test_dispatch_episode_and_pending_manifest.py` exists, but no PR workflow executes it yet (it is only collected; see #2163). It becomes ENFORCED for experiment dispatch only when a PR gate runs it]**
5. A producer contract change ships only after the receiver is ready, with bounded reads, path containment, checksums and a rollback. **[POLICY]**
6. Growth is visible before it blocks: any file above 50 % of the hard limit is flagged on every PR. A red `storage-health` is a P0 incident routed to #1156 / #2152. **[DETECTED: storage-health early warning `PRE_LIMIT_GROWTH_RISK`, non-blocking. Routing: POLICY until the S1 DISCOVER lane or watchdog reads it]**
7. Done means native CI green on an unrelated PR, a producer → receiver replay with counts, no lost evidence, 72 h stable growth, independent review, and exact-head merge plus main readback. **[POLICY]**
8. Do not say "resolved", "autonomous", "monitored" or "learned" unless a GitHub-native instruction, CI step, test or automation changed and was read back. An issue comment is evidence, not enforcement. **[POLICY]**

## 5. Prospective evidence discipline

For active forward tests and ledgers:

- the target test must exist in the Active Test Registry;
- the owner defines the schema, horizon, benchmark, validator and scorer;
- forecasts, decisions, horizons and invalidators must be frozen before outcomes;
- frozen inputs may not be rewritten after outcomes become observable;
- source rows, initialization rows and schemas are not outcome evidence;
- incomplete horizons remain pending, not failed;
- duplicate and overlapping event-window status must be explicit;
- use existing validators and scorers rather than reproducing their logic;
- row validity, coverage readiness and promotion status must remain separate;
- a coverage gate may permit governance review but never automatic promotion.

Use `.agents/skills/prospective-evidence-ledger/SKILL.md` for prospective row creation, maturity checks, outcome attachment, lineage reconciliation and coverage validation.

## 6. Repository write safety

- Work on an isolated `agent/task-YYYYMMDD-short-purpose` branch.
- Use pull requests for canonical changes.
- Never force-push, rewrite history, delete backup branches or use backup branches as workspaces.
- Search before creating a file.
- Prefer updating or appending to the existing owner file over creating a duplicate document.
- Preserve historical files unless an approved retirement workflow applies.
- Follow `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md` before any high-impact operation.
- Changing `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, archive routing, precedence or source governance is high-impact and requires the policy safepoint sequence first.
- Enforce permanent separation of destructive authority. A source-writing principal must not also hold destructive recovery/Vault authority.
- Never broaden credentials, weaken safeguards or obtain a recovery-destructive permission merely to make a source task succeed.

### Mandatory branch assertion before every write

Before any `create_file`, `update_file` or `delete_file` operation:

```yaml
target_branch_explicitly_supplied: REQUIRED
target_branch_verified_to_exist: REQUIRED
target_branch_is_default_branch: MUST_BE_NO
target_branch_is_backup_branch: MUST_BE_NO
write_path_and_operation_declared: REQUIRED
```

If any field cannot be verified, stop with:

```text
WRITE_BRANCH_UNVERIFIED
```

Never omit the branch argument and rely on the tool default. Never create placeholder or test files to probe connector behavior in a production repository.

For any destructive or high-impact operation, also verify:

```yaml
source_destructive_authority: YES | NO | UNKNOWN
recovery_destructive_authority: YES | NO | UNKNOWN
same_principal_session_or_credential: YES | NO | UNKNOWN
separation_result: PASS | BLOCKED | UNVERIFIED
```

`BLOCKED` stops with `SEPARATION_OF_DESTRUCTIVE_AUTHORITY_VIOLATION`. `UNVERIFIED` stops with `SEPARATION_OF_DESTRUCTIVE_AUTHORITY_UNVERIFIED`.

## 7. Archive discipline

Classify material before writing:

- framework governance or architecture -> `01_CORE_FRAMEWORK/`
- DATA PING protocol or source QA -> `02_DATA_PING/`
- weekly operations or automation -> `03_WEEKLY_OPERATIONS/`
- market and regime learning -> `04_MARKET_LEARNING/`
- Cycle Navigator product -> `05_CYCLE_NAVIGATOR/`
- Research Lab synthesis or tests -> `06_RESEARCH_LAB/`
- prompts and agent workflows -> `07_PROMPTS_AND_AGENTS/`
- raw external evidence -> `08_SOURCE_MATERIAL/`
- unclear temporary material -> `09_ARCHIVE_INBOX/`

Archive the durable learning, not every intermediate conversation or report.

Every valid index addendum must also be discoverable through `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md` unless it is already directly listed in `CANONICAL_INDEX.md`.

## 8. Validation before completion

Before declaring work complete:

- verify every referenced path exists;
- verify current production data routing against `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`;
- verify active versions against the canonical index and addendum registry while respecting explicit routing supersessions;
- verify no legacy file was treated as current authority;
- verify output status and evidence status are explicit;
- verify no hidden interpolation or unsupported scoring occurred;
- verify prospective inputs predate outcomes;
- verify frozen fields were preserved;
- verify source rows were not counted as outcomes;
- verify validator result, coverage readiness and promotion status are separate;
- verify the diff contains only intended files;
- verify every write used an explicit non-default task branch;
- verify separation of destructive authority for every destructive or high-impact operation;
- report unresolved paths, blocked data and manual interventions honestly.

A remediated write incident cannot receive an unqualified `PASS`. Use `PARTIAL_REMEDIATED` for the write layer and report the final repository state separately.

## 9. Skill composition

Default composition order:

1. `canonical-context-router` to resolve current authority.
2. `prospective-evidence-ledger` for active test and ledger row lifecycle work.
3. The existing domain validator or scorer when applicable.
4. `research-lab-red-team` when interpreting evidence, testing survival or considering promotion.
5. `codex-intake` when a reproducible bounded research finding should become a code-remediation candidate.
6. `archive-governance` before any repository write.

Skills define procedure. Canonical repository files define current truth. A skill must never become a parallel source of market rules.
