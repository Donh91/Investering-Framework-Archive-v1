# Phase 1 — Framework Intelligence Live Parallel Shadow Contract v1

Status: ACTIVE_WHEN_MERGED
Authority: RESEARCH_ONLY_SHADOW
Canonical market authority: NONE
Portfolio authority: NONE
Live Master Monday influence: NONE
Cycle Navigator influence: NONE

## Purpose
Run the Framework Intelligence / Consultation layer every Monday after the existing weekly package and Unified Experimental Lifecycle Adjudication have completed, while keeping its output completely isolated from live conclusions.

Phase 1 measures whether the framework consistently uses its own accumulated learning better than the current weekly path, without granting that learning new authority.

## Timing
- Existing market evidence freeze remains authoritative.
- Existing Master Monday machine package remains unchanged.
- Unified Experimental Lifecycle Adjudication may finish later in the morning.
- Phase 1 runs after adjudication and may read only already-created repository evidence.
- Phase 1 output is observational. It MUST NOT be consumed by the current Master Monday or Cycle Navigator workflow.

## Mandatory provenance
Each Phase 1 run records exact paths, blob/content hashes where available from the source payload, generated timestamps, ISO week, and whether the source existed for the same completed week.

A missing or mismatched weekly source remains missing. No later evidence may be substituted silently.

## Duplicate control
Raw experiment candidate count is never treated as independent evidence. Semantic duplicates are separated from qualified independent candidates. Specialist commentary is not an evidence event.

## Consultation outputs
The layer may emit only:
- NO_MATERIAL_LEARNING
- WEEKLY_ANALYSIS_CONTEXT
- CONTRADICTION_CONTEXT
- RANGE_CONTEXT
- METHOD_IMPROVEMENT_CANDIDATE
- EXPERIMENT_ONLY
- NOT_EVALUABLE

It may record `would_offer_to_master_monday`, but `live_consumed` MUST remain false throughout Phase 1.

## Required observations
Each weekly run records:
1. Weekly package status and experiment-registry status reported by that package.
2. Matching adjudication availability.
3. Raw vs duplicate-adjusted candidate counts.
4. Lifecycle-state counts.
5. RANGE-family state, including replication limitations.
6. Contradictions between weekly package claims and actually available shadow evidence.
7. Information-utilization misses.
8. Bounded consultation notes.
9. Scientific-firewall status.
10. Complexity/compute footprint.

## Hard gates
- ZERO_LIVE_MASTER_MONDAY_INFLUENCE
- ZERO_CYCLE_NAVIGATOR_INFLUENCE
- ZERO_CANONICAL_PROMOTION
- ZERO_PORTFOLIO_AUTHORITY
- ZERO_DUPLICATE_EVIDENCE_INFLATION
- ZERO_RETROSPECTIVE_FORECAST_CREATION

Any violation blocks Phase 2.

## Minimum observation period
Default Phase 1 window: three completed weekly observations. A severe integration defect may extend the window. Phase 2 requires an explicit later decision and is never automatic.

## Phase 2 readiness
After at least three completed observations, Phase 1 may recommend `READY_FOR_PHASE2_REVIEW` only when:
- every hard gate passed;
- source binding was valid each week or missingness was explicit;
- consultation added material context in at least two weeks OR correctly returned no-material-learning;
- no unbounded compute path appeared;
- duplicate-adjusted family handling remained stable;
- no forecast-skill claim exceeded scientific admission status.

Otherwise the state is `CONTINUE_PHASE1` or `NEEDS_FIX`.
