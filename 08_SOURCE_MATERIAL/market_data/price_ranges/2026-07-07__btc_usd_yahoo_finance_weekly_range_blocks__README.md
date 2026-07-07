# BTC-USD Yahoo Finance Weekly Range Blocks

Date added: 2026-07-07
Status: BACKTEST_READY_DERIVED_RANGE_DATASET
Source input: 7 uploaded Yahoo Finance BTC-USD PDF exports
Storage path: 08_SOURCE_MATERIAL/market_data/price_ranges/

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

Purpose:
Historical weekly high-low and intra-week range blocks for future range evaluation and replay work.

Boundary:
Historical data only.
