# Veles Quant-Layer Research Queue

Date: 2026-09-12
Status: RESEARCH_ONLY / NON_EXECUTION
Owner: 04_RESEARCH_LAB/auto_trading/
Source note: source_notes/VELES_QUANT_LAYER_AND_OPEN_SOURCE_STACK_2026-09-12.md

## Purpose

Convert the Veles architecture review and open-source benchmark scan into bounded, falsifiable work without creating a parallel trading engine or granting execution authority.

## Binding posture

The existing second-pass AUTO_TRADING decision remains authoritative:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

This queue does not supersede the current P0 order. New work below is admitted only where it directly accelerates those P0 gates.

## P0-linked work

### Q1 - Planted leakage defect pack

Goal: turn observed real-world failure classes into mechanical negative controls.

Include at minimum:
- future-data append should not alter value at time t;
- missing observations must not silently become zero-return observations;
- declared warm-up must prevent premature outputs;
- source pagination must not silently return a tail-only time series;
- point-in-time macro/news/fundamental availability must respect observable timestamps;
- strategy adaptation must not inherit prior validator/approver evidence.

Primary reference: HKUDS/Vibe-Trading recent fixes.

Acceptance:
- detector catches planted defects;
- clean controls pass;
- no candidate strategy can run before the detector itself passes its defect pack.

### Q2 - Monotonic trial accounting on benchmark corpus

Goal: use a known alpha corpus to prove trial accounting before broad search.

Method:
- activate proposal-time monotonic attempt counter first;
- select a small frozen subset of Alpha Zoo families;
- increment N before implementation/result visibility;
- preserve failed/abandoned trials;
- prohibit reset by strategy-family change.

Acceptance:
- exact N lineage reproducible from receipts;
- no survivor-only accounting;
- multiple-testing correction can consume the same immutable attempt ledger.

### Q3 - Risk-layer ablation

Question: does a deterministic risk layer improve survival independently of signal quality?

Arms:
A. baseline signal with fixed conservative sizing;
B. same signal + volatility scaling;
C. same signal + volatility scaling + hard drawdown gate;
D. same as C + turnover/cost gate.

Rules:
- identical signal stream across arms;
- no LLM confidence treated as calibrated probability;
- identical fees/slippage assumptions;
- same timestamps and fills;
- predeclare stop, sizing and comparison metrics before results.

Primary outcomes:
- max drawdown;
- risk of ruin / terminal failure rate in resampling;
- cost-adjusted return;
- turnover;
- abstention rate;
- tail loss.

Secondary outcomes:
- Sharpe/Sortino only with uncertainty and selection context.

### Q4 - Multi-agent reasoning ablation

Question: does debate/role specialization add incremental value over a single researcher and deterministic baseline?

Arms:
A. deterministic baseline;
B. single LLM researcher;
C. researcher + sealed adversarial validator;
D. bull/bear debate + sealed validator.

References:
- Veles role separation;
- TauricResearch/TradingAgents debate architecture;
- virattt/ai-hedge-fund analyst/strategy/fund decomposition.

Controls:
- identical point-in-time data pack;
- same token/model budget where possible;
- evaluator receives sealed candidate spec, not chain-of-thought/narrative history;
- deterministic risk layer identical across B-D;
- no cross-arm memory contamination.

Acceptance:
- only incremental evidence after cost/latency/variance counts;
- NO_EDGE is a valid result.

## P1 work

### Q5 - Interface matrix

Map the following across Veles, ai-hedge-fund, TradingAgents, Vibe-Trading and Lumibot:

`Observation -> Signal -> CandidateSpec -> ValidationReceipt -> RiskDecision -> Target -> OrderIntent -> FillReceipt -> Ledger`

Output should identify:
- existing framework owner;
- missing interface if any;
- duplicate capability;
- source of truth;
- writer authority;
- fail-closed state;
- whether adoption would reduce or increase complexity.

Default decision: reuse existing framework owner unless a benchmark proves a material gap.

### Q6 - One-code-path execution fidelity benchmark

Deferred until at least one strategy family survives Q1-Q4.

Compare:
- current minimal framework simulator;
- Lumibot equivalent implementation;
- only later Nautilus if surviving strategies need event/microstructure fidelity.

Do not benchmark live execution before paper/simulation fidelity differences become decision-relevant.

## Hard rejections

This queue explicitly rejects:
- direct broker integration now;
- real-money deployment;
- direct Kelly sizing from LLM conviction;
- arbitrary adoption of 5% daily stop / 10% per-trade risk examples;
- broad swarm expansion;
- short-window PnL promotion;
- GitHub stars as quality evidence;
- strategy self-validation;
- strategy promotion from historical success alone.

## Research receipts

Every run created from this queue must record:
- hypothesis ID;
- proposal-time trial number N;
- frozen spec hash;
- data/source hashes;
- effective/observable/retrieved timestamps where relevant;
- model/provider/version and inference budget;
- evaluator identity and separation status;
- cost/slippage assumptions;
- result artifact hash;
- failure/abandonment state if not completed;
- explicit authority = RESEARCH_ONLY_NON_CANONICAL.

## Stop condition

Do not expand this queue with another architecture source until at least one of Q1-Q4 has produced a reproducible artifact.

The next architecture review should be triggered by evidence, not by another impressive diagram.
