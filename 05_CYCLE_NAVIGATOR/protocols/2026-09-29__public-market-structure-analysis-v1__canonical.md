# Cycle Navigator Public Market Structure Analysis v1

Status: ACTIVE
Effective: CN #27 / 2026-W40
Authority: PUBLIC_ANALYSIS_ONLY_NO_PRECISION_SCORE_NO_PORTFOLIO_EXECUTION

## Public architecture

Cycle Navigator has three separate public layers:

1. **PRICE RANGES** — unchanged prospective BTC/ETH range forecasts and the only public precision-score family.
2. **MARKET STRUCTURE** — qualitative CN-edge analysis for the completed week and coming week. No percentage, HIT/MISS score or synthetic accuracy number.
3. **BULL / BEAR BASELINE** — prospectively archived weekly evidence-balance context. The public site's live Market Weather is owned by Official Compass under `MARKET_WEATHER_SOURCE_OF_TRUTH_v1`, not by the CN scorecard.

Never blend these layers into one score.

## Market Structure — fixed analytical questions

Use the same five headings every week, in the same order:

1. **REGIME & RESILIENCE** — phase and whether structure survives volatility/retests.
2. **LEADERSHIP** — quality and persistence of relative leadership.
3. **ROTATION / TRANSMISSION** — whether capital hands off into subsequent market-cap cohorts.
4. **BREADTH & PERSISTENCE** — whether participation is broad and durable.
5. **FLOW QUALITY / FRAGILITY** — whether price action is internally supported or fragile, synthesizing canonical spot/microstructure, flow/ETF, breadth, sentiment, relative-strength and counterevidence where available.

For **WEEK GONE**, summarize what actually developed versus the prior thesis.
For **WEEK AHEAD**, state what CN currently expects / watches in the same five headings.

These are analytical conclusions, not scoreable public predictions. Internal learning may audit them, but no public Market Structure percentage is produced.

## Bull / Bear baseline and live Market Weather

Canonical ownership is defined by:
`05_CYCLE_NAVIGATOR/protocols/2026-09-29__market-weather-source-of-truth-v1__canonical.md`.

Cycle Navigator may archive the weekly baseline for:
- **1-3 DAYS**
- **5-7 DAYS**
- **2-3 WEEKS** when a governed structured horizon exists.

The weekly baseline is not an accuracy score and is not the site's live owner.

**Official Compass** owns the current/live Market Weather display. The site reads that payload verbatim and never infers Bull/Bear from price, prose, CN fields, or protection state.

If a governed horizon is missing, display **UNAVAILABLE** rather than inventing 5/5.

The public 0-10 display is a coarse categorical encoding of governed Compass direction:
- UP -> Bull 7 / Bear 3
- DOWN -> Bull 3 / Bear 7
- MIXED or SIDEWAYS -> Bull 5 / Bear 5
- NO_EDGE or UNAVAILABLE -> no numeric value

Protection / re-entry is a separate lane and must not be added as a hidden Bull/Bear overlay.

## Accountability

- Price-range forecasts remain prospectively frozen and scored exactly as before.
- Bull/Bear readings are prospectively archived for learning and later calibration, but no public accuracy score is implied unless a separate prospective scoring contract is approved.
- Historical Market Structure scores may remain in immutable archives as legacy records, but they are not shown as the current public precision methodology.
