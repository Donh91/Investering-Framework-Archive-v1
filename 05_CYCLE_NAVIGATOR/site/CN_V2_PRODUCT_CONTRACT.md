# Cycle Navigator Public Product v2

Status: IMPLEMENTATION CONTRACT
Owner: #1012 / PR #1016

## Product identity
Cycle Navigator is not a crypto quote dashboard. It answers four public questions:
1. What should I do now?
2. Where are we in the cycle and what is likely next?
3. Why does the evidence place us here, and what unlocks the next phase?
4. How accurate has the frozen historical record been?

## Public navigation
Primary navigation is deliberately limited to three mobile-first views: `NOW / PATH / WHY`.

Scoreboard and methodology are not competing top-level destinations. They live as concise, expandable proof layers inside `WHY`, with deep links/anchors allowed for visitors who want the full record. This keeps the first iPhone read action-first while preserving accountability.

### NOW
Action-first. Use only existing canonical Handlekompas/Cycle Navigator outputs. No independent website analysis.
- hero answers `WHAT SHOULD I DO NOW?` in one concise stance
- current phase and immediate risk/direction
- current 0-24h posture where canonically supported
- segment map from large caps through microcaps/memes only where canonical data exists
- next 1-3 days and next 5-7 days only where supported
- next confirmation gate and invalidation/risk
- compact LIVE precision with explicit measurable coverage
- contextual BTC/ETH/ETHBTC values only when they explain/test a frozen call or range
- no standalone generic quote dashboard

### PATH
Curated conditional cycle map, not a decorative destiny timeline.
- current phase is visually dominant
- next phase is the most-likely conditional transition, not a promise
- later phases remain explicitly unconfirmed until their gates are met
- every forward transition shows: evidence state, why it is next, confirmation gate, invalidation/delay condition
- ETA appears only when existing canonical evidence supports it; otherwise timing is shown as unconfirmed
- no synthetic probability or website-created forecast

### WHY
Explain in public language:
- why the timeline is measured this way
- why the current phase is current
- 2-4 decisive evidence families
- strongest blocker preventing next phase
- what must happen to unlock next phase
- adaptive evidence-backed ETA in days/weeks when supported
- prior ETA remains immutable for later ETA-accuracy scoring

`WHY` contains two secondary proof layers:

#### Scoreboard
Proof, not marketing.
- latest completed week first
- cycle/regime precision separated from numerical price-range precision and timing/ETA precision
- full defensible CN history with method/era labels
- forecast range -> actual range -> score only where point-in-time evidence supports it
- explicit measurable coverage/denominator
- OPEN/not-yet-matured excluded from denominator
- no hindsight reconstruction
- historical score methods remain locked; show method context instead of silently normalizing
- mark manual era vs automated era
- never manufacture one all-time aggregate across non-comparable scoring eras

#### How it works
Trust layer, not a copyable blueprint.
Explain at a high level:
`DATA -> SPECIALIST ANALYSIS -> EVIDENCE / CHALLENGE -> MASTER MONDAY -> FROZEN CYCLE NAVIGATOR -> LIVE MONITORING -> SCORE & LEARNING`

Public-safe explanation may include:
- weekly autonomous evidence collection by category
- specialist analysis and challenge/reconciliation
- Master Monday synthesis and Cycle Navigator freeze
- immutable forecast-before-outcome discipline
- later scoring and learning
- separate LIVE Handlekompas/tactical observation layer
- fail-closed / abstention behavior when evidence is unavailable

Do not expose private repository paths, credentials, proprietary prompts, exact orchestration recipes, source hashes, hidden thresholds, weights, transformations, complete source mappings, or enough implementation detail to clone the framework.

## Weekly/public coupling
Canonical autonomous evidence -> Master Monday/CN -> immutable weekly package -> website and X publication from the same frozen facts. X is downstream, not a score source. LIVE data is a separate tactical observation layer and may never rewrite weekly forecasts or official scores.

## LIVE semantics
LIVE may update current action/context between weekly issues only from eligible existing canonical outputs.
- provisional precision evaluates immutable current-CN non-alias claims only
- OPEN/not-yet-evaluable claims are excluded from the denominator
- public UI always shows measurable coverage beside provisional precision
- price tracking appears only when the frozen CN contains a numerical range for that horizon
- at forecast maturity, provisional observation holds if the next CN is delayed
- a new CN starts a fresh LIVE observation; only the official completed-week score enters locked history
- LIVE/public presentation has `authority=false`

## Historical recovery gate
Search legacy CN namespaces, forecast ledgers, current delivery namespace, commit/PR history and archived publication evidence before declaring a historical field unavailable. Memory-seeded values are discovery hints only.

Public aggregate history must disclose N and provenance coverage. Approx. 99% provenance confidence is acceptable for recovered history when point-in-time intent is clear, but a missing original forecast must never be guessed from outcomes. Manual publication is not invalid merely because it was manual; scoring-era differences remain visible.

## Public copy firewall
Normal public UX must not expose machine-room labels such as `DEGRADED`, `REPRODUCIBLE`, API/authority jargon, hashes, ingestion gaps, workflow health or internal cohort names. Preserve internal state, translate only the consequence: for example `Range not published this week`, `Waiting for breadth confirmation`, or `Update pending`.

## Review gates
1. PRODUCT/UX: first-time iPhone user understands action, phase, risk and next gate in under 10 seconds; primary navigation has at most three choices.
2. DATA/SCIENCE: same frozen CN package feeds weekly site/X facts; LIVE cannot rewrite; price scoring uses frozen ranges only; historical methods/coverage remain explicit; conditional PATH contains no hidden website inference.
3. ADVERSARIAL/FAILURE: stale/missing/null/partial/delayed rollover, false-green build order, privacy leakage, unsupported ETA/aggregate and mobile layout fail safely.

No merge/deploy until all three pass after the final implementation.