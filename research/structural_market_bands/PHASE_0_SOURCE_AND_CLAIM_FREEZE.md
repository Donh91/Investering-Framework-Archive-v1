# PHASE 0 — SOURCE AND CLAIM FREEZE

Status: COMPLETE
Date: 2026-07-29
Research: SMB FUNCTIONAL REPLICATION v0.1

## 1. First-party sources

1. Alphractal metric page
   - https://app.alphractal.com/cryptos/chart/btc/valuation-models/valuation-models/structural-market-bands

2. Original developer post, Arch Physicist
   - https://x.com/arch_physicist/status/2066482020138508656

3. Alphractal explanatory thread
   - https://x.com/Alphractal/status/2077251871144632496

4. Alphractal launch post
   - https://x.com/Alphractal/status/2077251875280183732

5. Alphractal support-zone post
   - https://x.com/Alphractal/status/2079328599358972415

## 2. Public claims accepted as source facts

The sources publicly state that Structural Market Bands:

- uses 100% on-chain data
- is constructed for UTXO-type blockchains
- uses reliability of lifespan data
- combines short-, medium- and long-term market-cap movements
- outputs dynamic structural support and resistance zones
- should be interpreted through structural potential/counter-pressure rather than conventional automatic support-resistance role reversal
- may be unsuitable or imprecise for UTXO chains with private transactions or unusual mining/transaction structures

## 3. Claims not accepted without validation

The following remain marketing, interpretation or unverified performance claims:

- the model resembles a physical law
- the bands are clearly superior to statistical models
- zone touches provide reliable forward returns
- the formula is unique rather than a transformation of established cost-basis or age-distribution metrics
- support and resistance are causally predictive
- the model generalizes across all Bitcoin regimes

## 4. Known unknowns

The public material does not disclose:

- the mathematical formula
- the definition of lifespan reliability
- the market-cap transformations used
- exact short-, medium- and long-term windows
- whether market cap means ordinary, realized, active or another adjusted capitalization
- weighting between lifespan cohorts
- smoothing method
- zone-width construction
- normalization method
- whether parameters are fixed through history
- point-in-time implementation details
- handling of lost coins, change outputs and self-churn
- entity adjustment
- historical revision policy
- objective performance statistics

## 5. Prohibited inferences

Research must not state that SMB equals any one of the following without evidence:

- Realized Price bands
- MVRV bands
- URPD bands
- CVDD
- Delta Cap
- HODL Waves
- Cointime economics
- a power-law model
- a proprietary machine-learning model

These may only be treated as candidate explanatory families or baselines.

## 6. Primary metric building blocks supported by documentation

Potential proxy components have transparent definitions in established on-chain documentation:

- Realized Cap HODL Waves: economic weight of supply segmented by age
  - https://docs.glassnode.com/further-information/metric-guides/age-distribution/realized-cap-hodl-waves

- HODL Waves: supply age distribution
  - https://docs.glassnode.com/further-information/metric-guides/age-distribution/hodl-waves

- Spent Output Age Bands: age of coins spent in a time window
  - https://docs.glassnode.com/further-information/metric-guides/lifespan/spent-output-age-bands-soab

- URPD: UTXO value grouped by acquisition-price buckets
  - https://docs.glassnode.com/further-information/metric-guides/price-distribution/urpd-utxo-realized-price-distribution

- Realized Price by holding-period cohort
  - https://docs.glassnode.com/basic-api/endpoints/breakdowns

These definitions make functional proxy research plausible, but data licensing and point-in-time availability must be checked in Phase 1.

## 7. Phase 0 conclusion

VERDICT: PASS

Reason:
The public claims are specific enough to define multiple falsifiable proxy families while leaving the proprietary formula explicitly unknown.

Next phase:
Data feasibility, provenance and point-in-time audit.
