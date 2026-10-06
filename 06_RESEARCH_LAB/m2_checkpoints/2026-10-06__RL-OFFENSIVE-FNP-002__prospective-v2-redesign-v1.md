# M2 Offensive Edge v2 - prospective permission-divergence redesign

Date: 2026-10-06
Status: DESIGN_FROZEN / IMPLEMENTATION_NOT_ACTIVATED
Authority: RESEARCH_ONLY / ZERO_MARKET_OR_PORTFOLIO_AUTHORITY

## Why T2 v1 must not be reactivated
Fresh provenance review establishes that GATE-BTC-PARTIAL-v0.1.1 was superseded and that a final frozen v0.2 permission rule is not recoverable. The recovered v0.1.1 structure is historical-only and several conjuncts lack operational definitions. Therefore current T2 may not synthesize ENTERED rows, substitute v0.1.1 for v0.2, or use the legacy gate as a live/prospective challenger.

The existing T2/T5 observer remains useful as historical instrumentation, but ZERO_ROWS is not evidence of zero divergence.

## Current official owner available
The current official daily Compass exposes a typed Main-Framework action permission:
- packet contract OFFICIAL_DAILY_COMPASS_v1;
- action_now from native_action_contract.NOW;
- horizon and capitalization actions are capped by that Main-Framework permission;
- Compass has no portfolio execution authority.

This can serve as the benchmark observation owner. It must not itself invent the challenger.

## Correct replacement question
When the current official Compass withholds proactive permission, would a separately preregistered research-only earlier-permission challenger have produced superior opportunity-cost-adjusted outcomes under identical information, clock and costs?

## Required architecture
OFFICIAL_COMPASS_BENCHMARK
 -> immutable benchmark snapshot
 -> separately frozen research challenger
 -> explicit same-time divergence
 -> immutable source row
 -> 24h / 72h / 7d maturation
 -> MAE / MFE / terminal return
 -> common-cost counterfactual
 -> missed-upside vs drawdown-added economics
 -> episode/dependence-aware adjudication

## Challenger admission gate
No challenger is activated by this design.

A challenger must first freeze:
1. theory and causal rationale;
2. exact source owners and knowledge-time;
3. exact eligible states;
4. exact action difference versus benchmark;
5. position fraction;
6. transaction/slippage model;
7. horizons;
8. falsifier and kill condition;
9. episode clustering/dependence treatment;
10. no-threshold-search declaration.

It may reuse existing Research Genome primitives and M6 event-outcome machinery where semantically compatible.

## Strong anti-self-test rule
The research layer may not infer an earlier permission merely because price rose later, Compass was bullish but action remained WAIT, CN expected UP, threshold proximity looked attractive, a retired observer activated, or a historical gate would have entered under reconstructed rules.

Divergence must be emitted by a preregistered challenger evaluated from information legally available at T0.

## Recommended challenger family
First candidate should be deliberately simple, not an AI policy:
OFFICIAL_PERMISSION_MINUS_ONE_CONFIRMATION_STEP_v1

Meaning: test whether one explicitly defined confirmation dependency can be relaxed while every other benchmark condition, source clock and health requirement stays identical.

This candidate is NOT YET SPECIFIED OR ACTIVE. The exact dependency must be chosen from current owner semantics before outcomes are inspected. If current Compass action is not decomposable into an auditable confirmation dependency, kill this candidate rather than approximate it.

This implements the existing Ocellus primitive:
same opportunity set + same clock + same costs + one changed rule + sole-blocker attribution.

## Legacy T2 status
GATE_BTC_PARTIAL_FT_1:
- historical identity retained;
- prospective owner binding: BLOCKED;
- v0.1.1 live reuse: FORBIDDEN;
- v0.2 synthesis: FORBIDDEN;
- current zero-row evidence: MEASUREMENT_GAP, not economic conclusion.

## Next implementation gate
Inspect the current native action owner for an auditable decomposition of confirmation/blocker dependencies.

If exactly one current dependency can be frozen without inventing semantics:
- preregister one challenger only;
- create a benchmark/challenger adapter;
- wire it to prospective receipt production;
- reuse T5 economics only after schema compatibility is proven.

If no such dependency exists:
- do not create a challenger;
- prioritize M6 prospective warning/action economics, which already has a clean typed warning owner.

No live Compass, threshold, market state or portfolio action changes from this document.
