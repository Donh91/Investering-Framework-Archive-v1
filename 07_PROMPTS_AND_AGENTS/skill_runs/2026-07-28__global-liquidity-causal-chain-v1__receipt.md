# Governance Receipt: Global Liquidity Causal Chain Research v1

**Dato:** 2026-07-28  
**Status:** INSTALLATION_PASS / PROGRAM_ACTIVE  
**Initial branch:** `agent/task-20260728-global-liquidity-causal-chain-v1`  
**Finalization branch:** `agent/task-20260728-finalize-global-liquidity-v1`

## Final decision manifest

```yaml
program: GLOBAL_LIQUIDITY_CAUSAL_CHAIN_RESEARCH_v1
archive_decision: EXECUTE_ALL_PHASES_UNDER_EXISTING_BACKTEST_GOVERNANCE
claim_freeze: PASS
source_architecture: PASS_WITH_DATA_GAPS
source_acquisition: IN_PROGRESS
statistical_engine: SYNTHETIC_VALIDATION_IMPLEMENTED_AND_CI_PASS
graph_engine: SYNTHETIC_VALIDATION_IMPLEMENTED_AND_CI_PASS
economic_execution: BLOCKED_G20_NO
independent_replication: BLOCKED_UNTIL_IMMUTABLE_ECONOMIC_RELEASE
prospective_monitoring: BOUND_TO_EXISTING_OWNERS
agent_delivery_monitoring: ACTIVE_EXISTING_AUTOMATION
new_active_test: NO
new_engine: NO
new_scheduler: NO
market_state_change: NO
gate_change: NO
rebuy_change: NO
deployment_change: NO
portfolio_action: NO
```

## Files created

```text
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/README.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/CLAIM_FREEZE_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_REGISTRY_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/SOURCE_AND_LITERATURE_BASELINE_v1.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/CAUSAL_DAG_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/PREREGISTERED_ANALYSIS_CONTRACT_v1.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/EXECUTION_STATE_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/AGENT_WORKPACKS_v1.md
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/PROSPECTIVE_MONITORING_CONTRACT_v1.json
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/validate_program.py
04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/STATUS_ADDENDA/2026-07-28__global-liquidity-causal-chain-v1.md
backtest_engine/liquidity_research.py
tests/backtest_engine/test_liquidity_research.py
tests/backtest_engine/test_global_liquidity_program_contract.py
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-28__global-liquidity-causal-chain-v1__receipt.md
```

## Validation and CI

```yaml
program_contract_checks: PASS_8_OF_8
synthetic_statistics_and_graph_tests: PASS_8_OF_8
program_control_tests: PASS_IN_CI
backtest_engine_foundation_workflow: PASS
backtest_wave_1_2_foundation_workflow: PASS
local_economic_data_test_executed: false
final_holdout_touched: false
```

Synthetic tests prove only method behavior:

- high level correlation can coexist with weak change correlation;
- a frozen positive lag can be recovered;
- negative lead direction is rejected;
- Holm and Benjamini-Hochberg adjustments remain bounded;
- block permutation is deterministic;
- purged walk-forward respects purge, embargo and final holdout;
- rolling beta recovers known exposure;
- cyclic DAGs fail closed.

They do not constitute economic evidence for the public liquidity claims.

## Source identities

```yaml
raoul_pal_screenshot_1_sha256: 495849d5cdb8dbd85bef598aa12b973a31c3b14b2b864553105dec59ceca73da
raoul_pal_screenshot_2_sha256: 1e394920c440ef08a87e22f1afb22e66a107d894c673a12fcfddb958ea514c56
fred_recent_backfill_sha256: e1184a8c5b34dd7aef8a3db747de9094cc4660e9f5f4a7f8bdf0f2b1a475339d
btc_investing_pdf_sha256: eba4f29d2c61b3e4cafcf01229b116abe76b15c2f576cf24c28f0b65a800b108
```

## Durable execution and monitoring

```yaml
pull_request: 205
pull_request_url: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/205
changed_files: 15
additions: 1227
deletions: 0
merge: PASS
merge_sha: afa41c5edac2c6c46937f859cbab92b2db669dd6
main_readback_readme: PASS
main_readback_execution_state: PASS
main_readback_receipt_pre_finalization: PASS
research_issue: 206
research_issue_url: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/206
codex_work_order_comment_id: 5109507321
codex_remote_delivery_at_finalization: PENDING_NO_RESPONSE_YET
monitoring_automation: FMOS_OPS_PLUS_CODEX_DELIVERY
monitoring_automation_updated: PASS
standalone_scheduler_created: NO
```

Issue #206 remains open until GLC-WP01 through GLC-WP07 and the final governance ruling are merged and read back. The existing FMOS automation monitors agent deliveries, source integrity, G15, G16, G20, immutable economic output and blind replication.

## Current phase state

```yaml
P0_CLAIM_FREEZE: PASS
P1_SOURCE_ARCHITECTURE: PASS_WITH_DATA_GAPS
P2_DATA_ACQUISITION_AND_NORMALISATION: IN_PROGRESS
P3_STATISTICAL_ENGINE_VALIDATION: SYNTHETIC_FIXTURES_IMPLEMENTED_G15_NOT_FULLY_PASSED
P4_GRAPH_ENGINE_VALIDATION: METADATA_AND_SYNTHETIC_IMPLEMENTED_G16_NOT_FULLY_PASSED
P5_ECONOMIC_TEST_EXECUTION: BLOCKED_G20_NO
P6_INDEPENDENT_REPLICATION: BLOCKED_UNTIL_P5_IMMUTABLE_RELEASE
P7_PROSPECTIVE_MONITORING: ACTIVE_SOURCE_AND_LINEAGE_ONLY
```

## Active blockers

```text
Exact final Backtest Build master binary is not byte-visible.
Exact GMI liquidity formula and source series are not disclosed.
Nasdaq owner history is not materialized.
CBO projection vintages are not materialized.
Treasury maturity and issuance owner tables are not materialized.
BIS GLI export is not materialized.
Global broad-money and PBoC histories are incomplete.
Historical real-time macro vintages are incomplete.
G15 and G16 are not fully passed.
G20 remains NO for this program.
```

These are execution gates, not abandonment conditions. The program proceeds through the next eligible work package and fails closed where source or readiness evidence is absent.

## Final installation validation

```yaml
branch_readback: PASS
changed_file_scope: PASS_EXACTLY_15
unit_tests_in_ci: PASS
workflow_status: PASS_2_OF_2
zero_unexpected_deletions: PASS
pull_request_mergeable: PASS
main_merge: PASS
main_readback: PASS
monitoring_automation_update: PASS
research_issue_created: PASS
write_governance_result: PASS
installation_repository_state: PASS
research_program_completion: IN_PROGRESS
```

## Authority boundary

```text
RESEARCH PROGRAM: ACTIVE
SOURCE ACQUISITION: ALLOWED
SYNTHETIC ENGINEERING VALIDATION: ALLOWED
ECONOMIC TEST: BLOCKED UNTIL G20 PASS
FINAL HOLDOUT: UNTOUCHED
NEW ACTIVE TEST: NO
NEW ENGINE: NO
NEW SCHEDULER: NO
LIVE LIQUIDITY SIGNAL: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
DEPLOYMENT CHANGE: NO
PORTFOLIO ACTION: NO
```
