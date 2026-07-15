# OTA Pings #14–#15 — Main Framework Review

**Evaluation date:** 2026-07-15  
**Research layer:** Claude/Fable OTA shadow  
**Framework authority:** MAIN_FRAMEWORK / CHATGPT  
**Status:** `SHADOW_ACCEPTED_WITH_CORRECTIONS`  
**Canonical state change:** `NONE`  
**Portfolio authority:** `NONE`

## Canonical verdict

```text
OTA_14_STATUS: USEFUL_HOLDOUT_UPDATE / NOT_CANONICAL_CLOSE_CONFIRMATION
OTA_15_STATUS: GOVERNANCE_FORMAT_MIGRATION_ACCEPTED
NUMERIC_OTA_SCORES: RETIRED
OUTCOME_SCHEMA: FROZEN_SIX_CLASS_EVALUATION_ONLY
TYPE2_STATUS: STRONGEST_CANDIDATE_SO_FAR / NOT_CONFIRMED
FLOW_NECESSITY_P3: WATCH_ONLY / NOT_ACTIVE_VERDICT
REDUNDANCY_COUNTER: 0_OF_5_MATURED_EVENTS
FRAMEWORK_STATE_CHANGE: NONE
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
PORTFOLIO_ACTION: NONE
```

## What OTA #14 contributes

OTA #14 correctly identifies a highly informative split: price and relative structure appeared to confirm while ETF flow continued to contradict the move. This is useful for the frozen July-14 holdout because it separates three possible future outcomes:

1. flow contradiction eventually causes a full retrace;
2. the move survives despite flow contradiction, falsifying flow necessity;
3. the apparent close confirmation fails once truth-layer settlement is checked.

The useful research question has therefore shifted from whether structure can precede price to whether ETF-flow confirmation is necessary for durability.

## Required corrections to OTA #14

### Close claims are not yet canonical

The stated BTC close near 64,988 and derived ETH/BTC close near 0.02909 came from FMP-derived cross-check data. The latest accepted DATA PING truth layer at the time still had the CEST daily candle partial. Therefore:

```text
BTC_COMPLETED_CEST_CLOSE_ABOVE_63300: PENDING_TRUTH_LAYER
ETHBTC_COMPLETED_CEST_CLOSE_ABOVE_0285: PENDING_TRUTH_LAYER
```

These may be treated as external shadow indications, not as canonical completed-close facts, until a later accepted DATA PING supplies the settled CEST ledger.

### The frozen flow leg is unresolved, not fully failed

The 13 July BTC ETF settlement of -424.7M confirms one contradictory completed session. The 14 July settlement remained pending. Under the frozen SCTA holdout:

```text
P1_FLOW_CONDITION: NOT_MET_YET
P2_TWO_SESSION_NEGATIVE_CONDITION: NOT_RESOLVED
P3_FLOW_NECESSITY_FALSIFIER: WATCH_ONLY
```

It is therefore too early to state that the two-session flow leg has fully failed or that P2 is formally active. The correct label is `FLOW_CONTRADICTION_CONTINUES / SECOND_SESSION_PENDING`.

### “Two consecutive closes above 64K” is not an active canonical gate

The active runtime registry contains BTC gates at 63.3K, 61.9K and 59.4K, plus ETH/BTC gates at 0.0275 and 0.0300. A two-close-above-64K permission pattern is not currently present in the canonical gate registry and must not be promoted through OTA language without a readable prior canonical receipt.

## What OTA #15 gets right

OTA #15 implements the framework feedback well:

- numerical Transition/Confirmation/Delta scores are retired;
- the six-class outcome schema is frozen for prospective evaluation;
- `correlationally strong` is downgraded to `suggestive within a curated historical sample`;
- the A04 classification error is explicitly owned;
- future decision-value claims require pre-event receipts, frozen gate states and counterfactual costs;
- OTA is restricted to hypothesis generation, adversarial audit, failure atlas, prospective case cards and gate-improvement testing;
- the ping acknowledges zero current decision delta versus canonical gates.

This is a material governance improvement. The former numeric OTA series should remain closed at n=14 and must not be resumed under another name without a separate governance decision.

## Required correction to OTA #15

### The redundancy counter has not reached 1/5

The redundancy kill criterion concerns five **mature catalyst events**, not five OTA outputs and not five snapshots from the same event. The July-14 holdout has not yet matured at the 12-session horizon. Therefore:

```text
REDUNDANCY_EVENTS_COMPLETED: 0/5
CURRENT_HOLDOUT: CANDIDATE_EVENT_1_AWAITING_MATURITY
```

Only after the mature outcome is known can the framework determine whether OTA produced a decision different from the existing close-basis and persistence gates.

### OTA #15 is a governance patch, not a new market observation

Because #15 re-scores the same state roughly 30 minutes after #14 and adds no material market evidence, it should be stored as:

```text
FORMAT_MIGRATION / GOVERNANCE_PATCH / NO_NEW_MARKET_EVENT
```

It should not count toward event frequency, prospective sample size, decision-value statistics or the redundancy counter.

## Frozen holdout state after review

```text
HOLDOUT_ID: SCTA_20260714
CLASSIFICATION: S2 / BORDERLINE_S3_INTRADAY_UNCONFIRMED
P1: OPEN
P2: WATCH — ONE NEGATIVE ETF SESSION CONFIRMED, SECOND SESSION PENDING
P3: WATCH ONLY
24H_RESULT: NOT_CANONICALLY_SCORED_YET
72H_RESULT: PENDING
7D_RESULT: PENDING
12_SESSION_RESULT: PENDING
FOMC_20260728_29: LOGGED_POTENTIAL_CONFOUND
```

The holdout must be judged only using the frozen six-class outcome set and the pre-registered P1/P2/P3 conditions. No condition may be rewritten after observing later outcomes.

## Operational decision

- Preserve OTA #14 as a useful research update with truth-layer caveats.
- Preserve OTA #15 as the governance transition to OTA v0.4.
- Do not create a new canonical market event.
- Do not alter the active edge event, gates, rebuy lock, rotation status or CN #16.
- Do not produce additional OTA temperature pings from the same unchanged state.
- Next substantive OTA output should be tied to a verified truth-layer close, completed ETF settlement or a frozen maturity mark.
- Evaluate redundancy only after mature catalyst outcomes, not per ping.

## Current canonical framework state

```text
ACTIVE_EVENT: ROTATION_REPAIR_EDGE_20260712_01
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: STRENGTHENED_INTRADAY_ONLY
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

The latest canonical state remains controlled by the latest accepted DATA PING. OTA may not substitute external closes, ETF values or derived ratios for the truth layer.