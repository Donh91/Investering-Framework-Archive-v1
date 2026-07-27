# W31 DATA PING input index

- Run: `run_b43a7f8d213c4e63a5e60ca9cb19d764`
- Snapshot: `2026-07-27T17:10:00Z`
- Role: intraday degraded-source follow-up
- Framework classification: `ETH_TRANSMISSION_FOLLOW_THROUGH_DETERIORATING_WITH_BREADTH_CONTRACTION`

## Weekly-use constraints

- usable for CoinGecko, OKX, FRED, DeFiLlama chain TVL and GeckoTerminal observations
- not usable for direct ETH/BTC settlement
- not usable for Binance feature families
- stale BTC ETF row must not overwrite the accepted 2026-07-24 owner row
- CFGI unavailable

## Non-actions

This index does not execute Master Monday or Precision Score. It only preserves the input and governing limitations.