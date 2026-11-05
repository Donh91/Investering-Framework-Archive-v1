# Cycle Navigator PATH · Quiet Editorial D0–D6

**Owner-approved 2026-11-05.** Existing SITE owner #1578; Supervisor #1156 receives closure receipts only. Product surface: the existing canonical Premium/VNext `PATH` tab. **Design and public source presentation only. No second forecast engine.**

## D0 · Audit, specific documented UI problems

The previous `vnext-live/index.html` and `premium-experience.css` defined 10 stages with a vertical spine but had multiple layers of historical overrides; numbers, status and names competed for space. Rotation used seven min-width cards inside a horizontal overflow rail even on narrow phones. PATH had three visually separate cycle/watch modules, contrary to the two-primary-layer PATH v3 source/product contract. Public source explanation displayed raw issue/Compass identity and left status links outside the reading narrative. The October SITE source-gated PATH v3 already rejects invalid current Compass/weekly joins, and **must not be weakened**. Existing Graph B and Compass are not design targets.

## Product system

Editorial, sober financial UI; one white card per section on an extremely pale neutral surface. Navy `#142940` for primary information, slate for secondary, sourced blue `#366eb2` for the existing *frozen weekly reference only*, reserved amber `#99692d` for a *source-provided unconfirmed next watch only*, neutral gray for unverified. None of these encodes probability, BUY/SELL, confirmation of altseason or an elapsed count. No gradients, ornamental icons, animation, AI-generated visuals or invented precision. Source-stamped pricing or projections are **not changed**.

Structure:
1. Weekly orientation. One documented reference and one next source condition, without implying a live phase progression or calendar ETA.
2. Market cycle, ten ordered structural stages. Chronological unbroken spine, minimum readable row height and one separate, visible evidence label per stage. The historical source reference is explicitly **not** a confirmed stage transition.
3. Compact Altseason Watch condition **within** the Market Cycle section, not a duplicate stage rail.
4. Capital rotation, one independent source/action field for BTC, ETH, LARGE_CAPS, MID_CAPS, SMALL_CAPS, MICROCAPS, MEMES. The visual order is **not** evidence of money flowing between them. A missing segment remains explicitly unverified and never inherits a neighbor's action.
5. Sources & Method: one unobtrusive closed-by-default disclosure, short DA/EN high-level explanation and exactly three public navigation links (CN, Compass, publicly scored archive). No raw internal source SHA, workflow, repository names in front-facing copy or protected data. Exact raw source remains only at the public destinations.
6. The existing globally visible Official Compass/source-expiry readback, approved Graph B and chart controls are untouched.

## Source and authority boundaries

- `pathModel` is the existing authoritative read-only selector: only `SOURCE_BOUND` + **FRESH** Official Compass + identical CN week/issue/Compass identity may display a blue reference or amber next condition.
- `pathRotationDisplay` projects the seven fixed UI names. Missing/expired/unsupported actions display *await source*, without a new state classifier or synthetic action. No MEMES borrowing MICROCAPS.
- `pathSourceReadback` separately joins the exact public CN `forecast_week` / `public_issue_number` and the native USDT hourly capture. It may display the **last observed UTC source clock localized in Europe/Copenhagen**, never an invented live price and never infer forecast qualification from spot freshness. A valid weekly join and an eligible hourly capture remain different claims.
- No modifications to immutable CN forecast freezes, weekly model cost, official scoring, client order/trading, pullback thresholds, source TTL, data publish or any agent schedule.
- The user-facing source summary must be understandable without implementation concepts like internal orchestrator, lineage, canonical, PIT authority, byte hashes or fail-closed.

## D5/D6 · Executable gates

- Use existing `vnext-live/validate.mjs` / `test-premium-experience.mjs` as the source identity regression owner. Add explicit proof that wrong week, issue, source identity, expired Compass, missing hourly feed, invalid currency and invalid stage/actions do **not** promote display.
- Assert ten stage rows, one nested altseason watch, exactly seven independent rotation entries, three public source links, closed-by-default accessible disclosure, DA/EN text coverage, scoped CSS and mobile/keyboard/focus contract.
- Existing Site Product Gate already executes real Chrome at 390 and 430 px; extend supported 320/768/desktop checks if the existing browser test infrastructure allows. Never claim native iPhone Safari certification from Chrome alone.
- Exact-head PR GitHub CI, source-level independent review where available, merge guarded by HEAD SHA, `main` readback and independently read the public Pages URL. A successful deployment **must** be verified separately from successful CI.
- Document any actual blocker or non-implemented screen width, do not silently treat a mockup as a release.

## Bounded release and rollback

Single original PR, minimal production code paths: `vnext-live/index.html`, `premium-experience.mjs`, PATH-scoped `premium-experience.css`, source/component tests. Preserve old page source in Git history; revert the merge commit to restore prior path layout, without touching published data. S1 needs one final closure receipt, not a second supervisor or a recurring review loop.

**Forbidden:** static stage 03 CURRENT, orange watch without eligible public source, USD/USDT conversion, fabricated 7/7 Monday prices, fake screenshots, portfolio execution, new APIs, additional cron, styling of Graph B or Official Compass.
