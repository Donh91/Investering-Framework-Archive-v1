# Trader.dev + AITradingArena — source note

**Date:** 2026-09-14  
**Status:** SOURCE_NOTE / RESEARCH_ONLY / NO_ALPHA_CLAIM / NO_AUTHORITY  
**Area:** agentic trading research / backtest orchestration / strategy discovery efficiency / transfer learning  
**Primary folder:** `08_SOURCE_MATERIAL/external_methods/`  
**Core impact:** NONE  
**Research Lab impact:** FUTURE RESEARCH CANDIDATE ONLY

## Sources

```yaml
trader_dev: https://trader.dev/
trader_dev_mcp: https://mcp.trader.dev/
ai_trading_arena: https://aitradingarena.com/
agent_repo: https://github.com/DaviddTech/ai-trading-agent
agent_repo_pinned_commit: fa5d9dfe9f02c281c314278edc16bb1527abc670
agent_repo_license: MIT
```

## Executive verdict

Trader.dev / AITradingArena is worth preserving because it exposes a concrete agent-native trading-research workflow that can be independently reproduced and attacked.

The value is **not** the public headline returns or the number of profitable strategies. Those remain unverified external backtest claims and carry selection, multiple-testing, execution and overfitting risk.

The durable value is the research architecture and one particularly falsifiable method claim:

```text
HARVEST EXISTING STRATEGY LOGIC + CROSS-MARKET TRANSFER + MINIMAL TUNING
may produce robust candidates more efficiently than
GREENFIELD INVENTION + HEAVY PARAMETER OPTIMISATION.
```

That claim is suitable for future independent testing against the framework's own archived strategy corpus, including the separately preserved FMZ corpus.

## Trader.dev architecture of interest

The reviewed public material describes an MCP-facing research service supporting agent workflows around:

- Pine Script strategy generation and inspection;
- backtesting on crypto pairs;
- parameter sweeps and strategy comparison;
- saved/forked strategy versions;
- multi-symbol and multi-timeframe testing;
- position/risk optimisation;
- live-signal monitoring as context, without the open agent repo itself placing orders.

The companion `DaviddTech/ai-trading-agent` repository is agent-readable and encodes workflows for new strategy research, strategy optimisation and position optimisation. Its useful discipline includes baseline preservation, one-main-change-at-a-time comparison, nearby-timeframe and multi-symbol checks, drawdown scrutiny, repaint/lookahead avoidance and explicit overfitting warnings.

These are useful implementation references, not proof that the external service produces durable edge.

## AITradingArena method worth testing

The reviewed public board states that agents share a common framework while changing signal logic, and that candidate strategies must meet minimum backtest thresholds before entering a forward-testing queue.

The most important externally reported observation is that a harvesting / pair-sweep approach discovered candidates much more efficiently than a heavily optimised approach in that factory. The site reports approximately:

```text
harvest-style lane: 15 candidates / 59 backtests
heavy optimisation lane: 4 candidates / 685 backtests
reported efficiency difference: roughly 44x
```

This is **source-reported evidence only**. It is not accepted as a framework finding and must not be treated as an established 44x advantage.

The transferable hypothesis is narrower:

```text
When compute budget is fixed, strategy-family reuse and cross-market transfer may outperform parameter-heavy search in prospective out-of-sample survivor yield.
```

## Future falsification design

If Research Lab later opens this case, use matched compute/data/risk assumptions and compare at minimum:

```text
Lane A: INVENT
AI creates new strategy logic from scratch.

Lane B: OPTIMISE
AI receives an existing strategy and is allowed broad parameter search.

Lane C: HARVEST
AI selects existing archived strategy logic and uses minimal tuning.

Lane D: TRANSFER
A selected strategy is moved substantially unchanged across instruments / nearby timeframes / eligible regimes.
```

Primary comparison should not be raw in-sample P&L.

Prefer measures such as:

```text
OOS survivors per 100 backtests
prospective survivors per 100 backtests
prospective survivors per compute-dollar or token budget
median OOS degradation
parameter-count sensitivity
cross-symbol survival
cross-timeframe survival
drawdown and tail-risk expansion
false-discovery / multiple-testing burden
```

Require realistic costs where relevant, no repaint/lookahead, frozen selection rules, independent holdout windows and explicit kill criteria.

## Critical caveats

Do not import these external claims as edge:

- public leaderboard backtests may be affected by selection and multiple testing;
- large displayed returns do not establish executable real-world performance;
- strategy correlations mean candidate count is not independent-edge count;
- external forward windows may still be short or underpowered;
- service internals and exact TradingView execution assumptions are not fully independently controlled by this framework;
- pricing / service availability can change;
- the external MCP service must never become required production infrastructure for the framework without a separate dependency and security review.

## Private disaster-recovery binding

### Agent repository

```yaml
vault_repository: Donh91/Investering-Framework-Vault
vault_path: external_sources/daviddtech-ai-trading-agent/2026-09-14/
manifest: external_sources/daviddtech-ai-trading-agent/2026-09-14/manifest.json
source_pinned_commit: fa5d9dfe9f02c281c314278edc16bb1527abc670
source_commit_count_all_refs: 13
source_ref_count: 3
source_file_count_at_pin: 45
full_history_bundle_sha256: df8e42aa55e1ba3be72f17e4ffa67d320d5732c9a32ffaf186fbf7d8819f9ef5
source_tree_sha256: fcca78cfb822fe6b7afe7d1138e8dad8af0f4f5e6b3064cc76a13e9b169f210f
restore_status: PASS
```

### Public website snapshot

```yaml
vault_path: external_sources/trader-dev-ai-trading-arena/2026-09-14/
manifest: external_sources/trader-dev-ai-trading-arena/2026-09-14/manifest.json
aggregate_receipt: receipts/2026-09-14__external-research-assets-dr-receipt.json
website_capture_status: PASS_PUBLIC_BYTES_SNAPSHOT
aitradingarena_html_sha256: e45b55f35344f64a4d2bc5283e18e8769e548a71931ffaa3f286760016454ad6
trader_dev_mcp_login_html_sha256: 67520fae09b068494156006b242475bb49a737854a987a4290fd71348385674e
trader_dev_pricing_html_sha256: f2d204369b40fc91ebee4699c579e3a63dbd7617071dbb0a4f739d5097905718
```

The website snapshot is a frozen public-byte capture for later comparison. It is not a guarantee that dynamic board state, strategy data or service behavior can be reconstructed completely from HTML alone.

## Disposition

```yaml
ARCHIVE: YES
RESEARCH_VALUE: HIGH
DIRECT_ALPHA_CLAIM: NO
DIRECT_STRATEGY_IMPORT: NO
EXTERNAL_SERVICE_DEPENDENCY: NO
CANONICAL_CHANGE: NONE
NEW_ENGINE: NONE
RESEARCH_CANDIDATE: HARVEST_VS_OPTIMISE_VS_INVENT_VS_TRANSFER
NEXT_BEST_ACTION: preserve now; later run an internally controlled falsification using archived strategy corpora and equal compute budgets
```
