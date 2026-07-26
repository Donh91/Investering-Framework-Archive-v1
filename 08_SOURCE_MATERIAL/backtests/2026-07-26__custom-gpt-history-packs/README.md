# Custom GPT historical backtest packs — source index

**Source date:** 2026-07-26  
**Archive status:** `HASH_AND_LOGICAL_ARCHIVE_COMPLETE / RAW_BINARY_GITHUB_COPY_PENDING_CONNECTOR / FINAL_SYNTHESIS_PENDING_CLAUDE`  
**Market, portfolio or canonical authority:** `NONE`

## Supplied source artifacts

| Original uploaded name | Bytes | SHA-256 |
|---|---:|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z.zip` | 159,355 | `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd` |
| `FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z(2).zip` | 27,454 | `fa01757df10b4fd079829220df97e7f86792829aaad9236645ef82c4eac7fa5f` |

The files were read directly from the uploaded sandbox paths and independently audited. Exact outer ZIP hashes, byte sizes, internal inventory, payload checks and audit findings are preserved here.

The currently available GitHub contents route does not accept a mounted local ZIP path as a repository binary file. Therefore this commit does not claim that the two ZIP byte streams themselves are present on `main`. No base64 surrogate or corrupted pseudo-binary copy is retained.

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
uploaded_source_bytes_locally_verified: PASS
outer_hash_preservation_in_github: PASS
logical_audit_preservation_in_github: PASS
raw_zip_repository_copy: PENDING_CONNECTOR_CAPABILITY
independent_checksum_validation: PASS_WITH_SELF_REFERENCE_EXCEPTIONS
canonical_backtest_input: NO
pipeline_fixture_value: HIGH
historical_edge_test_value: LIMITED
final_test_plan_ratification: DEFERRED_PENDING_CLAUDE_PACKAGE
```

See the independent audit at:

`04_MARKET_LEARNING/backtests/2026-07-26__custom-gpt-history-packs__audit.md`
