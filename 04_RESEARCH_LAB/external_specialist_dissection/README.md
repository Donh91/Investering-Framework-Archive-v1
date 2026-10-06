# External Specialist Dissection Master Queue v1

Status: ACTIVE_RESEARCH_QUEUE / RESEARCH_ONLY / DEDUP_FIRST / NO_TRADING_AUTHORITY
Canonical owner: 04_RESEARCH_LAB
Established: 2026-10-06
Machine-readable state: QUEUE_V1.json

## Mission

Systematically extract the highest-value research primitives from specialist crypto products, dashboards, analytics services and public protocol implementations without copying products wholesale or treating provider labels as truth.

Canonical method:

`specialist -> niche competence -> primitive hypothesis -> first-party/public evidence -> internal reproduction where possible -> provider/internal challenger -> matched controls -> forward freeze -> outcome -> retain / modify / kill`

Reference success case:

`Ocellus -> Early Buyer Retention / gate-accountability idea -> Pons v2 public contract source -> internal CurveBuy/CurveSell decoder -> live official-RPC proof`

This queue is the canonical cross-repo handoff for future agents. Do not start a new specialist scan without reading this file and QUEUE_V1.json first.

## Selection score

Every lane is ranked on five 0-5 dimensions:

1. DISTINCT_INFORMATION: adds a different information class rather than another vendor for the same metric.
2. REPRODUCIBILITY: can be checked against first-party/public/raw evidence.
3. DECISION_LEVERAGE: can improve false-positive rejection, entry quality, exit quality or pullback protection.
4. CROSS_FRAMEWORK_LEVERAGE: useful beyond one token or one subsystem.
5. DEPENDENCY_EFFICIENCY: useful without making the Framework dependent on an opaque/expensive provider.

Maximum score: 25.

## Priority map

### X0 - DISAGREEMENT_ALPHA_V1
Priority: P0 / TRANSVERSAL
Score: 25/25
Owner: Research Lab method layer
State: NEW_PRIMITIVE_CANDIDATE

Question:
When external specialist labels disagree with internal reproducible evidence, does the disagreement itself predict false positives, hidden risk, or missed edge?

Examples:
- GMGN SMART_MONEY vs internal wallet replay;
- Bubblemaps cluster vs internal funding/behavior evidence;
- GoPlus/Honeypot SAFE vs executable sellability;
- Arkham entity label vs raw provenance;
- Ocellus creator/sellability state vs canonical chain evidence.

Required output:
provider claim + timestamp + internal claim + confidence + disagreement class + later matured outcome.

Rule:
Agreement is not automatically valuable. Disagreement is not automatically alpha. Both need denominator and outcomes.

Terminal states:
SUPPORTED_DISAGREEMENT_SIGNAL / LABEL_ONLY / PROVIDER_SUPERIOR / INTERNAL_SUPERIOR / NO_INCREMENTAL_VALUE.

### S1 - EXECUTABLE_SELLABILITY_TRUTH_V1
Priority: P0
Score: 24/25
Owner: Meme Alpha Lab microstructure + existing execution-quality owners
Targets: GoPlus, Honeypot.is, raw router/contract simulation
State: NEW_PRIMITIVE_CANDIDATE

Why:
Static "honeypot/safe" labels matter less than whether a position can actually be bought and sold at realistic notional after tax, gas, slippage, transfer restrictions and liquidity.

Specialist capabilities observed:
- GoPlus exposes token security and EVM/Solana transaction simulation.
- Honeypot.is exposes honeypot checks, tax/gas and holder/pair context.

Primitive:
`EXECUTABLE_ROUND_TRIP = can_buy x can_sell x realized_cost x size_capacity x state_at_cutoff`

First experiment:
Take a matched sample of risky and ordinary microcaps. Freeze provider outputs and an independent executable route/simulation state. Grade later:
- false SAFE;
- false UNSAFE;
- realized buy/sell friction;
- max executable size;
- liquidity loss after entry;
- whether the safety gate avoided loss or merely blocked winners.

Promotion target:
a reproducible internal sellability/round-trip gate or calibrated external challenger.

Kill:
provider labels add no value beyond direct simulation/raw contract/liquidity checks.

### S2 - WALLET_SKILL_TRUTH_TOURNAMENT_V1
Priority: P0
Score: 23/25
Owner: existing Wallet Alpha Protocol / Wallet Qualification
Targets: GMGN, Nansen, Fomo, Kolscan, Cielo, Lookonchain, raw chain
State: EXTEND_EXISTING

Why:
"Smart money" is economically valuable only if the label survives complete portfolio replay, losers, realized exits, latency and skill decay.

Fresh specialist observation:
GMGN explicitly separates Smart Money from KOL and Sniper, exposes realized/unrealized PnL, wallet history, holdings and exits, and describes Smart Money as statistically profitable over time.

Primitive:
`WALLET_SKILL = complete_history x realized_expectancy x breadth x repeatability x realizable_exit x lead_time x decay`

First experiment:
Freeze provider labels on a bounded cohort. Replay complete wallet outcomes and compare:
- provider SMART_MONEY;
- internal REPEATABLE_EDGE_CANDIDATE;
- matched unlabeled wallets;
- lucky-one-hit controls.

Primary output:
precision/recall of profitable repeatable wallets, lead-time value, edge decay, disagreement outcomes.

Do not create a new wallet engine.

### S3 - ENTITY_ADJUSTED_CLUSTER_AND_BUNDLE_V1
Priority: P0
Score: 23/25
Owner: existing forensics / Distribution Overhang / cluster research
Targets: Bubblemaps, Arkham, Rugcheck-style challengers, raw chain
State: EXTEND_EXISTING

Why:
Nominal holder count is weak. The useful variable is economically independent ownership and coordinated latent supply.

Primitive family:
- ENTITY_ADJUSTED_CONCENTRATION;
- LAUNCH_BUNDLE_SCORE;
- COMMON_FUNDER_DENSITY;
- SYNCHRONIZED_ENTRY_EXIT;
- CLUSTER_PERSISTENCE_ACROSS_LAUNCHES;
- CLUSTER_EXIT_OVERHANG.

Reference control:
shared CEX/bridge/router infrastructure is not common ownership evidence.

First experiment:
reconstruct historical public cluster claims for winner and loser launches, then compare specialist clusters with deterministic funding/timing/transfer evidence.

Highest-value extension:
cluster persistence across later tokens. A recurring coordinated group may be more predictive than one launch's concentration.

### S4 - LAUNCH_TRAJECTORY_AND_RETENTION_V1
Priority: P0
Score: 23/25
Owner: Meme Alpha Lab
Targets: Ocellus as challenger, Pons v2 first-party source
State: ACTIVE_IMPLEMENTATION / REFERENCE_SUCCESS_CASE

Already achieved:
- public Pons v2 source identified;
- CurveBuy/CurveSell semantics reproduced;
- internal decoder built;
- live official-RPC proof succeeded;
- first-N curve-flow retention proxy exists.

Next:
- append-only prospective curve trade tape;
- first-sale latency;
- first-10/50 cohort maturation;
- graduation-threshold/progress reconstruction;
- buyer acceleration and deceleration;
- matched losers;
- direct-transfer/post-graduation reconciliation.

Do not downgrade first-party Pons evidence in favor of Ocellus composite labels.

### S5 - DERIVATIVES_CROWDING_TO_PULLBACK_V1
Priority: P0-P1
Score: 22/25
Owner: existing SPOT_PERP_FLOW_DIVERGENCE + Compass/Pullback research
Targets: CoinGlass, Laevitas, exchange-native data
State: EXTEND_EXISTING

Why:
The existing spot/perp lane asks whether a pump is spot-led or leverage-led. The missing higher-value question is whether leveraged structure predicts a pullback/distribution window before price visibly breaks.

Current specialist surfaces:
- CoinGlass: OI, funding, liquidation events/maps/heatmaps, order book and derivatives flows.
- Laevitas: options OI, IV, skew, GEX, flow and term structure.

Primitive:
`CROWDING_RISK = spot_perp_divergence x delta_OI x funding_basis x liquidation_surface x options_skew/GEX x price_response`

Research target:
detect states such as:
- leverage-led pump;
- spot distribution into rising long OI;
- healthy deleveraging;
- short pressure absorbed by spot;
- liquidation magnet near price;
- options downside demand preceding spot weakness.

Framework use if supported:
Pullback-risk, Distribution-risk, re-entry timing and Compass horizon calibration.

No direct SELL authority.

### S6 - DISTRIBUTION_EGRESS_AND_EXCHANGE_FLOW_V1
Priority: P1
Score: 21/25
Owner: Distribution / Exit Overhang + Wallet Alpha
Targets: Arkham, Nansen challenger, raw chain/explorer
State: EXTEND_EXISTING

Fresh specialist observation:
Arkham's 2026 Intel API exposes entity labels and fund-flow data; its address-intelligence updates became real-time in September 2026.

Primitive:
`LATENT_SUPPLY -> TRANSFER -> CEX/POOL_DESTINATION -> REALIZED_SELLING -> PRICE_ABSORPTION`

Key question:
Does a qualified early winner or cluster moving supply toward known exchange/deposit infrastructure improve exit-risk prediction beyond simple wallet selling?

Controls:
labels are challenger evidence; raw transaction path and destination semantics remain required.

### S7 - ATTENTION_CONVERSION_CURVE_V1
Priority: P1
Score: 20/25
Owner: Narrative/Culture + Promotion Network
Targets: DexScreener, GeckoTerminal, GMGN Callouts, verified social sources when admitted
State: EXTEND_EXISTING

Existing assets:
Alpha already stores thousands of timestamped DexScreener PROFILE/BOOST observations.

Primitive:
`attention_event -> qualified_wallet_response -> unique_buyer_acceleration -> liquidity -> price -> retention`

Separate:
- profile visibility;
- paid/boost events;
- public callouts;
- organic wallet-led discovery.

High-value question:
Do qualified wallets lead public attention, follow it, or distribute into it?

Never equate PROFILE/BOOST with Ocellus dexPaidAt without exact semantics.

### S8 - UNLOCK_SUPPLY_OVERHANG_V1
Priority: P1
Score: 20/25
Owner: existing research/packages/UNLOCK_SUPPLY_OVERHANG_V1
Targets: Tokenomist, CryptoRank, DropsTab, first-party vesting contracts, Arkham/Nansen challengers
State: ALREADY_SPECIFIED

Fresh validation:
Tokenomist currently exposes released percentage, upcoming value and next-7d emission views plus API/CLI surface.

Canonical hypothesis:
`scheduled_supply x recipient_identity x cost_basis x realized_transfer/selling x executable_liquidity x spot/perp_response`

Do not create another unlock package.

### S9 - LAUNCH_MEV_SNIPER_EXECUTION_QUALITY_V1
Priority: P1
Score: 19/25
Owner: Microstructure / forensics shadow
Targets: raw chain/traces first; MEV/transaction-forensics specialists only as challengers
State: NEW_PRIMITIVE_CANDIDATE / SOURCE_AUDIT_REQUIRED

Question:
Can same-block/early-block execution be decomposed into ordinary early demand versus privileged routing, bundling, sandwich/MEV, coordinated sniping or creator-proximate participation?

Primitive family:
- first tradable block share;
- bundle/co-transaction structure;
- priority/bribe behavior where observable;
- repeated actor/cohort recurrence;
- post-entry retention;
- realizable exit.

Rule:
"sniper" is not automatically good or malicious.
The outcome target is execution quality and recurrence, not labels.

### S10 - PROTOCOL_VALUE_CAPTURE_TRUTH_V1
Priority: P2 CONDITIONAL
Score: 17/25
Owner: existing Microcap/FUSE utility research
Targets: DeFiLlama, Token Terminal, Artemis, CryptoFees, first-party protocol data
State: EXTEND_EXISTING / TOKEN_CLASS_CONDITIONAL

Why:
For utility/AI/infrastructure tokens, price narratives should be separated from actual protocol usage and token-holder value capture.

Primitive:
`usage -> fees -> protocol revenue -> holder revenue/burn/buyback -> token supply -> valuation`

Fresh validation:
DeFiLlama currently exposes protocol-level TVL, fees, gross protocol revenue and holder-revenue style fields for supported projects.

Use only where the token thesis actually depends on utility/value capture.
Low value for pure memes.

## Recommended execution order

The queue should not run all lanes simultaneously.

Current bounded order:

1. S1 EXECUTABLE_SELLABILITY_TRUTH_V1
2. S2 WALLET_SKILL_TRUTH_TOURNAMENT_V1
3. S3 ENTITY_ADJUSTED_CLUSTER_AND_BUNDLE_V1
4. X0 DISAGREEMENT_ALPHA_V1 begins as a shared ledger as S1-S3 produce comparable claims
5. Continue S4 LAUNCH_TRAJECTORY_AND_RETENTION_V1
6. S5 DERIVATIVES_CROWDING_TO_PULLBACK_V1
7. S6 DISTRIBUTION_EGRESS_AND_EXCHANGE_FLOW_V1
8. S7 ATTENTION_CONVERSION_CURVE_V1
9. S8 UNLOCK_SUPPLY_OVERHANG_V1
10. S9 LAUNCH_MEV_SNIPER_EXECUTION_QUALITY_V1
11. S10 PROTOCOL_VALUE_CAPTURE_TRUTH_V1 only on qualifying utility-token cases

Reason:
S1-S3 have the strongest combination of false-positive protection, reproducibility and direct microcap value. S5 has exceptional cross-framework value but belongs primarily in mature market/Pullback research rather than the hot-path launch detector.

## Source facts refreshed 2026-10-06

- GMGN publicly describes Smart Money separately from KOL and Sniper and exposes wallet PnL/history/holdings/trade behavior through its current AI/Skills workflow.
- GoPlus documents Token Security plus EVM/Solana transaction simulation APIs.
- Honeypot.is documents honeypot checks including tax/gas and pair/holder resources.
- Arkham's current Intel API exposes entity labels/fund flows, with real-time address-intelligence update feeds announced in September 2026.
- CoinGlass V4 documents real-time liquidation maps/heatmaps plus OI/funding/order-book/flow families; some advanced liquidation surfaces require higher paid API plans.
- Laevitas exposes options OI, IV, skew, GEX, flow and term-structure analytics.
- Tokenomist currently exposes unlock/emission data and API/CLI access.
- DeFiLlama exposes protocol TVL/fees/revenue/value-capture style data for supported protocols.

These are source-capability facts only, not evidence that any provider has predictive alpha.

## Resume contract for future agents

Before doing specialist work:

1. Read this README.
2. Read QUEUE_V1.json.
3. Fresh-read the current owner files named in the selected lane.
4. Search existing issues/PRs for the lane ID.
5. Do not create a duplicate engine/package.
6. Execute only the first OPEN highest-priority lane whose prerequisites are satisfied.
7. Write results back into this directory or the named canonical owner and update QUEUE_V1.json state.
8. If a provider/source fails audit, persist the negative result.
9. If a specialist concept leads to first-party/public reproducible evidence, prefer the internal primitive and retain the provider as challenger.
10. Never promote technical reproduction directly to trading edge.

## Completion definition

This program succeeds if it produces fewer opaque labels and more reproducible primitives that can answer:

- who is actually skilled?
- can the asset actually be exited?
- are holders economically independent?
- is supply moving toward distribution?
- is a pump spot-led or leverage/crowding-led?
- does public attention lead demand or arrive after insiders/qualified wallets?
- does scheduled supply matter after actual absorption?
- does protocol usage create token-holder value?
- which external labels fail often enough to become anti-signals or disagreement signals?

More integrations are not success.

Better falsifiable decisions are success.
