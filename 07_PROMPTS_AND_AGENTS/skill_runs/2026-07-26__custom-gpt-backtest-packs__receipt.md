# Skill run receipt - Custom GPT backtest packs

**Date:** 2026-07-26  
**Status:** `PASS_AUDIT / PASS_HASH_PRESERVATION / PARTIAL_BINARY_MATERIALIZATION / FINAL_SYNTHESIS_DEFERRED_PENDING_CLAUDE`

## Inputs

- `DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z.zip`
  - bytes: `159355`
  - SHA-256: `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd`
- `FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z(2).zip`
  - bytes: `27454`
  - SHA-256: `fa01757df10b4fd079829220df97e7f86792829aaad9236645ef82c4eac7fa5f`

## Validation

```yaml
large_pack_files: 70
large_pack_non_manifest_checksum_entries: 69
large_pack_checksum_mismatches: 0
parts_pack_files: 16
parts_pack_ordinary_checksum_mismatches: 0
exact_duplicate_data_files_between_packages: 5
manifest_self_reference_defects_found: YES
rebuild_script_replay_safe: NO
validation_duplicate_keys_correct: NO
```

## Routing

- source identity and hashes:
  `08_SOURCE_MATERIAL/backtests/2026-07-26__custom-gpt-history-packs/README.md`
- human audit:
  `04_MARKET_LEARNING/backtests/2026-07-26__custom-gpt-history-packs__audit.md`
- machine audit:
  `04_MARKET_LEARNING/backtests/2026-07-26__custom-gpt-history-packs__machine-audit.json`

## Boundary

The current GitHub contents route does not accept the mounted local ZIP files as raw binary repository objects. The exact hashes and logical audit are archived; raw ZIP copies remain pending a binary-capable route. No base64 surrogate was retained.

No economic backtest, edge claim, market-state change, forecast score or portfolio action was produced.

## Next gate

`INGEST_AND_COMPARE_CLAUDE_PACKAGE`
