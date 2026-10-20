# S7 - Attention Conversion Curve v1

Status: IMPLEMENTATION_READY / RESEARCH_ONLY / EXTEND_EXISTING
Priority: P1
Master issue: #1512
Owner: Meme Alpha Lab Narrative/Culture + Promotion Network

## Purpose

Measure whether public attention events precede qualified demand, merely follow an existing move, or coincide with distribution.

Do not create a new social engine.

## Existing prospective source

Meme Alpha v4 already records delta-encoded ephemeral observations:
- DexScreener BOOST
- DexScreener PROFILE
- GeckoTerminal TREND / SOL_TREND

These are machine-observation timestamps.

They are NOT automatically:
- exact event creation timestamps;
- DexScreener paid-profile approval timestamps;
- verified KOL call timestamps;
- proof of organic attention.

## Event classes

- DEX_PROFILE_FIRST_OBSERVED
- DEX_BOOST_FIRST_OBSERVED
- DEX_BOOST_CHANGE_OBSERVED
- GECKOTERMINAL_TREND_FIRST_OBSERVED
- GECKOTERMINAL_TREND_CHANGE_OBSERVED
- VERIFIED_SOCIAL_POST
- PAID_PROFILE_VERIFIED

The first implementation supports only the first five from existing v4 data.

PAID_PROFILE_VERIFIED remains a separate future semantic and must not be inferred from PROFILE or BOOST.

## Canonical freeze

For each chain + token + event class preserve:
- event_id;
- chain;
- token address;
- first_observed_at_utc;
- source;
- raw item_type;
- source state hash;
- source fields as observed;
- observation_semantics;
- provenance path.

Subsequent changed BOOST/TREND observations remain distinct change rows.

## Research joins

Later join attention events to existing owners:
- launch/birth tape;
- Pons curve-flow and early-buyer retention;
- Wallet Qualification;
- Promotion Network chronology;
- Distribution / Exit Overhang;
- S6 supported egress;
- market/liquidity outcomes.

## Core derived questions

1. Were qualified wallets present before first public attention?
2. Did unique/economically independent buying accelerate after attention?
3. Did liquidity improve or deteriorate after attention?
4. Did early/qualified wallets distribute into the attention event?
5. Does attention convert to durable holders or only transient churn?
6. Does BOOST intensity/change add information beyond already-rising price/volume?

## Candidate conversion states

Do not emit these until joined evidence exists:
- WALLET_LED_PRE_ATTENTION
- ATTENTION_LED_CONVERSION
- ATTENTION_WITHOUT_CONVERSION
- DISTRIBUTION_INTO_ATTENTION
- LATE_ATTENTION_AFTER_MOVE
- DATA_INSUFFICIENT

The first build creates event truth only.

## Controls

- same chain/token age;
- liquidity band;
- pre-event momentum;
- prior visibility state;
- boost/profile presence;
- broad meme regime.

Matched non-attention tokens are required before predictive claims.

## Negative controls

- PROFILE is not PAID_PROFILE.
- BOOST is not proof of organic interest.
- observed_at is first machine observation, not exact upstream activation time.
- social links embedded in a profile are not verified post timestamps.
- repeated identical state is not a new event because source is delta-encoded.
- a later profile description change must not rewrite first-observed content.
- attention after a price move cannot be credited with discovering the move.
- provider popularity rank is not causal evidence.

## First implementation

1. deterministic extractor over existing ephemeral v4 CSVs;
2. first-observed event ledger + change-event ledger;
3. exact chain/token/event identity;
4. fixture tests proving PROFILE != PAID_PROFILE and observed_at != upstream creation time;
5. no threshold, score, alert or BUY/SELL output.

## Promotion

Possible later conclusions:
- ATTENTION_CONVERSION_INCREMENTAL_VALUE_SUPPORTED
- WALLET_LEAD_MORE_INFORMATIVE
- ATTENTION_LAGGING_ONLY
- BOOST_CHANGE_USEFUL_NOT_PROFILE
- NO_INCREMENTAL_VALUE
- INSUFFICIENT_EVIDENCE

## Authority

RESEARCH_ONLY.
No candidate promotion.
No alert authority.
No portfolio action.
No auto execution.
