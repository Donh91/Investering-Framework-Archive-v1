# EDGE-001 T2 Control Boundary Repair v1.2

Date: 2026-10-07
Status: FROZEN_BEFORE_V1_2_EXECUTION
Authority: RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY
Depends on: T2_OUTCOME_REGISTRY_METHOD_REPAIR_v1_1.md

## Reason and scope

The #1526 execution audit independently reproduced two control defects in the frozen v1.1 generator: unresolved end-of-tape controls disappear, and a qualifying adverse crossing at the P1 fire itself can later be mislabeled V_REVERSAL. All episode/family/cross-asset audits passed. Neither defect changes the actual historical control rows on the frozen tape. No Framework warning, lead statistic, action outcome or threshold search was used to select this repair.

This contract supersedes only the defective v1.1 control boundary implementation. Source tape, windows, grids, P1/P2, trough families, stable IDs, overlap clustering and warning semantics remain frozen. Both v1 and v1.1 outputs remain immutable audit artifacts.

## Frozen control evaluation

1. Include the P1 fire close in the adverse-threshold evaluation. If that close is already at or below 90% of the causal pre-fire BTC peak, the event cannot be a V-reversal control even if the next close recovers.
2. Evaluate eligible same-segment closes from the fire through the inclusive 14-day deadline. A BTC 10% crossing disqualifies the V-reversal; regaining the pre-fire peak before any crossing qualifies it. No next-segment price is read for the decision.
3. If no crossing or regain is observed and the current continuity segment ends before the deadline, emit CONTROL_CENSORED. This includes the final segment of the tape. Record censor_utc at the last eligible same-segment close and censor_reason as DATASET_END_BEFORE_CONTROL_DEADLINE or CONTINUITY_SEGMENT_END_BEFORE_CONTROL_DEADLINE.
4. If the same-segment tape reaches the deadline without recovery, do not invent a V-reversal or a censored positive control. The eligible positive/censored control census does not itself assert a warning failure.
5. Control IDs retain the frozen v1.1 identity scheme. Censor fields annotate uncertainty, not adverse or recovered outcomes.

## Artifacts and lineage

Generator: scripts/research/edge001_t2_outcome_registry_v1_2.py
Output: T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_2.json
Contract: EDGE001_T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_2
Parent v1 SHA-256 remains c8f8aa30502b909f016787161a661b2183f8ceef61c820cea00c53c5b70f71db.
Parent v1.1 SHA-256 must be b8ffeadecf4a1adf182eac8a5ab163d002af1237c1274cf3e867588977592882.
Source SHA-256 remains f3adc5716343c3a6e7dca812f4ca2d607abb5dd37495a7fa268ab41e5e889bd8.

## Acceptance and continuation

Run twice from one frozen head with byte-identical output. The independent audit must pass all source, parent, ID, extraction, censoring, family, transitive overlap and control fixtures. Compare with v1.1: all episode/family/cluster and comparator rows must remain identical; any actual control-row difference must be disclosed. No warning join or scoring is part of this execution.

Only after exact main artifact and audit readback may the subsequent T2B mission consider v1.2 as its repaired outcome membership input. Before an actual join, bind the T2B input to this exact artifact hash and preserve its IDs. This is dependency repair, not scoring or warning authority. Current typed historical Claim A remains NOT_TESTABLE_AT_PIT; Claim B remains NOT_TESTABLE_NOW.

CLAIM_LEVEL=HYPOTHESIS
WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
