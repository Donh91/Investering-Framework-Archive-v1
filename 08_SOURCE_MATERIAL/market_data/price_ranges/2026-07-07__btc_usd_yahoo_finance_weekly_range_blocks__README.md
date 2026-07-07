# BTC-USD Yahoo Finance Weekly Range Blocks

Date added: 2026-07-07
Status: PARTIAL_GITHUB_INGEST_BACKTEST_READY_LOCAL_PACKAGE
Source input: 7 uploaded Yahoo Finance BTC-USD PDF exports
Storage path: 08_SOURCE_MATERIAL/market_data/price_ranges/

## GitHub ingest status

Confirmed in GitHub:
- README / QA note
- 2026 weekly range-block CSV

Prepared but not fully uploaded through connector in this run:
- 2020 weekly range-block CSV
- 2021 weekly range-block CSV
- 2022 weekly range-block CSV
- 2023 weekly range-block CSV
- 2024 weekly range-block CSV
- 2025 weekly range-block CSV
- combined 2020-2026 weekly range-block CSV
- daily deduplicated OHLCV CSV
- simple weekly actual ranges CSV

Reason:
The GitHub connector accepts direct text content, but does not ingest local mounted file paths as file uploads. A path test confirmed that passing a local file path writes the path string, not the file contents. Therefore the full local package remains archive-ready, but only the small direct-text uploads were permanently written in this run.

## Local extraction result

Daily extraction summary:
- Raw rows from PDFs: 2919
- Unique daily rows after deduplication: 2263
- Coverage: 2020-04-04 to 2026-06-14
- Missing calendar days: 0
- Duplicate-date conflicts: 0
- QA status: PASS

Weekly range-block summary:
- Weekly rows: 324
- Coverage: 2020-W14 to 2026-W24
- Week model: ISO week, Monday to Sunday
- Split: one CSV per ISO year

## Purpose

Historical weekly high-low and intra-week range blocks for future range evaluation and replay work.

## Boundary

Historical data only. This is source material for backtest and calibration, not a trading signal or framework promotion.
