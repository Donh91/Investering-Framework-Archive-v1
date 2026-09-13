# AT-SRC-0007 — RohOnChain Astra discovery / validation architecture

Status: `SCREENED`
Captured: 2026-09-11
Source type: X / architecture inspiration / unverified implementation claims
Primary source: https://x.com/rohonchain/status/2098113579073556917?s=46&t=SUBrcpc4yI4ppaXpURK03g
Author: `@RohOnChain`
Evidence class: `ARCHITECTURE_INSPIRATION_NOT_PERFORMANCE_EVIDENCE`

## Source material available

The user supplied screenshots of the X post and embedded architecture graphic. The screenshots describe a continuous research/trading stack with:

- multiple raw data feeds;
- a cheap/parallel monitoring layer intended to filter candidates before expensive reasoning;
- separate hypothesis, backtest and validation roles;
- an orchestration / chief-of-staff layer;
- an independent risk layer with hard stop conditions;
- a deployment / notification layer;
- a stated principle that no bot should grade its own output;
- a stated principle that every kill switch should be checkable by something other than the bot's own claim.

The post also contains concrete implementation and performance-adjacent claims such as 300 parallel agents, specific vendor/model choices, context size, token prices, fixed Sharpe/t-stat/drawdown thresholds, long historical windows and direct broker deployment.

Those implementation claims are **not independently verified here** and must not be treated as evidence of profitability, reliability or superiority.

## Highest-value principles retained

### 1. Independent evaluation, not self-grading

A hypothesis-generating process should not be the final authority on whether its own work passes.

Framework-native interpretation:

`proposal -> independent/reproducible test -> separate validation/adjudication -> promotion decision`

This should reuse the existing Research Lab, F12 falsification, frozen evidence, blind-opposition and adjudication machinery rather than creating permanent "Hypothesis Bot / Backtest Bot / Validation Bot" identities.

### 2. Machine-checkable kill conditions

A risk or stop condition should be observable from an independent state source or deterministic artifact, not from an agent saying that the condition was checked.

Examples of acceptable evidence classes include:

- externally sourced account / market state;
- deterministic portfolio-state calculation;
- immutable run artifact;
- signed / hashed result package;
- CI or validator output;
- independent readback from the execution venue.

The important idea is **external verifiability**, not the source post's specific 5%/2%/30% thresholds.

### 3. Cheap filtering before expensive reasoning

The post's monitoring-layer idea is structurally compatible with the Framework's `Minimum Sufficient Intelligence` principle.

Research question:

Can deterministic or lower-cost detectors eliminate obvious noise before Astra-class reasoning **without materially reducing recall of later-valid opportunities**?

The target is not "70% cheaper" because that number is source-specific and unverified. The target is a measured cost/recall frontier.

### 4. Separation of discovery, evidence testing and validation

Strategy mining creates severe selection bias. Hypothesis generation, backtesting and final statistical/adversarial validation should therefore have distinct contracts and frozen handoffs.

A single Astra parent may orchestrate these stages, but downstream evaluation must not silently inherit mutable reasoning from the proposer.

### 5. Proof that work actually ran

"The bot says it tested it" is insufficient.

Research runs should leave machine-readable evidence such as:

- frozen strategy/spec hash;
- input-data contract/version;
- exact test window;
- code/version hash;
- cost/fill assumptions;
- result artifact;
- validator result;
- timestamps and provenance.

This aligns closely with existing frozen-forward, immutable evidence and provenance principles in AUTO_TRADING.

## Important improvements over the source architecture

### Multiple-testing correction is mandatory

A large hypothesis generator can manufacture apparently strong Sharpe ratios and t-statistics by chance. Therefore simple thresholds such as `Sharpe > 1.5` or `t-stat > 2` are not sufficient when hundreds/thousands of strategies are searched.

Future Astra research should evaluate methods such as:

- Deflated Sharpe Ratio;
- Probability of Backtest Overfitting / combinatorial purged cross-validation where appropriate;
- White / Hansen-style reality-check concepts;
- family-wise or false-discovery controls for large strategy searches;
- out-of-time and frozen-forward confirmation.

The Framework should reward survival after search-bias correction, not the best in-sample result.

### Risk must be deterministic but not arbitrary

The source's specific hard thresholds are anecdotes, not universal risk laws. A 5% portfolio drawdown kill, 2% position cap or 30% sector cap may be too loose, too strict or structurally wrong depending on strategy, horizon and asset class.

Retain the *non-negotiable externally verifiable enforcement* principle; research the thresholds separately.

### Permanent 300-agent swarms are rejected by default

The Framework already prefers minimum-sufficient teams, bounded parallelism and marginal agent-utility learning. Large permanent swarms create correlated errors, token/compute waste, difficult attribution and noisy consensus.

Astra should spawn only the smallest set of independent capabilities needed for the unresolved questions.

### Direct deployment is out of scope

The source describes a deployment bot that can ship strategies to a broker. AUTO_TRADING currently remains research/simulation/paper-only. No live execution authority is created by this note.

### Kelly sizing is not accepted from a backtest headline

Any future sizing research must account for estimation error, regime drift, fat tails, liquidity/capacity and model uncertainty. Raw Kelly output from an optimized backtest is not a safe deployment rule.

## OpenAI Agents API relevance

OpenAI's official 2026-09-10 Agents API announcement materially increases the technical feasibility of long-running parent/subagent research workflows, but it does **not** validate this trading architecture or any claimed edge.

Official source:
https://openai.com/index/introducing-the-agents-api/

Relevant verified capabilities include:

- managed Codex harness;
- long-running sessions with automatic context compaction;
- MCP/custom/built-in tools;
- tool search and programmatic tool calling;
- parallel subagents with isolated contexts;
- hosted or external sandboxes.

The canonical Agents API infrastructure note belongs under the Astra/agent layer:
`07_PROMPTS_AND_AGENTS/astra/2026-09-11__openai-agents-api-infrastructure-opportunity__source-note.md`

AUTO_TRADING should consume that infrastructure later as an execution lane, not duplicate it as a trading-specific harness.

## Framework-native research questions created by this source

1. Does independent grading reduce false strategy promotion versus proposer self-evaluation?
2. Does machine-checkable external risk verification catch silent failures that self-reported agent checks miss?
3. What pre-reasoning filter gives the best token/compute reduction while preserving opportunity recall?
4. Does isolated proposer/tester/validator handoff outperform one continuous context on calibration and backtest-overfit rate?
5. Which multiple-testing corrections best predict frozen-forward survival in our strategy search space?
6. When does parallelism add marginal information, and when does it only duplicate correlated reasoning?

## Promotion boundary

This source may influence research design only.

It does not establish:

- profitability;
- a live 24/7 trading system;
- validity of the source's performance thresholds;
- validity of the stated vendor/model economics;
- permission to connect an agent to a broker or exchange for live execution.

Any downstream promotion must pass existing Research Lab / F12 / adjudication and future explicit execution-governance requirements.