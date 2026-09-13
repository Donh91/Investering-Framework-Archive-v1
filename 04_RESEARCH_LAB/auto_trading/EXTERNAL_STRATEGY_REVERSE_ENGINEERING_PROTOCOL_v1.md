# EXTERNAL STRATEGY REVERSE ENGINEERING PROTOCOL v1

Status: RESEARCH_ONLY / GENERIC AUTO_TRADING METHOD
Date: 2026-09-13
Scientific owner: existing experiment lifecycle under issue #885
First reference case: EdgeOnchain / issue #922

## Purpose

Turn an externally observable trader, bot, wallet cohort or automated strategy into a falsifiable research object without requiring access to proprietary source code.

The target is not to guess hidden internals. The target is to reconstruct the strategy's **revealed decision policy** from point-in-time observable actions and market state.

Core chain:

`identity -> action ledger -> point-in-time opportunity set -> selection policy -> sizing policy -> timing policy -> source outcome -> observable signal -> delayed executable copy outcome`

This protocol is reusable across prediction markets, on-chain wallets, copy-trading systems, smart-money feeds, MAEVE-like systems, FOMO Radar, STAMPEDE and future external strategy sources.

## Permanent distinctions

Never collapse these concepts:

1. `SOURCE_ALPHA`
   - the original strategy earns positive expectancy after its own costs.

2. `OBSERVABLE_ALPHA`
   - an external observer can identify the qualifying action or signal with a timestamp that is not retrospective.

3. `COPYABLE_ALPHA`
   - a follower entering after realistic observation, processing and routing delay retains positive expectancy after costs.

4. `SCALABLE_ALPHA`
   - the copyable edge survives realistic depth, liquidity, market impact and crowding at relevant capital size.

A source can have genuine alpha and still fail all three downstream layers.

## Edge decomposition

A profitable equity curve is not sufficient evidence of predictive skill.

Decompose observed performance into:

`selection edge x sizing edge x timing edge x execution edge x leverage/compounding`

Where applicable also isolate:

- market beta / regime exposure;
- survivorship;
- parlay or correlated-leg leverage;
- DCA or averaging effects;
- fee/rebate effects;
- promotional exclusions;
- follower modifications.

Do not call the residual `alpha` until simple counterfactuals are beaten.

## Stage 0 - Identity and source freeze

Before any performance test, resolve the exact entity being studied.

Freeze:

- canonical account / wallet / profile;
- execution wallet(s) and proxy relationships;
- known contract addresses;
- source URLs and retrieval times;
- software/repository commit where relevant;
- venue / chain / market universe;
- time span;
- known version boundaries;
- any source that can retroactively edit or delete historical signals.

Fail closed if identity is ambiguous.

Never infer that a social account, vault, dashboard and execution wallet are the same entity without evidence.

## Stage 1 - Immutable action ledger

Build the complete observable action history before analyzing winners.

Each row should preserve, where applicable:

- immutable event/action ID;
- source entity;
- action type;
- asset / market / outcome;
- side;
- first observable timestamp;
- source execution timestamp;
- transaction or order identifier;
- price / odds;
- size;
- fees;
- venue;
- liquidity / depth at action time;
- market/event start and settlement times;
- final outcome;
- realized P&L;
- provenance and retrieval timestamp.

Retain losers, cancellations, unresolved actions and failed executions.

Missing is `UNKNOWN`, never silently zero, win or loss.

## Stage 2 - Opportunity-set reconstruction

Actions alone create selection bias. Reconstruct what the strategy could have selected at each decision time.

For each action timestamp, preserve a point-in-time candidate universe with features that were genuinely available then.

Examples:

- all eligible markets on the venue;
- all tokens meeting launch/liquidity rules;
- all assets in the strategy's claimed universe;
- all candidate signals emitted by the upstream detector.

This creates both positive examples, what the strategy chose, and matched negative examples, what it did not choose.

Without an opportunity set, behavioral reverse engineering is descriptive only and cannot establish a selection policy.

## Stage 3 - Selection-policy reconstruction

Estimate:

`P(action | point-in-time observable state)`

Use transparent baselines first:

- market probability / price level;
- momentum;
- liquidity;
- volume;
- age;
- volatility;
- regime;
- simple rank / threshold rules.

Then test more flexible models only if they add out-of-sample explanatory value.

Primary questions:

- which candidates are systematically chosen?
- which candidates are systematically rejected?
- what minimum edge / score / liquidity appears necessary?
- are selection rules stable over time and regimes?
- do apparent rules survive version boundaries?

The goal is a behavioral approximation, not a claim that hidden model internals have been recovered.

## Stage 4 - Sizing-policy reconstruction

Separately model:

`size | selected action, bankroll, market state, exposure`

Test whether sizing depends on:

- estimated edge / confidence;
- implied probability / price;
- volatility;
- liquidity / capacity;
- bankroll;
- current portfolio exposure;
- correlated positions;
- drawdown / risk state;
- strategy version.

Compare source sizing with simple controls:

- equal stake;
- fixed fractional;
- volatility-scaled;
- liquidity-capped;
- capped Kelly-like rules where methodologically appropriate.

A strong equity curve driven mainly by aggressive sizing is not evidence of superior predictions.

## Stage 5 - Timing-policy reconstruction

Study when the strategy acts, not only what it selects.

Measure time relative to:

- market creation;
- event start;
- liquidity arrival;
- public catalyst;
- source signal publication;
- relevant price move.

For prediction markets, compare source entry probability with subsequent market probability.

For traded assets, compare source entry with post-entry price path and volume/liquidity changes.

Persistent favorable repricing after source action is stronger evidence than headline win rate alone, but it still requires controls for market beta and selection effects.

## Stage 6 - Source-alpha adjudication

Test source performance using the source's own executable prices and costs.

Required controls should include the simplest relevant alternatives, for example:

- market-implied probability;
- matched odds / asset / time controls;
- naive favorite or momentum rules;
- equal weighting;
- matched random selection;
- buy-and-hold or universe return where applicable.

Measure more than return:

- expectancy;
- drawdown;
- calibration where probabilistic forecasts exist;
- hit rate by probability/score bucket;
- MFE / MAE;
- turnover;
- tail losses;
- regime-conditioned results;
- parameter / rule stability.

Use dependence-aware inference when multiple actions share the same event, wallet cluster, market regime or underlying catalyst.

## Stage 7 - Observability and alpha-decay clock

Find the earliest timestamp at which an independent observer could have known the actionable signal.

Never substitute source execution time for public observability time.

Record:

- source action time;
- first machine-observable time;
- first public/social time if relevant;
- data polling delay;
- processing delay;
- routing / signing delay.

This defines the `alpha-decay clock`.

## Stage 8 - Copyability test

Reprice the same action at fixed delays from first observable time.

Default grid unless venue-specific evidence justifies another:

- immediate observable entry;
- +30 seconds;
- +1 minute;
- +5 minutes;
- additional longer horizons where strategy cadence requires them.

Use contemporaneous executable prices/orderbook depth, not the source's earlier fill or later close.

Measure:

- expected return after delay;
- probability/price deterioration;
- missed-trade rate;
- spread / slippage / fees;
- fill size available;
- capacity;
- crowding / market impact.

Output one of:

- `SOURCE_EDGE_AND_COPYABLE`
- `SOURCE_EDGE_NOT_COPYABLE`
- `NO_VERIFIED_SOURCE_EDGE`
- `INSUFFICIENT_EVIDENCE`

## Stage 9 - Scale and crowding

If copyability survives small notional, test capital sensitivity.

Simulate increasing order sizes and estimate the point where:

- slippage erases expectancy;
- fill probability falls materially;
- signal publication changes the market;
- correlated followers create crowding;
- venue limits become binding.

A strategy with positive $100 expectancy may have no scalable value.

## Stage 10 - Reverse-engineered clone test

Only after stages 0-9, build a transparent behavioral clone from observable features.

The clone must be frozen before evaluation.

Compare:

1. source strategy actions;
2. transparent reverse-engineered rules/model;
3. simple baseline;
4. optional more flexible model.

Evaluate:

- action agreement;
- calibration / ranking agreement;
- sizing agreement;
- timing agreement;
- source-outcome capture;
- copyable post-cost outcome.

High action agreement does not prove identical internals. It shows that observable behavior can be approximated.

## Stage 11 - Transfer learning into Framework

Do not import an external bot wholesale.

Promote only the smallest component that survives ablation, for example:

- a feature family;
- wallet provenance transform;
- selection threshold;
- sizing rule;
- timing rule;
- no-trade gate;
- risk veto;
- latency/capacity model.

Every promoted component must show incremental value over an existing Framework owner.

## Required falsifiers

Downgrade or reject a reverse-engineering case if:

- identity cannot be frozen;
- the historical action ledger is materially incomplete;
- losers or failed actions are selectively missing;
- the opportunity set cannot be reconstructed enough to test selection bias;
- apparent edge disappears against simple controls;
- source edge disappears after realistic costs;
- source edge exists but observation/copy delay destroys expectancy;
- performance is explained mostly by leverage, compounding or sizing rather than the claimed predictive mechanism;
- results depend on retrospective feature construction;
- the reconstructed policy is unstable across adjacent periods/regimes;
- capacity is too small to matter;
- maintenance cost exceeds expected information value.

## Anti-leakage rules

Use #885 lifecycle controls.

Permanent rules:

- freeze point-in-time features before outcomes;
- no retrospective signal edits;
- no future liquidity, settlement or price data in selection features;
- no changing identity labels after seeing outcomes without a new version;
- no reusing the same holdout to tune and grade a clone;
- every failed/abandoned specification remains in trial accounting;
- same-data method correction is not independent evidence;
- forward evidence governs promotion.

## Archive contract

Each external case should have:

1. `AT-SRC-*` source note for discovery, provenance and claims;
2. case-specific research queue;
3. immutable raw/derived ledger contract;
4. reverse-engineering experiment specification;
5. result artifact with source/copy/scale rulings;
6. prospective forward record if promoted.

Generic conclusions should be lifted out of the case file and added to `THEORY_LEDGER.md` only when they are falsifiable and reusable.

## First implementation case

EdgeOnchain is the first clean reference case because prediction-market execution offers discrete actions, explicit prices/probabilities, final settlement and public on-chain/API evidence.

The first Edge experiment should prioritize:

`canonical identity -> complete action ledger -> point-in-time market opportunity set -> selection/sizing/timing reconstruction -> source alpha -> latency-decay copy test`

Vault/token research remains secondary to the behavioral strategy-reconstruction question.

## Success condition

This protocol succeeds if it turns external performance stories into reusable, falsifiable evidence and reliably separates:

`real source edge` from `marketing`, and `source edge` from `edge the Framework can actually observe, copy and scale`.
