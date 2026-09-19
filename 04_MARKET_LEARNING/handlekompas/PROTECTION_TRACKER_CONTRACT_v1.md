# Compass Protection & Re-entry Tracker v1

**Status:** ACTIVE WHEN MERGED TO MAIN  
**Owner:** Official Compass / Cycle Navigator authority chain  
**Public surface:** Cycle Navigator NOW  
**Private consumer:** Portfolio Compass may consume the same canonical state, but wallet data never enters the public projection.

## Purpose

Expose one shared, privacy-safe market protection state for the public Compass and private Portfolio Compass consumers without creating a parallel pullback forecast engine.

The public tracker answers only:

- is material pullback / distribution risk currently quiet, building, elevated, high or confirmed?
- is canonical distribution evidence absent, warning or confirmed?
- is there a supported ETA window, otherwise UNKNOWN?
- is re-entry inactive, waiting for the flush, waiting for reclaim, or ready for review?

It does **not** publish wallet holdings, position actions, private evidence values or automatic execution instructions.

## Authority

The tracker is a bounded translation of already-canonical Official Compass and frozen/current Cycle Navigator state.

It must not treat the research-only pullback-learning lane as canonical authority. At v1, `04_MARKET_LEARNING/pullback_learning/` remains descriptive/research-only and its current eligibility suspension cannot be bypassed by this tracker.

Storm/Tsunami or similar dramatic classes are not manufactured. They remain UNKNOWN unless a future canonical owner explicitly publishes a reproducible class.

## Public contract

`COMPASS_PROTECTION_TRACKER_v1`

Required fields:

- `pullback_risk_state`: NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED / UNAVAILABLE
- `pullback_class`: bounded canonical translation or UNKNOWN
- `distribution_risk`: NONE / WARNING / CONFIRMED / UNKNOWN
- `eta_window`: explicit supported window or UNKNOWN
- `confidence_quality`: LOW / MEDIUM / HIGH, meaning evidence quality, never probability
- `decisive_public_drivers`: short privacy-safe evidence-family explanations
- `invalidation`
- `last_material_change_at`
- `data_quality`
- `reentry_state`: INACTIVE / WAIT_FOR_FLUSH / WAIT_FOR_RECLAIM / REVIEW / UNAVAILABLE
- `reentry_message`
- authority flags with `portfolio_execution=false`, `wallet_specific=false`, `new_market_classifier=false`

## Escalation semantics

- NORMAL stays visually quiet.
- BUILDING/ELEVATED is a watch state, not a sell command.
- HIGH/CONFIRMED is prominent and may trigger a fresh Compass reassessment immediately.
- Distribution/exit escalation is protective and bypasses the normal non-protective event-refresh cooldown.
- ETA stays UNKNOWN unless an existing canonical structured owner explicitly provides a bounded pullback/distribution ETA.

## Re-entry semantics

Re-entry is prospective and sequential:

1. HIGH/CONFIRMED risk -> WAIT_FOR_FLUSH.
2. Risk de-escalates after a material warning -> WAIT_FOR_RECLAIM.
3. REVIEW opens only after the existing Compass confirmation gate is constructive again while risk is no longer elevated.
4. REVIEW means reviewable re-entry conditions, never automatic BUY or portfolio execution.

Stabilization alone is not recovery. Recovery alone is not rotation.

## Event-driven refresh

The existing Compass Event Refresh owner compares the candidate protection/re-entry state with the last Official Compass.

A material protection-state transition or opening of REENTRY REVIEW can request an `EVENT_DRIVEN` Official Compass between the fixed 08:17 and 20:17 Copenhagen freezes.

Normal market noise and unchanged states remain silent. The site never synthesizes a new risk state from live prices by itself.

## Privacy

The public projection must contain zero:

- wallet addresses,
- holdings,
- position values,
- position-specific trim/sell/rebuy instructions,
- private source bindings,
- private evidence snapshots.

Portfolio Compass may separately translate the same canonical state into private wallet-aware review actions.
