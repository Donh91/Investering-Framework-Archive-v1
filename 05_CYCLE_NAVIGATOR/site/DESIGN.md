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
