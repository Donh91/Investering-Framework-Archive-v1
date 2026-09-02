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

Candidates created before this cutover are permanently hindsight-ineligible. A single or byte-identical legacy candidate ID is terminalized as:

`LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE`

A legacy candidate ID that already exists at multiple paths with divergent bytes is not repaired or collapsed to an arbitrary winner. The entire ID-group is terminalized as:

`LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE_HINDSIGHT_INELIGIBLE`

with all observed variant paths, hashes and creation timestamps retained in the terminal record and `ratification_allowed=false`.

Any candidate ID appearing at multiple paths when any member is post-cutover fails closed as `POST_CUTOVER_DUPLICATE_CANDIDATE_ID`, even when bytes are identical. Prospective occurrence identity must therefore be one immutable record at one path.

The current materializer already binds new candidate identity to `receipt.output_hash + forecast index + candidate payload` and scans the full pending tree for an existing ID, so the duplicate-ID condition discovered in CI is classified as legacy archive debt rather than accepted prospective behavior.

## New lifecycle

For candidates created at or after cutover:

1. materialize immutable `FORECAST_CANDIDATE_v1`;
2. process any already-recorded owner decision packet;
3. if no terminal decision exists, build an outcome-free `FORECAST_RATIFICATION_QUEUE_v1`;
4. the framework owner reviews only the queue and candidate record;
5. owner writes one append-only `FORECAST_RATIFICATION_PACKET_v2`;
6. the next maintenance run verifies candidate hash, candidate Git first-add time, decision time, packet Git first-add time and decision scope;
7. `REJECT` becomes an append-only terminal record and produces no forecast;
8. `RATIFY` deterministically selects the latest qualifying baseline observation at or before owner decision time and freezes a forecast at the owner decision time;
9. supported price metrics receive `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1` at freeze;
10. exact and legacy maturation are physically separated.

## Timing contract

- candidate `created_at_utc` must be at or before its first Git-add timestamp and no more than 15 minutes earlier;
- a prospective candidate must exist at exactly one repository path;
- owner decision may not precede the candidate's first Git-add time;
- decision SLA: 60 minutes after candidate creation;
- packet must be first recorded in Git no earlier than the declared decision time and no more than 15 minutes later;
- a candidate or packet outside its recording bound fails closed;
- no decision by the SLA becomes `EXPIRED_NO_OWNER_DECISION` only after candidate Git provenance is available;
- a just-materialized untracked candidate within its SLA remains `AWAITING_OWNER_DECISION` and is never terminalized from an unverifiable Git timestamp;
- workflow execution time never becomes forecast freeze time.

The 60-minute SLA and 15-minute recording tolerances are new prospective governance bounds. They are not applied retrospectively and are intended to prevent later market movement from becoming hidden ratification information while leaving operational room for the external owner review.

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

The legacy direct ratifier CLI is disabled. Freeze logic remains an internal library used by `process_forecast_ratifications.py`; production writes must pass through the processor's Git-timing and terminal-state validation.

## Terminal dispositions

- `LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE`
- `LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE_HINDSIGHT_INELIGIBLE`
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
- choose a canonical winner among divergent legacy candidate records;
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
5. divergent pre-cutover duplicate ID is quarantined without choosing a variant;
6. any post-cutover duplicate ID fails closed;
7. no-decision candidate expires after SLA;
8. candidate and packet Git anti-backdating bounds are enforced;
9. queue contains no outcome data;
10. direct ratifier CLI cannot write;
11. terminalization is idempotent;
12. existing candidate backlog tests pass;
13. existing exact settlement and historical replay guards pass;
14. broad architecture / continuity / automation CI passes;
15. independent adversarial review finds no unresolved P0/P1 issue.

## Scientific boundary

Successful ratification throughput only repairs prospective lifecycle integrity. It does not make the resulting sample statistically independent or sufficiently powered. Skill remains unproven until prospective outcomes satisfy the separate replication, settlement, baseline and effective-N gates.
