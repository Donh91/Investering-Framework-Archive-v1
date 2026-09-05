# Compounding Learning Controller v1 - Implementation Status

**Status:** `IMPLEMENTED_ON_GOVERNED_BRANCH_AWAITING_PR_CI_MERGE`  
**Date:** 2026-09-05  
**Implementation branch:** `agent/task-20260905-compounding-learning-v1-final`  
**Fresh-main base at branch creation:** `163e3bfee6366c26ad8f9065b30e1c3afe87f29f`

## Why this implementation exists

The original exploratory implementation on `agent/task-20260904-compounding-learning-v1` proved that a learning controller was feasible, but it was built before the current Unified Experimental Adjudication architecture and diverged materially from main.

That old branch is therefore retained only as historical salvage material. It is not the implementation base and must not be merged blindly.

The current implementation was rebuilt from fresh main after verifying the active owners:

1. Experiment Lifecycle Registry;
2. Scientific Admission Registry;
3. Unified Experimental Lifecycle Adjudication;
4. existing research-governance bindings and single-writer workflow.

## Frozen responsibility

The controller has one responsibility:

> Convert mature, already-adjudicated evidence into durable learning state, calibrated uncertainty, contradiction tracking, and a bounded proposal for the next highest-information prospective test.

It does not decide what the evidence means at candidate level. Unified Experimental Adjudication remains the scientific interpretation owner.

## Implemented runtime

### Entrypoint

`scripts/research/compounding_learning_controller.py`

A thin compatibility entrypoint preserves the existing governance action vocabulary while routing implementation into the dedicated v1 core.

### Deterministic core

`scripts/research/compounding_learning_v1_core.py`

Implemented functions cover:

- post-adjudication freshness validation;
- 7/14/30/60/90/120/180/240-day descriptive checkpoints;
- historical requalification clock protection;
- semantic-family aggregation;
- support / negative / inconclusive / contested learning-state synthesis;
- material-learning delta detection;
- contradiction-preserving learning state;
- candidate next-test generation;
- transparent information-value ranking;
- one bounded next-best-test selection;
- persistent learning backlog;
- append-only material learning events;
- confirmatory-study anti-peeking firewall;
- idempotent no-op behavior when no material learning delta exists.

## Machine-readable products

Under:

`00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/`

v1 owns:

- `STATE.json` - `LEARNING_STATE_v1` carried by the existing controller-state contract;
- `events/LE-*.json` - append-only `LEARNING_EVENT_v1` material-change history;
- `NEXT_BEST_EXPERIMENT.json` - `NEXT_BEST_TEST_PROPOSAL_v1` carried by the existing proposal contract;
- `LEARNING_BACKLOG.json` - durable ranked unresolved-test backlog;
- `POLICY.json` - research-only authority and checkpoint policy.

## Checkpoint semantics

All profiles now share the descriptive schedule:

`7 / 14 / 30 / 60 / 90 / 120 / 180 / 240 days`.

The checkpoints are learning and operations checkpoints, not automatic scientific verdicts.

For confirmatory studies:

- interim performance inference remains forbidden;
- scientific-method change remains forbidden;
- automatic child experiments remain forbidden;
- checkpoint scope is limited to accrual health, data quality, concentration and maturity readiness;
- final confirmatory adjudication remains owned by its frozen confirmatory test.

## Material-learning rule

Raw observation growth alone is not material learning.

A `LEARNING_EVENT_v1` is created only when mature, current Unified-Adjudication evidence materially changes a semantic family's adjudicated evidence signature or mature outcome count.

This explicitly prevents pseudo-learning from log volume.

## Next-best-test contract

An active proposal includes:

- unresolved uncertainty;
- hypothesis;
- explicit frozen baseline;
- explicit falsifier;
- what would change the current view;
- transparent information-value ranking and component surface;
- expected incremental value marked unproven;
- required lineage;
- target / horizon / regime fields that must be frozen by Scientific Admission;
- negative controls;
- redundancy risk;
- complexity tax;
- false-positive and false-negative costs to freeze;
- revisit condition;
- ranked-lower alternatives.

The ranking score is explicitly a transparent heuristic for test selection, not an empirical probability or skill estimate.

Every proposal has:

- `requires_scientific_admission=true`;
- `automatic_execution=false`;
- `canonical_effect=false`;
- `portfolio_execution=false`.

## Health and discoverability

Dedicated health owner:

`scripts/health/build_compounding_learning_health.py`

Expected output:

`research/architecture_health/LATEST_COMPOUNDING_LEARNING_HEALTH.json`

The health contract fails closed on:

- missing or invalid adjudication/state/proposal/backlog;
- authority or ownership breach;
- missing checkpoint schedule;
- state/adjudication drift;
- missing append-only event history;
- incomplete next-test proposal contract;
- Scientific Admission bypass.

The framework handoff builder now exposes a mandatory experiment-learning / Astra read order:

1. Experiment Registry;
2. Scientific Admission;
3. Unified Adjudication;
4. Compounding Learning State;
5. Next Best Test Proposal;
6. Learning Backlog;
7. Compounding Learning Health.

## Workflow integration

`.github/workflows/unified-experimental-lifecycle-adjudication.yml`

The existing Monday owner remains the only production writer.

Production order is now:

1. validate lifecycle/adjudication/controller machinery;
2. build Unified Experimental Adjudication;
3. persist weekly/latest adjudication;
4. run Compounding Learning Controller;
5. validate authority and confirmatory firewalls;
6. build dedicated Compounding Learning health;
7. rebuild framework handoff immediately;
8. commit through existing `framework-main-writer` concurrency and verified main readback.

PR validation is read-only.

No additional high-frequency parallel writer was created.

## Tests

Existing Compounding Learning regression tests are preserved.

New adversarial coverage includes:

- full checkpoint schedule;
- support + failure in the same semantic family becomes contested;
- uncertainty / falsifier / information-gain contract;
- raw observation growth does not become material learning;
- new mature evidence does become material learning;
- backlog retains deprioritized/historical ideas;
- confirmatory checkpoints cannot peek at skill;
- append-only event mutation is rejected;
- dedicated health passes correct wiring and fails adjudication drift.

Local pre-write validation completed with all controller and health tests passing before branch publication.

## Hard authority boundary

The implementation cannot autonomously:

- change canonical framework logic;
- change a threshold or model weight;
- change portfolio action;
- rewrite old candidates, admissions, forecasts, outcomes or adjudications;
- create retrospective prospective evidence;
- bypass Scientific Admission;
- execute a child experiment automatically;
- treat a technical/data failure as market falsification;
- inflate confidence merely because more observations arrived.

## Acceptance still required

This file records implementation status, not merge success.

Final acceptance requires:

1. branch diff review against then-current main;
2. PR CI green;
3. exact-head merge;
4. fresh-main readback of code/contracts;
5. production/manual Unified Adjudication run if workflow dispatch is available;
6. live state/backlog/proposal/health/handoff readback after that run.

Until those steps pass, status must not be upgraded to `MERGED_ACTIVE_VERIFIED`.
