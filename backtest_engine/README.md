# Framework Backtest Engine foundation

This package implements the engineering layer for `FRAMEWORK_BACKTEST_READINESS_BUILD_v1`.

It validates package identity, temporal order, source authority, composite keys, ETF session semantics, continuation behavior and the W30 deterministic golden fixture.

It does **not** run economic backtests. `READINESS_GATE_G20` remains `NO` until the corrected final master is byte-audited and every mandatory readiness gate passes.

## Commands

```bash
python -m backtest_engine audit-package /path/to/package.zip
python -m backtest_engine replay-w30 /path/to/materialized/w30_fixture
python -m backtest_engine run-engineering-gates \
  /path/to/materialized/w30_fixture \
  /path/to/DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z.zip \
  --continuation-package /path/to/FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z.zip
```

The test bundle contains the minimum W30 inputs and expected outputs required to reproduce volatility, drawdown, settled UTC daily aggregation, derived ETH/BTC bounds, ETF trailing features and BTC/ETH ETF-flow divergence.
