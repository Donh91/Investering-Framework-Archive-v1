# Cycle Navigator Publication Standard v2

**Status:** CANONICAL_PUBLICATION_STANDARD  
**Effective from:** Cycle Navigator #16  
**Approved:** 2026-07-14  
**Owner:** Main Framework / ChatGPT  
**Public language:** English  
**Purpose:** Preserve a concise, professional, repeatable weekly publication format with transparent scoring, market-compass interpretation and explicit cycle time horizons.

---

## 1. Permanent public structure

1. `VERIFIED SCORECARD — #<previous> (LAST WEEK)`
2. `WEEKLY MARKET UPDATE`
3. `CYCLE COMPASS`
4. `ALTCOIN CYCLE`
5. `MARKET OUTLOOK — WEEK #<current>`
6. `WEEKLY ACTION PLAN`
7. `KEY TAKEAWAY`

Keep the publication concise. Compress long cycle and outlook explanations by roughly 10–15% without removing decision logic, time horizons, ranges or scoring.

---

## 2. Verified Scorecard

Score the previous published Cycle Navigator only against its frozen public forecast.

Required blocks:

- BTC weekly range score
- ETH weekly range score
- combined Price Range Score
- Day 1–2 score
- Day 3–4 score
- Day 5–7 score
- combined Intraday Map Score
- Intraday Path: `HIT / PARTIAL / MISS`
- Cycle / Regime result and rolling record
- Rotation result and rolling record

Emoji convention:

- `✅` for a high score or clear hit
- `⚠️` for a partial miss
- `❌` for a material miss

Public score legend:

```text
✅ 80–100: High precision
⚠️ 55–79: Partial accuracy
❌ Below 55: Material miss
```

Permanent formula shown to readers:

```text
Asset Range Score =
70% × containment
+
30% × interval overlap / Jaccard

PRICE RANGE SCORE =
average of BTC and ETH
```

Containment measures how much of the actual move remained inside the forecast. Interval overlap/Jaccard measures how tightly the forecast matched the actual range.

Cycle/regime and rotation are tracked separately from price. Do not hide them inside one blended overall score.

From #16 onward, weekly and intraday forecasts must be frozen prospectively before outcomes are known. Published history is locked; no retroactive score changes.

---

## 3. Weekly Market Update

This is the main interpretive compass, not a live-price snapshot and not a generic market recap.

Every week it must explain:

```text
Last week’s thesis
→ What the market proved
→ What it failed to prove
→ How the probability map changed
→ What this week must resolve
```

Required headings:

- `Last Week’s Thesis`
- `What the Market Proved`
- `What It Failed to Prove`
- `How the Map Changed`
- `This Week’s Test`
- `Weekly Compass`

Avoid obvious statements such as “broad rotation did not happen” without explaining the market mechanism, transmission failure and consequence for the phase map.

The final Weekly Compass should be memorable, usually two short lines connecting the previous test to the coming test.

---

## 4. Cycle Compass

Use simple public language.

Always show:

- the full market-cycle sequence
- `WE ARE HERE`
- current stage
- next decision window
- conditional horizon for the following phase
- what moves the market forward
- what moves it backward

Do not base the section on a single current price print. It describes the durable weekly phase and transition test.

---

## 5. Altcoin Cycle

Time horizons are mandatory and are a defining Cycle Navigator feature.

Always show:

- current altcoin stage with `WE ARE HERE`
- next stage and estimated horizon
- selective-alt-rotation horizon
- broad-altseason horizon
- short explanation of what each future stage means
- conditions that unlock the next stage
- a concise current read

Use conditional language. A time horizon is a scenario window, not a promised date.

---

## 6. Market Outlook

Required content:

- weekly BTC range
- weekly ETH range
- base, bull and bear scenarios with probabilities
- Day 1–2 BTC/ETH range and expected behavior
- Day 3–4 BTC/ETH range and expected behavior
- Day 5–7 BTC/ETH range and expected behavior
- bull confirmation
- bear invalidation
- rotation confirmation

Each public range and scenario must be frozen at publication for next week’s scorecard.

---

## 7. Action language

Use clear public language rather than unexplained internal framework labels.

Permanent wording:

```text
New Entry Signal: Not Active
(The market has not yet confirmed a re-entry window.)
```

Also include `Active Trim Signal` and a concise asset-tier action map.

Default closing instruction when appropriate:

```text
Prepare. Do not chase.
```

---

## 8. Publication and archive rules

- Save each final public post as `PUBLISHED_LOCKED`.
- Preserve the exact published score, wording, forecast ranges and phase calls.
- No retroactive adjustments.
- Corrections, if unavoidable, must be stored as explicit append-only corrections rather than silent edits.
- Archive the publication timestamp, source Master Monday, source handoff and visual-asset hash.
- Public Cycle Navigator forecasts must not be scored against a different internal forecast track.
