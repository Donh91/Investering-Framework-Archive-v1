# HISTORICAL SHADOW SENSOR VALIDATION — MASTER HANDOFF v1

## Mission
Perform a bounded, evidence-first historical reconstruction of the recovered legacy shadow sensor family and prepare a machine-readable evidence package for independent research review.

This is NOT a canonical-rule change, portfolio execution task, retrospective threshold optimization, or permission to invent missing historical semantics.

## Authority
- Repository: `Donh91/Investering-Framework-Archive-v1`
- Canonical authority for current repo state: current `main` at execution time.
- Sensor recovery authority: `04_MARKET_LEARNING/shadow_registry/LEGACY_RECOVERY_QUEUE.json` and `06_RESEARCH_LAB/historical_sensor_recovery_v1/RECOVERED_LEGACY_SENSOR_DEFINITIONS_2026-08-21.json`.
- All recovered sensors remain `RESEARCH_ONLY_NON_CANONICAL`.
- No automatic promotion, market-rule changes, threshold changes, weight changes, or portfolio execution.

## Division of labour
### Codex / repository reconstruction stage
Use repository files, git history, archived research material, timestamped DATA PING/capture/hourly/breadth/ETF/outcome data, and deterministic scripts where useful.

Do the mechanical evidence archaeology:
1. Inventory all historical source files and commits relevant to each recovered sensor.
2. Recover exact historical definitions only where provenance supports them.
3. Build a timestamped event ledger of historical sensor-observable states.
4. Join those states to contemporaneous market evidence without future leakage.
5. Build outcome windows at 6h, 12h, 24h, 48h, 72h, 7d, 14d and 30d where data permits.
6. Record missingness explicitly. Never interpolate a semantic state that cannot be reconstructed.
7. Preserve source path, commit/blob identity where available, observation timestamp, retrieval/capture timestamp, and transformation provenance.
8. Detect overlapping components and likely double counting between recovered sensors and the current sensor stack.
9. Produce evidence, not investment conclusions.

### Fresh research-thread stage
The independent research thread receives the Codex evidence package and performs adversarial scientific interpretation:
- lead/lag usefulness,
- false-positive behaviour,
- regime dependence,
- redundancy versus incremental information,
- leakage risk,
- survivorship/selection bias,
- data-quality sensitivity,
- whether evidence supports KEEP, WATCH, REDUNDANT, NOISE, REGIME_SPECIFIC, UNTESTABLE, or a separate prospective forward-test proposal.

Historical fit alone MUST NOT produce `PROMOTION_CANDIDATE` without a separately designed prospective test.

## Priority order
### P0
- `EARLY_ROTATION_PRE_TRIGGER_V1_1`
- `FAKE_ROTATION_TYPE3_V2`
- `FLOW_SUPPORTED_PULLBACK_VS_FLOW_DRIVEN_DETERIORATION`
- `BTC_SURVIVAL_ALT_DETERIORATION_DIVERGENCE`
- `ODM_V1_OUTCOME_DELAY_MAPPER`
- `CCE_V1_CONFIDENCE_COMPRESSION_ENGINE`

### P1
- `SRE_V1_SIGNAL_RELIABILITY_ENGINE`
- `FAE_V1_FORECAST_ATTRIBUTION_ENGINE`
- `ROTATION_BREADTH_FILTER_V2`
- `ROTATION_DOMINANCE_FILTER_V2`
- `ETF_FLOW_POST_TEST_BEHAVIOR`

### P2
- `ROTATION_READINESS_SCORE_V2`
- `MACRO_DELAY_WINDOW_V2`
- `RWE_V1_REGIME_WEIGHT_ENGINE`

P2 composite/adaptive constructs must not be reconstructed as if valid until component provenance and redundancy are tested. `RWE_V1_REGIME_WEIGHT_ENGINE` remains blocked from runtime and may not alter live weights.

## Required historical evidence families
Search the whole repository and git history, including archived/research material, for contemporaneous evidence such as:
- BTC and ETH price/OHLCV,
- direct ETHBTC,
- BTC dominance,
- TOTAL2/TOTAL3 or explicitly labelled proxies,
- large/mid/small-cap or Top100 breadth with membership/provenance,
- stablecoin liquidity/flows,
- ETF BTC/ETH flows and settlement status,
- funding, OI, taker flow and long/short evidence,
- macro context including PMI/business-cycle material, Copper/Gold, rates and VIX where historically available,
- DATA PING outputs and timestamped framework observations,
- forecast/outcome/maturation ledgers,
- historical research notes that pre-date the outcome being evaluated.

External public market data may be used only to fill clearly identified factual market-series gaps. Keep external backfill physically and logically separate from repo-native evidence and preserve source/provenance. Do not use outside commentary to reconstruct what the framework supposedly knew at the time.

## Anti-leakage rules
For every historical observation define `information_cutoff_utc`. Only evidence demonstrably available at or before that cutoff may contribute to sensor state. Future outcomes are joined only after the state is frozen.

Forbidden:
- using later research prose to infer an earlier state,
- tuning recovered thresholds against later outcomes,
- using famous dates or known episode identity as an input,
- silently replacing missing canonical breadth with a modern proxy,
- treating current definitions as historical definitions unless provenance establishes identity,
- selecting only successful historical episodes.

## Negative controls
Where sample size permits, include:
- timestamp-shift/placebo states,
- matched non-trigger periods,
- component-only baselines,
- simple ETHBTC/BTC-dominance/breadth baselines,
- comparison against current-stack signals available over the same window.

The question is incremental information, not whether a complex sensor can describe history after the fact.

## Minimum outputs
Create under `06_RESEARCH_LAB/historical_sensor_recovery_v1/validation_v1/`:

1. `01_SOURCE_INVENTORY.json`
2. `02_SENSOR_PROVENANCE_MATRIX.json`
3. `03_HISTORICAL_EVENT_LEDGER.csv`
4. `04_MARKET_OUTCOME_LEDGER.csv`
5. `05_SENSOR_OUTCOME_JOIN.csv`
6. `06_REDUNDANCY_DEPENDENCE_MATRIX.csv`
7. `07_NEGATIVE_CONTROLS.csv`
8. `08_DATA_GAPS_AND_UNTESTABLE.md`
9. `09_CODEX_RECONSTRUCTION_REPORT.md`
10. `10_RESEARCH_THREAD_HANDOFF.md`
11. `MANIFEST.json` with SHA-256 for all produced artifacts.

If data volume is too large for Git, keep generated bulk datasets out of canonical tracked paths and provide deterministic generation scripts plus compact summaries/manifests. Respect existing storage architecture.

## Required per-sensor reconstruction fields
At minimum:
- sensor_id
- historical_definition_status
- definition_source_path
- definition_source_commit_or_blob
- observation_timestamp_utc
- information_cutoff_utc
- component_values
- reconstructed_state
- state_confidence: EXACT / PARTIAL / UNTESTABLE
- missing_components
- repo_native_evidence_refs
- external_backfill_refs
- leakage_check
- notes

## Evaluation guardrails
Do not claim causality. Do not optimize thresholds. Do not merge distinct historical versions. Do not hide nulls. Do not score an event when required components were unavailable under the historical definition.

For P0, prioritize episode coverage and exactness over quantity. A small exact sample is superior to a large synthetic sample.

## Initial hypotheses to test, not assume
- Early Rotation Pre-Trigger may provide lead time but may be highly redundant with liquidity + dominance + ETHBTC.
- Fake Rotation Type 3 may be useful primarily as a veto/false-positive filter rather than a positive predictor.
- ETF-era divergence may explain periods where BTC remains healthy while alt breadth/ETHBTC deteriorate.
- ODM may add value by separating sensor quality from incorrect maturation horizon.
- CCE may add value if apparently independent confirmations are actually transformations of the same underlying market move.

These are hypotheses only.

## Stop conditions
Stop and label `UNTESTABLE` when exact historical semantics or required contemporaneous evidence cannot be recovered. Do not create new semantics to rescue a test.

## Write policy
Use a dedicated branch/PR. Generated findings remain research-only. Run all relevant CI. Do not merge any change that modifies canonical market rules, thresholds, weights, execution policy, or current sensor semantics.

## Final handoff
The Codex report must end with a compact research-thread brief containing:
- what is exactly reconstructed,
- what is partially reconstructed,
- what is untestable,
- strongest apparent signal candidates without promotion language,
- strongest redundancy concerns,
- highest-value unanswered questions,
- exact paths to all evidence artifacts.

The next research thread should independently challenge the reconstruction before any prospective test design is accepted.
