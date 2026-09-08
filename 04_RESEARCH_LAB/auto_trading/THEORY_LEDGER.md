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

## AT-HYP-0008 - Constrained AI-to-strategy compilation beats opaque AI decisions

Hypothesis:
Using AI to translate natural-language strategy ideas into a limited, inspectable deterministic rule schema will produce more reproducible and auditable research than allowing an LLM to directly emit BUY/SELL decisions.

Inspired by:
NMST Foundry's constrained AI form-filler approach.

Test status: HIGH PRIORITY FOR ASTRA

Required comparison:
- human-authored deterministic rule
- AI-compiled deterministic rule reviewed before test
- unconstrained AI decision policy

Success criteria:
Lower rule ambiguity, higher replay reproducibility and no material loss of post-cost strategy quality.

Falsifier:
If constrained compilation mainly creates generic rules with no useful research productivity gain, retain AI for analysis/code only.

---

## AT-HYP-0009 - Common-clock/common-cost forward competition improves strategy selection

Hypothesis:
Strategies evaluated under the same market clock, fill convention, fee model, spread/slippage assumptions and starting capital can be compared more reliably than strategies coming from independent backtests with heterogeneous assumptions.

Inspired by:
NMST League shared runtime.

Test status: HIGH PRIORITY

Required design:
- frozen rule version
- identical starting equity
- identical price source and candle-close definition
- identical fee/slippage schedule by liquidity bucket
- immutable forward-event ledger

Falsifier:
If ranking is unstable across small reasonable changes in the common execution model, the leaderboard is measuring assumptions rather than edge.

---

## AT-HYP-0010 - Frozen forward records dominate editable backtests for promotion decisions

Hypothesis:
A strategy that survives a frozen simulated forward period with immutable rules provides materially stronger promotion evidence than one selected from repeated editable backtests.

Test status: HIGH PRIORITY FOR ASTRA

Metrics:
forward return after costs, drawdown, downside deviation, turnover, strategy drift, consistency and performance relative to frozen baseline.

Guardrail:
Backtests remain for discovery. Forward records govern confidence.

Falsifier:
If frozen forward performance is not more predictive of later survival than walk-forward/backtest evidence, reduce its promotion weight.

---

## AT-HYP-0011 - CFGI has more value as a feature family than as a raw sentiment threshold

Hypothesis:
CFGI can add incremental automated-trading value when used through velocity, divergence, dispersion, component signals and regime interaction, while raw Fear/Greed score thresholds alone will show little robust forward alpha.

Rationale:
CFGI itself characterizes sentiment as a gauge rather than a price predictor and reports weak next-day predictive relationship for the composite score.

Test status: VERY HIGH PRIORITY FOR ASTRA

Feature families to test:
1. score level
2. score delta / velocity
3. 15m vs 1h vs 4h vs 1d disagreement
4. asset CFGI minus broad MARKET CFGI
5. cross-sectional CFGI dispersion across the investable universe
6. individual component values and component velocity
7. CFGI behaviour conditional on Framework regime state
8. CFGI behaviour around flush, reclaim, mechanical recovery and rotation sequences

Baselines:
- price/volume only
- simple RSI/momentum
- framework regime only
- price/volume + framework regime

Promotion requirement:
CFGI must add stable post-cost out-of-sample value over these baselines rather than merely explain moves after they occur.

Falsifier:
If feature ablation shows no stable incremental value across regimes or the value disappears after realistic latency/costs, keep CFGI as context only.

---

## AT-HYP-0012 - Modular data/signal providers improve scientific attribution

Hypothesis:
Separating data modules, signal modules, strategy logic and execution into independent components improves attribution and reduces the risk that an apparently successful strategy hides which input actually contributed edge.

Inspired by:
NMST's stated model of supplying data/signals and a marketplace for proven strategy/data modules.

Test status: QUEUED

Example architecture:
CFGI data module -> feature transformation -> deterministic strategy -> framework regime gate -> execution simulator.

Required experiment:
Run ablations that remove each module one at a time.

Falsifier:
If modularization creates complexity without improving attribution, testability or robustness, simplify the stack.

---

## AT-HYP-0013 - Dynamic top-k feature selection can outperform static sentiment thresholds

Hypothesis:
For a given coin/timeframe, selecting a small number of recently useful features from a broader feature family can outperform fixed universal thresholds, provided selection is constrained by walk-forward evidence and stability penalties.

MAEVE inspiration:
Secondary technical material describes a later system selecting three inputs dynamically from 14 candidates.

Test status: VERY HIGH PRIORITY FOR ASTRA

Required comparison:
- fixed universal 3-trigger rules
- fixed coin/timeframe-specific rules
- rolling top-3 selection
- rolling top-3 with stability/turnover penalty
- rolling top-3 with correlation/redundancy penalty

Falsifier:
If dynamic selection improves in-sample fit but loses out-of-sample stability or rotates features excessively, static/simple rules win.

---

## AT-HYP-0014 - AND-gated entries plus asymmetric exits can create high hit-rate behavior

Hypothesis:
Requiring several independent conditions for entry, while allowing exit on a target, stop, time-loss or opposite qualified signal, can produce a strategy with selective entries and rapid invalidation that exhibits a higher hit rate than symmetric entry/exit gating.

MAEVE inspiration:
Secondary architecture descriptions report three aligned entry triggers and later simplified exit logic.

Test status: HIGH PRIORITY

Required tests:
- 1-of-N, 2-of-N and 3-of-N entry gates
- symmetric vs asymmetric exit rules
- profit factor and expectancy, not hit rate alone
- regime-conditioned performance

Falsifier:
If hit-rate improvement comes mainly from tiny wins and larger losses, or disappears after costs, reject the architecture despite attractive win rate.

---

## AT-HYP-0015 - DCA can inflate headline win rate and hide capital-weighted risk

Hypothesis:
A strategy using DCA may convert many losing initial entries into profitable final positions, increasing position win rate while simultaneously increasing capital at risk, tail loss and path dependency.

MAEVE inspiration:
Secondary technical material reports DCA as an important component of the earlier system.

Test status: CRITICAL AUDIT HYPOTHESIS

Required metrics:
- first-entry accuracy
- position-level win rate
- DCA-adjusted cost basis
- capital-weighted return
- MAE before final exit
- maximum capital committed per position
- drawdown under simultaneous DCA events

Falsifier:
If DCA materially improves net expectancy and drawdown-adjusted performance rather than merely cosmetic win rate, retain it as a legitimate strategy component.

---

## AT-HYP-0016 - Global-market plus asset-specific regime hierarchy improves action quality

Hypothesis:
A two-level context model, broad market regime plus asset-specific regime, can improve direction, position size and strategy activation compared with asset signals alone.

MAEVE inspiration:
GMDI descriptions distinguish global crypto direction from individual-coin direction.

Framework fit:
This is structurally compatible with existing BTC-vs-ecosystem and regime separation, but must be tested independently rather than assumed.

Test status: HIGH PRIORITY FOR ASTRA

Falsifier:
If global context simply duplicates asset momentum/volatility without incremental out-of-sample value, do not add another regime layer.

---

## AT-HYP-0017 - Time-loss exits reduce stagnant capital drag

Hypothesis:
A maximum-hold exit can improve portfolio efficiency when a thesis fails to progress even without hitting price stop, especially for short-horizon strategies.

MAEVE inspiration:
Secondary technical material reports a maximum-hold / time-loss concept.

Test status: QUEUED

Metrics:
capital turnover, opportunity cost, expectancy by holding duration, subsequent move after forced exit, false-exit rate.

Falsifier:
If time-loss systematically exits just before delayed winners and worsens net expectancy, remove or make regime-dependent.

---

## AT-HYP-0018 - Public CFGI features can explain a meaningful fraction of MAEVE actions

Hypothesis:
A time-valid model using only public CFGI components, public market data and known context can predict MAEVE ENTRY/DCA/EXIT/NONE decisions above simple baselines.

Test status: MAEVE CORE REVERSE-ENGINEERING HYPOTHESIS

Required dataset:
A provenance-backed MAEVE action ledger plus matched no-trade controls.

Success test:
Out-of-time action prediction and calibration materially above frequency, price-only and composite-CFGI baselines.

Falsifier:
If public feature models cannot predict MAEVE action timing better than simple market-state baselines, the public inputs are insufficient to behaviorally clone the system.

Important:
Failure does not prove the existence or nature of a private signal.

---

## AT-HYP-0019 - Rolling range normalization may matter more than raw sentiment values

Hypothesis:
The predictive information in sentiment/features is more stable when expressed relative to recent coin/timeframe-specific ranges or percentiles than as absolute thresholds shared across regimes.

MAEVE inspiration:
Secondary MRE descriptions emphasize rolling range-low, range-high and price differential behavior.

Test status: VERY HIGH PRIORITY

Required comparison:
- raw feature level
- rolling percentile
- z-score
- distance from rolling extrema
- velocity conditional on percentile

Falsifier:
If normalized features add no stable out-of-sample value over raw values, avoid MRE-style complexity.

---

## AT-HYP-0020 - Apparent MAEVE performance changed materially across versions or regimes

Hypothesis:
The decline in public headline win-rate checkpoints from roughly mid-90s to 84.85% reflects one or more of: broader asset coverage, harder market regimes, changed trade counting, version changes, leverage/short introduction or genuine edge decay.

Test status: RESEARCH_QUEUED

Required evidence:
- row-level trade history by date
- version boundaries
- asset/timeframe mix
- trade counting definition
- portfolio return rather than win rate only

Falsifier:
If standardized row-level reconstruction shows the apparent change is purely a reporting/counting artifact, do not infer edge degradation.

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
