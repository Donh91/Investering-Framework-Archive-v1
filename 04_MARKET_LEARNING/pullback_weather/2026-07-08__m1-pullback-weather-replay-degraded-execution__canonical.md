# M1 Pullback Weather Replay — Degraded Execution

**Date:** 2026-07-08  
**Run ID:** M1_DEGRADED_EXEC_20260708  
**Status:** CANONICAL CALIBRATION EVIDENCE  
**Scope:** Pullback Weather Replay, pullback early-warning design, urgency vs confirmation, ETF-flow / ETHBTC / price-vol sensor roles  
**Mode:** DEGRADED_M1_EXECUTION  
**Source:** FABLE M1 Pullback Weather Replay report + PULLBACK_WEATHER_ROW export  
**Boundary:** No market call. No portfolio action. No rule ratification. No trim/rebuy/deploy unlock.

---

## 1. Executive verdict

```text
DEGRADED_M1_PASS
Confidence: 70/100
```

The degraded 2-leg hypothesis was tested:

```text
ETF deterioration + ETH/BTC weakness + price/vol stress
vs.
price/vol structure alone
```

The full 3-leg hypothesis remains NOT_RUN because BTC.D is missing:

```text
ETF deterioration + BTC.D reclaim + weak ETH/BTC = NOT_RUN
```

Core result:

```text
Flows + ETH/BTC gave substantially earlier warning.
Price/vol gave cleaner confirmation.
No single family won all dimensions.
```

Canonical interpretation:

```text
Urgency and confirmation should remain separate layers.
```

---

## 2. Data and preflight status

### Data status

```text
BTC OHLC: FULL
ETH/BTC: FULL / DERIVED
BTC ETF flow: FULL / Farside frozen / 373 prints / anchor-verified
ATR14: FULL
BTC.D: DATA_MISSING
Funding/OI: DATA_MISSING
Liquidation clusters: DATA_MISSING
CFGI: DATA_MISSING
Breadth/deployment: DATA_MISSING
CHIEF/PTR ledger: DATA_MISSING
Decision ledger: DATA_MISSING
```

### Minimum data gate

```text
PARTIAL
```

Allowed:

```text
DEGRADED_M1_EXECUTION
A/C/D family replay
```

Not allowed:

```text
FULL_M1
core 3-leg hypothesis
BTC.D-based concentration tests
actual framework-vs-ledger scoring
```

### Reconciliation flag from datapack

Farside showed positive prints on 2026-07-02, 2026-07-06 and 2026-07-07, while prior canonical language referenced outflows resuming on 2026-07-06.

Status:

```text
RECONCILIATION_FLAG
No market interpretation.
DATA PING should resolve print revision / source-state mismatch.
```

---

## 3. Event universe

Event close rule used:

```text
R2 = 50% retrace OR new trailing 30d close high
```

Reason:
R1, using 50% retrace only, collapsed structurally in cascade-bear conditions into one long super-event. R2 segmented the bear legs in a way that matched PTR-like sequences better.

Wave mapping:

```text
Ripple: <5%
Wave: 5–12%
Heavy Wave tag: 10–15%
Storm: 12–25%
Tsunami: >25%
```

Event distribution:

```text
10 total price-defined pullback events
5 WAVE
1 STORM
4 TSUNAMI
1 OPEN / UNRESOLVED event: PW10
PW01 excluded from evaluation window as warmup/window artifact
```

PW10 was scored only on the warning side, not final outcome side.

---

## 4. Main result: lead vs precision trade-off

### Lead-time result

For scorably large events, A+C gave much earlier warnings than D-only:

```text
A+C median lead to C12: 23.5 days
D-only median lead to C12: 7.0 days
```

A+C was earlier than D-only on all four scorably large events:

```text
PW05: 25d vs 8d
PW07: 20d vs 6d
PW08: 22d vs 4d
PW10: 25d vs 10d
```

Important highlight:

```text
PW07 A+C warning fired on 2025-09-26,
14 days before the 2025-10-06 cycle top.
```

Canonical learning:

```text
ETF + ETH/BTC can function as weather-warning / urgency instruments.
```

---

### Precision and false-alarm result

False alarms:

```text
A family: 5
C family: 2
D family: 0
Total: 7
```

Most false alarms clustered in rally periods, especially April 2026.

D-only had the cleanest false-alarm profile:

```text
D-only FAR_wave: 0.00
```

Canonical learning:

```text
Price/vol structure is late but clean.
It should remain a confirmation / precision layer.
```

---

### Naive trim result

Naive trim execution was not validated.

```text
A+C trim edge: -6.8%
C-only trim edge: +18.5%
D-only trim edge: +7.5%
```

Interpretation:

```text
A-family / ETF flow deterioration is valuable as urgency information,
not as a standalone trim trigger.
```

Ratification boundary:

```text
Naive A-family trim execution = REJECT
```

---

## 5. Family scorecard summary

```text
A-only:
- Strong lead
- High false-alarm cost
- Net trim edge: -1.3%
- Insurance Ratio: 10.2

C-only:
- Best cost-adjusted single family in this degraded sample
- Net trim edge: +18.5%
- Insurance Ratio: 4.4
- Needs more rows

D-only:
- Cleanest precision layer
- 0 false alarms
- Shorter median lead: 7d
- Net trim edge: +7.5%
- Insurance Ratio: 13.0

A+C:
- Best early-warning lead: 23.5d median
- Full >=Wave recall in evaluation sample
- Net trim edge: -6.8% due to false alarms
- Insurance Ratio: 7.9

A+C+D:
- Same lead as A+C
- Did not solve A-family false-alarm cost
```

Primary architecture conclusion:

```text
The degraded M1 result supports the framework architecture more than any single sensor family.
```

---

## 6. Depth underestimation learning

At warning time, realized pullback class was usually deeper than the warning-stage current drawdown class.

Observed pattern:

```text
Depth underestimation: +1 to +3 classes
Average underestimation around +1.2 classes
```

Canonical learning:

```text
Early warnings can lean forward on urgency.
Depth classification must remain confirmation-gated.
```

Recommended language for DATA PING / Cycle Navigator:

```text
pullback risk rising
depth unknown
classification not confirmed
```

Avoid:

```text
This is only Wave
```

unless confirmation is present.

---

## 7. F1 / F2 repair quality learning

Degraded F1/F2 data was thin.

```text
F1 -> I relapse: 1/5
F2 -> G: 1/1
```

Status:

```text
NEEDS_MORE_ROWS
```

Learning:

```text
F2-degraded discriminated in the right direction in the single available case,
but sample size is insufficient and breadth is missing.
```

---

## 8. Improvement candidates

### IC-M1-1 Urgency / classification working split

```text
Status: KEEP as doctrine confirmation
No rule change
```

Learning:

```text
A+C = lead / urgency layer
D = confirmation / precision layer
```

---

### IC-M1-2 A3 regime blindness

```text
Status: SHADOW_ONLY
```

A3 caused multiple false alarms in rally periods.

Candidate fix:

```text
A3 only active when 20-print mean < 0
```

But this must not be introduced now because it would be threshold adjustment after outcomes.

Action:

```text
Pre-register for M2 / future forward rows only.
```

---

### IC-M1-3 C-family cost-adjusted strength

```text
Status: NEEDS_MORE_ROWS
```

C-only looked strong in this degraded sample, but the sample is bear-heavy and small.

Action:

```text
Evaluate in M2 Sensor Combination Tournament.
```

---

### IC-M1-4 Depth-underestimation constant

```text
Status: SHADOW_ONLY
```

Potential future logging field:

```text
DEPTH_UNDERESTIMATION_PRIOR
```

Potential communication note:

```text
Early pullback warnings often understate eventual depth by at least one class.
```

No rule status.

---

### IC-M1-5 F2-degraded definition

```text
Status: NEEDS_MORE_ROWS
```

No promotion due to sample size and missing breadth.

---

### IC-M1-6 Naive A-family trim execution

```text
Status: REJECT
```

Reason:

```text
Net trim edge was negative in the only available degraded sample.
```

Canonical boundary:

```text
ETF-flow deterioration cannot translate directly into trim action without confirmation layer.
```

---

## 9. DATA PING / Cycle Navigator activation

Future pullback-weather outputs should preserve this division:

```text
URGENCY_LAYER:
ETF flow deterioration
ETH/BTC weakness

CONFIRMATION_LAYER:
price/vol structure
range break
ATR expansion
swing confirmation

CLASSIFICATION_LAYER:
confirmed drawdown depth
post-flush repair quality
F1/F2 state
```

Suggested fields for future DATA PING / Shadow rows:

```text
PULLBACK_WEATHER_STATE
URGENCY_SCORE_DEGRADED
CONFIRMATION_SCORE_DEGRADED
ETF_FLOW_WARNING_ACTIVE
ETHBTC_WEAKNESS_ACTIVE
PRICE_VOL_CONFIRMATION_ACTIVE
EARLIEST_WARNING_DATE
LEAD_TO_C12_IF_KNOWN
DEPTH_CLASS_CONFIRMED
DEPTH_UNDERESTIMATION_RISK
A3_REGIME_BLINDNESS_FLAG
F1_F2_DEGRADED_STATE
DATA_QUALITY
```

Authority:

```text
SHADOW / CALIBRATION ONLY
NO_EXECUTION_WEIGHT
```

---

## 10. Full-M1 upgrade requirements

To upgrade M1 from DEGRADED to FULL, the framework still needs:

```text
1. Daily BTC.D series, ideally both total and ex-stables.
2. Breadth/deployment definitions if F1/F2 is to become full rather than degraded.
3. CHIEF/PTR export for actual framework labels.
4. Decision ledger for actual trim/rebuy comparison.
5. Funding/OI history for leverage-stress family.
6. Liquidation cluster or liquidation volume history.
7. CFGI / Fear & Greed history.
8. ETH ETF flow freeze if flow congruence is tested.
9. Cross-regime extension beyond one bear-heavy cycle sample.
```

---

## 11. Next mission recommendation

Given M1 and M4 have now produced labels, the next natural mission is:

```text
M2 SENSOR COMBINATION TOURNAMENT — DEGRADED
```

Rationale:

```text
M1 produced pullback warning labels.
M4 produced rotation survival labels.
M2 can now test which sensor combinations add value and which add noise.
```

Key M2 questions:

```text
Does A+C outperform C-only after false alarms?
Does adding A to C improve lead enough to justify cost?
Does D serve best as confirmation-only?
Can a smaller stack beat the full degraded stack?
Can BASE_DEPTH / LADDER fields add rotation value without overfit?
```

---

## 12. Related data file

Rows archived here:

```text
04_MARKET_LEARNING/pullback_weather/data/2026-07-08__m1-pullback-weather-rows-degraded-execution.csv
```

---

## 13. Canonical one-line summary

```text
M1 DEGRADED confirms that ETF + ETH/BTC can provide substantially earlier pullback weather warnings than price/vol alone, but those early signals are costly if used naively; the correct framework architecture is urgency first, confirmation second, classification gated, and no standalone flow-based trim execution.
```

---

## 14. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_RULE_RATIFICATION
NO_TRIM_RULE
NO_REBUY_UNLOCK
NO_DEPLOY_SIGNAL
DEGRADED_M1_ONLY
```
