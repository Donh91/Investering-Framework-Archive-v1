# Cycle Navigator Visual / Motion Design Skill

## Mission

Maintain Cycle Navigator as a premium, Apple-level, mobile-first market instrument while preserving the Cycle Navigator authority model exactly.

Presentation may improve comprehension, hierarchy and delight. It must never create, infer, rewrite, smooth, promote, suppress or override market state.

## Approved design authority

**Quiet Precision** is the approved production direction.

Read `05_CYCLE_NAVIGATOR/site/DESIGN.md` before changing the public UI.

The page should feel calm, exact and expensive rather than loud. The visual system is:

- off-white / white primary canvas,
- deep navy `#07172f` ink,
- CN blue `#2f6fda` accent,
- generous whitespace,
- subtle hairline borders,
- very limited shadows,
- consistent thin-line icons,
- the Cycle Navigator compass as the primary identity,
- a small number of dark navy instrument surfaces where contrast genuinely helps.

CN Instrument may contribute isolated high-contrast surfaces. It must never turn the page back into a dark crypto dashboard.

## Authority rules

Before changing presentation code, read:

1. `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md`
2. `05_CYCLE_NAVIGATOR/site/DESIGN.md`
3. `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
4. the machine package referenced by `week_dir`

Never let LIVE prices rewrite OFFICIAL weekly state, forecast, score, rotation ladder, altseason countdown, frozen test or publication status.

If canonical data is unavailable, show degraded/unavailable state honestly.

Never publish null forecast ranges.

A structural/component score must never be presented as overall precision.

## Design principles

Use Apple-style restraint and design-engineering judgment:

- remove before adding,
- content over chrome,
- typography and spacing before decoration,
- one strong hierarchy rather than many equally loud cards,
- immediate interaction feedback,
- motion only when it explains feedback, spatial continuity, state transition or sequence,
- no animation on functional data simply because it looks impressive.

The user should understand the current cycle state quickly on an iPhone without reading the full technical report.

## Information hierarchy

The first mobile viewport should communicate:

1. OFFICIAL current cycle state,
2. LIVE context,
3. next confirmation gate.

Then progressively disclose:

- this-week and 2–3-week working map,
- altseason / mania clocks,
- cycle phase timeline,
- rotation ladder,
- public action compass,
- verified calibration,
- current open scoring,
- X/public archive and technical audit details.

Long technical text belongs in progressive disclosure below the primary state.

## Icon language

Prefer a coherent thin-line family derived from permissively licensed icon geometry or original CN SVGs.

Core semantic icons:

- compass = cycle state,
- signal = market evidence,
- clock = timing / ETA,
- route = cycle path,
- target = action / forecast,
- check / shield = verification,
- chart = calibration.

Do not use emoji as primary interface icons.

## Motion budget

Motion must answer a real question:

1. What changed?
2. Where did this surface come from?
3. What state changed?
4. What is the next step in the cycle sequence?

Default to no motion for frequently read data.

Implementation rules:

- animate transform and opacity where possible,
- keep ordinary UI transitions short,
- use strong ease-out rather than slow ease-in,
- avoid looping ambient motion,
- avoid bouncing cards / numbers,
- do not animate uncertainty into apparent certainty,
- respect `prefers-reduced-motion`.

## Free-only rule

Production must not require paid hosting, fonts, UI kits, motion libraries or design services.

Default stack:

- semantic HTML,
- CSS,
- vanilla JavaScript,
- native browser APIs,
- GitHub Pages or another genuinely free static host.

## Safari / iPhone first

Primary QA:

- ~390 × 844 Safari portrait,
- ~430 × 932 Safari portrait,
- landscape sanity check,
- desktop second.

Requirements:

- safe-area aware,
- no horizontal page scrolling,
- touch targets remain practical,
- no hover-only critical information,
- compositor-friendly motion,
- readable typography without zoom.

## Anti-patterns

Do not regress toward:

- near-black full-page crypto dashboards,
- rainbow gradients,
- neon overload,
- excessive glassmorphism,
- fake 3D coins,
- candlestick hero art,
- generic AI card grids,
- confetti,
- infinite motion,
- meaningless hover tricks,
- decorative animation on charts / financial data.

## Public privacy / identity

Do not visibly advertise repository owner, GitHub username, internal framework paths or developer identity in the public presentation.

The current GitHub Pages hostname is a temporary hosting constraint; future privacy migration may replace it without changing the Quiet Precision design system.

## Definition of done

A design change is complete only when:

- SITE_CONTRACT authority is unchanged,
- `DESIGN.md` is respected,
- first mobile viewport communicates the current state clearly,
- all dynamic content remains readable,
- reduced-motion works,
- no horizontal page scroll exists,
- clocks reflect existing OFFICIAL windows only,
- paused/locked phases remain visibly paused/locked,
- verified and legacy score series remain distinct,
- no paid dependency is introduced,
- no visible repo-owner identity is added to page content,
- deployment remains compatible with the existing static Pages workflow.
