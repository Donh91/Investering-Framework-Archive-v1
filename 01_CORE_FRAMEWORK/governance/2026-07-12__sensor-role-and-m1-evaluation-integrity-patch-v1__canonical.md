# Sensor Role and M1 Evaluation Integrity Patch v1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** sensor authority / pullback evaluation integrity  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Depends on:** `06_RESEARCH_LAB/audit_summaries/2026-07-12__sensor-survival-timing-placebo-regime-audit-v1__canonical.md`

## Purpose

Freeze role separation and prevent denominator, overlap, latency and redundancy errors from re-entering future backtests or live interpretation.

## Binding sensor roles

```text
A1/A2: URGENCY_ONLY
A3: QUARANTINE_ZERO_EXECUTION_WEIGHT
C1/C2: LEAN_WARNING
D1/D2/D3: CONFIRMATION_OR_VETO
BTC.D B1: SHADOW_SURVIVAL_RECLAIM_CONTEXT
STABLECOIN_SUPPLY: LIQUIDITY_AVAILABILITY
NORMALIZED_DEX_ACTIVITY: REALIZED_ACTIVITY
CHAIN_ACTIVITY_BREADTH: SHADOW_CONFIRMATION
ALTCOIN_MARKET_BREADTH: INDEPENDENT_REQUIRED_AXIS
```

No A/C/D blended vote or composite score is authorized. D must not be counted as a second or third warning vote after A/C.

## C2 expansion boundary

C2 receives expanded forward row collection under the existing Pullback Edge outcome/test lineage. This is data expansion only.

```text
live authority increase: NO
threshold change: NO
new test: NO
new engine: NO
```

## M1 event-universe contract

Every future M1 or pullback-family result must report:

```text
events_total
events_eligible
events_excluded
exclusion_reason_by_event
denominator_used
event_window_definition
signal_attribution_method
```

A percentage without numerator and denominator is invalid for governance use.

## Attribution contract

Use one of:

1. non-overlapping event windows; or
2. one-to-one nearest eligible event attribution frozen before scoring.

One signal may not create multiple successes merely because event windows overlap. Related events may remain linked in notes, but independence and score counting are separate.

## Timing and availability contract

For every prospective sensor row preserve:

```text
source_timestamp
verification_timestamp
print_status
revision_status
operational_availability_timestamp
signal_timestamp
framework_acceptance_timestamp
```

Historical same-day availability may not be assumed when the source is delivered later. Latency variants must be tested when the median state duration is shorter than the operating cadence.

## Redundancy contract

DEX-volume change and DEX/supply-ratio change belong to one realized-activity family. They may not count as two confirmations in confluence, scores or narrative confidence.

## BTC.D reproducibility discrepancy

```text
frozen canonical B1 fires with price follow-through: 21
direct threshold recomputation: 22
additional date: 2025-03-04
status: SOURCE_CONFLICT_REPRODUCIBILITY_OPEN
```

The 21-row frozen package remains the historical owner until the exact warm-up, eligibility or date-boundary cause is independently resolved. The discrepancy does not authorize threshold adjustment or selective row choice.

## Authority boundary

This patch changes role and evaluation governance only. It does not change market state, portfolio state, allocations, thresholds or public claims automatically.
