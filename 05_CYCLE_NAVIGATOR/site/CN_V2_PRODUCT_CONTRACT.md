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
NOW / PATH / WHY / SCOREBOARD / HOW IT WORKS

### NOW
Action-first. Use only existing canonical Handlekompas/Cycle Navigator outputs. No independent website analysis.
- current 0-24h posture
- segment map from large caps through microcaps/memes where canonical data exists
- next 1-3 days
- next 5-7 days
- confirmation gate and invalidation/risk
- no standalone generic BTC/ETH quote dashboard

### PATH
Curated cycle map. Current phase, next phase, later phases and conditional path to broad altseason/mania. Future phases are conditional, never decorative destiny.

### WHY
Explain in public language:
- why the timeline is measured this way
- why the current phase is current
- strongest blocker preventing next phase
- what must happen to unlock next phase
- adaptive evidence-backed ETA in days/weeks when supported
- prior ETA must remain immutable for later ETA-accuracy scoring

### SCOREBOARD
Proof, not marketing.
- latest completed week
- rolling precision
- cycle/regime precision separated from price-range precision
- full CN history with method/era labels
- forecast range -> actual range -> score where point-in-time evidence supports it
- OPEN/not-yet-matured excluded from denominator
- no hindsight reconstruction
- historical score methods remain locked; show method context instead of silently normalizing
- mark manual era vs automated era

### HOW IT WORKS
Trust layer, not a copyable blueprint.
Explain at a high level:
- weekly evidence collection
- specialist agents and responsibilities by category, not implementation secrets
- evidence reconciliation
- Master Monday/Cycle Navigator freeze
- immutable forecast and later scoring
- LIVE Handlekompas tactical layer
- data families at category level
- fail-closed / abstention behavior
Do not expose private repository paths, credentials, proprietary prompts, exact agent orchestration recipes, source hashes, hidden thresholds, or enough implementation detail to clone the framework.

## Weekly/public coupling
Canonical autonomous evidence -> Master Monday/CN -> immutable weekly package -> website and X publication from the same frozen facts. X is downstream, not a score source. LIVE data is a separate tactical layer and may never rewrite weekly forecasts or official scores.

## Historical recovery gate
All CNs are assumed to have had price ranges unless exhaustive continuity search disproves recoverability. Search legacy CN namespaces, forecast ledgers, current delivery namespace, commit/PR history and archived publication evidence. Memory-seeded values are discovery hints only.

Public aggregate history must disclose N and provenance coverage. Approx. 99% provenance confidence is acceptable for recovered history, but a missing original forecast must never be guessed from outcomes.

## Review gates
1. PRODUCT/UX: first-time iPhone user understands action, phase, risk and next gate in under 10 seconds.
2. DATA/SCIENCE: same frozen CN package feeds weekly site/X facts; LIVE cannot rewrite; price scoring uses frozen ranges only; historical methods remain explicit.
3. ADVERSARIAL/FAILURE: stale/missing/null/partial/delayed rollover, false-green build order, privacy leakage and mobile layout fail safely.

No merge/deploy until all three pass after the final implementation.