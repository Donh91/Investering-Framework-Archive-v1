# BTC/ETH ETF 2026-08-06 — candidate reconciliation

## Status

`COMPLETE_ROW_CANDIDATE_PROVENANCE_INCOMPLETE_NOT_OWNER_GRADE`

The user-supplied structured result contains complete numeric issuer rows for both BTC and ETH for 2026-08-06 and both rows tie exactly to the supplied displayed totals:

- BTC: `+137.6M USD`
- ETH: `+92.1M USD`

These values match the pre-existing conflict-detection candidates in request `DP-ETF-DIRECT-OWNER-20260807-02` and contain zero dash/unknown issuer cells.

However, the supplied result does not contain the owner-contract provenance required by the targeted request: two retrievals >=60 seconds apart, exact retrieval timestamps, page-generation freshness evidence, argument/payload/row hashes, freeze evidence and packet hash. Therefore owner nomination remains `NO` and the authoritative ETF owner remains through 2026-08-05.

## Diagnostic synchronized rolling sums through 2026-08-06

These are reproducible from the supplied structured rows but are **not owner-ledger sums** until 2026-08-06 itself receives owner-grade validation.

### 3 sessions

Constituents: 2026-08-04, 2026-08-05, 2026-08-06

- BTC: `211.5 + 244.4 + 137.6 = 593.5M`
- ETH: `53.1 + 60.8 + 92.1 = 206.0M`
- BTC minus ETH: `+387.5M`

### 5 sessions

Constituents: 2026-07-31, 2026-08-03, 2026-08-04, 2026-08-05, 2026-08-06

- BTC: `-265.4 + 170.1 + 211.5 + 244.4 + 137.6 = 498.2M`
- ETH: `9.0 - 11.9 + 53.1 + 60.8 + 92.1 = 203.1M`
- BTC minus ETH: `+295.1M`

### 7 sessions

Constituents: 2026-07-29, 2026-07-30, 2026-07-31, 2026-08-03, 2026-08-04, 2026-08-05, 2026-08-06

- BTC: `32.1 + 233.1 - 265.4 + 170.1 + 211.5 + 244.4 + 137.6 = 763.4M`
- ETH: `-32.9 + 12.8 + 9.0 - 11.9 + 53.1 + 60.8 + 92.1 = 183.0M`
- BTC minus ETH: `+580.4M`

## Cross-asset correction to Claude OTA R-57

The earlier Claude OTA correctly disclosed that its BTC and ETH rolling windows were not synchronized. With candidate rows now synchronized through the same 2026-08-06 session, the claim that ETH 5- and 7-session absolute-dollar flow exceeded BTC is **superseded**. BTC exceeds ETH in all synchronized 3/5/7 windows.

This does **not** restore the earlier anti-transmission label. Both assets show positive multi-session ETF absorption and the 2026-08-06 same-session candidate is dual-positive. The appropriate diagnostic description is:

`STRONG_DUAL_POSITIVE_ETF_ABSORPTION_WITH_BTC_ABSOLUTE_DOLLAR_DOMINANCE_AND_RELATIVELY_STRONG_ETH_PARTICIPATION_NOT_ROTATION_CONFIRMATION`

Same-session 2026-08-06 spread is `BTC +45.5M` over ETH. ETH is about 40.1% of combined BTC+ETH flow for the session. BTC flow is heavily IBIT-led (`128.3M` of `137.6M`); ETH is heavily ETHA-led (`81.1M` of `92.1M`). AUM-normalized comparison remains blocked.

## Framework effect

- ETF owner advance: `NO`
- canonical market state change: `NONE`
- portfolio action: `NONE`
- rotation: `NO_CHANGE_NO_ROTATION`
- research escalation: `NO`
- next required event: complete `DP-ETF-DIRECT-OWNER-20260807-02` provenance requirements or obtain equivalent owner-grade direct validation.
