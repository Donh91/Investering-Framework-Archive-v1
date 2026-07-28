# Governance Receipt: Global Liquidity Causal Chain Research v1

**Dato:** 2026-07-28  
**Status:** PENDING_PR_VALIDATION  
**Branch:** `agent/task-20260728-global-liquidity-causal-chain-v1`

## Decision manifest

```yaml
program: GLOBAL_LIQUIDITY_CAUSAL_CHAIN_RESEARCH_v1
archive_decision: EXECUTE_ALL_PHASES_UNDER_EXISTING_BACKTEST_GOVERNANCE
claim_freeze: PASS
source_architecture: PASS_WITH_DATA_GAPS
source_acquisition: IN_PROGRESS
statistical_engine: SYNTHETIC_VALIDATION_IMPLEMENTED
 graph_engine: SYNTHETIC_VALIDATION_IMPLEMENTED
economic_execution: BLOCKED_G20_NO
independent_replication: BLOCKED_UNTIL_IMMUTABLE_ECONOMIC_RELEASE
prospective_monitoring: BOUND_TO_EXISTING_OWNERS
new_active_test: NO
new_engine: NO
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

## Local validation before write

```yaml
program_contract_checks: PASS_8_OF_8
synthetic_statistics_and_graph_tests: PASS_8_OF_8
program_control_tests_designed: 3
local_economic_data_test_executed: false
```

Synthetic tests demonstrate:

- high level correlation can coexist with weak change correlation;
- a frozen positive lag can be recovered;
- negative lead direction is rejected;
- Holm and Benjamini-Hochberg adjustments remain bounded;
- block permutation is deterministic;
- purged walk-forward respects purge, embargo and final holdout;
- rolling beta recovers known exposure;
- cyclic DAGs fail closed.

## Source identities

```yaml
raoul_pal_screenshot_1_sha256: 495849d5cdb8dbd85bef598aa12b973a31c3b14b2b864553105dec59ceca73da
raoul_pal_screenshot_2_sha256: 1e394920c440ef08a87e22f1afb22e66a107d894c673a12fcfddb958ea514c56
fred_recent_backfill_sha256: e1184a8c5b34dd7aef8a3db747de9094cc4660e9f5f4a7f8bdf0f2b1a475339d
btc_investing_pdf_sha256: eba4f29d2c61b3e4cafcf01229b116abe76b15c2f576cf24c28f0b65a800b108
```

## Validation plan

```yaml
branch_readback: PENDING
changed_file_scope: PENDING_EXPECT_15
unit_tests_in_ci: PENDING
workflow_status: PENDING
zero_unexpected_deletions: PENDING
pull_request: PENDING
merge: PENDING
main_readback: PENDING
monitoring_automation_update: PENDING
research_issue: PENDING
final_repository_state: PENDING
```

## Authority boundary

```text
RESEARCH PROGRAM: ACTIVE
SOURCE ACQUISITION: ALLOWED
SYNTHETIC ENGINEERING VALIDATION: ALLOWED
ECONOMIC TEST: BLOCKED
FINAL HOLDOUT: UNTOUCHED
NEW ACTIVE TEST: NO
NEW ENGINE: NO
LIVE LIQUIDITY SIGNAL: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
PORTFOLIO ACTION: NO
```
