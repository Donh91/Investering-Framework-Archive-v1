# EDGE-001 July Native Predecessor Mechanism Study v1

Status: COMPLETE_DISCOVERY_ONLY
Date: 2026-10-07
Authority: RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY

## Freeze order

The native component matrix was frozen first:
- `JULY_NATIVE_COMPONENT_MATRIX_v1.json`
- commit: `8265562397a2eb8139d15262a29c47abe1f51cd9`
- outcome_attached=false

Only after that freeze were known outcome artifacts opened. This preserves the contract's pre-outcome component extraction requirement.

Both A1 and A2 remain one dependence group. No independent N=2 claim is made.

## C1 — A1 PRESENT versus first resolving

At canonical PRESENT, the native stack contained:
- BTC intraday survival loss below 61.9K, close not confirmed.
- 24h breadth VERY_WEAK.
- CFGI FEAR_PRESSURE.
- taker SELL_SKEW.
- OI not expanding aggressively.
- ETHBTC repair still held.
- ETF evidence was not uniformly bearish: BTC positive print/trend unconfirmed, ETH confirmed.

By first resolving at 20:06Z:
- BTC had reclaimed 61.9K current, close still unconfirmed.
- 1h and 7d breadth were repaired while 24h remained weak.
- taker sell skew faded to mixed.
- ETHBTC 0.0275 still held.

Descriptive primitive signal: escalation was not simply "weak breadth". The strongest native distinction was loss/reclaim of BTC survival structure plus flow pressure, while ETHBTC remained protective. Resolution appeared when structure reclaimed and short/long breadth plus taker flow improved even before 24h breadth fully repaired.

## C2 — A1 PRESENT versus A2 NEAR_PRESENT

A2 at 2026-07-13 05:25Z had genuine deterioration:
- BTC current and two settled hourly closes below 63.3K.
- 24h breadth 29%, 7d breadth 23%.
- BTC and ETH spot taker proxies sell-lean across horizons.

But A2 remained below PRESENT because:
- BTC still held above 61.9K.
- latest daily close remained 63,920.40, above 63.3K.
- ETHBTC repair 0.0275 held.
- OI contracted in BTC and ETH.
- no acute funding stress.
- current ETF confirmation, market-wide CVD and stablecoin persistence were missing.

This is the cleanest native mechanism distinction in the July family: reclaim-quality deterioration + weak breadth + sell flow was insufficient for PRESENT while deeper survival structure and ETHBTC repair remained intact and leverage stress was absent.

## C3 — sensor candidate versus Framework moderation

A2 opening is an explicit moderation example:
- sensor candidate: NEAR_PRESENT
- Framework state: WATCH
- BTC current and completed closes still above 63.3K
- ETHBTC above 0.0275
- new pullback alert: NO
- active trim: NO

The framework therefore already separated sensor deterioration from action authority. This is consistent with the later M6 principle WARNING != SELL, but it is not proof of current-state equivalence.

## Post-freeze known outcome context

A1 canonical anchor:
- BTC 61,784.48 at 2026-07-08 14:03Z.
- accepted 72h low 61,544.56, max additional downside -0.3883%.
- 72h close 64,248.00, +3.9873%.
- research-only validated 7d close 65,171.99, terminal +5.4828%, MFE +6.1383%.

Canonical July close receipt adjudicated:
`market_stress_detection_value=PARTIALLY_SUPPORTED_SHORT_LIVED_STRESS`
and
`tactical_trim_execution_value_24h_72h=NOT_SUPPORTED`.

A2 prospective event later recorded survival held without confirmation, breadth translation failure and contradictory flow; later pullback warnings were ratified without automatic promotion or action. This is context, not an independent outcome validation sample.

## Candidate primitives for prospective ablation

These are nominations only, not validated signals.

### PRIM-TSU-01 STRUCTURE_DEPTH
Question: does survival-gate deterioration add incremental information beyond shallow reclaim deterioration?
Rationale: A1 PRESENT lost 61.9K intraday; A2 NEAR_PRESENT lost 63.3K reclaim quality but held 61.9K.
Prospective ablation: same warning opportunity set, compare shallow reclaim-only versus reclaim + deeper survival deterioration.

### PRIM-TSU-02 BREADTH_PERSISTENCE_NOT_SNAPSHOT
Question: does multi-horizon breadth persistence add value beyond one weak breadth snapshot?
Rationale: A1 resolution occurred while 24h remained weak but 1h/7d repaired; A2 showed violent intraday breadth rebounds that failed to translate into 24h/7d improvement.
Prospective ablation: snapshot breadth versus preregistered persistence/translation representation. Do not fit thresholds from July.

### PRIM-TSU-03 FLOW_CONFIRMATION
Question: does persistent sell-lean flow add incremental value after structure and breadth?
Rationale: sell skew aligned with A1 stress and faded at resolution; A2 deterioration included sell-lean BTC/ETH flow, but structure held.
Prospective ablation must test incremental value, not standalone predictive status.

### PRIM-TSU-04 LEVERAGE_STRESS_MODERATOR
Question: should absence of expanding OI/acute funding stress reduce escalation confidence?
Rationale: A2 explicitly remained below PRESENT partly because OI contracted and funding was not acute. A1 OI also did not expand aggressively, so July alone cannot establish directionality.
Status: LOW_CONFIDENCE_NOMINATION, strongest need for prospective falsification.

### PRIM-TSU-05 ETHBTC_REPAIR_PROTECTIVE_CONTEXT
Question: does intact ETHBTC repair reduce probability that BTC deterioration becomes broad distribution?
Rationale: ETHBTC 0.0275 held throughout A1 and A2. Because it did not vary across the key July contrasts, July cannot establish incremental discrimination.
Status: CONTEXT_CANDIDATE_ONLY, not an edge candidate from this case.

### PRIM-TSU-06 MISSINGNESS_AS_CONFIDENCE_BRAKE
Question: should unavailable ETF/CVD/stablecoin layers constrain confidence/action rather than be treated as neutral?
Rationale: A2 explicitly retained missing layers and no action. This is governance/observability logic, not predictive alpha.
Status: KEEP_AS_FAIL_CLOSED_GOVERNANCE_PRIMITIVE.

## Best scientific next test

Do not combine all six into a composite.

The cheapest useful prospective ablation is hierarchical:
1. base = shallow BTC reclaim deterioration;
2. + deeper structure/survival information;
3. + breadth persistence/translation;
4. + flow confirmation;
5. leverage/ETHBTC only as separately reported moderators;
6. missingness always remains a confidence brake.

Each step must use the same warning opportunity set, legal information clock, outcome contract and costs. A more complex step survives only if it adds incremental decision information over the simpler prior step.

## What July does NOT prove

- no historical population edge;
- no current ELEVATED/HIGH/CONFIRMED mapping;
- no optimal threshold;
- no sell/trim edge;
- no independent sample size above one dependence family;
- no evidence that every weak breadth/flow episode is a tsunami;
- no authority to change Compass, portfolio or M6 thresholds.

## Adjudication

July supports a mechanism hypothesis: deepening price-structure failure appears more discriminating than shallow reclaim loss alone, while breadth persistence and flow are plausible confirmation layers. The same evidence strongly warns against converting stress detection directly into selling.

This is sufficient to nominate prospective ablations, not sufficient to advance EDGE-001 above HYPOTHESIS.

CLAIM_LEVEL=HYPOTHESIS
INFORMATION_EDGE=NOT_ESTABLISHED
ACTION_EDGE=NOT_ESTABLISHED
WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
