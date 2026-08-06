# Audit Receipt — ETF Owner Validation 2026-08-05

- Request: `DP-ETF-DIRECT-OWNER-20260806-01`
- Validation: `PASS`
- Packet SHA-256: `0a6e29f5b302e5e3fbe3c5c49a9e07df78ebcb34d3430ddbf6ec1e44afb030b1`
- Freeze UTC: `2026-08-06T09:10:31.381Z`
- Post-freeze source calls: `0`
- BTC owner total: `+244.4M USD`
- ETH owner total: `+60.8M USD`
- Two retrievals: identical, 99.012 seconds apart
- BTC row SHA-256: `0649d4353ecf8cf53ba874f4ef5a921881835d02aa41bb12ea99dbb9e5328a2e`
- ETH row SHA-256: `0eae40ac42c1402b332f2ba30097ab069c1dc49488bbff6b6cadc538d926b768`
- Invocation-receipt bijection: `PASS`
- Owner nomination: `YES` for both assets
- Earlier `+2.8M / 0.0M` candidates: permanently rejected non-owner values
- Parser signature: tenth fund field selected instead of Total
- Parser remediation issue: `#318`
- Full runtime hash-integrity issue remains: `#317`
- Canonical state change: `NONE`
- Portfolio effect: `NONE`
- Research escalation: `RESOLVED_NO_FURTHER_RESEARCH_NOW`

## Files

- `08_SOURCE_MATERIAL/etf/2026-08-06__btc-eth-etf-2026-08-05-owner-validation.json`
- `09_SOURCE_QA/etf/2026-08-06__btc-eth-etf-2026-08-05-owner-validation.json`
- `04_MARKET_LEARNING/etf/2026-08-06__btc-eth-etf-2026-08-05-owner-reconciliation.md`
- `04_MARKET_LEARNING/etf/LATEST_ETF_FLOW_STATUS_v1.json`
