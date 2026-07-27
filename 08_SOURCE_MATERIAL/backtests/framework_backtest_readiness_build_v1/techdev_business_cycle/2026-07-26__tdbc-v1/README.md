# BACKTEST BUILD source index — TDBC v1 TechDev Business Cycle

**Collection state:** `ACTIVE`  
**Test execution:** `LOCKED`  
**Source role:** Claude research package, adversarial audit and candidate-method specification.

## Source identity

| Artifact | Bytes | SHA-256 | Repository materialization |
|---|---:|---|---|
| `TDBC v1 TechDev Business Cycle 2026-07-26.zip` | 237,291 | `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c` | pending final source-batch materialization |
| `TechDev_52_2026-07-26_1538UTC.jpeg` | 152,750 | `5b9691af6456ae1148eac7c42897a757c67fa326ca83a0b0875d17850a31af51` | previously hash-indexed; current copy identity matches |

The ZIP has 18 members and 786,311 uncompressed bytes. Its checksum ledger contains 17 entries and every entry independently matches.

## Inventory

```text
TDBC_v1/
├── README_MANIFEST.md
├── SHA256SUMS.md
├── 01_report/
│   └── TDBC_REVERSE_ENGINEERING_OG_BACKTEST_v1.md
├── 02_code/
│   └── TDBC_INDICATOR_SPEC_v1.py
├── 03_rows/
│   ├── TDBC_CROSS_DISCRIMINATOR_v1.csv
│   ├── TDBC_EVENT_FORWARD_RETURNS_v1.csv
│   ├── TDBC_HISTOGRAM_SERIES_2M_2000_2026.csv
│   └── TDBC_PREREGISTERED_FALSIFIERS_v1.csv
├── 04_raw_data/
│   ├── PCOPPUSDM.csv
│   ├── btc_daily.csv
│   ├── copper_daily.csv
│   ├── eth_daily.csv
│   ├── gold_daily.csv
│   └── gold_lbma_monthly.csv
└── 05_prior_run_replication/
    ├── TDBC_EVENT_ROWS_v1.csv
    ├── TDBC_INDICATOR_2M_CUAU_MACD_FULL.csv
    ├── TDBC_PHASE_ROWS_v1.csv
    └── TDBC_SENSITIVITY_GRID_v1.csv
```

## Accepted source-level observations

- The package contains a concrete candidate reconstruction for the TechDev 2-month Copper/Gold MACD histogram.
- Existing TechDev archive material independently confirms that the chart uses a 2-month Copper/Gold MACD histogram and a separate 2-month RSI.
- The package's exact `12/26/9`, anchor and ticker implementation remain candidate specifications until framework-owned reproduction.
- The final positive bar is explicitly in progress and must not be treated as settled.
- The package includes a prior-run replication chain with rounding-level parity to the current rows.

## Reproducibility boundary

The included Python script reconstructs the indicator from live Yahoo downloads. It does not currently:

- run from the packaged local raw tables;
- pin dependencies;
- reproduce the full event study;
- reproduce the bootstrap;
- reproduce the source-B comparison;
- reproduce the confound and transmission tables.

Therefore this source is preserved as:

```yaml
source_package: ACCEPTED
indicator_candidate: HIGH_VALUE
full_replay_package: NOT_READY
canonical_sensor: NO
falsifiers: UNRATIFIED
backtest_execution: LOCKED
```

See:

`04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/extensions/2026-07-26__tdbc-v1-techdev-business-cycle__audit.md`
