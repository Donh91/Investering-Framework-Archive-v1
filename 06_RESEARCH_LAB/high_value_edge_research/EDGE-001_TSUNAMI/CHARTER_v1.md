# EDGE-001 Tsunami Early Warning and Survival, Research Charter v1

Mission ID: EDGE-001-TSUNAMI
Date frozen: 2026-10-06
Status: ACTIVE / PREREGISTERED / RESULTS_NOT_YET_ADJUDICATED
Authority: RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY

## Core question

Can the Framework detect market deterioration early enough to provide economically useful protection without systematically exiting recoveries and good pumps?

This package extends M6 Distribution Survival. It does not replace M6, HCEL, Compass or any existing owner.

## Two claims, adjudicated separately

### Claim A, INFORMATION EDGE

Before a qualifying adverse episode becomes obvious in price alone, Framework deterioration information provides useful lead versus frozen price-only comparators on the same legally knowable clock.

A may survive even if no action policy is yet economically validated.

### Claim B, ACTION EDGE

A separately preregistered defensive response to that information improves economic survival versus HOLD and frozen simple comparators after costs, false exits, upside surrendered and re-entry friction.

B cannot be inferred from A. WARNING != SELL.

## Null hypotheses

A0: Framework warnings provide no robust economically useful lead beyond simple price-only information.
B0: Any apparent protection benefit is offset by false exits, lost upside, costs, re-entry drag or selection bias.

The research objective is to try to kill A and B, not to rescue them.

## Evidence classes

A_PIT_VERIFIED: value and legal knowledge time are independently bound to an immutable historical artifact.
B_EVENT_TIME_PROXY: historical value is plausible/correct but exact historical knowledge-time is not independently proven.
C_RECONSTRUCTED: computed later from historical raw data under a frozen method.
D_UNUSABLE: provenance, continuity or timing is insufficient for the claim.

Primary strong historical claim must be driven by A_PIT_VERIFIED evidence. B/C may support sensitivity or discovery but cannot silently upgrade the primary claim.

## Episode universe

Do not select only crashes. The registry must seek both adverse and recovery/control families:
- qualifying BTC drawdown families using the already frozen M6 grids 10/15/20 percent;
- qualifying ETH drawdown families using 15/20/30 percent;
- recovered-warning and V-reversal controls;
- strong continuation/pump periods where an over-defensive policy would lose material upside;
- slow deterioration and fast-shock families where admissible.

Primary independence remains the frozen M6 family rule: overlapping peak-to-trough windows are one family, or a later candidate peak less than 14 calendar days after prior family trough remains the same family. Sensitivities 7d and 30d only.

## Frozen comparators

Information-edge comparators:
P0 HOLD / no warning reference.
P1 first hourly close at least 5 percent below running peak, inherited M6 primary price-only comparator.
P2 3 percent running-peak drawdown, inherited M6 sensitivity comparator.
P3 simple trend comparator may be admitted only if its formula and clock are frozen before tournament scoring.

Framework cannot receive a better clock, cleaner source or lower latency than comparators.

## Framework states

Primary warning identity remains pullback_risk_state in ELEVATED, HIGH, CONFIRMED.
BUILDING is watch/control only.
NORMAL is non-warning.
UNAVAILABLE or degraded is non-assessable, never bearish evidence.

Historical predecessor signals may only be mapped into current semantic states if a separate provenance mapping is frozen before outcome scoring. Otherwise preserve their native historical identity.

## Lead-time measurements

For every independent episode family measure where admissible:
- first Framework watch time;
- first primary warning time;
- first price-only comparator time;
- qualifying drawdown threshold-cross time;
- trough time;
- Framework lead versus price-only;
- Framework lead versus threshold crossing;
- no-warning false negative;
- warning recovery / false alarm control.

A positive lead is not sufficient for edge. It must survive independence, provenance and false-positive controls.

## Economic tournament

No optimized live action is authorized. Candidate action mappings must be separately byte-frozen before their results are scored.

Every action candidate must use identical opportunity set, execution clock, fees/slippage, fill assumptions and outcome tape versus its comparator.

Minimum economic vector:
- net terminal wealth versus HOLD;
- net terminal wealth versus frozen price-only comparator;
- max drawdown and drawdown avoided;
- upside surrendered;
- MAE/MFE;
- false-exit cost;
- confirmation delay;
- time out of market;
- re-entry time and price;
- re-entry drag or benefit;
- turnover and costs;
- peak giveback;
- tail-loss/CVaR style metric when sample geometry supports it.

Do not collapse the vector into an optimized scalar score in v1.

## Existing negative control

PULLBACK_EDGE_20260708_01 is a mandatory recovered-warning control. Existing frozen reconstruction shows about -0.3883 percent 7d adverse excursion versus +6.1383 percent MFE and +5.4828 percent terminal BTC return. It is adverse evidence against WARNING=>SELL and must remain in the tournament.

## Anti-overfitting rules

- no threshold search after viewing tournament outcomes;
- no best-cell cherry-pick;
- repeated warnings inside one family do not inflate N;
- parameter sensitivity must be reported as a surface, not only the winner;
- use purge/embargo or clustered uncertainty when dependency geometry requires it;
- preserve all failed and method-invalid variants;
- PBO/DSR/CPCV only when trial/sample geometry makes them meaningful;
- no latest-vintage data may impersonate historical knowledge-time.

## Claim ladder gates

HISTORICAL_CANDIDATE_EDGE: at least one falsifiable historical advantage survives basic PIT/baseline/negative-control checks.
ROBUST_HISTORICAL_EDGE: advantage survives appropriate independent families, simple baselines, false-positive controls, costs and sensitivity without material unresolved leakage.
PROSPECTIVELY_SUPPORTED_EDGE: preregistered future M6 observations support the same mechanism out of sample.
DOCUMENTED_FRAMEWORK_EDGE: robust historical plus prospective support, independent adversarial review, and no unresolved material methodological objection for the claimed scope.

No minimum N is invented here. Statistical language must be bounded by actual independent-family count and uncertainty. Tiny N cannot receive population-level language.

## Claude Bridge role

Claude is an independent adversarial reviewer, not a co-optimizer.

Pre-result audit must attack: episode selection, provenance/knowledge time, comparator fairness, leakage, independence, action mapping, costs/re-entry, and whether the proposed claim can actually be falsified.

Post-result audit must attempt to explain away any apparent edge with simpler baselines, timing advantages, dependence, selection effects or implementation artifacts.

Claude must not be told to make the result positive and must not design a replacement live policy.

## Required phases

T0 charter and governance freeze.
T1 data archaeology and provenance matrix.
T2 immutable episode/control registry.
T3 historical-as-was information-edge tournament.
T4 frozen action-policy economic tournament, only after T3.
T5 robustness and falsification battery.
T6 independent Claude post-result audit.
T7 ChatGPT final adjudication.
T8 ongoing prospective M6 confirmation.

## Immediate kill/defer conditions

Defer or weaken the claim if historical knowledge-time cannot be established, simple price-only baselines explain the result, false positives erase protection value, independent N is too small for claimed scope, or action economics require post-hoc tuning.

## Current authority

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
PORTFOLIO_EXECUTION=FALSE
CLAIM_LEVEL=HYPOTHESIS