# Endgame Capital Preservation Priority v1

**Date:** 2026-09-04  
**Status:** ACTIVE_RESEARCH_PRIORITY / NON_CANONICAL  
**Authority:** ZERO_PORTFOLIO_EXECUTION / ZERO_THRESHOLD_CHANGE / ZERO_MARKET_RULE_CHANGE  
**Extends:** `research/framework_evolution_learning/2026-08-29__cycle-compass-exit-distribution-research-program-v1.md`

## Mission

Treat late-cycle exit timing as a first-class framework objective because the highest-cost failure is asymmetric:

1. **Premature exit:** de-risking during the final parabolic phase and sacrificing material remaining upside.
2. **Late exit:** mistaking distribution/regime break for a normal pullback and giving back a large share of cycle gains.

The framework must therefore learn to approach exit in **graduated, reversible confidence stages**, while preserving a fail-safe path to decisive capital protection when deterioration becomes sufficiently confirmed.

This document does **not** activate a new exit ladder, sell rule, threshold, weight or portfolio action. The native E0-E7 Exit Ladder remains `OWNER_BLOCKED` until a complete prospective owner, producer, validator and multi-horizon lifecycle are frozen.

## Endgame objective

The target is not an exact top date. The target is to improve the probability that the framework can answer, prospectively:

- Are we still in healthy parabolic continuation?
- Is late-cycle risk merely rising, or is distribution becoming persistent?
- How much upside is plausibly still being left on the table if we act now?
- How much downside risk is being accepted if we wait for one more confirmation?
- Which evidence would **cancel** the warning and restore a more offensive state?
- When has the balance shifted far enough that capital preservation should dominate remaining upside capture?

## Research-only staged vocabulary

Use the following as **descriptive research states only** until governance explicitly promotes a native owner contract. They are not a substitute for canonical Action Compass phases/warnings and must not be emitted as portfolio authority.

- `R0_NO_ENDGAME_EVIDENCE` — normal bullish/rotational behavior; no specific late-cycle concern.
- `R1_ENDGAME_WATCH` — one or more late-cycle conditions are notable, but evidence is weak, isolated or non-persistent.
- `R2_ENDGAME_CAUTION` — multiple families deteriorate or euphoria/extension rises enough to justify close monitoring; warning remains readily reversible.
- `R3_DISTRIBUTION_CANDIDATE` — persistent deterioration beneath headline strength is plausible and survives at least one meaningful countercheck; false-exit risk must still be measured explicitly.
- `R4_EXIT_CONFIRMATION_PENDING` — evidence is broad, persistent and increasingly hard to explain as ordinary deleveraging/rotation; the remaining-upside versus avoided-drawdown trade-off becomes the primary research question.
- `R5_EXIT_REGIME_CONFIRMED` — research conclusion that the evidence package is consistent with a genuine regime break rather than a routine pullback. This state has **zero execution authority** until separately ratified by governance.
- `RESET_INVALIDATED` — any warning/candidate state may revert when re-acceleration, renewed breadth/leadership/liquidity or other frozen falsifiers invalidate the prior deterioration thesis.

No level-skipping assumptions are permitted. Repeated observations from overlapping windows are not independent confirmation by default.

## Confidence design

Every endgame observation should separate:

- **state confidence** — confidence that the descriptive late-cycle state is correctly classified;
- **action confidence** — confidence that acting now would improve terminal capital outcome versus waiting;
- **data confidence** — source freshness, continuity, provenance and measurement validity;
- **reversal confidence** — evidence that the warning is being invalidated/re-accelerated.

The framework must not collapse these into one number until calibration supports doing so.

## Required prospective learning

For every material warning/candidate observation, freeze the evidence available at that timestamp and later score:

### False-exit cost
- maximum favorable excursion after the warning at 24h, 72h, 7d, 14d and 30d where data permit;
- large-cap / mid-cap / small-cap / microcap opportunity cost where comparable universes exist;
- whether the warning was later invalidated and by which evidence family;
- whether a staged reduction would have dominated a full exit.

### Late-exit cost
- subsequent drawdown from the warning observation over the same frozen horizons;
- drawdown avoided by hypothetical staged actions, without retroactively selecting the best action;
- delay introduced by persistence/cross-confirmation requirements;
- whether the extra confirmation materially reduced false positives.

### Sequence learning
Track the order and persistence of evidence families, especially:
- breadth decay beneath strong headline price;
- relative leadership failure/recovery across BTC, ETH and broad alts;
- ETH/BTC persistence versus one-off crosses;
- BTC dominance and deployment/rotation context;
- leverage, funding, OI, liquidations and deleveraging quality;
- sentiment/CFGI trajectory rather than one extreme reading;
- stablecoin/liquidity deployment versus mere supply;
- ETF/absorption context;
- holder/cycle context as corroboration, never a standalone exit trigger;
- volatility/options stress where measurement quality is adequate.

## Mandatory falsification questions

Every late-cycle research package must answer both sides:

1. What is the strongest case that the framework is **too bearish too early**?
2. What is the strongest case that the framework is **recognising real deterioration too late**?
3. Which current observations are correlated duplicates rather than independent information?
4. What evidence would re-accelerate/revert the warning?
5. What observation would upgrade the warning by one stage?
6. What evidence is missing or too stale to justify stronger confidence?

## Integration with current framework

Reuse existing owners and contracts rather than create a competing market engine:

- Action Compass canonical phase/warning vocabulary remains authoritative for visible cycle language.
- Daily Director remains descriptive/shadow and must challenge premature bearishness versus delayed deterioration.
- T5 / FNP_CUMULATIVE remains the natural opportunity-cost accountability lane when a real frozen action divergence exists.
- T6 / ROTATION_SURVIVAL_FORWARD remains the natural survival/persistence research lane where its provenance contract is valid.
- Action Compass exit-warning calibration remains descriptive only.
- Master Monday should treat Endgame as a standing calibration question once sufficient prospective evidence exists.
- Monthly AI Learning Council may review matured endgame evidence, but cannot autonomously change canonical rules.

## Guardrails

- No magic-top indicator.
- No exact top-date claims.
- No hindsight-created historical rows represented as prospective evidence.
- No automatic threshold fitting on the same cycle used to evaluate the threshold.
- No automatic portfolio execution.
- No single-family exit trigger.
- No treating parabolic strength itself as distribution.
- No treating a normal leverage reset as a regime break without persistence/cross-family evidence.
- No suppression of a warning merely because price subsequently rises for a short interval; classification quality and action quality must be scored separately.

## Success criterion

Endgame research is successful when the framework can increasingly distinguish:

`PARABOLIC CONTINUATION -> WATCH -> CAUTION -> DISTRIBUTION CANDIDATE -> EXIT CONFIRMATION -> EXIT REGIME`

while also being able to move backward when evidence invalidates the warning.

The practical optimization target is **not maximum top-ticking precision**. It is maximizing retained cycle wealth by minimizing the combined cost of premature exit and delayed exit under prospective, reproducible evidence.