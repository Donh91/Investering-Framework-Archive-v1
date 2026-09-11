# ASTRA DISCOVERY / VALIDATION RESEARCH QUEUE

Status: `RESEARCH_ONLY`
Owner: Investering Framework Research Lab
Primary source anchor: `source_notes/AT-SRC-0007_ROHONCHAIN_ASTRA_DISCOVERY_PIPELINE.md`
Infrastructure dependency: Astra landing zone + future OpenAI Agents API qualification

## Purpose

Translate the useful parts of the RohOnChain architecture into falsifiable, framework-native research without copying a fixed bot swarm or granting live trading authority.

The target architecture is:

`cheap deterministic / low-cost monitoring -> Astra hypothesis generation -> reproducible backtest -> independent validation -> frozen-forward evidence -> existing F12/adjudication -> paper-only candidate`

Existing owners remain authoritative. No parallel regime engine, portfolio engine or live broker executor is created here.

## P0 — Independent grading contract

Test whether proposer/evaluator separation reduces false strategy promotion.

Compare:

1. one continuous Astra context generates and grades a strategy;
2. proposer and evaluator are isolated but share the same frozen evidence;
3. proposer, backtest runner and validator use separate contexts/artifacts;
4. separate validator plus blind adversarial falsifier.

Required outputs:

- frozen strategy/spec hash;
- exact test window;
- code/version hash;
- cost/fill model;
- result artifact;
- validator artifact;
- reason for accept/reject;
- whether the evaluator saw proposer reasoning.

Primary metrics:

- false-promotion rate;
- calibration;
- out-of-time survival;
- frozen-forward survival;
- duplicate reasoning rate;
- token/compute cost.

Kill criterion:
If independence adds cost/latency without reducing false promotion or improving later survival, simplify.

## P0 — Machine-checkable risk / kill-switch verification

Research principle:
A risk check is not valid because an agent reports that it ran.

Every future risk gate should be independently verifiable from deterministic or external state.

Candidate evidence:

- venue/account readback;
- deterministic exposure calculation;
- position/portfolio state artifact;
- run hash / signed manifest;
- CI/validator status;
- independent data source.

Research tasks:

- enumerate every proposed future kill switch;
- identify the independent observable that proves the condition;
- define fail-closed behavior for missing/stale evidence;
- test whether the check can be replayed from stored artifacts;
- log disagreement between agent claim and external state.

Do **not** adopt the source post's specific numeric thresholds as defaults.

## P0 — Search-bias / multiple-testing firewall

Astra can generate hypotheses faster than humans, which increases the risk of discovering false alpha.

Before broad strategy mining, build a research policy that records:

- total hypotheses attempted, including failures;
- strategy-family membership;
- parameter-search space;
- repeated use of the same data window;
- model/reasoner version;
- number of effective trials;
- out-of-time holdout integrity.

Candidate statistical tools to evaluate:

- Deflated Sharpe Ratio;
- Probability of Backtest Overfitting / CSCV concepts;
- purged / embargoed validation for overlapping financial labels;
- White/Hansen-style data-snooping corrections where applicable;
- false-discovery control across large hypothesis families;
- frozen-forward confirmation.

Promotion must not depend on a naive `Sharpe > X` or `t-stat > Y` threshold after large-scale search.

## P1 — Pre-reasoning cost gate

Test whether cheaper deterministic / smaller-model monitoring can suppress obvious noise before Astra reasoning.

Candidate inputs:

- existing Data Ping / market state;
- regime-transition flags;
- MMT microstructure candidates where justified;
- CFGI feature changes;
- liquidity/executability filters;
- event/catalyst triggers;
- Alpha/Research Lab candidates.

Benchmark:

`ALL_TO_ASTRA` versus `FILTER_THEN_ASTRA`.

Measure:

- Astra tokens / task;
- wall-clock time;
- candidate recall;
- precision;
- missed later-valid hypotheses;
- false suppression;
- downstream research quality.

Goal:
Find the Pareto frontier between compute reduction and opportunity recall. Do not optimize compute alone.

## P1 — Minimum-sufficient parallelism

The source's fixed 300-agent swarm is not adopted.

Instead, test whether bounded subagents add marginal information.

For each mission log:

- capability / question owner;
- unique evidence added;
- falsifier added;
- conclusion changed?;
- token cost;
- latency;
- overlap with existing owner;
- disagreement contribution.

Astra may add parallelism only when expected marginal information justifies the cost.

This should feed the existing Shadow-only agent-utility learning layer rather than create a new scheduler.

## P1 — Artifact-backed execution proof

Every research stage should emit verifiable artifacts rather than narrative self-reports.

Minimum candidate manifest:

- `research_contract_id`
- `decision_at`
- `strategy_spec_hash`
- `data_contract_hash`
- `code_commit_sha`
- `model_and_effort`
- `test_window`
- `fill_cost_model`
- `result_artifact_hash`
- `validator_result`
- `observable_at_cutoff`
- `lookahead_check`
- `promotion_state`

This should reuse existing provenance, Forecast Ledger and experimental-lifecycle machinery.

## P2 — Agents API execution-lane benchmark

OpenAI Agents API is a candidate harness, not a new framework owner.

Once the canonical Astra infrastructure note is merged and Astra/API access is available, compare the same frozen research mission across:

1. current GitHub/Codex/API stack;
2. Agents API parent agent with bounded subagents;
3. hybrid lane where deterministic preprocessing remains external and Astra handles only unresolved reasoning.

Test:

- completion rate;
- context continuity across long runs;
- tool reliability;
- subagent isolation;
- provenance completeness;
- token/tool cost;
- wall-clock latency;
- recoverability after interruption;
- policy/authority compliance.

The winner is the simplest lane that preserves or improves research quality and governance.

## Explicit rejects / non-adoptions

Do not copy these source claims into the framework as defaults:

- 300 permanent agents;
- any unverified vendor/model cost claims;
- claimed one-million-token session architecture as a design requirement;
- naive universal Sharpe/t-stat gates;
- direct live broker deployment;
- arbitrary 5% drawdown / 2% position / 30% sector thresholds;
- raw Kelly sizing from an optimized backtest;
- agent self-report as proof a risk check or backtest ran.

## Astra mission when available

Astra should first audit this queue against existing owners and delete/merge any redundant task before running new work.

Then execute in this order:

1. map existing Research Lab / F12 / Forecast Ledger / adjudication coverage;
2. implement only missing schemas or validators;
3. benchmark independent grading;
4. build the search-bias firewall;
5. benchmark pre-reasoning cost gates;
6. measure marginal subagent utility;
7. compare Agents API as an execution lane;
8. promote only changes with measurable gain.

## Success condition

This queue succeeds if Astra increases the rate of **reproducible surviving research per unit of compute** while decreasing false promotion and preserving hard governance boundaries.

It fails if it merely produces more agents, more backtests, more attractive Sharpe ratios or more automation without stronger evidence.