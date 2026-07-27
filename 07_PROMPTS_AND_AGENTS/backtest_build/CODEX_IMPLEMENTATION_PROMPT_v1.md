# CODEX IMPLEMENTATION PROMPT — BACKTEST ENGINE v1

## ROLE

You are Codex working inside `Donh91/Investering-Framework-Archive-v1`.

Implement the engineering foundation for `FRAMEWORK_BACKTEST_READINESS_BUILD_v1` exactly as specified by the frozen architecture contracts. This is an implementation task, not a market-analysis task.

## REQUIRED INPUTS

Read first:

- `04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/architecture/BACKTEST_ARCHITECTURE_CONSTITUTION_v1.md`
- `OWNER_DATASET_REGISTRY_v1.json`
- `READINESS_GATE_v2.json`
- `TEST_MATRIX_v1.json`
- `GRAPH_ANALYSIS_SPEC_v1.md`
- `DUAL_MODEL_REPLICATION_PROTOCOL_v1.md`
- `ADJUDICATION_AND_PROMOTION_POLICY_v1.md`

## BRANCH

Create and work only on:

`agent/backtest-engine-foundation-v1`

Do not write directly to main.

## IMPLEMENTATION SCOPE

Create:

```text
backtest_engine/
  __init__.py
  contracts/
  io/
  point_in_time/
  validation/
  fixtures/
  cli/
tests/backtest_engine/
.github/workflows/backtest-readiness-manual.yml
```

Implement only the engineering and readiness layer:

1. package identity and checksum validator;
2. owner-registry validator;
3. composite-primary-key validator;
4. temporal contract validator;
5. settlement and timezone validator;
6. direct/derived authority validator;
7. venue and market-type separation validator;
8. weekend/holiday ETF absence validator;
9. continuation/resume validator interface;
10. deterministic W30 fixture replay interface;
11. run-manifest and checksum writer;
12. failure reason-code registry.

## TEMPORAL CONTRACT

Required relation:

`knowledge_at_utc <= decision_at_utc <= execution_at_utc < label_end_utc`

Create positive and negative fixtures for:

- same-day ETF flow before close;
- monthly FRED before month-end;
- annual FRED before year-end;
- ALFRED initial release;
- 2M bar before settlement;
- in-progress candle;
- CEST and UTC settlement;
- future breadth membership;
- forward-filled ETF calendar days.

## AUTHORITY CONTRACT

The validator must reject:

- derived ETH/BTC in direct gate tests;
- cross-divided high/low as traded extrema;
- spot/swap/index silent substitution;
- cross-venue derivatives aggregation without a declared method;
- reconstructed TechDev data labelled as vendor data.

## TESTS

Use Python standard library where possible. All tests must be deterministic.

Required tests:

- valid registry passes;
- duplicate owner for one metric/test fails;
- blocked dataset referenced as owner fails;
- invalid temporal order fails;
- ETF weekend zero fails;
- direct-gate/derived-source combination fails;
- venue substitution fails;
- composite-key false positive is avoided;
- timestamp-only duplicate rule is explicitly rejected;
- malformed manifest fails;
- missing hash fails where required;
- fixture rerun produces identical hash.

## WORKFLOW

Create a manual and PR-triggered workflow that:

- runs only when architecture, engine or engine tests change;
- uses a pinned Python version;
- runs unit tests;
- runs contract validation;
- creates a readiness artifact;
- does not fetch live market data;
- does not run economic tests;
- does not modify canonical pointers;
- has no cron schedule.

## OUTPUT

Commit:

- code;
- tests;
- fixtures;
- workflow;
- implementation README;
- engineering receipt;
- exact test output.

Open a PR with:

- changed files;
- test counts;
- pass/fail status;
- explicit statement that economic execution remains locked.

## HARD PROHIBITIONS

Do not:

- execute any package preliminary backtest script;
- implement BT01-BT15 economic tests yet;
- alter framework state;
- alter portfolio state;
- change owner selections;
- relax a frozen contract to make tests pass;
- add a schedule;
- auto-merge a failing PR.

## DONE CONDITION

```yaml
engine_foundation: IMPLEMENTED
unit_tests: PASS
contract_tests: PASS
workflow: PR_AND_MANUAL_ONLY
live_data_calls: NONE
economic_backtests: NONE
readiness_gate_G20: NO
```
