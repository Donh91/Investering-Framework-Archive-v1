# Hindsight Violation Report — P1b Gate Window Partial Replay

Date: 2026-07-07  
Status: PASS_WITH_LIMITS

## Result

No confirmed hindsight violation in the generated market-only replay rows.

## Limits

- This is a counterfactual application of current ratified rules to historical data.
- It is not an actual historical DATA PING state replay because full DATA PING rows are missing.
- Future OHLC/returns are only used in outcome columns.
- ETF rows are taken from the P1b finalized ETF file through 2026-07-02; no 06 Jul placeholder issue is included in this replay window.

## Data missing labels preserved

- DATA_PING_ROWS_FULL_WINDOW
- BREADTH_LEDGER
- BTCD_LEDGER
- STABLECOIN_OFFICIAL_LEDGER
- FUNDING_OI_LEDGER
- ETHBTC_DAILY_FULL

## Governance conclusion

Rows are usable for mechanical v0.2/ETF/FNP scaffolding only.

They are not sufficient to ratify:

- full framework behavior
- rebuy
- recovery
- rotation
- portfolio action

Hindsight status remains PASS_WITH_LIMITS, not full replay proof.
