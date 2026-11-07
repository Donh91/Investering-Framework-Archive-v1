# S1 Release Control, standalone GitHub Pages release contract v1

Status: `SEPARATE_GITHUB_PAGES_REPOSITORY_NOT_CREATED`; separate AppDeploy read-only staging is live at https://s1-release-control-4e0h9r.v2.appdeploy.ai/ (READY in host QA, not GitHub Pages, not release/custody authority). Original code owner: Archive PR #1996. Canonical S1 owner: Archive issue #1156. This file is a bounded publication procedure, not a workflow, repository-creation permission, S1 scheduler or claim of release.

## Target separation

1. Create one new public, dedicated GitHub project repository under the existing Donh91 owner when an authenticated repository-create capability is actually available. Preferred available name if unclaimed: `S1-Release-Control`. Never reuse `CycleNavigator-scores`, `Eksperimenter-framework-`, `Investering-Framework-Archive-v1` Pages or alter the existing CN Pages site.
2. Copy only reviewed files from a qualified, exact-source Archive PR/main commit: `index.html`, `release-core.js` and `release-identity.json` with immutable SHA256 bindings. Include `.nojekyll`. Do not copy owner raw market values, private Bridge/Alpha/Vault data, credentials, `LATEST_*` snapshots, generated source authority or repository write tokens.
3. Publish via a dedicated GitHub Pages source in the new repo, with `contents:read`, `pages:write` and `id-token:write` for its deployment workflow only. This is a **site publication workflow** triggered by the new site's own main pushes or explicit dispatch, not a scheduler or supervisor. Source edits remain governed at original PR/main before the exact static distribution bytes enter the site repository.
4. Bind the published `release-identity.json` to the source Archive 40-character commit, manifest source digest, target repository main commit and the actual Pages run. A source-side CI artifact is only a candidate; setting `production_deployed:true` in a generated file without a verified Pages+CDN readback is forbidden.
5. Verify the real HTTPS URL, CDN status and byte-for-byte `index.html` + `release-core.js` digests, and browser behavior with both live/failed API. Verify CN deployed root + `legacy` + `vnext` unchanged through independent original readbacks.

GitHub reference: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages (one project Pages site per repository) and https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site.

## Reproducible build at current source HEAD

The historical PR-only workflow on tested source HEAD `0e5ceee5c1121cfcf1edb8994f1d20cf0ba38358` created `s1-standalone-site-<exact-head-sha>` with the following bytes; the executable workflow is **out of this narrowed initial PR release**. Its preserved, inactive reference template is `tools/s1-release-control/deployment-template/pr-only-validation-workflow.yml`, requiring an independently qualified workflow-change release before activation:
- `index.html`
- `release-core.js`
- `.nojekyll`
- `release-identity.json` with `S1_STANDALONE_STATIC_BUNDLE_v1` and `production_deployed:false`
- `SHA256SUMS`

The artifact may be transferred by an existing authorized qualified release owner to the separately governed repository. It must not be auto-integrated merely because all tests are green. Never use Circle Navigator Pages as temporary publication fallback.

## Live acceptance contract

Require `GET /release-identity.json` over the actual Pages HTTPS host (not a guessed URL), `source_head_sha` equals the approved exact original source commit, `content_sha256` matches CDN `index.html` and `release-core.js` bytes, a native successful Pages deployment run, actual target main SHA, real 390/430px and desktop navigation with correct stale fallback and a successful public REST path, no secret/API-key storage, and an unchanged CN production source.

Release remains BLOCKED if current-source independent Vault/custody and branch/platform gates are required by the applicable policy but cannot be proven. A source safepoint is not a verified independent external backup. A separate site does not create any new S1/Strategist/Codex/Grok permissions.

## Capability gap, exact next trigger

The connected GitHub tool in this session can inspect repositories, create and edit PR branches, run source-controlled CI, and interact with original issues. It does **not** expose creating a repository or configuring its Pages settings. Existing paid browser automation reports no available balance and no new paid browser spend is authorized.

`SEPARATE_GITHUB_PAGES_REPOSITORY_CREATION_UNAVAILABLE` is the exact blocker. Resume only when an actual authorized public repo creation + Pages administration route exists and the original source is release-qualified. Do not claim the potential URL `https://donh91.github.io/S1-Release-Control/` is deployed or known to exist. Do not repurpose CN or open a second operator to bypass it.
