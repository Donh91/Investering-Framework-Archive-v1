# M5 Range Skill Audit — Ledger Reconstruction + Degraded Scoring

**Date:** 2026-07-08  
**Run ID:** M5_DEGRADED_20260708  
**Status:** CANONICAL NEGATIVE CALIBRATION EVIDENCE  
**Scope:** Cycle Navigator range skill, Forecast Ledger reconstruction, verified actuals, baseline comparison, public precision integrity, range-model review trigger  
**Mode:** LEDGER_RECONSTRUCTION + DEGRADED_M5_EXECUTION  
**Source:** FABLE M5 Range Skill Audit report + RANGE_SKILL_ROW export  
**Boundary:** No market call. No portfolio action. No rule ratification. No range-model promotion.

---

## 1. Executive verdict

```text
READY_FOR_DEGRADED_M5_EXECUTION -> EXECUTED
Confidence: 74/100
```

Primary null hypothesis:

```text
Cycle Navigator does not beat DUMB_1.5xATR on Winkler interval score.
```

Result:

```text
NULL NOT REJECTED
CN loses to DUMB_1.5xATR
```

Head-to-head on Winkler alpha=0.10:

```text
CN beats DUMB_1.5: 5/14 weeks
CN median Winkler: 65.6
DUMB_1.5 median Winkler: 28.6
Median gap: approx. 2.3x against CN
```

CN also lost to DUMB_2.0:

```text
CN beats DUMB_2.0: 5/14 weeks
DUMB_2.0 median Winkler: 19.9
```

CN beat only previous-week baseline:

```text
CN beats PREVWK: 8/14 weeks
```

Canonical governance interpretation:

```text
Range layer is not currently validated as skill evidence.
Range-model review is now row-supported.
```

---

## 2. Source and scoring status

Forecast ledger reconstruction found:

```text
14 SOURCE_BACKED scored rows
10 BTC ranges
4 ETH ranges
1 DATA_MISSING candidate: CN09
1 MEMORY_CONTEXT_ONLY candidate: MM-W26, not scored
Intraday blocks catalogued, not scored
```

Scoring gate:

```text
PASS for DEGRADED_M5
FULL_M5 not permitted because n < 26
```

Actuals:

```text
14/14 verified actuals
FMP EOD full OHLC basis
No self-reported actuals used for scoring
No close/intraday mixing
```

Baselines:

```text
DUMB_1.5xATR: ready and scored
DUMB_2.0xATR: ready and scored
PREVWK: ready and scored
EWMA: not scored because not pre-registered
```

---

## 3. Main result table

```text
Model       Mean Winkler / Median Winkler | Jaccard | Containment | Breach days | Width ratio
CN          103.9 / 65.6                  | 0.383   | 45%         | 3.8         | 1.33
DUMB_1.5     90.2 / 28.6                  | 0.461   | 55%         | 3.1         | 1.27
DUMB_2.0     77.2 / 19.9                  | 0.427   | 78%         | 1.6         | 1.69
PREVWK      117.5 / 76.0                  | 0.337   | 41%         | 4.1         | 1.40
```

Primary conclusion:

```text
CN does not outperform hard naive ATR baselines on range skill.
```

---

## 4. Failure mode: transition anchoring

The key finding is not that CN ranges were too wide or too narrow overall.

```text
Failure mode = transition anchoring
not width gaming
```

Evidence:

```text
CN width ratio: 1.33
DUMB_1.5 width ratio: 1.27
DUMB_2.0 width ratio: 1.69
```

CN was not simply overwide.

The problem was placement:

```text
April rally: CN was anchored too low.
May-June drawdown: CN was anchored too high.
```

Important rows:

```text
CN02: 0% containment
CN03: Jaccard 0.000
CN03 forecast: 66K-73K
CN03 realized: 73.3K-78.4K
```

May-June down-leg bias:

```text
CN midpoint bias roughly +3% to +12%
```

Canonical learning:

```text
The range model reacts late around regime transitions.
```

---

## 5. Connection to M1 / M2 learning

M5 directly complements M1 and M2.

M1/M2 showed:

```text
ETF flow + ETH/BTC can provide early transition urgency.
Price/vol provides later confirmation.
```

M5 shows:

```text
Range layer misses or lags the same transitions.
```

Potential future shadow hypothesis:

```text
Use flow/ratio urgency as range re-anchoring trigger.
```

Boundary:

```text
SHADOW_ONLY
NEEDS_FORWARD_ROWS
No retuning on the 14-week sample
```

---

## 6. CN relative strength: flush weeks

CN had one relative strength:

```text
Flush-week performance was best of all four models.
```

Flush mean Winkler:

```text
CN: 272.9
DUMB_1.5: 300.6
DUMB_2.0: 274.2
PREVWK: 334.8
```

Status:

```text
NEEDS_MORE_ROWS
n=3
No proof
```

Canonical interpretation:

```text
CN may have better flush intuition, but this is not yet validated.
```

---

## 7. Verified actuals and public precision integrity

M5 found source conflicts between self-reported actuals and independently verified OHLC actuals.

Example:

```text
W2 self-reported actual: 66K-71K
W2 verified actual: 67.7K-74.9K
```

Public / internal scoring implication:

```text
Self-reported actuals must never be used for precision scoring.
Verified actuals only.
```

This replicates the earlier concern that self-scores can be flatteringly biased.

Canonical rule candidate:

```text
VERIFIED_ACTUALS_ONLY for all public precision scoring
```

Status:

```text
KEEP as ledger-integrity governance input
```

---

## 8. Range vs structure separation

M5 does not invalidate the broader Cycle Navigator framework.

It separates layers:

```text
Phase / structure calls: still supported by M1/M4 evidence
Pullback weather: supported as architecture evidence by M1/M2
Rotation restraint: supported by M4/M2
Range forecasting: weakest layer; needs review
```

Public layout implication:

```text
Separate Phase/Structure score from Range score.
Do not let qualitative edge be carried by weak numerical range layer.
```

Status:

```text
ROW_SUPPORTED + STRUCTURAL
```

---

## 9. Improvement candidates

### IC-M5-1 Range layer as skill evidence

```text
Status: REDUCE_WEIGHT
```

Reason:

```text
CN failed to beat DUMB_1.5 on Winkler.
Median gap approx. 2.3x against CN.
```

---

### IC-M5-2 Winkler + breach columns

```text
Status: SHADOW_ONLY / governance-method candidate
```

Recommendation:

```text
Run Winkler alpha=0.10 and breach-day metrics in parallel with existing public score.
```

---

### IC-M5-3 Flush-week strength

```text
Status: NEEDS_MORE_ROWS
```

---

### IC-M5-4 Verified actuals only

```text
Status: KEEP
```

Reason:

```text
Self-reported actuals conflicted with verified actuals in a flattering direction.
```

---

### IC-M5-5 Re-anchoring cadence

```text
Status: NEEDS_MORE_ROWS / STRUCTURAL
```

Observation:
CN04, after re-anchoring post-breakout, was one of CN's best relative rows.

---

### IC-M5-6 Intraday blocks

```text
Status: NEEDS_MORE_ROWS
```

Intraday blocks should only be scored in a separately pre-registered horizon layer.

---

## 10. Creative extension learnings

### CE-M5-1: Placement error, not width error

```text
ROW_SUPPORTED
```

CN range misses are directionally systematic:

```text
Too low in upside transition
Too high in downside transition
```

Shadow hypothesis:

```text
Flow/ratio urgency can act as range re-anchoring trigger.
```

---

### CE-M5-2: Dual-alpha reporting

```text
STRUCTURAL_HYPOTHESIS
```

Proposal:

```text
Report Winkler alpha=0.10 and alpha=0.20 plus width ratio side-by-side.
```

Purpose:
Avoid hidden width tolerance.

---

### CE-M5-3: Forecast skill vs communication skill

```text
ROW_SUPPORTED + STRUCTURAL
```

Learning:

```text
Qualitative structure calls may be strong while numerical ranges are weak.
```

Public scoring should separate:

```text
Phase/Structure score
Range score
```

---

### CE-M5-4: +/-1 week placebo shift

```text
ANTI_OVERFIT_CHECK
NEEDS_FORWARD_ROWS
```

Purpose:
Test whether ranges are week-specific or merely broad level anchors.

---

### CE-M5-5: Forward ledger from restart

```text
STRUCTURAL
```

Recommendation:
When Cycle Navigator publication resumes, pre-register Winkler / breach columns from day one.

---

### CE-M5-6: No retuning on 14 weeks

```text
OVERFIT_RISK_HIGH
REJECT
```

Any re-tuning of range width against these 14 rows is forbidden.

---

## 11. Range model review trigger

M5's own condition for range-model review is now met.

Evidence:

```text
CN failed DUMB_1.5 comparison.
CN failed DUMB_2.0 comparison.
Error mode is clear and row-supported.
Verified actual conflicts were found.
Range and structure skill diverge.
```

Governance status:

```text
RANGE_MODEL_REVIEW_TRIGGERED
```

Boundary:

```text
Review design only first.
No immediate retuning.
No overfit correction from these 14 rows.
```

---

## 12. Next mission recommendation

Next best mission:

```text
RANGE_MODEL_REVIEW_v0_1 — DESIGN ONLY
```

Not M3 yet:

```text
M3 requires decision ledger + loss function.
```

Not FULL M1 yet:

```text
FULL M1 requires BTC.D.
```

Range Model Review should design a safer forward range process with:

```text
ATR baseline first
Winkler primary
verified actuals only
range/structure score separation
transition re-anchoring as shadow-only
anti-overfit constraints
```

---

## 13. Related data file

Rows archived here:

```text
04_MARKET_LEARNING/range_skill/data/2026-07-08__m5-range-skill-rows-degraded-execution.csv
```

---

## 14. Canonical one-line summary

```text
M5 DEGRADED shows that Cycle Navigator range forecasts do not beat DUMB_1.5xATR on primary Winkler scoring, with the failure driven by transition anchoring rather than overwide ranges; verified actuals must be mandatory, range skill must be separated from phase/structure skill, and a range-model review is now row-supported.
```

---

## 15. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_RULE_RATIFICATION
NO_RANGE_MODEL_PROMOTION
NO_RETUNING_ON_14_ROWS
NO_PUBLIC_PRECISION_FROM_SELF_ACTUALS
DEGRADED_M5_ONLY
```
