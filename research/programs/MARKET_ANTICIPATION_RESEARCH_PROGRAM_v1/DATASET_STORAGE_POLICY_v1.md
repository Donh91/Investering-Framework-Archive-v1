# Dataset Storage Policy v1

## Purpose

Maximize long-horizon research value without turning Git history into a bulk-object store.

## Principles

1. Git stores code, schemas, manifests, receipts, indexes, small canonical tables and compact research outputs.
2. Raw high-volume payloads are stored outside ordinary Git history unless they are both small and uniquely valuable.
3. Every external dataset must have a source identity, retrieval timestamp, settlement/publication timing, schema version, SHA-256 and explicit retention class.
4. Images and charts are derivative presentation artifacts, never primary research evidence.
5. Missing data stays missing. No silent interpolation, forward-fill or current-universe substitution.
6. Promotion from temporary artifact to durable owner dataset requires byte readback, member hashes and a registry update.

## Storage classes

### T0 - Git metadata

Use for:
- collectors, tests and workflows;
- schemas and contracts;
- manifests, receipts and hashes;
- compact indexes and coverage summaries;
- small derived tables needed for deterministic replay.

Target limits:
- preferred file size below 1 MB;
- review required above 5 MB;
- prohibited above 25 MB unless explicitly exempted.

Formats:
- JSON, JSONL, CSV, Markdown, Python, YAML.

### T1 - Git compact canonical data

Use for small, high-value, slowly changing canonical tables.

Requirements:
- normalized text format;
- deterministic ordering;
- compression-benefit assessment;
- source pointer and hash registry;
- no duplicated raw and normalized copies in Git.

Target limits:
- dataset below 20 MB uncompressed;
- annual growth forecast below 10 MB;
- otherwise route to T2 or T3.

### T2 - GitHub Actions artifacts

Use for:
- raw API payloads;
- periodic capture bundles;
- validation packages;
- temporary large replay inputs;
- pre-promotion owner candidates.

Requirements:
- artifact ID and digest in registry;
- package and member hashes;
- expiry date;
- promotion or deletion decision before expiry;
- no artifact may be the only permanent copy of a promoted owner dataset.

### T3 - durable bulk storage

Use for:
- large historical CSV/JSON/Parquet bundles;
- multi-year candles, derivatives history and constituent histories;
- immutable backtest masters;
- datasets that would materially inflate Git history.

Preferred order:
1. Git LFS when available and economically reasonable;
2. immutable release asset or dedicated data repository;
3. approved object storage with immutable versioning;
4. external source pointer only when redistribution is prohibited.

Requirements:
- immutable URI or object ID;
- package SHA-256;
- member manifest;
- schema and coverage metadata;
- local registry pointer in T0.

### T4 - external licensed or non-redistributable source

Use when data may be queried but not archived or redistributed.

Store only:
- source contract;
- retrieval recipe;
- timestamps;
- row counts and coverage;
- hashes where legally allowed;
- derived statistics that comply with license terms.

## Format policy

Priority for analytical storage:
1. Parquet with zstd for large typed tables;
2. compressed JSONL for sparse event logs;
3. gzip CSV only when interoperability requires it;
4. plain JSON/CSV for small reviewable artifacts.

PNG, JPG, PDF and charts must not substitute for row-level data. Generated charts should be reproducible from registered tables and normally excluded from permanent bulk storage.

## Retention policy

- Fixture and CI artifacts: 14 days.
- Live owner-capture candidates: 30 days unless promoted earlier.
- Failed-source and outage evidence: 30 days, with compact receipt retained permanently in Git.
- Promoted owner datasets: durable T3 copy plus permanent T0 registry entry.
- Duplicate raw captures may be deleted after parity and append-only continuity are proven, while hashes and receipts remain.

## Partitioning and compaction

- Intraday market data: partition by venue, symbol, interval and UTC month.
- Daily macro data: partition by source and UTC year.
- Event ledgers: append-only JSONL or Parquet partitioned by event family and year.
- Breadth constituents: partition by freeze date and universe-method version.
- Compact only closed partitions. Never rewrite an open partition without a new version and receipt.

## Promotion gate

A dataset may be promoted only if all are present:
- source identity;
- raw payload or immutable source object;
- normalized representation;
- package and member SHA-256;
- schema version;
- coverage start/end;
- settlement, publication and retrieval timing;
- duplicate and overlap policy;
- missingness policy;
- raw-to-normalized parity receipt;
- storage class and retention decision;
- license/redistribution classification.

## Authority

This policy grants no framework-state, model-weight or portfolio authority. Research datasets remain evidence inputs until separately validated and promoted through existing framework governance.
