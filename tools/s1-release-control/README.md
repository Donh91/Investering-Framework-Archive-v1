# S1 Release Control · read-only release workspace

**Status:** standalone static GitHub-first web app, staged on its own PR. This is not a release authority, new Supervisor, new queue backend, scheduled job, paid model trigger or change to the existing Cycle Navigator site.

## Scope and sources

- `index.html` is a self-contained, browser-hosted read-only interface. No npm dependencies, API credentials, services, server, build process, backend or privileged GitHub identity.
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

## Deployment boundary

**This PR only creates this isolated folder.** The current GitHub Pages workflow uploads `05_CYCLE_NAVIGATOR/site/dist` and does **not** automatically publish `tools/s1-release-control/`. Do not claim a live URL from this PR. A later, separately reviewed deployment integration or an independent GitHub Pages publication route is required. No Pages workflow, existing site, permissions, secrets, private repo, main, trading logic or high-impact workflow has been modified.

To inspect locally, open `index.html` in a modern browser with network access. To run non-privileged static guard tests: `node tools/s1-release-control/test-static.mjs`. Browser readback is subject to anonymous GitHub REST rate limits and local network access. A private-source aggregator would require separate formally authorized and narrowly scoped server-side architecture; it is intentionally not implemented.

## Explicit non-goals

No GitHub write API, no queue scheduling, no permission expansion, no paid reviews or agents, no automatic merge, no token storage, no private raw/normalized market data, no Vault credential access, no false independent approval and no new S1 automation.
