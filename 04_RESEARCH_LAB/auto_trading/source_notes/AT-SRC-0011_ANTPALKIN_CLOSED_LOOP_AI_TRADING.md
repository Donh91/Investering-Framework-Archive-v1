# AT-SRC-0011 - Antpalkin closed-loop AI trading architecture

Date captured: 2026-09-12
Status: SCREENED / BORROW_PRINCIPLE
Evidence class: ARCHITECTURE INSPIRATION; vendor/performance claims unverified

## Source

- X article: `The self-improving AI trading machine is mostly built. One piece left.`
- User-provided export of the article

## Source thesis

The source describes a six-stage quant loop:

`RESEARCH -> CODE -> BACKTEST -> LIVE -> POST-MORTEM -> FINE-TUNE`

The core claim is that modern agents can automate much of the first five stages and that the remaining compounding advantage is persistent learning across research cycles.

Useful source proposals include:

- parallel specialist researchers with limited cross-talk to reduce anchoring;
- strategy-code generation/debug loops;
- sealed out-of-sample windows;
- walk-forward validation;
- Monte Carlo and Deflated Sharpe / multiple-testing awareness;
- a separate breaker/adversarial agent;
- stress tests at higher transaction costs and hostile historical regimes;
- deterministic kill switches in code rather than system prompts;
- immutable preregistration of expected outcomes;
- persistent memory / hypothesis graph that retains failures, regime dependence and untested ideas.

## Framework overlap audit

Most of the strongest ideas already exist in the Investering Framework in stronger governed form:

- Research Lab red-team and independent grading;
- search-bias / multiple-testing firewall;
- prospective/frozen evidence;
- Forecast/Sequence immutability;
- negative-learning priority;
- Kill Criteria at birth;
- deterministic risk/kill-switch verification;
- artifact-backed proof;
- no self-promotion by the proposing agent.

Therefore this source does NOT justify a new parallel self-improving trading engine.

## Incremental value worth retaining

### 1. Persistent hypothesis graph

The useful incremental concept is a durable graph of research state, not just semantic memory:

- hypothesis attempted;
- exact spec/hash;
- asset/regime tested;
- result and failure reason;
- falsifier hit/not hit;
- related hypotheses;
- whether the failure should prevent rediscovery;
- unresolved next test.

This should be compared with existing Compounding Learning / Theory Ledger infrastructure rather than added blindly.

### 2. Explicit cost of rediscovery

Measure how often an agent proposes materially equivalent hypotheses that were already rejected. A learning system should reduce duplicated failed research over time.

### 3. Blind-specialist design as an experiment

Independent specialist agents may reduce anchoring, but only if they add marginal information. Existing minimum-sufficient-parallelism research remains authoritative.

## Critical correction to the source narrative

A loop that rewrites a losing strategy until its backtest turns green is NOT automatically self-improvement. Without search-budget accounting, untouched holdouts and frozen-forward evidence, it is an automated overfitting machine.

The Framework must preserve this ordering:

`failure diagnosis -> proposed revision -> new immutable version -> untouched validation -> adversarial test -> frozen forward`

Never:

`fail -> mutate repeatedly on same history -> stop when profitable -> promote`.

## Classification

- closed-loop quant workflow: `BORROW_PRINCIPLE`
- persistent hypothesis graph: `HIGH-VALUE RESEARCH CANDIDATE`
- autonomous strategy mutation on same backtest history: `REJECT`
- LLM-owned live risk limit: `REJECT`
- code-level independent kill switch: `ALREADY ALIGNED / RETAIN`

## Astra research task

Benchmark current Theory/Sequence/Research Lab memory against an explicit hypothesis graph.

Measure:
- duplicate-hypothesis rate;
- failed-idea rediscovery rate;
- time/token cost per surviving hypothesis;
- out-of-time survival of proposed revisions;
- whether memory causes useful learning or merely entrenches stale assumptions.

No live execution authority is granted.