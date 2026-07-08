# CN R&D Audit — Regime / Phase / Range Calibration Update

**Date:** 2026-07-08  
**Status:** CANONICAL CALIBRATION LEARNING  
**Scope:** Cycle Navigator, Research Lab, ETH/BTC gate discipline, range-score benchmark discipline, regime/phase audit hygiene  
**Source inputs:** OPUS 4.8 regime reverse-engineering package + FABLE/CN R&D Audit 2026-07-08 + row CSVs  
**Boundary:** No market call. No portfolio action. No public track-record update. No automatic rule ratification.

---

## 1. Executive conclusion

The July 8 R&D packages should be archived as calibration learning, not as a new engine.

The combined value is:

- OPUS 4.8 strengthens governance/audit hygiene: walk-forward labeling, hindsight-tax awareness, and honest measurement of defensive value.
- FABLE/CN R&D strengthens operational Cycle Navigator calibration: ETH/BTC gate base rates, rotation fakeout risk, persistence minimums, and range benchmark discipline.

The correct archive classification is:

```text
CANONICAL CALIBRATION LEARNING
+
RESEARCH LAB / CN R&D AUDIT
+
NO EXECUTION AUTHORITY
```

---

## 2. OPUS 4.8 calibration learning

### 2.1 Walk-forward labels are mandatory

All public regime and phase labels used in Cycle Navigator, Master Monday, Forecast Ledger or public scoring must be labeled as:

```text
WALK_FORWARD
```

unless explicitly marked:

```text
RETROSPECTIVE_DIAGNOSTIC
```

Reason:
Retrospective labeling can materially understate real-time pain and real-time uncertainty.

In the OPUS reverse-engineering package, walk-forward downtrend exposure since the 2025 ATH was materially higher than retrospective downtrend exposure. The key learning is not the exact parameter set, but the direction of the bias:

```text
Retrospective regime labels can make a live regime engine look cleaner than it was in real time.
```

Framework implication:
Never publish or score a phase/regime label as if it had been known live unless it is explicitly walk-forward.

---

### 2.2 Defensive value must be measured as insurance, not raw edge

Regime-following / trend-filtering may reduce drawdowns but does not automatically create return edge.

Correct measurement frame:

```text
drawdown reduction per return forgone
```

Not:

```text
beats buy-and-hold
```

Canonical learning:

```text
Framework defensive value should be measured as capital protection efficiency, not as unconditional alpha.
```

Use this for:

- FNP / opportunity-cost analysis
- Research Lab audits
- Cycle Navigator methodology notes
- defensive rule reviews
- future comparisons against simple baselines

---

### 2.3 Raw ETH/BTC trend-state is not an alt-outperformance signal

The OPUS package found that naive ETH/BTC phase labels did not reliably predict altcoin outperformance. The value was instead in fakeout reduction through persistence-filtered phase state.

Canonical distinction:

```text
ETH/BTC persistence = transmission quality / fakeout filter
ETH/BTC threshold cross = not altseason confirmation
ETH/BTC phase entry = not automatic alt outperformance
```

This supports the existing framework doctrine:

- persistence over spikes
- rotation survival over first signal
- multi-gate confirmation over single-threshold gates

---

## 3. FABLE / CN R&D Audit calibration learning

### 3.1 Larsson / BTCAnalytica claim rejected as public signal

The public claim that Larsson flipped blue around August 2025 near $112K with no whipsaws was not reproducible across the tested configuration family.

However, the trend-filter family showed defensive drawdown value during the tested bear-leg.

Canonical treatment:

```text
Larsson-style filters may be studied as drawdown-protection context.
They are not imported as signals.
They have zero execution authority.
Any future use is shadow-only and must be logged as corroborator, not confirmation.
```

Allowed future use:

```text
Larsson-SLOW proxy = de-escalation corroborator only
Same class as TechDev macro context
Useful if aligned
Ignored if alone
Never execution authority
```

---

### 3.2 ETH/BTC 0.0275 has high standalone false-positive risk

FABLE quantified the historical base rate for ETH/BTC 0.0275 upward close-crosses since January 2025:

```text
4/5 closed 0.0275 crosses died before 14 days
≈ 80% false-positive rate as standalone signal
```

Canonical interpretation:

```text
ETH/BTC > 0.0275 = repair attempt
not rotation confirmation
not deploy
not recovery
```

Operational consequence:
ETH/BTC 0.0275 may support PREPARE / WATCH language only when consistent with other inputs. It cannot promote rotation alone.

---

### 3.3 ETH/BTC 0.0300 can also fake

FABLE identified one case where ETH/BTC held above 0.0300 for approximately 27 days and still failed later.

Canonical learning:

```text
ETH/BTC duration alone is insufficient.
Even 14–30d ETH/BTC survival can be a slow-bleed fake rotation if breadth, BTC.D, deployment and flow congruence do not confirm.
```

This strengthens the multi-gate rule:

```text
ETH/BTC persistence
+
breadth survival
+
BTC.D deceleration / non-reclaim
+
stablecoin deployment
+
flow congruence
```

not ETH/BTC alone.

---

### 3.4 Slow-bleed fake rotation must be instrumented

New explicit row type:

```text
SLOW_BLEED_FAKE_ROTATION_ROW
```

Trigger condition for future observation:

```text
ETH/BTC survives ≥14 calendar days above a relevant gate
WITHOUT breadth / BTC.D / deployment confirmation
```

Purpose:
Close the instrumentation hole where ETH/BTC duration looks healthy but broader transmission does not survive.

Status:

```text
SHADOW FORWARD TEST ROW
NO EXECUTION WEIGHT
POST-GATE SEQUENCE OBSERVATION
```

---

### 3.5 2–3 day persistence is a minimum guardrail, not excessive caution

FABLE found structural confirmation lag of approximately:

```text
median: 5 days
p90: 13 days
```

Canonical learning:

```text
2–3d persistence = minimum guardrail
not excessive caution
```

Framework implication:
Do not weaken 2–3d persistence merely because it feels slow. It is already faster than median structural confirmation in the tested swing-regime method.

---

### 3.6 Quantile / envelope bands rejected as range model

FABLE’s 65-week range test found:

```text
Envelope mean Jaccard ≈ 0.298
Dumb 2.0×ATR mean Jaccard ≈ 0.496
Dumb 1.5×ATR mean Jaccard ≈ 0.530
```

Envelope lost to the dumb 2.0×ATR band in 55/65 weeks.

Canonical treatment:

```text
Quantile / envelope bands = visual context only
not forecast model
not Cycle Navigator range model
not public range-score input
```

---

### 3.7 CN benchmark must add dumb 1.5×ATR

Prior Cycle Navigator scoring used dumb 2.0×ATR as a naïve benchmark. FABLE shows 1.5×ATR is a harder and often better baseline, especially in calmer weeks.

Canonical update:

```text
Add DUMB_1.5_ATR as secondary CN benchmark column.
Do not remove DUMB_2.0_ATR.
Use both to separate flush-regime tolerance from calm-regime precision.
```

Purpose:
Make CN range-skill evaluation more honest and harder to game.

Status:

```text
METHODOLOGY UPGRADE
EFFECTIVE FOR FUTURE SCORECARDS
NO RETROACTIVE PUBLIC SCORE REWRITE UNLESS EXPLICITLY AUDITED
```

---

### 3.8 Spike / grind ETH/BTC gate-cross signature remains shadow-only

FABLE observed a small-n pattern:

- gate-crosses where ratio swing-regime was already UP died quickly
- grind-style / transition crosses looked less fragile

This is useful but underpowered.

Canonical treatment:

```text
SPIKE_GRIND_SIGNATURE = SHADOW_ONLY
no execution weight
no promotion
log future crosses only
```

Potential future row:

```text
ETHBTC_GATE_CROSS_SIGNATURE:
SPIKE / GRIND / UNKNOWN
```

---

## 4. Ratified now vs deferred

### Ratified now as calibration

```text
1. Walk-forward label requirement.
2. Defensive value measured as drawdown-reduction per return forgone.
3. ETH/BTC 0.0275 and 0.0300 are insufficient alone.
4. Slow-bleed fake rotation row type added for future observation.
5. 2–3d persistence is minimum guardrail.
6. Quantile/envelope rejected as range model.
7. DUMB_1.5_ATR added as secondary CN benchmark.
```

### Deferred / shadow-only

```text
1. Spike/grind ETH/BTC gate-cross signature.
2. Larsson-SLOW proxy.
3. Any promotion of ETH/BTC phase state into deploy logic.
4. Any new range model based on envelopes.
```

---

## 5. Integration map

### Cycle Navigator

Use for:

- scorecard benchmark calibration
- range-method honesty
- public wording around ETH/BTC and altseason
- future precision-score reviews

Do not use for:

- public track-record rewrite unless separately audited
- new forecast engine
- market call

### DATA PING

Use for:

- ETH/BTC gate interpretation
- rotation repair vs confirmation labels
- shadow rows on slow-bleed fake rotations

Do not use for:

- portfolio action
- rebuy unlock
- rotation confirmation alone

### Research Lab

Use for:

- future audit baselines
- rows-over-architecture discipline
- FNP and opportunity-cost measurement
- drawdown-insurance scoring

### Master Monday

Use for:

- methodology notes
- gate discipline
- CN handoff calibration

Do not let this override live DATA PING state.

---

## 6. Canonical one-line summary

```text
July 8 R&D confirms that the framework should become more honest and harder to fool, not more complex: use walk-forward labels, measure defense as insurance, treat ETH/BTC gates as repair attempts until multi-gate survival confirms, reject envelope bands as range models, and benchmark CN against both 2.0×ATR and 1.5×ATR dumb baselines.
```

---

## 7. Boundary

```text
NO_MARKET_CALL
NO_PORTFOLIO_ACTION
NO_REBUY_UNLOCK
NO_ROTATION_CONFIRMATION
NO_PUBLIC_TRACK_RECORD_UPDATE
NO_NEW_ENGINE
```
