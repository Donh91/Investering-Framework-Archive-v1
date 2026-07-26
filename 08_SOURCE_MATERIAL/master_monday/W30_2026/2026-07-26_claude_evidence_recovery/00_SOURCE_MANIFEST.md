# W30 Master Monday Evidence Recovery — Source Manifest

**Package class:** `EXTERNAL_RESEARCH_EVIDENCE`  
**Evidence anchor:** 2026-07-26T12:26:13Z  
**Delivered:** 2026-07-26T12:47:00Z  
**Canonical authority:** `NONE`

## Original attachments

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `CN W30 MASTER MONDAY EVIDENCE RECOVERY 2026-07-26.zip` | 1,676,211 | `9353f2fcefb9aaf38d8102dd3a4ec538fba302352178e883e1bcf0cdc6472ad8` |
| `W30 MASTER MONDAY EVIDENCE RECOVERY.pdf` | 156,817 | `23b0f7f9b8aa7dc0612b2f757744f934f1246dd16ea81670e0f54c06ed5cdae3` |

The ZIP contains `109` files and approximately `8.69 MB` uncompressed source material.

## Root package objects

- `W30_MASTER_MONDAY_EVIDENCE_RECOVERY.md`
- `cn_raw_bridge.json`
- `receipts.json`

## Structured data objects

- `data/forecast_maturity_ledger_W30.csv`
- `data/source_qa_matrix.csv`
- `data/delta_vs_dp_snapshot.csv`
- `data/breadth_membership.csv`
- `data/etf_flows_last10_farside.csv`
- `data/settled_closes_btc.csv`
- `data/settled_closes_eth.csv`
- `data/settled_closes_ethbtc.csv`
- `data/computed_core.json`
- `data/computed_aux.json`

## Raw evidence families

The ZIP preserves source-native or near-source-native payloads covering:

- Binance BTC, ETH and ETH/BTC prices and klines.
- Kraken BTC, ETH and ETH/XBT series.
- Coinbase spot crosschecks.
- Bitstamp ETH/BTC crosscheck.
- OKX tickers, marks, indices, funding, open interest, long/short ratios, taker data and bounded liquidation rows.
- Binance Futures and Bybit error payloads documenting geo restrictions.
- CoinGecko global and market-universe payloads.
- Farside BTC and ETH HTML table captures.
- DeFiLlama stablecoins, chains and historical chain payloads.
- FRED DGS2, DGS10, T10Y2Y, VIX, broad dollar, HY OAS, NFCI, SP500, Nasdaq 100 and WTI series.
- Yahoo fallback payloads for DXY, Russell 2000, copper, gold and crude oil.
- Stooq challenge/error captures.
- Retrieval scripts, run anchor, raw manifest and error logs.

## Evidence routing

- Human-readable interpretation and longitudinal learning are routed to `04_MARKET_LEARNING/`.
- Source health, provenance and package integrity are routed to `08_SOURCE_MATERIAL/`.
- Governance write receipt is routed to `07_PROMPTS_AND_AGENTS/skill_runs/`.

## Binary materialization note

The exact ZIP and PDF were supplied as conversation attachments and are identified by cryptographic hash above. The current GitHub connector used for this ingest supports UTF-8 text writes but not direct binary attachment transfer. Therefore the raw binary containers are not duplicated into the repository in this commit.

This limitation does not change the evidence classification, but repository-local binary materialization remains `PARTIAL`. The logical evidence, integrity hashes, source inventory, QA events and conflict log are archived here.