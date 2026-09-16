# Cycle Navigator Premium Design Refresh Plan

Status: SELECTED DIRECTION / DESIGN PROPOSAL
No production CSS/HTML changes are authorized by this document.

## Entry condition

The functional v2 baseline is merged, deployed and historically bound. The refresh starts from that deployed product. It does not restart product definition.

## User-selected direction — Apple-like professional minimalism

The current production screenshots are the visual anchor. Preserve the light, calm, premium, native-feeling interface rather than replacing it with a dark trading terminal or decorative crypto dashboard.

Target character:
- Apple-like restraint, clarity and confidence
- very light neutral page background
- white content surfaces with subtle borders/shadows
- one deep navy/near-black action surface for the highest-priority NOW state where useful
- navy/ink primary text, cool grey secondary text, restrained blue accent
- generous whitespace and strong typographic hierarchy
- large, readable action/state typography
- segmented NOW / PATH / WHY navigation with native-control feel
- rounded geometry used consistently, not everywhere
- data presented as calm evidence, never gamified
- compass/logo used as a refined brand signature, not a giant decorative hero

The original Cycle Navigator compass identity remains the brand source. Logo treatment may be simplified/resized for interface use, but its visual identity should remain recognizable.

## Explicit anti-direction

Do NOT drift toward:
- Bloomberg/trading-terminal density
- neon crypto aesthetics
- glassmorphism as a dominant language
- large decorative mountain/market hero imagery
- excessive gradients, glows or blue light effects
- dense grids of mini cards
- sci-fi instrument panels
- gratuitous 3D/orbit graphics
- animation that competes with reading
- generic AI-dashboard styling

Taste-style reviewers should actively flag these patterns.

## Taste extraction — what to adopt

Use Taste selectively as design governance rather than design authority.

### Adopt
- audit-existing-project-first workflow
- typography consistency review
- spacing/rhythm review
- Color Consistency Lock
- Shape Consistency Lock
- Page Theme Lock
- anti-slop / generic-pattern review
- responsive/mobile pre-flight
- motion restraint review
- hard visual pre-flight before merge

### Do not delegate
Taste or any external design layer may not alter:
- information architecture
- NOW / PATH / WHY semantics
- action meaning
- frozen forecast meaning
- LIVE/OFFICIAL distinction
- historical scores
- evidence availability
- ETA/ranges
- fail-closed behavior

## Baseline visual findings from current iPhone views

### Keep
- light neutral canvas
- three-way pill navigation
- oversized HOLD/action hierarchy
- strong dark NOW card against light surroundings
- simple white PATH cards
- wide margins and breathing room
- low visual noise
- restrained blue-grey palette
- direct plain-language headings

### Improve
- introduce the real compass brand into the header/navigation without stealing first-screen space
- tighten type-scale consistency between NOW and PATH
- reduce all-caps where it harms calmness while retaining small-label utility
- make truncation impossible for critical NEXT DAYS / NEXT GATE content
- reduce card nesting and repeated borders lower on the page
- create a more intentional spacing token system
- make current/active/watch/not-confirmed states visually distinct without adding bright colors
- make LIVE versus OFFICIAL instantly legible through subtle label/surface treatment
- improve long PATH card scanability with a quiet connective path/rail rather than isolated floating cards
- improve scoreboard readability with editorial spacing and sticky/compact mobile affordances
- integrate the compass motif as a tiny directional/progress cue only where semantically appropriate

## Selected concept family

The previous three-way concept exploration is superseded by one selected family:

### Calm Precision

This combines the trust and whitespace of Quiet Institutional with only the useful interaction discipline of Precision Instrument.

It is NOT a dark instrument dashboard.

Design language:
- light-first interface
- near-black/navy action emphasis
- restrained Cycle Navigator blue
- SF/Apple-like system typography stack where platform-appropriate
- large titles, short copy, progressive disclosure
- thin dividers, subtle shadows, quiet surfaces
- compact compass cues for current position/path progression
- motion limited to state transitions, navigation and path progression

## Logo treatment

Use the supplied Cycle Navigator compass/logo as the visual reference.

Interface variants should include:
1. compact compass mark for header/favicon/navigation
2. horizontal wordmark for desktop/about/share contexts
3. full logo/tagline reserved for brand/about/footer/social use

Do not place the full large logo above the NOW action on mobile. Action comprehension remains first.

## Implementation sequence after approval

1. Freeze exact production screenshot baseline and current semantic DOM/data hooks.
2. Build tokens: type, spacing, radii, border, shadow, semantic colors.
3. Refresh global shell/navigation/header with compact compass branding.
4. Refine NOW first-screen hierarchy without changing content meaning.
5. Refine PATH into a connected calm progression rather than a card stack.
6. Refine WHY/evidence and Scoreboard using fewer containers and stronger editorial rhythm.
7. Add only subtle motion with `prefers-reduced-motion` support.
8. Run Taste-style pre-flight.
9. Run CN semantic/data/fail-closed gates.
10. Compare against baseline on iPhone before any merge.

## Taste-style pre-flight checklist

A design fails if any answer is no:
- Does it still feel calmer than a typical crypto dashboard?
- Can HOLD/current action be understood immediately?
- Is the phase visible without scrolling through decoration?
- Is NEXT GATE fully readable, never visually truncated by design?
- Are OFFICIAL and LIVE distinguishable without jargon overload?
- Is there one coherent radius vocabulary?
- Is there one coherent spacing rhythm?
- Does blue mean the same thing everywhere?
- Are dark surfaces reserved for intentional emphasis?
- Is motion informational rather than decorative?
- Does the compass/logo strengthen identity without stealing hierarchy?
- Does PATH read as conditional progression rather than destiny?
- Are historical misses/unavailable values as visible as successes?
- Does the interface still work when ranges or evidence are absent?
- Does it look designed rather than agent-generated?

## Permanent post-refresh quality control

Future changes must pass both:

`CALM PRECISION VISUAL CONSISTENCY` + `CN SEMANTIC INTEGRITY`

Taste-style tooling remains a reviewer/advisor layer. Cycle Navigator contracts remain authority.