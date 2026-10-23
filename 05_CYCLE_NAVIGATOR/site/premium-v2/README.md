# Cycle Navigator · Premium v2.1

**APPROVED MISSION, NOT APPROVED PRODUCTION RELEASE**

This folder is an **isolated development lane** under SITE #1578 and Supervisor #1156. It is deliberately NOT copied by the existing `05_CYCLE_NAVIGATOR/site/build-public.mjs` (which currently enumerates its public site assets). Nothing in this folder should appear on the official GitHub Pages homepage until separately reviewed and released.

Read in order:

1. `design-registry.json`: exact authority ordering, source paths, approved vs rejected art direction and references.
2. `RECOVERY_BASELINE.md`: P0 source-bound baseline, actual HTTP-readback evidence and unverified legacy behavior.
3. `reference/appdeploy-bc/README.md`: exact AppDeploy B/C snapshot context; the copied visual source is a deliberately quarantined DEMO, NEVER a canonical price source.
4. `graph-b/official-source-adapter.mjs` and tests: pure, source-only data gate, no HTTP or market decisions.
5. SITE `DESIGN.md`, `SITE_CONTRACT.md`, `PATH_V3_CYCLE_ROTATION_PRODUCT_SPEC.md` and the older Kompas Minimal contract before extending components.

Release progression: **RECOVERY → SOURCE_FREEZE → COMPONENT_PORT → DATA_ADAPTER → B+PROOF+KOMPAS+PATH → MULTIVIEWPORT_DIFF → NATIVE_SAFARI → REVIEW/CI → EXPLICIT_RELEASE_DECISION → CDN_READBACK.**

AppDeploy is exclusively DESIGN AND TEST; GitHub is version control; Pages remains one canonical public site. Port actual source components rather than layering more overrides on the wrong frontend. Tests must reject demo sine wave or post-hoc blue price interpolation, mismatched CN issue, stale/retracted records, fake historical precision and source masks.

No new GitHub Actions workflows, paid design packages, external API keys, backend, scheduler, DB or additional supervisor are authorized in this lane. The existing October 2026 GitHub Actions minutes constraints remain binding.

**Never mistake files written to this isolated folder, a Draft PR, or a passing syntax test for a visually approved live website.**

## Delivery update · 23 October 2026 · Draft #1769

**Candidate scope developed (not live):**
- Graph B: `graph-b/source-graph-b.html` + copied original authored B CSS + pure B data adapter and guarded SVG renderer
- Proof: three-step source → observed → provisional score explorer, exact immutable public original URL candidate from provisional readback receipts; no independently VERIFIED score banner
- Compass: read-only owner-source `HOLD_WAIT`, issued-time and expiry gate, five official horizons and 7 tiers, coarse Bull/Bear *evidence* (not probability)
- PATH: original ten-phase taxonomy with source-guarded active phase. Current phase `UNAVAILABLE` leaves all stages unselected
- DA/EN: single B language switch emits `cn:languagechange`, other components render bilingual from their source data
- Source states: verified observed-hour replay cannot fabricate missing hours, stale market data cannot remain flagged current after its source-based freshness expiration, and an open Compass tab expires the action based on original valid-until clock
- `build-next.mjs`: compile-free static entrypoint copied ONLY into `site/dist/next` from 11 explicit approved assets; no AppDeploy mock scripts, no original source repo secrets, no public root or workflow edits

Read `QUALITY_AND_RELEASE_GATES.md` before any staged Pages connection. The NEXT packager is LOCAL ONLY and has NOT been invoked in the canonical GitHub workflow. No direct public preview link is certified.

The quarantined nine-file AppDeploy B/C source snapshot must never be copied into `/next/` or main site bundle. Only derived, reviewed original DOM/SVG and authored CSS can be packaged. `graph-b/source-graph-b.css` was copied with native CSS rules, excluding original non-native `@tailwind` expansion directives. Optional Vite/TS toolchain remains a separate justified proof, not a dependency for this first source parity candidate.

The original legacy route was inspected in a live browser session `84c400bd-5b98-49bd-8ac8-14e226e5fa7d`: NOW/PATH/PROOF navigation and DA/ENG worked, old hourly chart rendered, but Official and price were labeled STALE/NOT CURRENT. This is **not yet a certified pixel-matched or native Safari-accepted rollback**.

No fake blue prospective curve on W43; source W43 `CN_FROZEN_DAILY_PRICE_PATH_v1` remains `UNAVAILABLE` for BTC and ETH. The public Edge archive is also not independently sealed; historical W42/W43 original claims currently 10/10 ABSTAIN each. No frontend success may promote these research and market source statuses.

**Release decision remains separate:** first actual Node tests, static build, source-readback, browser screenshot diff, physical iPhone Safari, independent review, and written owner acceptance. Do not merge/release based on these documentation and isolated V8 tests alone.
