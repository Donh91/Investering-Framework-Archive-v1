# Marginal Decision Value & Breadth Truth v1 — Source and Reproducibility Receipt

**Dato:** 2026-07-12  
**Status:** RECEIPT  
**Område:** source lineage / reproducibility  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/marginal_decision_breadth_v1/`

## Frozen source products

```yaml
program_package:
  filename: MARGINAL_DECISION_VALUE_BREADTH_TRUTH_PROGRAM_v1_20260712.zip
  bytes: 21981813
  sha256: 84d1614e5fdeb2477853fe980f588450e099a9b9ea852bb13a141f1e640481ca
  files: 55

breadth_source_artifact:
  filename: CMC_FROZEN_BREADTH_TRUTH_2023_2026_V3.zip
  bytes: 21500916
  sha256: 5664e81a38161486d21fa01116a5ee9f88ec60a1f9ce36bc9da003b9a4a2050c
  weekly_snapshots: 184
  frozen_universe_rows: 18400
```

## GitHub execution lineage

```yaml
research_repository: Donh91/Eksperimenter-framework-
extractor_install_merge_sha: e123c2aa3e5e0df7bdb7fa935be4525af15eb3f7
validated_parser_and_taxonomy_merge_sha: 7f338cfbac1da29682fea9bb5772e47fb4af421a
successful_workflow_run_id: 29200348955
artifact_id: 8262211530
artifact_digest: sha256:5664e81a38161486d21fa01116a5ee9f88ec60a1f9ce36bc9da003b9a4a2050c
workflow_conclusion: success
```

Relevant durable code owners in the experiment repository:

```text
scripts/fetch_cmc_frozen_breadth.py
scripts/fetch_cmc_frozen_breadth_v2.py
.github/workflows/run_cmc_frozen_breadth_truth.yml
```

## Source convention

```text
provider: CoinMarketCap historical snapshot pages
source convention: CMC_HISTORICAL_WEEKLY_FROZEN_UNIVERSE
snapshot cadence: weekly Sunday snapshots
period: 2023-01-01 through 2026-07-05
interpolation: none
current-constituent backfill as truth: forbidden / not used
```

The source parser decodes the historical 200-row table embedded inside CoinMarketCap `__NEXT_DATA__` / `props.initialState`. Stablecoin exclusion uses exact stablecoin tags and symbols rather than the broader `stablecoin-protocol` tag, which could incorrectly exclude volatile protocol tokens.

## Archived package coverage

`PACKAGE_MANIFEST.csv` preserves exact paths, byte sizes and SHA-256 values for every file in the 55-file research package, including the source artifact, charts and reproduction scripts.

The canonical repository stores:

- the durable research owner;
- machine summary;
- principal evidence tables;
- complete package manifest;
- exact experiment-repository code and run receipts;
- updated governance and active-test state.

The complete 22 MB package and 21.5 MB raw source artifact are identified by hash and remain external frozen package products. This repository snapshot is not described as a byte-complete copy of either ZIP.

## Method boundary

- Weekly snapshots are not daily observations.
- Four-week snapshot changes are not historical daily 30DMA breadth.
- No missing observations were interpolated.
- No current constituent set was projected backward as truth.
- M4 contains one resolved real rotation episode.
- Exploratory negative or exhaustion relations do not become inverse live rules.
- No portfolio backtest or portfolio action is claimed.

## Reproduction status

```text
SOURCE_EXTRACTION_CODE: PRESERVED_IN_EXPERIMENT_REPOSITORY
SOURCE_RUN_RECEIPT: PASS
PACKAGE_MANIFEST: PASS
CANONICAL_DURABLE_LEARNING: PRESERVED
BYTE_COMPLETE_ZIP_IN_CANONICAL_REPO: NO
FULL_GIT_MIRROR: NOT_CLAIMED
```
