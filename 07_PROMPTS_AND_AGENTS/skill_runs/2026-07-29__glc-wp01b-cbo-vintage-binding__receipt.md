# GLC WP01B CBO Vintage Binding Receipt

**Dato:** 2026-07-29  
**Status:** PASS_POINTER_BINDING / BYTE_MATERIALIZATION_PENDING  
**Initial branch:** `agent/task-20260729-glc-wp01b-cbo-vintages`  
**Finalization branch:** `agent/task-20260729-finalize-glc-wp01b-cbo`  
**Issue:** #206

## Decision manifest

```yaml
operation: BIND_IMMUTABLE_CBO_PROJECTION_VINTAGE_POINTERS
source_owner: CONGRESSIONAL_BUDGET_OFFICE
source_repository: US-CBO/cbo-data
source_repository_commit: 284a95665f9f2f74ed1f482feb629b43fce323da
repository_vintages_bound: 3
raw_bytes_materialized: 0
sha256_materialized: 0
publication_timestamps_materialized: 0
economic_execution: false
parameter_search: false
final_holdout_access: false
framework_promotion: false
portfolio_action: false
```

## Bound source objects

```yaml
catalog_blob: 77efe04577cf723a6241ea2534c02c15705966d8
schema_blob: 8c9b7884ce88394a44d22df3643eef254b89a8d4
vintage_2024_06_blob: c71ef5986e1ccf6bdb4d993b6fcc141bfc3db9bc
vintage_2025_01_blob: 999655e773307bd04b7ea07bd03b81f5d516fa7b
vintage_2026_02_blob: 99f55b63bb8db8c214e2ee08de5ce0c216358fac
```

## Target variables

```text
proj_outlays_net_interest
proj_outlays_net_interest_gdp_share
proj_debt_held_by_public
proj_primary_deficit
```

## Paths created

```text
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/official_sources/cbo/CBO_TEN_YEAR_BUDGET_VINTAGE_MANIFEST_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/official_sources/cbo/CBO_NET_INTEREST_SOURCE_CONTRACT_v1.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/official_sources/cbo/ACQUISITION_RECEIPT_CBO_POINTERS_v1.json
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-29__glc-wp01b-cbo-vintage-binding__receipt.md
```

## Paths updated

```text
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_CONTRACTS_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_REGISTRY_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/EXECUTION_STATE_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/validate_program.py
```

## Point-in-time boundary

```text
Use only a vintage with publication_timestamp <= decision_at.
A later vintage may not revise earlier framework knowledge.
Projection year and vintage date remain separate keys.
No interpolation across fiscal years.
No forward fill across vintages.
```

## Remaining blockers

```text
CBO raw byte materialization
SHA-256 and row-count audit
publication timestamp extraction
earlier pre-2024 CBO website vintages
deterministic vintage selector
G20 readiness
```

## Final validation record

```yaml
branch_readback_manifest: PASS
branch_readback_contract: PASS
branch_readback_receipt: PASS
changed_file_scope: PASS_EXACTLY_8
zero_file_deletions: PASS
pull_request: 222
pull_request_url: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/222
pull_request_mergeable: PASS
pull_request_changed_files: 8
pull_request_additions: 512
pull_request_deletions: 14
workflow_runs: NONE_FOR_THIS_SCOPE
main_merge: PASS
main_merge_sha: a33cf589d6dd0fd93c0040c0c8c997223af4b07a
issue_206_milestone_comment: PASS
archive_content_result: PASS
write_governance_result: PASS
final_repository_state: PASS
```

The 14 deletions are replacement-line deletions in three explicitly updated JSON control files. No path was deleted.

## Authority boundary

```text
SOURCE POINTER BINDING: YES
SOURCE BYTE MATERIALIZATION: NO
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
