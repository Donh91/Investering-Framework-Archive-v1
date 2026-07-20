# Master Monday 2026-W30 - DATA PING DERIVED RAW

run_id: MASTER_MONDAY_W30_20260720T080654Z
status: DATA_PING_DERIVED
source_resolution: ACCEPTED_LOG_RECEIPT
source_version: DATA_PING_V6
accepted_log_id: DATA_PING_V6_20260719T200033Z
source_timestamp: 2026-07-20T05:49:59.233Z
source_path: 02_DATA_PING/weekly_closeouts/accepted/2026-07-20T054959Z__master-monday-w30-final-closeout__accepted.json
source_blob_sha: 8d94f83b592a60c586639892b2ad697d19c35af6
data_quality: MEDIUM
format_test_excluded: true
recovery_checkpoint_id: DATA_PING_V5_RECOVERY_CHECKPOINT_20260719T144323Z
missing_fields: [FIXED_RISK35_v1, MARKET_WIDE_CVD, OFFICIAL_STABLECOIN_TOTAL_HISTORY, ETF_20_SESSION_WINDOW]

## Accepted actuals
- BTC W30 O/H/L/C: 63920.40 / 65600.00 / 61824.97 / 64415.75, CLV 0.6863.
- ETH W30 O/H/L/C: 1812.27 / 1946.52 / 1750.20 / 1862.12, CLV 0.5701.
- ETH/BTC W30 O/H/L/C: 0.02835 / 0.02981 / 0.02821 / 0.02891, above 0.0275 and below 0.0300.
- Farside 17 July: BTC +132.3M, IBIT +136.5M, ETH +36.7M. BTC and IBIT positive four completed sessions.
- Dynamic breadth shadow: 1H 14.08%, 24H 23.94%, 7D 40.85%, membership changed and not comparable.
- Binance spot taker: BTC 1H -14.61M, 4H -19.67M, 24H +14.63M. ETH 1H -1.93M, 4H -0.17M, 24H +2.42M.
- Futures taker ratios were below or near 1 and 24H OI fell about 0.6% for BTC and ETH.

## Deterministic derived state
- Weekly structure confirmed above BTC 63.3K and ETH/BTC 0.0275.
- Pullback warning remains active, de-escalated one level, not cleared.
- Rotation remains NO_ROTATION.
- Broad recovery remains NOT_CONFIRMED.
- Large-cap window remains WATCH_ONLY_NOT_OPEN.
- New entry signal remains NOT_ACTIVE.
- Portfolio action: NONE.

This file is operational evidence only. Final interpretation belongs to 03_framework_ratified_final.md.
