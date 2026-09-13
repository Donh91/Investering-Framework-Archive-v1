# ASTRA HANDOVER - AUTO_TRADING RESEARCH VAULT

Status: Prepared for future Astra ownership of heavy research.

## Mission

When Astra becomes the primary research model for this folder, do not start by inventing a trading bot.

Start by auditing the accumulated evidence, repository overlap and current Investering Framework architecture. The objective is to identify the smallest set of robust, testable automated trading capabilities that can reuse the framework's existing intelligence without duplicating it.

## Required first pass

1. Read this entire folder.
2. Read the current repository authority / precedence documentation.
3. Locate existing owners for DATA PING, regime state, Research Lab, Forecast Ledger, Sequence Ledger, experimentation and governance.
4. Search the repo for overlap before proposing any new engine.
5. Classify every AUTO_TRADING source and theory as:
   - duplicate
   - complementary
   - conflicting
   - novel
   - insufficient evidence
6. Audit all claimed edges for testability and data availability.

## Astra research priorities

### Priority A - Reproducible strategy baselines

Implement a minimal, transparent research harness that can compare candidate strategies with simple baselines under identical data and cost assumptions.

Do not optimize aggressively.

### Priority B - Regime-conditioned strategy selection

Test whether existing framework regime/state outputs improve strategy performance without rewriting those upstream outputs.

### Priority C - Execution realism

Model fees, spread, slippage, liquidity, latency and capacity by asset tier. Reject paper edges that disappear under executable assumptions.

### Priority D - Strategy portfolio architecture

Test whether multiple simple specialists outperform a monolithic AI trading policy on robustness, drawdown and regime stability.

### Priority E - AI role audit

Compare four designs:

1. deterministic strategy
2. deterministic strategy + existing regime gates
3. deterministic strategy + AI researcher/controller
4. direct AI trading policy

The direct AI policy must earn its complexity with evidence.

### Priority F - MAEVE public behavioral reconstruction

Read `maeve/` before beginning.

MAEVE is a rare candidate natural experiment because a former CFGI-powered AI trader appears to have produced a large public forward trade record.

Do not try to guess proprietary source code.

Mission sequence:

1. Recover and normalize as many original public MAEVE trade/action rows as possible from X, historical CFGI dashboard records, caches, mirrors, archives and other public sources.
2. Reconcile row coverage against public cumulative trade-count checkpoints.
3. Reconstruct the public CFGI feature state that existed BEFORE each action, controlling for CFGI methodology/version changes.
4. Add matched no-trade controls by asset/timeframe/regime.
5. Model `P(MAEVE action | public CFGI + market + framework context)` using interpretable models first.
6. Run feature ablation across raw CFGI level, velocity, cross-timeframe divergence, rolling percentile/range, asset-vs-market dispersion and individual components.
7. Separate v1/v2 or other version epochs where evidence supports them.
8. Audit DCA, capital-weighted PnL, MFE/MAE, time-in-market, concurrent exposure, fees/slippage and trade-count semantics before trusting headline win rate.
9. Treat unexplained residual decisions as latent-factor candidates, never as proof of a specific private indicator.
10. Build MAEVE-inspired public-feature clones only after the action model is sufficiently identified, then freeze and forward-simulate them under common-clock/common-cost assumptions.

MAEVE heavy-modeling trigger:

Begin full behavioral reverse engineering when at least one is met:
- >= 200 well-formed action/position rows;
- >= 20% coverage of a documented trade epoch;
- direct historical dashboard/API trade data becomes available.

Until then, prioritize source recovery, parsers, schemas and evidence quality over model fitting.

### CFGI / MAEVE multi-timeframe evidence update - 2026-09-10

Before acquiring any new historical CFGI data, read `maeve/CFGI_MAEVE_DATA_INVENTORY_V1.json` and reuse repo-native evidence first.

The inventory currently proves several distinct evidence classes that must not be conflated:

- provider-side historical availability metadata for MARKET/BTC/ETH on native `15m`, `1h`, `4h` and `1d` back to March 2022;
- targeted, locally materialized, no-lookahead `1h` BTC/ETH historical event windows with high component-field coverage;
- immutable point-in-time `4h` CFGI cold-raw captures in `03_DAILY_CAPTURE_LOGS/raw` from 2026-08-18 onward in the currently inspected archive window;
- point-in-time `1d` cold-raw captures in the same cold lane;
- weekly derived CFGI calibration artifacts;
- the restricted MAEVE ledger/recovery package in `Donh91/secrets`, which remains the behavioral action-label authority.

Provider availability is not proof that the entire multi-year raw cube is already materialized locally. Conversely, a missing full-cube proof is not authority to bulk-backfill. First inventory exact local paths, hashes, coverage and overlap; only then request the smallest genuine missing cells.

#### Preferred research ladder

Treat timeframes as different research roles rather than assuming a policy learned on one clock scales mechanically to another:

- `15m` - research microscope. Use for MAEVE timing, feature velocity, persistence, cross-timeframe transitions, entry/DCA microstructure and sequence learning. It is not the preferred default execution clock.
- `1h` - primary execution-research candidate. Use for interpretable action models, matched controls, chronological OOS and later frozen paper simulation.
- `2h` - derived intermediate candidate only. Native provider authority is not currently proven. If tested, construct strictly from CLOSED `1h` observations using time-valid transforms such as last value, slope/change, persistence, range and disagreement. Never use future-containing resampling bins, and never label derived observations as native.
- `4h` - primary robust execution-research candidate. Lower-noise action/confirmation clock with an existing immutable forward cold-raw validation lane.
- `1d` - regime/risk context. Prefer as trend, regime and risk-budget context rather than the default trade clock.

Astra should first compare native single-timeframe `1h` and `4h` models under identical chronological splits and cost assumptions. Only after those baselines are stable should it test hierarchical fusion, where `15m` supplies time-valid micro-dynamics and `1d` supplies regime context.

Do not equate the currently observed CFGI component fields with the historically described ten public MAEVE/CFGI algorithm families unless a schema or primary source proves that mapping.

Do not use recovered MAEVE `analisis_hora` or related component columns as clean entry features until their timestamp semantics pass leakage adjudication.

## Required experiment discipline

For every experiment:

- immutable experiment ID
- frozen hypothesis
- frozen data window definitions
- source provenance
- baseline
- costs
- train / validation / test or walk-forward split
- results by regime and asset tier
- parameter sensitivity
- falsifier
- kill criteria
- reproducibility receipt

Retain failures.

## Security boundary

Do not request or store private keys in this public research repository.

Do not enable live trading as part of research.

Any future execution system must be separated from public research material and undergo explicit security, permissions, risk-limit and capital-allocation review.

## Data/licensing boundary

Do not bulk republish paid/proprietary CFGI historical raw data in the public archive unless the license explicitly permits redistribution.

Prefer public manifests containing source IDs, query metadata, hashes, derived features and reproducibility receipts. Restricted raw data belongs in an appropriate private plane.

## Expected Astra output

Astra should eventually produce:

1. `AUTO_TRADING_AUDIT.md`
2. `EXPERIMENT_REGISTRY.json` or compatible existing-registry integration
3. a minimal research/backtest implementation or adapter, only if no suitable owner already exists
4. `STRATEGY_SCORECARD.md`
5. `REJECTED_IDEAS.md`
6. a promotion recommendation with explicit evidence levels
7. for MAEVE, a provenance-backed trade coverage report, behavioral attribution report and frozen public-feature clone candidates if evidence warrants them

## Definition of success

Success is not 'a bot that trades'.

Success is a research system that can reliably distinguish:

- real edge from backtest illusion
- regime-specific edge from universal claims
- signal quality from execution quality
- useful AI control from unnecessary AI complexity
- a strategy worth paper-testing from one that should be killed
- observed MAEVE behavior from stories told about MAEVE

Only after that should live-execution architecture even be considered.
