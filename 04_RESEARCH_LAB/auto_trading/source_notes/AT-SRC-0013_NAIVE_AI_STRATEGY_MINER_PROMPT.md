# AT-SRC-0013 — Naive AI Strategy Miner Prompt

Date captured: 2026-10-08
Status: SCREENED / BASELINE_FIXTURE
Source type: User-supplied screenshot of an X/shared prompt
Exact source URL: UNKNOWN
Evidence class: METHOD INSPIRATION / NEGATIVE-AND-CHALLENGER BASELINE
Authority: RESEARCH ONLY / NO EXECUTION

## Source summary

The supplied prompt instructs an AI coding/research agent to:

1. collect strategies from several public/free strategy sources;
2. convert each strategy into a testable specification;
3. build a backtest engine;
4. include fees and slippage;
5. rank strategies against buy-and-hold;
6. explain why winners work and when they should fail;
7. suggest five variants of each shortlisted strategy;
8. independently re-check selected winners;
9. move from paper to small size only after validation.

The prompt contains several good operational instincts, but the central procedure:

`collect many -> backtest all -> rank winners -> generate variants`

is also a clean example of a high-throughput strategy-selection process that can manufacture false alpha through multiplicity and adaptive reuse of the same evidence.

## Retain

Useful baseline features:
- one explicit spec per strategy;
- source provenance;
- exact asset/timeframe;
- entry/exit/stop/position assumptions;
- fees and slippage in every run;
- comparison against buy-and-hold;
- explicit losing-strategy reporting;
- explanation of market conditions and failure modes;
- paper-first language;
- no invented results.

These are necessary, but not sufficient, for trustworthy research.

## Missing scientific controls

The source does not make the following load-bearing:

- proposal-time immutable trial count `N`;
- frozen hypothesis before result visibility;
- sealed out-of-sample period;
- multiple-testing / false-discovery correction;
- right-truncation invariance;
- warm-up / recursive-indicator convergence tests;
- parameter-search budget;
- selection-procedure audit;
- purging / embargo where labels overlap;
- frozen-forward evaluation before promotion;
- adaptive-search accounting when five variants are proposed after seeing a winner;
- independent evidence for whether a reconstructed indicator-to-strategy conversion is faithful.

The instruction to suggest five variants **after** identifying a promising strategy is particularly useful as an adversarial example of adaptive multiplicity.

## Framework disposition

Do **not** build a new Auto Trading lane.

Classify as:

`NAIVE_AI_STRATEGY_MINER_BASELINE`

This baseline belongs under the existing Auto Trading evidence machine and should be used later as a challenger against the governed pipeline.

Existing canonical research posture remains:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

## Future benchmark

When the current Auto Trading P0 acceptance conditions are satisfied, freeze one common strategy corpus and compare:

### N0 — naive prompt baseline

- collect corpus;
- translate strategy;
- run historical backtests;
- rank winners;
- generate variants;
- re-test / shortlist.

### G1 — governed framework pipeline

- source;
- claim extraction;
- hypothesis frozen before outcome visibility;
- monotonic trial count;
- data contract;
- baseline;
- leakage tests;
- realistic costs;
- multiplicity controls;
- walk-forward;
- frozen-forward;
- adversarial audit.

## Shared input corpus

The existing FMZ/Herman corpus is a suitable candidate because it is already classified as:

`BENCHMARK + BORROW_PRINCIPLE`

not as proven edge.

Do not cherry-pick the subset after results are known. Freeze corpus inclusion rules before the benchmark.

## Metrics

Compare N0 vs G1 on:

- number of tested hypotheses / variants;
- number of apparent historical winners;
- OOS survival rate;
- frozen-forward survival rate;
- max drawdown;
- post-cost return;
- profit factor;
- turnover;
- parameter sensitivity;
- false-positive strategy promotions;
- compute/API cost;
- human correction count;
- reproducibility;
- time from source to valid research receipt.

## Primary research question

> How much apparent AI-generated strategy alpha disappears once trial count, leakage, adaptive search and frozen-forward requirements are enforced?

This is more valuable than copying the source prompt as production architecture.

## Promotion / kill interpretation

If N0 performs as well as G1 prospectively at materially lower complexity/cost, the Framework should simplify.

If N0 produces many historical winners that fail governed OOS/frozen-forward testing, it becomes useful evidence for why the stricter research pipeline is required.

No outcome grants execution authority automatically.

## Relationship to existing work

This source is consistent with:
- `EXTERNAL_ARCHITECTURE_AUDIT_2026-09-12__SECOND_PASS_DECISION.md`
- `AT-SRC-0010_HERMAN_FMZ_STRATEGY_CORPUS.md`
- existing trial-count / leakage / multiplicity priorities
- the Miles adversarial benchmark already present in the experiment lifecycle.

No new THEORY_LEDGER hypothesis is required now.
