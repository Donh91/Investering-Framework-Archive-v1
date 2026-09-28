# Cycle Navigator public score and lineage - canonical retrieval card

**Status:** ACTIVE_ROUTING_CARD  
**Purpose:** remove ambiguity between the public Cycle Navigator series, migration-era machine issue numbers, frozen forecasts and completed-week scores.

## The rule that must be followed

**Never resolve a Cycle Navigator precision score from `issue_number` alone.**

From W36 onward, the migration-era machine counter is one issue ahead of the actually published public series:

| Forecast week | Public CN | Machine issue |
|---|---:|---:|
| 2026-W36 | #23 | #24 |
| 2026-W37 | #24 | #25 |
| 2026-W38 | #25 | #26 |
| 2026-W39 | #26 published / completed | #27 |
| 2026-W40 | #27 current projection | #28 |

This offset created the recurring false conclusion that a public issue had no frozen ranges. The data was present in the immutable published post and range ledger, while the same-number machine freeze referred to a different forecast week.

## Canonical retrieval order

For **"Cycle Navigator precision", "score from last week", "today's CN score", "frozen ranges" or "how accurate was CN"**:

1. Read `public_series/CN_PUBLIC_SERIES_INDEX.json`.
2. Resolve the public issue by **forecast week + immutable publication**, not by machine issue number.
3. Read the scorecard named by `latest_completed_score.scorecard_path`.
4. For frozen/public ranges, follow the immutable published post and `forward_range_ledger/`.
5. For realized range scoring, follow `corrections/YYYY/Www/RANGE_SCORE_CORRECTION.json` and the 168h weekly actuals.
6. Use machine scorecards only as outcome/calibration evidence when their claim lineage is explicitly mapped to the public issue.
7. Never blend PRICE RANGE and MARKET/STRUCTURE into an overall percentage unless a stable prospective aggregation contract exists.

## Current completed public score

**CN #26, forecast week 2026-W39**

- MARKET / STRUCTURE: **60%** - legacy pre-v2 method, closed and retained for audit
- PRICE RANGE aggregate: **81.85%**
- BTC ranges: **78.66%**
- ETH ranges: **85.05%**
- Intraday D1-2: **83.19%**
- Intraday D3-4: **86.35%**
- Intraday D5-7: **76.02%**
- Overall combined: **UNDEFINED**, deliberately not synthesized

Canonical scorecard:

`public_scorecards/2026/W39/CN26_PUBLIC_SCORECARD.json`

Immutable public forecast:

`published/2026/CYCLE_NAVIGATOR_26_X_PUBLISHED_2026-09-21.md`

## Current public issue

The current W40 public projection is **CN #27**.

Its underlying migration-era machine package is W40 / machine issue #28. CN #27 is currently approved but not yet user-confirmed as published.

CN #27 starts **Market / Structure v2** with five fixed, non-duplicative dimensions:

`REGIME | LEADERSHIP | FIRST_HANDOFF | DEEPER_TRANSMISSION | BREADTH_PERSISTENCE`

CN #26's 60% remains a legacy score and must not be treated as a like-for-like v2 baseline. The first comparable v2 outcome score is produced after W40 completes.

## Frozen-score versus outcome-score vocabulary

- **FORECAST FREEZE** = the claims/ranges fixed before outcome evaluation.
- **COMPLETED SCORE** = evaluation after the matching forecast week has matured.
- **CALIBRATION** = learning from the difference between freeze and outcome.
- **PUBLIC CN NUMBER** = number shown in the actually published public series.
- **MACHINE ISSUE NUMBER** = internal migration-era counter. It is not a safe public join key.

## Master Monday boundary

Master Monday supplies completed-week evidence and calibration context. It does not redefine the identity of the public CN issue. When Master Monday or another consumer asks for CN precision, it must consume this public-series index/scorecard rather than infer identity from the weekly machine folder.

## No-hindsight invariant

Recovered ranges are valid only when they come from an immutable prospectively published CN artifact. The W38 CN #25 ranges meet this requirement and are already preserved in the forward range ledger and correction artifact. Historical machine nulls are not allowed to erase that published freeze.
