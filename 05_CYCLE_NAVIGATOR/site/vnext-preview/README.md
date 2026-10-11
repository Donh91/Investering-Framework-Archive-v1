# Cycle Navigator vNext - Interactive design preview (2026-10-11)

**Preview URL:** https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/

**Status:** ISOLATED INTERACTIVE PREVIEW / CURRENT PRODUCTION UNCHANGED / NOT CONTINUOUS LIVE SIGNAL

## Latest v2 result-page evolution (Sunday 2026-10-11)

- **DA/EN toggle** now appears in the desktop/iPhone header and persists the selected language; the new W42 score story has bilingual catalog entries.
- The HOME proof teaser no longer promotes the historical CN27 82.05% figure as the leading metric. It instead introduces the **new W42 forward accuracy / direction / pullback Edge era**, with explicit PENDING status.
- RESULTS now leads with **Price Range weekly + intradays**, **Direction/Rotation claims**, and **Pullback Edge warnings**, all individually gated by prospective freeze/outcome completion.
- A clear 12–48h / 7d / 14d / 21d / 28d / 56d claim checkpoint rail explains that longer original forecasts remain open across subsequent CN issues.
- Pullback tape distinguishes explicit warning vs no-warning, possible onset, severity, recovery and independent altcoin basket impact. Each absent source observation is UNKNOWN / ABSTAIN, not 100 or 0.
- The existing CN1–27 and X-era score summary, frozen-vs-actual BTC/ETH comparison chart and historical rows are preserved **behind a Legacy Scores disclosure**, not deleted.
- Preview remains pinned to CN28/W41 and official Compass 11 Oct; **none of the v2 W42 scores or facts have yet been fabricated or graded**.

Implemented and merged scoring core: https://github.com/Donh91/CycleNavigator-scores/pull/3 . Existing weekly CN now has source-bound new-era freeze step: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1577 . Neither feature creates a new scheduled worker. Work-owned integration and source-test roadmap: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578 .

## How to preview

Open the URL on iPhone Safari or desktop. Bottom navigation on iPhone:

1. **Overblik** - current-source official direction vs action, Compass authority, pullback protection, one simplified market-cycle journey, frozen BTC/ETH W41 scenario corridors and latest public score credibility.
2. **Kompas** - exactly two narrow three-column action tables (five horizons and seven independent capitalization rungs), official source permission, compact interpretation, separate SELL/Distribution/Re-entry.
3. **Resultater** - CN #27 completed public score (W40), observed-vs-frozen price corridor chart with BTC/ETH toggle, all 27 historical public score claims with method-era labels, and link to independent score repo.

## Preview source receipt

The preview uses a pinned, allowlisted, source-derived JSON seed saved as `seed.json`:

- Weekly CN public #28, forecast week **2026-W41**, from `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`, official source status **DEGRADED** and its frozen machine package for W41. No downgrade status is concealed.
- Official Compass ID **CMP-20261011-7d14a9ee5914**, published **2026-10-11T13:15:27Z**, `data_status=OK`, `action_now=HOLD_WAIT`; 12h direction UP and 1-3D/5-7D/2-3W MIXED, 4-8W UNAVAILABLE. The snapshot is a time-stamped point-in-time source, not an auto-refreshing market recommendation.
- Protection tracker: pullback BUILDING with low-quality risk evidence and uncertain ETA; distribution UNKNOWN; separate SELL assessment UNAVAILABLE; re-entry INACTIVE.
- Public completed CN #27, **2026-W40**, Price Range Precision **82.05%**; BTC **82.27%**, ETH **81.82%**; market/structure accuracy percentage **UNDEFINED** from CN #27; frozen claim evaluation is separate. Graph uses the exact six public range scorecard rows, no simulated prices.
- Original `05_CYCLE_NAVIGATOR/site/history-scoreboard.json` CN #1-27, kept as original separate-era score claims. Modern scorecards for CN #23-27 and all historic 27 issue entries are now public in `https://github.com/Donh91/CycleNavigator-scores`, but do not have independent cryptographic proof of forecast-before-outcome. No claim that Git commits are immutable.

No keys, wallets, private holdings, hidden repo data or non-public research included in the preview seed.

## Files

- `premium-index.html`: semantic layout for three views, custom inline SVG identity/artwork, source/a11y dialog, touch navigation and chart controls.
- `premium.css`: mobile-first Quiet Precision visual system, custom chart grammar and reduced-motion.
- `premium.js`: read-only source contract validation and navigation, explanation/score rendering, transcript-copy interaction; fails closed on missing/invalid seed. Danish editorial translations are guarded by exact Compass ID+forecast week to avoid translating changed/new source as if it were the frozen snapshot.
- `seed.json`: source-derived public material with exact model/data identity.
- `check-premium.mjs`: zero-dependency CI integrity/safe-DOM/syntax check.
- Earlier `index.html`/`check-preview.mjs` are retained for design comparison only and are NOT the polished public AppDeploy preview.
- `../DESIGN_MOTION_REFERENCE_LIBRARY.md`: all links from motion-design inspiration article.

## Design principles / limitations

- One actionable narrative at a time. Official Compass decides today's action; weekly CN remains independently frozen; the frontend never becomes a new signal/score generator.
- The static illustrated cycle journey is a sequence of possible gates, **not** a dynamically confirmed 4–8-week cycle checkpoint or an ETA.
- The 7D scenario corridors are *published forecast ranges*, not probabilities or point forecasts.
- Historic range bars plot published frozen and realized extrema only; they are not synthesized price trajectories.
- All exposed data must show source time, owner role and stale/degraded limitations.
- Preview deployment is independent from the GitHub Pages production site; current production code, build pipeline and user automations have NOT been modified.

## Next release gates

1. Capture and review actual Safari iPhone screenshots at 390 and 430 widths and desktop; compare with current live pages. QA snapshot URLs are supplied by the standalone preview host but independent human review is still pending.
2. Source/API parity tests against actual production public `data/latest.json` and `data/compass.json`, including stale/misaligned/partial fixtures, i18n and projected current status. Do not use this pinned preview seed in a production hot-reload feed.
3. Check content inventory: move every present NOW/PATH/WHY/PROOF section to appropriate visible, expandable or archived destination; no unintentional omission.
4. Integrate source-locked score navigation with published `CycleNavigator-scores` release integrity when attestation and external timing gates exist; never claim proof prematurely.
5. Merge any bounded site production work only after fresh-main contract review and product/visual acceptance, independent of any other running Work/Codex missions.

**Scored historical public claims are not investment returns or a demonstrated profit-making trading edge.**

## vNext Motion QA update · 2026-10-11

- A second X article supplied a complete list of 20 motion-design repositories. The complete links, product fit and future adoption decisions are frozen in [MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md](MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md) and cross-linked from the canonical site design reference library.
- The **Resultater** page now provides a source-honest `Se animeret sammenligning` action, opening the older CN #27 source comparison inside the Legacy section without promoting that historical result as a new v2 Edge metric.
- Animation is deterministic and **data-invariant**: frozen range bars (source scorecard) are revealed, then observed low–high bars, then the precomputed score. Existing endpoints, price scales, grade formula and 6 source rows never change.
- A small in-place `Afspil sammenligning` button makes it repeatable; BTC/ETH switch and DA/EN switch remain source-driven. No sound, 3D, vendor CDN or new framework/dependency.
- All historical data and score metrics are fully visible when `prefers-reduced-motion: reduce` is active; default motion finishes after ~880ms and does not loop.
- The score visual stays folded in the Legacy disclosure as required by the new Score Era product concept. One tasteful direct link in the v2 section makes it discoverable when desired.
- Programmatic source contract and motion smoke tests are included in `check-premium.mjs`, checked on PR #1576. Standalone AppDeploy reports ready and no frontend/network errors as of the last deployment. Native iPhone Safari visual/manual sign-off and production owner mapping remain pending.

**Guardrails**: This animation is historical educational visualization, not a simulated market progression, forecast path, trading signal, independent cryptographic attestation or demonstration of statistically significant profitable Edge.

## Single Work handover packet

**START HERE:** [WORK_EXECUTION_PACKET_2026-10-11.md](WORK_EXECUTION_PACKET_2026-10-11.md) — step-by-step Work browser/Safari UI audit, original-vs-new IA inventory, source parity, proof/risk semantics, exact screenshot/CI gates, production safety and complete ready-to-copy launch prompt. Coordinates with [Archive issue #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578). **Prepared, not independently run yet.**
