# Pons V2 launch-origin matched denominator - DEED follow-up v1

Date: 2026-09-23
Status: HISTORICAL_REPRESENTATION / PREREGISTRATION_READY
Owner: #1087
Prospective credit: 0
Trade authority: none

## Question

Are the DEED launch-origin observations - 2.99% creator/caller initial position and 25 launch-time snipe-tax exemptions - actually discriminative risk evidence, or ordinary Pons mechanics?

The answer must come from a denominator, not DEED's later chart.

## What the framework already knew

The repository already contained an important control before this DEED analysis:

### TAGPAD
- exact CA: 0x1998e567d1ea5aab594250db38522cdbe95bef0c
- Pons V2 LaunchAndBuy
- launch: 2026-09-05T17:00:45Z
- creator/recipient bought ~15M / 1B = ~1.5%
- 3 launch-time snipe-tax exemptions
- creator + 2 of 3 checked exempt wallets later no longer held TAGPAD; third check failed
- first audit ~$22.2k MC, later ~$3.3k, ~-85% after WAIT
- process classification: privileged launch participants appeared to have exited while sell pressure remained.

This is a critical matched negative because it shows:
1. exemptions are not unique to DEED;
2. initial creator LaunchAndBuy is not unique to DEED;
3. a much smaller exemption set can coexist with severe downside.

### FLYBRAIN
Existing repository case verifies:
- exact CA 0x4eb990547bce4a982432ca88cf5fae7eed1a2d35
- Pons V2
- creator 0x6ce4085EfB52a6eBDb7d6989beb8860847f4b42A
- 1B supply
- GOOGL quote asset
- 1% creator tax
- Pons mechanics include launcher/creator-fee recipient opening-tax exemption plus optional additional exemptions.
- public scanner snapshot around six minutes showed a very different early expansion path, followed later by violent distribution.

FLYBRAIN is a matched winner/expansion control but its exact launchAndBuy initial supply % and exemption count are not yet reproduced in the canonical case. Keep UNKNOWN rather than infer.

### DEED
- exact CA 0x5E55f18453545d0D4314C5106a2D8Db934298E95
- launchAndBuy
- initial caller position 29.9M / 1B = 2.99%
- 25 snipe-tax exemptions
- severe later boom/bust
- named-wallet social allegations not fully reproduced.

## Immediate falsification result

The naive hypothesis:
> "Any creator LaunchAndBuy or any snipe-tax exemption is a pump/dump signal"

is already falsified as useful framing because these are native Pons mechanics.

The refined hypothesis is:
> "The **degree and subsequent behavior** of privileged launch access may carry risk information."

Candidate variables:
- initial creator/caller supply %
- exemption count
- exemption count excluding protocol-required creator/fee-recipient identities
- exemption-address pre-public acquisition %
- exemption-address sell-through before/after first public expansion
- common funding/control among exemption recipients
- proceeds convergence
- creator fee destination alignment
- time from launch to broad public participation
- public-vs-exempt executable price/tax asymmetry

## First two fully numeric launch-origin rows

| case | initial creator/caller % | exemption count | later path | interpretation |
|---|---:|---:|---|---|
| TAGPAD | ~1.5% | 3 | ~$22.2k -> ~$3.3k after first WAIT (~-85%) | severe downside with small privileged set |
| DEED | 2.99% | 25 | severe boom/bust, exact magnitude venue-dependent | unusually large exemption set vs TAGPAD, but N=1 comparison |
| FLYBRAIN | UNKNOWN | UNKNOWN | major early expansion then violent distribution | control requiring exact origin replay |

Two numeric rows are **not enough** to infer a threshold, monotonic relation or causal effect.

## Why exemption count alone is likely weak

Pons explicitly supports launcher/creator-fee exemptions and optional additional exemption addresses. Different project/team structures can legitimately create different counts.

Therefore:
- count is descriptive;
- count cannot become a risk score alone;
- large count should trigger provenance enrichment, not automatic rejection;
- the important quantity may be what exempt entities actually do.

A 25-address list whose members never receive/buy meaningful supply may be less dangerous than a 3-address list that accumulates 20% and sells into retail.

## Better unit: privileged economic exposure

Define historical-research fields without weights:

PRIVILEGED_ENTITY_COUNT
PRIVILEGED_SUPPLY_PCT_T0_T5M
PRIVILEGED_NET_BUY_PCT_T0_T5M
PRIVILEGED_FREE_TRANSFER_PCT_PRE_PUBLIC
PRIVILEGED_SELLTHROUGH_PCT_T0_T60M
PRIVILEGED_SELLTHROUGH_PCT_T0_T24H
PRIVILEGED_PROCEEDS_CONVERGENCE_STATE
PRIVILEGED_COMMON_FUNDER_STATE
PUBLIC_EXECUTION_TAX_DISADVANTAGE_T0_T5S
CREATOR_INITIAL_POSITION_PCT
CREATOR_FIRST_SELL_SECONDS
CREATOR_24H_SELLTHROUGH_PCT

UNKNOWN is mandatory where unavailable.

## Matched-denominator sampling contract

Do not hand-pick only famous winners and scams.

Historical representation population:
- exact Pons V2 factory launches;
- fixed contiguous block/time windows where feasible;
- include dead/no-market tokens;
- no minimum social attention;
- no minimum outcome;
- sample identity from factory event before outcome lookup.

Stratification is analysis-only after sampling:
- no/low market formation
- severe downside
- flat/noise
- realizable expansion
- expansion then major distribution

Outcome buckets must be defined from executable market observations, not social labels like scam/gem.

## Minimum historical representation target

Phase H1:
- >=30 exact Pons V2 launches from outcome-blind factory sampling;
- >=2 market regimes/days where feasible;
- reproduce origin fields for every sampled launch or mark UNKNOWN;
- record source/RPC health;
- no threshold fitting.

Phase H2:
- if H1 data completeness is acceptable, expand to >=100 rows before claiming any stable distributional pattern.

The earlier external broad base-rate claim remains external until exact factory/block/event/graduation definitions are reproduced.

## Outcome fields

At frozen horizons where data exists:
- market_eligible
- sellability_state
- liquidity_usd
- executable_mcap_or_fdv_semantics
- MFE at 5m/15m/60m/6h/24h
- MAE at same horizons
- severe_drawdown_after_first_public_eligibility
- realized exit feasibility for a small bounded notional
- graduation state/time

No ATH-only outcome.

## Analyses allowed after H1

Descriptive only:
- distribution of creator initial %
- distribution of exemption count
- correlation between count and privileged economic exposure
- outcome distributions conditional on broad bins chosen before outcome inspection
- missingness/source health
- whether DEED is statistically unusual on launch-origin fields

No production threshold, score, BUY/SELL gate or weight.

## Candidate prospective challenger after H1/H2

Only if historical representation shows nontrivial separation:
Champion:
existing Alpha Lab safety/identity/sellability gates.

Challenger:
Champion + privileged-launch-origin enrichment.

Prospective population:
future Pons V2 launches, frozen at launch before outcomes.

Primary test:
Does origin enrichment reduce severe adverse outcomes / structurally privileged launches among qualified watches while preserving realizable winners?

Kill if:
- features are common defaults with no incremental discrimination;
- false avoidance of realizable winners is material;
- data missingness dominates;
- effect disappears across regime/day;
- only hindsight sell-through variables carry the result;
- outcome leakage is required.

## Critical anti-hindsight separation

T0-available:
- launch caller/deployer
- launch config
- pair token
- creator tax/config where decoded
- initial LaunchAndBuy amount
- exemption set
- supply
- transaction/block time

Post-T0 enrichment:
- exempt-wallet subsequent buys
- transfers
- sell-through
- proceeds
- market outcomes
- KOL wave.

A future model can use only what was available by its decision timestamp. Post-T0 variables may train later time-horizon gates only if prospectively frozen before their own decision.

## Decision

DEED has produced a legitimate new research direction, but not yet a risk signal.

The matched denominator already falsifies the simplistic rule "exemptions = bad". TAGPAD proves severe downside can occur with only 3 exemptions. FLYBRAIN proves a Pons launch can achieve major realizable expansion under the same venue family.

The strongest hypothesis now is **privileged economic exposure and subsequent behavior**, not raw exemption count.

Next executable step is a deterministic historical Pons V2 origin extractor over outcome-blind factory rows. That is a code task and must respect the canonical CODEX_ONLY write boundary. This research packet freezes what that extractor is allowed to measure so Codex does not invent semantics.
