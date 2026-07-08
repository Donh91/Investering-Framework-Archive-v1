# M4 Rotation Survival Replay — Degraded First Pass

**Date:** 2026-07-08  
**Run ID:** M4_DEGRADED_20260708  
**Status:** CANONICAL CALIBRATION EVIDENCE  
**Scope:** Rotation survival, ETH/BTC gate discipline, fake rotation detection, slow-bleed fake rotation, Cycle Navigator / DATA PING calibration  
**Mode:** DEGRADED FIRST PASS  
**Source:** FABLE M4 Rotation Survival Replay report + 18 ROTATION_SURVIVAL_ROW rows  
**Boundary:** No market call. No portfolio action. No rule ratification. No deploy/rebuy/rotation confirmation.

---

## 1. Executive verdict

```text
DEGRADED_M4_PASS
Confidence: 72/100
```

The mission executed cleanly and produced 18 walk-forward ETH/BTC gate-cross rows.

The degraded M4 pass supports the framework's restraint around ETH/BTC gates:

```text
ETH/BTC gates are repair / rotation-watch signals.
They are not standalone rotation confirmation.
They cannot confirm deploy.
They cannot unlock rebuy.
```

Main limitation:

```text
n(REAL_CANDIDATE episodes) = 1
single-cycle-leg confinement
breadth/deployment/BTC.D/flow congruence = DATA_MISSING
```

Therefore, the result is calibration evidence only.

---

## 2. Data inventory

```text
Source: FMP cryptocurrency-historical-price-eod
BTC: settled daily close
ETH: settled daily close
ETH/BTC: DERIVED = ETH close / BTC close
Date range: 2025-01-01 to 2026-07-07
Rows: 553 settled days
Missing days: 0
Settled cutoff: 2026-07-07
2026-07-08 in-progress data excluded
```

Unavailable in degraded mode:

```text
BTC.D = DATA_MISSING
breadth = DATA_MISSING
stablecoin deployment = DATA_MISSING
flow congruence = DATA_MISSING
ETF-flow context = DATA_MISSING in this run
```

---

## 3. Gate base rates

### ETH/BTC 0.0265

```text
Resolved crosses: 4
Fake: 3/4
Fake rate: 75%
Wilson95: [0.30, 0.95]
```

### ETH/BTC 0.0275

```text
Resolved crosses: 5
Fake: 4/5
Fake rate: 80%
Wilson95: [0.38, 0.96]
```

Canonical calibration:

```text
0.0275 = repair attempt
not rotation confirmation
not deploy
not recovery
```

### ETH/BTC 0.0300

```text
Resolved crosses: 7
Fake: 6/7
Fake rate: 86%
Wilson95: [0.49, 0.97]
```

Canonical calibration:

```text
0.0300 can still fake.
Higher gate does not equal safer signal without context.
```

### Pooled

```text
Resolved crosses: 16
Fake: 13/16
Pooled fake rate: 81%
Wilson95: [0.57, 0.93]
```

Important caveat:

```text
Gate crosses are not independent.
Some are clustered inside the same underlying ETH/BTC episode.
```

---

## 4. Framework doctrine comparison

### 4.1 0.0275 as repair, not rotation

Result:

```text
SUPPORTED
```

Reason:

```text
4/5 resolved 0.0275 crosses failed.
All 0.0275 failures fell back below the gate within 12 closes.
```

Framework impact:

```text
ETH/BTC > 0.0275 may support Early Rotation Watch / repair language only.
It must never be treated as rotation confirmation alone.
```

---

### 4.2 0.0300 can slow-bleed fake

Result:

```text
SUPPORTED
```

Key row:

```text
RS17
Gate: 0.0300
Cross date: 2026-03-27
Hold days: 27
Outcome: SLOW_BLEED
```

Framework impact:

```text
Even ETH/BTC > 0.0300 with >14d survival can fail.
ETH/BTC duration alone is insufficient.
```

---

### 4.3 Duration alone is insufficient

Result:

```text
SUPPORTED
```

Key points:

```text
P(hold >=14 | hold >=3) = 4/9
P(hold >=30 | hold >=14) = 3/4
```

Interpretation:

```text
2–3d persistence filters FAKE_FAST.
It does not confirm rotation.
```

Canonical language:

```text
2–3d persistence = minimum hygiene
not confirmation
```

---

### 4.4 Multi-gate survival remains required

Result:

```text
SUPPORTED INDIRECTLY
```

No single ETH/BTC-only feature separated REAL_CANDIDATE from FAKE with enough reliability for promotion.

Framework implication:

```text
Rotation confirmation still requires:
ETH/BTC persistence
+
BTC.D behavior
+
breadth survival
+
stablecoin deployment
+
flow congruence
```

---

### 4.5 Slow-bleed fake rotation row justified

Result:

```text
SUPPORTED
```

However, in degraded mode the full condition:

```text
ETH/BTC survives >=14d above gate WITHOUT breadth / BTC.D / deployment confirmation
```

cannot be fully attested because breadth, BTC.D and deployment are missing.

Status:

```text
SLOW_BLEED_FAKE_ROTATION_ROW remains shadow forward-test row.
No execution weight.
```

---

## 5. Counter-evidence and doctrine refinements

### 5.1 Spike / grind as one label is rejected

Result:

```text
SINGLE SPIKE/GRIND LABEL = REJECT
DUAL LOGGING = SHADOW_ONLY
```

Reason:

```text
Acceleration-based and regime-based definitions disagreed on important rows.
The real candidate rotation also showed acceleration.
```

Canonical refinement:

```text
Do not convert spike/grind into a single decision label.
Acceleration is not automatically bearish.
```

---

### 5.2 Higher gate is not automatically stronger

Result:

```text
SUPPORTED
```

Reason:
0.0300 had the highest fake rate in this sample because many crosses were gate-hugging pokes from an already elevated base.

Framework implication:

```text
Gate level without base context can mislead.
```

---

### 5.3 Exit-side blindness

New important learning:

```text
ETH/BTC persistence measures entry / repair quality.
It does not measure whether a profitable rotation window remains open.
```

The real 0.0275 hold lasted approximately 307 closes and extended far beyond the cycle top.

Canonical learning:

```text
Rotation module sees doors opening.
Pullback / stress apparatus must detect doors closing.
```

Framework impact:

```text
PROTECT / exit-side logic must not rely on ETH/BTC gate duration alone.
```

---

## 6. New shadow candidates from M4

These are not promoted. They are only logged for future rows.

### IC-M4-1 BASE_DEPTH_FILTER

```text
Status: SHADOW_ONLY
```

Observation:

```text
Real candidate crosses came from deep base:
>=16% below gate and 60/60 days below.

Fakes came from gate-hugging:
0.5% to 6.2% below gate.
```

Interpretation:

```text
Most promising new feature.
Also most suspicious because it has near-perfect in-sample separation.
```

Action:

```text
Pre-register and log future crosses.
No execution weight.
```

---

### IC-M4-2 LADDER_COMPLETION

```text
Status: NEEDS_MORE_ROWS
```

Observation:
The real candidate climbed the full ladder:

```text
0.0265 -> 0.0275 -> 0.0300
within approximately 3 days
from below 0.0265
```

Action:

```text
Log ladder completion days for future ETH/BTC cross sequences.
No execution weight.
```

---

### IC-M4-3 SIG-B / regime-at-cross

```text
Status: SHADOW_ONLY
```

Observation:
Regime-at-cross may matter, but the sample is too small and definition-dependent.

Action:

```text
Log SIG-A and SIG-B separately.
Do not collapse into one spike/grind label.
```

---

### IC-M4-4 BTC trend precondition

```text
Status: SHADOW_ONLY / EXPLORATORY
```

Observation:

```text
11/11 crosses with BTC < EMA50 failed.
All real candidate crosses had BTC > EMA50.
```

Caveat:

```text
Price-only.
In-sample.
Single-cycle-leg.
No promotion.
```

---

### IC-M4-5 EXIT_SIDE_GAP

```text
Status: NEEDS_MORE_ROWS / DESIGN FLAG
```

Learning:

```text
ETH/BTC gate duration can help classify openings.
It cannot classify closes.
```

Action:

```text
Add exit-side axis to FULL-M4 and future Pullback Weather Replay.
```

---

## 7. DATA PING / Cycle Navigator logging update

Future ETH/BTC gate crosses should log these fields when available:

```text
ETHBTC_GATE
ETHBTC_CROSS_DATE
ETHBTC_HOLD_DAYS
ETHBTC_GATE_STATUS
BASE_DEPTH_PRIOR30
DAYS_BELOW_GATE_PRIOR60
LADDER_COMPLETION_DAYS
BTC_VS_EMA50_EXPLORATORY
SIG_A_R5PCT
SIG_A_LABEL
SIG_B_RATIO_REGIME
SIG_B_LABEL
SLOW_BLEED_RISK
BTC_D_RECLAIM_DAYS
BREADTH_STATE
DEPLOYMENT_STATE
FLOW_CONGRUENCE
DATA_QUALITY
```

Authority:

```text
SHADOW_ONLY
NO_EXECUTION_WEIGHT
```

until sufficient future rows exist.

---

## 8. Full-M4 upgrade requirements

To upgrade from DEGRADED M4 to FULL M4, the framework needs:

```text
1. Daily BTC.D, preferably both total and ex-stables conventions.
2. Breadth series with pre-bound proxy definition.
3. Stablecoin deployment proxy with pre-bound definition.
4. Daily BTC and ETH ETF flows, Farside primary and sum-verified.
5. Flow congruence definition.
6. List of framework-declared historical rotation attempts.
7. Extended 2021-2024 history for more real rotation cases.
8. Pre-registration sign-off for outcome horizons and signature definitions.
9. Direct ETH/BTC pair if available, otherwise derived pair remains DEGRADED.
```

---

## 9. Ratified as calibration only

The following are accepted as calibration evidence:

```text
1. 0.0275 is repair attempt, not rotation confirmation.
2. 0.0300 can fake and can slow-bleed fake.
3. ETH/BTC duration alone is insufficient.
4. 2–3d persistence is minimum hygiene, not confirmation.
5. Slow-bleed fake rotation row is justified as shadow row.
6. Single spike/grind label is rejected.
7. BASE_DEPTH, LADDER_COMPLETION and BTC trend precondition are shadow-only future log fields.
8. ETH/BTC gate duration does not solve PROTECT / exit-side logic.
```

Not ratified:

```text
Any deploy rule.
Any rebuy rule.
Any rotation confirmation rule.
Any market call.
Any portfolio action.
Any promotion of BASE_DEPTH, LADDER or BTC trend precondition.
```

---

## 10. Related data file

Rows archived here:

```text
04_MARKET_LEARNING/rotation_survival/data/2026-07-08__m4-rotation-survival-rows-degraded-first-pass.csv
```

---

## 11. Canonical one-line summary

```text
M4 DEGRADED confirms that ETH/BTC gates are useful as repair and rotation-watch diagnostics but dangerous as standalone confirmation: 0.0275 had 80% resolved fake rate, 0.0300 had 86% resolved fake rate including one slow-bleed failure, duration alone was insufficient, and new base-depth / ladder / BTC-trend features must remain shadow-only until future rows validate them.
```

---

## 12. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_RULE_RATIFICATION
NO_REBUY_UNLOCK
NO_DEPLOY_SIGNAL
NO_ROTATION_CONFIRMATION
DEGRADED_M4_ONLY
```
