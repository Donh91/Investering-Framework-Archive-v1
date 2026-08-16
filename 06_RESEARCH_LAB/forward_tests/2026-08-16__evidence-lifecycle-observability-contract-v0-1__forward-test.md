# Evidence Lifecycle Observability Contract v0.1

**Dato:** 2026-08-16  
**Status:** FORWARD_TEST  
**Område:** Research Lab / evidence lifecycle / latency attribution  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `AGENTS.md`, `.agents/skills/prospective-evidence-ledger/SKILL.md`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`  

## Purpose

Repair the observability gap identified by the bounded lifecycle review without changing market rules, thresholds, weights, policy semantics, scorers, portfolio logic or existing test definitions.

This contract does not create a new engine, market sensor, score or decision rule. It defines audit metadata that existing evidence-producing pipelines may emit prospectively so later latency attribution can distinguish source, retrieval, provenance, acceptance, policy-evaluable and decision-evaluation delay.

## Core rule

Lifecycle timestamps are evidence, not inferred history.

A timestamp may be populated only when the producing system has an explicit receipt or event that proves the corresponding lifecycle transition. Git commit time, report generation time, model narrative time and retrospective estimates are not substitutes.

Historical timestamps must not be reconstructed merely to fill the schema.

## Lifecycle receipt contract

Each instrumented evidence run should emit or append a receipt containing, where genuinely observable:

```yaml
contract: EVIDENCE_LIFECYCLE_RECEIPT_v0_1
source_run_id:
evidence_lane:
observation_time:
source_available_time:
retrieval_start_time:
retrieval_complete_time:
normalization_time:
provenance_validation_time:
owner_grade_time:
framework_ingest_time:
framework_acceptance_time:
policy_evaluable_time:
decision_evaluation_time:
action_divergence_time:
source_lineage:
artifact_hash:
validator_run_id:
contract_version:
repo_head_sha:
```

Each lifecycle field must carry one status:

```text
KNOWN
DERIVED_WITH_RECEIPT
UNAVAILABLE
CONTRACT_BLOCKED
NOT_APPLICABLE
```

`DERIVED_WITH_RECEIPT` is allowed only when a deterministic transformation from an explicit receipt is documented. It must never mean model inference or interpolation.

## Acceptance semantics

`framework_acceptance_time` is the first explicit event at which the existing framework acceptance contract records the evidence as accepted for its intended lane.

It is not:

- Git commit time;
- artifact publication time;
- DATA PING retrieval time;
- report generation time;
- a later analyst statement that the evidence was usable.

If no explicit acceptance event exists, record `UNAVAILABLE`.

## Policy-evaluable semantics

`policy_evaluable_time` may be populated only when the existing frozen policy contract can actually be evaluated from accepted evidence.

If the relevant evaluator or mapping does not exist under the frozen contract, record:

```text
status: CONTRACT_BLOCKED
```

Do not invent sensor-to-policy mappings, policy evaluators or market semantics to create this timestamp.

## Decision evaluation semantics

`decision_evaluation_time` is the timestamp of the actual existing decision/policy evaluation event.

Director-context generation, weekly-report generation, Git commits and narrative analysis are not valid substitutes unless the owner contract explicitly defines them as the decision evaluation event.

## FNP linkage

Existing FNP rows may reference a lifecycle receipt ID when the owner schema already permits a reference or when a non-invasive companion receipt can preserve the linkage without changing frozen FNP semantics.

Permitted attribution dimensions are descriptive only:

```text
SOURCE
RETRIEVAL
NORMALIZATION
PROVENANCE
ACCEPTANCE
POLICY
DECISION
CONTRACT_GAP
UNKNOWN
```

This contract does not change FNP classifications, scoring, horizons or promotion logic.

## Ordering validation

Where two timestamps are both observable, validators should reject impossible lifecycle ordering. Examples:

```text
retrieval_start_time <= retrieval_complete_time
retrieval_complete_time <= normalization_time
normalization_time <= provenance_validation_time
framework_ingest_time <= framework_acceptance_time
framework_acceptance_time <= policy_evaluable_time
policy_evaluable_time <= decision_evaluation_time
```

The validator must allow legitimate parallel stages and missing stages. It must not fabricate ordering by populating unavailable fields.

## Prospective-only rule

Instrumentation begins prospectively from merge/activation.

Old evidence may be linked only where exact historical receipts already exist. No retrospective timestamp interpolation, backdating or synthetic completion is allowed.

## Success criteria

The repair is successful when a prospective sample can support end-to-end attribution for materially relevant evidence runs and can explicitly distinguish observed delay from unavailable or contract-blocked delay.

A future Permit Latency Attribution Audit may consume these receipts only after sufficient prospective rows exist.

## Non-goals

This repair must not:

- create a new market engine or shadow layer;
- change market rules, gates, thresholds or weights;
- change portfolio actions;
- create a policy evaluator;
- repair missing policy semantics by inference;
- reinterpret source rows as outcome rows;
- convert missing timestamps into zero delay;
- retroactively manufacture lifecycle history.

## Validation status fields

Every receipt consumer should preserve:

```yaml
row_validity:
coverage_readiness:
edge_or_promotion_status:
```

Observability PASS is not evidence of market edge and does not authorize promotion.

## Kill / modification criteria

Modify or suspend this instrumentation if it:

- increases false timestamp precision;
- causes retrospective reconstruction to be treated as observed history;
- changes frozen evidence or policy semantics;
- becomes a parallel decision engine;
- materially increases pipeline failure rate without producing usable attribution rows;
- duplicates an existing owner receipt without adding lifecycle observability.

## Next research sequence

After sufficient prospective receipts exist:

1. rerun Permit Latency Attribution Audit;
2. attribute delay to observed lifecycle stages and contract gaps;
3. only then continue to fake-rotation falsification and transmission-ordering research.

Until then, additional latency conclusions remain bounded by partial lifecycle observability.
