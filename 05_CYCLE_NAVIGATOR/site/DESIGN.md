# Cycle Navigator Design Language — Quiet Precision

> Cycle Navigator should feel like an Apple-level financial instrument: calm, precise, spacious and immediately legible. The compass logo and CN blue provide identity; data and hierarchy provide the drama. Never add decoration that competes with the cycle state.

## Approved direction

**Quiet Precision** is the production design authority.

Use the approved Apple-level design study as the visual reference. CN Instrument may contribute small, high-contrast instrument surfaces (for example the verified score card), but the page must remain primarily light, quiet and editorial.

## Brand

- Primary canvas: off-white / white.
- Primary ink: deep navy `#07172f`.
- Brand accent: CN blue `#2f6fda`.
- Secondary blue/cyan is allowed only for hierarchy, chart progress or active confirmation.
- The Cycle Navigator compass is the primary brand mark and must stay recognizable.
- Prefer a consistent thin-line icon family: compass, signal, clock, route, target, shield/check, chart.
- No emoji as primary UI icons.

## Hierarchy

The first mobile viewport should answer, in order:

1. What is the current official cycle state?
2. What is happening live now?
3. What is the next confirmation gate?

Then progressively disclose:

- working forecast,
- cycle / altseason timeline,
- capital rotation,
- public action compass,
- verified calibration / current scoring,
- public X record and audit detail.

Do not force the user to read every technical detail before understanding the current state.

## Surfaces

- Generous whitespace beats extra cards.
- Default surfaces are white with a subtle hairline border.
- Use shadows sparingly; prefer borders and spacing.
- Dark navy surfaces are reserved for a small number of instrument moments such as verified score / high-salience state.
- Avoid nested glass-on-glass surfaces.
- Rounded corners should feel engineered, not playful.

## Typography

- Use the Apple/system stack: `-apple-system`, `BlinkMacSystemFont`, `SF Pro Display`, `SF Pro Text`, `system-ui`.
- Large headlines use tight optical tracking and short line length.
- Body copy must remain readable on iPhone Safari; avoid dense walls of text.
- Small labels may use restrained uppercase + tracking for instrument semantics.

## Motion

Motion is explanatory, not decorative.

Allowed purposes:

- feedback,
- spatial continuity,
- state transition,
- explaining cycle sequence.

Rules:

- frequent data surfaces stay still;
- prefer transform / opacity only;
- no slow infinite ambient motion;
- no bouncing data cards;
- press feedback should be immediate and subtle;
- respect `prefers-reduced-motion`;
- do not animate OFFICIAL uncertainty into false confidence.

## Data integrity

Design never creates market authority.

- LIVE market data is context only.
- OFFICIAL state comes from the Cycle Navigator frozen package.
- DEGRADED remains visible.
- Structural/component scores are not presented as overall precision.
- Null ranges are not published.
- Broad altseason and mania timers remain paused/locked when OFFICIAL CN has no valid calendar ETA.
- Current scoring stays open until completed evidence exists.

## Mobile-first acceptance

Primary viewport: roughly 390 × 844 Safari portrait.

Before shipping:

- no horizontal page scroll,
- minimum practical touch targets,
- safe-area aware,
- first screen clearly communicates state,
- live values are visually subordinate to OFFICIAL authority,
- timeline is understandable without reading long prose,
- calibration distinguishes verified scores from legacy X claims,
- progressive disclosure is used for long public/audit text.

## Anti-patterns

Do not regress toward:

- crypto-casino neon,
- rainbow gradients,
- excessive glassmorphism,
- generic AI dashboard card grids,
- spinning coins / candlestick hero art,
- motion for motion's sake,
- several competing accent colors,
- long technical paragraphs above the core state.

## Design review standard

Use Apple-style restraint and design-engineering review principles: remove before adding, make interaction feedback immediate, keep animations purposeful, and judge polish on a real narrow mobile viewport before declaring a redesign complete.


## Frozen weekly chart / language control

The weekly price instrument is a restrained dark navy exception inside the existing light page: one BTC/ETH selector, fine grid, right price scale, blue immutable corridors/forecast, green observed path, explicit observation cutoff and a single day readout. TradingView Lightweight Charts supplies the financial-chart interaction and typography geometry. No fabricated candles or decorative market movement.

PATH uses one visible narrative thread: leadership → rotation → altseason → protection/reset. Its connector dots encode source-published time distance only, using fewer illuminated dots for longer windows and none for unsupported timing. They never depict completion or probability. Frozen weekly timing is the conservative ceiling when a faster live review window disagrees.

The DA/ENG control is a compact upper-right segmented button, with a navy active state and a saved language preference. Keep both controls readable and operable on narrow iPhone screens. Technical validation is separate from Morten's visual acceptance.


## Premium Finish · site chart design contract (29 October 2026)

**Original references**: official site https://donh91.github.io/Investering-Framework-Archive-v1/ ; owner-provided iPhone screenshots 28–29 October (dark Graph B, oversized explanation, uninformative flat dashed line). Site design-skill review used the real site capture and extracted site tokens: navy `#0A2546`, light background `#F5F7FA`, accent blue `#346ED7`, ink `#07172F`; typography uses the existing system font stack. Hex tokens are *observed source colors*, while the new chart-specific quiet navy `#0c1b31`, green `#56d6ae`, and forecast blue `#8fbbfa` are **authored design choices**, not extracted brand facts.

### Editorial hierarchy and constraints

1. Outside chart: one white editorial surface. Inside: quiet dark navy instrument, compact BTC/ETH readout and a two-item legend (actual price; original high/low). Third dashed-forecast legend item appears only if independently issued original seven-point expected-close data are valid.
2. Preserve three verified Monday forecast range windows as subtle independent *bands and boundaries*, not an interpolated expected-price trajectory. Seven independently issued daily low/high points take precedence when admissible; both retain initial freeze and reason. Real observed hourly price has green unbroken stroke only across contiguous verified samples.
3. Remove all synthetic W44 test-line/three-midpoint curve, the large test-warning box, and duplicate "not issued" banners; nothing new may invent an official daily closing-price path. No consumer-visible letter "B".
4. Hide detailed low/high tables behind one accessible minimum-44px summary, and keep seven per-day research explanations behind another optional disclosure. Values remain selectable and source exact.
5. At 390 and 430 CSS pixels, graph must not horizontally overflow; show 248px tall plot with 46px compact price-axis rail, short labels and clear observed stroke. On desktop show 282px plot, and do not stretch typography. Use system-font numerical tabular lining and keep labels readable.
6. Source not available, stale, and cross-asset switching must fail closed and show truthful state. No independent trading actions, score authority, or probability interpretation.
7. **Two independent release gates**: technical/exact-head E2E and data/source integrity + actual rendered screenshot at 390/430 and desktop checked for hierarchy, contrast, truncation, responsive layout and whether green actual vs blue frozen range is visually unambiguous. Screenshots captured on PR via existing root Chrome CDP smoke (markers `CN_DESIGN_SCREENSHOT_390_PART`, `CN_DESIGN_SCREENSHOT_430_PART`). A screenshot *saved or captured* is not visual approval by itself. Physical Safari, VoiceOver, and zoom remain unverified unless actually inspected.

### Research/product split

The original daily forecast contract `CN_FROZEN_DAILY_RANGE_PLAN_v1` is a prospective producer with per-day `low/high/why/invalidate_if`. It is *conditional on source evidence*, and refusal remains valid. Daily 2–3-week macro-influenced scenarios are an explicitly separate Task 2 shadow research horizon, not a public numerical signal until proved with point-in-time freezes, width-aware baseline scores and post-outcome evaluation. Do not backfill W44.
