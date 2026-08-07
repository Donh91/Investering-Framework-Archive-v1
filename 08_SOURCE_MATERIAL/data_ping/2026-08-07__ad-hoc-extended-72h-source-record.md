# Extended DATA PING 72h — ad hoc source record — 2026-08-07

Source package: `udvidet_data_ping_72h_20260807.zip`
Package SHA-256: `f9bc11677687b9043785df131df0428097697ce3124f993d4a4fea2e4b0240ba`
Mode supplied by source: `AD_HOC_EXTENDED_DATA_ASSISTANCE`
Framework interpretation supplied by source: `DEFERRED_TO_MAIN_FRAMEWORK`
Predecessor state changed: `false`

The compact ZIP contained `methodology.txt`, `72h_summary.csv`, `funding_history.csv`, `checksums.json`, `report.json`, `current_snapshot.csv`, and `README.txt`. Internal file checksums supplied by the package:

- methodology.txt `f5c68da00e18a7ba9ec0a9ccc791f3ec1842f2911d69c24e8dc39022288312cf`
- 72h_summary.csv `edd828f392f6d3cd9813e03d41912a7989e6530f187175c2140087eb7267d53c`
- funding_history.csv `138b6493967dda4fb5441c34f810b7615d15460c249b0f30885c300c47c5a2f5`
- report.json `704a930c239ae2c12985f075eb12a210b5833a484ca5072d2f38c0d7199deb2c`
- current_snapshot.csv `9c050f36b578a325dcf9b2e1715a15bbae65b7c18e9ed5c3b8e19ab8107ec470`
- README.txt `7c3e3aaa28dff69de7f5f73fa04cde4d6251e3f45522f2c2735082130c0a4f87`

## Methodology supplied

Sources: Binance Spot, Binance USD-M Futures, CoinGecko. Window: roughly latest 72 hourly bars ending 2026-08-07. Returns = end_close/start_close-1. OI changes use first/last retrieved hourly observations. Funding stats use 10 latest settlements. No regime classification or trading action. Ad hoc run; predecessor state unchanged.

## 72h summary

| symbol | start | end | return | high | low | range | OI coin change | OI USD change | latest taker ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTCUSDT | 63950.93 | 65012.00 | +1.6592% | 65390.99 | 63880.00 | 2.3654% | -2.0685% | -0.7970% | 0.9727 |
| ETHUSDT | 1869.68 | 1916.38 | +2.4978% | 1943.02 | 1855.50 | 4.7168% | -2.1419% | -0.0189% | 0.8178 |
| ETHBTC | 0.02923 | 0.02948 | +0.8553% | 0.02975 | 0.02904 | 2.4449% | n/a | n/a | n/a |

Funding mean over supplied latest 10 settlements: BTC `0.000039836`; ETH `0.000026693`. BTC funding min/max `0.00000799 / 0.00007684`; ETH min/max `-0.00000562 / 0.00007309`.

## Current snapshot supplied

- BTCUSDT `65049.82`, 24h `+0.369%`, high `65390.99`, low `64166.0`
- ETHUSDT `1918.08`, 24h `+0.122%`, high `1943.02`, low `1894.35`
- ETHBTC `0.02949`, 24h `-0.271%`, high `0.02975`, low `0.02942`
- CoinGecko global market cap `2294895092804.127`, BTC dominance `56.7489459143%`, ETH dominance `10.0614751687%`, market-cap 24h `+0.2846919691%`, source updated_at epoch `1786115849` (= 2026-08-07T15:17:29Z).

## Funding rows preserved

BTC: 2026-08-04 08:00Z 0.00006248; 16:00Z 0.00007684; 2026-08-05 00:00Z 0.00001674; 08:00Z 0.00001015; 16:00Z 0.00002676; 2026-08-06 00:00Z 0.00006595; 08:00Z 0.00002632; 16:00Z 0.00005939; 2026-08-07 00:00Z 0.00000799; 08:00Z 0.00004574.

ETH: 2026-08-04 08:00Z 0.00005342; 16:00Z 0.00007309; 2026-08-05 00:00Z 0.00003467; 08:00Z 0.00000613; 16:00Z 0.00003054; 2026-08-06 00:00Z 0.00000394; 08:00Z 0.00000987; 16:00Z 0.00000987; 2026-08-07 00:00Z -0.00000562; 08:00Z 0.00005102.

## Source limitations

The source explicitly states that full raw 72-row arrays were queried live but are **not included** in the compact export. Therefore the endpoint summaries cannot be independently replayed row-by-row from this package. This archive accepts the package only as an extended/ad-hoc longitudinal evidence supplement; it does not become bounded owner, canonical predecessor, or portfolio authority.
