# EDGE-001 T2 Outcome-Only Registry Contract v1

Status: FROZEN_BEFORE_GENERATED_REGISTRY
Authority: RESEARCH_ONLY
Date: 2026-10-06

## Purpose

Freeze episode membership and causal price-only comparators before any Framework warning join.

## Source

06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz

Windows remain separate: ALTSEASON_2020_2021 and MODERN_ANALOGUE_2025_2026. continuity_segment_id breaks all causal state; no cross-gap peak borrowing.

## Adverse grids

BTC: 10, 15, 20 percent.
ETH: 15, 20, 30 percent.

Detection uses the existing deterministic peak -> threshold -> trough -> same-size rebound-confirmed zigzag procedure, generalized only to the preregistered EDGE-001 grids. No Framework state is an input.

Primary family rule: 14 calendar days. The generated registry retains episode detail and 14d families.

## P1/P2

P1 5 percent and P2 3 percent are causal running-peak drawdown timelines.
Running peak is maximum eligible hourly close since segment/reset.
After a fire, comparator remains disarmed until an eligible hourly close regains or exceeds the prior peak.
A continuity segment change resets the causal peak and arms a new segment.

## V-reversal control

For primary BTC 10 percent scope: a P1 fire is V_REVERSAL when price regains the causal pre-fire peak within 14 calendar days, in the same continuity segment, without first crossing the BTC 10 percent adverse threshold from that peak.

## Independence

T2 is per-asset outcome membership. Cross-asset overlapping clusters are resolved only after both asset registries exist and before inferential scoring.

## Hard guard

framework_warning_data_joined must equal false.
No ELEVATED/HIGH/CONFIRMED, predecessor signal, Compass row or M6 warning can affect membership.

## Generator

scripts/research/edge001_t2_outcome_registry.py

## Generated artifact

06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1.json

The generated source_sha256 binds the exact compressed input bytes.

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
CLAIM_LEVEL=HYPOTHESIS