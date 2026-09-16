# LuxAlgo Mechanism Qualification v1

**Dato:** 2026-09-14  
**Status:** SHADOW_ONLY  
**Område:** Research Lab / external mechanism qualification / auto-trading research  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Depends on:** `research/experiment_lifecycle/RESEARCH_EXECUTION_TOPOLOGY_v1.json`, `research/experiment_lifecycle/SEQUENTIAL_RESEARCH_QUEUE_v1.json`, `.agents/skills/research-lab-red-team/SKILL.md`, `.agents/skills/developer-source-research/SKILL.md`  
**Framework base SHA:** `82fdabd502b1522dea9d29b3dabddab34f0ab6da`

## Purpose

Qualify selected LuxAlgo open-source mechanisms against existing Investering framework owners without importing a parallel tool stack, changing market semantics, consuming the active experiment-execution slot, or granting any external component canonical, market or portfolio authority.

This document records a frozen qualification decision only. It is not an experiment result, implementation approval, source-feed activation, signal, threshold change or execution permission.

## Frozen proposition

Selected LuxAlgo mechanisms may contain incremental research or execution-architecture value, but only the smallest mechanism that demonstrates measurable divergence from existing framework owners should survive into a bounded challenger.

The null hypothesis is that each mechanism is redundant, explanatory-only, operationally premature or not worth its dependency and maintenance cost.

## Authority and non-interference boundary

This qualification MUST NOT:

- change `research/experiment_lifecycle/SEQUENTIAL_RESEARCH_QUEUE_v1.json` ordering;
- consume the single active experiment-execution slot;
- create a new market engine, shadow market authority or portfolio rule;
- change thresholds, weights, scoring semantics, Cycle Navigator state, Master Monday state or production routing;
- create broker write authority or live/paper order capability;
- introduce a new paid call, API key, credential or scheduled workflow;
- read or expose restricted Round 3 provider values;
- convert source-backed claims into outcome rows;
- auto-promote any finding.

Current experiment topology remains binding: one active `EXPERIMENT_EXECUTION` stage, while bounded research context may mature separately without outcome-row authority.

## Immutable upstream bindings

The following upstream revisions were inspected and freeze the source state for this qualification:

| Mechanism | Repository | Frozen upstream commit | Qualification focus |
|---|---|---|---|
| Conditional frequency / statistical envelope | `LuxAlgo/edge-stats` | `7cfa6d52f561e2c764ba900252e80356b03af9fe` | `P(outcome | conditions)`, N, Wilson CI, sample guards, temporal stability, reproducible query envelope |
| External Pine strategy execution/replay | `LuxAlgo/PineTS` | `1fdcf4ab5f8994046f1a95eb741d0fec00e34328` | Pine v5/v6-like runtime over custom OHLCV, strategy/indicator series, parity risk |
| Execution safety reference | `LuxAlgo/trade-relay` | `2e1a74c37307a20fcb0754d52b3530b55643dce7` | deterministic risk rails, idempotency, persistent kill switch, full signal-to-fill recorder |
| Broker abstraction reference | `LuxAlgo/broker-sdk` | `062b491b00d4aee01f56b37f63e3a12019bdadd2` | read/write capability separation, fail-soft normalization, golden vectors and canaries |
| Uncertainty/scoring reference | `LuxAlgo/whale-options` | `11f9c072827426f100193102a64451278787825b` | explicit missing inputs, cold-start disclosure, reason trace, replayability |
| Public-record source challenger | `LuxAlgo/market-trackers` | `9bf1045b6953e42a56f112445481d411a92261c9` | primary-source provenance, freshness, CFTC/Fed gap-driven candidate only |

Moving upstream `main` branches are not qualification authority. Any later experiment must either use these revisions or explicitly freeze and review newer revisions.

## Existing owner and redundancy result

Repository search and current Research Lab routing did not identify an existing local owner that already provides all of the following as one governed mechanism:

1. a composable conditional-frequency query envelope with mandatory sample-size/uncertainty/stability reporting;
2. isolated replay of external Pine strategies on framework-controlled OHLCV data;
3. the exact Trade Relay execution-rail/flight-recorder architecture.

This absence does NOT authorize new engines. The existing owners remain:

- Research Lab and `research/experiment_lifecycle/` for falsification and bounded experiments;
- current historical datasets/vault bindings for evidence;
- current source/provenance owners for source admission;
- future execution governance for any order-capable layer.

LuxAlgo mechanisms may only challenge or refine these owners.

## Mechanism dispositions

### Q1 — Edge Stats conditional edge envelope

**Primary verdict:** `FORWARD_TEST_CANDIDATE`

**Why it survives qualification:**

The mechanism makes historical conditional claims auditable by coupling each estimate to its eligible sample, sample size, uncertainty interval and temporal stability. The useful idea is the statistical envelope and query discipline, not LuxAlgo's preset catalog or market conclusions.

**Proposed local challenger:** `CONDITIONAL_EDGE_ENVELOPE_v1`

**Required preregistration before execution:**

- 8–12 fixed questions only;
- exact eligibility denominator;
- exact condition definition;
- exact outcome definition and horizon;
- unconditional baseline for every conditioned estimate;
- fixed query/trial budget;
- chronological holdout not used for hypothesis selection;
- regime split and early/late stability check;
- explicit multiple-testing status for any exploratory extension;
- opportunity-cost and false-negative accounting where decision-relevant.

**Required output envelope:**

`N_conditioned`, `successes`, conditioned rate, Wilson 95% CI, baseline N/rate, absolute and relative lift, temporal splits, holdout result, trial count, multiple-testing status and one of `REPLICATED | FRAGILE | NO_EDGE | FALSIFIED | INSUFFICIENT_N`.

**Promotion condition:**

Material incremental information over the current evaluator on held-out or prospectively frozen evidence without threshold tuning after observation. Incremental value may be improved discrimination/calibration OR a useful falsification of an existing assumption.

**Kill condition:**

Kill or keep research-only if it merely re-expresses existing metrics, produces no material incremental decision information, depends on post-hoc condition selection, fails stability/holdout, or invites combinatorial mining without a trial ledger.

**Authority ceiling:** `RESEARCH_EVIDENCE_ONLY`.

### Q2 — PineTS external strategy replay

**Primary verdict:** `FORWARD_TEST_CANDIDATE_AFTER_Q1_GATE`

**Why it survives qualification:**

A Pine-compatible runtime could materially reduce friction when testing external public strategies/bots against framework-controlled data. Its value is as an external-strategy falsification substrate, not as a signal provider.

**Proposed local challenger:** `EXTERNAL_STRATEGY_REPLAY_LAB_v1`

**Hard prerequisites:**

- Q1 qualification/experiment reaches a terminal gate before this consumes an execution slot;
- every strategy is frozen by source URL/repository, commit or content SHA, parameters and date before replay;
- TradingView/Pine semantic parity is checked per strategy rather than assumed globally;
- unsupported constructs fail closed;
- cost/slippage/execution assumptions are frozen before scoring;
- discovery/train and untouched holdout periods are separated;
- parameter-search trial count is durable;
- no live execution path.

**License boundary:** PineTS is AGPL-3.0/commercial upstream. Treat it as an isolated research dependency unless a separate licensing review explicitly permits broader integration. Do not copy its code into the auto-trader core by default.

**Kill condition:**

Reject as a framework dependency if parity cannot be demonstrated for intended scripts, unsupported semantics are common, licensing creates unacceptable coupling, or the lab fails to add falsification capability beyond existing backtest paths.

### Q3 — Trade Relay execution architecture

**Primary verdict:** `SOURCE_CONTEXT_ONLY`

Do not integrate now. Preserve these design assertions for a future execution-plane architecture review:

- intelligence proposes; deterministic execution authority disposes;
- agent-originated orders never bypass deterministic risk rails;
- idempotency is mandatory;
- projected position/risk is checked before order placement;
- kill switch persists across restarts;
- unable-to-verify risk should fail closed;
- raw signal → parsed intent → each rail verdict → broker request → fill/rejection is reconstructable.

A later execution architecture audit should compare the native framework design against these properties and create remediation only for demonstrated gaps.

### Q4 — Broker SDK architecture

**Primary verdict:** `SOURCE_CONTEXT_ONLY`

Potentially reusable principles:

- separate IO (`fetchRaw`) from pure normalization;
- normalize against golden conformance vectors;
- use provider canaries to catch schema/API drift;
- represent unsupported capabilities explicitly;
- keep read authority separate from order/write authority;
- never fabricate values when a provider cannot supply them.

No broker integration is authorized by this qualification.

### Q5 — Whale Options uncertainty mechanics

**Primary verdict:** `MODIFY_EXISTING_TEST_IF_GAP_PROVEN`

Do not adopt the options-flow engine. Audit existing framework scorers for these mechanics only:

- explicit `missing` rather than guessed component values;
- cold-start status;
- input-coverage disclosure;
- reason-level traceability;
- deterministic replay from stored evidence.

If all are already satisfied, disposition becomes `NO_INCREMENTAL_VALUE`. If one is materially absent, route the smallest gap to the existing owner rather than creating a new scoring layer.

### Q6 — Market Trackers

**Primary verdict:** `SOURCE_CONTEXT_ONLY`

Do not add it as a broad new feed or source owner. It may become a challenger only when the existing source map identifies a concrete missing evidence class, with CFTC COT or Federal Reserve communications as plausible examples.

Any candidate must pass existing source-admission rules: primary-source lineage, freshness, license/storage boundary, incumbent comparison, reproducibility and incremental value. No source-gap finding means no integration.

## Explicitly rejected paths

The following ideas are rejected at qualification time:

- install the full LuxAlgo MCP ecosystem as framework infrastructure;
- inject LuxAlgo indicators into Cycle Navigator or production direction logic;
- create an always-on LuxAlgo data feed;
- run all historical condition combinations and keep winners;
- treat Edge Stats historical frequencies as forecasts;
- use PineTS outputs as execution authority;
- connect live broker credentials during research qualification;
- adopt Whale Options scores or GEX as new framework signals without separate evidence;
- add Vela, Trade Journal or Prop Firm Sim before a concrete owner gap exists;
- change the existing experiment queue to prioritize this work.

## Anti-p-hacking firewall for Q1

`CONDITIONAL_EDGE_ENVELOPE_v1` is not authorized to become a free-form mining engine.

Before the first outcome query runs, persist:

- the frozen question set;
- all condition/outcome definitions;
- eligibility rules;
- horizons;
- query count budget;
- baseline definitions;
- holdout boundary;
- planned stability/regime splits;
- correction rule if exploratory tests are later admitted;
- promotion and kill criteria.

Exploratory findings may generate a NEW preregistered candidate. They may not be relabeled as confirmatory evidence after inspection.

## Execution ordering

Qualification does not mutate the current sequential queue.

Recommended order when governance permits:

1. Mature `CONDITIONAL_EDGE_ENVELOPE_v1` through the existing Research Lab / experiment lifecycle without queue jumping.
2. Run it only when the single execution slot is legitimately available.
3. Close Q1 as `REPLICATED`, `FRAGILE`, `NO_EDGE`, `FALSIFIED` or `INSUFFICIENT_N`.
4. Only then decide whether `EXTERNAL_STRATEGY_REPLAY_LAB_v1` is still worth building.
5. Conduct the Trade Relay execution architecture comparison later, before any order-capable production plane is authorized.
6. Run Broker SDK / Whale Options / Market Trackers checks only on demonstrated local gaps.

## Falsification-first expected outcome

Pre-registered expectation, not evidence:

- Edge Stats concept: likely `ADOPT_MECHANISM_NARROWLY` if it adds a disciplined conditional base-rate layer without duplicating existing evaluation.
- PineTS: likely `RESEARCH_ONLY` / bounded replay capability if parity is acceptable.
- Trade Relay: likely `REFERENCE_ARCHITECTURE_ONLY`.
- Broker SDK: likely `REFERENCE_ARCHITECTURE_ONLY`.
- Whale Options: likely mechanism-level ideas only, potentially `NO_INCREMENTAL_VALUE` if existing scoring already satisfies them.
- Market Trackers: likely `GAP_DRIVEN_ONLY`.

The preregistered expectation must not influence later scoring.

## Qualification completion criteria

This Phase A is complete only when:

- external commits are frozen;
- existing-owner overlap is explicit;
- every surviving mechanism has a falsifier and kill condition;
- no current experiment order changed;
- no runtime dependency was installed;
- no workflow/source feed/credential was created;
- no market/portfolio authority was granted;
- the artifact is reviewed through normal PR/readback governance.

## Next authorized design action after Phase A merge

Prepare the bounded preregistration package for `CONDITIONAL_EDGE_ENVELOPE_v1` as research context only. Do NOT execute historical outcome queries until the existing experiment lifecycle legitimately grants an execution slot and the preregistration is frozen.
