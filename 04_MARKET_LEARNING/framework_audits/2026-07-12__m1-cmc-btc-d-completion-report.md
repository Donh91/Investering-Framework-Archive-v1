# M1 Pullback Weather Replay — CMC BTC.D Completion

**Date:** 2026-07-12  
**Run:** M1_CMC_B1_COMPLETION_20260712  
**Status:** RESEARCH_RESULT_NO_PROMOTION

## Mission

Complete the previously missing pre-registered B1 leg using the CoinMarketCap direct-source convention without changing the threshold or retrospectively retuning the event universe.

## Frozen B1 definition

```text
B1 condition:
BTC.D(t) - BTC.D(t-5 calendar days) >= +0.75 percentage point

Fire:
rising edge only

Source:
CMC_DIRECT_SOURCE_CONVENTION

Evaluation window:
2025-03-01 through 2026-07-07
```

All required dates in the M1 evaluation window exist. The only CMC source gap is 2023-01-05.

## Standalone B1 result

```text
Rising-edge fires: 22
TRUE_PRE: 5
IN_EVENT_PREC12: 1
IN_EVENT_LATE: 14
False alarms: 2
Wave recall before/at C5: 5/9 = 55.56%
>=Storm recall before/at C12: 1/4 = 25.00%
Detected >=Storm event: PW07
Earliest PW07 lead to C12: 20 days
```

B1 does not satisfy the pre-registered >=Storm recall requirement of 0.70. Its standalone early-warning discrimination is weak in this sample.

## Core conjunction test

Using the supplied A/C rising-edge dates, without threshold changes:

| Model | Window | Alerts | False | Wave recall | >=Storm recall | Median storm lead |
|---|---:|---:|---:|---:|---:|---:|
| A+C | 3d | 5 | 0 | 3/9 | 2/4 | 9d |
| A+B+C | 3d | 2 | 0 | 1/9 | 0/4 | n/a |
| A+C | 5d | 8 | 0 | 5/9 | 4/4 | 7d |
| A+B+C | 5d | 3 | 0 | 1/9 | 1/4 | 3d |
| A+C | 10d | 11 | 2 | 6/9 | 4/4 | 8.5d |
| A+B+C | 10d | 5 | 1 | 3/9 | 1/4 | 3d |

Adding B1 reduced recall rather than adding unique early-warning value. Under the declared CMC convention, the strict three-leg core hypothesis is not supported in this sample.

## Placebo-shift attack

B1 dates were shifted by ±30/60/90 days without changing the event universe.

The actual series detected 1/4 >=Storm events. The -30-day placebo detected 4/4, while +60 and +90 detected 3/4.

This does not prove B1 has no value. It demonstrates that event density and phase alignment can manufacture attractive lead results. Loosening the threshold after seeing this result is prohibited threshold shopping.

## Role interpretation

```text
BTC.D B1 as early pullback warning:
NOT_SUPPORTED_IN_SAMPLE

BTC.D as rotation-survival / reclaim / veto context:
REMAINS_PLAUSIBLE_AND_TESTED_IN_M4

BTC.D as standalone trade trigger:
FORBIDDEN
```

## Source-integrity limitation

The M1 PDF states 151 rising-edge fires:

```text
A: 71
C: 38
D: 42
```

The supplied row CSV contains 81 warning rows:

```text
A: 48
C: 16
D: 17
```

Therefore the B1 leg is directly reproducible, while A/C/D combinations are reproducible only against the 81-row export. The original aggregate cannot be independently regenerated without the daily signal table or generating script.

## Final status

```text
M1_CMC_B_LEG_COMPLETION: COMPLETE
M1_STRICT_3_LEG_HYPOTHESIS: NOT_SUPPORTED_IN_SAMPLE
M1_ORIGINAL_REPORT_EXACT_REPRODUCTION: PARTIAL_SOURCE_CONFLICT
RULE_RATIFICATION: NONE
```
