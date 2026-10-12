# Pullback time qualification · Read-only ETA UI / Work release note

**Prepared**: 2026-10-12 · **Owner**: Existing CN vNext site PR #1576 and supervisor issue #1578  
**Status**: CODED + SOURCE TESTED + VITE BUNDLED in Draft branch. **ETA revision NOT YET DEPLOYED** to AppDeploy public preview. Production Pages unchanged.

## Product correction requested

User approved minimalist editorial home and Kompas, but correctly noted that the Pullback status on its own looks like an unconditional market crash warning. The immediate UI must connect each governed risk watch to **source-backed period / start / end uncertainty**. It must not infer exact onset, magnitude, sell permission or a 0–100 probability.

- Overblik: keep one small Pullback metric, add source-time line beside status, and place one caveat right under the fact grid. No extra illustrations.
- Kompas: show exactly the same source-time line directly underneath the governed `PULLBACK` status; separate SELL/TRIM and Distribution remain visible. Existing longer explanation stays in the native Pullback disclosure below both decision tables.
- DA/EN: localized qualifiers, no LLM reclassification; zero change to five horizons, seven asset tiers, official action and Bull/Bear meter.
- Read-only integration is `official-pullback-eta.mjs`, invoked by `premium.js` only on the verified source bundle, and `test-official-pullback-eta.mjs` includes thirteen source/negative cases.

## Confirmed immutable source examples

### Historic preview (archived Sunday 11 October)

Original Official Compass `CMP-20261011-7d14a9ee5914`, 2026-W41:
- Source risk `BUILDING`; `eta_window` exactly **"Possible W41 retest, particularly Day 3–7; timing and occurrence unconfirmed."**
- Structured public onset-start/end: **not present**. Strictly parsed *that single canonical sentence*, projected its **source W41 days 3–7** to **7–11 October 2026**. The period is explicitly **possible / historical**. It is not a verified dip, not a prediction that the event occurred and not confirmed onset/end.
- Preview status remains **POINT_IN_TIME_PREVIEW_ARCHIVE_NOT_LIVE**. It cannot act as the current live risk feed.

### Latest official W42 source inspected (not substituted into archived preview)

Official public Compass `CMP-20261012-3f1e99c2868e` issued 2026-10-12T16:18:05Z:
- `pullback_risk_state = ELEVATED`
- `eta_window = Possible renewed retest during W42; onset timing is unsupported.`
- `public_explanation.contract = CN_PUBLIC_PROTECTION_COPY_v1`; `forecast_week = 2026-W42`; `onset_start_utc = null` and `onset_end_utc = null`.
- Valid public wording for live consumer: **"Muligt i uge 42 · ingen præcis ETA"**, followed by **"Start/slut og størrelse ikke kvantificeret. Kun watch – ikke SELL."**
- DO NOT turn forecast-week bounds into purported forecast event start/end, or into SELL/trim advice.

## Strict precedence rules

1. Owner must be `Official Compass` only, original `COMPASS_PROTECTION_TRACKER_v1`; source data `OK`, official authority permits no new market classifier or portfolio execution.
2. When an aligned typed `CN_PUBLIC_PROTECTION_COPY_v1` exists, require exact `forecast_week` and `risk_state` agreement; invalid/missing alignment is `ETA NOT VERIFIED`.
3. Both onset endpoints present + parseable UTC + chronologically sorted => **possible governed forecast time range**, not actual realized onset.
4. Both onset endpoints NULL => only the sourced week context plus `NO PRECISE ETA`.
5. Partial dates, wrong contract, unsupported week, inconsistent risk, historic prose variations => do NOT parse into a synthetic ETA.
6. Exactly one historical canonical W41 string is recognized for source day ordinals 3–7; all other free prose remains `NO SUPPORTED ONSET`.
7. Risk state, separate SELL and distribution never gain authority from the time display. An unverified/unavailable source hides or explicitly marks ETA unavailable.
8. Source snapshot time + public CN identity must remain visible; no freshness/real-time claim for Sunday seed.

## CI and deploy audit

- Existing exact-head static contract / score lineage / DA/EN / 30 feed parity / Official Bull/Bear tests passed.
- `test-official-pullback-eta.mjs`: **13/13 pass** for historic W41, W42 null starts, valid typed dates, partial/end-before-start, invalid Z, wrong contract/week/state, noncanonical prose, source authority fail-closed.
- Production-style `verify-vite-bundle.mjs`: uses an ephemeral Vite installation **only inside PR CI**. This caught a real duplicate `currentLanguage()` export that the old script VM smoke test missed. The duplicate was fixed. Vite bundle then **PASSED** on GitHub PR head `1d516168c505be81f89b2c3640da4c929f054e8b`.
- AppDeploy initial two builds failed before the Vite root cause was known. Rolled back to last stable **v12** snapshot `1791825108854`, which redeployed READY with no frontend/network errors.
- New GitHub source is corrected, but the final AppDeploy redeployment was BLOCKED BY **CREDITS_USAGE_LIMIT_REACHED**, free tier reset at **2026-10-13T00:00:00Z**. DO NOT claim ETA code is live before a new READY receipt.
- No paid upgrade needed. No duplicate automation required. The EXISTING enabled supervisor #1578 owns this release gate.

## Next eligible execution: existing Work/Supervisor

After the reset, read this source file and current main/branch state, then synchronize these files from GitHub branch `design/cn-vnext-public-proof-20261011` to existing AppDeploy app `cycle-navigator-vnext-preview-l1nbkq` only:

| GitHub source | AppDeploy destination |
|---|---|
| `premium-index.html` | `index.html` (rewrite `premium.css` → `src/styles.css`, `premium.js` → `src/main.ts`) |
| `premium.css` | `src/styles.css` |
| `premium.js` | `src/main.ts` (rewrite `./premium-i18n.js` → `./i18n.js`; other `.mjs` imports remain relative in `src/`) |
| `premium-i18n.js` | `src/i18n.js` |
| `official-pullback-eta.mjs` | `src/official-pullback-eta.mjs` |
| Existing `seed.json` | `public/seed.json` stays pinned and unchanged |

Keep `src/official-bullbear.mjs` unchanged. Preserve existing AppDeploy E2E test suite and append risk-ETA functional test if not present.

**Verify**: AppDeploy deployment READY / no frontend-network errors, 390×844 and 430×932 actual mobile-width QA, desktop, DA→EN→DA, source week W41 contextualized as historic, exact risk/SELL separation, both pages time line, collapsed explanations, Bull/Bear and 5+7 rows, no overflow. Screenshot after-fix. Also verify all 9 GitHub Actions checks on the exact latest PR head, then retain PR #1576 Draft until separate production-source parity and rollback gates pass.

**Release boundary**: Product design approval ≠ retroactive proof of forecast, W42 scoring, independent time anchoring or permission to change current production Pages.
