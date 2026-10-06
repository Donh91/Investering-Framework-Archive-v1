# EDGE-001 T2 Outcome Registry Method Repair v1.1

Status: BYTE_FROZEN_BEFORE_V1_1_EXECUTION
Date: 2026-10-07
Authority: RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY
Supersedes for future T2 scoring: family/censoring/identity mechanics of T2 v1 only. T2 v1 remains immutable as audit baseline.

## Reason for repair

Post-execution outcome-only audit of v1 found two material deterministic defects before any Framework-warning join or T3 scoring:
1. v1 family grouping used successive peak-to-peak distance instead of the already-frozen M6/charter trough-based independence rule.
2. threshold-crossed episodes that reached a continuity-segment boundary before rebound were silently dropped.

No warning performance, lead statistic or action result was inspected to choose this repair.

## R1, episode extraction and segment boundary

Within each continuity_segment_id, detect peak -> frozen threshold cross -> running trough exactly as v1.

If the threshold has crossed and the continuity segment ends before same-size rebound confirmation, emit the episode as RIGHT_CENSORED_AT_SEGMENT_END. Do not bridge the gap, infer a rebound or borrow any price from the next segment.

For a censored episode:
- threshold_cross_utc is observed and retained;
- trough_utc is the lowest observed eligible point from cross through the last row of that segment;
- rebound_utc=null;
- right_censored=true;
- censor_utc=last eligible timestamp of segment;
- censor_reason=CONTINUITY_SEGMENT_END_BEFORE_REBOUND.

At a segment boundary all causal state resets. The next segment begins independently.

## R2, family rule

Primary family rule is the frozen M6/charter rule:
- overlapping peak-to-trough windows are one family; OR
- a later candidate peak less than 14 calendar days after the prior family trough remains in the same family.

Operational deterministic grouping: sort episodes by peak_utc. Maintain family_end_trough_utc as the latest trough timestamp among episodes already assigned to the family. A candidate joins when candidate.peak_utc <= family_end_trough_utc OR candidate.peak_utc - family_end_trough_utc < 14 calendar days. When joined, update family_end_trough_utc=max(existing, candidate.trough_utc). Otherwise open a new family.

A continuity-segment boundary always prevents cross-gap family merging, regardless of calendar distance.

Sensitivity family gaps 7d and 30d may be generated later but cannot replace the 14d primary rule.

## R3, stable IDs

IDs are deterministic and namespaced. They do not depend on warning data.

episode_id = EDGE001_EP_{window}_{asset}_{grid}_{segment}_{peakUTC}_{crossUTC} with non-alphanumeric timestamp characters normalized.
family_id = EDGE001_FAM_{window}_{asset}_{grid}_{ordinal2}.
control_id = EDGE001_CTL_{window}_{asset}_VREV_{segment}_{p1FireUTC}.

Generated registry must assert global uniqueness of all IDs.

## R4, cross-asset cluster identity

Per-asset families are not inferential N.

For the primary inferential clustering layer, take BTC10 and ETH15 primary-grid families and construct cross-asset clusters outcome-only.

Families belong to one cross-asset cluster when their observed peak-to-trough intervals overlap. Transitive overlaps form one cluster. Families that do not overlap remain separate. A continuity gap does not create artificial overlap.

cluster_id = EDGE001_XCL_{window}_{ordinal2}.

This clustering is used only for independence accounting. It does not alter per-asset episode/family membership.

## R5, controls

V-reversal controls retain v1 causal definition and receive stable IDs. Controls that cannot be adjudicated before a continuity boundary are explicitly CONTROL_CENSORED, not silently negative or positive.

The known modern count of one primary V-reversal control remains a power limitation. No pooling or taxonomy change is permitted to rescue the three-control ladder floor.

## R6, immutable lineage

T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1.json remains preserved unchanged.
New artifact: T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_1.json.
New contract string: EDGE001_T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_1.

v1.1 must record parent v1 artifact SHA-256 and exact source SHA-256. A reconciliation section must report v1 versus v1.1 episode counts, family counts, censored episodes and cross-asset cluster counts.

## R7, hard guards

framework_warning_data_joined=false.
No Compass/protection/predecessor signal may be read by the generator.
Primary thresholds, P1/P2 definitions, source tape and windows remain unchanged.
No T3 statistic or action simulation is part of v1.1.

## Gate

T2B remains BLOCKED until v1.1 is generated, deterministic, reconciled and audited for contract compliance.

CLAIM_LEVEL=HYPOTHESIS
WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE