# DATA PING source record — run_f6dc99c81a9d410db226a70e9f678ee5

- snapshot_utc: `2026-08-05T12:26:16.969Z`
- snapshot_copenhagen: `2026-08-05 14:26:16.969 CEST`
- collector_version: `15.2.0`
- collection_status: `PARTIAL`
- packet_sha256: `a6518839af60a526b70b820fdc7627e2516452fbb5769a82aca92aea63261f65`
- planned_core_actions: 60
- attempted_core_actions: 60
- core PASS/PARTIAL/STALE: 55/4/1
- validator: PASS, failed checks 0
- freeze_count: 1
- post_freeze_call_count: 0

## Current direct market

| instrument | value | 24h |
|---|---:|---:|
| BTCUSDT | 64,476.94 | +1.017% |
| ETHUSDT | 1,879.16 | +0.432% |
| ETHBTC | 0.02915 | -0.580% |

## Current derivatives

| venue | asset | mark | index | funding | open interest |
|---|---|---:|---:|---:|---:|
| Binance | BTC | 64,433.8347 | 64,459.0100 | 0.00003826 | 107,116.602 BTC |
| Binance | ETH | 1,879.6800 | 1,880.2630 | 0.00000738 | 2,327,675.836 ETH |
| OKX | BTC | 64,348.1000 | 64,429.3000 | 0.0000592279 | $2.012096B |
| OKX | ETH | 1,879.3600 | 1,880.3600 | 0.0000012798 | $1.340297B |

## Flow and positioning

- Spot taker-buy shares BTC 1h/4h/12h: `0.485441 / 0.450270 / 0.504956`
- Spot taker-buy shares ETH 1h/4h/12h: `0.614854 / 0.568534 / 0.505924`
- Spot taker-buy shares ETHBTC 1h/4h/12h: `0.234616 / 0.340705 / 0.357985`
- Futures taker buy/sell BTC: `1.0023`
- Futures taker buy/sell ETH: `1.0938`
- Global long/short BTC: `1.31`
- Global long/short ETH: `2.3445`
- Top-position long/short BTC: `1.5026`
- Top-position long/short ETH: `1.4842`

## Returns

| instrument | 1h | 4h | 12h | 24h | 48h |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | +0.0204% | -0.1383% | -0.0488% | +0.9496% | +0.9689% |
| ETHUSDT | +0.0321% | -0.1752% | -0.0439% | +0.4679% | -0.9585% |
| ETHBTC | 0.0000% | -0.0685% | -0.0343% | -0.4777% | -1.9166% |

## Breadth

- transform: `COINGECKO_TOP100_FILTERED_v3`
- supplied filter: `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`
- included: 89
- advancers/decliners/unchanged: `35/41/13`
- advance ratio: `0.39325842697`
- median 24h return: `0.0%`
- equal-weight mean: `-0.0730337%`
- membership hash: `067fbefec92e2c5b1c40625e94958321e1b64f54fab612ea4f4df2b0c9304f6c`
- scoring permission: NOT AUTHORIZED; locked owner remains v1.1.

## ETF and sentiment

- ETH ETF 2026-08-04: `+$53.1M`, current run PASS.
- BTC ETF: current parse PARTIAL and not usable; no current-run value.
- Prior independently verified latest settled BTC ETF session is not copied into this packet.
- CFGI global: 46 Neutral, current.
- CFGI ETH: 49 Neutral, current.
- CFGI BTC: 46 Neutral, stale and excluded from current-state scoring.

## Source gaps

- BTC ETF latest value unresolved in this retrieval.
- Stablecoin global total unresolved after registered fallbacks.
- 24h/72h/168h realized volatility unavailable due insufficient settled candles.
- DTWEXBGS four-observation delta unavailable.
- Optional DeFi total not resolved.
- GeckoTerminal has two low-reserve anomalies and is diagnostic only.

## Authority boundary

This is a collector packet. It contains no framework interpretation, canonical promotion, portfolio action or automatic model-weight change. The full transport payload is not duplicated in the repository; the supplied canonical packet hash, receipts and this relevance-preserving record provide lineage.