# OnChainMind and Public Historical Data Source Admission Audit

**Date:** 2026-09-01  
**Status:** `SHADOW_ONLY / SOURCE_ADMISSION_AUDIT / NO_MARKET_AUTHORITY`  
**Area:** Research Lab / source discovery / on-chain / expectations / historical data  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Capability manifest:** `06_RESEARCH_LAB/audit_summaries/onchainmind_source_admission_v1/SOURCE_CAPABILITY_MANIFEST.json`  
**Authority:** zero framework-state, threshold, weight, gate, rebuy, rotation, deployment, execution or portfolio authority

## 1. Executive verdict

The main result is not that the framework should ingest OnChainMind.

The main result is that modern source tooling now makes it practical to use sites such as OnChainMind as **sensor-discovery maps**, then route directly to upstream public APIs and official data archives where provenance, history and permissions are cleaner.

Final disposition:

```text
ONCHAINMIND_RESEARCH_CONTEXT: KEEP_SHADOW
ONCHAINMIND_DIRECT_MACHINE_INGESTION: REJECT
ONCHAINMIND_RAW_DATA_ARCHIVE: REJECT
ONCHAINMIND_PROPRIETARY_COMPOSITES: REJECT_NEW_WEIGHT
URPD_COST_BASIS_TOPOLOGY: HIGH_RESEARCH_VALUE / SHADOW_CANDIDATE
INSTITUTIONAL_VS_ORGANIC_CAPITAL_FLOW: RESEARCH_CANDIDATE / EXISTING_ETF_ERA_OWNER_REQUIRED
OLD_COIN_SPENDING_DORMANCY: RESEARCH_CANDIDATE / COMPRESS_TO_ONE_FAMILY
POLYMARKET_EXPECTATIONS: NEW_INFORMATION_CLASS_CANDIDATE / SOURCE_CONTRACT_REQUIRED
COIN_METRICS_COMMUNITY: RESEARCH_OWNER_CANDIDATE
BGEOMETRICS: HIGH_VALUE_RESEARCH_SOURCE_CANDIDATE / RAW_PUBLIC_ARCHIVE_FORBIDDEN
DEFILLAMA: SOURCE_UPGRADE_OR_CROSSCHECK / NOT_NEW_SIGNAL
NEW_ENGINE: NO
NEW_ACTIVE_TEST: NO
LIVE_WEIGHT_CHANGE: NONE
PORTFOLIO_ACTION: NONE
```

The framework should therefore move from `SCRAPE_DASHBOARD_DATA` toward:

```text
DISCOVER_CONCEPT
-> VERIFY_TERMS
-> FIND_UPSTREAM_MACHINE_SOURCE
-> FREEZE_SOURCE_CONTRACT
-> DETERMINISTIC_PARSE
-> TEST_INCREMENTAL_VALUE
-> KEEP / SHADOW / KILL
```

## 2. Why automated OnChainMind extraction was stopped

OnChainMind was initially mapped to determine the scope of its indicator library. The site exposes a broad catalogue spanning on-chain, valuation, holder cohorts, URPD, capital flows, derivatives, ETFs, stablecoins, relative performance, macro, prediction markets and proprietary composite models.

After the Terms of Use were inspected, further automated extraction was stopped.

The current terms explicitly prohibit scraping, crawling, mining or automated extraction of data, charts or content, and state that third-party market/on-chain data displayed on the platform is for viewing inside the platform rather than extraction, storage or redistribution.

Therefore:

```text
OCM_AUTOMATED_SCRAPING: STOPPED
OCM_PREMIUM_OR_RAW_DATA_COPY: NO
OCM_PUBLIC_GITHUB_RAW_ARCHIVE: NO
OCM_ROLE: DISCOVERY_REFERENCE_AND_HUMAN_RESEARCH_CONTEXT
```

The audit preserves only high-level research conclusions derived before the stop. It does not reproduce OCM datasets, premium charts, proprietary formulas or bulk page content.

ChartInspect, referenced by OCM for multiple chart families, was also rejected as a scraping target after its access terms were found to prohibit automated scraping/reverse engineering outside the official licensed interface.

This is a governance improvement, not a loss of capability. Technical ability to scrape does not create permission to scrape.

## 3. OnChainMind concept audit

### 3.1 URPD / cost-basis topology - strongest discovery

URPD is the most differentiated OCM concept for this framework.

The useful question is not another fair-value line. It is:

```text
How much BTC supply is concentrated near spot?
Which holder cohorts own that supply?
Where are dense cost-basis shelves versus liquidity vacuums?
Does topology alter stress propagation, recovery survival or cascade risk?
```

This belongs to the existing `Stress and Structure` family.

Potential compact features, to be defined only from an independent reproducible source, include:

```text
supply_near_spot_share
nearest_dense_cost_basis_distance
nearest_liquidity_vacuum_distance
above_vs_below_spot_supply_asymmetry
cost_basis_concentration_entropy
cohort_share_near_spot
```

None is approved as a live metric by this audit.

The important distinction is:

```text
URPD_AS_TOPOLOGY_CONTEXT: INTERESTING
URPD_AS_BUY_SELL_SIGNAL: NOT_SUPPORTED
URPD_AS_NEW_VOTE: NO
```

### 3.2 Profitability / cost-basis dashboards - useful but highly redundant

MVRV, SOPR, realized/unrealized profit and loss, STH/LTH profitability and realized-price families are useful descriptions of holder stress and recovery.

However, presenting many related indicators side by side must not create pseudo-confirmation.

Disposition:

```text
FAMILY_ROLE: COMPACT_VALIDATION_OR_CHALLENGER
INDEPENDENT_SIGNAL_COUNT: ONE_FAMILY_MAXIMUM
NEW_WEIGHT: ZERO
```

The most promising research use is whether one compact holder-profitability state reduces BTC false negatives or false permissions beyond simple price/trend and the existing BTC state.

### 3.3 Dormancy / old-coin spending - retain as one compressed family

CDD, VDD, ASOL, Dormancy, Liveliness, Vaultedness, coin-years-destroyed and related measures are conceptually related observations of old-coin spending and conviction turnover.

The framework should not admit them as many independent confirmations.

Research question:

> Does one causally normalized old-coin-spending feature add incremental information about distribution, capitulation or recovery survival after price, trend, holder profitability and ETF-era flow context are already known?

Disposition:

```text
RESEARCH_CANDIDATE: YES
FAMILY_COMPRESSION_REQUIRED: YES
LIVE_AUTHORITY: ZERO
```

### 3.4 Institutional versus organic capital flow - interesting ETF-era research

OCM's capital-flow framing separates institutional flows from native/on-chain capital movement and encourages measuring whether price moves are ETF/treasury-led or broadly confirmed by organic realized-cap and holder activity.

This is relevant to existing ETF-era absorption and transmission research.

It does not justify an OCM-specific owner.

Any test should reconstruct the concept from framework-owned or independently licensed sources such as settled ETF flow owners plus reproducible on-chain capital-flow data.

Disposition:

```text
OWNER: EXISTING_ETF_ERA_ABSORPTION_OR_RESEARCH_LAB
NEW_ENGINE: NO
OCM_DATA_REQUIRED: NO
```

### 3.5 Stablecoins - do not reopen a failed predictive claim

OCM contains stablecoin growth, momentum and buying-power constructions.

The framework already has historical evidence that stablecoin information did not justify standalone predictive authority and is better retained as liquidity-availability/activity context.

Therefore OCM stablecoin variants remain replication ideas only.

```text
STABLECOIN_NEW_PREDICTIVE_WEIGHT: REJECT
CONTEXT_OR_CROSSCHECK: ALLOWED
```

### 3.6 Derivatives and options - no Round 3 bypass

OCM exposes funding, OI, liquidations, CVD, order-book and options-derived context.

The framework already owns governed prospective derivatives collection, including restricted-plane evidence and an analysis firewall.

OCM must not be used to bypass that firewall or import interpreted values into public control-plane research.

```text
ROUND3_BYPASS: FORBIDDEN
OCM_DERIVATIVES_ROLE: HUMAN_CONTEXT_ONLY
```

### 3.7 Relative performance / altseason / standard technicals - reject new weight

Relative performance, altseason indices, moving averages, momentum and standard technical indicators are heavily represented elsewhere in the framework and public market data.

The frozen breadth program already found that descriptive participation does not automatically create predictive gate value.

Disposition:

```text
ALTSEASON_OR_BREADTH_NEW_VOTE: REJECT
STANDARD_TECHNICAL_NEW_WEIGHT: REJECT
```

### 3.8 Proprietary composite scores - reject as machine inputs

OCM composite risk/valuation scores are useful visual summaries but create three governance problems:

1. opaque or partially recoverable weights;
2. correlated components counted as apparent confirmation;
3. source changes that the framework cannot independently reproduce.

Disposition:

```text
PROPRIETARY_COMPOSITE_MACHINE_INPUT: REJECT
EXTERNAL_CONTEXT: ALLOWED
```

### 3.9 Prediction markets - genuinely different information class

Prediction-market probabilities are different from price, on-chain, flow, technical and social-sentiment indicators.

They encode market-priced beliefs about explicit future events.

This makes them a credible `EXPECTATIONS_CONTEXT` candidate, especially for:

- macro-event probabilities;
- crypto policy/regulatory outcomes;
- event timing;
- event-resolution calibration;
- expectation shifts before market repricing.

The correct source is the public upstream prediction-market API, not OCM's presentation layer.

No prediction-market probability is a portfolio signal by itself.

## 4. New upstream source discoveries

### 4.1 Coin Metrics Community - strongest long-history open baseline

Official Community API and official GitHub archives were verified.

Key properties:

```text
AUTH: none for Community API
API_ROOT: https://community-api.coinmetrics.io/v4
OFFICIAL_ARCHIVE: https://github.com/coinmetrics/data
ARCHIVE_CADENCE: daily
LICENSE: CC BY-NC 4.0
RATE_LIMIT: 10 requests / 6 seconds / IP
```

The official BTC community CSV contains daily history beginning in 2009 and includes, among other available community fields:

- BTC price/reference rates;
- market cap and MVRV;
- active/balance addresses;
- exchange inflow/outflow and balances where available;
- hash rate;
- issuance;
- supply;
- transaction activity.

It does not provide the full OCM-style URPD/cohort/dormancy stack through the community archive.

Recommendation:

```text
ROLE: LONG_HISTORY_RESEARCH_OWNER_CANDIDATE
COPY_WHOLE_DATASET_INTO_FRAMEWORK_REPO: NO
RETRIEVAL: ON_DEMAND_FROM_OFFICIAL_VERSIONED_ARCHIVE
```

The reason not to copy it is not legal prohibition. The archive is already official, versioned, licensed and updated daily. A second copy in the framework would create staleness and duplicate truth.

### 4.2 BGeometrics - strongest newly discovered rich on-chain research source

BGeometrics exposes a large machine-readable Bitcoin data API computed from its Bitcoin node and explicitly supports AI-agent/MCP use.

Its public documentation lists rich families including:

- MVRV / MVRV Z / STH-MVRV / LTH-MVRV;
- SOPR variants;
- NUPL and realized profit/loss;
- STH/LTH realized prices;
- CDD / VDD / dormancy;
- HODL waves;
- holder cohorts and supply in profit/loss;
- exchange/miner metrics;
- ETF and derivatives data on applicable tiers;
- URPD.

The free plan documents roughly four years of history for many daily endpoints. A live source probe confirmed that `/v1/mvrv` exposes a machine-readable daily history covering the recent multi-year regime.

URPD was also verified as a real API surface. Point-in-time queries succeeded for recent August 2026 dates, while older requested dates returned no rows. Therefore:

```text
URPD_POINT_IN_TIME_QUERY: VERIFIED_FOR_RECENT_DATES
URPD_LONG_HISTORY: NOT_VERIFIED
URPD_RETENTION: SHORT_OR_INCOMPLETE / EXACT START UNKNOWN
```

This is important. It means the framework can begin prospective URPD observation now if a formal source contract is approved, but it must not pretend that a long historical URPD backtest already exists.

BGeometrics terms permit personal/research API use within plan limits but prohibit bulk website scraping and redistribution of underlying API data without the required commercial arrangement.

Therefore:

```text
PUBLIC_RAW_GITHUB_STORAGE: NO
TRANSIENT_RESEARCH_FETCH: ALLOWED_WITHIN_TERMS
PUBLIC_OUTPUT: VALUE_FREE_PROVENANCE + OUR OWN AGGREGATED FINDINGS ONLY
```

BGeometrics is the best newly discovered candidate for a bounded Work/source-adapter task.

### 4.3 Polymarket - strongest genuinely new information class

Official Polymarket documentation confirms public market data can be read without credentials.

Verified surfaces include:

```text
Gamma API: https://gamma-api.polymarket.com
CLOB API: https://clob.polymarket.com
Data API: https://data-api.polymarket.com
GET /prices-history
```

`/prices-history` supports explicit market ID, `startTs`, `endTs`, `interval` including `all`/`max`, and fidelity controls. Public order books, prices and market metadata are also documented.

This makes a deterministic expectation-history study technically feasible.

However, this audit did not resolve a sufficiently explicit redistribution/storage licence for bulk historical Polymarket data.

Disposition:

```text
TECHNICAL_ACCESS: PASS
INCREMENTAL_INFORMATION_CLASS: HIGH
BULK_ARCHIVE_RIGHTS: UNRESOLVED
SOURCE_CONTRACT: REQUIRED_BEFORE_COLLECTION
LIVE_AUTHORITY: ZERO
```

### 4.4 DefiLlama - useful upstream, mostly source-quality rather than new edge

Official public APIs and open adapter repositories make DefiLlama useful for reproducible DeFi/stablecoin/DEX context.

The framework already contains substantial liquidity, stablecoin and DEX reasoning, so the likely value is:

- better source provenance;
- historical gap repair;
- crosschecks;
- direct upstream data rather than dashboard summaries.

It should not automatically reopen old predictive hypotheses.

Disposition:

```text
ROLE: SOURCE_UPGRADE / CROSSCHECK
NEW_SIGNAL: NO
```

### 4.5 Other sources screened

The following were kept below admission threshold for now:

```text
Checkonchain: rich chart research, raw/API rights not resolved -> DISCOVERY_ONLY
Blockchain.com Charts: historical JSON/download potential, exact current owner contract not fully resolved -> HOLD
Newhedge: large API catalogue, access/terms less clean than stronger candidates -> WATCHLIST
CryptoDataDownload: useful downloadable history, limited incremental value versus current owners -> LOW_PRIORITY
ChartInspect: direct scraping rejected by terms -> DISCOVERY_REFERENCE_ONLY
```

## 5. What is genuinely better in 2026

Compared with the older framework era, the capability improvement is material.

We can now routinely:

1. map a research website and classify its information families quickly;
2. inspect terms before ingestion;
3. discover official upstream APIs and GitHub archives;
4. distinguish free/public, licensed, premium and non-redistributable data;
5. verify endpoints live rather than rely on screenshots;
6. discover MCP/agent-native interfaces;
7. bind source versions, API contracts, timestamps and hashes;
8. route private/restricted versus public evidence correctly;
9. build deterministic collectors and validators rather than LLM-reading chart pixels;
10. run incremental-value and falsification tests before adding another sensor.

The practical bottleneck has shifted from `CAN_WE_GET_THE_DATA?` to:

```text
MAY_WE_USE_IT?
IS IT POINT_IN_TIME SAFE?
IS IT REPRODUCIBLE?
DOES IT ADD INFORMATION WE DO NOT ALREADY HAVE?
DOES THE COMPLEXITY PAY FOR ITSELF?
```

This is a major framework advantage.

## 6. Recommended bounded experiments

No new active test is created by this audit. The following are research candidates for a later implementation package.

### E1 - URPD Cost-Basis Topology

Objective:

> Does point-in-time cost-basis topology improve stress/recovery or cascade-risk classification beyond price/trend, holder profitability and existing structure context?

Required fields before test:

```text
source_contract
snapshot_time
settlement_rule
price_bin_definition
supply_bin_definition
coverage_start
missing_snapshot_rule
provider_revision_rule
raw_storage_permission
```

Preferred first mode:

```text
PROSPECTIVE_SHADOW_COLLECTION
```

Do not backfill missing historical snapshots by interpolation.

### E2 - Compact On-Chain Incremental Value

Use a small predefined family, not dozens of signals.

Candidate information axes:

```text
holder_valuation: MVRV or STH-MVRV
realized_behavior: SOPR
old_coin_spending: VDD/normalized dormancy
```

Compare against:

```text
simple BTC price/trend baseline
existing framework BTC state
```

Predeclare horizons such as 7d / 14d / 28d and report return, MAE/MFE, drawdown, opportunity cost, calibration and block-aware uncertainty where applicable.

Kill the family if marginal value disappears after the baseline or is concentrated in one regime.

### E3 - Prediction-Market Expectations Context

Freeze only clearly defined markets with explicit resolution rules and sufficient liquidity.

Research questions:

- are probabilities calibrated at event resolution?
- do probability changes precede or merely mirror BTC/macro repricing?
- is any information incremental to FRED, scheduled-event data and price?
- does liquidity/spread identify unreliable probabilities?

The likely successful role is `EXPECTATIONS_CONTEXT`, not trade execution.

### E4 - Institutional versus Organic Capital Confirmation

Reconstruct with framework-owned sources rather than OCM data.

Compare settled ETF/treasury flow context with realized-cap or holder-flow change to distinguish externally funded price strength from broader native capital confirmation.

This must attach to existing ETF-era absorption research, not become another named engine.

## 7. K17 and deterministic evidence boundary

No numeric predictive conclusion is claimed from LLM extraction of thousands of API rows.

This audit intentionally stops short of a performance backtest because the framework's K17 rule requires deterministic parsing, source coverage validation and point-in-time lineage for numeric evidence.

The correct implementation sequence is:

```text
source contract
-> deterministic fetcher
-> raw/private or transient storage according to licence
-> schema + timestamps + hashes
-> deterministic feature calculation
-> frozen test specification
-> walk-forward outcomes
-> red-team
```

A summarising scrape layer may discover a source. It may not become the numeric evidence engine.

## 8. Work handoff recommendation

A later Work mission would be valuable, but only as a bounded source-adapter/research implementation, not another framework expansion project.

Recommended scope:

```text
A. Coin Metrics Community point-in-time owner for allowed community metrics
B. BGeometrics transient research adapter with no public raw-data persistence
C. URPD prospective snapshot contract and retention audit
D. Polymarket legal/source contract, then expectations research adapter if cleared
E. deterministic compact on-chain incremental-value replay
F. exact kill/keep decision against current owners
```

Do not add BGeometrics to the current fixed MCP pilot queue automatically. The MCP evaluation method says new connections require a demonstrated gap and separate approval/queue decision after the existing approved sequence. The gap is now documented, but the queue itself is unchanged by this audit.

## 9. Archive/data policy from this audit

```text
OCM_RAW_DATA: DO_NOT_ARCHIVE
CHARTINSPECT_RAW_DATA: DO_NOT_ARCHIVE
BGEOMETRICS_RAW_DATA: DO_NOT_ARCHIVE_PUBLICLY
POLYMARKET_BULK_HISTORY: DO_NOT_ARCHIVE_UNTIL_RIGHTS_RESOLVED
COIN_METRICS_COMMUNITY_RAW_COPY: LEGALLY_POSSIBLE_NONCOMMERCIAL_BUT_UNNECESSARY_DUPLICATION
DEFILLAMA_RAW_COPY: NOT_REQUIRED
```

Archive instead:

```text
source identity
official endpoint/docs
licence or legal-use state
history/coverage capability
rate-limit class
point-in-time safety status
storage/redistribution status
framework role
research question
kill criterion
```

The machine-readable capability manifest is the durable implementation of this rule.

## 10. Final decision matrix

```text
ONCHAINMIND:
  value: HIGH_AS_RESEARCH_MAP
  direct_data_owner: NO
  machine_ingestion: REJECT
  ongoing_role: SHADOW_CONTEXT

URPD_COST_BASIS_TOPOLOGY:
  novelty: HIGH
  current_evidence: INSUFFICIENT_FOR_AUTHORITY
  next_role: PROSPECTIVE_SHADOW_CANDIDATE

BGEOMETRICS:
  source_value: HIGH
  historical_depth: STRONG_RECENT_4Y_FOR_MANY_METRICS
  urpd_history: RECENT_POINT_IN_TIME_VERIFIED / LONG_HISTORY_UNRESOLVED
  raw_public_archive: NO
  next_role: BOUNDED_RESEARCH_ADAPTER_CANDIDATE

COIN_METRICS_COMMUNITY:
  source_value: HIGH
  history: LONG
  reproducibility: HIGH
  next_role: RESEARCH_OWNER_CANDIDATE

POLYMARKET:
  novelty: HIGH
  public_access: YES
  history_api: YES
  rights_for_bulk_storage: UNRESOLVED
  next_role: SOURCE_CONTRACT_THEN_EXPECTATIONS_SHADOW

DEFILLAMA:
  novelty: LOW_TO_MEDIUM
  source_quality_value: MEDIUM_TO_HIGH
  next_role: CROSSCHECK_OR_SOURCE_UPGRADE

NEW_ENGINE: NO
NEW_ACTIVE_TEST: NO
CANONICAL_MARKET_RULE_CHANGE: NO
LIVE_WEIGHT_CHANGE: NONE
PORTFOLIO_ACTION: NONE
```

## 11. Durable conclusion

The biggest improvement available today is not scraping more dashboards.

It is the ability to turn a dashboard discovery into a governed upstream data pipeline quickly, while rejecting sources that are legally restricted, opaque, redundant or non-incremental.

OnChainMind is therefore worth retaining as a **research compass**, especially for URPD/cost-basis topology and capital-flow questions.

The data machinery should instead be built, where justified, on upstream sources that are machine-readable, point-in-time safe, contractually usable and capable of surviving the framework's incremental-value test.
