# MMT V3 RESEARCH QUEUE

Status: `RESEARCH_ONLY`
Owner: Investering Framework Research Lab
Source anchor: `source_notes/AT-SRC-0006_MMT_V3_MARKET_DATA_AND_SCRIPTING.md`

## Purpose

Turn MMT's market-microstructure and typed-scripting capabilities into falsifiable research tasks without creating a new market-state engine or execution authority.

MMT is treated as a candidate data/feature/compiler layer. Existing Framework owners remain authoritative for regime, Data Ping, strategy governance, execution permissions and promotion.

## Priority order

### P0 — Duplicate-coverage audit

Before any paid data purchase or large backfill:

1. inventory the exact MMT fields/timeframes/venues needed for each hypothesis;
2. map them against existing archived order-flow, derivatives, exchange and market-structure data;
3. mark each requested series as `EXISTING`, `DERIVABLE`, `FREE_FORWARD_CAPTURE`, `PAID_GAP`, or `NOT_NEEDED`;
4. refuse duplicate paid acquisition unless a reproducibility or latency requirement justifies it.

Primary objective: maximize research coverage per paid byte/request.

### P0 — Free/live Shadow capture feasibility

Test whether live MMT terminal/scripting access can create prospective evidence for the highest-value features without paid historical API acquisition.

Candidate live captures:
- top-of-book and depth imbalance
- spread/depth asymmetry
- trade sweep intensity
- buy/sell volume delta
- CVD divergence
- OI change
- funding/liquidation bursts
- TPS / trade-rate acceleration

Every capture must preserve `effective_at`, `observable_at`, `retrieved_at`, venue, symbol, feed version and source provenance.

### P1 — Execution Risk Feature Pack

Research whether microstructure improves executable-price and slippage estimation.

Compare:
- candle-close execution proxy
- spread-only proxy
- spread + depth
- spread + depth + trade-flow
- full microstructure pack

Evaluate by liquidity bucket and strategy horizon.

Success is lower realized execution-model error, not better directional PnL by construction.

### P1 — Microstructure incremental-alpha ablation

Test feature families one at a time on top of simple baselines:

Baseline A: price/volume only
Baseline B: price/volume + existing Framework regime
Baseline C: price/volume + regime + existing derivatives features

Add separately:
- book imbalance
- depth skew
- trade sweep intensity
- CVD/VD divergence
- OI interaction
- liquidation intensity
- funding stress
- heatmap concentration
- trade-rate acceleration

Only retain families that add stable out-of-time information after realistic latency and costs.

### P1 — Astra-to-MMT compiler evaluation

Compare three research implementation paths:

1. human-authored deterministic MMT script;
2. Astra-compiled typed MMT script from a frozen research specification;
3. unconstrained LLM/free-form implementation.

Measure:
- semantic correctness
- reproducibility
- compile/type failure rate
- leakage/look-ahead risk
- implementation time
- token cost
- repeated-run consistency
- ease of audit

Goal: determine whether MMT v3 is a useful deterministic target language for Astra, not whether Astra can make flashy indicators.

### P2 — Venue robustness

For surviving features, compare:
- single venue
- two-venue aggregate
- broad multi-venue aggregate

Reject features that disappear after venue changes unless there is a defensible venue-specific mechanism.

### P2 — Stress/event studies

Use microstructure around known Framework events:
- liquidation flush
- reclaim
- mechanical recovery
- breakout failure
- volatility expansion
- rotation onset

Ask whether order-flow structure improves timing or merely restates the price move after the fact.

## Candidate hypotheses

### MMT-H1 — Microstructure improves execution estimation more reliably than direction prediction

Expected result:
MMT depth/spread/trade-flow features should materially reduce execution-model error even if directional alpha is weak.

Falsifier:
No stable reduction in realized-vs-modelled execution error after accounting for feed latency and venue differences.

### MMT-H2 — Typed script compilation improves research reproducibility

Expected result:
Astra-generated typed MMT scripts from frozen specifications should have lower ambiguity and better replay consistency than unconstrained LLM decision logic.

Falsifier:
Compilation errors, semantic drift or hidden platform assumptions erase the reproducibility benefit.

### MMT-H3 — A small subset of microstructure features adds regime-conditional alpha

Expected result:
Some order-flow features may add incremental information only in specific regimes/horizons rather than universally.

Falsifier:
Incremental value disappears under walk-forward testing, realistic costs or simple feature-ablation controls.

### MMT-H4 — Prospective free/live capture can defer most paid-history needs

Expected result:
A bounded live Shadow collector can accumulate enough clean forward evidence to answer many research questions before purchasing historical raw feeds.

Falsifier:
Required sample sizes/horizons are too long, feature history is indispensable, or free/live access cannot preserve the needed fields reliably.

## Hard guardrails

- no MMT feature may rewrite upstream Framework regime state;
- no MCP agent may receive order-placement or publishing authority through this research path;
- no paid MMT history may be acquired before the duplicate-coverage audit;
- no heatmap/order-flow feature is promoted from visual intuition alone;
- no backtest may use data that was not observable at the decision timestamp;
- all strategy promotion remains under existing Research Lab / F12 / adjudication governance.

## Astra handoff

When Astra is active, first mission is **not** to build indicators.

First mission:

`existing data inventory -> gap map -> free/live feasibility -> smallest useful experiment set -> deterministic scripts -> prospective Shadow evidence -> ablation -> retain/revise/kill`

This preserves Minimum Sufficient Intelligence and avoids buying or processing data merely because it is available.
