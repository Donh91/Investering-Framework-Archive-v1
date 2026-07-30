# OPERATIONAL TRANSLATION LAYER v1.0

**Status:** Canonical operational rule  
**Effective:** 2026-07-29  
**Expanded scope effective:** 2026-07-30  
**Scope:** Master Monday, RAW 1–3D, RAW 5–7D, RAW 2–3W, DATA PING and other framework outputs that contain a market forecast or action implication.

## Purpose

Preserve the full framework analysis while adding a separate, simple and scorerable translation into price and action.

The framework must continue to show its complete reasoning, uncertainty, signal conflicts and alternative scenarios. It must then produce a distinct operational layer that answers:

- What is the primary expected price path?
- What price range is expected?
- What should be done now?
- What should not be done?
- What invalidates the primary path?
- What is the most important alternative path?

This layer does not replace or simplify the underlying architecture. It compresses the architecture into a concrete output that can be acted on and audited separately.

## Locked two-layer structure

### Layer A - Full Analysis

Must preserve:

- market state and regime
- liquidity and flow interpretation
- BTC dominance, ETH/BTC and breadth
- derivatives and positioning
- macro context
- signal convergence and conflict
- confidence and data-quality limits
- alternative scenarios
- framework reasoning

### Layer B - Operational Translation

Must be written in simple language and contain:

1. **Horizon**
2. **Primary price sequence**
3. **Expected BTC range**
4. **Expected ETH range**, when relevant
5. **Action now**
6. **Do not do**
7. **Invalidation**
8. **One alternative path**
9. **Confidence**
10. **Main failure risk**

## Standard format for Master Monday and RAW

```text
OPERATIONAL TRANSLATION

Horizon:
[1–3D / 5–7D / 2–3W]

Primary price path:
[One explicit, ordered sequence]

Expected BTC range:
[Low–high]

Expected ETH range:
[Low–high or NOT SCORED]

Action now:
[HOLD / WAIT / PREPARE / PARTIAL REDUCE / REDUCE / REBUY TIER 1 / REBUY TIER 2 / PROTECT]

Do not:
[One concrete prohibited action]

Invalidation:
[Measurable price, close, flow or transmission condition]

Alternative path:
[One concise alternative]

Confidence:
[Low / Moderate / High]

Main failure risk:
[Single most important reason the translation may fail]
```

## Compressed terminal format for DATA PING

DATA PING uses a deliberately shorter operational translation because its main purpose is frequent market-state updating rather than a full forecast report.

Every user-facing DATA PING reconciliation must end with exactly one adaptive and unambiguous sentence beginning:

```text
**Top-up og købsvindue:**
```

The sentence must state:

1. a definite action now;
2. a time horizon or measurable trigger for reassessment;
3. the decisive reason.

The canonical detailed rule is:

`governance/DATA_PING_TOP_UP_BUY_WINDOW_OUTPUT_RULE_v1_0.md`

This compressed line supplements rather than replaces the full DATA PING framework read. It may not override canonical state, portfolio locks, source-QA boundaries or predecessor-lineage restrictions.

## Scoring and audit

The analysis and operational translation must receive separate IDs when the output is a scored forecast.

Recommended identifiers:

```text
ANALYSIS_ID: MM-YYYY-WW-A
TRANSLATION_ID: MM-YYYY-WW-T
```

or for RAW:

```text
ANALYSIS_ID: RAW-YYYYMMDD-HORIZON-A
TRANSLATION_ID: RAW-YYYYMMDD-HORIZON-T
```

For DATA PING, the exact published terminal sentence should be archived with the framework read whenever practical and may later be evaluated as an operational timing call.

The translation is evaluated independently on:

- direction
- range placement
- depth
- timing
- path sequence
- invalidation quality
- action quality

The audit must distinguish between:

1. Analysis correct, translation correct
2. Analysis correct, translation wrong
3. Analysis wrong, action still protective
4. Analysis wrong, translation wrong
5. Translation too vague to score

## Governance

- The operational translation may not modify the full analysis retroactively.
- The original translation must remain frozen after publication.
- Only outcomes, scores and audit comments may be appended.
- The translation may not create false certainty. One primary path is mandatory, but confidence and invalidation must remain explicit where the long format applies.
- A broad range used only to obtain an easy hit must be penalized.
- The DATA PING terminal line must be concise without becoming ambiguous.
- This layer is an execution-compression and accountability layer, not a new market engine.

## Canonical learning

The identified framework weakness was not missing defensive understanding. It was insufficient compression of that understanding into one concrete, scorerable primary sequence.

This rule is intended to improve action clarity without changing the framework architecture.
