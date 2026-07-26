# W30 Source QA and Receipt Log

**Package QA matrix:** 90 rows in the original ZIP  
**Evidence role:** Source health, provenance, freshness and comparability  
**Status:** `COMPLETE_FOR_PACKAGE / NON_CANONICAL`

## Successful evidence families

- Multi-venue live spot crosschecks for BTC, ETH and ETH/BTC.
- Settled Binance spot kline series for price, range, taker and close calculations.
- Farside settled BTC and ETH ETF tables through 2026-07-24.
- CoinGecko global market and filtered breadth universe.
- DeFiLlama stablecoin and chain datasets.
- OKX derivatives, positioning ratios and bounded liquidation rows.
- FRED macro series and Yahoo fallbacks.
- Source-native timestamps and cross-venue freshness checks.

## Error and limitation events

### GEO_RESTRICTION

- Binance Futures API: HTTP `451`.
- Bybit: HTTP `403`.
- Consequence: derivative layer was completed on OKX, but continuity with Binance-based history is not one-to-one.

### ENDPOINT_UNAVAILABLE / challenge

- Stooq returned a JavaScript challenge.
- Yahoo was used as a fallback for selected market series.
- Fallback values must retain method and source tags.

### LOCAL_PREREGISTRATION_UNAVAILABLE

- F5 frozen text was not present in the external research container.
- H7 slope-condition frozen text was not present locally.
- Consequence: primary adjudication remains with the main framework.

### MISSING OR PARTIAL

- Per-asset BTC and ETH CFGI unavailable locally.
- Exchange stablecoin balances unavailable without a documented free endpoint or paid provider.
- Sector breadth unavailable without a reproducible category join.
- Full liquidation totals limited by OKX row caps.
- Global liquidity/M2 proxy excluded because no method was frozen.

## Freshness handling

The package distinguished:

- `LIVE`
- `SETTLED_UTC`
- `SETTLED_CEST`
- `LATEST_AVAILABLE`
- `EXPECTED_PUBLICATION_LAG`
- `MISSING`
- `GEO_BLOCKED`

Current-run freshness was supported by source timestamps, settled kline close times and cross-venue parity. FRED publication lag was not misclassified as transport failure.

## Comparability controls

- UTC and CEST close bases were kept separate.
- OKX derivatives were venue-tagged and marked non-comparable to Binance series where necessary.
- CoinGecko total-market dominance was not mixed with ex-stablecoin dominance.
- Weekend ETF dates were marked `NON_SESSION`, not zero.
- Settled Farside primary rows retained priority over provisional reports.
- Bitstamp midpoint versus lagging last trade was explicitly documented.

## Receipt integrity

Original `receipts.json` in the ZIP contains the detailed action-level receipts and payload SHA-256 values. Package-level integrity is anchored by:

- ZIP SHA-256: `9353f2fcefb9aaf38d8102dd3a4ec538fba302352178e883e1bcf0cdc6472ad8`
- PDF SHA-256: `23b0f7f9b8aa7dc0612b2f757744f934f1246dd16ea81670e0f54c06ed5cdae3`

## Quality caveats discovered during ingest

The external package is comprehensive but contains internal inconsistencies in low-vol arithmetic, Stage-1 persistence count, depeg summary and ETF leader/concentration formatting. These are routed to the dedicated conflict registry and block silent promotion of the affected fields.