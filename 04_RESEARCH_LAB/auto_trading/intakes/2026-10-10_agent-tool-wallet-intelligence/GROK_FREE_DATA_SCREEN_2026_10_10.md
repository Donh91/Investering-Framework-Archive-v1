# Free Crypto Data Stack: source screen (2026-10-10)

Status: RESEARCH ONLY. Parent PR #1558. Source: owner-supplied Grok list, plus direct official docs and current repository source search. Free-tier claims are not authority for a live source.

## What we already own
- DefiLlama historical stablecoins: scripts/data_terminal/defillama_stablecoin_owner.py; Historical Research Vault reuses owner.
- CoinGecko API and KEYLESS public MCP recovery: research/api_agent/mcp/COINGECKO_MCP_RESEARCH_RECOVERY_v1.json; existing Data Ping.
- Binance public spot: scripts/data_terminal/binance_spot_owner_collector.py and forecast source owners.
- Blockscout/SQD: current exact-chain provenance and bounded on-chain replay.
- Deep Research skills and connector discipline: adding another generic MCP framework would duplicate ownership.

## Worth testing
1. BASIS DESK, source https://basisdesk.news/developers
   Free no-key read-only remote MCP: news search, article retrieval, market snapshot, whale transfers, token safety, daily brief. News is AI-generated with linked primary sources; token safety comes from GoPlus and some prices from existing aggregators. Compare an isolated sample against existing official-source news and native-chain receipts. Measure availability, latency, primary-citation correctness and incremental event coverage, with same-time controls. Do not mistake another facade over CoinGecko or GoPlus for independent evidence.
2. COINPAPRIKA, source https://coinpaprika.com/api/pricing/
   Free 20,000 calls/month, only 2,000 assets and limited daily history; up to 10 minute updates; website indicates personal/non-commercial free use. New possible read-only independent pricing crosscheck for BTC/ETH and select liquid alts, not reliable coverage for microcaps or intraday. Verify licensing and provider independence before archiving or publishing results. Test against existing CoinGecko, OKX and Binance owners; reject if no incremental value.

## Watch or reject
- mempool.space: public BTC fee/transaction data, rate-limited; useful only if a specific BTC mempool-cost evidence gap arises. No new collector without gap.
- web3-research-mcp (aaronjmars): MIT local Node MCP wrapping CoinGecko, DefiLlama and research/search. Existing deep research and native source adapters already cover its core functions. Do not install; possible reference for exact token-ID ambiguity and venue listing contracts only.
- Etherscan/Basescan and Dune/Arkham free access: evaluate only for exact uncovered chain and evidence family. SQD and Blockscout are already owners.
- Claude/Grok/NotebookLM/Perplexity/Gemini service tiers: user-supplied price limits are unverified and change; no separate standing agents or subscriptions justified.

## Decision
Two bounded shadow challengers: Basis Desk source-recovery and CoinPaprika price-crosscheck. Both must produce point-in-time, provider-aware incremental proof or CLEAN_NOOP. No code, runtime connectors, schedules, source weights, portfolio or trading changes.

Primary docs: https://www.coingecko.com/en/api/pricing ; https://defillama.com/subscription ; https://github.com/aaronjmars/web3-research-mcp ; https://mempool.space/docs/api . Native DefiLlama MCP is a Pro benefit, while free direct endpoints are separately available.
