# TradFi ↔ Crypto Transmission Pilot - Red-Team Qualification Review

**Dato:** 2026-09-11  
**Status:** QUALIFICATION_REVIEW / PASS_WITH_DOWNGRADED_INCREMENTAL_COUNT  
**Område:** Research Lab red-team / plugin capability qualification  
**Pilot owner:** `07_PROMPTS_AND_AGENTS/astra/TRADFI_CRYPTO_TRANSMISSION_PILOT_v0_1.md`  
**Qualification run:** `07_PROMPTS_AND_AGENTS/skill_runs/2026-09-11__tradfi-crypto-transmission-qualification-run-01.md`  
**Authority:** READ_ONLY_RESEARCH

## Frozen proposition

Combining public-equity research, public market data and current framework context adds reproducible institutional TradFi ↔ crypto information that the crypto-native stack would otherwise miss or discover materially later, often enough to justify a durable read-only Research Lab capability.

This proposition does **not** claim trading edge, market timing skill, portfolio authority or a new market engine.

## Existing owner and redundancy check

The repository already has:

- Research Lab falsification and source-review machinery;
- API-agent capability routing;
- prospective evidence governance;
- crypto-native market-state owners;
- ETF, stablecoin, rotation, miner and market-structure research context.

Therefore a separate market engine, score, active-test ID or portfolio layer would be duplicate architecture.

The only defensible new unit is a **read-only source-context capability** that discovers and verifies institutional transmission facts and routes them into existing Research Lab owners.

## Primary-source revalidation

The qualification run's strongest facts were rechecked against public primary sources.

Revalidated examples include:

1. Nasdaq / Payward: Nasdaq Ventures agreed to invest $100 million in Payward, with continued work on Nasdaq Equity Tokens and market-surveillance integration.
2. Franklin Templeton / Binance: eligible institutional clients can use Benji-issued tokenized money-market fund shares as off-exchange collateral for Binance trading while assets remain in regulated custody.
3. Franklin Templeton / MoonPay: eligible institutional users can move between supported stablecoins and tokenized money-market fund exposure through an onchain execution workflow.
4. Visa: stablecoin settlement expanded to nine blockchains with a reported $7 billion annualized run rate.
5. Coinbase: Q2 2026 crypto trading-volume market share reached 10.3% while average USDC held in Coinbase products reached $20 billion despite a softer market environment.
6. Robinhood: Q2 2026 total net revenue rose 32% while crypto transaction revenue fell 38%, confirming that HOOD is not a clean one-factor crypto-demand proxy.
7. MARA: 9,270 BTC, about 26% of quarter-end holdings, were loaned or pledged as collateral, with additional bitcoin-backed financing after quarter-end.
8. Strategy: approximately 845,050 BTC were held as of 2026-09-07, alongside separate USD Reserve and USD Cash balances.
9. Strive: the September 8 filing reported a 1,375 BTC purchase, but this is a repeated corporate-treasury pattern rather than a new transmission category.

No restricted provider values were needed for this revalidation.

## Red-team correction to the headline score

The original `9/10 incremental` count is too generous if the unit of value is **distinct framework information family** rather than merely a new primary-source fact.

A stricter de-duplication is required:

```yaml
TCT_001_NASDAQ_PAYWARD: DISTINCT_INCREMENTAL
TCT_002_COINBASE_VENUE_CONSOLIDATION: DISTINCT_INCREMENTAL_SOURCE_CONTEXT
TCT_003_ROBINHOOD_PROXY_IMPURITY: DISTINCT_INCREMENTAL_NEGATIVE_FILTER
TCT_004_STRATEGY_TREASURY: REDUNDANT_EXISTING_ABSORPTION_FAMILY
TCT_005_MARA_COLLATERAL_LENDING: DISTINCT_INCREMENTAL
TCT_006_VISA_STABLECOIN_SETTLEMENT: DISTINCT_INCREMENTAL
TCT_007_BENJI_SCALE: SUPPORTIVE_REDUNDANT_TOKENIZATION_FAMILY
TCT_008_BINANCE_TOKENIZED_MMF_COLLATERAL: STRONG_DISTINCT_INCREMENTAL
TCT_009_MOONPAY_STABLECOIN_MMF_RAIL: SAME_BROAD_INSTITUTIONAL_CAPITAL_MOBILITY_FAMILY_AS_TCT_008
TCT_010_STRIVE_TREASURY: REDUNDANT
```

Conservative gate score:

```yaml
eligible_cases: 10
original_case_level_incremental_count: 9
strict_distinct_incremental_family_count: 6
minimum_required: 3
strict_gate_result: PASS
```

The relevant conclusion therefore survives even after penalizing repeated examples and same-family evidence.

## Decision divergence

### What this capability can change

It can change:

- Research Lab priority;
- which institutional transmission mechanism should be investigated next;
- whether a listed equity is considered a clean or impure crypto proxy;
- whether a source gap is considered closed;
- whether a structural adoption narrative has primary-source evidence;
- which future relationship deserves a separately governed prospective test.

### What it cannot currently change

It cannot change:

- DATA PING market state;
- Cycle Navigator state;
- BTC or alt deployment permission;
- portfolio sizing;
- market thresholds or weights;
- canonical market rules.

No evidence in the current qualification demonstrates forecasting or portfolio decision value.

## Evidence classification

```text
PRIMARY_SOURCE_FACTS: STRONG
SOURCE_LINEAGE: STRONG
RESTRICTED_DATA_BOUNDARY: PASS
MARKET_OUTCOME_ROWS: NONE
PROSPECTIVE_EDGE_ROWS: NONE
PERFORMANCE_EVIDENCE: NONE
TRADING_EDGE: UNPROVEN
```

The correct evidence class is source-backed research context, not outcome evidence.

## Strongest supporting case

The Franklin Templeton / Binance collateral integration is the strongest case because it exposes a direct institutional TradFi collateral → crypto trading-capacity rail that is not represented by price, dominance, breadth or ETF-flow data alone.

The MoonPay integration strengthens the same broader family by showing stablecoin ↔ regulated tokenized money-market-fund movement, but it should not be counted as an entirely independent mechanism for qualification scoring.

## Strongest falsification case

Corporate Bitcoin treasury purchases are easy to overcount.

Strategy and Strive show that the pilot can become a headline collector that repeatedly rediscovers the same BTC-absorption family without changing research priority. If future runs mainly produce this type of repetition, the capability should be merged into existing source monitoring or retired.

## False-positive cost

The main false-positive risk is mistaking institutional infrastructure adoption for live market transmission.

Examples:

- tokenization growth does not equal altseason;
- a Nasdaq/Kraken partnership does not equal immediate capital inflow;
- Coinbase company strength does not equal broad crypto risk-on;
- one miner's treasury behavior does not define a market-wide miner distribution regime.

Therefore no automatic market-state promotion is permitted.

## False-negative cost

Ignoring the capability entirely would miss observable changes in:

- institutional collateral rails;
- regulated tokenized cash-management products;
- stablecoin settlement infrastructure;
- corporate and miner balance-sheet deployment;
- listed-company proxy purity;
- TradFi/crypto market-infrastructure integration.

Those facts can matter for future hypothesis selection even when they do not alter current market state.

## Baseline and comparison

Baseline:

```text
CURRENT_CRYPTO_NATIVE_STACK_PLUS_EXISTING_PUBLIC_WEB_RESEARCH
```

The capability survives only if it repeatedly adds verified institutional behavior or infrastructure facts beyond what that baseline already contains.

It does not need to beat DATA PING as a live market detector because that is not its role.

## Falsifier, promotion and kill criteria

```yaml
falsifier: future eligible cases are mostly repetitions of already-known ETF, treasury, stablecoin or tokenization narratives without a new mechanism, source gap closure or research-priority change
promotion_condition: none to market authority; durable discoverability as a read-only Research Lab capability is justified by the current strict 6/10 distinct-family pass
kill_condition:
  - five consecutive future eligible cases are redundant with existing owners
  - useful operation requires paid data in more than half of cases
  - repeated attempts to convert structural adoption into live market confirmation
  - no future case changes research priority or closes a source gap over a meaningful observation window
observation_window: next 10 future eligible real events after initial qualification
minimum_valid_rows: 10 future event reviews for any stronger claim
baseline: CURRENT_CRYPTO_NATIVE_STACK_PLUS_EXISTING_PUBLIC_WEB_RESEARCH
owner: EXISTING_RESEARCH_LAB
review_date: AFTER_NEXT_10_FUTURE_ELIGIBLE_EVENTS
```

## Authority boundary

```yaml
may_change:
  - research_priority
  - source_context
  - evidence_gap_status
  - proxy_purity_assessment
may_not_change:
  - canonical_market_state
  - thresholds
  - model_weights
  - data_ping_state
  - cycle_navigator_state
  - portfolio_action
portfolio_authority: ZERO
rotation_authority: ZERO
data_ping_authority: ZERO
master_monday_authority: CONTEXT_ONLY_IF_EXISTING_OWNER_CHOSES_TO_CITE_IT
cycle_navigator_authority: ZERO
```

## Verdict

```text
SHADOW_OBSERVATION
```

Operational recommendation:

```text
KEEP_AS_READ_ONLY_RESEARCH_CAPABILITY
DO_NOT_CREATE_NEW_ENGINE
DO_NOT_CREATE_NEW_ACTIVE_TEST_YET
DO_NOT_AUTOMATE_RECURRING_COLLECTION_YET
DO_NOT_BUY_PREMIUM_DATA_YET
ADD_DISCOVERABILITY_TO_EXISTING_ASTRA_ONBOARDING_ROUTER
REVIEW_AFTER_NEXT_10_FUTURE_ELIGIBLE_EVENTS
```

## Confidence

`HIGH` that the capability is relevant as institutional source-context and Research Lab discovery.

`LOW` that it currently has proven forecasting, market-timing or portfolio value.

## Required next action

Make the qualified read-only capability discoverable from the existing Astra onboarding/router, preserving all existing authority ceilings. Do not schedule it, do not create a new engine, and do not add a new API task class.
