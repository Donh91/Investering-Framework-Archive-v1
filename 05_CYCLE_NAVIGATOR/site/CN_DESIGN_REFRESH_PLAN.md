# Cycle Navigator Premium Design Refresh Plan

Status: PROPOSAL ONLY
No production CSS/HTML changes are authorized by this document.

## Entry condition

Begin visual redesign only after the functional v2 baseline is merged, deployed and its historical scoreboard is complete. That condition is now satisfied by the production baseline following PRs #1053 and #1054.

The refresh starts from the deployed product. It does not restart product definition.

## Phase 1 — Baseline freeze

Capture and retain:
- current production commit
- deployed Pages run / artifact
- mobile and desktop reference views when available
- current NOW / PATH / WHY information order
- current full historical scoreboard structure
- current fail-closed examples

The baseline is the semantic reference, not the visual ceiling.

## Phase 2 — Audit only

Run the selected design-review layer against the existing product without code changes.

Audit for:
- generic dashboard patterns
- weak first-screen hierarchy
- inconsistent spacing or radius vocabulary
- overuse of cards / pills
- weak distinction between action, state, evidence and caveat
- mobile density problems
- underused negative space
- confusing motion
- weak PATH storytelling
- scoreboard scanability
- visual distinction between frozen OFFICIAL and contextual LIVE data
- logo / brand coherence

Every finding must identify whether it is visual-only or touches a locked product rule.

## Phase 3 — Three visual concepts, same semantics

Generate three concept directions using the exact same information and states.

### Concept A — Quiet Institutional

Character:
- restrained, high-trust market research product
- typography and whitespace carry hierarchy
- minimal glow
- thin evidence lines and calm surfaces
- data feels audited rather than gamified

Best for:
- credibility
- weekly reading
- scoreboard/history
- professional sharing

Risk:
- can become too conservative or generic if brand character is weak

### Concept B — Precision Instrument

Character:
- premium navigation/instrument aesthetic
- the cycle path becomes the signature visual object
- subtle compass/orbit geometry
- compact data surfaces
- motion explains progression and confirmation gates
- action and next gate feel like instrument readings

Best for:
- distinctive Cycle Navigator identity
- PATH storytelling
- visual logo integration
- recurring weekly engagement

Risk:
- motion or instrumentation can become decorative if not tightly governed

### Concept C — Editorial Intelligence

Character:
- high-end editorial/data publication
- strong headline typography
- fewer containers, more composition
- weekly narrative and evidence blocks flow like a premium report
- historical accountability appears as an elegant ledger rather than a dashboard table

Best for:
- first-time comprehension
- public storytelling
- social screenshots
- making complex reasoning feel simple

Risk:
- must retain enough state structure for fast recurring use

## Preferred exploration order

1. Precision Instrument as the likely signature direction
2. Quiet Institutional as the trust-control reference
3. Editorial Intelligence as the hierarchy/choreography challenger

Do not pick a winner from prose. Render all three against the same real CN state first.

## Phase 4 — Concept selection

Selection rubric:
- action understood in <10 seconds on iPhone
- current phase instantly visible
- next gate and invalidation instantly findable
- frozen vs LIVE distinction obvious without machine jargon
- historical scoreboard reads honestly
- visual identity feels recognizably Cycle Navigator
- no semantic information lost
- no unsupported confidence created
- design remains maintainable by coding agents

Select one direction before implementation.

## Phase 5 — Implementation

Create a dedicated `agent/task-*` design branch.

Implementation principles:
- preserve DOM/data hooks where practical
- build a small reusable token/component system first
- avoid repeated one-off CSS fixes
- change one visual system at a time: type → spacing → surfaces → components → motion
- maintain responsive behavior throughout rather than patch mobile last
- use actual production data states, including missing and limited-evidence cases

## Phase 6 — Dual review gate

### Design pre-flight
Review:
- typography
- spacing
- shape consistency
- color consistency
- visual hierarchy
- dark-mode quality
- responsive layout
- reduced-motion behavior
- visual regressions
- generic AI aesthetic / over-decoration

### CN semantic pre-flight
Re-run:
- v2 release validator
- Pages-equivalent build
- privacy checks
- official/LIVE separation checks
- historical scoreboard checks
- null range fail-closed checks
- mobile action hierarchy checks

Both must pass.

## Permanent post-refresh quality control

After adoption, the selected design rules should become regression checks for future coding agents. Any agent adding a section must pass both:

`VISUAL CONSISTENCY` + `CN SEMANTIC INTEGRITY`

This turns the external design skill from a one-off makeover into a controlled visual quality layer around the product.
