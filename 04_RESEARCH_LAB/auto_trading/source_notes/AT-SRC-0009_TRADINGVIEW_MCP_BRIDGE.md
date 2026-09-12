# AT-SRC-0009 — TradingView MCP Bridge

Captured: 2026-09-11
Status: RESEARCH_QUEUED
Evidence class: OPEN-SOURCE TOOL / INTERFACE INFRASTRUCTURE; NOT STRATEGY OR PERFORMANCE EVIDENCE
Primary repo: https://github.com/tradesdontlie/tradingview-mcp
Source snapshot reviewed: `tradesdontlie/tradingview-mcp@c05b8f5755ed8e64ea242de88ddbf46aa24d56a4`
Social discovery source: Miles Deutscher X thread, 2026-09-11

## Executive assessment

TradingView MCP Bridge is materially relevant to the AUTO_TRADING research vault, but not as a market-data backbone, not as an execution engine, and not as evidence that any chart indicator has alpha.

Its strongest role is as an **optional agent-to-chart research adapter** that can make TradingView Desktop legible and controllable by an LLM for:

- chart-state inspection;
- indicator/value extraction;
- Pine Script authoring, compilation and debugging;
- screenshot/visual verification;
- replay-based qualitative research;
- alert/watchlist workflow prototyping;
- compact context extraction from an otherwise large stateful GUI.

The repository itself explicitly states that it is not a trading bot and is not suitable for production automated trading. It is an interface layer over a locally running TradingView Desktop instance via Chrome DevTools Protocol (CDP).

## What the source actually provides

The project exposes a large MCP/CLI surface over TradingView Desktop, including:

- symbol/timeframe/chart control;
- quote/OHLCV and visible indicator values;
- Pine lines, labels, tables and boxes;
- Pine source injection, compilation, error retrieval and save/open workflows;
- multi-pane layouts;
- screenshots;
- price-alert management;
- watchlist read/write;
- bar replay and simulated replay trades;
- JSONL streams for local monitoring;
- generic UI automation primitives.

The current README describes roughly 78 MCP tools. Its research notes emphasize compact-by-default outputs, granular tool selection, Pine compile-error-fix loops, temporal consistency problems, and real-time agent latency.

## Strongest transferable principles

### 1. GUI state should be converted into narrow structured tool outputs

The repository reports that a naïve full-chart read can consume roughly an order of magnitude more context than targeted compact reads. This maps directly to our `Minimum Sufficient Intelligence` and capability-routing principles.

The useful pattern is:

`question -> smallest chart read -> structured artifact -> reasoning`

not:

`entire TradingView workspace -> giant screenshot/context dump -> LLM guess`.

### 2. Pine Script can act as a constrained research compiler target

The compile loop is useful:

`formal hypothesis -> generated Pine -> compile -> inspect errors -> revise -> save artifact`

This is directionally aligned with `AT-HYP-0008` (constrained AI-to-strategy compilation), but TradingView/Pine must remain a presentation/prototyping target rather than the authoritative backtest engine.

### 3. Chart and indicator state can be captured as reproducible evidence artifacts

Screenshots, current indicator values, Pine source, compile errors and replay state can all become run artifacts. This is stronger than an agent merely saying that it "looked at the chart".

### 4. UI adapters are different from data providers

The MCP bridge mainly reads/control state already exposed inside a user's TradingView Desktop application. It should therefore be classified as an interface adapter, not as a new canonical market-data owner.

This distinction prevents the framework from accidentally treating a GUI scraping/control bridge as superior truth to existing APIs and archived datasets.

## Why this is especially relevant for Astra

Astra should eventually be capable of converting a research contract into code, using tools, debugging, comparing outputs and preserving artifacts over long-running missions.

TradingView MCP offers a concrete future execution lane for tasks such as:

1. take a formally specified indicator hypothesis;
2. compile it into Pine;
3. render it on selected markets/timeframes;
4. read the resulting values/labels/tables programmatically;
5. capture screenshots and source as evidence;
6. compare against deterministic backtests outside TradingView;
7. kill the hypothesis if the visual/TV implementation diverges from the canonical test.

This should be an **optional capability**, not an always-on agent.

## Important limitations and risks

### Local-desktop dependency

The bridge requires:

- TradingView Desktop;
- Node.js 18+;
- local MCP/CLI process;
- TradingView launched with a Chrome remote-debugging port.

That means it is **not immediately compatible with an iPhone-only operating model**. A future use would require an approved desktop/self-hosted runner or equivalent controlled environment.

Do not build current framework dependencies around this tool.

### Undocumented internal interfaces

The repository explicitly warns that it relies on undocumented TradingView/Electron internals and may break after TradingView updates.

Therefore:

- never make it a canonical data owner;
- pin/test versions if evaluated;
- health-check before every research run;
- treat breakage as `CAPABILITY_UNAVAILABLE`, not as missing market evidence.

### CDP security boundary

The project exposes TradingView over Chrome DevTools Protocol on localhost. Its own security policy flags risks including code injection, unintended data exposure, credential/session leakage and local MCP vulnerabilities.

Any future framework integration must require:

- localhost-only binding;
- isolated runner;
- no exposed debug port;
- no exchange/wallet credentials in the same browser/app context;
- narrow tool allowlist;
- no generic `ui_evaluate` or arbitrary-code-style capability unless explicitly sandboxed and required.

### TradingView terms/licensing

The project states that programmatic consumption of TradingView data may conflict with TradingView Terms of Use and that users are responsible for compliance.

No archive, bulk extraction or redistribution of TradingView data should be designed around this bridge without a separate terms/license review.

### Real-time reasoning staleness

The project's own research notes say streaming can update faster than an LLM can reason, creating stale analyses and race conditions.

Therefore the bridge should **not** be treated as a high-frequency decision loop.

Potential use is better suited to:

- snapshot research;
- low-frequency chart validation;
- Pine development;
- prospective Shadow alerts whose detector logic is deterministic and whose LLM analysis happens after a frozen event.

### Replay is not canonical backtesting

TradingView replay is useful for qualitative, visual and implementation checks. It must not replace our canonical point-in-time backtest/walk-forward/frozen-forward pipeline.

Replay workflows are vulnerable to:

- manual/agent hindsight;
- indicator repainting;
- incomplete cost/slippage assumptions;
- visual overfitting;
- differences between displayed bars and executable market microstructure.

## Social-thread content we explicitly do NOT adopt

The Miles setup image includes generic rules such as fixed EMA/RSI definitions, a fixed `1%` max-risk-per-trade rule and a minimum risk/reward ratio.

Those are demonstration configuration values, not evidence-backed framework rules.

We do not inherit them.

Likewise, "watch my watchlist overnight and send me top trade setups" is a workflow example, not a validated strategy or authority grant.

## Social-thread follow-up: capability separation

Additional screenshots from the same thread make the intended workflow clearer: after the MCP bridge is installed, Miles proposes using Claude Code remote control / scheduled tasks to monitor a watchlist overnight and return a daily report, alongside Pine creation, replay, alerts and chart analysis.

This does **not** change the architectural classification of TradingView MCP. The scheduling/orchestration capability is separate from the chart adapter itself.

For this framework the correct separation remains:

`Astra / Agents execution harness owns orchestration + schedule`
`-> TradingView MCP is called only when chart/Pine/UI capability is required`
`-> frozen evidence artifacts return to the canonical Research Lab`

Do not let a convenient desktop scheduler become the owner of strategy logic, risk policy, market truth or promotion decisions.

The thread also markets "replay mode/backtesting in seconds" and live-market-data access. The open-source repository supports replay and chart data access, but neither claim is sufficient to promote TradingView replay to canonical backtesting or TradingView UI state to canonical data authority.

The screenshot binaries themselves are not required as archive artifacts because the substantive thread claims are captured here and the upstream repository is the stronger, inspectable source.

## Fit with current architecture

Best fit:

`ResearchContract`
`-> optional TradingView/Pine adapter`
`-> frozen artifacts`
`-> canonical backtest/replay comparison`
`-> F12/adjudication`
`-> Shadow only`

Existing owners remain authoritative:

- DATA PING / existing market-data contracts for market truth;
- Research Lab for hypotheses and experiment lifecycle;
- F12 / unified adjudication for promotion decisions;
- Forecast Ledger / learning layers for accountability;
- Astra Landing Zone for capability routing, budgets and bounded tool use.

## Research hypotheses worth testing

### TVMCP-H1 — Pine compiler productivity

Astra + TradingView MCP can turn a frozen indicator specification into compiling Pine with fewer human steps and lower time-to-valid-artifact than generic coding alone.

### TVMCP-H2 — structured chart extraction beats screenshot-only analysis

Structured values/lines/tables + a screenshot should reduce chart-reading errors and token usage versus screenshot-only agent analysis.

### TVMCP-H3 — TradingView implementation equivalence

A Pine implementation generated through the bridge should match the canonical Python/research implementation within explicitly defined tolerances on the same closed-bar dataset.

Failure to match is a research defect, not an invitation to average results.

### TVMCP-H4 — prospective alert value

A deterministic Shadow detector running through TradingView alerts may improve event capture/latency for a narrow setup family, but only if it adds unique coverage beyond existing Data Ping/automation sources after cost and reliability penalties.

### TVMCP-H5 — GUI adapter marginal value

The bridge should survive an A/B test against direct API/data workflows. Its value is justified only if it adds unique visual/Pine/TradingView capability or materially reduces development time; duplicating data already available through canonical APIs is not enough.

## Current decision

`RESEARCH_QUEUED / OPTIONAL_UI_ADAPTER / NO_EXECUTION / NO_CANONICAL_DATA_AUTHORITY`

Do not install into production infrastructure now.

The next correct step is a future Astra-era capability/overlap benchmark, not immediate operational deployment.