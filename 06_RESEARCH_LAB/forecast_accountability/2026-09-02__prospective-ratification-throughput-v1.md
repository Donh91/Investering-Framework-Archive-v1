# Prospective Forecast Ratification Throughput v1

Date: 2026-09-02
Status: PROPOSED_IMPLEMENTATION
Authority: research / learning only

## Problem

The API-agent forecast family already had an explicit ratifier and a governance statement that unratified candidates require owner ratification before becoming `FROZEN_FORECAST_v1`. The production maintenance workflow materialized PENDING candidates and matured already-frozen forecasts, but did not provide an operational owner decision channel.

This created a growing PENDING population without a prospective terminal decision mechanism.

## Prospective cutover

The hard cutover is Control Plane commit:

`4057fde279ed0d8eea2df07da10543bda38ee8f8`

Commit time: `2026-09-02T09:56:53Z`.

Candidates created before this cutover are permanently:

`LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE`

They may remain archive/research context, but may not later be converted into forward evidence.

## New lifecycle

For candidates created at or after cutover:

1. materialize immutable `FORECAST_CANDIDATE_v1`;
2. process any already-recorded owner decision packet;
3. if no terminal decision exists, build an outcome-free `FORECAST_RATIFICATION_QUEUE_v1`;
4. the framework owner reviews only the queue and candidate record;
5. owner writes one append-only `FORECAST_RATIFICATION_PACKET_v2`;
6. the next maintenance run verifies candidate hash, decision time, Git recording time and decision scope;
7. `REJECT` becomes an append-only terminal record and produces no forecast;
8. `RATIFY` deterministically selects the latest qualifying baseline observation at or before owner decision time and freezes a forecast at the owner decision time;
9. supported price metrics receive `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1` at freeze;
10. exact and legacy maturation are physically separated.

## Timing contract

- decision SLA: 60 minutes after candidate creation;
- packet must be first recorded in Git no earlier than the declared decision time and no more than 15 minutes later;
- a packet outside either bound fails closed;
- no decision by the SLA becomes `EXPIRED_NO_OWNER_DECISION`;
- workflow execution time never becomes forecast freeze time.

The 60-minute SLA is a new prospective governance bound. It is not applied retrospectively and is intended to prevent later market movement from becoming hidden ratification information while leaving operational room for the external owner review.

## Outcome-blind owner surface

`LATEST_RATIFICATION_QUEUE.json` is produced without reading any outcome root.

Every candidate row explicitly declares:

- `outcome_data_included = false`.

Every valid ratification packet must declare:

- `outcome_blind = true`;
- `decision_basis_scope = [RATIFICATION_QUEUE, CANDIDATE_RECORD]`;
- `outcome_paths_read = []`;
- `self_promotion_allowed = false`.

The processor itself has no outcome-root input.

## Packet contract

Example shape only; values must come from the live queue/candidate at decision time.

```json
{
  "contract": "FORECAST_RATIFICATION_PACKET_v2",
  "candidate_id": "<candidate_id>",
  "candidate_sha256": "<sha256 of canonical candidate record>",
  "decision": "RATIFY or REJECT",
  "decision_at_utc": "<current owner decision time>",
  "authority": "CHATGPT_FRAMEWORK_OWNER",
  "owner_actor": "GPT-5.6 Sol",
  "outcome_blind": true,
  "self_promotion_allowed": false,
  "prospective_cutover_commit_sha": "4057fde279ed0d8eea2df07da10543bda38ee8f8",
  "decision_basis_scope": ["RATIFICATION_QUEUE", "CANDIDATE_RECORD"],
  "outcome_paths_read": [],
  "decision_rationale": "<brief falsifiable owner rationale>"
}
```

## Terminal dispositions

- `LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE`
- `EXPIRED_NO_OWNER_DECISION`
- `REJECTED_BY_OWNER`
- `RATIFIED_AND_FROZEN`

Terminal records are append-only and carry no portfolio, canonical-promotion, model-weight or self-promotion authority.

## Settlement

A ratified supported price forecast is frozen with:

- `frozen_at_utc = decision_at_utc`;
- `outcome_due_utc = decision_at_utc + frozen horizon`;
- latest available qualifying baseline at or before decision time;
- candidate and ratification hashes;
- baseline evidence hash;
- `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`;
- `FROZEN_AT_RATIFICATION_DECISION_PROSPECTIVE_ONLY`.

The API-agent Continuity workflow then runs exact settlement first and legacy maturation only on a physically generated non-exact subset.

## Non-goals

This change does not:

- ratify old backlog candidates;
- auto-promote model output;
- use outcomes in ratification;
- alter forecast direction or thresholds;
- change portfolio actions;
- prove forecast skill;
- retrospectively repair past unratified candidates.

## Acceptance gates

Before merge:

1. integration test RATIFY -> exact FROZEN at owner decision time;
2. baseline after decision is not selected;
3. REJECT is terminal and creates no forecast;
4. pre-cutover candidate cannot be ratified;
5. no-decision candidate expires after SLA;
6. backdated / late-Git-recorded packet fails closed;
7. queue contains no outcome data;
8. terminalization is idempotent;
9. existing candidate backlog tests pass;
10. existing exact settlement and historical replay guards pass;
11. broad architecture / continuity / automation CI passes;
12. independent adversarial review finds no unresolved P0/P1 issue.

## Scientific boundary

Successful ratification throughput only repairs prospective lifecycle integrity. It does not make the resulting sample statistically independent or sufficiently powered. Skill remains unproven until prospective outcomes satisfy the separate replication, settlement, baseline and effective-N gates.
