# Premium v2.1 · staged candidate acceptance matrix

**Date:** 2026-10-23 · **Owner:** SITE #1578 · **Oversight:** #1156  
**Current state (2026-10-24):** PREMIUM NEXT BUILT + CHROME CI VERIFIED; ISOLATED /next/ RELEASE NOT YET DEPLOYED; physical Safari and independent review outstanding.  
**DRAFT PR:** #1769. Do not merge or switch canonical root from this status.

## Source and design freeze

- [x] Design Registry established with explicit acceptance hierarchy, 12 Oct minimalist Kompas, approved Graph B reference, PATH 10-phase spec and Proof FROZEN→OBSERVED→ASSESS
- [x] All nine source AppDeploy B/C files captured at app snapshot `1792595071401`, unchanged, reference-only and NOT PUBLIC ASSET
- [x] Actual B markup/SVG copied from original AppDeploy DOM into graph-b, demo starting quote/forecast restore switch removed
- [x] Original authored AppDeploy CSS copied for B with only three non-browser `@tailwind` directives removed; original quarantined untouched
- [x] Proof external source must link to exact 40-hex commit + allowlisted public path, with independently sealed proof explicitly false
- [ ] Owner's approved 390/430 physical iPhone screenshots captured as hash-bound visual reference in GitHub under approved privacy/metadata controls
- [ ] Actual candidate B screenshot compared pixel/geometry/text hierarchy against B/C original reference. **No longer assume CSS style equals original visual.**

## Source authority and model firewall

| Evidence | Status | Required behavior |
| --- | --- | --- |
| Current W43 expected-close daily path | UNAVAILABLE | no blue expected day-by-day price curve |
| Genuine aggregate original D1–2, D3–4, D5–7 ranges | AVAILABLE | source-exact shaded interval windows, never interpolated blue midpoints |
| First-party BTC/ETH hourly closes | AVAILABLE but time-sensitive | only eligible original hourly spot PASS source, preserve UTC gaps |
| Official Compass action | source-issued | show as current ONLY while `valid_until_utc` not reached, otherwise explicitly historical |
| PATH position | UNAVAILABLE | no blue “we are here” or inferred ETA |
| 70/30 source-reported live price-range precision | PROVISIONAL | labelled original-score-to-date, separate from Direction/Edge and investment return |
| Public Edge Scorebook | PROVISIONAL_NOT_SEALED | 10/10 ABSTAIN W42 and W43; no invented binary accuracy |
| Original Git SHA + public source URL | navigation identity only | does NOT independently establish an ex-ante timestamp |
| Original score proof seal | NOT VERIFIED | independent witness + immutable publication + recomputed score missing |

## Current development code and tests

`graph-b/official-source-adapter.mjs`: 8 positive/negative source tests  
`proof/public-source-links.mjs`: 7 public commit/ABSTAIN tests  
`proof/price-range-proof.mjs`: 5 three-window original source/coverage tests  
`compass/official-compass-path.mjs`: 4 five-horizon/seven-tier/expiry/phase tests  
`preflight.test.mjs`: 5 original source/quarantine/root builder tests  
`build-next.test.mjs`: 4 noncanonical staging isolation tests

Mandatory normal Node commands from repository root (using existing installation, no new packages required):

```sh
node --test 05_CYCLE_NAVIGATOR/site/premium-v2/graph-b/official-source-adapter.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/proof/public-source-links.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/proof/price-range-proof.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/compass/official-compass-path.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/preflight.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/build-next.test.mjs
```

The owner-approved NEXT-only bundle is packaged locally **only after normal build** with:

```sh
node 05_CYCLE_NAVIGATOR/site/premium-v2/build-next.mjs
```

This emits `site/dist/next/`, never rewrites `site/dist/index.html`, and bundles ONLY the allowlisted 11 source UI files plus a staging `index.html`. It must not be connected to the existing production Pages action without a reviewed safety change and explicit staging gate.

## Visual/manual browser requirements

- [ ] Open noncanonical staged `/next/graph-b/source-graph-b.html` on the actual host once available. No AppDeploy link substituted as proof.
- [ ] Compare at 390×844 and 430×932 with exact approved AppDeploy B screenshots; inspect white frame/card spacing, Deep Navy plot, original dashed blue source-only condition, green actual, low/high shaded window geometry, typography, readable right price axis and 44px touch targets.
- [ ] DA/EN switch updates ALL B, Proof, Compass/PATH sections, not merely header language attribute.
- [ ] Genuine BTC→ETH→BTC switching, time scrub to earlier actual hour and missing hourly gap behavior.
- [ ] Source stale→fresh, now→expired in an **already-open tab**; late bundle must not show current action.
- [ ] Browser network verifies `/data/latest.json`, `/data/compass.json`, `/data/publication-lineage.json`, and public scores; CORS failure means Proof links unavailable (NOT silently verified).
- [ ] Price-range Proof FROZEN→OBSERVED→SCORED transitions show original immutable ranges, source-reported coverage 42/42, 48/48, 15/72 at verified W43 historical test time, no recomputed score and no stale “current” claim.
- [ ] Edge: original public source link resolves to source commit; exact blob SHA and source SHA-256 checked. Fail without original.
- [ ] Keyboard, VoiceOver, focus visibility, reduced motion, 200% text size, safe area insets; iPhone Safari on physical device required.
- [ ] New front end remains performant; no extra market fetch loop, no new paid backend/data provider, no server-side task or external model router.
- [ ] Existing legacy NOW, PATH, PROOF continue working; verify measured behavior rather than assuming old root is fully compatible.

## Governance/readback

- [ ] Real Node tests, exact PR HEAD checks, source and independent adversarial review.
- [ ] Compare current main against branch; rebase/reconcile any new unrelated main changes before safe merge (never force-push unseen changes).
- [ ] NEXT-only staging build can be viewed on PUBLIC GitHub Pages without changing canonical root and with an explicit “DEVELOPMENT ONLY” disclaimer.
- [ ] Only after owner accepts paired visual & functional test and verified source issue/expiry, prepare **separate** official-root release PR, with exact build/CDN hash, reversal rehearsal and no silent AppDeploy promotion.
- [ ] Final owner release decision recorded separately. No production root changes before then.

**Hard stop:** A screenshot/mock/blue sine wave is never a real issued market forecast; a green CI signal is never a substitute for owner-approved visual geometry.

## 2026-10-23 · Concrete Vite + LIVE browser QA milestone (development ONLY)

- **Independent source-kode app:** `cycle-navigator-premium-v2-1-github-source-qa-71fr1g` (AppDeploy FREE frontend-only test, no backend, no proprietary data). Original first test with default Vite single-entry **FAIL**: direct `/graph-b/source-graph-b.html` returned `NoSuchKey`, even though AppDeploy reported READY. This disproves the claim that READY itself certifies correct published paths.
- **Correction**: Vite root `index.html` was set to original extracted GitHub B HTML/card/SVG source; only import paths were rewritten for root and test cross-origin read-only canonical `/data/` URLs. Second real browser run `e41a6d8b-1822-42d6-a477-76e2c8919a57`: B header + original `B` badge, navy plot, BTC/ETH switch, slider, source-only actual, correctly unavailable W43 blue line, Proof 01→02→03 with provisional W43 score and commit-pinned CN29/30 original URLs, Official action/7-tier/10 PATH stages observed. Browser reported no horizontal clipping; iPhone Safari and pixel-diff remain UNVERIFIED. AppDeploy QA emitted no frontend/network errors at that snapshot. This is a development environment, **not production GitHub Pages**.
- **Third repeat**: AppDeploy's current Vite config was extended *via minimal approved diffs*, keeping `base:'./'` and `maxParallelFileOps:128`, to expressly include **both** `index.html` and `graph-b/source-graph-b.html` in the Rollup multi-entry inputs. READY version `1792788950881` with 0 reported frontend/network errors. Public `fetch_content` independently reads **both** root and nested /graph-b route content, no more `NoSuchKey`.
- **Portable GitHub build candidate**: `premium-v2/vite.config.mjs`, `premium-v2/package.json` pins Vite 6.3.6 + TypeScript 5.7.3, `index.html`, original first-party `assets/CN_LOGO.svg`. `base:'/Investering-Framework-Archive-v1/next/'` and explicit `rollupOptions.input` cover two HTML routes; `publicDir:false` avoids auto-exposing quarantined source. This is versioned in DRAFT #1769 only. **Genuine Node dependency install, lockfile review, Vite build using GitHub CI, and canonical Pages `/next/` are STILL NOT COMPLETED.**
- Distinguish **AppDeploy hosted Vite binary success** (tested) from **GitHub Pages output** (not yet published). AppDeploy reformats/normalizes source after upload and the QA JavaScript uses absolute canonical public JSON URLs, so no assertion of byte-identical published assets. The official product remains unchanged.

The original B SVG source port still needs approval of exact design geometry at 390x844 / 430x932 in native Safari. Historical `HOLD_WAIT` validity and stale spot freshness require accurate clock-edge checks while a browser tab stays open. The public W43 daily blue prospective expected-close path is still **UNAVAILABLE**, so no result may claim two live B curves as a source-complete product.

## 2026-10-23 · Post-Vite multi-entry acceptance proof

- AppDeploy source-QA **version `1792789076700` READY** after adding the same exact first-party canonical `CN_LOGO.svg` to the development header (no new backend, no AppDeploy marketing page source adopted).
- Explicit Vite two-entry version `1792788950881`: BOTH `/` and `/graph-b/source-graph-b.html` returned actual Graph B page content from a fresh external HTTP reader; `NoSuchKey` issue resolved without changing production GitHub Pages.
- Actual Node v22 URL assertions: **6/6 PASS** for `latest.json`, `compass.json` and `publication-lineage.json` from **both** native `/next/graph-b/source-graph-b.mjs` and Vite bundled `/next/assets/source-graph-b.<hash>.js`. Both resolve to `https://donh91.github.io/Investering-Framework-Archive-v1/data/` (no second market data owner).
- Exact GitHub adapter suites re-executed: **24/24** source-only Graph B/Proof/70-30/Compass-PATH adversarial cases, **6/6** source-quarantine preflight cases in V8. Dedicated new `build-next.test.mjs` includes the URL checks; **full Node suite and first-party Vite/Pages dist remain outstanding**.
- External screenshot provider Firecrawl reported **INSUFFICIENT_CREDITS**; no screenshot was fabricated and no additional paid credits were authorized or added. AppDeploy provides generated screenshot URLs, but no manual pixel-by-pixel native Safari owner QA has passed.

This is a Vite/build route proof, **NOT canonical Pages release permission**. Keep PR Draft and `/next` integration subject to separate staged-review gate, and root subject to explicit owner visual accept/rollback.


## 2026-10-23 · New-thread Vite artifact hardening (exact code locally tested)

- Draft #1769 now includes verify-vite-output.mjs and verify-vite-output.test.mjs; staged Graph B HTML has explicit noindex,nofollow.
- Actual local Node 22 run on **byte-identical files** (git blob SHA matching GitHub): node --check on both + node --test verify-vite-output.test.mjs: **6/6 PASS**, 0 FAIL. This is a synthetic fixture/adversarial **validator** test, **NOT** a real Vite build or full Premium suite.
- Verifier mandates BOTH Vite HTML entrypoints, source Graph B markup, noindex markers, every emitted local asset referenced by HTML, correct /Investering-Framework-Archive-v1/next/ basepath, all 3 official public JSON feed references in compiled JS, quarantine of AppDeploy Math.sin demo, SHA-256 per emitted asset. It stops with a nonzero exit on regression. Run npm run verify:next **after** a real Vite build.
- Genuine npm ci is **NOT VERIFIED**: the Draft project has no package-lock.json; do not invent a lockfile or report install success. npm install --package-lock-only --ignore-scripts must be performed in a network-capable controlled environment and lockfile reviewed/committed before npm ci can pass.
- site/build-public.mjs currently deletes site/dist at start. If existing Pages publication is later extended for approved /next/ staging, sequence MUST be: canonical build and all original data/score/lineage stages → npm ci and real Vite multi-entry build → verify:next → existing final artifact checks → existing upload-pages-artifact. Running Vite earlier destroys /next/; do not introduce another Pages workflow or execute an unreviewed staging release.
- **Unverified:** real Vite 6 install/build manifest, full Premium Node suite, current exact-head CI following these commits, actual served Pages /next/, screenshot parity/native iPhone, root-vs-legacy rollback rehearsal, separate staging review/merge authorization and final root release acceptance.
- Remain DRAFT and fail closed until the missing evidence is produced. No production root changes from this hardening.


## 2026-10-23 · Approved mandate execution checkpoint · real Premium root

Owner's full phased mandate approved in chat on 2026-10-23 for phases 1–5, governed noncanonical /next/ staging ONLY. Canonical GitHub Pages homepage replacement remains separate, not delegated by this mandate.

### CODED on existing Draft PR #1769

- premium-root.mjs is now a fail-closed, source-native HTML transformation. Vite's pre HTML hook uses the original graph-b/source-graph-b.html as the SINGLE authored B+Proof+Compass+PATH surface for /next/index.html. The existing nested Graph B entry remains unchanged and independently buildable. This eliminates the root link-only landing problem without creating a second hand-maintained Graph B.
- Added a restrained root hero, direct section navigation, original CN identity, noindex staging disclaimer, source-preserving 7 asset paths and DA/EN-labeled root navigation.
- Added premium-root.test.mjs; extended actual artifact verifier to FAIL if root is merely a link-only landing or lacks B, Proof, Compass or PATH, and updated its positive and negative fixture tests.
- Added stage-next.mjs + stage-next.test.mjs, with guarded npm ci → tests → Vite build → emitted output validation, requiring package-lock.json and SIX pre/post identical SHA-256 snapshots: root index, legacy index, vnext index, latest.json, compass.json, publication-lineage.json. Script is NOT installed in the existing CI and cannot be called a deployed release.
- Extended package.json npm test and stage:pages:next scripts. No new dependency, workflow, scheduler or backend introduced.

### Actually verified this execution

- Fetched exact GitHub source and evaluated source-identical pure premium-root.mjs function in JS V8. Original B, Proof, Kompas/PATH, canonical logo and seven relative asset references preserved; all targeted structural assertions passed and 3/3 malicious/missing-source cases rejected. This validates PURE ROOT ASSEMBLY, not npm/Vite/Chrome.
- AppDeploy existing QA app cycle-navigator-premium-v2-1-github-source-qa-71fr1g updated from the latest owned source assembly without changing its isolated public test JSON feeds. Current READY QA snapshot version 1792792800686, zero AppDeploy-reported frontend and network errors. QA-only source is normalized and data URLs differ by environment, so neither BYTE PARITY nor physical iPhone certification is asserted.
- Source-assembly and staging guard tests have been COMMITTED but a full Node test suite, real npm ci, the GitHub project-basepath Vite build, exact-head CI and independent review remain NOT VERIFIED in this execution. The local terminal cannot resolve github.com/npm; do NOT generate a guessed package-lock.
- Latest real /next/ on Github Pages NOT VERIFIED; public site root remains unchanged by this branch.
- Branch was diverged and 33 commits behind main at most recent comparison. Do not rebase/force-push blindly; reconcile against fresh main before governed merge.

### Next release-bound actions

1. Produce lockfile in a network-capable trusted environment; review npm package integrity/lock reproducibility; exact branch npm ci, all node tests, actual Vite build and emitted artifact validator.
2. Resolve any Vite rebase/module URL breakage, current-main drift, full canonical compatibility and independent review. Add ONLY reviewed stage:pages:next integration AFTER all canonical public/lineage/social steps and BEFORE the existing artifact upload in cycle-navigator-pages.yml. No second Pages workflow.
3. Full browser mobile (390×844 and 430×932), accessible interactions, DA/EN, real source expiry/failure paths, original graph B geometry, historical root/legacy rollback and real /next/ Pages readback. A QA READY is never this acceptance.
4. Governed noncanonical /next/ publication may proceed only with exact-head green checks, required independent review, verified rollback, no budget bypass and real URL evidence. Root homepage stays protected behind a SEPARATE owner visual/data/rollback releaseaccept.


## 2026-10-23 · CI diagnostic and patched Vite pin

- Real exact-head GitHub Actions gate run 40030844172/job/120678411322 (evaluated on HEAD fb1c689b) FAILED the **existing canonical** test 05_CYCLE_NAVIGATOR/site/tests/premium-mobile-browser.test.mjs:408 with Graph B top=747.4375 CSS px, threshold <=740. It is not a pass and cannot be waived. Root is protected by separate release contract. Route to established SITE owner for legitimate DOM/layout fix, compare latest main, run both 390 and 430 mobile tests. Preserve this failure in acceptance evidence.
- Security research checked upstream vitejs/vite Oct 21 advisory GHSA-8g5g-mxqh-grgj and signed v6.4.5 release. Pinned Vite updated from 6.3.6 to patched 6.4.5 (source-only dependency change, no runtime behavior assumed). The future reviewed package-lock must be generated against 6.4.5. No npm install/Vite compile is claimed from this patch.
- The earlier branch-head check outcomes are superseded after any further commit. Re-read current exact head before any merge/release, and do not bypass Actions exhausted-month policy.

## 2026-10-24 · Actual GitHub runner source + Vite + browser evidence · supersedes older readiness notes

**Authority:** SITE #1578, oversight #1156, owner's explicit phases 1–5 noncanonical /next release mandate. Historical 2026-10-23 notes above correctly describe the earlier failures; **their 'no lockfile', '33 behind', 'not wired', 'CI failure' and 'no real Vite/browser test' status statements are now superseded**. Keep the history for traceability.

### Verified actual-source work, not estimated

- PR #1769 safe main synchronization at merge commit `1a6914bdbe2fdf1091bd722168bd00e382ec7780`, without force or change to main; comparing main against pre-documentation head yielded **0 behind**, exclusively premium-v2 source plus the two pre-existing workflow files. Main may change later; recheck.
- Real npm v3 lockfile committed at `05_CYCLE_NAVIGATOR/site/premium-v2/package-lock.json`, directly reconstructed from a GitHub hosted npm runner receipt SHA256 `03c1f1eaed810408a37771270e18322d05d321af2f802dddf8fff0dab633a321`; Vite 6.4.5 and TS 5.7.3 pinned, 66 package entries. The temporary PR-restricted lock-bootstrap step was REMOVED. No hand-written dependency graph.
- Existing `cn-site-v2-gate.yml` now tests Premium via Node, reproducible npm ci + full test suite + actual Vite dual-entry build, artifact validator and actual 390/430 Chrome CDP at the **GitHub Pages prefix**, then canonical existing 390/430 browser tests. No new workflow. Verified 61/61 Premium Node unit/negative tests both before AND after install, 0 fail.
- Real Vite artifact `CN_NEXT_VITE_ARTIFACT_CHECK_v1 = PASS`: `site/dist/next/index.html` and `site/dist/next/graph-b/source-graph-b.html` plus SHA256-hashed CSS/JS, base `/Investering-Framework-Archive-v1/next/`. Zero demo forecasts. Current candidate artifact hash receipts from GitHub CI: index `aa0017b1ec3db7d05ef765ad3347d74dae261681f3df36edd00f8d9222ead6a2`, nested B HTML `c28011aae6fe10cf8a96277f318810607adfb156bc86c2ee9dcdc7aef3af625b`.
- `stage-next.mjs` snapshots **all 62 existing canonical public artifact files** by name and SHA256 before/after build, not just original six sentinels. `ALL_NON_NEXT_ARTIFACT_HASHES_IDENTICAL` PASS. New CSS/JS, missing or changed canonical files and symlinks cause hard fail. Existing `build-public.mjs` still wipes site/dist, so staging remains sequenced strictly **after** canonical build/score/live/lineage/social/final-shell checks.
- Actual headless Chrome CDP `NEXT_VITE_BROWSER_REAL_CDP_PASS` at 390 and 430 CSS px, 0 overflow, original B/Proof/Kompas/PATH on NEXT root, DA/EN, ETH/BTC, nested B entry, real CN logo, no HTTP asset errors, no JS exceptions. Browser runner may restart Chrome once with a new isolated profile; both failures still fail the job. THIS IS NOT PHYSICAL IPHONE SAFARI.
- The previous canonical B top=747.4 mobile failure was superseded by newer `main` reconciliation, with canonical Chrome 390/430 tests PASS (not threshold change or bypass).
- ONE step in **existing** `cycle-navigator-pages.yml` is coded **only on this unmerged branch**, after finalized canonical integrity checks and before existing `upload-pages-artifact@v4`, using `node 05_CYCLE_NAVIGATOR/site/premium-v2/stage-next.mjs`. Exactly one Pages workflow/upload/deploy; root remains the original site. Staging on main is **not** active yet.
- Best last exact-head CI evidence before this documentation commit: head `f9d245485fcb268afe4e836e6f20706e3f257f0d`, **8 SUCCESS, 3 SKIPPED, 0 FAIL**. Real Node/Vite/browser run: https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/40071828979/job/120806725536 . **After ANY subsequent source/documentation commit, rerun/re-read exact HEAD checks; do not extrapolate this evidence.**

### Still NOT satisfied, nonwaivable staging acceptance

- Independent exact-head reviewer approval/adversarial audit: GitHub reviews on PR #1769 = 0 at last check. Review requested in PR conversation / SITE #1578 / Supervisor #1156. Do not impersonate reviewer. Same author cannot self-certify independence.
- Approved 390/430 iPhone Safari original B screenshot/geometry/text parity; actual Safari, zoom/VoiceOver, reduced motion and hands-on source/expiry interactions NOT fully certified by Chrome.
- `/next/` live GitHub Pages 200 + asset checks + canonical root/legacy/data rollback readback must be checked **after** governed merge/deploy. AppDeploy READY is only DEV QA: https://cycle-navigator-premium-v2-1-github-source-qa-71fr1g.v2.appdeploy.ai/
- Need re-read fresh main, exact head, actual GitHub required rules, Actions budget and independent recovery point; no CI bypass, no paid-minute subscription, no direct main push.
- **Separate owner acceptance required to replace official root** after user sees and approves `/next/` on iPhone; current mandate alone authorizes only governed noncanonical staging.

Durable execution summary and explicit reviewer assignment: SITE https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578#issuecomment-6381161809 and Supervisor https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6381165679 .

## 2026-10-24 · Final-review remediation, current execution

Owner mission: repair/review/release existing #1769 to isolated `/next/` only; no root promotion. Earlier historical counts do not certify this new head.

- P2-A: `clearUnissued()` clears Bull/Bear value and explanatory validity. Expired sources also suppress numerical Bull/Bear; current values show original issue and expiry. Offline refresh + DA/EN + open-tab expiry tested.
- P2-B: slider HTML, available observation cap and refresh initialization now allow closing hour 168. Runtime tests distinguish exact hour 167/168 and absent final close, without filling gaps or altering source.
- P2-C: Proof exposes separate observation timestamp, 90-minute source SLA/deadline and STALE/CURRENT alongside unchanged PROVISIONAL score maturity. Every repaint revalidates against clock; one local deadline timer updates an open tab, also before optional external links return; visibility/pageshow revalidate. No extra polling or score computation.
- P2-D: retained existing asset invalidation/request-generation implementation. New runtime adversarial test keeps ETH fetch unresolved while language/slider change, then resolves a newer BTC request before the older ETH response. No old-asset quote survives.
- Real Chrome source QA exposed untranslated static labels; bounded DA/EN heading, ARIA-label and source-status translations added without geometry/redesign or source changes.
- Added 9 runtime tests against actual UI modules + actual source adapters: full Premium suite **76/76 PASS**, genuine committed-lockfile `npm ci` PASS, actual Vite **6.4.5** BOTH entrypoints PASS, compiled asset/basepath verifier PASS. Test-only clock/DOM fixtures never enter published Vite modules.
- Guard-removal negative controls caught **4/4** A/B/C/D regressions; originals restored and full suite passed. This is implementation testing, not independent approval or physical Safari.
- Canonical pipeline: **166/166** existing public product release checks PASS; hourly, source freshness, full-stack, public live precision, lineage self-tests/readback PASS. Full pre/post `stage-next.mjs` SHA-256 inventory: **62/62 non-NEXT canonical assets identical**, no added/deleted/modified outside `next/`.
- Public source at local build: W43/CN #30, observed through `2026-10-24T07:00:00Z`, source equality PASS, STALE_AT_BUNDLE_TIME; Compass `DEGRADED` correctly unavailable, not invented current evidence. Original daily forecast unavailable, no synthetic blue curve.
- Main locally reconciled via ordinary nonforce merge `1bc9208cc` from source `108f02db1da3421b99d46e0455cb21852fdb72b5` (13 newer commits). Only existing Premium subtree and two preexisting site workflow diffs relative to main; no canonical source changes authored in this execution.
- Existing Chrome CI test expanded to 390×844, 430×932 and 1440×1000 plus offline Bull/Bear assertions. Execution on the new exact head must be read back before release; historical Chrome runs are not substituted.

**Still required:** genuinely independent new-head review and applicable platform checks; physical iPhone Safari/VoiceOver/zoom and owner visual acceptance required above; contemporary recovery/safepoint verification before high-impact workflow integration; actual live Pages readback only after governed merge. No waiver or fabricated approval. Root and canonical data remain protected.

Publication note: this host can fetch but ordinary Git push has no GitHub credential. Publish the tested exact tree through the connected Git object API with both original PR head and current-main parent, then fast-forward the existing branch with expected-head verification. No force, direct main write or new PR.
