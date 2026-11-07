# S1 Release Control · read-only release workspace

**Status:** integrated release candidate on draft PR #1996; actual deployment and recovery acceptance not yet asserted. This is not a release authority, new Supervisor, new queue backend, scheduled job, paid model trigger or change to the existing Cycle Navigator site.

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

## Shared classification and agent projection

- `release-core.js` is the single conservative classification engine for browser and Node. Its `PROVEN` label means a specific source observation, **not** verified required checks, branch protection or release authorization.
- `projection-v1.mjs` is a versioned on-demand Node 22 read-only consumer of the **same public GitHub owner set**. It produces `S1_RELEASE_PROJECTION_v1` with source SHA40, current main, observed time, exact-head CI, review, risk, next action, required-gate unknowns, source issues and explicit `merge_authorized:false`.
- Run: `node tools/s1-release-control/projection-v1.mjs --stdout`, or `node tools/s1-release-control/projection-v1.mjs --output /tmp/s1-projection.json`. It does **not** write to GitHub, dispatch, grant permission, use tokens, create an authority store or schedule itself. Public API rate limits and repo visibility can produce partial or UNOBSERVED outputs.
- It never asserts natural scheduled S1 execution from an ordinary PR, merge or script run. No private Bridge/Alpha/Vault data is read.
- The browser's local queue export remains an **observation plan**. The Node projection is on-demand public API readback, not an automatic production feed or a second canonical source.

## Tests and negative controls

`node --test tools/s1-release-control/test-static.mjs` checks read-only and same-origin contracts.
`node --test tools/s1-release-control/test-projection-v1.mjs` uses deterministic public-API fixtures for stale HEAD, changed main, stale review, denied access, incomplete file readback, cross-commit CI and false autonomy.
`node 05_CYCLE_NAVIGATOR/site/build-public.mjs` builds the normal CN public bundle and optionally stages the isolated cockpit at `dist/s1-release-control/`.
`node tools/s1-release-control/test-browser.mjs` uses actual Chrome CDP at 390px, 430px and 1440px with the GitHub API deliberately blocked to prove honest fallback and mobile/desktop behavior. It is **not** iPhone Safari testing.

A PR-only GitHub Actions workflow runs independent static, adversarial and Pages-isolation jobs, with least-privilege read permissions, no cron, no new supervisor and no paid API. Each run must be bound to its actual PR HEAD.

## Controlled deployment boundary

The existing `.github/workflows/cycle-navigator-pages.yml` still publishes only `05_CYCLE_NAVIGATOR/site/dist`. A bounded change to `05_CYCLE_NAVIGATOR/site/build-public.mjs` now **stages** `/s1-release-control/` inside that same bundle. Existing CN root, `/legacy/`, and `/vnext/` are not rewritten for this feature, and a missing cockpit file is an explicit optional-build warning, never a reason to forge success.

This does **not** mean publication already occurred. A real live URL requires exact HEAD tests, governance/recovery qualification, merge, Pages run success, and a real CDN/browser readback. Private-source publication and additional scheduler architecture are not part of this PR. If the external Vault/recovery or actual platform rules cannot be independently verified, release remains HOLD regardless of passing tests.

## Explicit non-goals

No GitHub write API, no queue scheduling, no permission expansion, no paid reviews or agents, no automatic merge, no token storage, no private raw/normalized market data, no Vault credential access, no false independent approval and no new S1 automation.
