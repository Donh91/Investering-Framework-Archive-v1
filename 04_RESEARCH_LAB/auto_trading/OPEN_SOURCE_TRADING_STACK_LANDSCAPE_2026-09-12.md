# OPEN-SOURCE AUTONOMOUS TRADING STACK LANDSCAPE — 2026-09-12

Status: RESEARCH QUEUE / NON-CANONICAL / NO EXECUTION AUTHORITY
Owner: Investering Framework Research Lab
Purpose: preserve high-value external repositories for later Astra/Cowork source-code-level research without prematurely adopting or installing them.

## Decision frame

These repositories are not approved components. They are research targets.

The framework should prefer:

`Astra/research intelligence -> explicit hypothesis -> cheap screening -> point-in-time validation -> deterministic event-driven simulation -> frozen forward/shadow -> independent risk gate -> execution adapter`

Do not collapse research, validation and execution into one LLM-controlled system.

## Priority shortlist

### 1. `nautechsystems/nautilus_trader`
URL: https://github.com/nautechsystems/nautilus_trader
Research priority: VERY HIGH
Candidate role: deterministic simulation / event-driven execution kernel

Why it matters:
- production-grade Rust-native multi-asset, multi-venue engine;
- same architecture across research, deterministic simulation and live execution;
- historical quote/trade/order-book/custom data support with nanosecond resolution;
- modular venue adapters including major crypto exchanges and DEX/perp venues;
- explicit separation between Python control plane and compiled execution/runtime core;
- potentially useful as a benchmark for backtest/live semantic parity and execution realism.

Do not assume adoption. First test architecture fit, reproducibility, operational burden, license constraints, data-model compatibility, simulation semantics and authority boundaries.

### 2. `nautechsystems/nautilus_agents`
URL: https://github.com/nautechsystems/nautilus_agents
Research priority: VERY HIGH
Candidate role: agent-to-trading-engine contract / authority-boundary inspiration
Current status: early alpha, not production-ready.

Why it matters:
- scoped, versioned Observations;
- agent produces narrow semantic Proposals instead of direct execution commands;
- trading engine retains every production decision and execution step;
- explicit Proposal / Trace / Advisory / Receipt concepts;
- local evidence recording and shadow policy comparison;
- protocol versioning, digests, expiry, identity checks and retention-aware recording;
- currently only narrow risk-reducing semantic proposal support, which is a feature for governance research rather than a limitation.

Strong transfer principle:
`agent reasons -> agent proposes -> independent engine validates/decides -> receipt records outcome`.

This is unusually aligned with the Framework's existing no-self-grading, independent-verification and bounded-authority principles.

### 3. `microsoft/RD-Agent`
URL: https://github.com/microsoft/RD-Agent
Research priority: VERY HIGH
Candidate role: autonomous research-loop benchmark

Why it matters:
- target for studying automated idea generation, implementation, experiment, evaluation and iterative feedback loops;
- potentially relevant to Astra-era hypothesis generation, factor research and self-improving Research Lab workflows;
- should be compared against existing Compounding Learning / Research Lab governance rather than imported as a parallel swarm.

Primary research question:
Can its useful R&D loop mechanics improve our hypothesis throughput and learning rate without weakening point-in-time correctness, ownership, falsification or reproducibility?

### 4. `microsoft/qlib`
URL: https://github.com/microsoft/qlib
Research priority: HIGH
Candidate role: quant research / factor / model experimentation benchmark

Why it matters:
- mature research platform worth benchmarking for factor/model pipelines, experiment management and portfolio research;
- natural companion research target to RD-Agent;
- potential source of design patterns for dataset/model separation and experiment reproducibility.

Do not treat equity-first assumptions as crypto-valid without separate testing.

### 5. `hummingbot/hummingbot`
URL: https://github.com/hummingbot/hummingbot
Research priority: HIGH
Candidate role: crypto execution/connectors reference implementation

Why it matters:
- broad CEX/DEX connector surface;
- strategy controllers and reusable deterministic executors;
- paper-trading support;
- API/CLI surfaces suitable for automation;
- valuable source for exchange abstraction, order lifecycle and execution plumbing.

Primary caution:
credential and execution authority surface is large. Study architecture before any installation or account connection.

### 6. `hummingbot/condor`
URL: https://github.com/hummingbot/condor
Research priority: VERY HIGH
Candidate role: AI-agent harness + deterministic Hummingbot execution benchmark

Why it matters:
- open-source harness for creating/managing AI trading agents;
- AI agents can be delegated tasks or run loops;
- connects LLM decision support to Hummingbot API / deterministic execution components;
- explicit dry-run support and routines/scheduling;
- highly relevant for comparing agent orchestration and permission design with our Astra/Agents API landing zone.

Primary caution:
Condor can control real orders, balances and stored exchange credentials. Treat it as a security-sensitive architecture reference, not a plug-in candidate by default.

### 7. `polakowo/vectorbt`
URL: https://github.com/polakowo/vectorbt
Research priority: HIGH
Candidate role: cheap high-throughput hypothesis screening

Why it matters:
- vectorized large-scale parameter and strategy sweeps;
- optional Rust acceleration;
- walk-forward tooling and broad portfolio analytics;
- well suited to `generate many -> kill most cheaply -> escalate survivors` workflows.

Strong transfer principle:
Use fast vectorized screening for discovery, but never confuse discovery with validation.

Required guardrail:
large search spaces increase multiple-testing / backtest-overfitting risk, so any VectorBT-like lane needs a strict search-budget ledger, holdout discipline and downstream event-driven validation.

### 8. `freqtrade/freqtrade`
URL: https://github.com/freqtrade/freqtrade
Research priority: HIGH
Candidate role: crypto-native strategy research / dry-run / bias-detection reference

Why it matters:
- integrated backtesting, dry-run, optimization and exchange connectivity;
- FreqAI adaptive modelling;
- explicit lookahead-analysis and recursive-analysis commands;
- useful benchmark for practical crypto research workflow and bias diagnostics.

Do not assume its live engine or ML layer should become canonical. Benchmark its diagnostics and workflow patterns first.

### 9. `QuantConnect/Lean`
URL: https://github.com/QuantConnect/Lean
Research priority: MEDIUM-HIGH
Candidate role: mature institutional-style algorithmic trading architecture benchmark

Why it matters:
- long-running reference implementation for research/backtest/live transitions;
- useful for studying data normalization, brokerage abstraction, execution models and deployment semantics;
- strong comparison target when evaluating whether our future execution kernel is too bespoke.

Potential drawback:
heavier platform assumptions and less crypto-native fit than some alternatives.

### 10. `tradesdontlie/tradingview-mcp`
URL: https://github.com/tradesdontlie/tradingview-mcp
Research priority: MEDIUM-HIGH, already separately queued
Candidate role: optional Pine / chart / UI research adapter

Why it matters:
- Pine write/compile/debug workflows;
- structured chart-state extraction;
- screenshots and replay controls;
- potentially useful as a visual/indicator lab for Astra.

Boundary:
not canonical market data, not canonical backtest, not execution authority.

## Current architecture hypothesis to test

A promising future split is:

1. **Astra / Agents API / internal orchestrator** — research planning, hypothesis generation, specialist delegation, bounded tool routing.
2. **Existing Framework data + Research Lab** — point-in-time evidence, regime state, governance, F12, provenance.
3. **VectorBT-like lane** — cheap broad discovery and parameter-space rejection.
4. **NautilusTrader-like lane** — deterministic event-driven simulation and execution-realism testing.
5. **Shadow / frozen-forward layer** — prospective evidence before any capital authority.
6. **Independent risk governor** — machine-checkable vetoes outside the proposing model.
7. **Execution adapter** — future explicitly approved deterministic venue interface, potentially inspired by NautilusTrader or Hummingbot.
8. **TradingView MCP** — optional research/visual/Pine adapter only.

This is a hypothesis, not a design decision.

## Cross-repository principles worth reverse-engineering

Prioritize research on:
- proposal/decision/receipt protocols;
- point-in-time observation contracts;
- deterministic simulation semantics;
- same-code backtest/live parity and where it still breaks;
- event-time correctness and clock ownership;
- order-book / latency / fill modelling;
- paper/shadow-forward modes;
- multiple-testing and search-bias controls;
- independent validation separate from strategy generation;
- external kill switches that do not trust the agent's own claim;
- credential isolation and least privilege;
- exchange connector abstraction;
- replayable artifacts and immutable experiment records;
- bounded agent tool permissions;
- failure receipts and explicit rejected/no-action states.

## Research sequence

Do not install all candidates.

Recommended order:

`repository/docs audit -> capability/overlap matrix -> source-code boundary audit -> threat/authority model -> reproducibility test -> minimal sandbox benchmark -> compare against existing owner -> retain principle / benchmark / component candidate / reject`

The first deep source-code comparison should likely cover:

1. NautilusTrader + Nautilus Agents
2. Microsoft RD-Agent (+ Qlib where relevant)
3. Hummingbot + Condor
4. VectorBT as cheap-screening accelerator

## Mandatory evaluation labels

Every external project should end in exactly one of:

- `BORROW_PRINCIPLE`
- `BENCHMARK`
- `POTENTIAL_COMPONENT`
- `REJECT`

No project becomes a framework owner merely because it is mature, popular or technically impressive.

## No-duplicate rule

Before importing data, strategy logic, connectors or research outputs, compare against existing Framework owners and archives. Prefer reuse of existing data and owners. External tools should fill a proven capability gap rather than recreate Data Ping, Cycle Navigator, Research Lab, Shadow, F12, forecast/accountability or existing historical archives.

## Future Astra handoff

When Astra is available, it should treat this file as a discovery map, not as an adoption list. It should independently verify current repository state, identify disagreement with this prioritization, and actively search for better alternatives.