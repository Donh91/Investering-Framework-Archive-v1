# WP04C5D Binance USD-M Derivatives Owner Capture

## Scope

Prospective public derivatives owner capture for BTCUSDT and ETHUSDT covering:
- funding rate history and current funding context;
- open interest snapshots;
- mark price and index price context;
- settled timestamps and retrieval timestamps;
- raw endpoint payloads, normalized rows, receipts and member hashes.

## Source policy

Primary source is Binance USD-M public market-data endpoints. No silent venue substitution is permitted. If the source is geo-restricted or unavailable, the capture must emit an explicit failure receipt. OKX, Bybit or other venues may later be added as separately identified owner datasets, never as hidden replacements.

## Storage routing

- raw payloads: T2 Actions artifact;
- normalized current capture: T2 Actions artifact;
- manifests, receipts and registry pointers: T0 Git metadata;
- closed monthly partitions after promotion: T3 durable bulk, preferably Parquet with zstd;
- charts and screenshots: excluded as primary evidence.

## Required fields

Each normalized row must include:
- venue;
- symbol;
- metric;
- source timestamp;
- settled or observation timestamp;
- retrieval timestamp;
- value and units;
- source endpoint identity;
- raw member SHA-256;
- schema version;
- missingness status.

## Gates

- no interpolation or forward-fill;
- duplicate timestamp rejection;
- numeric and sign validation;
- raw-to-normalized parity;
- package and member readback;
- two independent live artifacts before prospective verification;
- enumeration and outcome access remain closed.
