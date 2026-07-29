# GLC WP01 Backtest Recovery Receipt

**Dato:** 2026-07-29  
**Status:** PENDING_PR_VALIDATION  
**Branch:** `agent/task-20260729-glc-wp01-backtest-recovery`  
**Issue:** #206

## Decision manifest

```yaml
operation: RECOVER_AND_CONTRACT_PRIOR_THREAD_BACKTEST_PACKAGES
uploaded_packages: 10
recovery_classification: RECOVERED_BASE_BINARY_PLUS_APPEND_ONLY_DELTAS
exact_final_183529Z_present: false
G01: PARTIAL_RECOVERED_CHAIN_EXACT_FINAL_MISSING
G02: BLOCKED
G20: NO
new_active_test: false
new_engine: false
parameter_search: false
final_holdout_access: false
market_state_change: false
gate_change: false
rebuy_change: false
deployment_change: false
portfolio_action: false
```

## Uploaded-artifact validation

```yaml
zip_crc_pass: 10
zip_crc_fail: 0
data_ping_checksum_entries_checked: 1457
data_ping_checksum_failures: 0
tdbc_checksum_entries_checked: 17
tdbc_checksum_failures: 0
```

## Recovered base

```yaml
filename: DATA PING BACKTEST HISTORY PACK 20260727T052808Z(1).zip
sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
bytes: 190546648
zip_members: 183
uncompressed_bytes: 209385211
internal_checksums: 180/180_PASS
master_daily_panel_rows: 5852
master_daily_panel_columns: 75
master_daily_panel_start: 2010-07-18
master_daily_panel_end: 2026-07-25
```

## Latest continuation

```yaml
filename: DATA_PING_BACKTEST_HISTORY_PACK_20260727T114012Z(1).zip
sha256: 26df6c5bba68b503ec1744b2ca03b8beecb37ce14abc8f3ced636017b2910521
internal_checksums: 257/257_PASS
role: CONTINUATION_DELTA_NOT_BASE_REPLACEMENT
```

## Portable bundle

```yaml
filename: GLC_BACKTEST_RECOVERY_BUNDLE_20260729.zip
sha256: a38fc62f2b3a2c933528878a10614d46d61dce609b2c9eebc51763e14255c64f
bytes: 2962221
members: 309
repository_storage: EXTERNAL_POINTER_AND_HASH_ONLY
```

## Paths created

```text
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/BACKTEST_MASTER_RECOVERY_MANIFEST_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/BACKTEST_MASTER_RECOVERY_REPORT_v1.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_CONTRACTS_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/ACQUISITION_RECEIPT_v1.json
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-29__glc-wp01-backtest-recovery__receipt.md
```

## Paths updated

```text
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/README.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_REGISTRY_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/EXECUTION_STATE_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/validate_program.py
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/architecture/READINESS_GATE_v2.json
```

## Source status after recovery

```yaml
exact_final_binary: BLOCKED
recovered_base: BYTE_VISIBLE_AND_CHECKSUM_PASS
master_panel: READABLE
nasdaq_official_owner: ACQUISITION_REQUIRED
bea_interest_payments: ACQUISITION_REQUIRED
cbo_vintages: ACQUISITION_REQUIRED
treasury_issuance_maturity: ACQUISITION_REQUIRED
bis_gli: ACQUISITION_REQUIRED
alfred_realtime_vintages: BLOCKED_PENDING_ACQUISITION
```

## Validation plan

```yaml
branch_readback: PENDING
program_validator: PENDING
changed_file_scope: PENDING_EXPECT_10
zero_deletions: PENDING
CI: PENDING
PR: PENDING
merge: PENDING
main_readback: PENDING
final_repository_state: PENDING
```

## Authority boundary

```text
SOURCE RECOVERY: YES
SOURCE CONTRACTS: YES
POINT-IN-TIME ENGINEERING: YES
ECONOMIC EXECUTION: NO
PARAMETER SEARCH: NO
FINAL HOLDOUT: SEALED
FRAMEWORK PROMOTION: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
DEPLOYMENT CHANGE: NO
PORTFOLIO ACTION: NO
```
