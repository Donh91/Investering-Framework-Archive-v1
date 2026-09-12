# TradingView MCP Research Queue

Status: RESEARCH ONLY
Owner: AUTO_TRADING / Research Lab
Source: `source_notes/AT-SRC-0009_TRADINGVIEW_MCP_BRIDGE.md`
Current decision: `OPTIONAL_UI_ADAPTER / NO_EXECUTION / NO_CANONICAL_DATA_AUTHORITY`

## Objective

Determine whether `tradesdontlie/tradingview-mcp` adds enough unique research value to justify maintaining a TradingView Desktop adapter in the Astra-era stack.

The burden of proof is on the adapter. Existing direct data/API owners and deterministic research tooling remain the baseline.

---

## P0 — Duplicate-capability audit

Before installing anything, map every relevant TradingView MCP capability against what the framework already has.

Required matrix:

| Capability | Existing owner/source | TV MCP adds unique value? | Needed for Astra? | Keep / reject |
|---|---|---|---|---|
| OHLCV / quote reads | existing market-data stack | TBD | TBD | TBD |
| indicator values | derivable in research code | TBD | TBD | TBD |
| Pine development | no equivalent GUI compiler lane | likely | TBD | TBD |
| screenshots / visual verification | partial elsewhere | likely | TBD | TBD |
| replay | research/backtest stack already exists | maybe only visual | TBD | TBD |
| TradingView alerts | existing automation/data alerts | TBD | TBD | TBD |
| drawings/layouts | presentation/research aid | maybe | low | TBD |
| UI automation | no direct equivalent | risky | low unless necessary | TBD |

Promotion criterion:

At least one material capability must be uniquely valuable after accounting for maintenance, security, token cost and fragility.

---

## P0 — Security and terms review

Do not install into a trusted or credential-bearing environment before all of the following are explicitly evaluated:

1. Chrome DevTools port is localhost-only.
2. Runner is isolated from exchange/wallet/private-key contexts.
3. Tool allowlist excludes unnecessary generic UI/eval capabilities.
4. No secret/session token can be surfaced through MCP outputs.
5. Dependency tree and install scripts are reviewed.
6. TradingView Terms of Use/licensing is reviewed for the intended level of automation and any data extraction/storage.
7. Version pinning and health checks are defined.

Any unresolved material issue => `NO_GO_FOR_INSTALL`.

---

## P0 — iPhone-only operational feasibility

Current user operating model does not include a persistent desktop.

Test future options only when there is a concrete Astra/Agents infrastructure lane:

- isolated self-hosted Mac/Windows runner;
- controlled remote desktop environment;
- dedicated machine with TradingView Desktop;
- secure bridge from Astra/Agents API to the runner.

Reject any architecture requiring routine manual desktop maintenance.

Success criterion:

The lane can be operated with near-zero recurring user intervention, while remaining isolated, observable and revocable.

---

## P1 — Pine compiler benchmark

Goal: test the strongest use case identified by the source.

Create a frozen set of representative indicator/strategy specifications:

- simple moving-average regime filter;
- non-repainting momentum/volatility composite;
- one multi-timeframe indicator;
- one indicator with tables/labels/lines;
- one intentionally tricky repaint-prone specification.

Compare:

A. generic Astra/Codex Pine generation without TradingView MCP;
B. Astra/Codex + TradingView MCP compile/error-fix loop.

Measure:

- time to first compile;
- number of compile iterations;
- token/tool calls;
- human interventions;
- correctness vs formal spec;
- repaint/leakage defects;
- final source reproducibility;
- ability to save screenshot + source + compiler output as artifacts.

Do not score visual attractiveness as edge.

---

## P1 — Implementation equivalence gate

For each surviving Pine artifact:

1. reproduce the same indicator in canonical research code;
2. use identical closed-bar inputs;
3. compare timestamp-aligned outputs;
4. define numerical tolerance before viewing results;
5. investigate every divergence;
6. never average disagreeing implementations.

If Pine and canonical implementation disagree materially, mark:

`IMPLEMENTATION_COLLISION`

and block downstream inference until resolved.

---

## P1 — Structured chart extraction vs screenshot-only benchmark

Frozen chart states should be analyzed under two lanes:

A. screenshot only;
B. structured MCP values/lines/tables + screenshot.

Measure:

- factual extraction accuracy;
- missed indicators/levels;
- hallucinated values;
- token cost;
- latency;
- confidence calibration.

Hypothesis:

Structured state plus targeted visual context will outperform screenshot-only reasoning at lower token cost.

---

## P1 — Repainting / look-ahead firewall

Any Pine research must explicitly classify:

- closed-bar computable vs live-bar dependent;
- repainting vs non-repainting;
- use of future-aware functions or data alignment;
- higher-timeframe bar availability semantics;
- alert timing relative to bar close.

No Pine-derived feature may enter a historical test unless its value was observable at the historical decision timestamp.

Required invariant:

`feature.observable_at <= decision_timestamp`

Otherwise => `QUARANTINED_FOR_LOOKAHEAD`.

---

## P2 — Replay research validity

Use TradingView replay only as a qualitative/implementation cross-check.

Test whether a frozen agent can walk forward bar-by-bar without future leakage and preserve an immutable action ledger.

Compare its actions against:

- canonical backtest;
- walk-forward engine;
- frozen-forward/paper process.

Replay is never promoted as the canonical backtest owner.

---

## P2 — Prospective Shadow alert experiment

Only after P0/P1 pass.

Choose one narrow, deterministic setup with an existing formal definition.

Run:

- current framework detector;
- TradingView alert implementation;
- optional Astra post-event interpretation after the event is frozen.

Measure:

- unique events found;
- false positives;
- missed events;
- timestamp latency;
- uptime/breakage;
- maintenance time;
- token cost;
- whether unique coverage changes a downstream research conclusion.

No trades, no sizing, no execution.

---

## P2 — Orchestration / adapter separation test

The social thread pairs TradingView MCP with Claude Code remote control and scheduled tasks for overnight monitoring. Treat these as separate capabilities.

Future test must compare:

A. Astra / Agents execution harness schedules and routes the job, calling TradingView MCP only when chart/Pine/UI access is required;
B. a desktop scheduler owns the entire workflow.

Required outcome:

- orchestration, budgets, retries, authority and audit logging remain with the Astra/Agents owner;
- TradingView MCP remains a bounded adapter;
- adapter outage must degrade only the TradingView-specific step, not the whole research system;
- no scheduler-created rule may bypass ResearchContract, F12 or execution authority boundaries.

Prefer A unless B demonstrates a unique capability that cannot be reproduced safely.

---

## P2 — Context-efficiency benchmark

The source reports compact targeted outputs as a major advantage.

Measure real framework workloads under:

- full screenshot/context dump;
- broad TradingView state read;
- minimum-sufficient targeted MCP calls.

Track:

- input tokens;
- output tokens;
- tool latency;
- factual accuracy;
- agent utility.

If targeted reads provide equal/better quality at meaningfully lower cost, encode the result into Astra capability-routing guidance.

---

## P3 — Agents API / Astra execution-lane benchmark

When the OpenAI Agents API/Astra stack is available for controlled evaluation, compare:

1. direct API/data-only research;
2. direct API + Pine compiler in generic sandbox;
3. direct API + isolated TradingView MCP desktop runner.

Question:

Does the desktop/UI lane add enough unique capability to justify its operational surface area?

Likely winning use cases should be limited to:

- Pine compile/debug;
- visual chart verification;
- proprietary/private visible TradingView indicators already licensed by the user;
- reproduction of workflows that only exist inside TradingView.

If direct APIs and deterministic code solve the task equally well, do not route through TradingView MCP.

---

## Explicit reject list

Do not promote any of the following merely because they appear in social-thread examples:

- fixed EMA/RSI directional rules;
- universal 1% position risk;
- universal minimum 2R filter;
- LLM-selected top trades from a watchlist without frozen detector logic;
- unattended chart mutation as evidence of autonomous trading capability;
- TradingView replay performance as proof of live edge.

---

## Promotion path

`SOURCE`
`-> security/terms review`
`-> duplicate-capability audit`
`-> isolated feasibility test`
`-> Pine/structured-state benchmarks`
`-> implementation equivalence`
`-> prospective Shadow experiment`
`-> F12/adjudication`
`-> RETAIN_AS_OPTIONAL_ADAPTER / REVISE / KILL`

There is no direct path from this queue to live execution.