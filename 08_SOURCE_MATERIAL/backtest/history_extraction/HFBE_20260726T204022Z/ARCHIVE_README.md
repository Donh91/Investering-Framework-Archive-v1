# HFBE parts 01-03 source archive

**Package ID:** `HFBE_20260726T204022Z`  
**Source ZIP:** `FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip`  
**ZIP SHA-256:** `fa01757df10b4fd079829220df97e7f86792829aaad9236645ef82c4eac7fa5f`  
**Archive status:** `ACTIVE_SOURCE_EVIDENCE`  
**Backtest authority:** `NOT_CANONICAL_BACKTEST_INPUT`

## Preservation

The complete uploaded ZIP is preserved byte-for-byte as Base64:

```text
FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip.b64
```

Reconstruction:

```bash
base64 -d FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip.b64 > FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip
```

The package and continuation manifests are also exposed as plain JSON under `exposed/manifests/`.

## Materialized evidence

```yaml
actual_window: 2026-04-18 through 2026-07-24
part_01_rows: 98
part_02_rows: 98
part_03_rows: 98
part_01_market_type: OKX index proxy, not spot
part_02_market_type: OKX index proxy, not spot
part_03_market_type: derived ETH-index / BTC-index ratio
volume_and_trade_count: unavailable
canonical_backtest_usable: false
```

## Integrity boundary

The source checksum ledger validates all 15 files it lists. Independent archival validation found two stale entries inside the source package manifest:

- the manifest's own declared size/hash;
- the checksum ledger's declared hash.

The uploaded ZIP is preserved unchanged. See `archive_integrity_receipt.json`.

## Continuation

The next extraction run must continue PART 01-03 before beginning PART 04:

```text
exposed/manifests/backtest_continuation_manifest.json
```

No market call. No portfolio action. No canonical state change.
