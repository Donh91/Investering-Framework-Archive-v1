# Cycle Navigator Mobile-First Image Template

**Dato:** 2026-07-06  
**Updated:** 2026-07-10  
**Status:** CANONICAL / SCORING_GOVERNANCE_CORRECTED  
**Område:** Cycle Navigator / visual template / public accountability  
**Primary folder:** `05_CYCLE_NAVIGATOR/templates/`  
**Related folders:** `05_CYCLE_NAVIGATOR/visuals/`, `05_CYCLE_NAVIGATOR/weekly_posts/`, `03_WEEKLY_OPERATIONS/master_monday/`, `06_RESEARCH_LAB/forward_tests/`  
**Supersedes:** earlier wide dashboard preference and the prior requirement to display unreconciled historical track-record bars  
**Depends on:** Master Monday version chain; verified scoring governance; FRLP v0.1; GPT-5.6 Fresh Eyes Audit Implementation

---

## 1. Purpose

The visual standard remains mobile-first, simple and iPhone-readable.

```text
Mobile-first.
Three sections.
Clear uncertainty.
Frozen forecasts.
No historical precision overclaim.
```

---

## 2. Binding scoring correction

```text
PUBLIC_TRACK_RECORD_STATUS: LOCKED_PENDING_INDEPENDENT_RECONCILIATION
HISTORICAL_PRECISION_BARS: SUSPENDED
BLENDED_PRECISION_SCORE: FORBIDDEN
RANGE_PHASE_ROTATION_SCORES: SEPARATE
FIRST_TRUE_FRLP_FORWARD_ROW: CN_15
```

The previous mandatory `Track Record Summary` panel is suspended while the public track record is locked.

The third section must now be:

```text
FORWARD TEST STATUS
```

Historical bars may return only after verified actuals, frozen baselines, complete source lineage, separate score categories and no-retroactive-adjustment checks are complete.

---

## 3. Required three-section layout

```text
1. Week Outlook
2. Altseason / Rotation Path
3. Forward Test Status
```

Remove:

- separate methodology panels;
- unreconciled historical score bars;
- average precision claims;
- dense dashboard columns;
- explanatory text that belongs in the written post.

Recommended format:

```text
Vertical 4:5 or 2:3
Single page
Readable on iPhone without zoom
Institutional and clean
```

---

## 4. Section 1 — Week Outlook

Required:

```text
BTC Official Forecast Range
Frozen baseline ranges: DUMB_1.5 and DUMB_2.0, in post or compact note
Bias
Key Levels
Signal
Risk
Invalidation
```

Rules:

- one official range only;
- range frozen before the forecast window;
- do not describe the range as proven edge;
- actual scoring waits for independently verified high/low;
- phase and rotation are not blended into range accuracy.

A simple path sketch is allowed, but must not imply precision beyond the frozen forecast.

---

## 5. Section 2 — Altseason / Rotation Path

Use only the established public phase line:

```text
Pre-Rotation
→ BTC Dominance Expansion
→ Early Rotation Watch
→ Selective Alt Rotation
→ Broad Altseason
→ Late Cycle / Exit
```

Do not invent diagnostic states as public phases.

Required fields:

```text
Current Phase
Next Conditional Phase
Evidence Needed
Failure Condition
Asset-Tier Permission
```

### Countdown rule

Specific calendar countdowns are allowed only when they are explicitly pre-registered forecasts with a frozen source and later outcome row.

Otherwise use:

```text
CONDITIONAL WINDOW
NOT YET EVIDENCE-SUPPORTED
TIMING UNCONFIRMED
```

Do not publish `altseason in 8–16 weeks` as a standing estimate unless it is frozen and scored as a timing forecast.

Selective Alt Rotation should remain the key phase to monitor before broad altseason.

### Unlock row

Use no more than three measurable unlocks.

Prefer categories such as:

```text
BTC structure survives
ETH/BTC repair persists
Breadth / BTC.D / deployment confirm transmission
```

Exact gates must come from the current ratified Master Monday/runtime registry, not from stale template values.

---

## 6. Section 3 — Forward Test Status

Required while public track record is locked:

```text
Forward Test Status
Range protocol: FRLP v0.1
Forward series start: CN #15
Official range frozen: YES / NO
Baselines frozen: YES / NO
Verified actual: PENDING / VERIFIED
Current outcome: UNSCORED / RANGE / PHASE / ROTATION
Historical scores: UNDER INDEPENDENT RECONCILIATION
No retroactive changes
```

Optional, only after a row matures:

```text
Official Range Score
DUMB_1.5 Score
DUMB_2.0 Score
Baseline Delta
```

Do not display a cumulative public average until the scoring governance explicitly unlocks it.

---

## 7. Visual style

Use:

```text
White background
Dark navy headers
Bright blue primary data
Orange current phase
Red only for risk/invalidation
Large readable numbers
Consistent icons
```

Avoid:

```text
Tiny footnotes
Dense methodology
Desktop-wide layouts
Prestige metrics without verified lineage
```

---

## 8. Five-second content test

The image should answer:

```text
1. What is the frozen weekly range and invalidation?
2. What public phase are we in, and what evidence moves it?
3. What is the current forward-test and scoring status?
```

---

## 9. Future image-generation prompt block

```text
Create a mobile-first vertical Cycle Navigator weekly framework report.
Use three sections only:
1. Week Outlook
2. Altseason / Rotation Path
3. Forward Test Status

Section 1: show one frozen BTC forecast range, bias, key levels, signal, risk and invalidation. Do not call the range proven edge.

Section 2: use only the established phase line: Pre-Rotation → BTC Dominance Expansion → Early Rotation Watch → Selective Alt Rotation → Broad Altseason → Late Cycle / Exit. Show Current Phase, Next Conditional Phase, max three measurable unlocks and a failure condition. Use a calendar countdown only if the timing claim is explicitly pre-registered.

Section 3: show FRLP v0.1 forward-test status from CN #15 onward. State whether the official range, baselines and verified actuals are frozen/available. Historical scores remain under independent reconciliation. Do not show historical precision bars or a blended score.

Make the design clean, institutional, navy/white/blue with orange phase emphasis, and readable on iPhone/X without zoom.
```

---

## 10. Public wording guardrails

Forbidden until scoring unlock:

```text
88% range precision
track record proves edge
price forecast accuracy
verified historical average
```

Allowed:

```text
forward test
frozen forecast
verified actual pending
range result
phase result
rotation result
baseline delta
historical reconciliation in progress
```

---

## 11. Canonical summary

Future Cycle Navigator visuals remain three-section and mobile-first, but the third section is `Forward Test Status`, not an unreconciled historical track record. Calendar countdowns are conditional and must be pre-registered to be scored. Range, phase and rotation accountability remain separate. Scoring governance overrides any older visual instruction that requires historical precision bars.