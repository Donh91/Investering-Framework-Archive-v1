# Cycle Navigator PATH v3 — Cycle Timeline + Weekly Rotation

**Status:** IMPLEMENTATION SPEC  
**Date:** 2026-10-06  
**Scope:** public Cycle Navigator PATH surface only  
**Supersedes presentation:** PATH v2 three-track layout as the primary information architecture  
**Does not supersede:** source ownership, Compass authority, scoring, forecast freezes, protection/sell authority, privacy, historical records

## 1. Problem statement

The current PATH page is technically correct but visually and conceptually overloaded.

Three separate presentation systems overlap:

1. MARKET CYCLE renders short-horizon Compass decision windows (0–12h, 1–3d, 5–7d, 2–3w, 4–8w).
2. ROTATION renders seven full cards from BTC to MEMES.
3. ALTCOIN CYCLE TIMER renders a second phase ladder that partially repeats ETH, large/mid, small, micro and broad-altseason progression.

This creates a hierarchy problem:

- NOW/Compass already owns short-horizon directional windows.
- PATH should explain the market journey, not repeat the NOW page.
- Rotation should show where capital is now and what opens next, not require seven near-identical cards.
- Altseason ignition is a milestone inside the cycle journey and should not require a second long duplicated ladder.

User screenshots on 2026-10-06 confirm the issue on iPhone: the current Decision Windows rail is visually attractive but semantically belongs to Compass, while the actual cycle route is lower on the page and competes with Rotation + Altcoin Timer.

## 2. Product objective

PATH must answer, in this order:

1. **Where are we on the crypto market journey?**
2. **What phase comes next if confirmation arrives?**
3. **Where is capital rotating this week?**
4. **What specifically must happen before the next risk tier opens?**
5. **How far are we from Altseason Ignition / broad altseason?**

The page should feel like a live cycle map, not a second dashboard of time horizons.

## 3. New information architecture

PATH v3 has two primary visual systems plus compact supporting context.

### A. MARKET CYCLE — primary hero timeline

This becomes the dominant visual element.

Canonical public journey:

1. BTC leadership
2. Ethereum leadership
3. Large + mid rotation
4. Altseason ignition
5. Micro acceleration
6. Broad altseason
7. Mania / euphoria
8. Distribution
9. Exit / protection
10. Cooldown / re-entry

The timeline is presentation-only. It may use live Compass/weekly source-owned states to identify a **current checkpoint** and a **next watch target**, but it MUST NOT fabricate a long-cycle classification.

Semantics:

- **Blue:** current supported checkpoint on the route.
- **Amber:** next supported watch target.
- **Grey:** later reference phases, not confirmed.
- A structured long-range destination may be shown separately as context, never silently converted into current phase.
- If no live checkpoint is defensible, show “CURRENT CHECKPOINT NOT CONFIRMED” rather than guessing.

This replaces the current PATH Decision Windows rail. The short-horizon 0–12h / 1–3d / 5–7d / 2–3w / 4–8w timeline must no longer be the primary PATH visualization.

### B. THIS WEEK'S ROTATION — compact live rail

Rotation becomes one compact horizontal/scrollable rail:

BTC → ETH → LARGE → MID → SMALL → MICRO → MEMES

Each node contains only:

- asset tier label
- concise public status
- visual state

No seven stacked cards.

Below the rail, show at most three compact readouts:

1. **CURRENT POSITION** — furthest currently supported tier.
2. **NEXT GATE** — first downstream tier that is not yet active, plus source-owned ETA/watch window if available.
3. **WHAT UNLOCKS IT** — short public-language explanation from the next tier's existing Compass reason / weekly context.

The section represents the current weekly rotation map, not a prediction that capital must move through every tier by Sunday.

Optional week framing may say “THIS WEEK” / forecast week, but MUST NOT synthesize day-by-day rotation timing.

### C. ALTSEASON WATCH — compact milestone, not another long timeline

The existing long ALTCOIN CYCLE TIMER ladder is retired as a separate repeated sequence.

Altseason remains highly visible as a compact watch panel attached to the cycle timeline:

- **Current checkpoint**
- **Next watch:** ALTSEASON IGNITION when appropriate
- **Meaning:** small caps begin to participate
- **Watch window:** source-owned conditional ETA only
- explicit “only if confirmation arrives”
- no browser countdown
- after ignition, focus can advance to Micro acceleration → Broad altseason → Mania / Euphoria → Distribution / protection → Re-entry using the existing source-owned transition logic

Protection remains separate authority:

- distribution: COMPASS_PROTECTION_TRACKER_v1
- exit/sell: COMPASS_SELL_ASSESSMENT_v1
- re-entry: COMPASS_PROTECTION_TRACKER_v1

The panel is a milestone/readout, not a second phase map.

## 4. Source ownership

PATH v3 changes presentation only.

### Market cycle / current checkpoint

May consume:

- Official Compass capitalization_ladder
- Official Compass structured horizons
- Cycle Navigator decision_projection
- existing weekly rotation context
- existing protection/sell/re-entry projections

It MUST NOT:

- infer a long-cycle stage from short-horizon direction
- promote a forward destination to current phase
- parse free-form prose into a new market classifier
- create a new cycle score
- create ETA arithmetic in browser

### Weekly rotation

Live statuses and ETA come from typed Official Compass capitalization_ladder.

Weekly CN rotation text is supporting context only.

MICROCAPS must never proxy MEMES.

### Altseason watch

Use existing altcoinTarget / source-owned target logic.

Default target remains:

**ALTSEASON IGNITION — Small caps begin to participate**

until a later governed stage is actually activated.

## 5. Exact UI hierarchy

### PATH header

Title:
**The market journey.**

Subtitle:
**Follow the cycle from Bitcoin leadership through rotation, altseason and protection. Blue shows the current supported checkpoint. Amber shows what the market must unlock next.**

Remove wording that advertises “three connected views”.

### Cycle status strip

At most three compact facts:

- CURRENT CHECKPOINT
- NEXT WATCH
- LONG-RANGE VIEW

Do not repeat NOW-page Bull/Bear or full directional horizon cards.

### Market cycle timeline

Horizontal mobile-first rail.

Suggested labels:

- BTC leadership
- ETH leadership
- Large caps
- Mid caps
- Small-cap ignition
- Broad altseason
- Mania
- Distribution
- Re-entry

Nodes may be swipeable on narrow screens. Mark the first phase after the current checkpoint as `NEXT`; preserve the source-owned Altseason target as a separate `WATCH` milestone if it lies later in the route.

Show each source-supported phase ETA on its incoming route segment as `ETA FROM NOW`. Display conditionality beside that range. ETAs are independent snapshots measured from now, may overlap and MUST NOT be added together. Unsupported ETAs remain absent and MUST NOT be inferred from phase order.

A compact dotted connector reflects only the destination phase’s current Compass gate state: WAIT = no filled dots, WATCH / BUILDING = partial amber dots, CONFIRMED / ACTIVE = blue dots. These are categorical source-state markers, not a percentage, a time estimate or deterministic progress. The active connector may use a restrained pulse when the source is WATCH; no dot may travel as though time or market progress were being measured.

The timeline should be fun to follow visually, but never imply deterministic progress. Large and mid caps are intentionally combined at the cycle level; the detailed weekly Rotation rail keeps LARGE and MID separate. This prevents the cycle timeline from duplicating the risk-curve rail.

### Altseason watch card

Placed directly below cycle rail.

Example:

ALTSEASON WATCH  
Next milestone: **ALTSEASON IGNITION**  
Small caps begin to participate  
**GATE STATUS · WAITING FOR CONFIRMATION**  
Any supported ETA is shown once on the milestone’s route segment, measured from now. Conditional windows require confirmation and are not countdowns.

When a later phase becomes relevant, the same card changes target rather than adding another timeline.

### Rotation section

Header:
**2 · THIS WEEK'S ROTATION**

Title:
**Where capital is moving now.**

Subcopy:
**A live risk-curve map for this week. The next tier only opens when its own signal confirms.**

One rail only:

BTC → ETH → LARGE → MID → SMALL → MICRO → MEMES

Below:
- CURRENT POSITION
- NEXT GATE
- WHAT UNLOCKS IT

Long explanations stay behind one optional disclosure: **Why this rotation?**

## 6. Duplication removal

Remove from primary PATH:

- MARKET CYCLE Decision Windows rail
- repeated near-term / week-ahead / long-cycle summary tiles as a dominant block
- seven stacked Rotation cards
- the long Altcoin Cycle Timer stage list

Keep only where uniquely useful:

- weekly context: short expandable detail
- long-range uncertainty: compact status
- altseason timing: one watch panel
- protection/exit/re-entry: phase nodes and compact watch state
- detailed 2–3w / 4–8w prose: More cycle context disclosure

## 7. Fail-closed rules

1. No current checkpoint from unavailable Compass.
2. No fabricated ETA.
3. Conditional ETA must include confirmation semantics.
4. No MEMES inference from MICROCAPS.
5. No forward long-range destination presented as current.
6. No protection state presented as automatic sell.
7. No site-side synthesis of Bull/Bear or new market classifier.
8. If sources disagree or alignment fails, live checkpoint/rotation fail closed while frozen weekly context may remain visible.

## 8. Mobile acceptance criteria

On iPhone, within the first PATH viewport plus one short scroll, the user should see:

- current cycle checkpoint
- next watch target
- the visual cycle journey
- altseason watch window if supported

The user should not encounter:

- repeated 0–12h/1–3d/5–7d/2–3w Compass rail
- multiple separate phase ladders saying roughly the same thing
- seven tall rotation cards

Rotation rail should fit as a compact swipeable sequence with all tier names readable.

## 9. Regression / CI acceptance

Release gates must assert:

- new PATH contract marker: `CN_PATH_CYCLE_ROTATION_v3`
- no primary `DECISION WINDOWS` rail in marketCycleTrack
- cycle journey contains BTC leadership through Distribution / Re-entry
- current checkpoint and next watch are separate
- Altseason watch is compact and source-owned
- Rotation remains BTC → ETH → LARGE → MID → SMALL → MICRO → MEMES
- Rotation is rendered as a rail, not seven stacked card components
- next gate ETA uses existing pathEta/timingWindow logic
- no countdown Date/Math arithmetic is introduced
- legacy three-track v2 marker is not required by public release gates
- public Compass alignment remains required
- mobile CSS contains cycle rail + compact rotation rail behavior

## 10. Migration plan

1. Archive this spec.
2. Implement new renderer on a fresh branch from current main.
3. Reuse existing source helpers wherever possible.
4. Retire duplicate renderer output, not underlying source data.
5. Update SITE_CONTRACT with PATH v3 IA.
6. Update validate-v2 and Pages/Public Contract workflow markers.
7. Build + parse validation.
8. Open PR.
9. Exact-head CI.
10. Merge only when green.
11. Verify main gates.
12. Verify exact merge-SHA Pages artifact and public Compass binding.

## 11. Non-goals

This change does not:

- alter Compass market logic
- alter Master Monday / CN forecasts
- alter Bull/Bear mapping
- alter scoring or historical records
- create a new market classifier
- create new sell/re-entry logic
- expose private thresholds, weights, prompts or paths

## 12. Product decision

This change is a versioned exception to the previous PATH v2 product freeze because a concrete mobile usability problem has been documented with production screenshots: Compass horizon duplication, repeated phase ladders and excessive vertical density.

The new architecture should be considered the preferred PATH presentation if and only if its exact-head release gates and post-deploy verification pass.


## 2026-10-07 decision clarity build checkpoint

Status: OPERATIONAL IMPLEMENTATION IN PROGRESS. User-authorized extension of PATH v3, preserving the existing design and source authority. Base: b97a4e14abd5b9e02f0052da97b09251d814b321. Task branch: agent/task-20261007-path-decision-clarity.

### Audit findings and approved scope

- The overview repeats a conditional 1–7d Altseason watch and calls it NEXT while Large + mid is the sequential next checkpoint. Replace this numeric summary with NEXT CHECKPOINT and its typed gate status. Phase timing stays on the route.
- Market Cycle is the macro journey. Rotation is this week's segment permission, including a separate MEMES gate. Altseason Watch is a compact opportunity/protection milestone, never a third repeated journey.
- Add a compact action lens for investor, swing and high-beta/meme readers, reading only official Compass action, sell assessment, capitalization permissions and re-entry. Warnings never create a sell instruction.
- Add an automated weekly visual in PATH after the cycle/rotation readout: immutable DAY 1–2, DAY 3–4 and DAY 5–7 BTC/ETH forecast bands versus published observed ranges to date from CN_PUBLIC_LIVE_PRICE_PRECISION_v1. Monday–Sunday horizontal calendar, observation cutoff and data gaps explicit. Reuse the existing hourly owner delivery chain and public schema. Do not publish restricted raw OHLC, draw a guessed close-price curve, infer direction from band midpoints, or treat the precision score as trade confidence.
- NOW gains one always-present compact dip/pullback card with expandable evidence, source ETA, confidence quality, classification, sell authority and re-entry. Existing data currently classifies ORDINARY RETEST WATCH with LOW evidence quality and unquantified depth/severity. Do not call it a confirmed large pullback or assert profitable sell/rebuy edge. Missing depth, duration and early re-entry remain visibly unquantified/unconfirmed.
- Remove duplicated primary risk summaries as this card takes over that job. Preserve existing Compass directional evidence and action authority.

### Source and safety manifest

Archive decision: EXISTING_OWNER_UPDATE. Classification: OPERATIONAL. Primary owner: this specification and SITE_CONTRACT.md. No canonical index, routing, source governance, workflow, credentials or backup changes planned. Normal isolated branch writes and reviewed PR only; no destructive source/recovery authority used. Backup scope: Git version history, no independent Vault snapshot claim. Public-only presentation work; existing sanitized public projections are the inputs. Round 3 and private source values are outside scope.

### Completion and resume requirements

1. Read this checkpoint and current task-branch diff before continuing.
2. Finish source audit, implement JS/CSS with progressive disclosure, and test valid, stale, missing and misaligned data cases.
3. Run existing public-product/contract validators and exact-head CI. Archive concrete validation outcomes here.
4. Merge only after checks pass, verify Pages exact SHA and artifact, inspect live browser output. Record any mobile acceptance limits honestly; issue #1518 is not PASS without actual viewport evidence.
5. Read current data/storage/architecture/automation health. Report scoped product success separately from pre-existing estate alerts.


## Decision clarity implementation record, 2026-10-07

Status: OPERATIONAL, implemented on task branch; deployment pending.

- Overview now uses sequential NEXT CHECKPOINT and no duplicate numeric timing. The repeated current-setup tile is reduced to one short context line. The full visual legend moves behind More cycle context; the route retains its short legend. Past checkpoints do not display future arrival ETAs.
- Market Cycle remains the macro route, Rotation remains segment permission, Altseason Watch remains the compact milestone. No separate altcoin ladder is recreated. A collapsed action lens preserves investor, swing sell/re-entry and high-beta/meme permissions without repeating NOW horizon cards.
- Weekly range journey renders two responsive SVG charts from existing public frozen and observed ranges. Bars represent each window’s aggregate low/high, not a chronological close-price path. The final frozen window spans Fri–Sun; upcoming hours and incomplete windows remain empty. Labelled boundary breaches show distance, without changing the official range score.
- NOW retest card replaces the repeated primary risk tile. Current ordinary retest classification stays unconfirmed; LOW quality is qualitative. Depth and duration are unavailable in the current typed signal. Sell/rebuy edge is not established when the separate sell assessment is unavailable. Re-entry remains source-owned and can remain inactive.
- PATH additionally requires an OK public Compass before accepting ALIGNED live overlays. Unavailable/stale evidence is never upgraded into a risk call. No workflows, source engines, raw-data schemas, frozen forecasts or historical scores were modified.

Validation checkpoint: node syntax validation passed for both changed browser scripts. Existing and new renderer checks: 123/123 public-product release checks passed locally. Synthetic tests cover issue/week mismatch, unavailable source, immutable input preservation, complete coverage only, labelled breach, stale observation, ordinary unconfirmed risk and stale Compass risk rejection. Exact-head CI and deployed visual acceptance remain pending.

Pre-change health snapshot: architecture evidence GREEN; automation production health RED with pre-existing adaptive-decision-miss-validation and edge001-t2-registry alerts. Product CI success must not be represented as aggregate estate health.
