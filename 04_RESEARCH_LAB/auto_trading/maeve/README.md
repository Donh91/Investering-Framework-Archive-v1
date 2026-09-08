# MAEVE PUBLIC TRADE RECONSTRUCTION & BEHAVIORAL REVERSE ENGINEERING

Status: ACTIVE RESEARCH TRACK
Date opened: 2026-09-08
Scope: Public evidence only. Research, replay and behavioral inference. No live execution.

## Mission

Reconstruct as much of the public trading history of CFGI's former M.A.E.V.E AI trader as legally and technically possible, then use that history as a natural experiment to study which public market/sentiment states were associated with entries, exits, DCA events, reversals and successful outcomes.

The objective is NOT to claim recovery of proprietary source code or secret indicators.

The objective is to build the best evidence-backed behavioral model possible from:

1. public MAEVE trade posts and historical dashboard records;
2. archived/cached copies of those records;
3. public CFGI historical signals and sub-signals;
4. OHLCV, volatility, liquidity and execution context;
5. the Investering Framework's reconstructed market/regime state;
6. published descriptions of MAEVE architecture and version changes.

## Why this is unusually valuable

MAEVE appears to have generated a large public forward record rather than only a retrospective backtest. That creates a potentially useful labeled dataset:

`market state -> MAEVE action -> later outcome`

If enough rows are recovered, Astra can test not only whether CFGI values correlate with price, but whether specific combinations predict MAEVE's own behavior and whether those behaviors added post-cost value.

## Evidence hierarchy

### Tier A - strongest
- original MAEVE X posts with timestamps
- original CFGI AI Dashboard trade rows
- original CFGI API/history at the relevant timestamp
- official CFGI documentation/articles describing MAEVE version or methodology

### Tier B - useful secondary
- search-engine cached copies
- web archives
- third-party X mirrors preserving original post text/timestamp
- contemporary articles quoting trade counts/performance

### Tier C - hypothesis-only
- community recollections
- promotional claims without row-level data
- reconstructed technical summaries with uncertain primary provenance

Do not merge Tier C claims into the trade ledger as fact.

## Known architecture clues

Public and secondary descriptions currently suggest at least two architectural eras.

### Earlier / v1-style behavior
- loop searches for entry, then exit
- three aligned data triggers required
- trigger logic varies by coin and timeframe
- ten public CFGI data inputs plus four private inputs were described
- DCA was part of the system
- different position sizing by timeframe
- static/hard-coded trigger selection reportedly caused adaptation problems

### Later / v2-style behavior
A secondary technical description attributes the following concepts to a later overhaul:
- Market Range Evaluator (MRE), rolling per-coin/per-timeframe windows
- dynamic evaluation of indicator ranges and associated price differentials
- Optimal Data Triggers (ODT), selecting three recent high-performing compatible inputs
- GMDI-style global + asset market-direction context
- adaptive position sizing from market state and portfolio exposure
- target, stop and maximum-hold/time-loss
- simplified exit if one exit condition fires
- close/reverse when an opposite qualified signal appears

These are RESEARCH HYPOTHESES until corroborated by primary evidence.

## Core research questions

1. How much of MAEVE's action timing can be explained by the ten public CFGI components alone?
2. Do velocity, percentile/range position and cross-timeframe disagreement explain more than raw CFGI score?
3. Did MAEVE select different public features by coin/timeframe/regime?
4. Did DCA materially inflate headline win rate relative to capital-weighted return?
5. Did later versions trade differently from early 2025 versions?
6. Can residual unexplained decisions reveal the shape, timing or role of latent/private signals without pretending to identify the exact proprietary formulas?
7. Which decision patterns survived out-of-sample and which degraded as trade count and market regimes expanded?

## Behavioral clone, not code theft

The target model is:

`P(MAEVE action | public features, price state, timeframe, version era, portfolio context)`

Start with interpretable models:
- conditional frequency tables
- logistic/multinomial regression
- shallow trees/rules
- survival/time-to-exit models
- feature ablation
- SHAP only where appropriate after simpler models

A complex model that predicts MAEVE but cannot explain why is lower priority than an interpretable approximation.

## Critical anti-leakage rules

- Preserve source post timestamp separately from inferred signal timestamp and fill timestamp.
- Never use data published after the trade timestamp as an input feature.
- Split by chronological eras, not random train/test only.
- Separate v1/v2 or other version epochs wherever evidence supports a boundary.
- Treat CFGI scoring methodology changes as dataset-version boundaries.
- Do not infer a private signal simply because a public feature model fails.

## Trade-count integrity

Headline win rate may be misleading if:
- DCA legs are counted differently from positions;
- breakeven/partial exits are classified as wins;
- capital at risk differs materially by trade;
- fees/slippage are excluded;
- overlapping positions create hidden portfolio drawdown.

Therefore reconstruct, where possible:
- trade/position ID
- DCA relationship
- gross and net PnL
- capital exposure
- maximum adverse/favorable excursion
- duration
- concurrent portfolio exposure

## Current status

Architecture evidence: PARTIAL
Performance checkpoints: PARTIAL
Individual public trade rows recovered: INCOMPLETE
Historical X archive: INCOMPLETE
Historical CFGI feature replay: READY IN PRINCIPLE, subject to source/licensing access

The correct next milestone is not an inferred strategy. It is a sufficiently complete, provenance-backed trade ledger.
