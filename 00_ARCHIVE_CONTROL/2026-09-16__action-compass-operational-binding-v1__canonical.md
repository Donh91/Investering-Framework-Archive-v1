# Action Compass Operational Binding v1

**Date:** 2026-09-16  
**Status:** CANONICAL_CURRENT_OPERATIONAL_BINDING  
**Scope:** current short-horizon navigation, daily decision freezes, Compass outcome scoring, Cycle Navigator/site tactical-context handoff.

## Binding decision

The framework's existing `Three-Horizon Action Compass` / Handlekompas action-posture concept is formalized as the first-class `05_COMPASS/` operational derivative.

This does **not** create a parallel market-state engine and does not supersede the Autonomous Data Authority Transition. It gives the existing Compass function a stable machine interface, daily prospective freeze and outcome-accountability chain.

Current route:

```text
current autonomous machine evidence + eligible live observations
-> deterministic Action Compass compilation
-> immutable daily tactical freeze
-> LATEST_COMPASS.json pointer
-> user-facing Compass and optional CN/site current-context surface
-> separate H12 / H72 / H168 outcome records
-> later learning / calibration
```

## Authority ceiling

Compass authority is:

```text
NAVIGATION_ONLY
NO_PORTFOLIO_EXECUTION_AUTHORITY
NO_MASTER_MONDAY_REWRITE
NO_CYCLE_NAVIGATOR_FREEZE_REWRITE
NO_MODEL_WEIGHT_AUTHORITY
NO_THRESHOLD_AUTHORITY
```

A Compass action label is a current navigation posture, not permission for an autonomous order.

## Canonical pointer

Agents, presentation layers and research jobs asking for current Compass state must resolve:

`05_COMPASS/LATEST_COMPASS.json`

and then the exact immutable freeze named by that pointer.

Do not infer current Compass state from chat history, a historical DATA PING Compass receipt, an old Handlekompas message, or the newest filename by guesswork.

## Cadence and immutability

One scheduled `DAILY_COMPASS_FREEZE` is produced per UTC date. Optional event freezes may be produced when a separately governed regime-change trigger is explicitly invoked.

Daily freezes are immutable. Only the pointer may advance. Outcomes are written to separate append-only artifacts after horizon maturity.

## Required horizons

Every daily Compass must expose:

- `NOW`;
- `H12` — next 12 hours;
- `D1_3` — next 1–3 days;
- `D5_7` — next 5–7 days.

Each horizon must carry direction, action posture, confidence, explanation, confirmation trigger and invalidation. Direction vocabulary is `BULLISH | NEUTRAL | BEARISH`.

## Required capitalization ladder

Every daily Compass must expose:

`BTC -> ETH -> LARGE_CAP -> MID_CAP -> SMALL_CAP -> MICRO_CAP`

Each rung must carry status, ETA, rationale, trigger and invalidation. This ladder is the preferred compact current altcoin/rotation status surface.

## Evidence contract

Every freeze preserves the evidence available at issuance time. The system targets at least 100 legitimate scalar observations across eligible current sources, but must never pad or invent observations to reach that number.

The freeze records point count, source-family coverage, missing sources and a reproducibility hash. Missing data is evidence of degraded coverage and stays explicit.

## Relationship to Cycle Navigator

Cycle Navigator remains the weekly strategic/public forecast-accountability layer. Compass is the daily tactical/navigation layer.

The two may disagree. Such disagreement must be preserved as `cn_alignment` and is itself eligible learning data.

The CN public site may consume a sanitized Compass subset as a distinct current/tactical surface. Compass must not replace or mutate the weekly CN forecast freeze, weekly scorecard, ranges or historical claims.

## Scoring contract

Matured Compass calls are scored prospectively at H12, H72 and H168 using timestamp-resolved historical market observations. The original freeze is never modified after outcome realization.

The initial v1 market-direction score uses a simple BTC/ETH return proxy and preserves ETH/BTC separately. Segment-specific ladder scoring remains unavailable unless eligible segment-level outcome data exists; BTC/ETH must not be used to fabricate small/microcap accuracy.

## Runtime economics

Routine Compass generation is deterministic and must not require an LLM or consume OpenAI/Astra/Codex budget. High-capability models may audit, challenge or research the accumulated Compass history separately, but are not a daily production dependency.

## Invariant

```text
CURRENT COMPASS = LATEST_COMPASS POINTER -> EXACT IMMUTABLE FREEZE.
FREEZE FIRST, SCORE LATER.
MISSING DATA STAYS MISSING.
TACTICAL CONTEXT MAY INFORM CN PRESENTATION; IT MAY NOT REWRITE CN HISTORY.
COMPASS HAS ZERO AUTONOMOUS ORDER AUTHORITY.
```
