# AT-E2-MILES-1007-v1 — Adjudication Contract

Status: APPROVED RESEARCH ONLY, PREREGISTERED, EXECUTION BLOCKED

Issue: #1007

Bound theories: `AT-HYP-0004`, `AT-HYP-0008`

External benchmark: Miles Deutscher AI-backtesting workflow

Frozen external repo snapshot: `Miles-Deutscher/Backtesting-Engine@a8f49c05760fcd0002eaed3c4f1e279e266d12b4`

## 1. Scientific question

The experiment is not designed to prove or disprove Miles Deutscher personally.

It tests two broader claims:

1. How much apparent AI-generated strategy alpha survives an honest evaluation pipeline?
2. Where should LLM intelligence live in an auto-trading architecture: strategy compilation or decision-time action selection?

The experiment must remain capable of producing an outcome that contradicts the current framework preference.

## 2. Frozen arms

### B0 — Buy and Hold
Deterministic benchmark.

### B1 — Simple SMA
Deterministic SMA crossover with parameters frozen before OOS reveal.

### B2 — Simple RSI
Deterministic RSI mean-reversion with parameters frozen before OOS reveal.

### A1 — Content Loop
The LLM may iteratively generate and improve strategies on design data only. Every proposed, failed, abandoned and rejected strategy counts toward the search budget. The final selected strategy is frozen before holdout reveal.

Purpose: quantify how much impressive in-sample performance can be manufactured through iterative AI-assisted search and how much survives honest evaluation.

### A2 — Factor Author
The LLM gets one permitted design-time task and returns deterministic executable rules or code. The resulting strategy is frozen. No LLM participates in decision-time execution.

### A3 — Action Agent
The LLM is asked to choose a bounded trading action at each decision point from the same permitted information budget. It may not rewrite its rules, inspect future outcomes or self-modify.

## 3. Hard execution preconditions

No model experiment may start until all are true:

- point-in-time replayable input history passes
- purity/look-ahead checks pass
- quarantined pre-fix derived history is excluded
- train/design/holdout boundaries are frozen
- deterministic baselines reproduce successfully
- cost/fill model is frozen

Failure of any gate means `BLOCKED`, not `PARTIAL PASS`.

## 4. Primary endpoint

`A2_FACTOR_AUTHOR_MINUS_A3_ACTION_AGENT_OOS_POST_COST_RISK_ADJUSTED_UTILITY`

This is the architecture question.

PnL alone is insufficient. The evaluator must include downside, instability and implementation burden when comparing A2 and A3.

## 5. Required secondary evidence

Report, at minimum:

- net OOS return after fees and slippage
- max drawdown
- downside-adjusted return
- profit factor
- turnover
- time in market
- trade count
- train-to-OOS alpha decay
- performance versus B0/B1/B2
- null-control excess result
- performance by regime
- BTC and ETH replication
- identical-input agreement
- run-to-run variance
- API cost
- decision latency for A3
- failed calls

## 6. Alpha-decay waterfall

Every headline result must be shown through the same sequence:

1. training / marketed result
2. after fees
3. after slippage
4. frozen holdout
5. walk-forward
6. multiplicity adjustment
7. null-control adjustment
8. regime split
9. cross-asset replication

The scientific output is the survival profile, not the best number observed anywhere in the process.

## 7. Multiplicity discipline

Winner-only reporting is forbidden.

Every A1 strategy attempt counts.

All failed, abandoned and rejected LLM-generated strategies remain in the denominator.

The report must disclose the strategy-trial count and parameter/search burden.

## 8. Adjudication states

### MILES_CONTENT_EDGE_REJECT
Use when attractive design/backtest performance does not beat the strongest simple deterministic baseline after OOS costs and multiplicity/null controls.

This does not mean AI coding is useless. It means the observed workflow did not establish predictive trading edge.

### FACTOR_AUTHOR_SUPPORTED
Requires reproducible post-cost OOS value over simple/null baselines and no material inferiority to A3 across required replication slices.

This supports the architecture pattern:

`LLM THINKS ONCE -> DETERMINISTIC MACHINE EXECUTES MANY TIMES`

### FACTOR_AUTHOR_UNPROVEN
Use when A2 does not clear simple/null baselines robustly.

### ACTION_AGENT_REJECT
Use when A3 fails to produce material reproducible OOS utility over A2 while imposing meaningfully more variance, turnover, latency or API cost.

### ACTION_AGENT_RESEARCH_CONTINUES
Only allowed if A3 materially and reproducibly improves post-cost OOS utility over A2 across BTC and ETH and more than one regime without unacceptable downside or instability.

This state does not grant paper/live or production authority.

## 9. Kill criteria

The confirmatory run is invalid if:

- holdout leakage is found
- quarantined non-PIT history is used
- prompt, strategy or parameters are tuned after holdout reveal
- deterministic baselines fail reproduction
- only the winning LLM run is retained

Architecture promotion is forbidden if:

- the claimed edge exists only on one asset
- the claimed edge exists only in one regime
- the claimed edge exists only in one stochastic run
- identical-input reproducibility fails the frozen execution-contract threshold

## 10. Authority boundary

This experiment can create evidence only.

It cannot:

- change portfolio state
- route or sign orders
- initiate paper trading
- change framework thresholds
- change model weights
- promote itself into production
- alter canonical trading state

A positive result creates a new review candidate, not authority.

## 11. Success condition for the experiment itself

The experiment succeeds scientifically even if all LLM arms fail.

A useful negative result is a successful experiment when it narrows the architecture search space.

The benchmark is complete only when the final report explicitly answers:

> Where, if anywhere, did LLM intelligence add reproducible post-cost value beyond deterministic baselines, and was that value better produced at design time or decision time?
