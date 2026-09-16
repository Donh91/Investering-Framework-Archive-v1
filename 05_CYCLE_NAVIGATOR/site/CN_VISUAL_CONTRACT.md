# Cycle Navigator Visual Contract v1

Status: DESIGN GOVERNANCE CONTRACT
Authority: subordinate to `SITE_CONTRACT.md`, canonical Cycle Navigator data contracts, historical publication integrity and public-product rules.
Baseline: Public Product v2 after PRs #1053 and #1054.

## Purpose

Future visual redesign may make Cycle Navigator substantially more polished, distinctive and premium without changing what the product means.

Design agents, Taste-style reviewers and Codex have broad freedom over pixels and zero independent authority over market semantics, historical facts, scoring, timing, action or data quality.

## Authority order

1. Canonical Cycle Navigator / Handlekompas authority and frozen historical evidence
2. `SITE_CONTRACT.md` and Public Product v2 product rules
3. This visual contract and the Cycle Navigator design system
4. Selected external design-review skills, including Taste candidates
5. Coding agent implementation
6. Visual pre-flight review

No lower layer may override a higher layer.

## Hard locks

### Semantic Lock
A redesign MUST NOT change the meaning, certainty, scope or authority of:
- NOW / PATH / WHY
- official weekly state
- LIVE observation
- action / risk / invalidation language
- score values or score-family meaning
- historical publication records
- forecast ranges
- ETA / timing claims
- missing / unavailable states
- manual, bridge, frozen-prospective or automated scoring-era distinctions

Copy may be shortened only when meaning and uncertainty are preserved exactly.

### State Visibility Lock
Uncertainty and failure states may never be styled away.

The interface must remain able to show, prominently and legibly:
- limited evidence
- unavailable / not published
- unconfirmed
- open / not yet mature
- delayed or missing official feed
- lack of numerical range
- non-comparable historical components

A prettier false-positive is a product defect.

### Historical Integrity Lock
Design may reorganize or progressively disclose historical evidence, but it may not:
- rewrite an old score
- calculate a new historical score to fill a gap
- hide a miss to simplify a chart
- combine non-comparable scoring eras into one synthetic precision percentage
- imply that `—` means zero

### Authority Separation Lock
LIVE context must remain visually distinguishable from the frozen OFFICIAL weekly layer.

LIVE prices and observations may explain or test frozen calls. They may never look like silent replacements for the frozen weekly call.

### Action-First Lock
On iPhone, the first useful screen must answer within roughly ten seconds:
1. What should I do now?
2. Where are we?
3. What matters next?
4. What would invalidate or change the call?

Visual spectacle may not push these answers below decorative content.

### Motion Budget
Motion may:
- establish hierarchy
- indicate state change
- explain cycle progression
- improve spatial orientation

Motion may not:
- delay access to action / phase / next gate
- continuously compete with data
- imply confidence or urgency not present in the evidence
- animate historical values in a way that suggests they are changing

Respect `prefers-reduced-motion`.

## Design-system locks

### Color Consistency
Each semantic state must use one stable visual language across pages. A state color cannot change meaning between NOW, PATH, WHY and Scoreboard.

### Shape Consistency
Cards, pills, controls, progress states and evidence blocks should use a small, intentional shape vocabulary. Avoid one-off component styling.

### Type Hierarchy
Typography must separate:
- decision / action
- phase / state
- evidence
- context
- provenance / caveat

Do not create visual importance by increasing everything.

### Page Theme
Cycle Navigator should feel like one coherent product, not a collection of agent-generated sections. Dark-mode treatment, density, borders, surfaces and motion language must be consistent.

## Permitted redesign freedom

Design agents MAY aggressively improve:
- typography
- spacing and rhythm
- component composition
- information density
- navigation polish
- logo treatment
- visual cycle maps
- evidence cards
- scoreboard readability
- chart / timeline presentation
- responsive behavior
- micro-interactions
- subtle depth and motion

They MAY propose a radically different visual direction as a concept, provided all hard locks remain intact.

## Taste / external design skill policy

Taste-style skills are `EXTRACT / ADOPT SELECTIVELY`, not design authority.

Preferred use:
1. audit existing production v2 without writing code
2. identify visual inconsistency, weak hierarchy and generic-agent patterns
3. propose multiple visual directions against this contract
4. allow a human-selected direction to become the implementation brief
5. use Taste/GPT-style review as a pre-flight visual gate after Codex implementation

Never allow an external generic design skill to rewrite product semantics for visual simplicity.

## Required redesign gate

A design PR may merge only when BOTH gates pass:

### Visual quality gate
- coherent type scale
- coherent spacing system
- consistent colors / shapes
- intentional dark-mode surfaces
- mobile polish
- no generic AI-dashboard clutter
- motion within budget
- no obvious visual regressions

### Cycle Navigator functional gate
- canonical data binding unchanged
- NOW/PATH/WHY semantics intact
- LIVE vs OFFICIAL distinction intact
- fail-closed states intact
- scoreboard/history integrity intact
- historical values unchanged
- unsupported ranges / ETA remain absent
- mobile action comprehension intact

Visual PASS cannot compensate for functional FAIL.
