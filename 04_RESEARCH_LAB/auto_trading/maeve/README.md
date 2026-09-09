# MAEVE PUBLIC TRADE RECONSTRUCTION & BEHAVIORAL REVERSE ENGINEERING

Status: NEAR-COMPLETE ARCHIVED-ERA RECONSTRUCTION / ACTIVE RESEARCH
Date opened: 2026-09-08
Major recovery accepted: 2026-09-09
Scope: Public evidence only. Research, replay and behavioral inference. No live execution.

## Mission

Reconstruct as much of the public trading history of CFGI's former M.A.E.V.E AI trader as legally and technically possible, then use that history as a natural experiment to study which public market/sentiment states were associated with entries, exits, DCA events and successful outcomes.

The objective is NOT to claim recovery of proprietary source code or secret indicators.

The objective is to build the best evidence-backed behavioral model possible from:

1. public MAEVE trade posts and historical dashboard records;
2. archived/cached copies of those records;
3. public CFGI historical signals and sub-signals;
4. OHLCV, volatility, liquidity and execution context;
5. the Investering Framework's reconstructed market/regime state;
6. published descriptions of MAEVE architecture and version changes.

## Recovery milestone

A user-supplied Claude forensic recovery package was independently audited on 2026-09-09.

The supplied normalized package contains:
- 432 parent positions, 426 closed and 6 open;
- 1,073 recovered fills consisting of 432 parent entries plus 641 DCA legs;
- internal fill-ID coverage from 75 through 1151 with four missing IDs;
- 318 matched public social posts, including 256 exact entry+exit-price matches and 62 Parent-ID matches;
- historical dashboard capture inventory, version timeline, portfolio history and provenance files.

The exact raw/normalized provider values are not copied into this public control-plane folder. Provider-value-free package hashes, reproduced statistics, corrections and caveats are recorded in `RECOVERY_AUDIT_2026-09-09.md`.

This upgrades the earlier state from `INCOMPLETE` to `NEAR_COMPLETE` for the recoverable archived dashboard era. It remains partial against later headline checkpoints that post-date the archived ledger coverage.

## Why this is unusually valuable

MAEVE generated a large public forward record rather than only a retrospective backtest. That creates a potentially useful labeled dataset:

`market state -> MAEVE action -> later outcome`

The recovered package is already sufficient for disciplined work on entry/exit CFGI levels, DCA economics, holding time, asset/timeframe segmentation and prospectivity of public trade publication.

The highest-value future expansion is the historical CFGI feature cube across all ten public algorithm families and four timeframes.

## Evidence hierarchy

### Tier A - strongest
- original MAEVE X posts with timestamps
- original CFGI AI Dashboard trade rows
- original CFGI historical/API values at the relevant timestamp
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

## Independently reproduced high-level findings

From the supplied normalized package:
- site-convention position win rate: 93.19%;
- first-entry-only win rate: 67.14%;
- USD-weighted win rate on the 209 positions with venue sizing data: 83.73%;
- median entry CFGI: 17.0;
- median exit CFGI: 70.75;
- all 426 closed positions exit at a higher CFGI than entry;
- no closed parent position enters above CFGI 30;
- no-DCA positions have a 96.94% first-entry win rate;
- positions requiring DCA have a 41.74% first-entry win rate;
- equal-weighted mean USD-weighted PNL on the sizing-complete subset is 1.54185%, while capital-weighted PNL is 0.76971%.

These results make DCA accounting and capital-weighted performance first-class audit concerns. Headline position win rate must not be treated as entry-signal accuracy.

## Known architecture clues

Public and secondary descriptions suggest at least two architectural eras.

### Earlier / v1-style behavior
- loop searches for entry, then exit;
- three aligned data triggers reportedly required;
- trigger logic reportedly varies by coin and timeframe;
- ten public CFGI data inputs plus four private inputs were described;
- DCA was part of the system;
- different position sizing by timeframe was described.

### Later / v2-style behavior
Secondary technical descriptions attribute concepts including:
- rolling Market Range Evaluator;
- Optimal Data Trigger selection;
- global + asset market-direction context;
- adaptive sizing;
- target, stop/time-loss concepts;
- possible reversal behavior.

These exact mechanics remain RESEARCH HYPOTHESES unless corroborated by primary evidence.

## Critical corrections and caveats

1. The package statement `94.4% of entries at CFGI 10-19` should be read as `10 <= score < 20`, because half-point scores exist.
2. The social reconciliation CSV independently reproduces a median exact-match publication lag of 0.8 minutes, not the 0.7 minutes stated in the supplied README.
3. No stop-loss field or stop-triggered exit is evidenced in the recovered ledger. This does not prove proprietary logic never contained a stop mechanism.
4. The supplied version-timeline CSV has one malformed unquoted-comma row and must be normalized before machine ingestion while preserving the raw artifact unchanged.
5. `analisis_hora` is approximately one hour after entry. Impulse/volatility/volume sub-score columns must therefore be treated as look-ahead SUSPECT until their timestamp semantics are resolved.
6. `cfgi_score_entry` is currently the cleanest recovered entry-time CFGI feature.

See `RECOVERY_AUDIT_2026-09-09.md` for the detailed independent audit.

## Core research questions

1. How much of MAEVE's action timing can be explained by clean public CFGI components alone?
2. Do velocity, percentile/range position and cross-timeframe disagreement explain more than raw CFGI score?
3. Did MAEVE select different public features by coin/timeframe/regime?
4. How much of headline success came from entry quality versus DCA rescue and patient exits?
5. Did later versions trade differently from early 2025 versions?
6. Can residual unexplained decisions reveal the shape or timing of latent/private inputs without pretending to identify proprietary formulas?
7. Which decision patterns survive chronological out-of-sample testing?

## Behavioral clone, not code theft

The target model remains:

`P(MAEVE action | time-valid public features, price state, timeframe, version era, portfolio context)`

Start with interpretable methods:
- conditional frequency tables;
- logistic/multinomial regression;
- shallow trees/rules;
- survival/time-to-exit models;
- feature ablation;
- more complex explainability only after simpler baselines.

A complex model that predicts MAEVE but cannot explain why is lower priority than an interpretable approximation.

## Critical anti-leakage rules

- Preserve post timestamp, signal timestamp and fill timestamp separately.
- Never use data published or sampled after the trade timestamp as an entry feature.
- Split by chronological eras, not random train/test only.
- Preserve MAEVE version boundaries where evidence supports them.
- Treat CFGI methodology changes as dataset-version boundaries.
- Do not infer a private signal merely because public models fail.
- Keep DCA legs linked to their parent position and never double-count execution mirror rows.

## Trade-count integrity

Headline win rate can be misleading if:
- DCA legs are counted differently from positions;
- capital at risk differs materially by trade;
- fees/slippage are excluded;
- overlapping positions create hidden portfolio drawdown;
- execution mirror rows are mistaken for independent trades.

Future scoring must preserve:
- first-entry quality;
- DCA relationship;
- gross and net PNL;
- capital exposure;
- duration;
- concurrent portfolio exposure;
- opportunity cost;
- separate position-level and fill-level counts.

## Current status

Architecture evidence: PARTIAL / EVOLVING
Archived-era trade-row reconstruction: NEAR_COMPLETE
Parent-position reconstruction: 432 TOTAL / 426 CLOSED
Fill reconstruction: 1,073
Historical X/social reconciliation: HIGH-VALUE PARTIAL
Historical CFGI composite replay: STRONG STARTING POINT
Ten-family x four-timeframe feature replay: MISSING / HIGHEST-VALUE NEXT SOURCE
Live execution eligibility: FORBIDDEN
Promotion status: RESEARCH ONLY

The next milestone is not to infer a secret algorithm. It is to recover the clean historical feature cube and run frozen, leakage-safe attribution and replay experiments under existing AUTO_TRADING governance.
