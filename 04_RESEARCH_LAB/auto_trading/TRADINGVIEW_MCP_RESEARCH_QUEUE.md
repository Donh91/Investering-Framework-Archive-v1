# TradingView MCP Research Queue

Status: `REJECTED_FOR_AUTO_TRADING / ARCHIVED`
Owner: AUTO_TRADING / Research Lab
Source: `source_notes/AT-SRC-0009_TRADINGVIEW_MCP_BRIDGE.md`
Decision date: 2026-09-12
Decision authority: external architecture audit + framework second-pass review

## Decision

Do not install, benchmark or integrate `tradesdontlie/tradingview-mcp` inside AUTO_TRADING.

The repository remains useful as historical inspiration for narrow ideas such as Pine authoring/compile-debug workflows, but it is not an eligible market-data, research-decision or execution adapter for this project.

## Why the lane is closed

### 1. The repository's own README conflicts with the intended AUTO_TRADING use

The project explicitly states that it must not be used for:

> Performing automated trading or algorithmic decision-making using extracted data

AUTO_TRADING exists to research algorithmic decision systems. That is sufficient to close this lane without spending further engineering time.

### 2. Desktop/UI dependency does not fit the operating model

The bridge requires TradingView Desktop, Node.js and a local Chrome DevTools Protocol port. The framework should prefer headless, reproducible, data/API-native research lanes with near-zero recurring manual desktop work.

### 3. The authority/security surface is unnecessary

The bridge exposes broad UI/application-control capabilities over an authenticated desktop session and relies on undocumented TradingView internals. Even if isolated, that surface is disproportionate to the unique research value available to this framework.

### 4. Canonical research owners already exist elsewhere

AUTO_TRADING should use direct data, deterministic research code, point-in-time contracts, existing Research Lab/F12 and independent validation rather than use TradingView as a canonical data or backtest owner.

## Preserved value

Do not delete the original source note or Git history. Preserve these transferable ideas only:

- structured chart state is better than screenshot-only reasoning when a chart UI is genuinely needed;
- compiler/error feedback can improve generated Pine source;
- visual verification can be useful as a human-facing research aid;
- orchestration should remain separate from any UI adapter.

These ideas do not justify running this bridge inside AUTO_TRADING.

## Re-open condition

This lane may be re-opened only if all of the following materially change:

1. the upstream project's terms/readme no longer conflict with the intended use;
2. a headless, terms-safe capability provides unique value not available through direct APIs or deterministic code;
3. the security/authority surface is narrowed to the exact required function;
4. a frozen capability-gap benchmark demonstrates material value.

Until then:

`SOURCE -> ARCHIVED -> REJECTED_FOR_AUTO_TRADING`

No execution authority is created by this file.