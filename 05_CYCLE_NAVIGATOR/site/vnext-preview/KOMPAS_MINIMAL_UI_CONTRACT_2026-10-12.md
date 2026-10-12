# Kompas vNext · Minimal Decision-First UI Contract

**Date:** 2026-10-12 · **Owner:** Existing Cycle Navigator site PR #1576, coordination issue #1578  
**Status:** IMPLEMENTED IN ISOLATED PREVIEW, source-snapshot only; not deployed to the existing production GitHub Pages site.

## Intent

The user explicitly requires the **same Kompas as the existing on-demand ChatGPT Kompas** (retaining all signal ownership, time horizons and asset coverage), but **simpler, visually refined, mobile-first**. Explanatory material must be folded behind dropdowns or placed at the bottom/tactically near the signal **only when actionable now**.

This supersedes previous oversized narrative Kompas hero panels, duplicate callout cards, long always-visible rationales or decorative radial market instruments. See also [Editorial v2 Design Standard](EDITORIAL_V2_DESIGN_STANDARD_2026-10-12.md).

## The five-second reading order

1. **HANDLING NU** — authoritative `Official Compass.action_now`, unaltered by any direction/pullback inference. Never manufacture BUY/SELL.
2. **MARKEDSRETNING · 0–12T** — authoritative `Official Compass.horizons.NEXT_12H.expected_direction`, clearly distinct from action.
3. **BULL / BEAR · 1–3d** — a tiny split evidence meter directly from the existing Official Compass `bull_bear_scale.horizons.1_3d` (status OK, total 10, exact source owner and contract). The archived source is **Bull 5 / Bear 5 (NEUTRAL)**; no probability or additional trade permission is implied. Missing, degraded or invalid source data show unavailable rather than a synthesized number. Original **5–7d** and **2–3w** evidence rows are located only in the folded `Min fortolkning` details. Authority: `MARKET_WEATHER_SOURCE_OF_TRUTH_v1`, `EVIDENCE_BALANCE_NOT_PROBABILITY`, `DIRECTION_ONLY_COARSE_v1`.
4. **PULLBACK / SELL / DISTRIBUTION** — source-bound `protection_tracker.pullback_risk_state`, `sell_assessment.state`, and `protection_tracker.distribution_risk` respectively. Must remain visible immediately, including UNKNOWN/UNAVAILABLE values. A pullback watch does not authorize SELL.
5. **Two tables** — `Tid | Retning | Handling` for 0–12h, 1–3d, 5–7d, 2–3w, 4–8w; and `Aktiv | Status | Handling` for BTC, ETH, large caps, mid caps, small caps, microcaps and memes. Memes must never inherit microcaps permission.
6. **All non-immediate exposition below** — exactly two **native `<details>/<summary>` disclosures**, both closed by default: `Min fortolkning` (1–3d synopsis plus other horizon rationale), and `Pullback, beskyttelse & re-entry` (risk class, ETA limitations, invalidation, underlying evidence, SELL authority and recovery context). An understated source/method link sits at the bottom.

## Implementation inventory

- `premium-index.html`: replaces dark duplicate action/heading and visible bulky commentary with two-column white summary, small protection/sell strip, both governed tables and two collapsed contextual disclosures.
- `premium.css`: mobile-first 390/430px design tokens; strong typographic hierarchy, subdued borders, native focus rings, 44px touch-aware summary controls, no trend art, no widget/third-party JS.
- `premium.js`: original source-only 5+7 row renderers preserved; source-bound risk/SELL/distribution inline mapping added, no duplicate SELL scorer or classifier; removes redundant custom toggle event handlers and relies on native details keyboard semantics.
- `premium-i18n.js`: DA/EN translation of new labels and disclosure content while preserving original source statuses, timestamp and frozen provenance.
- `check-premium.mjs`: static regression asserts five+seven source-bearing contracts, risk/status on top, exactly two initially folded native details, no old visible giant Kompas cards, fail-closed source availability and no new signal ownership.
- Existing `seed.json` is STILL deliberately pinned to **CN #28 / W41** and Compass 2026-10-11T13:15:27Z; this preview is **NOT LIVE**. No historical scores, source freezes or price formulas changed.

## Verification and release boundary

- Latest exact-head PR CI: all 9 core site/Compass/architecture pipelines passed on commit `8f7e353a5efcfa9e56f324daf1706f08c3e5f057`.
- Updated isolated AppDeploy preview returned READY and zero reported frontend/network errors.
- Independent browser QA [TinyFish run](https://agent.tinyfish.ai/runs/4ba887b2-0911-46e1-a692-fd71ae32db08) verified action vs direction, three risk labels, exactly 5+7 rows, both closed/open/reclosed disclosures, DA→EN→DA translations and no sideways scroll in tested 1420×945 desktop viewport. The independent browser **could not** set 390×844, so iPhone Safari acceptance remains pending.
- Work release gate: make actual 390/430px mobile screenshot comparison and test native details, long status labels, source-fail-closed state, keyboard/VoiceOver; fix any defects on the same design branch. Reconcile fresh-main before a distinct production integration PR.
- Existing live GitHub Pages site **must not** be modified without verified rollback, data-parity map and final release approval.

**Visual policy:** source-action first; maximum two readily visible tables; elaborate research belongs in disclosures or the Resultater page. Re-evaluate every new UI surface by whether it shortens the user's time to a safe decision, not whether it looks technologically impressive.

## Bull/Bear micro-scale acceptance · 2026-10-12

- `official-bullbear.mjs` is the pure source-only adapter. It requires the exact approved contract, source owner, integer Bull/Bear values totaling 10, matching published bias and authority flags. Unsupported claims fail closed.
- `test-official-bullbear.mjs` covers exact archived 5/5 values, three governed horizons, optional positive source fixtures, missing/malformed/mismatched fields and source immutability.
- `premium-index.html` and `premium.css` present a restrained five-pixel split bar with textual values and an explicit non-probability disclaimer. Other horizons remain inside the existing `Min fortolkning` accordion.
- DA/EN strings are defined in `premium-i18n.js`. Official action, risk, SELL/distribution, five time horizons and seven asset tiers remain separately governed.
- This is a design-preview feature only; GitHub Pages production is unchanged. The archived 2026-W41 seed is not a live October 12 market signal.
