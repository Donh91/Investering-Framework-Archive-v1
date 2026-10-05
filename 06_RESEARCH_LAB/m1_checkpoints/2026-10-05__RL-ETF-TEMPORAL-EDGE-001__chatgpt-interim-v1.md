# M1 ChatGPT Interim Checkpoint v1

**Mission:** `RL-ETF-TEMPORAL-EDGE-001`  
**Date:** 2026-10-05  
**Author:** ChatGPT 5.6 Sol High  
**Status:** INTERIM / NOT_FINAL_ADJUDICATION  
**Authority:** RESEARCH_ONLY / NO_CANONICAL_EFFECT  
**Fresh-main observed while investigating:** `96db107da92537841462a68c39ddb613fc11001e`

## Frozen research question

Is ETF-flow persistence still one of the framework's strongest documented decision edges when historical decisions are replayed using only ETF information actually knowable at each decision timestamp?

## Verified interim findings

### F1 - Official PIT semantics are stricter than current live settled semantics

The ratified #1211 knowledge-time owner decision requires the first accepted observation to have no non-structural unknown fund cells, plus total parity and verification semantics.

Current `scripts/data_ping/auto_market_state.py` accepts `DAILY_SETTLED_ETF_CALIBRATION_v2` when BTC and ETH rows have:
- `session_final == true`
- `total_parity == true`
- a numeric `reported_total`

It does not require `unknown_fund_cell_count == 0`.

The resulting classification is `ETF_SETTLED_FINAL_PARITY`.

### F2 - The current daily settled capture can be live-valid while PIT-ineligible

The stored 2026-10-02 calibration capture contains:
- BTC reported total 31.7m with 1 unknown fund cell, IBIT
- ETH reported total -17.3m with 2 unknown fund cells, ETHA and ETHB
- both rows marked `session_final=true`
- both rows pass total parity
- unknown cells are not imputed

That row can pass current live `auto_market_state` normalization, but it would not satisfy the strict #1211 first-complete knowledge-time rule.

### F3 - Correct PIT replay code exists

`backtest_engine/etf_pit_replay.py` implements the #1211-style replay contract around `ETF_OBSERVATION_v1`, including observed knowledge time and cumulative-max knowledge time for trailing features.

### F4 - Clear production adoption of ETF_OBSERVATION_v1 was not found

Repository search located:
- schema
- owner decision
- PIT replay implementation
- tests / experiment fixtures

It did not locate a normal production producer emitting `ETF_OBSERVATION_v1` from the daily settled ETF capture path.

This is an interim provenance finding, not proof that no indirect mapping exists. Claude folder/consumer audits are tasked to challenge it.

### F5 - Historical A1/A2 evidence remains role-limited and single-regime

The Sensor Survival material retains:
- A1 ETF 5-session net below -500m as `URGENCY_ONLY`
- A2 outflow streak >=3 as `URGENCY_ONLY`

A1 remains one-cycle evidence. A2 was explicitly marked for additional forward rows, not execution authority.

### F6 - Current prospective validation has not supplied the missing proof

Current relationship compression shows relevant legacy pairs with:
- `WAITING_FOR_MAPPING`
- `matured_outcome_count = 0`
- no current prospective validation

This applies to ETF-flow + price absorption and A1/A2 urgency + C1/C2 lean warning representations found in the current research registry.

## Interim claim classification

**ETF defensive edge:** `WEAKENED / INSUFFICIENT_EVIDENCE`

Not rejected.

The historical defensive hypothesis remains plausible, but the stronger claim that ETF flow is among the framework's strongest documented decision edges is not yet cleanly supported under:
1. strict point-in-time knowledge;
2. revision-aware source vintages;
3. prospective validation;
4. measurable decision divergence.

## Highest-value falsification target for GPT-6.1 Sol

Attempt to prove that the apparent A1/A2 defensive value is:
- materially reduced by knowledge-time delay;
- explained by price/breadth/rotation information already available;
- dependent on one stress regime;
- or not reproducible after revision-aware admissibility.

Conversely, if the edge survives, quantify what remains unique after those controls.

## Open unknowns

1. Whether a production mapping from daily ETF capture to `ETF_OBSERVATION_v1` exists under a non-obvious owner path.
2. The count and exact timing of post-capture A1/A2 fires using only first-complete eligible vintages.
3. Decision divergence versus price/breadth/rotation controls.
4. False-positive and false-negative cost under corrected timing.
5. Whether current live-state ETF semantics should be repaired, or intentionally remain a distinct live-only notion of settled total.

## Boundaries

No market-rule change.
No threshold or weight change.
No portfolio action.
No canonical promotion.
No code repair is authorized by this checkpoint.
