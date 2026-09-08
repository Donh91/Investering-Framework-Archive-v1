# BlockHorizon Historical Research Vault Architecture v1

**Dato:** 2026-09-08  
**Status:** OPERATIONAL_RESEARCH_ARCHITECTURE / RESEARCH_ONLY / TERMS_HOLD  
**Område:** BlockHorizon historical exports / Astra replay / backtest input / provenance  
**Primary folder:** `06_RESEARCH_LAB/blockhorizon_source_candidate_v1/`  
**Depends on:** `SOURCE_CONTRACT_v1.json`, `METRIC_REGISTRY_v1.json`, control/restricted data-plane governance

## Decision

Build one BlockHorizon source archive, not a new engine and not a new shadow layer.

The archive has three logical layers:

```text
A. immutable source-receipt layer
B. ephemeral normalized research-view layer
C. experiment / simulation layer owned by existing Research Lab governance
```

No layer may promote itself into framework authority.

## A. Source-receipt layer

Current terms status blocks GitHub persistence of raw BlockHorizon values. The durable repository record therefore contains only provider-value-free metadata: filenames, hashes, bytes, row/column counts, timestamp ranges, schema/column names, cadence, duplicate state and completeness metadata.

If the rights gate later clears, raw exports route only to the restricted data plane:

```text
Donh91/secrets/raw/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
Donh91/secrets/receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
```

Raw captures are append-only by retrieval. A changed historical export is a new revision, never an overwrite.

## B. Ephemeral normalized research view

Astra or another authorized research runner may build a temporary local panel from the user-supplied exports. The normalized view is derived, disposable and not an owner of truth.

Rules:

1. `timestamp` is the metric timestamp. `retrieved_at_utc` is provenance. Never conflate them.
2. Keep original column semantics. Never silently convert blank bucket cells to zero.
3. Preserve STH, LTH and aggregate metrics as distinct features.
4. Repeated `Price [USD]` columns may be collapsed to one BlockHorizon reference-price column only after exact crosscheck against BlockHorizon OHLC Close passes for the selected snapshot.
5. If a price mismatch exists, stop with `BLOCKHORIZON_REFERENCE_PRICE_MISMATCH` rather than select a winner silently.
6. Complex distributions remain wide or sparse depending on the task. No lossy bucketing is allowed by default.
7. Normalization never changes the source files.

Current seed validation found zero timestamp duplicates, strictly increasing timestamps for all timestamped unique datasets, and zero reference-price mismatches across the overlapping comparisons recorded in `SEED_INVENTORY_METADATA_v1.json`.

## C. Simulation and Astra research layer

Research must use existing Research Lab governance. BlockHorizon is an evidence source, not a scoring owner.

Preferred use cases:

- bottom/top event studies;
- recovery versus failed-recovery sequence studies;
- STH/LTH divergence and convergence;
- realized versus unrealized profitability transitions;
- old-coin activation and distribution lead-time;
- cost-basis reclaim and loss-cluster studies;
- pre-ETF versus ETF-era robustness checks;
- leave-one-cycle-out model validation;
- minimal sufficient sensor stack / redundancy retirement;
- challenger testing of BlockHorizon proprietary metrics.

## Information-time firewall

The current seed is a 2026 retrieval of historical series. That is not automatically contemporaneous historical evidence.

Three modes must remain separate:

```text
RETROSPECTIVE_DESCRIPTIVE
CONTEMPORANEOUS_REPLAY
PROSPECTIVE_FORWARD
```

A current reconstruction may be used for retrospective pattern research. It may not be described as a true 2017 or 2021 information-time replay unless the metric definition, model version and revision state then available are independently verified.

Explicit example: `Stock-to-Flow Model 2024 Refit` is a challenger reconstruction and cannot be treated as a pre-2024 contemporaneous signal.

## Anti-overfit contract

Astra backtests should default to:

- expanding or rolling feature transforms only, never full-sample normalization;
- no centered moving averages;
- no future returns in features;
- separate development and untouched evaluation periods;
- leave-one-cycle-out robustness where sample size permits;
- pre-ETF and ETF-era reporting separately rather than pooled-only reporting;
- continuous outcomes before arbitrary binary labels where possible;
- maximum adverse excursion, maximum favorable excursion and time-to-event outcomes;
- correlation / redundancy / incremental-value tax before adding sensors;
- falsification and negative controls;
- no threshold tuning on the final holdout.

Historical fit alone is not promotion evidence.

## Compactness

Do not duplicate source price in every normalized metric. Current seed crosscheck shows the repeated BlockHorizon `Price [USD]` column matches BlockHorizon OHLC Close on all overlapping checked rows. Deduplication is therefore safe for the current snapshot only after the validator reproduces that PASS.

Do not persist both CSV and JSON when the export semantics are identical. Prefer CSV for flat and multi-column time series. Use JSON only when a future export loses structure in CSV.

## Missing-data semantics

Raw blank percentage is not a quality score.

Examples such as early `>10y` cohorts, HODL age bands, Coin Vintages and cost-basis buckets can contain structurally impossible or inactive cells. Keep them blank until BlockHorizon definitions establish whether blank means zero, not-applicable or missing.

No interpolation by default.

## Completion criterion for Vault v1

Vault v1 is research-ready when:

- current seed metadata is hash-bound;
- P0 completion queue is exhausted or explicitly deferred;
- source definitions for every retained metric family are captured;
- rights/retention status is explicit;
- revision semantics are tested on at least one later retrieval;
- the local validator can reproduce duplicate, timestamp and reference-price checks;
- Astra protocol can construct a frozen-snapshot panel without hidden lookahead.
