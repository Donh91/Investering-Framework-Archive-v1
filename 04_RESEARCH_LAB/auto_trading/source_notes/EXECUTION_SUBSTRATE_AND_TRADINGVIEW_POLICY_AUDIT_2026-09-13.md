# Execution Substrate + TradingView Policy Audit — 2026-09-13

Status: RESEARCH_ONLY / NON_EXECUTION / NO_NEW_AUTHORITY
Owner: `04_RESEARCH_LAB/auto_trading/`
Purpose: reconcile the 2026-09-13 external source bundle against current AUTO_TRADING state and preserve only incremental value.

## Executive decision

The external bundle is directionally strong and mostly confirms work already present on current `main`.

The most important incremental conclusion is not a new agent architecture. It is an execution/data separation rule:

`official/licensed data -> strategy/research agent -> deterministic risk gate -> paper/dry-run -> deterministic execution adapter -> live only after governed promotion`

Do not use TradingView-derived market data or UI scraping as an AUTO_TRADING machine data layer.

Existing authoritative posture remains:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

This note does not activate an exchange, broker, API key, paper bot or live bot.

## 1. Mathieu2301/TradingView-API — REJECT for AUTO_TRADING data/execution

Source repo: https://github.com/Mathieu2301/TradingView-API
Official TradingView policy: https://www.tradingview.com/policies/
Official TradingView API support note: https://www.tradingview.com/support/solutions/43000474413-i-need-access-to-your-api-in-order-to-get-data-or-indicator-values/
Official TradingView suspicious-activity/automation warning: https://www.tradingview.com/support/solutions/43000674726-why-is-my-account-banned-due-to-suspicious-activity/

Observed upstream repo characteristics:
- unofficial JavaScript library exposing realtime TradingView prices/indicator values;
- claims premium/invite-only indicator access, realtime values, replay, drawings and automated strategy backtesting;
- explicitly advertises trading-bot and automated backtest use cases;
- approximately 4.4k GitHub stars at review time;
- no framework-relevant verified live-alpha evidence identified.

Official TradingView policy is decisive for this use case:
- TradingView states market data/content is display-only;
- non-display usage explicitly includes automated trading, automated order generation, algorithmic decision-making, price referencing, order verification, smart routing and machine risk/control processes;
- TradingView states it does not currently provide a public API for data/indicator values, while its REST API is for brokers integrating with the platform;
- automated data collection, scraping, scripts, bots and extraction can trigger temporary and eventually permanent bans.

Decision:

`REJECT / NO_DATA_AUTHORITY / NO_EXECUTION / NO_AUTOMATED_RESEARCH_DEPENDENCY`

The repo may remain an external technical curiosity only. Do not install it into AUTO_TRADING, do not use its data for backtests, and do not build a bot dependency around TradingView session/WebSocket internals.

This confirms and strengthens the already-closed `TRADINGVIEW_MCP_RESEARCH_QUEUE.md` lane. No re-open condition is met.

## 2. Data layer — prefer official exchange/broker/licensed feeds

Preferred principle:

`direct venue/broker/provider API > unofficial UI/session scrape`

Crypto candidates:
- exchange-native APIs where available;
- CCXT as a normalized integration reference/adapter candidate;
- existing approved framework data owners remain authoritative until a proven gap exists.

CCXT reference: https://github.com/ccxt/ccxt

Relevant properties:
- unified public/private REST APIs across many exchanges;
- WebSocket support through CCXT Pro;
- market data, order books, trades, OHLCV, balances and orders;
- exchange credentials remain venue-owned and must remain least-privilege;
- useful as adapter/reference infrastructure, not as alpha evidence.

Traditional/cross-asset candidates should use broker/provider APIs with explicit terms, e.g. Alpaca or licensed market-data providers, only when the framework actually needs those markets.

## 3. Execution substrate comparison

### A. Freqtrade — strongest near-term benchmark for crypto directional strategy workflow

Repo: https://github.com/freqtrade/freqtrade
Docs: https://www.freqtrade.io

Strengths:
- mature crypto-native backtest -> dry-run -> live workflow;
- active since 2017 and actively maintained;
- official exchange API connectivity across major venues;
- dry-run forward testing is a first-class mode;
- explicit `lookahead-analysis` and `recursive-analysis` diagnostics;
- fees included in backtest accounting;
- FreqAI adds adaptive ML research, but is not evidence of edge by itself.

Framework fit:
- high-value benchmark for strategy packaging, dry-run semantics, bias diagnostics and operational bot lifecycle;
- especially relevant if the first surviving strategy family is candle/timeframe-based crypto directional trading.

Caution:
- integrated optimization can amplify search bias if trial accounting is weak;
- candle backtests do not prove fill realism;
- do not make FreqAI or hyperopt a self-promoting research loop.

Disposition:

`BENCHMARK / POTENTIAL_COMPONENT_LATER`

### B. Lumibot — strongest supplied cross-asset + built-in agent runtime reference

Repo: https://github.com/Lumiwealth/lumibot
Docs: https://lumibot.lumiwealth.com

Strengths:
- same strategy code can run in backtest, paper/live broker contexts;
- built-in AI-agent runtime inside the strategy loop;
- explicit read-only researcher/bull/bear roles and trade-capable final agent patterns;
- supports stocks/options/crypto/futures/forex and broker integrations.

Framework fit:
- strong benchmark for one-code-path semantics and agent-to-order plumbing;
- useful if future scope expands beyond crypto or if we want a reference implementation where agents are already integrated in the backtest loop.

Caution:
- built-in examples are demonstrations, not validated alpha;
- direct trade-capable LLM agents conflict with our preferred authority split unless deterministic risk/order gates remain external and binding.

Disposition:

`BENCHMARK / POTENTIAL_COMPONENT_LATER`

### C. Hummingbot — strongest supplied crypto execution/connectors reference, especially CEX/DEX and market making

Repo: https://github.com/hummingbot/hummingbot
Docs: https://hummingbot.org

Strengths:
- standardized CLOB and DEX/Gateway connectors;
- paper trading;
- Strategy V2 Controllers/Executors;
- order lifecycle, WebSocket/REST, rate-limit and connector-maintenance patterns;
- strong fit for multi-venue, market-making, liquidity and DEX execution research.

Framework fit:
- more compelling than Freqtrade if the surviving strategy requires order-book events, multi-venue execution, market making, DEX routing or liquidity provision;
- useful source for connector abstraction and execution state machines.

Caution:
- broader credential/order authority surface;
- more operational complexity than needed for a simple directional candle strategy.

Disposition:

`BENCHMARK / POTENTIAL_COMPONENT_LATER`

### D. NautilusTrader — highest-fidelity future execution/simulation benchmark

Repo: https://github.com/nautechsystems/nautilus_trader
Docs: https://nautilustrader.io/docs/

Strengths:
- production-grade event-driven engine;
- same strategy/execution algorithm code across backtest and live;
- deterministic simulation, portfolio/risk and live execution architecture;
- multi-asset/multi-venue, fine event-time semantics and adapter model.

Framework fit:
- best late-stage benchmark when a strategy has survived scientific gates and execution realism becomes the bottleneck;
- particularly relevant for order-book/microstructure, latency/fill sensitivity or complex multi-venue strategies.

Caution:
- highest integration/operational burden of this shortlist;
- unnecessary before signal families survive leakage, multiple-testing and frozen-forward validation.

Disposition:

`VERY_HIGH_VALUE_BENCHMARK / DEFERRED_COMPONENT_CANDIDATE`

## 4. Agent architecture worth borrowing, not copying

### virattt/ai-hedge-fund

Preserve:
- fund/strategy/analyst decomposition;
- allocator separate from strategy sleeves;
- master risk above strategy proposals;
- one pipeline concept across research/backtest/paper/live;
- persistent ledger/book concept;
- deterministic risk/execution outside the LLM.

Do not preserve as evidence:
- famous-investor personas as alpha;
- educational/demo performance;
- aspirational self-improvement claims without sealed validation.

### TauricResearch/TradingAgents

Preserve:
- specialist analysts;
- bull/bear adversarial debate as a testable reasoning pattern;
- portfolio/risk review separated from initial analysis;
- persistent decision log/checkpoint recovery;
- recent point-in-time/look-ahead fixes as negative learning examples.

Do not preserve as evidence:
- paper/simulated returns as proof of live edge;
- debate complexity unless ablation shows incremental value over a single researcher + sealed validator.

Current framework mapping remains Q4 in `VELES_QUANT_LAYER_RESEARCH_QUEUE.md`.

## 5. Practical stack hypothesis for THIS framework

Not a deployment decision. Candidate sequence only:

`existing official/PIT-safe data owners`
`-> Astra/Research Lab generates CandidateSpec`
`-> sealed independent validator`
`-> deterministic risk decision`
`-> current simulator / cheap screening`
`-> execution-substrate benchmark`
`-> frozen forward Shadow`
`-> paper/dry-run on official venue/broker API`
`-> independent reconciliation + kill switch`
`-> only then governed live candidate`

Execution substrate selection should be strategy-dependent:

- directional crypto / candle-based -> benchmark Freqtrade first;
- DEX/CEX market making / order-book / liquidity -> benchmark Hummingbot first;
- cross-asset + embedded agent-loop comparison -> benchmark Lumibot;
- microstructure/high-fidelity/event-driven survivor -> benchmark NautilusTrader.

Do not select a universal engine before a surviving strategy family tells us what execution semantics are required.

## 6. Ten-step implementation order

1. Keep TradingView automation/scraping lanes closed.
2. Freeze official/licensed data contracts and timestamps.
3. Complete leakage detector + planted defect pack.
4. Complete monotonic trial accounting / multiple-testing ledger.
5. Produce candidate strategies only through frozen specs.
6. Run canonical backtest/simulation with explicit fees/slippage and deterministic risk gates.
7. Require sealed OOS / walk-forward / frozen-forward evidence.
8. Benchmark only the execution substrate matching the surviving strategy family.
9. Run paper/dry-run for a meaningful forward period with reconciliation, failure receipts and external kill switch.
10. Consider live authority only through a separate governed promotion, with least-privilege keys, capital caps and no LLM ability to override risk/execution gates.

## 7. Proven infrastructure vs unverified AI claims

### Proven as infrastructure capability

This label means the software demonstrably implements the plumbing. It does NOT mean the software produces alpha.

- Freqtrade: crypto bot lifecycle, backtesting, dry-run/live, diagnostics, exchange connectivity.
- Hummingbot: CEX/DEX connectors, order lifecycle, strategy controllers/executors, paper trading.
- Lumibot: strategy/backtest/live broker framework and built-in agent runtime.
- NautilusTrader: production-grade event-driven backtest/live execution architecture.
- CCXT: normalized exchange API adapter library.

### Useful research/agent architecture, edge unproven

- virattt/ai-hedge-fund;
- TauricResearch/TradingAgents;
- HKUDS/AI-Trader;
- swarm-trader and similar role/persona-agent projects.

### Research-only specialized ML/RL reference

- FinRL: valuable reinforcement-learning research ecosystem, but not evidence that RL strategies generalize live without independent controls.

### Reject for machine AUTO_TRADING data dependency

- Mathieu2301/TradingView-API;
- previously reviewed TradingView MCP automation lane.

## 8. Lower-value context links

Third-party comparison/blog/social pages in the source bundle are useful for discovery only. They are not used as evidence when official docs, source code or repository state are available.

GitHub stars, X distribution, YouTube views and backtest screenshots are not alpha evidence.

## Final framework verdict

The external bundle confirms the current direction rather than requiring a redesign.

Highest incremental value:
1. make the TradingView rejection explicit at policy level;
2. add Freqtrade as first crypto-directional execution benchmark;
3. retain Hummingbot for market-making/DEX execution, Lumibot for cross-asset/agent parity, NautilusTrader for late-stage high-fidelity validation;
4. keep all agents upstream of deterministic risk and execution authority;
5. do not spend engineering effort on live execution until Q1-Q4 scientific gates produce a survivor.

No Core change. No broker/API installation. No live or paper deployment created by this note.
