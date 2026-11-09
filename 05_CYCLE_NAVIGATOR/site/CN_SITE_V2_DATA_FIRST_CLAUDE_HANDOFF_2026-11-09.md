# CN SITE v2 | DATA-FIRST / DESIGN-REPLACEABLE HANDOFF
Owner lane: original CN #1516 and SITE #1578. Prepared 2026-11-09, based on main `fe12174f84b7480c58572a1fdca1dcd05067963a`. This document is a **technical handoff, not release approval**.

## Goal
Claude may completely replace the look and chart implementation of the CN site, while the **original source-owned market meaning and verified published values remain identical**. No alternative chart is automatically approved or live.

## Parallel research lanes (independent reads, one integrated owner)
- R1 Source/clock/quote: original W46 0/7 then 7/7 same-Monday amendment, original issue clock, first eligible scoring hour, hash and source custody; source-owned CN #1516.
- R2 Public distribution: `site/build-public.mjs`, `dist/data/latest.json`, `dist/data/compass.json`, `dist/data/publication-lineage.json`; reject mismatched public issue/week, unsupported quote conversion, stale or missing sources.
- R3 Forecast vs actual geometry: `site/frozen-week-chart.js` and `site/graph-history/index.html`; source day-indexed expected close/low/high, genuine hourly closes with gaps, no smoothing that changes source values or future extrapolation.
- R4 Cross-product integration: Official Compass current-action owner, Master Monday weekly context, CN PATH/rotation, Results/scoreboard. Keep separate authority and freshness; don't promote SHADOW to Official.
- R5 Release/mobile/rollback: `cycle-navigator-pages.yml`, 390/430 Chrome gates, graph-history runtime, deployed CDN parity, actual iPhone Safari acceptance remains distinct.
- R6 Adversarial/data-science: baseline vs actual skill, immature scores, data gaps, out-of-sample evidence, no numeric precision claims merely from 7/7 completeness.

## Design-independent source contract
1. Original CN weekly issuer is the ONLY authority for the seven-day prospective BTC/ETH path. Preserve `05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`, manifest, issue clock, correction receipt, SHA and the first 0/7 revision. No backward reconstruction.
2. Public source for the active week is `/data/latest.json`, specifically `public_live_precision.daily_price_path` (7 original close/low/high values per asset), `hourly_price_path` (genuine hourly observations), `daily_observations`, `price_quote_labels`, `public_series.current_public_projection`, `window_scores`. Data must pass week, issue, UTC, provenance, unit and eligibility gates before drawing.
3. `/data/compass.json` owns current Official Compass. `/data/graph-history/timeline.json` owns the W46+ public historical view; earlier actual-only W45 remains archival. `/data/publication-lineage.json` is an independent freshness and source-to-public equality receipt, not a new forecast authority.
4. A blue dashed curve consists of exactly seven ORIGINAL daily expected-close points at their source-owned UTC target times, with seven source high/low pairs. A green actual curve consists only of observed source-qualified hourly closes, with explicit gaps; the current quote is never a future point. Chart design may be any library or SVG, but geometry must be derived from these values, not illustrative fixtures.
5. Seven-day chart viewport can expand to 14/21 days ONLY as a view; it may NOT invent days 8-21 forecast values. Source absence = explicit unavailable. Quote mismatch = no shared price comparison axis. Missing data must never be interpolated, hidden or silently shown as valid.
6. Official action, weekly context, PATH and scores remain separate authorities. `DEGRADED`, `STALE`, `UNKNOWN`, `ABSTAIN` and immature outcomes cannot be silently converted to positive status, confidence or accuracy. No new investment or model authority.
7. DA/EN, BTC/ETH switching, iPhone 320/390/430, keyboard/touch/VoiceOver/reduced motion, readable source clocks and explicit first-known issuance are product requirements. Do not duplicate site schedulers, providers, paid API calls or source writers.

## Existing verified baseline, not a guarantee for a future redesign
- Original W46 BTC+ETH 7/7 and same-Monday amendment were merged through #2051-#2053; Graph History W46+ repaired in #2056. Existing Pages exact-byte/CDN verification recorded in #1516.
- On 2026-11-09 18:55 UTC, public `latest.json` and `timeline.json` agreed on the seven BTC forecast points. Timeline had 17 consecutive hourly BTC closes, last 17:00 UTC. `compass.json` showed `data_status=OK` with Official source verified. `publication-lineage.json` reported `source_to_public_equality=PASS` but `release_freshness_state=STALE_AT_BUNDLE_TIME` (115.17m versus 90m SLA). **Freshness must be rechecked; do not call all connections continuously healthy.**
- Native Chrome 390/430 tests are documented; independent physical Safari visual approval and real-time browser screenshot are not certified here.

## Claude design freedom
**Replace freely:** page hierarchy, navigation, colors, typography, layout, CSS, component framework, chart renderer, axis, zoom, touch interactions, information density, responsive patterns and visual presentation. Nordic Editorial is a reference, NOT an immutable visual requirement.

**Preserve exactly:** canonical original forecast and actual source values, seven-day UTC target timestamps, forecast/actual distinction, source receipts, privacy allowlist, scoring and immutable issuance, quote semantics, independent current Compass action, history provenance, stale/no-source behavior, and exact-head CI/Pages readback.

**Canonical source adapter promotion on PR #2063 (pending CI/merge):** A byte-identical copy of the existing source-only adapter has been promoted from the isolated design lab to `site/source-adapter/official-source-adapter.mjs`. The original `premium-v2/graph-b/official-source-adapter.mjs` is now a **compatibility re-export** to the canonical file. `site/cn-site-v2-source.mjs` is a zero-logic public re-export, and the ordinary public build ships it together with `source-adapter/official-source-adapter.mjs`. Future Claude page designs can import `/cn-site-v2-source.mjs` (adjust for repository Pages base path) and call the original `readOfficialGraphB(snapshot,asset,{now_utc,publication_lineage})` / `replayObservedUntil` without building a second forecast or time-series model. The original source validation includes exact-quote, first-issued, ISO Monday, hourly gap, daily bounds, lineage and per-asset freshness gates. The current canonical root **still uses the older** `frozen-week-chart.js`; its convergence to this one shared path plus dual-renderer visual equivalence is NOT DONE. Avoid changing production until browser checks, structural compatibility and original release gates qualify.

## Acceptance gates before handing the design to Claude
- [x] W46 7/7 source and public graph-history connection verified at the checked timestamp.
- [x] Existing 390/430 browser gates and production Pages receipt found in original #1516.
- [ ] Both `cn-v2-design-data-boundary.test.mjs` and `cn-v2-real-public-adapter.test.mjs` pass in exact-head CI after the published bundle and lineage are generated. New read-only checks are wired to Pages and Public Contract Gate on this PR; successful CI not yet evidenced.
- [x] Existing source-only adapter promoted without changing its algorithms to `site/source-adapter/official-source-adapter.mjs`, with a compatibility re-export for old Premium design.
- [x] Public design-neutral zero-logic ESM `cn-site-v2-source.mjs` added to source bundle build; final deployment and CDN parity not yet verified.
- [ ] Existing pure adapter and current canonical `frozen-week-chart.js` converge behind ONE verified read path; compare BTC/ETH, stale, 0/7, USD/USDT mismatch, hourly gaps, W46 amendment and W47 rollover.
- [ ] P0 upstream hourly freshness: Source file `03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-09.csv` contained only 17 hours, last close 17:00 UTC; independent CI build 22:26 UTC reported 326.51 min stale and source equality PASS. Native scheduled owner run 17:27 had sequence PASS but intraday CANCELLED; no later hourly owner capture was confirmed in sampled schedule search. Original CN owner evidence/trigger: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516#issuecomment-6753267352 . Must verify two consecutive fresh owner hours and Pages readback; no backfilled or synthetic rates.
- [ ] Real built bundle imports `dist/cn-site-v2-source.mjs` and gives exactly identical Graph B output to the canonical module, BTC+ETH, with measured hour preservation, negative provenance/quote tests. New test is added; pass on final exact HEAD and CDN publish not yet established.
- [ ] Redesign can swap renderer without changing source adapter or canonical forecast, verified by a minimal alternative renderer test.
- [ ] Final pre-Claude `main` SHA and Pages/CDN readback confirmed; then create owner's **single backup tag**.

## Backup requested by owner, execute only AFTER technical completion
Claude is to create **only one tag** on the then-current main: `cn-site-v1-backup-20261109`. No file copies, no site edits, no workflow dispatch for the tag operation. Report the tag and exact commit SHA. Before tagging, verify the tag does not already exist; do not overwrite. Rollback candidate: `git checkout cn-site-v1-backup-20261109 -- 05_CYCLE_NAVIGATOR/site`, then redeploy Pages. **Caution:** this restores only the site tree, not any changed data contracts/workflows; check compatibility before using rollback.

## Native links
- SITE owner: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578
- CN source owner: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516
- Pages: https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/.github/workflows/cycle-navigator-pages.yml
- Public: https://donh91.github.io/Investering-Framework-Archive-v1/
