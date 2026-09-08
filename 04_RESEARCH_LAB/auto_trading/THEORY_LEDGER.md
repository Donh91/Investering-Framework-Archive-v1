# AUTO_TRADING THEORY LEDGER

Purpose: capture testable theories, not trading folklore.

Each theory must eventually have an immutable test ID, explicit falsifier, baseline, data contract and realistic execution-cost assumptions.

---

## AT-HYP-0001 - Process edge before signal edge

Hypothesis:
A disciplined research pipeline that forces provenance, simple baselines, out-of-sample validation and post-cost evaluation will eliminate more bad strategies than adding more indicators will create good ones.

Test status: QUEUED

Falsifier:
If strategies that pass the full pipeline do not show materially better out-of-sample survival than strategies selected from in-sample performance alone, the process has not demonstrated value.

---

## AT-HYP-0002 - Regime-conditioned strategies beat universal strategies

Hypothesis:
Existing Investering Framework regime and market-state outputs can improve automated strategy selection by turning strategies on, down-weighting them or suppressing them when their historical edge is structurally mismatched.

Examples to test:
- trend following in expansion vs chop
- mean reversion in compression vs breakout regimes
- rotation strategies only when transmission survives
- defensive/no-trade states during stress or structurally poor liquidity

Test status: HIGH PRIORITY FOR ASTRA

Guardrail:
The auto-trading layer consumes regime state. It does not rewrite the upstream regime engine to make a strategy look better.

---

## AT-HYP-0003 - Strategy portfolio over monolithic bot

Hypothesis:
A portfolio of simple, independently testable strategy families with explicit activation conditions is more robust than one large AI policy that directly maps all observations to trades.

Candidate families:
- time-series trend
- cross-sectional momentum
- mean reversion
- volatility breakout
- post-flush / reclaim behaviour
- BTC vs ecosystem relative strength
- liquidity / flow-conditioned exposure
- basis / carry where operationally and legally suitable

Test status: QUEUED

Falsifier:
If strategy diversification adds correlation, costs and instability without improving drawdown-adjusted out-of-sample performance, retain fewer strategies.

---

## AT-HYP-0004 - AI is best used as researcher and controller before predictor

Hypothesis:
LLMs/agents add more durable value by researching, coding, testing, auditing, monitoring drift and selecting among proven strategies than by directly predicting price from prose or unconstrained context.

Test status: HIGH PRIORITY FOR ASTRA

Required comparison:
- deterministic baseline strategy
- deterministic strategy + regime gating
- deterministic strategy + AI research/controller layer
- direct AI trade-decision policy

---

## AT-HYP-0005 - No-trade is an explicit action

Hypothesis:
Treating PASS / NO_EDGE as a first-class output improves risk-adjusted results by preventing weak-signal overtrading, especially after fees and slippage.

Test status: QUEUED

Metrics:
turnover, fee drag, adverse selection, drawdown, Sharpe/Sortino, profit factor, hit rate by confidence bucket.

---

## AT-HYP-0006 - Execution quality can dominate forecast quality

Hypothesis:
For smaller crypto assets, fill quality, spread, slippage, market depth and latency can erase a statistically valid signal. Strategy validation must therefore use executable prices rather than idealized closes wherever possible.

Test status: HIGH PRIORITY

Required segmentation:
BTC / ETH / large cap / mid cap / small & microcap.

---

## AT-HYP-0007 - Self-improvement requires bounded governance

Hypothesis:
An AI system that can rewrite its own strategy logic from recent outcomes will overfit unless changes are versioned, replayed, compared against frozen baselines and subjected to kill criteria.

Test status: GOVERNANCE PRINCIPLE TO VALIDATE

Default implementation:
AI may propose changes. It may not silently promote them.

---

## Candidate metrics for every strategy

At minimum:
- net return after costs
- max drawdown
- volatility
- Sharpe / Sortino where meaningful
- profit factor
- turnover
- exposure
- win/loss asymmetry
- tail loss
- regime-conditioned performance
- walk-forward stability
- parameter sensitivity
- capacity / liquidity sensitivity
- baseline excess return
- false-positive cost
- false-negative / missed-opportunity cost

Do not optimize on one headline metric.
