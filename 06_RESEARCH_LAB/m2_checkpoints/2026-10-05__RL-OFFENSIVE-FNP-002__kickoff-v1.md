# M2 Offensive Edge / False-Negative Cost - Kickoff Checkpoint v1

**Mission:** `RL-OFFENSIVE-FNP-002`  
**Date:** 2026-10-05  
**Status:** ACTIVE_RESEARCH_KICKOFF  
**Authority:** RESEARCH_ONLY / NO_CANONICAL_EFFECT  
**Fresh main:** `cece12569a0e1cc43c7ae1269259c968fcb6095d`

## Frozen question

How much upside has the framework sacrificed through delayed confirmation, by asset tier and regime, and when was that delay justified by drawdown avoided?

## Current evidence state

### Prospective T2 / T5

The canonical active-test registry defines:
- T2 `GATE_BTC_PARTIAL_FT_1`: BTC partial permission versus WAIT.
- T5 `FNP_CUMULATIVE`: which locks are correct restraint versus genuine missed opportunity.

The current T5 runtime is instrumented prospectively but evaluator-blocked.

Current `research/framework_memory/fnp_forward_rows/LATEST.json` reports:
- status: `PASS_NO_ELIGIBLE_INPUT`
- current_source_row_count: 0
- source_rows_created: 0
- outcome_attachments_created: 0
- derived_fnp_metrics_emitted: false
- authoritative_fnp_evaluator_available: false

The T5 runtime explicitly requires only real post-activation T2 `DIVERGENCE_CAPTURED` receipts and forbids retrospective backfill.

### Coverage evidence

The current main directory `research/api_agent/coordination/` contains the coordinator state/config but no persisted `LATEST_BTC_PARTIAL_WAIT_COVERAGE_HEALTH.json`.

The general coordinator workflow is prepared to consume that file if present.

This is evidence of absent persisted coverage state on current main, not proof that no historical check ever ran.

### Historical FNP-001

FNP-001 is not valid actual-policy replay evidence.

Current backtest lineage material classifies it as retrospective-policy quarantine / not policy-replay eligible because the original decision timestamp, actual policy definition, cost basis and execution timestamp were not fully recoverable.

Therefore historical estimates from that case may be explanatory context only, not a quantitative anchor for M2.

### Graduated alt deployment

T3 `GRADUATED_DEPLOYMENT_V1_1` remains data-blocked in the active registry.

The October conditional-edge-envelope Stage B mapping also reports:
- CEE-Q10 exit opportunity cost: evaluator not ready.
- outcome queries: 0
- executable_now: 0
- candidate_execution_state: NO_EXECUTION.

### Initial Research Lab inference

The framework appears better instrumented to measure future false-negative cost than it was historically, but the current evidence plane remains evidence-starved.

The core risk for M2 is false precision: turning historical narratives or zero-row prospective ledgers into a numeric opportunity-cost estimate.

## Questions for GPT-6.1 Sol

1. What claims about defensive-vs-offensive calibration are supported despite zero current prospective FNP rows?
2. What claims must remain UNKNOWN?
3. Does the current evidence justify any assertion that the framework is systematically too defensive?
4. Is the tier-dependent hypothesis testable now, given BTC has an explicit T2 owner while graduated alt deployment remains blocked?
5. What is the minimum evidence needed before changing aggression/permission posture?
6. Separate:
   - architecture readiness,
   - evidence readiness,
   - economic conclusion,
   - current opportunity-cost knowledge.

## Questions for Claude

Trace why the current prospective machinery has zero eligible T5 rows and whether this is:
- genuine no-divergence observation;
- missing coverage persistence;
- source-owner nonproduction;
- maturity/evaluator blockage;
- broken wiring;
- or an intentional fail-closed design.

Do not infer economic value.

## Boundaries

No retrospective pseudo-rows.
No invented cost percentages.
No new thresholds/actions.
No portfolio action.
No canonical promotion.
No code changes from model output.
