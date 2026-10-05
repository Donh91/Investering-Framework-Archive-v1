# M6 Interim Adjudication v3 — owner consolidation before Claude slice 2

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Owner:** ChatGPT 5.6 Sol High  
**Status:** CONTINUE_BOUNDED / AWAIT_CLAUDE_SLICE2  
**Authority:** RESEARCH_ONLY / NO_LIVE_EXIT_RULE / NO_PORTFOLIO_ACTION  
**Framework main at adjudication:** `caaecea68cd7a1ff4057f145546eba9de2fcc9d9`

## Executive decision

M6 remains high-value research, but it must not create a new exit engine.

The evidence now supports a narrower architecture:

1. **Historical-as-was accountability:** Claude RL-010 slice 2.
2. **Historical policy discovery / tail-risk economics:** existing Historical Cycle & Exit Lab (HCEL), not a new SPAR exit policy.
3. **Sequence / lead-time diagnostics:** SPAR remains descriptive.
4. **Natural prospective evidence:** Action Compass typed protection rows, T5 FNP and T6 rotation survival.
5. **Independent adversarial adjudication:** GPT-6.1 Sol only after bounded evidence packets.

No live sell or trim rule is supported.

## Evidence synthesis

### T4: warning is not sell

The July T4 warning is a strong event-level counterexample to an unqualified warning-to-sell mapping.

From BTC 61,784.48:
- post-warning 7d low: 61,544.56, only -0.3883%;
- 7d high: 65,577.00, +6.1383%;
- 7d close: 65,171.99, +5.4828%.

The research reconstruction reproduces both persisted 24h and 72h high/low/close values exactly before extending to 7d.

The staged immediate-trim frontier is monotonic in this recovered-warning episode:
- 10% trim surrenders 0.5483 pp terminal upside to avoid 0.0388 pp adverse excursion;
- 25% trim surrenders 1.3707 pp to avoid 0.0971 pp;
- 50% trim surrenders 2.7414 pp to avoid 0.1942 pp;
- 100% exit surrenders 5.4828 pp to avoid 0.3883 pp.

This is a falsifier for `WARNING => SELL`, not for every confirmation-dependent staged policy.

### SPAR: useful diagnostics, not exit authority

Fresh SPAR work now includes a strict-P3/comparator feasibility replay.

Discovery-only counts:
- strict target events: 15;
- target matured 72h: 14;
- primary ETH-weakness comparator events: 17;
- comparator matured 72h: 17.

Descriptive target-minus-primary 72h:
- BTC median return delta: +0.7330 pp;
- BTC median MAE delta: +0.4418 pp.

This does not demonstrate a bearish incremental edge.

Comparator definitions were not in the original SPAR-v1 preregistration, so the result remains `DISCOVERY_ONLY_NOT_CONFIRMATORY`.

GPT-6.1 Sol pass 2 independently concluded:
`SPAR_NEXT_STEP=REMAIN_DESCRIPTIVE; NO_NEW_INFERENTIAL_IDENTITY_JUSTIFIED_NOW`.

Adjudication:
Do not make SPAR the exit-policy owner.

### Episode power: enough to falsify gross claims, not enough to prove a fine exit frontier

The gap-sensitive census preserves all 20/30/40% thresholds and 7/14/30-day family-gap rules.

At the primary 14-day family rule:

BTC:
- 2020-21 >=20%: 8 families all, 7 no-gap;
- 2020-21 >=30%: 2 all, 1 no-gap;
- 2020-21 >=40%: 1 all, 0 no-gap;
- 2025-26 >=20%: 3 all/no-gap;
- 2025-26 >=30%: 2 all/no-gap;
- 2025-26 >=40%: 1 all/no-gap.

EW alt proxy:
- 2020-21 >=20%: 11 all, 9 no-gap;
- 2020-21 >=30%: 6 all, 5 no-gap;
- 2020-21 >=40%: 4 all/no-gap;
- 2025-26 >=20%: 10 all/no-gap;
- 2025-26 >=30%: 4 all/no-gap;
- 2025-26 >=40%: 2 all/no-gap.

Implication:
There is useful event diversity for coarse falsification of claims such as "this policy always protects" or "warning always means sell".

There is not enough independent terminal-cycle evidence to optimize or validate a complex multi-stage production exit policy.

### Existing HCEL is the correct policy owner

The Sep-27 Historical Cycle & Exit Lab already did the policy-family work M6 would otherwise duplicate.

Evidence label:
`RETROSPECTIVE_FROZEN_POLICY_REPLAY`

At 20 bps/side the E3 cross-family ladder was the most robust policy in that frozen family:
- top median TWR vs HOLD 1.089;
- worst top TWR 0.843;
- control median TWR 0.952;
- median drawdown reduction 11.4 pp;
- median premature-exit cost 3.9%;
- time out of market 12%.

But:
- effective independent macro-cycle N was about 2;
- HOLD won wealth-only at 50 bps/side;
- no policy dominated;
- E3 is discovery evidence, not proven edge.

ChatGPT adjudication on 2026-09-27 already classified E3:
`PROMISING HISTORICAL DISCOVERY / NOT_YET_PROSPECTIVE_TEST_READY`.

The prospective challenger was:
`ACCEPTED_IN_PRINCIPLE / BLOCKED_PENDING_REPAIR_AND_REPRODUCTION`.

## Unfinished HCEL gate

Current search finds no completed HCEL O-1 after Sep-27.

The approved continuation remains:

1. reproduce the original 504-row result hash;
2. add PB-02 with no threshold changes;
3. audit E3 code/spec missing-data parity;
4. explicitly test partial missingness;
5. freeze `POLICY_SPEC_v0_1` before repaired rerun;
6. adjudicate whether ranking materially changes;
7. if clean, run right-truncation invariance and per-family availability/provenance tests;
8. only then consider a research-only prospective shadow emitter.

Known defect:
v0 written missing-data semantics and implementation differ. A stale active family may remain counted when its current input is unavailable.

No threshold tuning is allowed during repair.

## GPT-6.1 Sol pass-2 adjudication

Independent API result:
- `VERDICT=INSUFFICIENT_EVIDENCE`
- `CONTINUE_RESEARCH=YES_BOUNDED`
- `LIVE_EXIT_RULE_SUPPORTED=NO`
- `selected_live_rules=[]`
- T4 = strong event-level counterexample to unqualified warning-as-sell
- minimum frontier must be paired/path-based and include net return, drawdown reduction, upside surrendered, recovered warnings, false exits, missed drawdowns, confirmation delay, re-entry, divergence, costs and knowledge time
- cheapest decisive falsifier = knowledge-time admissibility gate, then a minimal paired economic comparison against HOLD and frozen price-only controls
- no new SPAR inferential identity now

ChatGPT accepts this with one routing modification:
the existing HCEL frozen policy family supplies the nearest candidate paired-policy owner once Claude slice 2 establishes what historical-as-was overlap actually exists.

## Current next-action tree

### Now
Claude RL-010 slice 2:
`AUG_OCT_2026_HISTORICAL_AS_WAS_OVERLAP_JOIN`

It must remain blind to Sol's M6 verdict until its report is written.

### If Claude returns LANE_A_ZERO_USABLE_EPISODES
- close historical-as-was retrospective skill claim as untestable on current archive;
- run HCEL O-1 reproduction/spec-parity repair;
- build prospective lane C from corrected existing owners;
- do not create a new SPAR exit engine.

### If Claude returns LANE_A_ONE_USABLE_EPISODE
- use it as an event-level falsification case only;
- bind it to HOLD / price-only / repaired HCEL comparators;
- do not claim population skill.

### If Claude returns LANE_A_MULTIPLE_USABLE_EPISODES
- validate independence and knowledge time first;
- then run paired path-based economic comparison using frozen policies;
- still no threshold tuning or live promotion.

## Current verdict

`CONTINUE_BOUNDED_RESEARCH`

`LIVE_EXIT_RULE=NO`

`NEW_EXIT_ENGINE=NO`

`SPAR_POLICY_OWNER=NO`

`HCEL_POLICY_OWNER=YES_PENDING_O1_REPAIR`

`CLAUDE_NEXT=SLICE2_HISTORICAL_AS_WAS_OVERLAP_JOIN`

`SOL_NEXT=WAIT_FOR_CLAUDE_SLICE2_OR_HCEL_O1_RESULTS`

No current market conclusion is created by this research adjudication.
