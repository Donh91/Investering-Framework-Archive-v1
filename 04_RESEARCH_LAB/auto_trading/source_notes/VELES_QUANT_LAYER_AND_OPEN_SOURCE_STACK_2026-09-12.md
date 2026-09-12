# Veles Quant-Layer + Open-Source Trading Stack Review

Date: 2026-09-12
Status: RESEARCH_ONLY / NON_EXECUTION / SOURCE_ARCHIVE
Owner: 04_RESEARCH_LAB/auto_trading/

## Scope

This note preserves the 2026-09-12 review of Veles' autonomous hedge-fund architecture, the separate quant-layer article shared by the user, and the surrounding open-source implementation landscape.

It is not evidence of profitable live trading and grants no execution authority.

## Source bundle

Primary architecture source:
- Veles, "How to Clone an Entire Hedge Fund with GPT-6 Astra and Run It From Your Bedroom 24/7" (working paper, September 2026)
- X source: https://x.com/velesxbt/status/2098396422710108372
- Drive source supplied by user: https://drive.google.com/file/d/1EHKOIjMI0uPOMIkMseeSK9MLUY724NED/view?usp=sharing
- X article source: https://x.com/i/article/2095445702620975109

User-supplied related article:
- "4 of 6 AI Trading Bots Blew Up Last Month. The 2 That Printed Money Had the Quant."
- Core claims discussed: expectancy, fractional Kelly, volatility scaling, drawdown/risk-of-ruin controls, turnover/cost drag, and kill switches.
- Treat the Alpha Arena/Nof1 performance claims as external claims requiring independent verification before any use as evidence.

Primary implementation references reviewed:
- https://github.com/HKUDS/Vibe-Trading
- https://github.com/virattt/ai-hedge-fund
- https://github.com/TauricResearch/TradingAgents
- https://github.com/Lumiwealth/lumibot
- https://github.com/ma-pony/cryptotrader-ai

Secondary discovery references supplied by user:
- https://github.com/1carlito/LLM-Stock-Manager
- https://github.com/suenot/062-multi-agent-llm-trading
- https://github.com/vasilkosturski/agentic-trading-system
- https://github.com/bhavuk1409/llm-trading
- https://github.com/EthanAlgoX/InvestCrew
- https://github.com/saurabhj9/ai-trading-system
- https://github.com/aminakhshi/financial_agent

Academic references supplied by user:
- https://arxiv.org/html/2602.23330
- https://arxiv.org/html/2602.18481v2

## Core architecture extracted from Veles

The useful contribution is not "Astra is smart enough to trade". It is the separation of concerns:

- Portfolio Manager: capital allocation, budget setting
- Research: candidate generation only
- Validator: adversarial accept/reject authority over sealed specifications
- Risk: independent hard kill authority that no other agent can override
- Execution: deterministic conversion of targets into orders
- Operations: sole writer to data/store/calendar surfaces

The paper's strongest framing is pipeline-first rather than personality-first. Each role should have bounded context, bounded tools and explicit authority.

The architecture maps well to the current framework principle that language models can propose or interpret, while deterministic owners and validators decide whether an action is admissible.

## Quant-layer article: what survives review

High-value principles:

1. Signals are not enough. Position sizing, volatility scaling, turnover/cost control and hard drawdown stops must be independent of the LLM analyst.
2. The analyst/LLM should not own final order sizing.
3. Most ticks/signals should legitimately result in no trade.
4. Kill-switch behavior must be mechanically testable, including forced synthetic red-day tests.
5. Paper testing is only useful if it tests refusal behavior, cost drag and risk gates, not just short-window profit.

Important caveats:

- LLM "conviction" is not automatically a calibrated probability and therefore should not be inserted directly into Kelly sizing.
- The example's `max_risk=0.10` is a demonstration parameter, not an accepted framework threshold.
- A 5% daily stop is likewise an illustrative setting, not adopted.
- Short paper-test profit is not promotion evidence.
- Any Kelly-like sizing requires an independently estimated edge/probability distribution, uncertainty treatment and caps.

## Repository review

### HKUDS/Vibe-Trading

Disposition: HIGH-VALUE RESEARCH BENCHMARK, NOT A RUNTIME DEPENDENCY YET.

Observed strengths:
- bundled Alpha Zoo with Kakushadze 101, GTJA 191, Qlib 158 and classical factors;
- explicit alpha bench/evaluator tooling;
- point-in-time / look-ahead controls are treated as first-class concerns;
- recent changelog demonstrates active repair of data-integrity defects, missing-value handling, backtest evidence gating and broker/paper isolation;
- strong fit as a strategy corpus and falsification/reference implementation.

Observed caution:
- its own recent fixes show how easy silent data/backtest defects are even in a mature project;
- warm-up behavior remains an explicitly documented open concern for some alpha families;
- do not import wholesale before independent leakage, licensing and reproducibility checks.

### virattt/ai-hedge-fund

Disposition: ARCHITECTURE/INTERFACE BENCHMARK.

Strengths:
- fund/strategy/analyst decomposition is directly relevant;
- one-code-path design for backtest/paper/live is conceptually strong;
- explicit hard-risk layer and the principle that the LLM never directly touches the trade;
- self-improvement is described as gated by CPCV/PBO-style validation.

Caution:
- README explicitly says educational/research only and currently does not actually trade;
- much of the persistent self-running fund remains aspirational;
- useful for interface design, not evidence of edge.

### TauricResearch/TradingAgents

Disposition: MULTI-AGENT REASONING BENCHMARK.

Strengths:
- clean specialization across fundamentals, sentiment, news, technical, bull/bear research, trader, risk and PM;
- explicit simulated exchange path;
- August 2026 release notes document look-ahead and point-in-time fixes across FRED, sentiment and memory;
- useful for adversarial-debate and decision-memory experiments.

Caution:
- multi-agent debate is not itself alpha;
- non-deterministic reasoning and memory can contaminate historical evaluation unless evaluation context remains sealed;
- use as an ablation target, not an assumed superior architecture.

### Lumiwealth/lumibot

Disposition: FUTURE EXECUTION/BACKTEST BENCHMARK, DEFERRED FROM P0.

Strengths:
- same strategy class can be backtested and then attached to a paper/live broker;
- supports deterministic and agentic strategies;
- broker/order/backtest infrastructure is substantially more mature than small demo repos.

Caution:
- current AUTO_TRADING prioritization explicitly defers execution-engine selection until honest strategy research survives;
- runtime adoption now would increase plumbing before evidence.

### ma-pony/cryptotrader-ai

Disposition: NICHE CRYPTO RISK/JOURNAL REFERENCE.

Strengths:
- hard-risk controls, decision journal and multi-agent debate are directly relevant to crypto-specific research.

Caution:
- very small public adoption footprint at review time;
- requires deeper code audit before receiving more weight than the larger benchmark repos.

### Secondary repos

Disposition: DISCOVERY ONLY unless a later independent audit identifies a unique capability not already covered by the primary five.

Do not spend near-term research budget duplicating inspection of low-adoption projects when Vibe-Trading, ai-hedge-fund, TradingAgents and Lumibot already span most relevant architecture surfaces.

## Framework-native decision

This review does NOT reverse the existing 2026-09-12 second-pass prioritization decision.

Current posture remains:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

Veles strengthens the organizational model, while the repository review strengthens the component/reference map. Neither justifies building more orchestration before the existing P0 empirical gates are complete.

## What to borrow now

Borrow as design constraints, not dependencies:

- explicit analyst -> validator -> risk -> execution authority separation;
- validator that sees sealed candidate specs rather than the researcher's narrative chain;
- risk owner with non-overridable veto/kill authority;
- operations/data writer with sole-write semantics;
- deterministic risk and sizing layer outside the LLM;
- no-trade/abstention as a normal output;
- one-code-path principle for any future backtest/paper/live engine;
- decision receipts and durable journals;
- point-in-time honesty and explicit warm-up/leakage controls.

## What NOT to adopt now

- live broker integration;
- real-money autonomous trading;
- direct Kelly sizing from LLM confidence;
- arbitrary 5% daily stop or 10% position-risk thresholds;
- broad multi-agent swarm expansion;
- architecture success claims based on GitHub stars;
- short-window paper PnL as evidence;
- self-promotion of strategies without sealed independent validation.

## High-value research tasks added to the AUTO_TRADING agenda

These tasks are subordinate to the already-adopted P0 empirical queue:

1. Build a cross-project interface matrix for `Signal -> CandidateSpec -> ValidationReceipt -> RiskDecision -> Target -> OrderIntent -> FillReceipt`, using Veles, ai-hedge-fund, TradingAgents and Lumibot as references.
2. Extract Vibe-Trading's leakage/warm-up failure classes into planted-defect tests for the framework's own mechanical leakage detector.
3. Use Alpha Zoo only as a controlled benchmark corpus after the proposal-time monotonic trial counter is active.
4. Run an ablation that compares single-researcher, bull/bear debate and deterministic baseline candidates under exactly the same data, costs and sealed evaluator.
5. Test whether deterministic risk-gating adds survival value independently of signal quality. Do not use uncalibrated LLM conviction as probability.
6. Preserve a future execution benchmark: if a strategy family survives, compare the framework's minimal simulator against Lumibot (and only later Nautilus if higher-frequency fidelity becomes observable).

## Acceptance gate before this source can change architecture

No architecture promotion from this review until all of the following exist:

- operational monotonic hypothesis-attempt counter;
- validated planted-leak detector;
- historical-source reconciliation result;
- at least one reproducible candidate test artifact;
- explicit cost/slippage model appropriate to its horizon;
- sealed validation independent of candidate generation;
- no hidden use of future/memory context;
- prospective or frozen-forward evidence for any promotion-strength claim.

## Final verdict

Veles is worth keeping as a top-tier architecture reference because it gets the authority graph right.

Vibe-Trading is currently the most interesting open research corpus/reference implementation from the supplied set, especially because its recent history exposes real failure classes around PIT data, missingness, warm-up and evidence gating.

ai-hedge-fund is the cleanest conceptual mapping to the "fund as pipeline" idea.

TradingAgents is the best multi-agent debate/memory benchmark.

Lumibot is the strongest execution/backtest bridge candidate, but adopting it now would be premature.

The net result is not "build the autonomous hedge fund now". It is: use these projects to make the evidence machine harder to fool, then earn the right to build the capital path later.
