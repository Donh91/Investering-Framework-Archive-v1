# BACKTEST BUILD source index — intake batch 01

## Uploaded artifacts

| Uploaded artifact | Bytes | SHA-256 | Intake classification |
|---|---:|---|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T062839Z(1).zip` | 19,137,076 | `7686e30631aba300a4c1fb09ca4e79b22e753eb3880fb7b3a81a07ccb4d83f9d` | exact duplicate of PR #174 audit |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T065351Z(1).zip` | 38,318,523 | `27e81b820aa6a7b86071a7c4a5adf09ffbac864b9d720664f3f510dc0bef5db9` | exact duplicate of PR #175 audit |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T114012Z.zip` | 930,818 | `26df6c5bba68b503ec1744b2ca03b8beecb37ce14abc8f3ced636017b2910521` | new FRED Phase 03 lineage checkpoint |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T093706Z.zip` | 153,254,475 | `0b777204eeafd71510d8a51fc75dc3007fa2f3a106ea53adebe0d97638193d0f` | new FRED Phase 02 lineage checkpoint |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T055608Z(1).zip` | 9,544,646 | `5114f3c99bfcdf47b08f14edded44386c8ae02c2c9fc2e53d1d3cbe36496a93e` | exact duplicate of PR #174 audit |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z(2).zip` | 4,747,666 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | exact duplicate of PR #173 audit |
| `TDBC v1 TechDev Business Cycle 2026-07-26(1).zip` | 237,291 | `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c` | exact duplicate of PR #171 audit |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T071452Z.zip` | 76,624,824 | `e8d601f9d715bd082c817e4f749541ac80da433c56dfa7e65a9baf003b5b305e` | new FRED Phase 01 lineage checkpoint |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T050435Z(1).zip` | 2,347,642 | `f1348699c9dca52eb3ab51696ffced66e6cb2840e157384320162ad8bc4916b0` | exact duplicate of PR #173 audit |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z(2).zip` | 159,355 | `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd` | exact duplicate of PR #168 audit |

## Integrity summary

```yaml
zip_crc: PASS_10_OF_10
DATA_PING_detached_checksums: PASS_1446_OF_1446
TDBC_detached_checksums: PASS_17_OF_17
corrupt_packages: 0
```

## Binary materialization policy

These files are cumulative checkpoints, and several contain predecessor ZIPs recursively. Their full binary payloads are therefore not copied into GitHub again.

The repository preserves exact package identity and audit lineage through:

- filename;
- byte count;
- SHA-256;
- member count;
- detached-checksum result;
- predecessor relationship;
- method and coverage boundaries;
- existing-audit or new-checkpoint classification.

The expected binary owner remains:

`DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip`

It must be uploaded and independently verified before the final owner-dataset registry is ratified.

## Authority boundary

Intermediate checkpoints are lineage evidence only. They are not independent samples and must not be summed, concatenated blindly or treated as multiple confirmations of the same rows.
