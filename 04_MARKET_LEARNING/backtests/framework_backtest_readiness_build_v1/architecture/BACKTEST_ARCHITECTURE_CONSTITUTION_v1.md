# FRAMEWORK BACKTEST ARCHITECTURE CONSTITUTION v1

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
architecture_id: BACKTEST_ARCHITECTURE_CONSTITUTION_v1
status: RATIFIED_DESIGN_EXECUTION_LOCKED
created_at_utc: 2026-07-27T20:05:00Z
canonical_repository: Donh91/Investering-Framework-Archive-v1
real_backtest_execution: LOCKED_UNTIL_READINESS_GATE_PASS
portfolio_authority: NONE
framework_state_authority: NONE
```

## 1. Mission

The Backtest Build exists to determine which parts of the framework contain reproducible information, which parts improve timing or risk control, which parts are redundant, and which parts are narrative rather than edge.

It is not a single strategy test. It is a scientific evaluation system for:

1. data integrity;
2. sensor validity;
3. incremental gate value;
4. sequence and survival behavior;
5. framework-state accuracy;
6. decision utility;
7. robustness across venues, eras and regimes;
8. opportunity-cost versus drawdown-protection trade-offs;
9. graph-level relationships between sensors, events and outcomes;
10. reproducibility between independent model implementations.

The primary objective is not the highest historical return. The primary objective is a framework that knows when it has evidence, when it lacks evidence and when it must fail closed.

## 2. Non-negotiable execution lock

No economic test, parameter search, threshold selection, strategy comparison or framework-promotion claim may run until every mandatory readiness gate is PASS.

Permitted before the gate:

- hash and manifest validation;
- schema validation;
- source-to-normalized parity;
- point-in-time contract validation;
- duplicate, gap and settlement checks;
- deterministic fixture replay;
- code unit tests;
- negative tests proving forbidden joins fail;
- graph construction from metadata and provenance only.

Forbidden before the gate:

- reporting backtest returns as evidence;
- ranking parameters;
- selecting gates from observed outcomes;
- using preliminary package results;
- promoting a sensor, threshold or policy;
- changing market, framework or portfolio state.

## 3. Immutable evidence hierarchy

Every dataset receives exactly one role for each test:

- `OWNER`: authoritative source for the primary result;
- `CHALLENGER`: independent robustness or venue comparison;
- `FIXTURE`: small deterministic integration sample;
- `SHADOW`: exploratory or lower-authority evidence;
- `BLOCKED`: not admissible for the declared use.

A source may be OWNER for one use and CHALLENGER or BLOCKED for another.

Examples:

- Binance spot ETH/BTC may be OWNER for a direct-pair gate.
- Derived ETH/BTC from ETHUSDT/BTCUSDT is CHALLENGER for direction and BLOCKED for direct gate scoring.
- OKX perpetual swap is OWNER for an OKX swap-specific derivatives test, but not a spot-price substitute.
- W30 five-session ETF rows are FIXTURE, while the full Farside archive is OWNER for economic ETF tests.

Owner selection must be frozen before outcome inspection.

## 4. Data lineage model

Every accepted row must be traceable through:

`raw source -> retrieval receipt -> normalized row -> feature row -> event row -> test sample -> result row -> conclusion`

Required row-level temporal fields:

- `event_time_utc`: when the measured event occurred;
- `period_start_utc` and `period_end_utc` when the row aggregates a period;
- `source_published_at_utc` when supplied or reproducibly inferable;
- `retrieved_at_utc`;
- `knowledge_at_utc`: earliest defensible time the framework could know the value;
- `decision_at_utc`;
- `execution_at_utc`;
- `label_end_utc` for forward outcomes;
- `settlement_basis`;
- `venue`;
- `market_type`;
- `method_id`;
- `source_hash` or receipt reference.

Hard temporal rule:

`knowledge_at_utc <= decision_at_utc <= execution_at_utc < label_end_utc`

Any violation is a blocking lookahead failure.

## 5. Settlement and timezone discipline

The following states must never be blended:

- `LIVE`;
- `INTRADAY_HIGH_LOW`;
- `PARTIAL_SESSION`;
- `SETTLED_UTC`;
- `SETTLED_CEST`;
- `US_SESSION_SETTLED`;
- `PERIOD_COMPLETE_SOURCE_PUBLISHED`.

UTC and Europe/Copenhagen daily series are separate datasets. A test must preregister one basis.

ETF flow dated day t is not available at the crypto-day open. The owner contract must use an explicit post-US-close `knowledge_at_utc` and a decision lag.

Monthly and annual FRED aggregates are unavailable until period completion and source publication. Latest-vintage observations are never treated as historical real-time truth unless an ALFRED or equivalent vintage field proves it.

Two-month business-cycle bars receive authority only at bar end. Bar-start indexing is plotting metadata, not tradable knowledge.

## 6. Direct, derived and proxy authority

Every feature is labelled:

- `DIRECT`;
- `DERIVED_SAME_VENUE`;
- `DERIVED_CROSS_SOURCE`;
- `INDEX_PROXY`;
- `PERPETUAL_PROXY`;
- `RECONSTRUCTION`;
- `SURVEY_OR_VENDOR_PROXY`.

Hard rules:

1. Derived ETH/BTC cannot score a direct ETH/BTC threshold.
2. Cross-divided ratio high/low fields are bounds, not traded extrema.
3. Perpetual swaps cannot silently replace spot.
4. Index candles cannot silently replace spot or perpetuals.
5. Venue-specific OI, funding, taker and positioning cannot be aggregated into a market-wide value without a separate declared aggregation method.
6. A reconstructed TechDev series cannot be represented as a vendor export.

## 7. Architecture layers

### Layer A: immutable source vault

Raw payloads, receipts, hashes, source contracts and rights flags. No feature logic.

### Layer B: normalized owner tables

Stable schemas, composite primary keys, explicit nulls, venue and method identity.

### Layer C: point-in-time feature store

Only backward-looking features. Every feature carries its maximum input knowledge time.

### Layer D: preregistered event ledger

Events are generated from frozen rules. Each row records rule version, trigger inputs and eligibility.

### Layer E: outcome ledger

Forward returns, maximum favorable excursion, maximum adverse excursion, drawdown, time-to-target, time-to-failure and survival duration.

### Layer F: test engine

Engineering, univariate, conditional, sequence, state-machine, policy and robustness tests.

### Layer G: graph engine

Provenance, dependency, lead-lag, co-occurrence and state-transition graphs.

### Layer H: synthesis and promotion

Independent replication, disagreement adjudication, confidence grading and shadow-to-core promotion rules.

## 8. Test families

### T0. Engineering and reproducibility

- checksums and package identity;
- schema and primary keys;
- source-to-normalized parity;
- W30 golden fixture replay;
- continuation and resume behavior;
- timezone and settlement parity;
- no weekend ETF zeros;
- direct versus derived authority guard;
- venue and market-type separation;
- deterministic rerun hash parity.

### T1. Sensor information tests

Measure whether one sensor contains forward information without claiming a strategy.

Required outputs:

- event count;
- unique non-overlapping cluster count;
- forward-return distribution;
- median and trimmed mean;
- bootstrap confidence interval;
- maximum adverse and favorable excursion;
- horizon stability;
- era and regime stability;
- missingness and availability profile.

### T2. Incremental gate tests

Compare a base signal with and without a gate.

Examples:

- ETH/BTC signal alone versus ETH/BTC plus breadth;
- price repair alone versus repair plus funding/OI;
- ETF flow alone versus flow plus breadth or volatility state;
- flush event alone versus delayed-rebuy confirmation.

The gate is useful only if it improves at least one declared objective without causing unacceptable degradation in the others.

### T3. Sequence and survival tests

Evaluate persistence, consecutive conditions, survival after trigger, failure hazard and time-to-confirmation.

Methods may include:

- Kaplan-Meier survival curves;
- discrete-time hazard models;
- run-length distributions;
- transition matrices;
- conditional event trees.

### T4. Framework state replay

Reconstruct what the framework could know at each decision time. No retrospective labels may enter the state generator.

Outputs:

- state confusion matrix;
- transition timing error;
- false-transition density;
- missed-transition rate;
- duration calibration;
- invalidation timeliness;
- action-permission accuracy.

BT10 remains blocked until the decision ledger and `knowledge_at_utc` fields are complete enough for the tested period.

### T5. Decision and policy utility

Only after T0-T4 pass.

Compare policies such as:

- immediate versus delayed rebuy;
- watch-only versus early deployment;
- no-rotation discipline versus permissive rotation;
- static range versus state-conditioned range;
- trim/hold decisions under deterioration.

Report:

- return;
- volatility;
- maximum drawdown;
- downside deviation;
- turnover;
- exposure time;
- opportunity cost;
- drawdown avoided;
- false-action count;
- time under incorrect state;
- tail outcomes.

No result is promoted solely because it maximizes return.

### T6. Robustness and falsification

Mandatory robustness checks:

- venue substitution where method-compatible;
- UTC versus CEST basis;
- adjacent threshold perturbations fixed before holdout;
- alternative feature windows;
- leave-one-era-out;
- leave-one-major-event-out;
- bull, bear, transition and high-volatility segmentation;
- block bootstrap;
- autocorrelation-preserving permutation;
- negative-control signals;
- synthetic timestamp shift designed to reveal leakage;
- missing-data stress;
- transaction-cost and delay stress for policy tests.

## 9. Statistical constitution

The engine must not treat daily rows as independent when horizons overlap.

Required practices:

- cluster overlapping events into independent episodes;
- use block bootstrap or event-cluster bootstrap;
- use purged walk-forward splits with embargo at least equal to the longest outcome horizon;
- reserve a final untouched chronological holdout;
- perform tuning only inside training folds;
- report effect size, uncertainty and sign stability, not p-value alone;
- apply multiple-testing control within declared hypothesis families;
- preserve all failed and null tests;
- prohibit retrospective deletion of inconvenient horizons or regimes.

Default evidence classes:

- `INSUFFICIENT_DATA`;
- `NULL_OR_UNSTABLE`;
- `DESCRIPTIVE_ONLY`;
- `REPLICATED_WEAK`;
- `REPLICATED_MATERIAL`;
- `ROBUST_CANDIDATE`;
- `CANONICAL_PROMOTION_ELIGIBLE`.

Promotion requires practical materiality, replication and robustness. Statistical significance alone is insufficient.

## 10. Outcome definitions

Every event test should evaluate a frozen subset of:

- forward return at 1, 3, 5, 7, 10, 20, 30 and 60 days;
- relative ETH versus BTC return;
- maximum favorable excursion;
- maximum adverse excursion;
- time to positive threshold;
- time to invalidation;
- probability of settled gate confirmation;
- probability of fallback below invalidation;
- state survival at 1, 3, 5, 10 and 20 sessions;
- realized volatility and range expansion;
- drawdown from event entry;
- opportunity cost versus a declared baseline.

A test must state its primary endpoint before execution. Secondary endpoints are diagnostic and cannot silently become the headline result.

## 11. Graph analysis constitution

Graph outputs are diagnostic unless separately validated.

Required graph families:

1. **Provenance DAG**: source, method, feature, event, test and conclusion lineage.
2. **Temporal dependency DAG**: which information is available before each decision.
3. **Sensor redundancy graph**: correlation, mutual information and conditional overlap.
4. **Lead-lag graph**: preregistered lag grid with walk-forward stability.
5. **Event co-occurrence graph**: which gates cluster in the same episodes.
6. **State-transition graph**: observed transition frequencies and survival durations.
7. **Contradiction graph**: sensors that systematically disagree near successes and failures.
8. **Failure-path graph**: sequence from candidate signal to invalidation.

Centrality is not causality. Edges must carry sample count, lag, stability and method identity.

## 12. Iterative research loops

### Loop 0: integrity

Reproduce hashes, schemas, rows and fixtures.

### Loop 1: independent replication

ChatGPT and Claude implement the same preregistered tests independently.

### Loop 2: discrepancy adjudication

Classify every difference as:

- data selection;
- time alignment;
- implementation;
- statistical method;
- interpretation;
- numerical tolerance.

### Loop 3: adversarial falsification

Attempt to destroy the observed effect using negative controls, alternative venues, era removal and timestamp audits.

### Loop 4: holdout execution

Run the untouched chronological holdout once.

### Loop 5: framework learning

Create a recommendation, not an automatic rule change.

Only one material rule or parameter change may be proposed per learning loop. Rejected variants remain archived.

## 13. Independent model protocol

ChatGPT and Claude receive:

- the same immutable owner registry;
- the same package hashes;
- the same event and outcome contracts;
- the same test matrix;
- the same random seeds where simulation is used;
- no access to the other model's result package before submission.

Each returns machine-readable results, code, logs, data lineage, failures and an executive conclusion.

Agreement is not proof. Disagreement is information and must be resolved at the artifact level.

## 14. Promotion ladder

`RAW_EVIDENCE -> SHADOW_OBSERVATION -> RESEARCH_CHALLENGER -> REPLICATED_CANDIDATE -> GOVERNANCE_REVIEW -> CANONICAL`

No direct jump is allowed.

Minimum promotion conditions:

- owner data PASS;
- point-in-time PASS;
- deterministic replication PASS;
- independent implementation parity PASS;
- sufficient independent episodes;
- stable effect direction across walk-forward folds;
- practical materiality;
- negative controls do not reproduce the effect;
- final holdout does not contradict the claim;
- explicit governance decision.

## 15. Current execution order

1. Freeze owner registry and accessibility status.
2. Repair package and builder contracts.
3. Build the point-in-time validator.
4. Execute T0 engineering suite.
5. Rebuild W30 golden fixture.
6. Freeze exact event definitions and primary endpoints.
7. Run independent ChatGPT and Claude implementations.
8. Reconcile outputs.
9. Run adversarial and graph analyses.
10. Execute final holdout.
11. Archive conclusions and research backlog.
12. Consider framework promotion only after governance review.

## 16. Current blockers

```yaml
corrected_final_master_summary: RECEIVED
corrected_final_master_binary_visibility: NOT_EXPOSED_IN_CURRENT_RUNTIME
final_master_byte_hash: UNVERIFIED
owner_registry: DRAFT_FROZEN_PENDING_FINAL_BYTE_AUDIT
framework_decision_ledger_point_in_time: INCOMPLETE
BT10: BLOCKED
preliminary_package_results: QUARANTINED
real_backtest_execution: LOCKED
```

The summary states that `DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip` contains 514 files, 18,934 counted rows, 513 final checksums and 489 predecessor checksums. Those claims are useful inventory evidence but do not substitute for direct byte-level verification of the ZIP.

## 17. Authority boundary

This architecture authorizes implementation and engineering validation only.

```yaml
market_call: NONE
forecast_change: NONE
rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action: NONE
backtest_result: NONE
```
