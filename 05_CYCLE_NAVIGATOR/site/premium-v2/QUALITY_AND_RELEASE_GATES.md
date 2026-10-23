# Premium v2.1 · staged candidate acceptance matrix

**Date:** 2026-10-23 · **Owner:** SITE #1578 · **Oversight:** #1156  
**Current state:** ISOLATED DEVELOPMENT ONLY, NOT LIVE, NOT OWNER VISUALLY APPROVED.  
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
