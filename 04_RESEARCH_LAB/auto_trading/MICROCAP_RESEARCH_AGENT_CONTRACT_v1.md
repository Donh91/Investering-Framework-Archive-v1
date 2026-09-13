# MICROCAP RESEARCH AGENT CONTRACT v1

Status: `PREPARED_NOT_ACTIVE`
Owner: Investering Framework Research Lab
Authority: `RESEARCH_ONLY`
Inspired by: `AT-SRC-0005` plus existing Framework governance

## Purpose

Create a reproducible, point-in-time research packet for a crypto asset before any strategy or portfolio layer evaluates it.

This contract is designed for Astra-class research and can be specialized for Robinhood Chain or other chains without changing the core evidence model.

It does **not** create BUY/SELL authority.

## Required input

Every run must freeze:

- chain / network
- token symbol
- canonical contract address
- canonical trading pair(s)
- research timestamp / `decision_at`
- intended research horizon
- requested evidence sources
- explicit unknowns carried into the run

If contract identity, chain identity or primary pool cannot be verified, return `DATA_BLOCKED` rather than guessing.

## Stage 0 — Identity and market object

Verify before interpretation:

- chain and contract address
- token standard
- duplicate/same-ticker contracts
- deploy timestamp where available
- proxy/upgradeability status
- tokenized real-world asset, utility token, meme, LP token or other structure
- canonical pool(s) and quote asset(s)
- whether the asset is transferable and actually tradable at the research timestamp

No narrative work may overwrite identity uncertainty.

## Stage 1 — Executability and liquidity

Measure the market a strategy could actually trade, not the headline price.

Capture where available:

- pool liquidity and concentration
- 24h and shorter-window volume
- pool age
- number of material venues
- spread / quote quality
- estimated price impact at predefined notional sizes
- slippage sensitivity
- buy-side vs sell-side depth asymmetry
- quote-asset quality
- route dependence
- liquidity migration / withdrawal risk

If execution quality cannot support the assumed order size, the asset cannot graduate to strategy testing at that size.

## Stage 2 — Contract, supply and control risk

Record facts separately from interpretation:

- total and circulating supply where reproducible
- mint authority
- pause / freeze / blacklist controls
- transfer restrictions
- tax / fee mechanics
- owner / admin privileges
- proxy upgrade authority
- treasury and protocol-controlled wallets
- holder concentration excluding known pools/treasury where appropriate
- LP ownership / lock / burn state where relevant
- deployer and first-funder relationships
- material contract changes since deployment

Unknown control rights are `UNKNOWN`, not `SAFE`.

## Stage 3 — On-chain behavior

Build a point-in-time behavioral snapshot:

- top-holder changes
- concentration trend
- recurring buyers / sellers
- wallet clusters
- funding-source overlap
- deployer / team-linked behavior when provable
- new-wallet share
- distribution vs accumulation
- bridge / CEX inflow-outflow context where attributable
- wash/self-trading indicators
- unusual transfer patterns
- LP additions/removals

Wallet labels must preserve confidence and provenance. A wallet is not "smart money" because one trade worked.

## Stage 4 — Product, narrative and social evidence

Research with citations:

- actual product / utility
- docs and website claims
- GitHub / development activity where relevant
- dependencies on other protocols or issuers
- tokenomics and value capture
- fee / revenue claims and whether independently verifiable
- roadmap and catalysts
- competitive set
- team / provenance where public
- social propagation
- creator/KOL concentration
- community takeover / CTO dynamics if applicable
- narrative fit and narrative crowding

Separate:

`FACT -> INFERENCE -> HYPOTHESIS`

Do not collapse them into one paragraph.

## Stage 5 — Framework context

Consume existing Investering Framework state rather than building a parallel regime engine.

Relevant context may include:

- broad crypto regime
- BTC / ETH leadership
- risk-on/risk-off state
- alt / meme rotation state
- chain-level activity
- liquidity conditions
- volatility / stress state
- execution-risk regime

The asset-research layer may consume this context. It may not rewrite upstream market state to improve the thesis.

## Stage 6 — Independent falsification

For load-bearing candidates, use two isolated passes over the same frozen evidence:

### Pass A — strongest evidence-backed bull case

Answer:

- What must be true for upside to persist?
- Which evidence is genuinely unusual or improving?
- What catalyst or mechanism can attract marginal demand?
- What would make this asset structurally better than close alternatives?

### Pass B — kill case / adversarial review

Answer independently:

- What is the most likely way the thesis is wrong?
- Which evidence may be vanity, circular or manipulated?
- What control / concentration / liquidity risk can invalidate price discovery?
- Which hidden assumption carries the most downside?
- What new evidence would force immediate rejection?

Neither pass may read the other's reasoning before commit when `BLIND_OPPOSITION` is used.

## Output contract

The internal research packet must include:

1. `identity`
2. `decision_at`
3. `evidence_coverage`
4. `market_executability`
5. `contract_control`
6. `holder_distribution`
7. `wallet_behavior`
8. `product_and_value_capture`
9. `social_and_narrative`
10. `framework_context`
11. `bull_case`
12. `kill_case`
13. `unknowns`
14. `recheck_triggers`
15. `source_refs`
16. `feature_snapshot`

Allowed research statuses:

- `REJECT`
- `WATCH`
- `RESEARCH_QUEUED`
- `DATA_BLOCKED`

This contract does not emit `BUY`, `SELL`, leverage, size or execution instructions.

## No magic score in v1

Do not compress the packet into one composite attractiveness score yet.

Retain separate components for:

- evidence completeness
- executability
- control risk
- holder concentration
- on-chain quality
- product quality
- catalyst quality
- social/narrative quality
- valuation context
- framework fit

A future weighted score is allowed only after prospective evidence shows it improves prediction or triage versus simpler rules.

## Historical learning design

Every accepted research packet should later be joinable to forward outcomes without look-ahead.

Candidate outcome windows:

- 1h
- 4h
- 24h
- 3d
- 7d
- 30d

For each window, preserve at minimum:

- forward return
- maximum favorable excursion
- maximum adverse excursion
- liquidity change
- volume change
- holder concentration change
- whether the original bull thesis remained valid
- whether a kill criterion fired
- whether the asset became untradeable / migrated / rugged

This turns research into a labeled dataset instead of a collection of memorable anecdotes.

## Astra evaluation mission

Astra should compare this structured contract against a generic free-form token-research prompt.

Measure:

- factual completeness
- source coverage
- hallucination rate
- repeated-run reproducibility
- missed critical risk fields
- time/token cost
- ability to predict later failures
- ability to identify differentiated winners without survivorship bias

Promotion criterion:

The structured contract survives only if it demonstrably improves research quality or downstream prediction relative to the simpler baseline.

## Presentation layer

A short public-style bull thesis may be generated only **after** the internal packet is complete.

It must:

- use verified facts and clearly labeled inference
- omit unsupported certainty
- never back-propagate persuasive framing into the internal evidence packet
- never substitute for the kill case

`PERSUASIVE_OUTPUT != RESEARCH_OBJECTIVE`
