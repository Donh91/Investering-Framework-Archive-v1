# S1 Release Control · read-only release workspace

**Status:** standalone, agent-first source-controlled release candidate on draft PR #1996. Separate GitHub Pages repository and deployment acceptance remain unresolved. This is not a release authority, new Supervisor, new queue backend, scheduled job, paid model trigger or change to the existing Cycle Navigator site.

## Scope and sources

- `index.html` is a static, browser-hosted read-only interface using the same-origin `release-core.js`. No npm dependencies, API credentials, services, server, build process, backend or privileged GitHub identity.
- Public GitHub REST GETs for precisely: `Donh91/Investering-Framework-Archive-v1`, `Donh91/Eksperimenter-framework-`, `Donh91/CycleNavigator-scores`. Reads `branches/main`, `pulls`, selected `pulls/{n}/files`, `pulls/{n}/reviews`, and `actions/runs?head_sha=...`.
- `Investering-AI-Audit-Bridge` and `Meme-Alpha-Lab` are private. The browser **does not fetch** them or request a token. They are explicitly labeled `PRIVATE / UNOBSERVED`. The restricted `Donh91/secrets` repo is never accessed or enumerated.
- An initial two-PR **historical snapshot** is a fallback for no network. Its observations are pinned to 7 November 2026 and ALWAYS identified as not live. A public REST readback replaces that snapshot only after GitHub responds. Seed never authorizes release.
- Live readback is cached for 20 minutes in the local browser. Cache contains only public GitHub PR metadata. A failure preserves the last public readback with stale labeling, not a synthetic PASS. Large PRs (100+ files) and incomplete readbacks fail closed.

## Evidence classifications

- **PROVEN**: a directly observed, SHA-bound public item, such as an actual workflow run at the exact PR HEAD. This is *only that item's* observation, not a holistic release approval.
- **UNOBSERVED**: no available exact proof, missing private/restricted access, GitHub API failure, incomplete file pages, missing required check enumerations, current recovery attestation or unverified provider bill.
- **BLOCKED/HOLD**: draft PR, missing required proof or HIGH_IMPACT gating. Source/Vault separation remains fail-closed.
- **PROPOSED**: a queue/next-action suggestion, never an actionable authenticated merge mandate.

GitHub run links, exact-commit links and source timestamps are for inspectability. An external immutable receipt must be verified at its original exact SHA/path/hash. A mutable PR body, comment, label, advisory or past snapshot alone is never such proof. An independent Vault recovery/readback specific to the current code change is NOT derivable from an older restore run.

## Queue

- Deterministic algorithm `s1-risk-priority-v1`: actual open PRs, P0/P1 labels as ordering *hints*, HIGH_IMPACT first, drafts, repository/number tie-break. Ranking is not release admission.
- Operator may locally add/remove up to 3–8 slots and reset deterministic order. **If only two real PRs are observed, the queue shows two.** No fictitious entries.
- JSON export contains precise PR HEAD/base SHA, current observed main SHA, source time, risk, proposed next action and `no_release_authority:true`. It is a reproducible observation snapshot, *not* a signed receipt. No manual spreadsheet or durable alternate state store.
- The existing S1 max-three-actionable-PRs-per-tick ceiling and Monday 09:30–10:30 Europe/Copenhagen read-only window are unchanged.

## Release gates

For each PR, inspect independently: head/base/main SHA, actual ruleset and required review state, branch-specific check runs, full changed-file list, verified exact-head review, dependencies, scope/owner, immutable receipts, HIGH_IMPACT safepoint and separation of destructive authority, original Vault recovery/restore readback and post-merge main/prod outcome. A green CI set alone NEVER means MERGE. Actual source-specific allowlist, one-use claim and billing/provider invoice are UNOBSERVED unless authenticated original proof is shown. This page does not dispatch or pay an API.

Canonical policies:
- [AGENTS.md](../../AGENTS.md)
- [Repository safety and backup policy](../../01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md)
- [S1 mission](../../00_FMOS/S1/MISSION.md)
- [Cross-repo data boundary](../../00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md)

## Machine-first canonical context for S1, Strategist, Codex and Grok

- Run `node tools/s1-release-control/agent-context-v1.mjs --stdout` for `S1_AGENT_OPERATIONS_CONTEXT_v1`, or `--output /tmp/s1-agent-context.json` for a reproducible noncanonical local JSON snapshot. No scheduling, writing, GitHub token or private-source access is involved.
- It reads **seven existing public canonical owners** by freezing current Archive `main` SHA40, fetching original paths at that exact commit, validating returned Git blob SHA and byte length, producing independent SHA-256 digests, reporting source-generated timestamps and advisory freshness, and rechecking `main` at the end. Changed `main`, stale/failed/private sources and unverified outcomes fail closed.
- Bounded summaries include original dashboard/incident coverage, handoff, Codex READY, Codex execution-state (not queue authority), remediation, automation health and architecture health. Full original records stay with their owners; no new ledger is authoritative.
- For the smallest cross-agent handoff, run `node tools/s1-release-control/agent-brief-v1.mjs --stdout`. This produces `S1_AGENT_OPERATIONS_BRIEF_v1`, an advisory composition of the original public source packet and original-PR projection with source/main alignment, owner-specific action hints, Codex READY source references, observed PR facts and every missing gate. It includes explicit `no_new_canonical_queue:true`, `release_permission:false` and `natural_S1_execution_proven:false`. It cannot dispatch or authorize any original agent.
- `schemas/agent-brief-v1.schema.json` is the machine-readable safety contract for that brief; `test-agent-brief-v1.mjs` asserts adversarial unknown, stale, mismatched SHA, false authority and S1 attribution failures.
- A `source_files[]` record carries `owner`, `source_path`, `main_sha`, `blob_sha`, `sha256`, `bytes`, `source_contract`, `generated_at_utc`, `observed_at_utc` and a pinned native GitHub source URL. `source_readback_verified` does not mean release permission or predictive edge.
- S1, Strategist and Codex can consume this object only through their **existing authorized** execution routes. Grok reads this public contract and original issue references, but Bridge advice remains separately authenticated through the existing private Bridge. A GitHub comment about the contract is not proof Grok executed or that S1 naturally consumed it.
- `merge_authorized:false`, `execution_provenance:INTERACTIVE_OR_ON_DEMAND_READ_ONLY_NOT_SCHEDULED_S1`, no new supervisor and no extra rights are permanent invariants. Verify source currentness again before taking an original GitHub action.

## Single low-friction agent brief

For an existing agent that needs the smallest useful operational handoff, use:

```sh
node tools/s1-release-control/agent-brief-v1.mjs --stdout
```

`S1_AGENT_OPERATIONS_BRIEF_v1` composes the original source-bound canonical context with a bounded public-PR view (max 3 PR details per repo per readback). It retains `original_source_ref`, owner, source alignment, SHA, freshness, real first next action, material gate gaps, and existing Codex READY references. No new task identity or canonical queue is introduced. Missing sources and unequal main snapshots are explicitly `PARTIAL_OR_STALE_RECHECK`. It cannot authorize release, claim a natural S1 merge, assume PR independence or treat Bridge as formal approval.

The versioned schema is `schemas/agent-brief-v1.schema.json`. Run `node --test tools/s1-release-control/test-agent-brief-v1.mjs` for positive, stale, forged-permission, wrong-main and bounded-queue negatives. This is **on-demand read-only code**, not proof that existing S1 has naturally consumed it. S1 and Grok Bridge receive original source-bound handoffs; they retain their original mandates and execution routes.

## Shared classification and agent projection

- `release-core.js` is the single conservative classification engine for browser and Node. Its `PROVEN` label means a specific source observation, **not** verified required checks, branch protection or release authorization.
- `projection-v1.mjs` is a versioned on-demand Node 22 read-only consumer of the **same public GitHub owner set**. It produces `S1_RELEASE_PROJECTION_v1` with source SHA40, current main, observed time, exact-head CI, review, risk, next action, required-gate unknowns, source issues and explicit `merge_authorized:false`.
- Run: `node tools/s1-release-control/projection-v1.mjs --stdout`, or `node tools/s1-release-control/projection-v1.mjs --output /tmp/s1-projection.json`. It does **not** write to GitHub, dispatch, grant permission, use tokens, create an authority store or schedule itself. Public API rate limits and repo visibility can produce partial or UNOBSERVED outputs.
- It never asserts natural scheduled S1 execution from an ordinary PR, merge or script run. No private Bridge/Alpha/Vault data is read.
- The browser's local queue export remains an **observation plan**. The Node projection is on-demand public API readback, not an automatic production feed or a second canonical source.

## Tests and negative controls

`node --test tools/s1-release-control/test-static.mjs` checks read-only and same-origin contracts.
`node --test tools/s1-release-control/test-projection-v1.mjs` uses deterministic public-API fixtures for stale HEAD, changed main, stale review, denied access, incomplete file readback, cross-commit CI and false autonomy.
`node --test tools/s1-release-control/test-agent-context-v1.mjs` checks frozen source SHA, SHA-256/byte integrity, changed main, source denial, stale pointers, source allowlist and no private access. No Cycle Navigator build is involved.
`node tools/s1-release-control/test-browser.mjs` uses actual Chrome CDP at 390px, 430px and 1440px with the GitHub API deliberately blocked to prove honest fallback and mobile/desktop behavior. It is **not** iPhone Safari testing.

The historical PR-only GitHub Actions validation at `0e5ceee5c1121cfcf1edb8994f1d20cf0ba38358` ran independent static, adversarial and Chrome/artifact jobs successfully. The workflow was deliberately **excluded from the initial merge scope** because modifying `.github/workflows/` requires stronger recovery/release evidence. The exact audited workflow remains a non-executable source template at `deployment-template/pr-only-validation-workflow.yml`. Future activation needs a separately authorized workflow release. The original read-only source tests remain in this folder.

## Separate-product GitHub Pages boundary

**S1 is NOT part of the Cycle Navigator site.** The earlier experimental change to `05_CYCLE_NAVIGATOR/site/build-public.mjs` has been entirely reverted in PR #1996, and the PR workflow no longer runs or publishes the CN build. No code path modifies the CN root, `/legacy/`, `/vnext/` or its Pages workflow.

The existing Archive Pages site is already assigned to Cycle Navigator. GitHub Pages provides one project site per repository. The durable deployment target is therefore **a separately owned PUBLIC repository dedicated to S1**, e.g. `Donh91/S1-Release-Control`, with its own project Pages address after actual creation, configuration, commit and deployment. This proposed name and URL are **not** a claim of an existing repository or live site.

The existing GitHub connector can edit original PRs but does not currently expose a repository-creation or Pages-settings/deployment action. A separate repository has **not** been created and no Pages deployment was attempted. Preserve this exact operational blocker `SEPARATE_GITHUB_PAGES_REPOSITORY_CREATION_UNAVAILABLE`; do not repurpose CN, issue a fake URL, or consume unapproved paid web-browser access to bypass it.

An authenticated repository-owner route capable of creating and configuring a public repo is needed once, then the original S1 release workflow can export exactly `index.html`, `release-core.js` and a source-bound manifest into the dedicated site without any private records or new scheduler. A Pages publish in that repository still requires a real run, exact source-commit readback, HTTPS/CDN bytes verification and browser checks. The historical SHA-bound PR-only job supplied a SHA256SUMS-bearing artifact, **not** a GitHub Pages deployment. The browser is separately hosted read-only at https://s1-release-control-4e0h9r.v2.appdeploy.ai/, with AppDeploy QA reporting READY; this external public staging host is not an original GitHub Pages release, merge receipt, or source-bound Vault proof.

The separate AppDeploy read-only site is observed READY, but canonical GitHub Pages and original repo release acceptance remain `UNOBSERVED`. No release permission can be inferred from browser hosting. No release permission can be inferred from PR success, browser-loopback success, a source safepoint or an unrelated Vault restore.

## Explicit non-goals

No GitHub write API, no queue scheduling, no permission expansion, no paid reviews or agents, no automatic merge, no token storage, no private raw/normalized market data, no Vault credential access, no false independent approval and no new S1 automation.

## Source cadence, partial-source intelligence and fail-closed action

The original `.github/workflows/operations-dashboard.yml` currently schedules its
`LATEST_HANDOFF.json` producer for **06:00 and 18:00 Europe/Copenhagen**, plus
`workflow_dispatch`. The S1 read-only observer separately imposes a **180-minute
handoff freshness limit**. Because those cadences differ, a 3+ hour old handoff
can be expected between scheduled refreshes; this alone does not prove that
the producer failed. It also must **never** be promoted to fresh merely to
satisfy the original 12-hour cadence. Diagnose expected schedule vs actual
GitHub workflow-run evidence through the original producer before any repair.

The historical PR-only validation (before narrowing release scope) attempted a
`S1_AGENT_BRIEF_ADMISSION_STATUS_v1` artifact. When a full agent brief cannot
be admitted, a SHA/byte/digest-bound **fresh original Codex ledger** may still
yield up to eight *public, original* `read_only_original_codex_candidate_pointers`.
These are exclusively browsing references to `research/codex/intake/` in the
frozen Archive main, not alternative queue items, task dispatches or a reason
to act. Each pointer explicitly declares `candidate_file_revalidated:false`,
`original_intake_recheck_required:true` and `action_permission:false`.
Invalid/misaligned source SHA, stale Codex, or nonpublic paths produce **zero**
candidate pointers, not fallback guesses.

The diagnostic declares `full_brief_admitted` and
`requires_live_original_source_recheck:true`; it does not verify original
producer cadence within the packet, a *current* main read at time of use,
current original candidate-file status, HIGH_IMPACT permission, cost,
independent recovery or scheduled S1 consumption. Treat an expired artifact
as historical only. Existing S1 action cap of 3 original PRs per eligible tick,
existing separate owner and Monday read-only window are unchanged.

## Authorized cross-repository discovery (S1 owner #1156)

For the **existing authorized agent/runtime only**, run `node tools/s1-release-control/discovery-inventory-v1.mjs` for bounded, read-only OPEN PR and non-PR issue discovery. An opt-in, separate `--closed-parked` scan gathers **possible** closed research revival candidates, not actionable work or permission to reopen. `--private-details` requires an existing credential and must never be executed on public hosting or logged to public Actions/artifacts/comments. No GitHub identity, token, workflow, task, or paid API is created by this module.

With `GITHUB_TOKEN`, the script attempts GitHub's authenticated `/user/repos` owner enumeration and limits the scan to `Donh91` repositories that **that credential** can access, while **always excluding** restricted `Donh91/secrets`. Without an authorized credential, or if this API is denied, it falls back to five already-known repositories and **explicitly marks full estate discovery UNKNOWN**. Private Bridge and Alpha metadata remain inaccessible when that token lacks access. More accessible repositories may be discovered automatically, but a repository inaccessible to the connected identity is NOT proof of no outstanding work.

The output is `S1_DISCOVERY_INVENTORY_v1`, **read-only advisory**; exact local private titles/IDs are redacted by default. Public site `index.html`, `release-core.js` and public projection remain **public-only**, without token capture or a private-data proxy. The module fails closed for HTTP, pagination, incomplete issue/PR read or repository-enumeration gaps. Counts in an incomplete pagination scope are observations, not a complete census. Dormant/parked text matching only means `REQUIRES_OWNER_SOURCE_TRIAGE`. Current AGENTS/release rules, existing original issues/PRs, S1 max-three-actionable limit, source/frozen PIT and Monday read-only take precedence.

Suggested verification: `node --test tools/s1-release-control/test-discovery-inventory-v1.mjs` on the exact PR HEAD in an authorized, isolated runtime. Local/mock or green unrelated hosted gates do **not** establish a qualified targeted hosted test, merge, production deployment, automatic S1 consumption, or completeness of every private source. After real merge, S1 should compare its native GitHub readback with the module's bounded observations and stage a material #1156 receipt only on genuine new evidence. Preserve the current dedicated AppDeploy site as public read-only staging until native site/browser/source acceptance is proven.
