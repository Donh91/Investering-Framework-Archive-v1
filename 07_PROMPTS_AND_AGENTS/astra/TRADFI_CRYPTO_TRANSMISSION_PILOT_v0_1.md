# TradFi ↔ Crypto Transmission Pilot v0.1

**Dato:** 2026-09-11  
**Status:** OPERATIONAL_READ_ONLY_PILOT  
**Område:** agent workflow / plugin qualification / institutional transmission research  
**Primary folder:** `07_PROMPTS_AND_AGENTS/astra/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, `research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md`, `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

## 1. Purpose

Qualify a small read-only research workflow that detects and verifies institutional transmission between traditional finance and crypto without creating a new engine, market rule, score, threshold or portfolio authority.

The pilot exists to answer one narrow question:

> Does combining public-equity research, structured market data and existing framework context produce source-backed information that the current crypto-native stack would otherwise miss or discover materially later?

This is a capability qualification workflow, not a trading signal.

## 2. Authority ceiling

```text
MODE = READ_ONLY_RESEARCH
CREATES_TRUTH = NO
FRAMEWORK_STATE_CHANGE = NO
MARKET_RULE_CHANGE = NO
THRESHOLD_CHANGE = NO
PORTFOLIO_ACTION = NO
TRADE_ACTION = NO
CANONICAL_PROMOTION = NO
AUTOMATIC_MERGE = NO
```

The pilot may produce source-backed research observations and evidence-gap notes only.

## 3. Existing-owner rule

This pilot must not create a parallel framework engine.

It routes into existing owners only:

- current Research Lab for falsification and hypothesis review;
- existing API-agent architecture for bounded model work;
- existing prospective ledgers only when a registered test owner explicitly accepts the evidence;
- current source/provenance controls for cited external evidence.

If no existing owner is appropriate, return `NO_EXISTING_OWNER_ROUTE` rather than create one.

## 4. Public data scope

Allowed source families:

1. Public Equity Investing workflows and their cited public sources when available.
2. Data plugin / Financial Datasets public market and SEC data when available.
3. Binance and CoinGecko public market data.
4. Official company IR, SEC filings, exchange announcements and other primary public sources.
5. Current GitHub framework control-plane owners and receipts.

Premium or paid datasets are optional enhancements, never a required dependency for pilot success.

If a paid source is unavailable, mark it unavailable and continue only with valid public sources.

Restricted provider values from `Donh91/secrets` are out of scope for this pilot unless a future authorized owner explicitly binds them under the cross-repository contract.

## 5. Core workflow

The workflow is intentionally small:

```text
DETECT
-> RESEARCH
-> VERIFY
-> COMPARE_WITH_EXISTING_FRAMEWORK
-> CLASSIFY
-> LOG
```

### DETECT

Identify a potentially meaningful TradFi ↔ crypto event, for example:

- institutional investment into crypto infrastructure;
- listed-company BTC/crypto treasury allocation;
- ETF or fund-structure change;
- exchange/broker crypto revenue or product shift;
- stablecoin or tokenization infrastructure adoption;
- miner treasury/selling behavior;
- capital-markets financing linked to crypto exposure;
- material ownership or institutional positioning change.

Detection alone has no decision value.

### RESEARCH

Gather the smallest sufficient source bundle.

Prefer primary sources first. Use secondary sources only for discovery or corroboration.

### VERIFY

For every material claim, record:

```yaml
claim:
source_type: PRIMARY | SECONDARY | STRUCTURED_DATA
source_name:
source_date:
source_ref:
verified: YES | NO | PARTIAL
data_gap:
```

Unsupported claims must not be upgraded by model confidence.

### COMPARE_WITH_EXISTING_FRAMEWORK

Ask whether the observation adds anything beyond existing crypto-native evidence.

Minimum comparison questions:

1. Is this already visible through BTC/ETH price, BTC.D, ETH/BTC, breadth, ETF flows or current Research Lab owners?
2. Does it reveal capital routing, institutional behavior or infrastructure change that those sensors cannot directly observe?
3. Does it contradict an existing framework assumption?
4. Does it merely explain an already-known move after the fact?
5. Would the framework have changed research priority, evidence-gap priority or hypothesis quality if this information had arrived earlier?

### CLASSIFY

Use one primary class:

```text
STRUCTURAL
CAPITAL_ROUTING
CORPORATE_TREASURY
TOKENIZATION_INFRASTRUCTURE
ETF_OR_FUND_STRUCTURE
BROKER_EXCHANGE_ACTIVITY
MINER_SUPPLY_BEHAVIOR
INSTITUTIONAL_POSITIONING
NO_INCREMENTAL_VALUE
INSUFFICIENT_EVIDENCE
```

And one decision-value state:

```text
NO_DECISION_VALUE_YET
RESEARCH_PRIORITY_CHANGE_ONLY
EVIDENCE_GAP_CLOSED
EXISTING_OWNER_SUPPORT
EXISTING_OWNER_CONTRADICTION
REDUNDANT_WITH_CURRENT_STACK
```

Do not emit BUY, SELL, DEPLOY, REDUCE, EXIT or portfolio sizing.

### LOG

Pilot outputs should be compact and reproducible:

```yaml
pilot_id:
observed_at_utc:
event_title:
primary_class:
decision_value_state:
source_bundle:
existing_framework_overlap:
unique_information:
contradiction_found:
missing_data:
recommended_existing_owner:
follow_up_required:
confidence: LOW | MEDIUM | HIGH
authority: READ_ONLY_RESEARCH
```

## 6. Plugin/tool routing

Use the cheapest qualified source path.

```text
Public Equity Investing
= listed-company research workflow, earnings, filings, catalysts, valuation context and ETF/index diligence.

Data / Financial Datasets
= structured company/SEC/market rows when the service is available.

Binance / CoinGecko
= public crypto market context and verification.

OpenAI Developers
= agent design, structured outputs, eval methodology and future SDK implementation guidance.

GitHub
= current framework authority, routing and evidence ownership.
```

Tool unavailability must produce explicit degraded status, never silent substitution.

## 7. Model routing

Do not create a new API task class during the pilot.

Reuse existing research task classes:

```text
Routine extraction / classification -> cheapest qualified existing executor.
Cross-domain synthesis -> existing DEEP_RESEARCH_MANUAL path.
Architecture or difficult orchestration review -> Astra-class model only when current capability routing policy selects it.
```

The pilot does not modify `API_TASK_REGISTRY_v1.json`.

## 8. Incremental-value test

A case counts as useful only if it adds at least one of:

```text
NEW_PRIMARY_SOURCE_FACT
NEW_CAPITAL_ROUTING_FACT
NEW_CONTRADICTION
NEW_EVIDENCE_GAP_CLOSURE
NEW_RESEARCH_PRIORITY
NEW_REPRODUCIBLE_CROSS_ASSET_RELATIONSHIP_CANDIDATE
```

A more eloquent explanation of already-known framework state is `REDUNDANT_WITH_CURRENT_STACK`.

For qualification review, repeated examples inside the same information family must be de-duplicated conservatively. A new source fact is not automatically a new framework information family.

## 9. Frozen pilot review gate

Review after the first 10 eligible cases.

Minimum pass condition:

- at least 3/10 cases add a source-backed incremental item from the list above;
- zero unsupported market-state or portfolio promotions;
- zero restricted-data boundary violations;
- every material claim has reproducible source lineage;
- tool/data unavailability is surfaced explicitly;
- no new engine, score or duplicate owner is created.

Strong pass:

- at least one case changes a Research Lab priority or closes an evidence gap that the current crypto-native stack would not have closed on the same information set.

## 10. Kill / merge criteria

Retire or merge the pilot if any of the following occurs:

1. The first 10 eligible cases produce fewer than 3 incremental source-backed items.
2. The next 5 cases after initial review are all `REDUNDANT_WITH_CURRENT_STACK`.
3. Useful results require paid datasets in more than half of eligible cases, making the public/free route non-viable.
4. The workflow repeatedly reproduces conclusions already generated by an existing Research Lab owner without new source lineage or evidence-gap value.
5. The taxonomy cannot be assigned consistently before outcomes or narratives are known.
6. The pilot attempts to become a market engine, portfolio layer or source of automatic framework promotion.

If it is useful but redundant with an existing owner, merge the workflow language into that owner and retire this standalone pilot.

## 11. First qualification cases

Run the frozen eval set in:

`07_PROMPTS_AND_AGENTS/astra/TRADFI_CRYPTO_TRANSMISSION_EVAL_CASES_v0_1.json`

The first live case should prefer an event with an official primary source and a clear cross-asset/infrastructure linkage.

## 12. Completion definition

Pilot v0.1 is ready for qualification when:

- the mission and frozen eval set are present in the Astra folder;
- a first implementation receipt records the current plugin capability test;
- no code or API task registry change is required;
- the workflow remains read-only and routes to existing owners.

Do not add this pilot to standing Astra mission routing or other canonical registries before the 10-case qualification gate passes. If it passes, promote discoverability by updating the existing Astra onboarding/router owner rather than creating a parallel registry.

## 13. Post-qualification status

The first 10-case run passed the original gate. A subsequent adversarial review then de-duplicated repeated information families and downgraded the headline count from 9/10 source-fact-level incremental cases to 6/10 distinct incremental information families.

Current qualification result:

```text
STRICT_MINIMUM_GATE = PASS
EVIDENCE_CLASS = SOURCE_BACKED_RESEARCH_CONTEXT
RESEARCH_LAB_VERDICT = SHADOW_OBSERVATION
OPERATIONAL_RECOMMENDATION = KEEP_AS_READ_ONLY_RESEARCH_CAPABILITY
MARKET_AUTHORITY = ZERO
PORTFOLIO_AUTHORITY = ZERO
RECURRING_AUTOMATION = NOT_YET_JUSTIFIED
PREMIUM_DATA_PURCHASE = NOT_RECOMMENDED
```

Binding review:

`07_PROMPTS_AND_AGENTS/skill_runs/2026-09-11__tradfi-crypto-transmission-red-team-review__qualification.md`

Future review should occur after the next 10 eligible real events. Stronger claims require prospective outcome evidence, not additional examples of institutional adoption.
