# AT-SRC-0006 — MMT Scripting v3 / Market Data API / MCP

Status: `RESEARCH_QUEUED`
Captured: 2026-09-11
Source type: official product/docs + social discovery
Discovery links:
- https://x.com/anthdm/status/2098094187350495339?s=46
- https://x.com/mmt_official_/status/2098093000593166456?s=46&t=SUBrcpc4yI4ppaXpURK03g
Primary official sources:
- https://docs.mmt.gg/scripting/v3
- https://mmt.gg/scripting/
- https://docs.mmt.gg/api
- https://docs.mmt.gg/api/websocket
- https://mmt.gg/mcp/
Evidence class: `INFRASTRUCTURE_AND_RESEARCH_CAPABILITY`, not signal/performance evidence.

## What is verified from official docs

MMT exposes a purpose-built statically typed scripting environment and separate market-data interfaces.

The documented data families include:
- OHLCV / candles
- individual trades / raw tape
- order-book depth
- volume delta / CVD
- open interest
- volume profile
- funding and liquidations
- order-book heatmaps
- Hyperliquid stop / take-profit / liquidation heatmaps

The WebSocket API exposes real-time trade and depth events plus higher-level streams. REST exposes historical/aggregated datasets for several feed families.

Scripting v3 declares subscriptions, typed inputs and visual outputs before execution. This is relevant because it makes indicator behavior inspectable and reproducible rather than hiding logic inside free-form AI decisions.

MMT also documents MCP support intended to let an AI agent interact with the terminal and write scripts. MMT states that MCP tokens are named/scoped and that publishing is not in scope for those tokens.

## What matters for the Investering Framework

### 1. Market microstructure as a separate feature layer

MMT is potentially valuable not as another market-state engine, but as an upstream microstructure feature provider.

Candidate features include:
- order-book imbalance by depth bucket
- spread and depth asymmetry
- trade-sweep / aggressive-flow intensity
- CVD and volume-delta divergence
- OI expansion/contraction with price
- liquidation bursts
- funding stress
- heatmap concentration / liquidity walls
- trade-rate / TPS acceleration

These should be consumed by existing research/strategy owners rather than creating a parallel regime model.

### 2. Better execution research

The strongest near-term fit is with `AT-HYP-0006` (execution quality can dominate forecast quality).

MMT data could help estimate whether a signal is actually executable under:
- spread
- visible depth
- short-horizon impact
- depth asymmetry
- liquidation-driven volatility
- liquidity withdrawal

This is potentially more valuable than inventing another directional indicator.

### 3. Agent-to-indicator compilation

Scripting v3 gives Astra a constrained target language for experiments:

`research hypothesis -> typed MMT script -> replay/forward observation -> result -> retain/revise/kill`

This is directly compatible with the existing principle that AI should compile research ideas into inspectable deterministic rules before any promotion.

### 4. Real-time-first, historical-second collection

MMT documents live raw tape access in the terminal across plans, while historical raw-trade depth is plan-dependent. The separate paid Data API provides real-time and historical data with plan-specific history windows.

Therefore the default research policy should be:
- use free/live capabilities first for prospective Shadow collection when technically sufficient;
- use existing archived data before buying duplicate historical coverage;
- only pay for MMT history where it closes a specific evidence gap that cannot be reconstructed from existing sources;
- preserve exact source/version/timestamp semantics for any purchased history.

## Do not assume

- that MMT order-flow features contain alpha merely because they are granular;
- that a visually compelling heatmap predicts direction;
- that raw tape automatically beats candle data after costs;
- that MCP-generated scripts are correct without deterministic validation;
- that product marketing speed claims imply better strategy performance;
- that MMT should replace existing Data Ping, regime, derivatives or execution owners.

## Highest-value Astra research questions

1. Does microstructure data add stable post-cost out-of-sample value beyond price/volume + Framework regime baselines?
2. Which microstructure families add unique information versus duplicate existing derivatives/order-flow sources?
3. Can MMT improve execution-risk estimation even when it adds no directional alpha?
4. Can Astra reliably compile natural-language hypotheses into typed MMT scripts with lower ambiguity and higher replay reproducibility than free-form Python/LLM logic?
5. Which features survive across venues and which are venue-specific artifacts?
6. Does multi-exchange aggregation improve robustness or dilute actionable local structure?
7. Can live Shadow collection build enough prospective history to avoid purchasing large historical datasets?

## Promotion rule

No MMT-derived feature, indicator or strategy gains trading authority from this source.

Promotion requires:
- time-valid data
- deterministic rule version
- simple baselines
- walk-forward / out-of-time survival
- realistic costs/slippage
- ablation versus existing framework features
- forward Shadow evidence
- explicit falsifier and kill criteria
