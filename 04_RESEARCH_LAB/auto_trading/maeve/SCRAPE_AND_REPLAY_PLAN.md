# MAEVE SCRAPE, RECONSTRUCTION & REPLAY PLAN

Status: READY FOR INCREMENTAL COLLECTION

## Phase 0 - Source inventory

Priority order:

1. `x.com/CFGI_MAEVE` original posts.
2. Historical `cfgi.io/ai-dashboard` pages/API responses.
3. Search-engine caches and X mirrors preserving status IDs/timestamps.
4. CFGI articles, GitBook and technical update posts.
5. Public Telegram logs if discoverable.
6. Screenshots/video captures containing trade tables.

Every recovered item receives:
- canonical URL/status ID;
- publication timestamp;
- capture timestamp;
- evidence class;
- SHA-256 of preserved text/file where legally retained;
- relation to trade/position IDs.

## Phase 1 - Raw public-trade extraction

For each candidate post or dashboard row, extract only explicit facts first:

- timestamp
- asset
- side
- action type
- timeframe if stated
- entry/exit/target/stop/DCA prices if stated
- leverage if stated
- reported outcome
- linked prior trade if clear

Never infer a missing timeframe, fill, DCA relationship or outcome into raw fields.

Deduplicate using:
1. original X status ID where available;
2. dashboard trade ID where available;
3. normalized `(asset, action, timestamp, reported price)` signature as fallback.

## Phase 2 - Completeness reconciliation

Use public performance checkpoints as approximate cumulative counters.

Questions:
- how many trade events exist before each checkpoint?
- are DCA events counted as trades?
- are exits counted separately?
- are breakevens called wins?
- does a dashboard position map to several X posts?

A trade ledger must carry a `coverage_estimate` by time interval.

Do not call the dataset complete because search results stop returning posts.

## Phase 3 - Historical feature reconstruction

For each entry/action timestamp reconstruct ONLY data that would have been available then.

### CFGI public feature set

For asset and broad MARKET where available:
- composite score
- price component
- volatility component
- volume component
- impulse component
- technical component
- social component
- dominance component
- trends/search component
- whales component
- order-book/orders component

Across:
- 15m
- 1h
- 4h
- 1d

Derived without look-ahead:
- first differences / velocity
- acceleration
- rolling z-score/percentile
- distance from rolling high/low
- cross-timeframe spread
- multi-timeframe agreement count
- asset-minus-market sentiment
- component dispersion
- persistence duration above/below candidate thresholds

### Market data

- open/high/low/close/volume
- realized volatility
- ATR/range
- momentum/trend
- drawdown from local high
- distance from support/reclaim structures
- liquidity/spread/slippage proxy where available

### Framework replay

Reconstruct independent framework context, without letting MAEVE labels alter it:
- BTC/ecosystem regime
- rotation state
- stress/flush state
- post-flush stage
- volatility regime
- transmission quality
- relevant liquidity/flow state

## Phase 4 - Matched controls

A trade-only dataset cannot identify what caused trading because it omits times when MAEVE chose not to trade.

Create matched no-trade controls for each asset/timeframe:
- same hour/day-of-week distributions
- similar volatility bucket
- similar price trend/range state
- random eligible bars drawn before outcome is known

Primary modeling target:

`P(MAEVE action | public features, context)`

not merely:

`P(win | MAEVE trade)`.

## Phase 5 - Behavioral reverse engineering

Start interpretable.

### A. Rule mining
- threshold grids
- AND combinations
- persistence conditions
- cross-timeframe conjunctions
- rolling percentile/range triggers

### B. Statistical action model
- multinomial/logistic models for ENTRY / DCA / EXIT / NONE
- regularization to prevent feature explosion
- time-blocked cross-validation

### C. Tree model
Use shallow trees to expose nonlinear threshold interactions.

### D. Latent residual analysis
Fit best public-feature model.

For decisions public features explain poorly, calculate residual action probability.
Cluster residuals by:
- coin
- timeframe
- regime
- volatility
- position exposure
- version era

The residual is NOT proof of a private indicator. It is a candidate latent-factor footprint that may reflect:
- one of four private inputs;
- GMDI/portfolio state;
- missing/incorrect timestamp;
- unavailable data;
- execution constraints;
- model/version drift.

## Phase 6 - Outcome attribution

For each position reconstruct:
- gross return
- realistic fee/slippage return
- MFE
- MAE
- duration
- DCA-weighted basis
- exposure/capital at risk
- concurrent position count where possible

Compare successful vs failed trades by:
- public feature state
- feature velocity
- timeframe alignment
- regime
- entry type
- DCA count
- version era

Win rate is secondary.

Primary outputs:
- capital-weighted net PnL
- drawdown
- profit factor
- exposure
- turnover
- return per unit of drawdown/exposure
- calibration of predicted action and predicted success

## Phase 7 - Hypothesis replay

Candidate MAEVE-inspired models should be recreated from public features only.

Examples:
1. static 3-trigger conjunction
2. coin/timeframe-specific static 3-trigger rules
3. rolling top-3 feature selection
4. top-3 with redundancy/correlation penalty
5. range-percentile trigger normalization
6. global-market + asset-regime hierarchy
7. target/stop/time-loss exit
8. DCA vs no-DCA comparison
9. reversal-enabled vs no-reversal

Benchmark against:
- buy-and-hold
- simple trend
- simple mean reversion
- volatility breakout
- framework regime-gated baselines

## Phase 8 - Frozen simulated forward test

Any behavioral clone that survives historical replay must be frozen before prospective simulation.

No parameter edits after the start timestamp.

Evaluate on:
- same clock
- same costs
- same execution conventions
- same starting capital

No live money during research phase.

## Licensing / archive policy

Public trade metadata and source references may be normalized into the research ledger.

Do not bulk republish paid/proprietary CFGI historical raw data in this public repository unless its license explicitly permits redistribution.

Prefer:
- source IDs/URLs
- API query metadata
- hashes
- derived features
- aggregate/reproducible test outputs

If a paid raw dataset is acquired, store it in an appropriately private/restricted plane and bind it to public experiment manifests by hashes/receipts.

## Astra mission trigger

Astra should begin heavy reverse engineering when at least one of these is true:

A. >= 200 well-formed MAEVE position/action rows with usable timestamps, or
B. >= 20% recovered coverage of a documented MAEVE trade epoch, or
C. direct historical dashboard/API data becomes available.

Before that point, Astra may help source discovery and parser construction, but should not overfit a small convenience sample.
