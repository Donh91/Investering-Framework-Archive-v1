# AUTO_TRADING GOVERNANCE

Status: Binding for this research folder until explicitly superseded.

## 1. Research before execution

AUTO_TRADING is a research program, not an execution authority.

No live order placement, wallet signing, API trading permission, leverage activation or autonomous capital allocation may originate from this folder without a separate explicit promotion and security review.

## 2. Existing framework remains upstream authority

Do not build a parallel DATA PING, regime engine, Forecast Ledger, Sequence Ledger or governance system merely to support a trading idea.

Prefer adapters that consume existing verified outputs.

If an auto-trading hypothesis disagrees with the existing framework, log the disagreement and test it. Do not silently rewrite upstream truth.

## 3. Evidence ladder

A strategy idea progresses through:

`INSPIRATION -> SPECIFIED -> REPRODUCED -> BACKTESTED -> WALK_FORWARD -> PAPER_LIVE -> AUDITED -> ELIGIBLE_FOR_PROMOTION`

Skipping stages is prohibited unless a later governance document explicitly allows it.

## 4. Minimum admissibility requirements

Before a strategy can leave research status, it must have:

- exact entry, exit and sizing rules
- exact data inputs and timestamp semantics
- data provenance
- immutable test version / ID
- simple baseline comparison
- realistic fees, spread and slippage
- out-of-sample or walk-forward evidence
- sensitivity analysis
- failure conditions / kill criteria
- regime segmentation
- evidence of no look-ahead leakage
- reproducible code and environment

## 5. Social-media rule

Tweets, threads, videos and screenshots are discovery inputs only.

PnL screenshots, claimed win rates, claimed wealth, creator reputation and engagement counts carry zero strategy-evidence weight unless independently reproduced.

## 6. Backtest hygiene

Every test should assume the backtest is wrong until proven otherwise.

Audit specifically for:

- look-ahead bias
- survivorship bias
- selection bias
- data snooping
- parameter overfit
- fee/slippage omission
- unrealistic fill assumptions
- timestamp mismatch
- future-universe leakage
- exchange delistings
- token liquidity/capacity constraints

## 7. Benchmark-first rule

Every sophisticated strategy must beat relevant simple baselines after costs.

Examples:
- buy-and-hold
- cash / no-trade
- simple moving-average trend
- simple momentum
- simple mean reversion
- fixed volatility targeting

If complexity does not add robust out-of-sample value, kill the complexity.

## 8. Asset-tier separation

Do not transfer evidence from BTC/ETH mechanically to microcaps.

At minimum segment:

- BTC
- ETH
- large-cap alts
- mid-cap alts
- small/microcaps

Execution assumptions and capacity must be specific to the tier.

## 9. AI change-control

Agents may:

- find sources
- generate hypotheses
- write test code
- run experiments
- challenge assumptions
- propose parameter changes
- monitor drift

Agents may not silently:

- promote a strategy
- rewrite frozen historical tests
- move the goalposts after an outcome
- delete failed experiments
- trade live capital

## 10. Negative evidence

Failed experiments are retained.

A rejected strategy is a useful result if it prevents future rediscovery of the same false edge.

## 11. Promotion principle

Promotion must answer:

1. What specific edge is demonstrated?
2. Against which baseline?
3. In which regimes and assets?
4. After which costs?
5. How stable is it out of sample?
6. What breaks it?
7. What is the maximum permitted risk if later used live?
8. How will we know it has decayed?

Until these are answered with evidence, status remains research-only.
