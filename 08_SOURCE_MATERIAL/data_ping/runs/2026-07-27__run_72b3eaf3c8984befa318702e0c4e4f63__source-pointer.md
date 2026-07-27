# Source pointer — DATA PING run_72b3eaf3c8984befa318702e0c4e4f63

```yaml
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
snapshot_id: snap_05a6df8461ae4bdfa72e893da17295fb
snapshot_utc: 2026-07-27T14:39:04.061Z
predecessor_snapshot_id: snap_f6488d4e57684f07b87ee148e75dc7d0
collector_status: PARTIAL
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Receipt summary

```yaml
receipt_count: 61
core_planned: 60
core_attempted: 60
core_PASS: 21
core_PARTIAL: 1
core_STALE: 3
core_FAIL: 34
core_UNAVAILABLE: 1
optional_FAIL: 1
```

## Accepted current source families

- CoinGecko global, BTC/ETH current and breadth
- FRED DGS2, DGS10, VIXCLS and DTWEXBGS
- OKX BTC and ETH ticker, mark, index, funding and OI
- BTC ETF latest settled row
- DeFiLlama chain TVL
- DeFiLlama stablecoin chain distribution only, not global total
- GeckoTerminal ETH pool sample

## Rejected or restricted source families

- Binance context: failed under geo restriction
- Binance final: failed under geo restriction
- direct ETH/BTC: unavailable
- ETH ETF: stale
- CFGI: stale or unavailable
- stablecoin global total: unavailable
- optional DeFi total TVL: response too large

## Authority boundary

This pointer preserves the pasted packet's identity and key lineage. The full chat payload is not claimed to have transport-level byte verification in GitHub.
