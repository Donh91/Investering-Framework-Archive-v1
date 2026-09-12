# Cycle Navigator Visual / Motion Design Skill

## Mission

Turn Cycle Navigator into a premium, cinematic, mobile-first market dashboard while preserving the existing Cycle Navigator authority model exactly.

This skill governs presentation only. It must never create, infer, rewrite, smooth, promote, suppress, or override market state.

## Non-negotiable authority rules

Before changing presentation code, read:

1. `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md`
2. `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
3. the machine package referenced by `week_dir`

Never let LIVE prices rewrite any OFFICIAL weekly state, forecast, score, rotation ladder, altseason countdown, frozen test, or publication status.

If canonical data is unavailable, keep the bounded fallback behavior and show degraded/unavailable state honestly.

Never publish null forecast ranges.

## Design ambition

Target the craft level of a premium editorial / Apple-like financial product with cinematic web storytelling.

The visual reference class includes long-form Fable 5 style websites: depth, parallax, progressive reveals, kinetic hierarchy, restrained 3D cues, scroll-linked storytelling and strong hero composition.

Fable 5 is a reference only. Do not copy source code from `codewithmuh/fable5-websites` unless a compatible license is explicitly present and verified at implementation time.

Prefer original implementation and permissively licensed references.

## Free-only rule

The production website must have zero required paid services, paid UI kits, paid animation libraries, paid fonts or paid hosting dependencies.

Default implementation stack:

- semantic HTML
- CSS
- vanilla JavaScript
- native CSS scroll-driven animations where supported
- IntersectionObserver / requestAnimationFrame fallbacks
- GitHub Pages or another genuinely free static host

Optional external code may only be introduced after verifying its current license and that the production use remains free.

Useful reference projects include:

- Magic UI, MIT: `https://github.com/magicuidesign/magicui`
- Motion Primitives, MIT: `https://github.com/ibelick/motion-primitives`
- React Bits: inspect the exact upstream repository and license before reusing code
- Fable 5 showcase, inspiration only unless licensing changes: `https://github.com/codewithmuh/fable5-websites`

## Visual language

Cycle Navigator is not a crypto casino.

Use:

- near-black navy canvas
- precise cyan / mint / amber state accents
- soft violet only as secondary depth
- glass and blur sparingly
- very subtle grid / noise / atmospheric layers
- large editorial type for the current cycle state
- high information density with generous hierarchy
- rounded geometry that feels engineered, not playful
- motion that explains sequence, causality or state

Avoid:

- rainbow gradients everywhere
- neon overload
- spinning coins
- generic candlestick hero imagery
- fake 3D tokens
- confetti
- attention-seeking infinite motion
- meaningless card hover tricks
- animations that make stale / degraded data look more certain

## Motion hierarchy

Motion must answer one of four questions:

1. Where am I in the report?
2. What changed?
3. Where is capital rotation trying to move?
4. What must unlock before broad altseason?

Preferred motion layers:

### Layer 1, orientation

- 2px page progress line
- sticky compact journey navigation
- current section highlight

### Layer 2, reveal

- section headings rise subtly into view
- cards reveal in short staggered groups
- dynamic lists reveal after data renders
- no element should travel more than roughly 24px for ordinary reveals

### Layer 3, narrative

- Rotation Ladder receives a scroll-linked progress rail
- active/watch states carry more luminance than inactive states
- Altseason Countdown progresses visually as a sequence, not as a date promise
- hero atmosphere shifts subtly with scroll, without moving primary text excessively

### Layer 4, micro-interaction

Desktop fine-pointer only:

- very soft pointer spotlight inside cards
- tiny elevation / saturation changes

Do not rely on hover for critical information.

## Safari / iPhone first

Primary QA targets:

- iPhone viewport around 390 x 844
- larger iPhone viewport around 430 x 932
- Safari portrait first
- Safari landscape sanity check
- desktop Safari / Chromium second

Use `100svh` or similarly safe viewport units where helpful.

Respect safe-area insets for sticky UI.

Avoid scroll listeners that do layout work on every event. Use passive listeners plus one requestAnimationFrame update.

Prefer transform and opacity for animated properties.

Native scroll-driven animations are preferred when available, with an accessible fallback.

## Accessibility

`prefers-reduced-motion: reduce` must disable nonessential motion and reveal all content immediately.

Do not animate focus position.

Keep tap targets usable on mobile.

Never encode state by color alone when a text status exists.

Preserve semantic headings and existing ARIA relationships.

## Performance budget

No autoplay video background.

No required WebGL / Three.js scene for the dashboard core.

No animation framework should be added merely to reproduce effects achievable in CSS + small JavaScript.

Avoid permanent `will-change` on large page regions.

Keep scroll work in one requestAnimationFrame loop.

Avoid expensive full-screen blur changes during scroll.

## Public privacy / identity rule

The public presentation should not visibly advertise the repository owner, GitHub username, internal framework paths or developer identity.

UI copy should say `canonical public pointer` or `OFFICIAL source`, not expose repository ownership.

Note: hiding visible references does not by itself make the backing repository anonymous. Network/API architecture must separately proxy canonical data if true source-level unlinkability is required.

## Content integrity

Motion may increase salience but not certainty.

DEGRADED must remain visually obvious.

Unconfirmed stages must never animate as completed.

A structural score must remain labelled as a component / structural score and not be presented as an overall accuracy percentage.

Null price ranges remain unpublished.

## Implementation pattern

Keep motion isolated from market logic:

- `styles.css`: core visual system
- `app.js`: data fetching and rendering authority
- `motion.css`: enhancement layer only
- `motion.js`: scroll/reveal choreography only

`motion.js` must not fetch market data or modify machine-package values.

Do not import presentation dependencies into `app.js`.

## Definition of done

A motion/design change is complete only when:

- SITE_CONTRACT authority is unchanged
- static content works with JavaScript motion disabled
- all dynamic app content remains readable
- reduced-motion works
- iPhone layout does not require horizontal page scrolling
- sticky navigation does not cover primary content
- rotation / countdown motion reflects existing statuses only
- no paid dependency was introduced
- no visible GitHub owner identity was added
- deployment remains compatible with the existing static Pages workflow
