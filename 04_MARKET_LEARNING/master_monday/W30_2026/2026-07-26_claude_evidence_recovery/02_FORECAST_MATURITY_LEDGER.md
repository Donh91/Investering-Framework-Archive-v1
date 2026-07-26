# W30 Forecast and Maturity Ledger

**Status:** `NON_CANONICAL / ADJUDICATION_OWNED_BY_MAIN_FRAMEWORK`

## F1 — death-zone durability

- Frozen truth-layer threshold: `62,200`.
- Later `62,342` refinement: provenance unresolved.
- Venue: Binance truth layer.
- Primary session basis: UTC; CEST retained as secondary evidence.
- Window: 2026-07-21 through 2026-07-27.
- Maturity: 2026-07-28T00:00:00Z.
- Package status: `5/7` settled rows.
- Settled rows in package:
  - 2026-07-21: `66,556.16`
  - 2026-07-22: `66,114.49`
  - 2026-07-23: `65,098.97`
  - 2026-07-24: `64,139.99`
  - 2026-07-25: `64,375.00`
- All five were above `62,200`.
- Score state: `WITHHELD_UNTIL_MATURITY`.
- Required evidence: settled UTC closes for 2026-07-26 and 2026-07-27.
- No interim score is permitted.

## F4 — ETH/BTC 0.0300 transmission gate

- Threshold: settled ETH/BTC close at or above `0.0300` within the ten-session window.
- Window: 2026-07-15 through 2026-07-24.
- Status: `MATURED`.
- UTC: `0/10` closes at or above threshold.
- CEST: `0/10` closes at or above threshold.
- Independent recomputation parity versus archive: `0.000` on all four comparison fields.
- Directional score: `GATE_UNMET`.
- Causal attribution: `CONFOUNDED` because F5 occurred during the window.
- No re-opening or re-trigger is permitted.

## F5

- Status: `CLOSED_TRIGGERED` around 2026-07-23.
- Frozen preregistration text was unavailable inside the Claude container.
- Authority: external adjudication by the main framework.
- Rule: must not be triggered again.

## H7 — five-row CEST close log

- Instruments: BTCUSDT, ETHUSDT and ETHBTC.
- Session basis: settled CEST close.
- Rows settled in package: `4/5`.
- Row 1, 2026-07-22:
  - BTC `66,072.47`
  - ETH `1,938.76`
  - ETH/BTC `0.02933`
- Row 2, 2026-07-23:
  - BTC `65,169.81`
  - ETH `1,882.72`
  - ETH/BTC `0.02889`
- Row 3, 2026-07-24:
  - BTC `64,155.00`
  - ETH `1,857.51`
  - ETH/BTC `0.02896`
  - Archive parity: `0.00 / 0.00`
- Row 4, 2026-07-25:
  - BTC `64,344.02`
  - ETH `1,872.65`
  - ETH/BTC `0.02910`
- Row 5 maturity: 2026-07-26T22:00:00Z.
- Frozen slope-condition text was unavailable locally.
- Final H7 adjudication remains external.

## Low-vol E12 forward observation

- Frozen anchor: 2026-07-22 UTC close.
- 5D maturity: 2026-07-28T00:00:00Z.
- Weight: `NONE_FRAGILE`; observations only.
- Internal package conflict:
  - Main report and embedded final JSON: `1D -1.54%`, `3D -2.63%`.
  - Forecast CSV, CN/RAW bridge and report footer: `1D +0.10%`, `3D -0.26%`.
- Status: `RECOMPUTE_REQUIRED_BEFORE_ADJUDICATION`.
- No version is accepted as canonical during ingest.

## Leading claim — July 14 case 2

- Kill rule: two of three cases fail twelve-session durability.
- P2 antecedent was not met because BTC ETF flows turned positive during 2026-07-15–20.
- P1 path had no settled close at or below `62,200` through package time.
- Expected maturity: approximately 2026-07-30.
- FOMC 2026-07-28–29 is a preregistered confound and must be logged separately rather than absorbed into the original claim.
- Status: `PENDING / SCORE_WITHHELD`.

## EXT-GCBLO-2026-07-24

- Status: `PENDING`.
- Maturity: 2026-10-23.

## Stage-1

- Threshold: `65,600` range-top ratification context.
- Status: `GOVERNANCE_PENDING`.
- Package conflict:
  - Main narrative reports three consecutive UTC closes below 65,600 beginning 2026-07-23.
  - Forecast CSV and handoff summary report four consecutive closes beginning 2026-07-22.
- No Stage-1 ruling is made by this ingest.

## Next maturity events recorded by the package

1. 2026-07-26T22:00:00Z — H7 row 5 / CEST close.
2. 2026-07-27T00:00:00Z — F1 row 6 UTC close.
3. 2026-07-28T00:00:00Z — F1 maturity and low-vol 5D.
4. 2026-07-29T18:00:00Z — FOMC decision/confound event.
5. Approximately 2026-07-30 — leading-claim twelve-session maturity.