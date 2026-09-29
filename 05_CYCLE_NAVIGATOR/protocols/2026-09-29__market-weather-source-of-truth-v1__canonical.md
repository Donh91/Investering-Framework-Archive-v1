# Market Weather Source of Truth v1

Status: **ACTIVE**
Effective: 2026-09-29
Contract: `MARKET_WEATHER_SOURCE_OF_TRUTH_v1`

## Purpose

Prevent Cycle Navigator, Official Compass and the public site from becoming competing short-horizon signal owners.

Market Weather is a compact public visualization of already-governed Compass direction. It is not a new market model, probability estimate, price forecast, precision score or portfolio-execution layer.

## Semantic ownership matrix

| Semantic role | Sole owner | Consumer / rule |
|---|---|---|
| Settled weekly evidence synthesis | Master Monday | Input to weekly CN; never a live site signal owner |
| Weekly frozen market thesis | Cycle Navigator | Immutable weekly baseline |
| Weekly Market Structure analysis | Cycle Navigator | Qualitative only from CN #27; no new public percentage |
| Price Range precision | Cycle Navigator public scorecard | Scored exactly under existing Price Range contract |
| Weekly Bull/Bear baseline | Cycle Navigator | Archived context; never silently substituted for live |
| Current 1–3d direction | Official Compass | Site renders only from current Compass |
| Current 5–7d direction | Official Compass | Site renders only from current Compass |
| Current 2–3w direction | Official Compass, sourced from governed structured CN horizon | UNAVAILABLE until structured input exists |
| Pullback / distribution / re-entry | Official Compass Protection tracker | Separate lane; never hidden inside Bull/Bear |
| Market Weather presentation | Public site | Read-only renderer; no synthesis |
| Historical proof | Immutable CN public series / archived scorecards | Historical Market Structure scores remain unchanged |

## One-way dataflow

`settled evidence -> Master Monday -> weekly CN -> Official Compass -> public site`

Live owner evidence may update Official Compass after the weekly CN freeze. It may change the current display without rewriting the weekly baseline.

No path may flow from the site back into CN, Compass, Master Monday or canonical market state.

## Conflict behavior

A weekly CN baseline and the current Compass may legitimately disagree.

The site must treat that as **baseline versus current update**, never as:
- an error,
- a reason to average the two,
- permission to overwrite the weekly freeze,
- permission to manufacture a third signal.

If current Compass is stale or unavailable, live Market Weather is unavailable. CN does not become an automatic fallback.

If the CN weekly baseline is absent, Compass does not fabricate historical baseline evidence.

## Display encoding

Contract: `OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1`
Semantics: `EVIDENCE_BALANCE_NOT_PROBABILITY`
Resolution: `COARSE_CATEGORICAL_DIRECTION`

The display intentionally adds no market semantics:

- governed `UP` -> Bull 7 / Bear 3
- governed `DOWN` -> Bull 3 / Bear 7
- governed `MIXED` or `SIDEWAYS` -> Bull 5 / Bear 5
- governed `NO_EDGE` or `UNAVAILABLE` -> no number

Protection / re-entry is displayed separately. It must not shift the Bull/Bear number as an extra hidden vote.

A future richer strength scale requires an upstream governed Compass field and a separate prospective contract. The browser may never create it.

## Horizon rules

- **1–3d:** Official Compass current short-horizon owner.
- **5–7d:** Official Compass current weekly-window owner.
- **2–3w:** Official Compass may publish only when a structured governed CN decision horizon exists. Historical prose must not be parsed retrospectively into a number.

## Migration

- Existing schema-v3 Compass artifacts are immutable and are not rewritten.
- A site reading an older projection with no Market Weather payload shows unavailable/awaiting state.
- First eligible schema-v4 Compass creates the live Market Weather payload.
- Historical CN #1–26 Market Structure scores remain unchanged.
- CN #27 onward has Market Structure analysis only; Price Range scoring continues unchanged.

## Authority

- portfolio_execution: false
- new_market_classifier: false
- probability_model: false
- site_synthesis_allowed: false
- forecast_rewrite: false
