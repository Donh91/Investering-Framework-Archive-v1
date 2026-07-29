# MAR-WP01 — Inventory and Overlap Audit

Status: COMPLETE_FOR_REPOSITORY_SCOPE
Date: 2026-07-29
Authority: RESEARCH_ONLY / ZERO_FRAMEWORK_STATE_AUTHORITY
Parent issue: #209

## 1. Purpose

Map reusable datasets, code, schemas, ledgers and governance components before any new economic testing. The audit prevents duplicate pipelines and binds each Market Anticipation work package to an existing owner where a suitable owner already exists.

## 2. Audit boundary

This receipt covers artifacts verifiably present in the canonical GitHub repository as of 2026-07-29. Uploaded chat files, external subscriptions and uncommitted local material are not treated as repository-owned until they receive an immutable source pointer, hash and knowledge timestamp.

Confidence classes:

- CONFIRMED: exact repository path, commit family or durable publication chain found.
- CONFIRMED_FAMILY: durable commit/PR family found; final owner path must be resolved by implementation code before read access.
- REFERENCED_NOT_LOCATED: named by the research contract or archive history but no exact canonical owner was located in this audit.
- MISSING: no point-in-time repository owner identified.

## 3. Confirmed reusable owners

### 3.1 Global Liquidity Causal Chain v1 — primary owner for macro-liquidity research

Canonical root:
`04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/`

Confirmed assets:
- source registry;
- source/literature baseline;
- causal DAG;
- frozen public claims;
- preregistered analysis contract;
- prospective monitoring contract;
- execution-state ledger;
- validator;
- CI contract tests;
- shared implementation module `backtest_engine/liquidity_research.py`.

Ruling: MAR-WP02 Liquidity Routing Map MUST extend this owner. It must not create a second macro-liquidity source registry, causal contract, lag calendar or monitoring pipeline.

### 3.2 DATA PING — primary owner for point-in-time market observations

Confirmed repository families include:
- raw/current packet archiving;
- source pointers and integrity receipts;
- settled Copenhagen daily rows;
- hourly and five-minute event paths;
- breadth recovery and membership state;
- venue cross-checks;
- source QA boundaries;
- validation receipts;
- machine summaries;
- prospective observations and dual-run shadow records.

Ruling: DATA PING remains the observation and evidence owner. MAR may consume frozen observations by reference but may not silently reinterpret, overwrite or repair accepted packet state.

### 3.3 Cycle Navigator — primary owner for published weekly cycle state and scoring history

Confirmed repository families include:
- locked published Cycle Navigator outputs;
- durable latest pointers;
- weekly handoffs;
- public track-record locks;
- prospective Score v2 forecasts;
- experiment-learning imports;
- Master Monday recovery/scoring links.

Ruling: MAR-WP05 Market DNA and MAR-WP07 Regime Transition Atlas may derive labels from locked Cycle Navigator history, but Cycle Navigator remains the owner of published cycle state. Derived labels require their own point-in-time receipt and may not retroactively alter a published score.

### 3.4 Backtest Readiness Build — primary owner for experiment execution

Canonical root:
`04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/`

Confirmed capabilities:
- research-program installation pattern;
- preregistration;
- source registries;
- deterministic validators;
- synthetic fixtures and CI tests;
- status addenda and immutable skill-run receipts;
- shared Python modules under `backtest_engine/`.

Ruling: all MAR economic experiments, event studies, walk-forward tests, purging, embargo, multiplicity controls and final holdout execution MUST run through this build or an explicitly versioned extension of it.

### 3.5 Forecast and Master Monday history — outcome and baseline owner

Confirmed through locked weekly execution commits linking Master Monday, Cycle Navigator and transparent prior-week scoring.

Ruling: MAR-WP06 Opportunity Cost Ledger and MAR-WP09 incremental-value analysis must compare against frozen, time-stamped forecasts and the exact baseline available at forecast time. Reconstructed hindsight forecasts are prohibited.

## 4. Components referenced but not yet bound to an exact canonical owner

The following named systems are operationally relevant but require a path-level binding receipt before MAR code may import them directly:

- Shadow Sentinel / shadow-layer feature registry;
- Research Lab package index and null-result registry;
- full Forecast Ledger schema and canonical outcome join key;
- institutional flow archives beyond ETF observations already present in DATA PING;
- options surface/history owner;
- CME positioning and basis-history owner;
- stablecoin issuance/redemption history owner;
- exchange reserve and venue-fragmentation history owner;
- DeFi liquidity and bridge-flow historical owner;
- narrative/research publication timestamp owner.

These are not assumed missing from the wider archive. They are classified as REFERENCED_NOT_LOCATED until a canonical path, schema version and receipt are identified.

## 5. Work-package owner binding

| Work package | Required primary owner | Allowed supporting owners | Duplicate owner prohibited |
|---|---|---|---|
| MAR-WP02 Liquidity Routing Map | Global Liquidity Causal Chain v1 | DATA PING, FRED/macro source receipts, ETF ledgers | macro source registry, lag calendar, causal DAG |
| MAR-WP03 Failed Move Library | DATA PING event paths | Forecast Ledger, Cycle Navigator | independent raw-price archive |
| MAR-WP04 Liquidity Stress Propagation | Backtest Build | DATA PING, Global Liquidity | separate experiment runner |
| MAR-WP05 Market DNA Library | Cycle Navigator locked history | DATA PING, Master Monday | alternative published regime state |
| MAR-WP06 Opportunity Cost Ledger | Forecast/Master Monday ledger | DATA PING outcomes, portfolio-neutral policy simulator | reconstructed hindsight forecasts |
| MAR-WP07 Regime Transition Atlas | Cycle Navigator + Backtest Build | Global Liquidity, Shadow features | unversioned regime taxonomy |
| MAR-WP08 Institutional Behaviour Atlas | DATA PING institutional-flow evidence | ETF/CME/options/stablecoin owners once bound | ad hoc scraped current-only tables |
| MAR-WP09 Incremental Value | Backtest Build | all frozen challenger tables | bespoke scoring outside frozen contract |
| MAR-WP10 Replication | independent agent + immutable release package | exact manifests and receipts | shared mutable notebook/state |

## 6. Overlap findings

### High overlap — merge/extend, do not duplicate

1. Liquidity Routing Map versus Global Liquidity Causal Chain.
2. Failed Move Library versus DATA PING prospective observations and event paths.
3. Market DNA / Regime Transition versus Cycle Navigator history and scoring governance.
4. Cross-track testing versus Backtest Readiness Build.
5. Opportunity-cost evaluation versus Master Monday/forecast scoring history.

### Complementary — retain as MAR challenger layer

1. Cross-owner event joins across macro liquidity, market microstructure and cycle state.
2. Failed-move conditional outcomes by regime.
3. Stress propagation sequencing and lead-lag uncertainty.
4. Institutional-flow archetypes conditioned on point-in-time liquidity state.
5. Explicit missed-upside versus avoided-drawdown accounting under the user's asymmetric preference.

### Not authorized at WP01

- new predictive claims;
- new framework sensors;
- portfolio actions;
- retroactive relabeling of accepted framework state;
- inspection of the sealed final holdout;
- economic backtests before schemas and label contracts are frozen.

## 7. Audit conclusion

The repository already contains most of the required governance and execution infrastructure. The principal risk is duplicate ownership, not absence of architecture. MAR should be implemented as a thin, manifest-driven challenger layer that references canonical evidence and execution owners.

Gate A is passed for repository-scope architecture and ownership design. Gate B remains blocked until the referenced-but-unlocated owners are resolved and point-in-time coverage is measured.