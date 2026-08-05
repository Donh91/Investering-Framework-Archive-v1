# Experiment Lifecycle & Execution Plane v1

**Status:** shadow-only operational architecture  
**Effective date:** 2026-08-05  
**Repositories:**

- Control plane: `Donh91/Investering-Framework-Archive-v1`
- Execution plane: `Donh91/Eksperimenter-framework-`

## Purpose

Turn new observations, forecast misses, sensor conflicts and unusual measurable combinations into prospective experiments that can create value later, without giving an unproven idea authority today.

The architecture deliberately allows ideas that initially look weak, strange or premature. Novelty is not a rejection reason. An idea is rejected only when it cannot be measured, cannot be falsified, violates an authority boundary, duplicates an existing semantic specification, or requires fabricated data.

## Core separation

### Control plane

Owns:

- candidate registration and semantic deduplication;
- immutable experiment specifications;
- prospective observations;
- frozen forecasts;
- outcome maturation;
- lifecycle registry;
- weekly adjudication context;
- governance decisions.

### Execution plane

Owns:

- independent request validation;
- deterministic replication of sensor firing logic;
- execution receipts;
- raw research artifacts and one-shot collectors;
- zero canonical, market, model-weight or portfolio authority.

### Remediation maturation

Remediation Maturation Engine remains separate. It handles workflow and system defects. Experiment Lifecycle handles market, sensor, sequence and data-quality hypotheses. A failed workflow is not a market experiment, and a failed market hypothesis is not a remediation task.

## Candidate sources

Candidates may originate from:

- Daily Director forecast candidates;
- Daily Director explicit experiment candidates;
- forecast or sequence misses;
- repeated sensor disagreement;
- unexpected causal ordering;
- data-quality anomalies;
- legacy hypotheses that encounter new prospective evidence;
- newly observed combinations of available metrics.

## Idea-bank policy

The latent candidate bank has no numerical capacity limit and no age-based expiry.

A candidate may remain:

- `PROPOSED`
- `WAITING_FOR_DATA`
- `WAITING_FOR_MAPPING`
- `INCUBATING`

for as long as necessary. It is revisited when the required metric, mapping, regime or event becomes observable.

The resource-intensive lane is bounded. By default, no more than five new frozen experimental forecasts may be created per Daily Director run. This separates broad creativity from controlled execution cost.

## Legacy Sensor Pair continuity

The frozen `SENSOR_PAIR_DISCOVERY_LAB_V0_1` catalog and its first prospective 2026-07-14 run remain valid historical forward evidence. They are not rewritten or retroactively rescored by this architecture.

The eight catalog concepts are registered in the new latent idea bank as `WAITING_FOR_MAPPING` concepts. Abstract sensor labels must later be mapped to explicit source-backed metric paths through a new linked candidate. The original concept stays immutable, preserving the possibility that an initially awkward combination becomes useful under a later data architecture or market regime.

No retrospective outcome is created merely because the old rows are now available. Any maturation adapter must use only later source-backed observations and preserve the original frozen timestamp and controls.

## Mandatory candidate fields

Every explicit experiment candidate must include:

- title;
- experiment kind;
- measurable hypothesis;
- explicit falsifier;
- fixed horizon;
- metric paths;
- deterministic component operators;
- target or `NONE` for pure data-quality tests;
- regime dependency;
- novelty reason;
- revisit conditions;
- current evidence basis.

## Supported experiment kinds

- `SENSOR_COMBINATION`
- `FORECAST_TEST`
- `SEQUENCE_TEST`
- `DATA_QUALITY_TEST`

## Sensor operators

- `GT`
- `LT`
- `DELTA_PCT_GT`
- `DELTA_PCT_LT`
- `POSITIVE`
- `NEGATIVE`
- `AVAILABLE`
- `CHANGED`

These deliberately remain simple and auditable. A complicated model may be proposed later, but v1 first records whether simple measurable conjunctions add value.

## Prospective freeze rule

When a candidate fires and has a valid target, the control plane may create a `FROZEN_FORECAST_v1` row.

The row is:

- prospective;
- immutable;
- experimental-only;
- bounded to a fixed outcome horizon;
- matured by the existing Outcome Maturation Engine;
- unable to change framework state or portfolio action.

No retrospective signal row may be created.

## Cross-repository replication

The control plane publishes an immutable dispatch manifest. The execution plane fetches public requests, verifies request hashes and independently recomputes whether the supplied sensor components fired.

Receipt states include:

- `REPLICATED_FIRED`
- `REPLICATED_NOT_FIRED`
- `REPLICATED_WAITING_FOR_DATA`
- `REPLICATION_MISMATCH`

Receipts are synchronized back to the control plane as audit evidence.

## Lifecycle states

- `PROPOSED`
- `WAITING_FOR_DATA`
- `WAITING_FOR_MAPPING`
- `INCUBATING`
- `FIRED_NO_TARGET`
- `FIRED_FORECAST_PENDING`
- `WAITING_FOR_MATURITY`
- `MATURED_SUPPORTED`
- `MATURED_NOT_SUPPORTED`
- `MATURED_INCONCLUSIVE`
- `KILLED`
- `GOVERNANCE_REVIEW_PERMITTED`
- `CLOSED`

Not all states are automatically assigned in v1. The registry starts with prospective and maturation states. Final adjudication remains weekly and governance-bound.

## Kill criteria

A candidate may be killed only for a documented reason:

- semantic duplicate;
- non-falsifiable specification;
- unavailable identity or unsupported metric lineage;
- fabricated or reconstructed evidence requirement;
- permanent schema incompatibility;
- concentrated severe-failure mode after sufficient sample;
- explicit governance closure.

Age, low narrative appeal or initial absurdity are not kill criteria.

## Promotion boundary

No candidate, firing, forecast, outcome or replication receipt may automatically:

- become canonical;
- change a gate;
- change a model weight;
- alter framework state;
- create a trade;
- change portfolio action.

Promotion requires mature prospective evidence, controls, independent event windows and explicit governance review.
