# Skill-run receipt — Claude OTA standalone reconciliation

```yaml
run_date: 2026-07-28
claude_run_timestamp_utc: 2026-07-28T18:49:39.660Z
source_mode: STANDALONE_OTA
reference_data_ping_used_by_chatgpt: run_7bd29842dd8b446781ea8a7f25c11d1a
branch: agent/task-20260728-claude-ota-standalone-reconciliation
```

## Completed

- archived the standalone Claude OTA source record;
- reconciled all seven supplied items against the current DATA PING and source-authority rules;
- verified Farside table semantics and missing-row behavior against official current pages;
- verified the July 28-29 FOMC meeting and July 29 statement time against the Federal Reserve's official calendar;
- withdrew the false AUM-normalized ETF feature and ratified a denominator-lineage rule;
- retained BTC 20-session ETF flow as a challenger pending row-level replay inputs;
- retained the ETH/BTC sequence as direct UTC shadow evidence only;
- preserved UTC versus Copenhagen settlement separation;
- updated the Farside timing hypothesis ledger from one to two observations;
- preserved closed experiment scores and no-retrigger rules.

## Adjudication summary

```yaml
standalone_contract: PASS
context_boundary: PASS
R_01_false_AUM_denominator: ACCEPTED_CORRECTION
R_02_BTC_20_session_ETF_sum: CHALLENGER_PARTIAL_REPLAYABILITY
R_03_ETHBTC_sequence: DIRECT_UTC_SHADOW_ONLY
R_04_dash_vs_zero: ACCEPTED_SOURCE_QA_RULE
R_05_edge_rule: FALSIFIED
R_05_after_1600Z: PROSPECTIVE_TEST_2_OF_10
R_06_post_window_stress: DESIGN_ONLY_NO_RESCORE
R_07_self_correction: PASS
FOMC_event: PRIMARY_SOURCE_VERIFIED
```

## Explicit non-actions

- no closed experiment rescored;
- no H7 row created before maturity;
- no UTC daily row used to score a Copenhagen-settled gate;
- no true AUM inferred;
- no canonical market-state change;
- no portfolio action.
