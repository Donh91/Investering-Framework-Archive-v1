# Cycle Navigator Mobile-First Image Template

**Dato:** 2026-07-06  
**Status:** CANONICAL  
**Område:** Cycle Navigator / visual template  
**Primary folder:** `05_CYCLE_NAVIGATOR/templates/`  
**Related folders:** `05_CYCLE_NAVIGATOR/visuals/`, `05_CYCLE_NAVIGATOR/weekly_posts/`, `03_WEEKLY_OPERATIONS/master_monday/`  
**Supersedes:** earlier wide dashboard-only visual preference for Cycle Navigator weekly images  
**Depends on:** CN #14 published visual, CN #15 mobile-first revision, Master Monday archive version-chain protocol

---

## 1. Purpose

This file preserves the approved visual direction for future Cycle Navigator weekly images after the CN #15 redesign.

The new standard is:

```text
Mobile-first.
Simpler.
Fewer panels.
Same framework logic.
More readable on iPhone/X feed.
```

The image should still feel like the same Cycle Navigator product as #14, but should no longer be a very wide desktop dashboard when the content is mainly three core sections.

---

## 2. Core design decision

The approved layout removes unnecessary right-side dashboard density.

Keep only:

```text
1. Week Outlook
2. Altseason Countdown
3. Track Record Summary
```

Remove from the visual image:

```text
- Separate Weekly Outlook panel
- Precision Methodology panel
- Extra explanatory boxes that repeat the post text
```

The written X post can contain the full explanation. The image should be a simple visual anchor.

---

## 3. Format

Recommended image format:

```text
Vertical / mobile-first
Approx. 4:5 or 2:3 ratio
Readable on iPhone without zooming
Single-page infographic
```

Avoid:

```text
Ultra-wide 16:9 dashboard
Too many tiny subpanels
Small methodology text
Duplicated explanations
```

---

## 4. Required layout

### Header

Include:

```text
Cycle Navigator logo
CYCLE NAVIGATOR #XX
Weekly Framework Report
Date range
```

Style:

```text
Institutional, clean, navy/blue, strong hierarchy.
```

---

### Section 1 — Week Outlook

Required content:

```text
BTC Forecast Range
BTC forecast path chart
Bias
Key Levels
Signal
Risk
```

Example for CN #15:

```text
BTC Forecast Range:
60.9K – 67.2K

Bias:
Repair Test

Key Levels:
61.9K Hold
63.3K Confirm

Signal:
ETH/BTC > 0.0275

Risk:
False Reclaim
```

Design note:

```text
The forecast path chart can sit next to the range box on mobile layout if readable.
The four bottom labels must be short and icon-led.
No long prose in this panel.
```

---

### Section 2 — Altseason Countdown

This is mandatory and should preserve the existing timeline logic.

Use the established phase line. Do not invent new actual phases.

Approved phase line:

```text
Pre-Rotation
→ BTC Dominance Expansion
→ Early Rotation Watch
→ Selective Alt Rotation
→ Broad Altseason
→ Late Cycle / Exit
```

For CN #15:

```text
Current Phase:
BTC Dominance Expansion

Marker:
WE ARE HERE
```

Important rule:

```text
Current phase must remain one of the existing timeline phases.
Diagnostic comments such as repair attempt, de-escalation or F2-watch must not be inserted as new phases.
```

Required countdown rows:

```text
Next Phase:
Early Rotation Watch — 1–4 weeks

Phase to Watch Closely:
Selective Alt Rotation — 4–10+ weeks

Broad Altseason:
8–16+ weeks
```

Core message:

```text
Selective Alt Rotation is the phase to watch closely before broad altseason.
```

Keep this sentence short and visible.

---

### Section 2 bottom row — unlocks

Use max three unlocks. Avoid long lists.

Approved CN #15 unlock row:

```text
BTC holds 61.9K
BTC closes above 63.3K
ETH/BTC trends toward 0.0300
```

Avoid adding every possible gate in the image. Full gate logic belongs in the written X post.

---

### Section 3 — Track Record Summary

Track record must be included.

Required content:

```text
Track Record Summary (#1–#latest completed)
Bar series
Current/latest completed week highlighted
Short no-retroactive-adjustment note
```

Example:

```text
Track Record Summary (#1–#14)
#14 highlighted
History is locked — no retroactive adjustments. Each week scored as published.
```

Average precision can be included only if recalculated correctly from the displayed bars.
If uncertain, omit average precision from the visual or mark it separately in the post.

---

## 5. Visual style

Use:

```text
White background
Dark navy headers
Bright blue for primary data
Orange for current phase / cycle emphasis
Red only for risk
Clean card borders
Large readable numbers
Consistent icon language
```

Do not use:

```text
Dense explanatory paragraphs
Multiple small text blocks competing for attention
Extra methodology panels
Extra right-hand dashboard column
Tiny footnotes beyond one short locked-history note
```

---

## 6. Content hierarchy

The image should answer three questions in under five seconds:

```text
1. What is this week's BTC range?
2. Where are we in the altseason timeline?
3. How has the framework performed historically?
```

Everything else belongs in the written X post.

---

## 7. Future image generation prompt block

Use this prompt pattern for future Cycle Navigator images:

```text
Create a mobile-first vertical Cycle Navigator weekly framework report image.
Build on the previous Cycle Navigator visual identity: navy headers, white cards, blue primary data, orange cycle-phase highlight, red risk accents, clean institutional research style, compass logo, @TheDonH91 branding.

Use only three main sections:
1. Week #XX Outlook
2. Altseason Countdown
3. Track Record Summary

Remove any separate Weekly Outlook panel and Precision Methodology panel.
Keep the layout compact and iPhone-readable.

Section 1 must include BTC Forecast Range, a simple BTC forecast path chart, and four short icon labels: Bias, Key Levels, Signal, Risk.
Section 2 must include the established phase timeline: Pre-Rotation → BTC Dominance Expansion → Early Rotation Watch → Selective Alt Rotation → Broad Altseason → Late Cycle / Exit. Do not invent new phases. Mark the current phase only from that timeline.
Section 2 must also include: Next Phase with estimated time, Phase to Watch Closely with estimated time, Broad Altseason estimate, and max three unlock gates.
Section 3 must include a compact track record bar chart and the note: History is locked — no retroactive adjustments.

Make it clean, readable, less wide, and optimized for iPhone/X feed viewing.
```

---

## 8. CN #15 reference values

The approved CN #15 mobile-first content reference:

```yaml
cycle_navigator_number: 15
date_range: July 6 – July 12, 2026
btc_forecast_range: 60.9K – 67.2K
current_phase: BTC Dominance Expansion
next_phase: Early Rotation Watch
next_phase_time: 1–4 weeks
phase_to_watch_closely: Selective Alt Rotation
phase_to_watch_time: 4–10+ weeks
broad_altseason_time: 8–16+ weeks
bias: Repair Test
key_levels: 61.9K Hold / 63.3K Confirm
signal: ETH/BTC > 0.0275
risk: False Reclaim
unlock_gates:
  - BTC holds 61.9K
  - BTC closes above 63.3K
  - ETH/BTC trends toward 0.0300
track_record: #1–#14
highlight_week: #14
```

---

## 9. Credibility guardrails

Do not break phase logic.

```text
Actual phases and current phases must come from the established phase timeline.
```

Allowed comments:

```text
repair attempt
support test
reclaim attempt
Early Rotation Watch strengthening
F2-watch improved
```

But these must appear as comments or state descriptions, not as new timeline phases.

Do not over-explain unlocks in the image.

```text
The image is a compass.
The written post is the explanation.
```

---

## 10. Canonical summary

```text
Future Cycle Navigator weekly images should use the CN #15 mobile-first standard: vertical, iPhone-readable, three main sections only, preserving Week Outlook, Altseason Countdown and Track Record Summary. The separate Weekly Outlook and Precision Methodology panels should be removed from the image. The Altseason Countdown must preserve the existing phase timeline and must not invent new phases. The image should clearly show the next phase, the phase to watch closely, and broad altseason timing, with Selective Alt Rotation highlighted as the personal focus phase before broad altseason.
```
