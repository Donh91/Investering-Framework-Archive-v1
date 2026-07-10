# Forward Range Ledger Protocol v0.1

**Source date:** 2026-07-08  
**Activated:** 2026-07-10  
**Run ID:** FRLP_V0_1_20260708  
**Status:** CANONICAL OPERATIONAL PROTOCOL  
**Scope:** Cycle Navigator forward range ledger, baseline freeze, verified actuals, scoring, shadow re-anchor, kill monitor  
**Basis:** RMR v0.1, M5, M2 TRIAD, M1, M4  
**Authority:** Operational from the first resumed Cycle Navigator post after governance bindings B1-B9 were approved on 2026-07-10.

---

## 1. Executive status

```text
PROTOCOL_READY_WITH_GOVERNANCE_BINDINGS
Confidence: 85/100
Governance bindings B1-B9: APPROVED 2026-07-10
Operational start: first resumed Cycle Navigator post / CN #12
```

This protocol does not promote a range model or make a market call. It creates an append-only, audit-ready forward process.

---

## 2. Core operating principle

Every future official CN range must be:

```text
pre-week
source-backed
timestamped
baseline-compared
frozen at publication
scored only on verified actuals
separated from phase/structure scoring
subject to kill criteria
```

Internal and public layers remain separate:

```text
Internal CN = full ledger, baselines, shadow rows, scores, kill monitor.
Public CN = curated, familiar and lightweight X output.
```

---

## 3. Approved governance bindings

```text
B1 Human adjustment:
Midpoint shift <= 0.5 x ATR14. Written pre-week rationale mandatory.

B2 Minimum width:
Official range may never be narrower than DUMB_1.5 width.

B3 Official adjustment anchor:
DUMB_1.5. Alpha is still calculated versus DUMB_1.5 and DUMB_2.0.

B4 ATR formula:
Wilder ATR14. TR=max(H-L, abs(H-Cprev), abs(L-Cprev)).
Seed=SMA of first 14 TR. At least 60 settled daily candles. Whole-USD rounding.

B5 Week convention:
UTC daily candles. Week=[publication date; publication date+6], seven candles.
Post must exist before day-1 close.

B6 Actual source hierarchy:
FMP EOD-full primary; freshness-checked Kraken public OHLC fallback.
Difference >0.5% creates SOURCE_CONFLICT row.
Self-reported actuals are forbidden for scoring.

B7 LOW_CONFIDENCE cap:
Maximum 2 of any rolling 8 scored weeks.

B8 Shadow re-anchor:
Trigger-day close +/-1.5 x ATR14(trigger day).
Official and shadow are scored over the same sub-window [trigger+1; week_end].

B9 Kill windows:
K1-K3 use rolling 8 scored weeks, not calendar weeks.
K4-K8 are event-based.

B10 ETH:
Optional. An ETH row is created whenever an ETH range is published, under identical rules.
```

---

## 4. Forward ledger structure

The operational ledger contains 66 fields in three groups.

### Group F — frozen at publication

Contains forecast identity, publication timestamp and URL, official range, baselines, ATR, human adjustment, phase/structure, TRIAD state, confidence, scenario fields and shadow state.

Rules:

```text
Immutable after publication.
Correction = new row with CORRECTION and NOT_FOR_SCORING.
X timestamp + GitHub commit = double freeze proof.
```

### Group S — filled after the week

Contains verified actuals and scoring:

```text
Winkler alpha=0.10 and alpha=0.20
DUMB_1.5 / DUMB_2.0 / PREVWK scores
adjustment alpha
Jaccard
containment
breach days
direction bias
width ratio
separate phase/range/timing/rotation/warning scores
```

### Group M — monitor

Contains kill flags, data-quality flags and notes.

Allowed data-quality values:

```text
FULL
DEGRADED
DATA_MISSING
SOURCE_CONFLICT
CORRECTION
PRINT_GAP
```

---

## 5. Baseline calculation

Inputs use the last settled UTC daily candle before publication.

```text
DUMB_1.5 = anchor close +/-1.5 x Wilder ATR14
DUMB_2.0 = anchor close +/-2.0 x Wilder ATR14
PREVWK = min(low) / max(high) over the previous seven settled UTC candles
```

Rules:

```text
Both ATR baselines are centered on anchor close, never forecast midpoint.
Baselines are calculated before publication.
Baselines are committed with the published row and never recomputed retrospectively.
Missing data = DATA_MISSING / NOT_FOR_SCORING. No inference.
```

---

## 6. Official range protocol

```text
Baseline first.
Human adjustment stays inside B1.
Official width respects B2.
Rationale is written before publication.
No intra-week official range editing.
Scenario bands never replace official range.
LOW_CONFIDENCE weeks remain fully scored.
Missing official range = DATA_MISSING / NOT_FOR_SCORING.
```

Allowed public wording:

```text
Range: 61,000-69,000
Basis: BASELINE_1.5 + shift +0.3xATR
Confidence: NORMAL
```

Forbidden:

```text
Blended precision percentage
Unverified actuals
Official range updated intra-week
Shadow range described as new official range
```

---

## 7. Shadow re-anchor protocol

States:

```text
NORMAL_RANGE
TRANSITION_WATCH
REANCHOR_SHADOW_ACTIVE
RANGE_LOW_CONFIDENCE
OFFICIAL_REANCHOR_ALLOWED
```

`OFFICIAL_REANCHOR_ALLOWED` is unreachable in v0.1.

The shadow range:

```text
never changes the official range
is timestamped separately
is scored over the same remaining sub-window as the official range
has no execution authority
```

Promotion discussion is not permitted until at least eight scored shadow instances beat never-move on median Winkler. K8 kills the mechanism if at least eight instances are worse.

---

## 8. Scoring formulas

All percentage-normalized scores use baseline anchor close P0.

```text
Winkler_alpha = [(U-L) + (2/alpha)*max(0,L-actual_low) + (2/alpha)*max(0,actual_high-U)] / P0 * 100
```

Primary:

```text
alpha=0.10
```

Secondary:

```text
alpha=0.20
```

Additional:

```text
Jaccard = overlap length / union length
breach day = daily low < L OR daily high > U
containment = (7 - breach days) / 7 * 100
direction bias = (forecast midpoint - actual midpoint) / P0 * 100
width ratio = forecast width / actual width
adjustment alpha vs DUMB_1.5 = Winkler_DUMB15 - Winkler_CN
```

Positive adjustment alpha means the human adjustment added value.

---

## 9. Public Cycle Navigator output

Public X output keeps a lightweight, familiar layout.

Required blocks:

```text
1. Phase / Structure
2. Range Forecast
3. Prior Week Range Score vs Baselines
4. Pullback Weather
5. Rotation State
6. Shadow Observations
7. What Would Invalidate This Forecast
```

No blended overall score may hide a lost range week behind a strong phase call.

---

## 10. Weekly workflow

### Before publication

```text
Fetch settled UTC candles and pass anchor checks.
Calculate ATR14 and three baselines.
Choose official range and write adjustment rationale.
Record TRIAD, phase, structure, confidence and scenario state.
```

### At publication

```text
Publish X post.
Capture timestamp and URL.
Write frozen Group F row.
Commit raw post and row to GitHub.
```

### During the week

```text
Track breach days.
Evaluate transition and shadow triggers.
Append shadow rows when triggered.
Never edit official range.
```

### After week end

```text
Fetch and verify actuals.
Write Group S scores once.
Create scorecard.
Update kill monitor.
```

---

## 11. Kill criteria

```text
K1: Adjusted CN median Winkler worse than DUMB_1.5 over 8 scored weeks -> suspend adjustment layer; revert to pure baseline.
K2: CN loses to both DUMB_1.5 and DUMB_2.0 over 8 scored weeks -> full governance review.
K3: At least 2 total-miss weeks in 8 scored weeks -> immediate revert to baseline architecture.
K4: Self-actual used -> annul score and create integrity row.
K5: Blended public score returns -> non-compliance flag and correction.
K6: Width ratio >2.5 without SCENARIO tag -> overwide-gaming flag.
K7: LOW_CONFIDENCE >2/8 scored weeks -> confidence-gaming review.
K8: At least 8 shadow instances worse than never-move -> kill shadow re-anchor mechanism.
```

---

## 12. GitHub layout

```text
05_CYCLE_NAVIGATOR/posts/CN_YYYY-MM-DD_post##.md
05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv
04_MARKET_LEARNING/range_skill/scorecards/RANGE_SCORECARD_YYYY-W##.md
04_MARKET_LEARNING/range_skill/shadow_reanchor/SHADOW_REANCHOR_LOG_v0_1.csv
04_MARKET_LEARNING/range_skill/kill_monitor/RANGE_KILL_MONITOR_v0_1.csv
```

---

## 13. First-post checklist

```text
B1-B9 approved and logged
Settled data fetched and anchor checks passed
ATR14 and baselines frozen before post
Official range and rationale recorded
Range not narrower than DUMB_1.5
TRIAD and confidence logged
Shadow state logged
Invalidators written
X timestamp and URL captured
Frozen row committed to GitHub
No self-actuals
No blended score
```

---

## 14. Operational start

```text
First true forward row: CN #12
Protocol state: ACTIVE
Model state: FORWARD_TEST_ONLY
```

---

## 15. Boundary

```text
NO MARKET CALL
NO PORTFOLIO ACTION
NO RANGE MODEL PROMOTION
NO INTRA-WEEK OFFICIAL REANCHOR
NO SELF-ACTUAL SCORING
FORWARD TEST BEFORE PROMOTION
```
