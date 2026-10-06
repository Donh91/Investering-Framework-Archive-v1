# EDGE-001 T2B Signal Join and Provenance Gate v1

Status: FROZEN / BLOCKED_UNTIL_T2_ARTIFACT_EXISTS
Date: 2026-10-06
Authority: RESEARCH_ONLY

## Dependency

Required immutable input: T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1.json.
If absent or its framework_warning_data_joined field is not false, STOP.

## Non-negotiable join rule

T2B may annotate existing T2 episode/control IDs only. It cannot add, remove, merge, split, move or relabel outcome-defined membership.

## Current typed identity

Join COMPASS_PROTECTION_TRACKER_v1 rows under native decision_policy_version.
Eligible primary states: ELEVATED, HIGH, CONFIRMED.
BUILDING remains watch/control and cannot become a primary warning through the join.

Knowledge time for every scored typed row is max(issued_at_utc, first main-branch commit time proven to contain the row). Rows without commit binding cannot be A_PIT_VERIFIED.

## Predecessors

No predecessor is mapped to current typed semantics in v1.
Native predecessor rows may be attached in a separate discovery namespace with native owner/name and A/B/C/D evidence class.
C_RECONSTRUCTED predecessor evidence cannot upgrade primary Claim A.

## Attribution

Primary W=14d before the outcome-defined threshold cross. Sensitivity W=30d.
Warnings earlier than W are burden observations only.
No warning in W is recorded explicitly as NO_WARNING.

## Version handling

2026-09-25_DECISION_INTEGRITY_V3_2 and 2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0 remain distinct strata.
Any newly observed policy version creates a new stratum before scoring.

## Required output

For each frozen T2 family/control:
- immutable T2 ID;
- typed warning onset(s) in W with state, policy version, issued time, commit-bound knowledge time and source hash;
- BUILDING observations separately;
- native predecessor annotations separately;
- evidence class per material field;
- explicit NO_WARNING where applicable;
- source integrity exclusions;
- issue-to-commit lag where typed row exists.

## Prohibited

No lead statistic, hit rate, p-value, circular-shift result, action simulation or ladder upgrade in T2B. Those belong to T3 after the joined evidence pack is frozen.

LIVE_EXIT_RULE=NONE
CLAIM_LEVEL=HYPOTHESIS