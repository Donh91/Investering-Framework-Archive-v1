# BlockHorizon Source Candidate v1

**Status:** PRIVATE_RAW_ARCHIVE_RECONCILED / AGENT_RESEARCH_PREP_READY / API_PENDING / RESEARCH_ONLY  
**Authority:** NONE_BY_ITSELF  
**Added:** 2026-09-07  
**Updated:** 2026-09-09  
**Purpose:** Preserve BlockHorizon as a high-priority Bitcoin on-chain historical research source while keeping raw values, source rights, revision semantics and framework authority separate.

## Current state

The original BlockHorizon seed bundle remains complete and immutable, and the 2026-09-09 multi-series combo exports have now been reconciled into the same restricted archive.

Original 2026-09-08 expectation baseline:

- 32/32 expected CSV retrievals verified;
- 29 unique expected content hashes;
- three expected exact-content duplicate groups preserved;
- 6,472,210 expected bytes verified;
- zero expected hash mismatches.

Current restricted archive after the 2026-09-09 supplemental batch:

- 55 CSV artifacts total;
- 48 unique content SHA-256 objects;
- seven exact-content duplicate groups archive-wide;
- 13,585,728 total CSV bytes;
- 14/14 files in the 2026-09-09 batch are unique and hash/readback verified;
- 5,539,163 bytes in the 2026-09-09 batch;
- all 14 batch files contain timestamp columns and monotonic timestamp sequences;
- the 161 archive-wide and 74 batch non-reference export-column counts include distribution buckets/model fields and are not independent-chart counts.

Current private main binding:

```text
Donh91/secrets@1700dd8ee4bf7ac03f0e18cd5b3647a07fda645f
```

Raw 2026-09-09 snapshot existed at:

```text
Donh91/secrets@a03ae86385cd6a3eb31c75e14bc6355e536552d3
```

Current provider-value-free reconciliation receipt:

```text
receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/2026/09/09/2026-09-09__blockhorizon_combo_reconciliation_receipt_v1.json
```

The repository owner explicitly confirmed on 2026-09-08 that the BlockHorizon downloads are authorized for private internal archival and research. This does not grant public redistribution authority.

## IMPORTANT FOR ALL AGENTS - READ ORDER

For current BlockHorizon work, use this order:

1. `SOURCE_CONTRACT_v1.json`
2. `CURRENT_PRIVATE_BINDING.json`
3. `METRIC_REGISTRY_v2.json`
4. `ASTRA_RESEARCH_PROTOCOL_v1.md`
5. authorized private archive README
6. exact private reconciliation receipt
7. exact private raw artifact only after immutable path/hash binding.

`METRIC_REGISTRY_v1.json` and `SEED_INVENTORY_METADATA_v1.json` are retained as historical seed-state records. They must not override the current v2 registry or current binding.

## Private raw data location

The raw BlockHorizon files belong only in the private restricted data plane:

```text
repository: Donh91/secrets
raw root: raw/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
private receipts: receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
```

Agents must not copy raw rows, complete CSVs, provider-value samples or reconstructed private values into this public repository, public issues, public pull requests, public logs or public-facing outputs.

Public files may contain only provider-value-free bindings, hashes, counts, timestamp ranges, schema/completeness and validation state.

## `All` export semantics - now verified from the CSVs

The provider's `All` selector means:

```text
export the selected chart series over each series' available historical timeline
```

It does **not** mean that every sibling chart in that metric family is automatically included.

Therefore every combo CSV is preserved byte-for-byte in private raw storage, every exported column is inventoried, and overlapping columns across combo files are deduplicated analytically rather than by deleting the raw retrieval.

## Current family reconciliation

### Complete

- Plain `HODL Waves`: complete 12/12 age buckets in one 2026-09-09 CSV.
- `CDD Short Term Supply` + `CDD Long Term Supply`: cohort symmetry complete.
- Previously archived aggregate/cohort MVRV, NUPL, SOPR, aSOPR, realized cap, realized cap HODL waves, cost-basis heatmap, profitability and structural seed series remain available.

### Partial, but not blockers for research preparation

`Supply Last Active` discrete family is 4/12 present. Remaining eight:

```text
Supply Last Active 1w-1m
Supply Last Active 1m-3m
Supply Last Active 3m-6m
Supply Last Active 6m-12m
Supply Last Active 2y-3y
Supply Last Active 3y-5y
Supply Last Active 5y-7y
Supply Last Active 7y-10y
```

`Spent Volume` discrete family is 4/13 present. Remaining nine:

```text
Spent Volume <1h
Spent Volume 1d-1w
Spent Volume 1w-1m
Spent Volume 1m-3m
Spent Volume 3m-6m
Spent Volume 6m-12m
Spent Volume 2y-3y
Spent Volume 3y-5y
Spent Volume 5y-7y
```

These 17 series remain the exact family-completeness queue. They are **not prerequisites** for beginning schema/provenance/redundancy/hypothesis-design work.

### Additional high-value series already recovered in combo exports

The 2026-09-09 combo files also recovered research inputs that were previously lower priority, including:

- ASOL;
- LTS and STS Position Change;
- MVRV Adjusted Ratio;
- MVRV Momentum Oscillator;
- LTS and STS supply in Profit/Loss;
- Supply Adjusted;
- Supply Probably Lost;
- UTXO Value Spent Total;
- UTXOs Spent;
- Supply Revived 1+ and 5+ Years;
- selected Outputs Spent and Spent Volume age bands.

Optional still-uncollected P2 charts include Balanced Price, Delta Price, Delta Cap, Market Cap To Thermocap Ratio, Difficulty Ribbon and Fee Ratio Multiple. Do not collect them merely for completeness.

## Research readiness

Current state:

```text
READY_FOR_SCHEMA_PROVENANCE_REDUNDANCY_AND_HYPOTHESIS_DESIGN
```

Recommended next phase:

1. schema and definition audit;
2. point-in-time/revision-risk classification;
3. overlap and redundancy map;
4. incremental-value test design against simple baselines;
5. regime segmentation, including pre-ETF vs ETF-era;
6. walk-forward and leave-one-cycle-out specification;
7. only then decide whether any additional BlockHorizon downloads have positive information value.

This readiness does not bypass framework analysis/adjudication gates. Outcome scoring, edge claims, threshold search, PnL simulation or promotion remain governed by the existing research framework.

## Future-dated PlanB model-grid warning

The file:

```text
planb_moving_averages_2026-09-09T06-38-17.csv
```

contains 849 timestamps after the 2026-09-09 retrieval date and extends to 2029-01-05. Preserve it raw, but treat post-retrieval rows only as model/projection-grid material pending definition review.

They must never be interpreted as observed future market actuals or used as realized outcomes.

## Provider chart-menu audit

The user supplied screenshots covering the full observed BlockHorizon menu of 147 charts on 2026-09-09. The observed menu does not contain `URPD` or `UTXO Realized Price Distribution` as a separate chart. URPD is therefore not a separate BlockHorizon completion item. The already archived Cost-Basis Heatmap remains the closest available BlockHorizon price-distribution research input without implying mathematical equivalence.

## Current treatment

Do not promote BlockHorizon into canonical runtime authority.

Treat it as:

- historical research source;
- challenger/crosscheck source;
- future ingestion candidate;
- non-authoritative for portfolio actions, thresholds, DATA PING, Cycle Navigator or canonical market state.

## Durable assets

```text
SOURCE_CONTRACT_v1.json
CURRENT_PRIVATE_BINDING.json
METRIC_REGISTRY_v2.json
ASTRA_RESEARCH_PROTOCOL_v1.md
VAULT_ARCHITECTURE_v1.md
METRIC_REGISTRY_v1.json                  # historical seed registry
SEED_INVENTORY_METADATA_v1.json          # historical seed inventory snapshot
tools/blockhorizon_seed_validator.py
```

## Data-plane rule

```text
public control plane -> source contract, code, current registry, hashes/counts/date ranges and value-free bindings
restricted plane -> original raw exports, private normalized research views, immutable private receipts
credential plane -> credentials only, never ordinary repository files
```

The public Research Lab owner controls research semantics. The private repository stores values and has no independent framework or market-rule authority.

## Analysis firewall

A full historical CSV downloaded in 2026 is not proof that the metric value, methodology or revision state was available at the historical timestamp. Current-methodology reconstructions, later model refits and provider backfills can create hindsight contamination.

Research must therefore distinguish:

```text
RETROSPECTIVE_DESCRIPTIVE
CONTEMPORANEOUS_REPLAY
PROSPECTIVE_FORWARD
```

No historical result self-promotes into canonical rules.

## Re-entry triggers

Resume collection when:

- a specific research hypothesis requires one of the 17 remaining core family bands;
- incremental-value analysis justifies an optional P2 chart;
- BlockHorizon exposes validated machine-readable access;
- a private retrieval revision requires hash/readback reconciliation.

Do not resume broad collection simply because additional charts exist.
