# BACKTEST BUILD source index — Custom GPT Phase 07

## Uploaded artifact

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T065351Z.zip` | 38,318,523 | `27e81b820aa6a7b86071a7c4a5adf09ffbac864b9d720664f3f510dc0bef5db9` | current cumulative Custom GPT package candidate |

## Package structure

```yaml
zip_members: 177
checksum_entries: 176
checksum_mismatches: 0
uncompressed_bytes: 41161787
embedded_predecessor_count: 8
latest_embedded_predecessor: DATA_PING_BACKTEST_HISTORY_PACK_20260727T062839Z.zip
latest_predecessor_hash_parity: PASS
```

## New source partitions

```text
normalized/daily/okx_swap/btc_usdt_swap_1d_2020-07-18_2021-05-13.csv
normalized/daily/okx_swap/eth_usdt_swap_1d_2020-07-18_2021-05-13.csv
normalized/daily/okx_swap/ethbtc_derived_from_okx_usdt_swaps_1d_2020-07-18_2021-05-13.csv
```

Raw evidence is split into six files under:

```text
raw/price/okx_swap_daily/phase_07_chunks/
```

Validation evidence is stored inside the package under:

```text
validation/phase_07_daily_swap_extension/
```

## Materialization policy

Collection is still active and each cumulative ZIP embeds all predecessor ZIPs. To avoid repeated nested binary storage:

```yaml
hash_and_lineage_archive: ACTIVE
logical_audit_archive: ACTIVE
intermediate_raw_zip_materialization: DEFERRED
latest_final_cumulative_zip_materialization: REQUIRED_AT_COLLECTION_BATCH_CLOSE
```

The original uploaded ZIP remains the byte owner until the cumulative collection batch closes. Repository records preserve its exact hash, byte count, coverage, predecessor relationship and independent validation result.
