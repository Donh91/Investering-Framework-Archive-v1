# Custom GPT historical backtest packs — source index

**Source date:** 2026-07-26  
**Archive status:** `RAW_BINARY_ARCHIVED / INDEPENDENT_AUDIT_COMPLETE / FINAL_SYNTHESIS_PENDING_CLAUDE`  
**Market, portfolio or canonical authority:** `NONE`

## Archived source artifacts

| Repository file | Original uploaded name | Bytes | SHA-256 |
|---|---|---:|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z.zip` | same | 159,355 | `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd` |
| `FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip` | `FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z(2).zip` | 27,454 | `fa01757df10b4fd079829220df97e7f86792829aaad9236645ef82c4eac7fa5f` |

The binary files are retained byte-for-byte. Their internal packages are not silently repaired or rewritten.

## Package relationship

The extraction-parts package is an earlier continuation artifact for parts 01–03. Five of its substantive data files are byte-identical to files already included in the larger history pack:

- BTC daily OKX index proxy;
- ETH daily OKX index proxy;
- derived ETH/BTC daily index proxy;
- raw BTC OKX index response;
- raw ETH OKX index response.

Therefore the smaller package adds lineage, continuation state, receipts, missing-data records and validation context, but not five additional independent datasets.

## Current disposition

```yaml
raw_source_preservation: PASS
independent_checksum_validation: PASS_WITH_SELF_REFERENCE_EXCEPTIONS
canonical_backtest_input: NO
pipeline_fixture_value: HIGH
historical_edge_test_value: LIMITED
final_test_plan_ratification: DEFERRED_PENDING_CLAUDE_PACKAGE
```

See the independent audit at:

`04_MARKET_LEARNING/backtests/2026-07-26__custom-gpt-history-packs__audit.md`
