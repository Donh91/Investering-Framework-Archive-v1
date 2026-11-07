# S1 Release Control · Research Parallel Lanes v1 · evidence reconciliation

Date: 2026-11-07. Original owner: [S1 issue #1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156). Implementation: [PR #1996](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1996).

Frozen preflight main: `5da1c18162d624aa074cc43c5901c2199adfec76`. This is a *historical source snapshot*, not the current main ref after subsequent framework writes. Research is PUBLIC_ONLY; private source data and credential access were not requested. Cost of paid AI: USD 0. No separate AI research workers were launched.

## Actual execution topology

The coordinator performed multiple independent **read-only GitHub tool requests**, including simultaneous connector requests for governance, source files, S1 #1156, the #1996 HEAD, and deployed-build source. Concurrent tool calls were not independent AI agents. An actual, verifiable GitHub Actions run at [42372888303](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42372888303) executed **three genuinely overlapping jobs** on exact HEAD `bb8ed8957c80d828d1b8f85c2130c5cdfca7b4b5`: `projection-adversarial`, `static-and-boundary`, `pages-isolation-smoke`. All started at 2026-11-07 12:31:53 UTC, and ended at 12:32:14, 12:32:23 and 12:32:22 UTC, all SUCCESS. They validate engineering evidence; they do not constitute eight parallel research agents. The later [Chrome run 42373565467](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42373565467) verified the actual page on 390, 430 and 1440px with the GitHub API intentionally blocked. A blocked public API is **not** evidence of live REST success.

## Eight independently falsifiable research tracks

### R01 · Existing infrastructure · PUBLIC RESEARCH OBSERVED, source integration tested
- Owner: canonical control plane / S1 #1156. Source: [AGENTS.md](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/5da1c18162d624aa074cc43c5901c2199adfec76/AGENTS.md), current `LATEST_OPERATIONS_DASHBOARD.json`, `LATEST_HANDOFF.json` and current S1 mission.
- Baseline: browsing original GitHub PR pages and original owner records without any new data store.
- Hypothesis: a read-only derived projection can reduce repeated status discovery without becoming a second canonical operator.
- Falsifier: a second writable source of truth, schedule or permissions authority, or a projection that claims completion absent original proof.
- Evidence: `release-core.js`, `projection-v1.mjs` and tests in PR #1996. Rule: derive from public original GitHub only.
- Open verification: no actual natural scheduled S1 consumption established.

### R02 · Agent interoperability · SCHEMA AND FIXTURE TESTED, ADOPTION UNPROVEN
- Owner: S1 and existing authorized consumers, not cockpit.
- Baseline: plain GitHub REST responses.
- Hypothesis: one versioned read-only machine object can preserve source, clock, SHA, status, gaps and no-authorization marker.
- Falsifier: simulated merge permission; missing SHA/clock incorrectly passing; a consumer requiring private data to understand a public item.
- Evidence: `projection-v1.mjs`, `test-projection-v1.mjs`, GitHub Actions `projection-adversarial` job.
- Open: actual *existing authorized agent* import/readback is not yet independently observed.

### R03 · Native GitHub release intelligence · ADVISORY CLASSIFICATION TESTED, RELEASE UNPROVEN
- Owner: original PR and S1 existing release classifier `scripts/governance/s1_release_evidence_classifier_v1.py`.
- Baseline: green PR workflow + generic GitHub mergeable flag.
- Hypothesis: exact HEAD, double-read main, changed-file completeness, stale review and partial run census prevent false-green release decisions.
- Falsifier: mismatched HEAD or failed run classified as a sufficient candidate/authorized release.
- Evidence: shared `release-core.js`; negative fixtures in `test-projection-v1.mjs`; native CI run.
- Open: GitHub branch protection endpoint returned 403 for the active connection; a configured ruleset (ID 25307191) is disabled. Neither observation proves permission to merge under canonical governance. Required checks remain UNOBSERVED.

### R04 · Private source boundaries / Grok · PRIVATE INTEGRATION BLOCKED, SAFE FALLBACK TESTED
- Owner: existing Bridge and Alpha Lab restricted domain owners.
- Baseline: neither private source is read from a public browser.
- Hypothesis: unavailability can be shown clearly without copying private data or placing tokens in static code.
- Falsifier: a private API request, local token, private raw receipt or invented Bridge review evidence.
- Evidence: `CROSS_REPO_DATA_BOUNDARY.md`, public allowlist and read-only browser guard tests.
- Open: authenticated minimum-value-safe Bridge/Alpha metadata contract and independent native receipts are UNOBSERVED. No workaround that widens permissions is authorized.

### R05 · Security / recovery / financial gates · RELEASE BLOCKED, GUARDS TESTED
- Owner: independent recovery custodian / original canonical policy.
- Baseline: treat historical Vault SUCCESS as equivalent to current release permission (INVALID baseline).
- Hypothesis: independent custody, exact-source restore, independent release assessment, permission separation, allowlist and billing attestations must remain independently verified.
- Falsifier: historical backup comment, missing receipt or technical success automatically becoming `release_permission=true`.
- Evidence: canonical repository safety policy, S1 release evidence classifier, historical run 41730191277 could not be independently read (404), current technical recovery release proof UNOBSERVED. A dated **internal** source safepoint was created and verified at `0ef8e3905778eb8c0574e5c7e894693743f57ebf`; it is NOT external recovery.
- Open: independent current-source Vault custody/separation and a genuinely separate release assessment.

### R06 · UX / decision clarity · MOBILE CHROME FALLBACK PASSED, LIVE DATA UX PENDING
- Owner: PR #1996 read-only interface.
- Baseline: original GitHub PR list, source pages and run links.
- Hypothesis: bounded table, evidence inspector, filters and a 3–8-capacity plan reduce ambiguous status without pretending to execute.
- Falsifier: horizontal overflow, fabricated data, unlabelled stale data or confusing `PROPOSED` with merge permission.
- Evidence: `index.html`, `test-browser.mjs`, Chrome run 42373565467 proves 390/430/1440px overflow and failure fallback; no JS exceptions.
- Open: public real GitHub and actual deployment behavior not yet observed on CDN.

### R07 · Autonomy / observability · REAL CLOSURE ATTRIBUTION UNPROVEN
- Owner: existing natural scheduled S1 / original #1156, not cockpit.
- Baseline: count a merged PR as S1 closure regardless of actor (INVALID baseline).
- Hypothesis: native run origin, actor, exact main/producer outcome and distinct delegation receipts can distinguish natural S1 from interactive work.
- Falsifier: manually merged or externally advised PR counted as unattended S1 success.
- Evidence: `00_FMOS/S1/MISSION.md`, shared projection always reports `autonomy_evidence: UNOBSERVED`, `test-projection-v1.mjs`.
- Open: actual natural S1 to original merge and production readback. Existing model spend estimates are not release success.

### R08 · Hosting / resilience · PR BUILD TESTED, PRODUCTION NOT RELEASED
- Owner: current Cycle Navigator Pages workflow / original PR #1996 release.
- Baseline: no cockpit deployment, static `tools/` folder absent from Pages artifact.
- Hypothesis: optional static copy into existing `site/dist/s1-release-control/` preserves the canonical CN homepage and rollback while serving a separate read-only route.
- Falsifier: CN root/legacy/vnext changes or failure to build; absent new files silently represented as shipped.
- Evidence: optional `build-public.mjs` copy with absence warning and PR-only isolation tests; Chrome loopback tests.
- Open: current-source release/recovery gates, qualified merge, successful Pages publication and exact production CDN bytes.

## Dependency map and honest finish line

`AGENTS / canonical boundary + real GitHub HEAD` → `public source readback` → `shared conservative classification` → `human + versioned agent projection` → `original owner S1/Grok/Codex decisions` → `qualified original GitHub outcome` → `main and natural Pages/consumer proof`.

This cockpit never writes source authority; GitHub, original ledgers and original owners remain canonical. Recoverability and exact release permission sit outside the browser. Priority queue is deterministic PLAN_ONLY, never an execution queue. `PROPOSED` cannot mean authorized MERGE. A manual interactive GitHub action cannot claim natural S1 completion.

**Not done:** private metadata projection, authentic S1 consumer adoption, immutable per-release external restore, independent technical review, release merge, real CDN acceptance and production autonomy metrics. Completion cannot be claimed while these are missing.

**Next source-bound action:** validate exact current PR HEAD and all meaningful tests, obtain an independent current-source recovery/separation attestation through the existing qualified owner, then evaluate governed release under existing policy. Avoid repeating unchanged reviews or fabricating PASS. Keep draft/HOLD when real evidence is absent.
