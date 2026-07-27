# BACKTEST BUILD source index — Custom GPT phases 03 and 04

**Collection status:** `ACTIVE`  
**Test execution:** `LOCKED`

## Supplied artifacts

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T050435Z.zip` | 2,347,642 | `f1348699c9dca52eb3ab51696ffced66e6cb2840e157384320162ad8bc4916b0` | Phase 03 cumulative predecessor |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z.zip` | 4,747,666 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | latest Phase 04 cumulative candidate |

The Phase 04 package embeds the Phase 03 package byte-for-byte. Phase 03 embeds the earlier cumulative package. No embedded predecessor is counted as an independent additional sample.

## Accepted new evidence

### Phase 03

- direct OKX BTC-USDT-SWAP 1Dutc: 2023-10-31 through 2024-08-25;
- direct OKX ETH-USDT-SWAP 1Dutc: same period;
- derived ETH/BTC: same period, `DERIVED_NOT_DIRECT`;
- 300 rows per series.

### Phase 04

- direct OKX BTC-USDT-SWAP 1Dutc: 2023-01-04 through 2023-10-30;
- direct OKX ETH-USDT-SWAP 1Dutc: same period;
- derived ETH/BTC: same period, `DERIVED_NOT_DIRECT`;
- 300 rows per series.

## Cumulative same-method milestone

```yaml
continuous_OKX_swap_daily_range: 2023-01-04_to_2026-04-17
BTC_direct_rows: 1200
ETH_direct_rows: 1200
ETHBTC_derived_rows: 1200
```

## Materialization policy

The Custom GPT packages remain cumulative and include earlier ZIPs. While this batch remains open:

```yaml
hash_and_lineage_archive: ACTIVE
logical_audit_archive: ACTIVE
intermediate_raw_zip_materialization: DEFERRED
latest_final_cumulative_zip_materialization: REQUIRED_AT_COLLECTION_BATCH_CLOSE
```

Exact names, byte counts, hashes, coverage, predecessor relationships and independent QA results are preserved. Raw GitHub ZIP materialization is deferred only to avoid repeatedly storing the same nested cumulative bytes.

## Authority boundary

These packages expand source readiness only. They do not authorize backtest execution, direct ETH/BTC scoring, framework interpretation, parameter selection, forecast scoring, rule promotion or portfolio action.
