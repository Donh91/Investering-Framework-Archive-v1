# PATH vNext · source/UX completion receipt · 13 October 2026

**Implementation owner**: existing Draft PR [#1576](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1576), Work/site issue [#1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578).  
**Old production owner**: PATH v3 [issue #1518](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1518), site product contract `SITE_CONTRACT.md`.  
**Scope**: PATH on the approved minimal vNext Overview; original Kompas, Resultater, source freezes and trading ownership are unchanged. Pullback Decision Profile design is deliberately **HELD for Task 2**; no extra UI work before admitted research.  
**Status**: **PATH DESIGN + SOURCE CODE + VITE/CI + ISOLATED PREVIEW + INDEPENDENT BROWSER QA COMPLETE**. **NATIVE IPHONE SAFARI + REAL-TIME PRODUCTION FEED/PAGES RELEASE NOT VERIFIED/NOT DEPLOYED**.

## Executive deliverables

- Archived five-stop PATH **no longer has hard-coded "BTC leads now"**. The current example only shows a **frozen, completed W40 BTC leadership reference** inside public CN #28/W41, with highly visible `ARKIV · IKKE LIVE · DEGRADED`.
- First-gate label `ETH/BTC skal stabiliseres og fastholdes` is conditional. ETH `HOLD` in the Official Compass is **not** silently turned into confirmed Ethereum leadership.
- Five always-visible landmarks: BTC, ETH, Large + mid, Altseason ignition, Exit/protection. The real **ten-stage canonical cycle** is accessible in one closed-by-default **native <details>** disclosure, together with 2–3W and 4–8W original-source context and separate Protection/Sell/Reentry truth.
- One compact `ALTSEASON-WATCH` rather than multiple competing timers. 30d shadow activity is not broad altseason; 90d/365d source confirmation missing and calendar ETA explicitly `Ingen verificeret ETA`. No synthetic dot spacing or countdown generated.
- Compact typed capital rotation, seven tiers: BTC HOLD, ETH HOLD, LARGE/MID/SMALL WAIT, MICRO HARD_WAIT, MEMES UNAVAILABLE. The site does not copy MICRO permission into MEMES. No second Compass trading owner.
- DA/EN both static labels and freshly source-rendered phase/rotation/ETA text; locale changes do not alter source data or stage order.
- Parent source contracts: original weekly CN frozen `market_state / rotation_ladder / altseason_countdown / decision_projection`; separate Official Compass `capitalization_ladder / protection / sell / reentry`. Site has no extra market classification, risk model, execution permission or wallet access.

## Source/type implementation inventory

| File | Purpose |
|---|---|
| `official-path.mjs` | Pure owner-data projection. Ten ordered phases and five overview stops; no client-side inferred ETA/current phase. Archive ID bound to exact W41 preview, future live requires first-party verified join. |
| `premium-index.html`, `premium.css` | Quiet editorial single PATH panel with current/next, brief cycle rail, Altseason Watch, seven-tier rotation and native full-cycle disclosure. |
| `premium.js`, `premium-i18n.js` | Source-render on authenticated seed and DA/EN switch; fail-closed on invalid source. No old custom expand-cycle onclick. |
| `official-feed-parity.mjs` | Separate future public site owner readback: PATH result **only if latest+Compass delivery fresh and canonical weekly/Compass join ALIGNED**, and typed original data exists. Returns `UNAVAILABLE` otherwise. This is an integration interface, not proof a vNext production consumer is already installed. |
| `test-official-path.mjs` | 16 deterministic source/negative tests (10 phases, 5 steps, seven tiers, ETH HOLD≠leadership, shadow watch≠altseason, no ETA, no source leak, stale/mismatched, DA/EN). |
| `test-official-feed-parity.mjs` | Four additional live PATH readback/negative cases, in the existing shared source-parity test suite. |
| `check-premium.mjs` | HTML and UI binding smoke checks for native disclosure and no hard-coded phase. |
| `verify-vite-bundle.mjs` + existing `.github/workflows/cn-vnext-preview-check.yml` | Real Vite production-style bundle and source/tamper tests without an added scheduler. |

## Verification evidence

- GitHub site Draft PR #1576 exact latest UI code check: 9 established site/architecture/Compass workflows **completed SUCCESS** on `e65a02085a253adc2ee6d7456b0bafb5ef335604` before this documentation commit; recheck on current branch HEAD after later updates.
- Existing isolated AppDeploy app `cycle-navigator-vnext-preview-l1nbkq` redeployed **READY**, QA snapshot reported **0 frontend errors and 0 network errors**.
- Site preview: https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/
- Host-generated browser screenshots (not independently human reviewed as real Safari):
  - mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791871339939/mobile.png
  - desktop: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791871339939/web.png
- Independent read-only browser run: https://agent.tinyfish.ai/runs/269fd231-3a7d-4fba-909a-1c9b32b137ac
  - Browser reported **988×2321 CSS viewport**. DA→EN→DA, source archive identity, five stages, ten full stages, seven action states, ALT watch no ETA, 2–3W original context / 4–8W not supported, Kompas and Resultater routes, no overlap/horizontal overflow: **PASS**.
  - **The browser explicitly did not offer 390×844 / 430×932 or native iPhone Safari emulation.** No native mobile acceptance, keyboard/VoiceOver accessibility certification or trustworthy manual after-fix screenshot claim.

## Final remaining release gates (single owner, no duplicate task)

1. Real mobile/Safari at 390px and 430px; source banner, five-stage route, seven-tier no-overflow, native details keyboard/VoiceOver, DA/EN switch, bottom dock and all 3 pages; attach screenshots. Existing issue #1518 tracks previous production PATH baseline; vNext owner #1578 must record new preview after-fix.
2. Live public `site/build-public.mjs` feed consumption is still a separate **bounded production consumer PR**, not merged on this Draft branch. Verify `CN_PUBLIC_SNAPSHOT_V2` + `PUBLIC_COMPASS_PROJECTION_v1` exact source identity, weekly DEGRADED, time checks, LIVE/STALE and source-to-element inventory. `official-feed-parity.mjs` is prepared and tested, but not sufficient to claim live website release.
3. Protect existing Pages deployment with rollback and independently reviewed exact main merge SHA, artifacts/readback and iPhone/DA/EN release gate. Keep PR #1576 Draft and production untouched until accepted. Do not merge the entire prototype into production.
4. PDP/Task 2 research, statistical probability, future pullback stages and 1–10 calibration are **intentionally not implemented in the PATH design**; future updates enter via Official Compass **only after independent admission**. Do not invent a source clock or SELL to make UI feel complete.

**Completion boundary**: PATH **preview work DONE**; PATH **public production rollout still gated**. Zero historical forecasts, weekly scores, market decisions or existing automation schedules modified by these PATH changes.
