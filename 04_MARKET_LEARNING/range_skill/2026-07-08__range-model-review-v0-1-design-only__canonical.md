# Range Model Review v0.1 — Design Only

**Date:** 2026-07-08  
**Run ID:** RMR_V0_1_20260708  
**Status:** CANONICAL DESIGN EVIDENCE  
**Scope:** Range-model redesign, forward-test architecture, scoring layout, verified actuals governance, re-anchoring state machine  
**Mode:** DESIGN_ONLY  
**Trigger:** M5_DEGRADED_20260708  
**Boundary:** No market call. No portfolio action. No rule ratification. No model promotion. No retuning on M5's 14 rows.

---

## 1. Executive verdict

```text
RANGE_MODEL_REVIEW_READY_FOR_FORWARD_TEST
Confidence: 76/100
```

RMR v0.1 is approved as design evidence, not as a promoted model.

Design purpose:

```text
Make future range skill measurable, falsifiable and cleanly separated from phase/structure skill.
```

Core design components:

```text
A. Baseline floor that can be introduced immediately without skill claim.
B. Bounded human adjustment layer, forward-tested through adjustment alpha.
D. Shadow-only re-anchoring state machine for transition failures.
F. LOW_CONFIDENCE range state with gaming controls.
```

No new backtest was run. No model was retuned on M5's 14 rows.

---

## 2. Failure decomposition

RMR splits the M5 range failure into two groups.

### Forward-test only problems

```text
Placement error: HIGH severity
Transition lag: HIGH severity
```

Evidence:

```text
CN02 0% containment
CN03 Jaccard 0.000
April upside transition: CN anchored too low
May-June downside transition: CN anchored too high
```

These can only be addressed by forward-tested design. They must not be fixed by retrospective tuning.

---

### Fix-now integrity / layout problems

```text
Verified actuals only
Winkler + breach scoring block
Phase/range score separation
No blended Overall Weekly Score
No self-actuals for public precision
```

These can be implemented immediately because they are integrity and scoring-layout changes, not skill claims.

---

## 3. Architecture verdicts

### A. PURE_BASELINE_DISCIPLINE

```text
Status: KEEP as interim floor
```

Inputs:

```text
pre-week anchor close
ATR14
```

Output:

```text
DUMB_1.5 and DUMB_2.0 statistical bands
commentary separate
```

Rationale:

```text
Guarantees baseline transparency and prevents unmeasured discretionary anchoring.
```

---

### B. ATR_PLUS_HUMAN_ADJUSTMENT

```text
Status: NEEDS_FORWARD_ROWS
Primary forward candidate
```

Design:

```text
Official range = ATR baseline plus bounded human center shift
Proposed bound: <=0.5 x ATR
Range never narrower than 1.5 x ATR
Written pre-week rationale required
```

Skill metric:

```text
adjustment_alpha = CN Winkler - DUMB_1.5 Winkler
```

Interpretation:

```text
Human range judgment becomes falsifiable each week.
```

Boundary:

```text
Bound needs governance binding before use.
No promotion before forward rows.
```

---

### C. REGIME_ADAPTIVE_WIDTH

```text
Status: SHADOW_ONLY
```

Reason:

```text
Possible retune risk because calm/flush width mapping may be derived from the same evidence family.
```

---

### D. TRANSITION_REANCHOR_SHADOW

```text
Status: SHADOW_ONLY
```

Inputs:

```text
TRIAD state from M2
breach count
```

Output:

```text
shadow range only
official range unchanged
```

Purpose:

```text
Instrument the documented transition-anchoring failure without introducing official hindsight-tuned re-anchoring.
```

---

### E. TWO_RANGE_OUTPUT

```text
Status: NEEDS_FORWARD_ROWS
```

Output:

```text
Core range + scenario band
Both must be scored
Scenario can never replace official range score
```

---

### F. NO_RANGE_UNTIL_REANCHOR / LOW_CONFIDENCE

```text
Status: KEEP as condition state
```

Use:

```text
Range may be published as LOW_CONFIDENCE in transition states
It is still scored
Frequency cap prevents opt-out gaming
```

---

## 4. Recommended composite challenger

The practical forward-test design is:

```text
RMR_COMPOSITE_CHALLENGER_v0.1
```

Components:

```text
A = baseline floor
B = bounded human adjustment with adjustment_alpha
D = shadow re-anchor
F = LOW_CONFIDENCE state
```

Authority:

```text
DESIGN ONLY
FORWARD TEST ONLY
NO MODEL PROMOTION
```

---

## 5. Re-anchoring state machine

States:

```text
NORMAL_RANGE
TRANSITION_WATCH
REANCHOR_SHADOW_ACTIVE
OFFICIAL_REANCHOR_ALLOWED
RANGE_LOW_CONFIDENCE
```

Critical governance point:

```text
OFFICIAL_REANCHOR_ALLOWED is unreachable in v0.1 by design.
```

It can only be opened later by governance if the shadow ledger has at least 8 scored instances with better median Winkler than never-move, and only at planned weekly publication time.

---

## 6. Scoring redesign

The old blended overall score is retired.

Future CN posts must show separate score lines:

```text
1. Phase / Structure score
2. Range score
3. Timing score
4. Rotation score
5. Warning / Risk score
```

Range score must include:

```text
Winkler alpha=0.10 primary
Winkler alpha=0.20 recommended
Jaccard
daily containment
breach days
direction bias
width ratio
CN vs DUMB_1.5
CN vs DUMB_2.0
CN vs PREVWK
verified actual source
```

Public-friendly rule:

```text
A good phase week can never hide a lost range week.
```

---

## 7. Forward ledger schema

Minimum fields:

```text
forecast_id
publication_ts
week_start
week_end
asset
official_range_low
official_range_high
official_range_mid
official_range_width
baseline_DUMB15_low
baseline_DUMB15_high
baseline_DUMB20_low
baseline_DUMB20_high
baseline_PREVWK_low
baseline_PREVWK_high
phase_label
structure_label
triad_state
transition_watch_flag
reanchor_shadow_flag
shadow_low
shadow_high
shadow_ts
official_reanchor_flag
confidence
actual_low
actual_high
actual_source
actual_verification_status
winkler_a10
winkler_a20
jaccard
containment
breach_days
direction_bias
width_ratio
phase_score
range_score
adjustment_alpha
notes
```

Freeze rule:

```text
Baselines must be calculated and logged at publication time, not at scoring time.
```

---

## 8. Kill criteria

```text
K1: CN adjusted median Winkler > DUMB_1.5 over next 8 scored weeks -> suspend adjustment layer.
K2: CN loses to both DUMB_1.5 and DUMB_2.0 over 8 weeks -> revert + governance review.
K3: 2 total-miss weeks in 8-week window -> immediate revert to baseline discipline.
K4: Any self-actual use -> week's score annulled + integrity row.
K5: Blended public score returns -> layout non-compliance flag.
K6: width_ratio >2.5 without SCENARIO status -> overwide-gaming flag.
K7: LOW_CONFIDENCE >2/8 weeks -> confidence-gaming check.
K8: shadow re-anchor killed if >=8 instances score worse than never-move.
```

---

## 9. Public template

Future Cycle Navigator posts should use seven blocks:

```text
1. PHASE / STRUCTURE
2. RANGE FORECAST
3. RANGE SCORE VS BASELINES
4. PULLBACK WEATHER
5. ROTATION STATE
6. SHADOW OBSERVATIONS
7. WHAT WOULD INVALIDATE THIS FORECAST
```

Purpose:

```text
Make the framework more honest without destroying public readability.
```

---

## 10. Counter-evidence / caution

RMR explicitly warns against overreacting:

```text
n = 14 only
one quarter / one regime sequence
ETH n = 4
CN was best in 3 flush weeks
risk of fighting the last war
internal Master Monday rows not fully scored
DUMB_2.0 can win by width in calm regimes
```

Canonical implication:

```text
Review is justified, but immediate retuning is not.
```

---

## 11. Creative extension / new design ideas

### CE-1 Adjustment Alpha

```text
Status: STRUCTURAL, NEEDS_FORWARD_ROWS
```

Use adjustment_alpha as the weekly public falsification metric for human range judgment.

---

### CE-2 Uncertainty tags

```text
Status: STRUCTURAL
```

Tags:

```text
NORMAL
LOW
SCENARIO
```

Scenario must never be relabeled as official range.

---

### CE-3 Anchoring Alert

```text
Status: ROW_SUPPORTED DESIGN, NEEDS_FORWARD_ROWS
```

Trigger idea:

```text
4-week same-sign direction bias -> ANCHORING_ALERT row
```

---

### CE-4 Placebo protocol

```text
Status: NEEDS_FORWARD_ROWS
```

Each quarterly audit should score ranges against +/-1-week shifted actuals.

Purpose:

```text
Detect whether ranges are week-specific or merely level anchors.
```

---

### CE-5 Public wording reform

```text
Status: STRUCTURAL
```

Replace vague precision percent with:

```text
range held X/7 days
beat naive band: yes/no
```

---

### CE-6 M1/M2 urgency context tag

```text
Status: ROW_SUPPORTED via M2, STRUCTURAL
```

TRIAD state should appear beside the range as context, not as numeric retuning.

---

### CE-7 Flush-strength narrative

```text
Status: REJECT_IF_NOT_REPLICATED
```

Do not use flush-week strength in public copy until replicated on at least 8 flush weeks.

---

## 12. Next mission

```text
Forward Range Ledger Protocol
```

Purpose:

```text
Implement RMR's schema, public template, scoring block, baseline freeze rule, shadow re-anchor log and kill-monitor from the first resumed CN post.
```

Parallel queue remains:

```text
M3 Challenger when decision ledger + loss function arrive.
FULL M1 when BTC.D arrives.
M2 forward-logging continues.
```

---

## 13. Related data file

Rows archived here:

```text
04_MARKET_LEARNING/range_skill/data/2026-07-08__range-model-review-v0-1-design-rows.csv
```

---

## 14. Canonical one-line summary

```text
RMR v0.1 does not promote a new range model; it makes range skill measurable and falsifiable through baseline discipline, verified actuals, separated scoring, bounded adjustment-alpha, shadow-only re-anchoring and hard 8-week kill criteria.
```

---

## 15. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_RULE_RATIFICATION
NO_MODEL_PROMOTION
NO_RANGE_RETUNING_ON_M5_ROWS
DESIGN_ONLY
FORWARD_TEST_REQUIRED
```
