# TradFi ↔ Crypto Transmission Pilot - Qualification Run 01

**Dato:** 2026-09-11  
**Status:** QUALIFICATION_RESULT / PASS_CANDIDATE_PENDING_INDEPENDENT_REVIEW  
**Område:** plugin qualification / institutional transmission research  
**Pilot owner:** `07_PROMPTS_AND_AGENTS/astra/TRADFI_CRYPTO_TRANSMISSION_PILOT_v0_1.md`  
**Frozen eval contract:** `07_PROMPTS_AND_AGENTS/astra/TRADFI_CRYPTO_TRANSMISSION_EVAL_CASES_v0_1.json`

## 1. Scope

Run 10 public-source TradFi ↔ crypto cases against the frozen pilot rules.

This run tests source discovery, classification, incremental information value, explicit missingness and authority discipline. It does not test trading performance and does not promote the pilot into standing routing.

## 2. Qualification rules

Minimum pass requires:

- at least 3 of 10 eligible cases add a source-backed incremental item;
- zero unsupported market-state or portfolio promotions;
- zero restricted-data boundary violations;
- complete reproducible public-source lineage for material claims;
- explicit tool/data unavailability handling;
- no new engine, score or duplicate owner.

Strong-pass evidence requires at least one case that changes a Research Lab priority or closes an evidence gap not directly covered by the crypto-native stack.

## 3. Case results

### TCT-001 - Nasdaq ↔ Payward / Kraken tokenized-equities infrastructure

```yaml
source_date: 2026-09-10
primary_class: TOKENIZATION_INFRASTRUCTURE
decision_value_state: RESEARCH_PRIORITY_CHANGE_ONLY
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL
```

Primary source:
`https://ir.nasdaq.com/node/110981`

Verified facts:

- Nasdaq Ventures agreed to invest $100 million in Payward, Kraken's parent.
- The companies are advancing Nasdaq Equity Tokens and a connected Payward/xStocks infrastructure path.
- Payward will adopt Nasdaq surveillance technology across crypto, equities, tokenized equities, futures and options.
- Nasdaq expects NETs in Q2 2027.

Why incremental:

This is not visible from BTC/ETH price, BTC.D, ETH/BTC or breadth alone. It is direct evidence of regulated market infrastructure being connected to crypto-native execution and tokenized-equity rails.

Authority effect:

No live market-state upgrade. Research priority only.

### TCT-002 - Coinbase Q2 2026 operating strength during soft crypto conditions

```yaml
source_date: 2026-07-30
primary_class: BROKER_EXCHANGE_ACTIVITY
decision_value_state: EVIDENCE_GAP_CLOSED
incremental_item: NEW_PRIMARY_SOURCE_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL
```

Primary source:
`https://investor.coinbase.com/news/news-details/2026/Coinbase-Q2-Earnings-Everything-Exchange-Drives-3rd-Consecutive-Quarter-of-Record-Crypto-Trading-Volume-Market-Share-Revenue-Diversification-and-Resilience/default.aspx`

Verified facts:

- Coinbase reported record crypto trading-volume market share of 10.3%.
- Average USDC held in Coinbase products reached a record $20 billion.
- Coinbase explicitly described the quarter as a challenging/soft market environment while market share increased.

Why incremental:

The crypto-native stack sees market structure, but not whether institutional/regulatory infrastructure share is consolidating inside a specific listed venue during weakness. This closes a company/infrastructure evidence gap without implying broad risk-on.

Authority effect:

Company strength is not rotation confirmation.

### TCT-003 - Robinhood Q2 2026 diversification and proxy impurity

```yaml
source_date: 2026-07-29
primary_class: BROKER_EXCHANGE_ACTIVITY
decision_value_state: EVIDENCE_GAP_CLOSED
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL
```

Primary source:
`https://investors.robinhood.com/news-releases/news-release-details/robinhood-reports-second-quarter-2026-results`

Verified facts:

- Total net revenue rose 32% YoY to $1.31 billion.
- Crypto transaction revenue fell 38% YoY to $100 million.
- Equity revenue rose 95% and event-contract revenue exceeded $156 million.
- Robinhood reported Robinhood Chain public mainnet and stock-token expansion as part of its global financial ecosystem.

Why incremental:

The case demonstrates that HOOD is not a clean one-factor crypto-risk proxy. A rising Robinhood business can coexist with falling crypto transaction revenue because the business is increasingly diversified.

Authority effect:

Do not use HOOD strength alone as crypto-demand confirmation.

### TCT-004 - Strategy corporate Bitcoin treasury and capital-market channel

```yaml
source_date: 2026-09-08
primary_class: CORPORATE_TREASURY
decision_value_state: EXISTING_OWNER_SUPPORT
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY_SEC
eligible: YES
result: INCREMENTAL_SUPPORTIVE
```

Primary source:
`https://www.sec.gov/Archives/edgar/data/1050446/000119312526384402/mstr-20260831.htm`

Verified facts:

- Strategy held approximately 845,050 BTC as of 2026-09-07.
- Aggregate acquisition cost was approximately $63.73 billion.
- The filing also reported $5.10 billion USD Reserve and $1.44 billion USD Cash.

Why incremental:

Corporate-treasury demand is a distinct capital-routing channel from ETF flows. The fact supports existing BTC-absorption research but should not be double-counted as independent market confirmation.

Authority effect:

Supportive context only, no alt-rotation inference.

### TCT-005 - MARA miner supply, collateral and lending behavior

```yaml
source_date: 2026-08-06
primary_class: MINER_SUPPLY_BEHAVIOR
decision_value_state: RESEARCH_PRIORITY_CHANGE_ONLY
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL
```

Primary source:
`https://ir.mara.com/sec-filings/all-sec-filings/content/0001507605-26-000020/q226shareholderletter.htm`

Verified facts:

- MARA held 35,577 BTC at Q2 end.
- 9,270 BTC, about 26% of holdings, were loaned or pledged as collateral.
- MARA stated it began selling BTC in 2025 to fund operations and expected opportunistic monetization to continue.
- Post-quarter financing used bitcoin-backed facilities as a non-dilutive funding source.

Why incremental:

This shows miners as active liquidity/collateral actors rather than passive BTC-beta proxies. The crypto-native price stack does not directly identify whether miner reserves are being sold, lent or collateralized for capital projects.

Authority effect:

Research input only, not a standalone distribution signal.

### TCT-006 - Visa stablecoin settlement expansion

```yaml
source_date: 2026-04-29
primary_class: CAPITAL_ROUTING
decision_value_state: RESEARCH_PRIORITY_CHANGE_ONLY
incremental_item: NEW_PRIMARY_SOURCE_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL
```

Primary source:
`https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.22336.html`

Verified facts:

- Visa added five blockchains to its stablecoin-settlement pilot, bringing the total to nine.
- Visa reported a $7 billion annualized stablecoin-settlement run rate, up 50% quarter over quarter.

Why incremental:

This is direct evidence of stablecoins moving into mainstream payment settlement infrastructure. Stablecoin market-cap data alone does not reveal this institutional settlement use.

Authority effect:

Structural deployment evidence, not current altseason or market-direction confirmation.

### TCT-007 - Franklin Templeton BENJI scale and transfer utility

```yaml
source_date: 2026-04-30
primary_class: TOKENIZATION_INFRASTRUCTURE
decision_value_state: EXISTING_OWNER_SUPPORT
incremental_item: NEW_PRIMARY_SOURCE_FACT
lineage: PRIMARY
eligible: YES
result: INCREMENTAL_SUPPORTIVE
```

Primary source:
`https://www.franklintempleton.com/press-releases/news-room/2026/franklin-templeton-stellar-development-foundation-mark-five-years-of-benji-the-first-u.s.-registered-tokenized-money-market-fund`

Verified facts:

- BENJI was described as the first U.S.-registered mutual fund using a public blockchain as its official system of record.
- Franklin reported $1.98 billion across the BENJI suite as of 2026-04-29.
- Cumulative peer-to-peer transfer volume exceeded $211 million as of 2026-03-31.

Why incremental:

Adds primary-source scale and utility evidence to RWA/tokenization research. It supports a structural thesis but is not independently a live crypto transmission signal.

Authority effect:

Existing-owner support only.

### TCT-008 - Franklin Templeton tokenized MMF as Binance off-exchange collateral

```yaml
source_date: 2026-02-11
primary_class: CAPITAL_ROUTING
decision_value_state: NEW_RESEARCH_PRIORITY
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY
eligible: YES
result: STRONG_INCREMENTAL
```

Primary source:
`https://www.franklintempleton.com/press-releases/news-room/2026/franklin-templeton-and-binance-advance-strategic-collaboration-with-institutional-off-exchange-collateral-program`

Verified facts:

- Eligible institutional clients can use Benji-issued tokenized money-market fund shares as off-exchange collateral when trading on Binance.
- The assets remain in regulated off-exchange custody while their value is mirrored into the trading environment.

Why incremental:

This is a direct TradFi collateral → crypto trading-capacity bridge. It is materially different from stablecoin supply, ETF flows or price-based rotation sensors and is a strong candidate for research into institutional deployment/collateral transmission.

Authority effect:

Changes research priority only. No trading signal.

### TCT-009 - Franklin Templeton ↔ MoonPay stablecoin/tokenized MMF institutional rail

```yaml
source_date: 2026-06-02
primary_class: TOKENIZATION_INFRASTRUCTURE
decision_value_state: RESEARCH_PRIORITY_CHANGE_ONLY
incremental_item: NEW_CAPITAL_ROUTING_FACT
lineage: PRIMARY
eligible: YES
result: STRONG_INCREMENTAL
```

Primary source:
`https://www.franklintempleton.com/press-releases/news-room/2026/franklin-templeton-and-moonpay-partner-to-expand-institutional-access-to-tokenized-money-market-funds`

Verified facts:

- Franklin Templeton and MoonPay connected Benji with MoonPay Trade's institutional infrastructure.
- Eligible institutional users can move between supported stablecoins and tokenized money-market fund exposure through an onchain execution workflow.

Why incremental:

This directly maps a stablecoin ↔ regulated yield-bearing fund capital-routing rail. It suggests a measurable future research question around liquidity parking versus deployable institutional collateral/cash-management infrastructure.

Authority effect:

Research-priority candidate only.

### TCT-010 - Strive corporate Bitcoin treasury purchase

```yaml
source_date: 2026-09-08
primary_class: CORPORATE_TREASURY
decision_value_state: REDUNDANT_WITH_CURRENT_STACK
incremental_item: NONE_FOR_PILOT_SCORE
lineage: PRIMARY_SEC
eligible: YES
result: REDUNDANT_CLASS_EXAMPLE
```

Primary source:
`https://www.sec.gov/Archives/edgar/data/1920406/000162828026060809/asst-20260908.htm`

Verified fact:

- Strive reported buying 1,375 BTC from 2026-08-31 through 2026-09-04 at an average price of approximately $79,281 including fees and expenses.

Why not counted as incremental:

The fact itself is new, but after TCT-004 the classification adds no new workflow capability or evidence type. It is deliberately counted as redundancy to prevent the pilot from inflating its score by collecting repeated corporate-treasury examples.

Authority effect:

No new research owner or market-state change.

## 4. Missingness / degraded-path test

The live plugin audit also exercised the frozen paid-data-unavailable case.

Observed:

```text
Financial Datasets company/SEC/fundamental path:
BLOCKED_BY_CREDITS_OR_SERVICE_AVAILABILITY
```

Behavior:

```text
PASS
```

The workflow surfaced the unavailability explicitly and used public primary sources where available. No premium values were fabricated and no absence was interpreted as negative market evidence.

This degraded-path behavior is counted as a guardrail pass, not as an incremental-information case.

## 5. Qualification score

```yaml
eligible_real_cases: 10
incremental_source_backed_cases: 9
redundant_cases: 1
strong_incremental_cases: 2
unsupported_market_or_portfolio_promotions: 0
restricted_data_boundary_violations: 0
material_claim_lineage_rate: 1.0
explicit_unavailability_handling: PASS
new_engine_created: NO
new_score_created: NO
new_active_test_created: NO
new_api_task_class_created: NO
```

Conservative note:

The `9/10` figure measures incremental source/evidence content, not proven decision value. It must not be presented as trading edge, forecast skill or a justification for Core promotion.

## 6. Result

```text
MINIMUM_10_CASE_GATE: PASS_CANDIDATE
STRONG_PASS_CONDITION: PASS_CANDIDATE
STANDING_ROUTING_PROMOTION: NOT_AUTHORIZED_BY_THIS_RUN
CODE_IMPLEMENTATION: NOT_YET_REQUIRED
PAID_DATA_PURCHASE: NOT_RECOMMENDED
```

Why strong-pass candidate:

TCT-008 and TCT-009 expose institutional collateral/cash-management transmission rails that are not directly represented by crypto-native price, dominance, breadth or ETF-flow sensors. They justify a bounded Research Lab priority around institutional collateral/deployment transmission, subject to independent review and existing-owner routing.

## 7. Recommended next action

1. Independent review the classification and 9/10 incremental count, with special focus on avoiding double-counting structural RWA evidence.
2. If review confirms at least the minimum 3/10 threshold, keep the workflow as a read-only Research Lab capability.
3. Only then add discoverability to the existing Astra mission router/onboarding owner.
4. Do not create a new market engine or scheduled collector.
5. Do not buy premium datasets yet.
6. Revisit code automation only after several real future events demonstrate repeated manual work and positive information value.

## 8. Source lineage summary

All 10 scored cases use public primary company/SEC sources except no secondary source is required for scoring.

No restricted provider data was used or copied into the control plane.
