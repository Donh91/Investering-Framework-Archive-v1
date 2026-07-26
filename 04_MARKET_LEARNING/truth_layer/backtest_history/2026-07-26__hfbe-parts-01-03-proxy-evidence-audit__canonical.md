# Historical Framework Backtest Extraction — Parts 01-03 proxy-evidence audit

**Date:** 2026-07-26  
**Run ID:** `HFBE_20260726T204022Z`  
**Status:** `CANONICAL_ARCHIVE_CLASSIFICATION`  
**Evidence class:** `A2_EVIDENCE_CANDIDATE`  
**Source package:** `08_SOURCE_MATERIAL/backtest/history_extraction/HFBE_20260726T204022Z/`  
**Market-state effect:** `NONE`  
**Portfolio effect:** `NONE`

## 1. Decision

The package is accepted into the archive as validated, partial source evidence.

It is not accepted as canonical BTC spot, ETH spot or direct ETH/BTC history, and it does not unlock a full framework backtest.

```text
ARCHIVE_ACCEPTED
+
PARTIAL_WITH_EXPLICIT_GAPS
+
PROXY_SEMANTICS_PRESERVED
+
CANONICAL_BACKTEST_INPUT: NO
```

## 2. Coverage

| Part | Requested | Materialized | Rows | Classification |
|---|---|---|---:|---|
| PART 01 — BTC daily | 2021-01-01 to 2026-07-24 | 2026-04-18 to 2026-07-24 | 98 | OKX BTC-USDT index proxy |
| PART 02 — ETH daily | 2021-01-01 to 2026-07-24 | 2026-04-18 to 2026-07-24 | 98 | OKX ETH-USDT index proxy |
| PART 03 — ETH/BTC daily | 2021-01-01 to 2026-07-24 | 2026-04-18 to 2026-07-24 | 98 | deterministic derived index ratio |

The raw OKX source pages contain 100 rows per asset. Two rows per asset fall after the requested end date and remain preserved only in raw evidence.

## 3. Independent validation

Independent archival checks confirm:

- source ZIP SHA-256: `fa01757df10b4fd079829220df97e7f86792829aaad9236645ef82c4eac7fa5f`;
- 16 extracted files preserved in the source ZIP;
- all 15 entries in the source checksum ledger match their corresponding files;
- 98 normalized rows per part;
- no duplicate dates;
- continuous daily coverage inside the materialized window;
- no BTC or ETH OHLC consistency failures;
- no derived ETH/BTC bound failures;
- raw-to-normalized row reconciliation passes.

## 4. Mandatory semantic boundaries

PART 01 and PART 02 are index-price candles. They must not be silently joined to, relabelled as or substituted for:

- Binance spot;
- OKX spot;
- volume-bearing spot candles;
- trade-count-bearing spot candles.

PART 03 is not a direct traded ETH/BTC market. Its `high_proxy` and `low_proxy` fields are cross-divided bounds, not directly observed intraday extrema.

```text
VENUE_AND_MARKET_TYPE_TAG_REQUIRED
+
NO_SILENT_PROXY_TO_SPOT_SUBSTITUTION
+
NO_DIRECT_ETHBTC_GATE_AUTHORITY
```

## 5. Missing evidence

The package remains incomplete because:

- 2021-01-01 through 2026-04-17 is not materialized;
- direct spot history is absent;
- volume and trade count are absent;
- direct ETH/BTC OHLCV is absent;
- only the first OKX history page was collected.

The archived continuation state correctly returns to PART 01-03 rather than advancing to PART 04.

## 6. Packaging defect

The source package manifest contains stale declared bytes/hashes for:

1. `manifests/backtest_package_manifest.json`;
2. `validation/backtest_file_checksums.sha256`.

This is classified as:

```text
PASS_WITH_MANIFEST_SELF_REFERENCE_DEFECT
```

It does not invalidate the preserved raw rows or normalized tables. It does prevent the source package manifest from serving as sole package-integrity authority. The independent archive receipt is authoritative for the uploaded ZIP and extracted-file inventory.

## 7. Permitted research use

Permitted:

- venue-tagged proxy path comparison;
- pipeline and pagination testing;
- deterministic derivation testing;
- overlap comparison against later direct spot histories;
- data-quality and source-fallback research.

Not permitted:

- strategy-performance claims;
- direct spot execution assumptions;
- volume-sensitive indicators;
- direct ETH/BTC gate scoring;
- canonical framework replay;
- market-state, rotation, rebuy or portfolio changes.

## 8. Continuation requirement

Next run:

```text
CONTINUE PART 01
CONTINUE PART 02
RECOMPUTE PART 03
DO NOT START PART 04 YET
```

Preferred resolution order:

1. approved direct spot archive;
2. otherwise continue OKX index pagination with explicit proxy tags;
3. preserve direct and proxy series separately;
4. recompute PART 03 after both parent histories expand;
5. retain a gap ledger until requested coverage and semantics are satisfied.

No rule ratification. No market call. No portfolio action.
