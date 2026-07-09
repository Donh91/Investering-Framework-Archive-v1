# M2 Sensor Combination Tournament — Degraded Execution

**Date:** 2026-07-08  
**Run ID:** M2_DEGRADED_20260708  
**Status:** CANONICAL CALIBRATION EVIDENCE  
**Scope:** Sensor roles, pullback warning stack, rotation survival stack, urgency vs confirmation, sensor redundancy, forward-test candidates  
**Mode:** DEGRADED_M2_EXECUTION  
**Source:** FABLE M2 Sensor Combination Tournament report + SENSOR_COMBO_ROW export  
**Boundary:** No market call. No portfolio action. No rule ratification. No trim/rebuy/deploy unlock. No sensor promotion.

---

## 1. Executive verdict

```text
DEGRADED_M2_PASS
Confidence: 68/100
Architecture verdict: C — same architecture, cleaner sensor roles
```

M2 supports the framework as a role-based architecture rather than a single-signal engine.

Primary learning:

```text
A = urgency / early weather warning
C = lean warning
D = confirmation / veto
Classification remains gated
Execution never comes from one sensor
```

The tournament does not validate a simpler replacement framework yet. Challenger gains are in-sample and degraded.

---

## 2. Data inventory

Used:

```text
M1_DEGRADED_EXEC_20260708 pullback rows
M4_DEGRADED_20260708 rotation survival rows
M1 event universe: 10 events, 9 in-window, PW10 open/warning-side only
M4 rotation universe: 18 crosses, 16 resolved
Farside BTC ETF flow freeze: 373 prints, anchor-verified
BTC OHLC / ETH close / derived ETHBTC
```

Missing:

```text
BTC.D
breadth
deployment
funding/OI
liquidation clusters
CFGI
CHIEF/PTR ledger
decision ledger
```

Data quality:

```text
DEGRADED across all conclusions
```

---

## 3. Track 1 — Pullback Weather sensor roles

### A-family: ETF-flow deterioration

Result:

```text
A gives real lead but most noise.
A must remain urgency-only.
```

Key metrics:

```text
A-only median lead to C12: 23.5d
A-only trim edge: -1.3%
A-only Insurance Ratio: 10.2
A false-alarm burden: high, mostly A3
```

Verdict:

```text
A1: KEEP as urgency-only
A2: KEEP as urgency-only
A3: ONLY_WORKS_IN_REGIME_X / SHADOW forward-test
A-family as trim trigger: REJECT
```

---

### A3 regime-blindness

Strongest specific sensor defect:

```text
A3 caused 5 of 7 false alarms.
```

A without A3 improved sharply:

```text
A_wo_A3 trim edge: +23.1%
A_wo_A3 Insurance Ratio: 20.9
```

Boundary:

```text
A3 is not deleted yet.
A3 is not promoted.
A_wo_A3 is a forward-test / prune-candidate only.
```

Reason:
This is a degraded, bear-heavy, in-sample result.

---

### C-family: ETH/BTC weakness

Result:

```text
C is the best cost-adjusted single warning family in the degraded sample.
```

Key metrics:

```text
C-only trim edge: +18.5%
C-only recall >=Wave: 8/9
C-only recall >=Storm: 4/4
```

Verdict:

```text
C1: KEEP, needs more rows
C2: KEEP, lean warning
C-family: KEEP as lean warning, not execution alone
```

---

### D-family: price / volatility structure

Result:

```text
D is late but clean.
D is confirmation / veto, not early lead.
```

Key metrics:

```text
D-only false alarms: 0
D-only median lead to C12: 7.0d
D-only recall >=Wave: 4/9
D-only recall >=Storm: 4/4
```

Verdict:

```text
D2: KEEP confirmation
D3: KEEP confirmation-only, not trim-trigger
D-family: KEEP as confirmation / veto layer
```

---

### Full degraded stack redundancy

Important finding:

```text
A+C+D = A+C with Δ=0.0 on all union warning metrics.
```

Interpretation:

```text
D does not add lead in union.
D adds quality as confirmation/veto.
```

Canonical implication:

```text
Do not treat D as another additive warning sensor.
Use D to escalate, confirm or veto.
```

---

## 4. Track 1 combo verdicts

```text
A-only: SHADOW_ONLY / urgency-only
C-only: KEEP / lean warning
D-only: KEEP / confirmation
A+C: SHADOW_ONLY / urgency-only, not execution
A+D: NEEDS_MORE_ROWS
C+D: KEEP / challenger-core
A+C+D: REDUCE_WEIGHT as trim-trigger, KEEP as weather stack with role separation
A_wo_A3: SHADOW_ONLY prune-candidate / forward rows required
A3-only: ONLY_WORKS_IN_REGIME_X
C2-only: NEEDS_MORE_ROWS
D3-only: KEEP confirmation-only
BEST2 A2+D1: NEEDS_MORE_ROWS / selection bias
BEST3 A2+C1+D1: NEEDS_MORE_ROWS / selection bias
```

---

## 5. Track 2 — Rotation Survival sensor roles

### Raw ETH/BTC gates

Result:

```text
Raw ETH/BTC gates remain insufficient alone.
```

Verdict:

```text
ETH/BTC gates: KEEP as repair markers
ETH/BTC gates: REJECT as standalone confirmation
0.0300 level as quality reading: REJECT
```

---

### Hold days / persistence

Result:

```text
2–3d persistence filters fast fakes.
It does not confirm rotation.
```

Verdict:

```text
hold >=3: KEEP as minimum hygiene floor
hold >=14: NEEDS_MORE_ROWS and partly circular
hold >=30: no information as signal, label-circular
```

---

### BASE_DEPTH

Result:

```text
Perfect in-sample separation.
```

Verdict:

```text
BASE_DEPTH: SHADOW_ONLY
OVERFIT_RISK_HIGH
mandatory forward logging
```

---

### LADDER_COMPLETION

Result:

```text
Promising but n(real)=1.
```

Verdict:

```text
LADDER_COMPLETION: NEEDS_MORE_ROWS
mandatory forward logging
```

---

### BTC trend precondition

Result:

```text
Most independent promising rotation feature.
11/13 fakes caught, 3/3 real candidates retained.
```

Verdict:

```text
BTC_VS_EMA50_EXPLORATORY: SHADOW_ONLY
```

---

### Spike / grind

Result:

```text
Single spike/grind label remains rejected.
```

Verdict:

```text
SIG_A: REJECT as single label
SIG_B: SHADOW_ONLY as dual-log context
```

---

## 6. Creative extension learnings

### CE-1: ETF flows may lead the top, not only the break

Status:

```text
ROW_SUPPORTED
NEEDS_FORWARD_ROWS
```

Observation:
A-family first fire occurred before peak on all four scorably large pullback events.

Shadow label:

```text
A_URGENCY_PRE_PEAK_WINDOW
```

---

### CE-2: EMA50 false-alarm split

Status:

```text
ROW_SUPPORTED
STRUCTURAL_HYPOTHESIS
NEEDS_FORWARD_ROWS
```

Observation:

```text
7/22 warnings over EMA50 were false.
0/19 warnings under EMA50 were false.
```

Potential interpretation:

```text
Warnings over EMA50 = urgency-only
Warnings under EMA50 = escalation-eligible
```

Boundary:

```text
Shadow only.
No execution authority.
Possible mechanical proximity bias.
```

---

### CE-3: Warning breadth does not predict severity

Status:

```text
ROW_SUPPORTED negative finding
```

Learning:

```text
More rules firing does not reliably imply deeper pullback class.
```

---

### CE-4: ETF placebo-test protocol

Status:

```text
STRUCTURAL_HYPOTHESIS
ANTI_OVERFIT_METHOD
```

Proposal:
Shift ETF flow series by +/-30/60/90 days and re-run A lead.

Purpose:
Check whether A-family lead is real or event-density artifact.

---

### CE-5: Trim metric is closure-rule sensitive

Status:

```text
ROW_SUPPORTED / METHOD FINDING
```

Learning:
R2 / NEW30DHIGH recoveries can delay re-entry and distort trim-edge comparison.

Future variant:

```text
Compare R-based re-entry vs F2-degraded re-entry.
```

---

### CE-6: ETH/BTC percentile gates

Status:

```text
STRUCTURAL_HYPOTHESIS
LOG_ONLY
```

Proposal:
Log rolling 180d ETH/BTC percentile at each cross to address fixed-gate drift.

---

### CE-7: REAL_CANDIDATE tail / exit-side failure mode

Status:

```text
STRUCTURAL_HYPOTHESIS
```

Learning:
Entry-side duration features can look strong while being blind to exit-side collapse.

Future scoring needs explicit exit-side column.

---

## 7. TRIAD-DEGRADED v0.1 challenger template

Status:

```text
DESIGN ONLY
NO PROMOTION
```

Inputs:

```text
A_wo_A3 = A1 or A2 as urgency-only
C-family = C1 or C2 as warning
D-family = D1 or D2 or D3 as confirmation / veto
```

Decision states:

```text
GREEN = no active signal
YELLOW = A urgency only, communication only
ORANGE = C warning active
RED = C warning + D confirmation same day
```

Allowed language:

```text
urgency elevated
warning active
confirmed defensive
repair attempt active for n days
```

Forbidden language:

```text
depth class at warning
rotation confirmed
deploy
rebuy
portfolio action
one-sensor conclusion
```

Forward kill criteria:

```text
K1: one missed >=Storm forward event = kill
K2: forward FAR_wave > 0.30 = kill
K3: trim < D_only over next 8 events = kill
K4: minimum 8 weeks forward logging before any status discussion
```

---

## 8. Sensor verdict list

```text
A1: KEEP, urgency-only
A2: KEEP, urgency-only
A3: ONLY_WORKS_IN_REGIME_X, shadow forward-test
C1: KEEP, needs more rows
C2: KEEP, lean warning
D1: NEEDS_MORE_ROWS
D2: KEEP, confirmation
D3: KEEP, confirmation-only, not trim-trigger
F1/F2-degraded: NEEDS_MORE_ROWS
Raw ETH/BTC gates: KEEP as repair markers / REJECT as standalone confirmation
Hold days: KEEP as minimum hygiene only
BASE_DEPTH: SHADOW_ONLY
LADDER_COMPLETION: NEEDS_MORE_ROWS
BTC_VS_EMA50_EXPLORATORY: SHADOW_ONLY
SIG_A: REJECT
SIG_B: SHADOW_ONLY / dual-log only
```

---

## 9. Operational activation for DATA PING / Shadow rows

Future relevant DATA PING / shadow rows should log:

```text
URGENCY_LAYER_A1_ACTIVE
URGENCY_LAYER_A2_ACTIVE
A3_REGIME_BLINDNESS_FLAG
C_WARNING_ACTIVE
D_CONFIRMATION_ACTIVE
D_VETO_STATUS
TRIAD_STATE_GREEN_YELLOW_ORANGE_RED
EMA50_FALSE_ALARM_SPLIT_CONTEXT
A_URGENCY_PRE_PEAK_WINDOW
DEPTH_UNDERESTIMATION_RISK
WARNING_BREADTH_COUNT
WARNING_BREADTH_SEVERITY_VALID=false
ETHBTC_ROLLING_180D_PERCENTILE
BASE_DEPTH_PRIOR30
DAYS_BELOW_GATE_PRIOR60
LADDER_COMPLETION_DAYS
BTC_VS_EMA50_EXPLORATORY
SIG_A_LABEL
SIG_B_LABEL
EXIT_SIDE_SCORING_REQUIRED
DATA_QUALITY
```

Authority:

```text
SHADOW / CALIBRATION ONLY
NO_EXECUTION_WEIGHT
```

---

## 10. Next mission recommendation

Priority order:

```text
1. FULL M1 if BTC.D is delivered / approved.
2. M5 Range Skill Audit if raw Forecast Ledger is delivered.
3. M3 Challenger only after decision ledger + loss function.
4. If missing data remains, run M2 Forward Logging Protocol.
```

Practical implication:

```text
M2 has generated the forward-logging protocol candidates.
The only way to move perfect in-sample findings toward evidence is forward rows.
```

---

## 11. Related data file

Rows archived here:

```text
04_MARKET_LEARNING/sensor_tournament/data/2026-07-08__m2-sensor-combo-rows-degraded-execution.csv
```

---

## 12. Canonical one-line summary

```text
M2 DEGRADED confirms that the framework should not simplify into one winning sensor; instead, it should enforce cleaner sensor roles: A1/A2 as urgency-only, C as lean warning, D as confirmation/veto, A3 as regime-blind shadow candidate, and all perfect rotation features as forward-logged shadow-only due to high overfit risk.
```

---

## 13. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_RULE_RATIFICATION
NO_TRIM_RULE
NO_REBUY_UNLOCK
NO_DEPLOY_SIGNAL
NO_SENSOR_PROMOTION
DEGRADED_M2_ONLY
```
