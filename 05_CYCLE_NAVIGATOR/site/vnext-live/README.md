# Cycle Navigator · PREMIUM vNext same-origin live candidate

**State:** staged candidate only. Never replace the canonical homepage through this package.

URL after the existing approved Pages build and natural deployment: `/Investering-Framework-Archive-v1/vnext/`

This is a new **live-source-connected candidate**, not the historical W40/W41 design demo `#1576`. It uses the vetted Quiet Precision principles and copies its **read-only source-parity adapter** and helper modules directly from Draft #1576, without `seed.json` or archived prices.

## Origin and authority

- The existing `site/build-public.mjs` writes the same original first-party public `dist/data/latest.json` and `dist/data/compass.json` used by the main website. This candidate fetches only `../data/latest.json` + `../data/compass.json`.
- `official-feed-parity.mjs` remains strict: public CN week, machine issue, Official Compass alignment, owner source expiry, completed score identity and 168 eligible hours are verified before corresponding values appear. False/late/wrong-week action is `UNAVAILABLE`. The 0–12h direction is explicitly labelled an observation proxy, not predictive edge.
- **All three primary views** Overblik / Kompas / Resultater use CURRENT first-party data, not the frozen archived `seed.json`. Horizon and 7-tier asset action tables only render when current Official Compass permits it; otherwise unavailable. The completed score is historic (latest completed week), properly separated from current frozen week, and market/structure scores are never fabricated.
- The frozen weekly price chart is the EXISTING audited first-party `../frozen-week-chart.js` + pinned TradingView vendor assets from the existing Pages build. It cannot draw a seven-point forecast for W43 where original source abstained; legacy three genuine intervals remain. It updates only from public `public_live_precision` with eligible observations.
- No new provider, scheduler, workflow, analytics vendor, trade permission, signal model, score engine, API bill, portfolio state or private files.

## QA and pending product gates

- `vnext-live/validate.mjs` (invoked from existing `validate-v2.mjs`) tests W43 DEGRADED/weekly-range source parity, Official freshness, 3-page contract, latest completed W42 score, stale/wrong-week/expired owner/partial evidence/legacy score refusal and source-only file allowlist. Stage builder also copies all candidate assets into existing Pages `dist/vnext/`; current `dist/index.html` untouched.
- CI PASS proves source/syntax integrity, **not** full iPhone Safari/VoiceOver or complete visual acceptance.
- Next QA: actual 390/430 Safari + DA/EN, BTC/ETH, missing daily path, post-freeze original 7-point positive, stale page at owner expiry, no horizontal overflow, source/event identity readback from deployed `/vnext/`.
- Next migration slice: compare complete NOW/PATH/WHY/PROOF inventory vs original production; extract only tested premium modules from Draft #1576 and improve any missing editorial/score details. Cutover needs a separate owner-governed PR with visual and rollback acceptance; never replace the homepage from this candidate PR.

Source owner: current `main` and SITE issue #1578. Keep Draft #1576 isolated.
