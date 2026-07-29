# OPERATIONAL TRANSLATION LAYER v1.0

Status: APPROVED OPERATIONAL FORMAT RULE
Effective: 2026-07-29
Scope: Master Monday and all RAW horizons

## Purpose

Preserve the complete analytical output while adding a separate, concrete and easy-to-understand translation into expected price behavior and action.

This is an output-layer improvement only.
It does not alter the framework architecture, signal hierarchy, regime engine, forecast methodology or governance.

## Required two-layer output

Every Master Monday and relevant RAW forecast must contain:

1. ANALYTICAL LAYER
   - full framework reasoning
   - signal state
   - regime interpretation
   - drivers, conflicts and uncertainty
   - alternative scenarios

2. OPERATIONAL TRANSLATION
   - one primary price path
   - one clear invalidation
   - concrete price ranges or levels
   - expected sequence and timing
   - explicit action
   - confidence and main risk

The two layers must remain separately auditable.

## Mandatory Operational Translation schema

```text
OPERATIONAL TRANSLATION

HORIZON:
1–3d / 5–7d / 2–3w / Weekly

PRIMARY PRICE PATH:
A short sequence using concrete levels or ranges.
Example:
64.5K rejection → 61K–62K retest → stabilization attempt.

EXPECTED RANGE:
BTC: lower–upper
ETH: lower–upper, when applicable

MOST LIKELY ACTION:
HOLD / WAIT / PREPARE / TRIM / REDUCE / REBUY LADDER / PROTECT

ACTION DETAIL:
What to do now, what not to do, and what changes the action.

INVALIDATION:
The observable price close, flow change or structural event that invalidates the primary path.

ALTERNATIVE PATH:
One concise alternative, not a long scenario tree.

CONFIDENCE:
Low / Moderate / High

MAIN RISK:
The single most important reason the translation could be wrong.
```

## Scoring and ledger rule

The Operational Translation receives its own frozen ID linked to the parent forecast.

Suggested IDs:
- MM-OT-YYYY-WW
- RAW13-OT-YYYYMMDD-##
- RAW57-OT-YYYYMMDD-##
- RAW23W-OT-YYYYMMDD-##

The analytical forecast and operational translation must be evaluated separately.

Track:
- direction accuracy
- range placement
- sequence accuracy
- timing accuracy
- action usefulness
- invalidation quality
- divergence from parent analysis

## Divergence audit

At outcome evaluation, classify:

- ANALYSIS_RIGHT_TRANSLATION_RIGHT
- ANALYSIS_RIGHT_TRANSLATION_WRONG
- ANALYSIS_WRONG_TRANSLATION_RIGHT
- ANALYSIS_WRONG_TRANSLATION_WRONG
- TRANSLATION_TOO_VAGUE_TO_SCORE

Purpose:
Identify whether errors arise in the market analysis or in compression from analysis into a usable action and price path.

## Guardrails

- The translation must not invent conviction absent from the analysis.
- It may compress uncertainty, but must preserve it through confidence and invalidation.
- It must select one primary path even when the analytical layer contains several possibilities.
- It must not hide behind broad ranges.
- It must not change the analytical layer retrospectively.
- It must remain simple enough to understand without reading the full analysis.

## Success criterion

The layer succeeds only if it improves action clarity and scorer reliability without degrading analytical integrity.
