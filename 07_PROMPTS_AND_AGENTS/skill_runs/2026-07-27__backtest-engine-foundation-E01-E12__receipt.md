# Skill-run receipt — Backtest Engine foundation and E01–E12

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
run_id: BACKTEST_ENGINEERING_E01_E12_20260727
branch: agent/backtest-engine-foundation-v1
run_type: ENGINE_IMPLEMENTATION_AND_ENGINEERING_REPLAY
```

## Implemented

- package SHA-256, ZIP CRC and detached-checksum audit;
- isolated manifest self-reference classification;
- direct/derived authority enforcement;
- spot/swap/index and venue substitution guards;
- point-in-time ordering validation;
- composite-key validation;
- ETF weekend and synthetic-zero rejection;
- backward continuation cursor, order and overlap checks;
- settled-only UTC daily aggregation;
- hourly volatility and drawdown builders;
- derived ETH/BTC proxy builder with explicit non-direct semantics;
- ETF trailing, streak, acceleration, reversal and concentration features;
- BTC/ETH ETF divergence;
- deterministic canonical output hashing;
- CLI and PR/manual-only CI workflow.

## Executed

- 17 local unit and red-team tests: PASS;
- W30 package CRC and 69 detached checksum checks: PASS;
- E01–E12 engineering gates: PASS 12/12;
- W30 semantic replay checks: PASS 10/10;
- deterministic repeated replay: PASS.

## Defect discovered and repaired

Initial daily replay incorrectly included an unsettled final hourly row. The golden fixture rejected the output. The builder was corrected to aggregate settled rows only, restoring the archived final-day close and 19-hour incomplete-day count.

## Explicit blocker

`DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip` was not present in the active runtime. Its summary claims are preserved, but final byte integrity is not marked PASS.

## Non-actions

```yaml
economic_backtest: NONE
parameter_search: NONE
final_holdout: NOT_TOUCHED
sensor_promotion: NONE
framework_state_change: NONE
portfolio_action: NONE
```

Result: `ENGINE_FOUNDATION_PASS_E01_E12_PASS_G20_REMAINS_NO`.
