# Historical Altseason Pullback Lab — Round 2 terminal research decision

Status: RESEARCH_ONLY / TERMINAL_DECISION_FOR_CURRENT_PRICE_VOLUME_LANE
Date: 2026-08-22
Authority: no portfolio execution, no production market-rule changes, no threshold/weight/policy-semantic changes.

## Evidence base

This decision records the externally executed Claude Opus 5 Round 2 cross-sectional follow-up performed against the recovered `alt_hourly_panel.csv.gz`.

Verified input facts from the Round 2 package:
- 851,882 per-asset hourly rows
- 35 symbols
- 25,506 distinct hours
- 46 frozen pullback anchors + 45 frozen matched controls = 91 inferential event units
- recovered panel SHA-256: `c55c37aa7038f7cd412267bfb8702ebbaf4eabce8db3a76df244bc25de563118`
- recovered panel reproduces the Round-1 aggregate essentially exactly
- Round 2 QA: 16/16 PASS
- GitHub writes by external research: 0
- paid CFGI calls in Round 2: 0
- FORWARD_TEST promotions/nominations: 0

## Terminal result

The cross-sectional objection to the Round-1 aggregate null is CLOSED for the current price/volume/taker-share tape.

Round 2 found:
- per-asset precursor behaviour: TESTED_NO_EDGE
- leaders vs laggards: TESTED_NO_EDGE
- LOW/MID/HIGH liquidity cohorts: TESTED_NO_EDGE
- cohort-removal robustness: TESTED_NO_EDGE
- per-asset reload behaviour: TESTED_NO_EDGE
- survivorship/delisting: TESTED_FRAGILE
- symbol-removal/universe sensitivity: TESTED_FRAGILE
- cross-era replication under the frozen V0 episode definition: STILL_NOT_TESTABLE

The decisive practical findings are:
1. zero cross-sectional cells survive proper family-wise correction in either full or actionable pre-top windows;
2. zero actionable LEADS appear across 42 tested universes;
3. zero of 11 reload policies and zero of 3 liquidity cohorts beat HOLD;
4. the aggregate null is not a composition artefact;
5. median 97.1% of assets fall during a pullback, showing these episodes are near-total common-factor events;
6. the common market factor becomes highly discriminative after the top while idiosyncratic structure remains weak, explaining why the aggregate was close to a sufficient statistic.

## Research lane decision

Do not spend additional historical research budget on broad searches for new transforms of the same altcoin price/volume/taker-share tape unless a separately pre-registered hypothesis identifies one or a few exact cells before outcomes are inspected.

This is not a claim that modest AUC ~0.60 effects cannot exist. Round 2 explicitly shows that the current 91-event design cannot reliably detect modest effects after wide family-wise search. The terminal decision is narrower: no robust precursor large enough to justify trading/trim/reload was found, and the actionable-window evidence is at or below permutation noise.

The historical benchmark for this lane is therefore:

`HOLD = undefeated baseline under tested constraints`.

No production behaviour changes from this statement alone.

## Round-1 finding disposition after Round 2

- F1: NOT_AFFECTED_BY_ROUND2
- F2 breadth confirms, not leads: UNCHANGED and extended to per-asset/cohort/leader-laggard views
- F3: UNCHANGED
- F4 trim/reload vs HOLD: UNCHANGED_AND_STRENGTHENED
- F5 selection/multiplicity null: UNCHANGED_AND_HARDENED

## New methodology findings

### Persistence criterion defect

The former heuristic `>=3 consecutive pre-top hours at directional AUC >=0.65` is not a calibrated family-wise criterion when features use overlapping rolling windows. Adjacent observations can share 96–99% of their input.

Under random labels, the 700-cell symbol family produced a median longest run of 13 hours and median 42 criterion-meeting cells. Therefore raw consecutive-hour count must not be interpreted as independent confirmation in future research.

### Episode-label era dependence

The current V0 episode definition is not era-neutral because the 0.75-recovery closure can leave modern drawdowns open for months. Round 2 showed that the imbalance is primarily closure-driven, not detection-driven.

A V2-style label candidate — current trigger plus closure on 0.75 recovery OR 336 hours, whichever occurs first — preserved 95.7% of frozen episodes while yielding materially more modern episodes. This is recorded only as `RESEARCH_LABEL_CANDIDATE_ONLY` and is not adopted retroactively.

## Next research capital

Priority shifts from more transformations of the same tape to genuinely new information dimensions, especially:
- open interest
- funding
- order-book depth / imbalance
- stablecoin exchange flows
- cross-venue positioning / basis / flow divergence

Any next programme must preserve no-lookahead, independent event inference, explicit multiplicity budget and prospective/frozen hypotheses before outcome inspection.
