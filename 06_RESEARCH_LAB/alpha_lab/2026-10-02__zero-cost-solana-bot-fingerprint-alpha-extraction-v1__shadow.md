# Zero-Cost Solana Bot Fingerprint Alpha Extraction v1

Date: 2026-10-02
Status: SHADOW_RESEARCH / ZERO_COST_OPEN_SOURCE
Owners: #1087 / #1134
Authority: RESEARCH_ONLY
Trade authority: NONE
New scanner: NO
Paid provider dependency: FORBIDDEN

## Owner constraint

The owner has explicitly ruled out paid data subscriptions/API dependencies for this research lane.

External services such as StalkChain, CabalSpy, MadeOnSol, Nansen, Birdeye and similar providers may be used only as:
- public methodology sources;
- free/open discovery surfaces;
- falsification challengers where access is genuinely zero-cost;
- inspiration for independently reproducible measurements.

The target state is:

`PUBLIC CHAIN + OPEN SOURCE + FRAMEWORK LOGIC`

not vendor dependence.

## New primary source

Paper:
**Demystifying Solana Bots: From GitHub Blueprints to On-Chain Fingerprints**
arXiv: 2607.28424v2
Accepted at ASE 2026.

Replication package:
`https://doi.org/10.5281/zenodo.21359451`

Public package:
`SolanaBotDemystifyPublic.zip`

The paper reports:
- 586 public Solana bot repositories;
- 200 bot-associated Solana addresses;
- 44,118,825 on-chain transactions;
- an additional February 2026 validation window;
- replication artifacts for RQ1/RQ2/RQ3.

The public Zenodo package exposes RQ3 analysis code and data including:
- `clustering.py`;
- `assign_validation_clusters.py`;
- transaction frequency / gas / tip / traded-token data;
- cluster outputs;
- validation-window datasets;
- transfer-recipient analysis;
- DEX interaction analysis.

## What the paper actually proves

The paper uses five address-level features for behavioral clustering:

1. transaction frequency;
2. transaction volume;
3. transaction success rate;
4. transaction fee;
5. asset diversity.

It then characterizes resulting clusters using:
- venue/program usage;
- traded-token profile;
- transfer-outflow recipients;
- Jito-tip concentration;
- economic behavior / profit distributions.

HDBSCAN produced:
- Cluster 0: 33 addresses;
- Cluster 1: 11;
- Cluster 2: 12;
- Cluster 3: 102;
- noise: 42;
- silhouette score: 0.6588.

Validation:
- 5-nearest-neighbor projection into the frozen baseline cluster space;
- all 100 Axiom validation addresses mapped to Cluster 3;
- SolanaMevBot validation addresses: 41 C0, 4 C1, 2 C2, 20 C3, 33 noise.

Temporal lesson:
- venue/program usage was the most stable behavioral dimension;
- transfer-outflow recipient structure was next;
- exact traded-token identity was substantially less stable.

## Critical scope correction

The paper DOES NOT establish that the five-feature fingerprint uniquely identifies:
- one human operator;
- one software repository;
- one bot implementation;
- the same actor after wallet rotation.

Therefore Alpha Lab must NOT claim:

`same behavioral cluster = same operator`.

The paper supports a weaker and useful statement:

`on-chain execution behavior can preserve stable category/service-like structure across time`.

Operator/software lineage is a NEW Alpha Lab hypothesis and requires stronger evidence.

## New Alpha Lab hypothesis

### H1 — EXECUTION_FINGERPRINT_AUGMENTS_ENTITY_RESOLUTION

A rotating wallet may preserve enough execution behavior to improve entity linkage when combined with independent evidence.

Candidate evidence families:

### Paper-backed stable candidates
- venue/program distribution;
- transfer-outflow recipient distribution;
- submission intensity;
- success-rate profile;
- fee distribution;
- asset diversity;
- pivot-asset usage.

### Alpha-Lab-specific challenger fields
These are hypotheses, NOT paper conclusions:
- fee payer reuse;
- ATA/account-creation payer reuse;
- Address Lookup Table reuse;
- normalized instruction/program sequence hash;
- Compute Budget parameter profile;
- priority-fee percentile;
- Jito-tip percentile;
- order-size quantization;
- launch-relative latency distribution;
- repeated route structure;
- post-buy gather/sell destination recurrence.

## New zero-cost alpha paths

### A. BOT_FINGERPRINT_LINEAGE
Use execution behavior only as a supporting edge in the existing entity graph.

Never:
`fingerprint similarity -> SAME_ENTITY`.

Allowed:
`fingerprint similarity + independent funding/control/recipient evidence -> OPERATOR_LINK_SUPPORT`.

### B. TRUE_ENTITY_INDEPENDENCE
Before counting wallet convergence, challenge apparent independence with:
- funding root;
- shared fee payer;
- shared account-creation payer;
- shared ALT;
- repeated recipient/collector;
- transaction-template similarity;
- repeated co-firing.

Goal:
avoid counting one bot fleet as N independent smart-money votes.

### C. EXECUTION_URGENCY
Normalize execution cost against contemporaneous network conditions.

Candidate fields:
- priority fee percentile;
- Jito tip percentile;
- fee / median fee ratio;
- confirmation / block-position context where public data allow.

This is never a standalone alpha signal.

Hypothesis:
high urgency becomes useful only when combined with:
- independent entity quality;
- early public eligibility;
- sellability;
- pre-crowd timing.

### D. NEGATIVE ALPHA / DISTRIBUTION FINGERPRINT
Study whether historically informative entities exhibit recognizable pre-distribution behavior:
- recipient shift;
- collect/sweep convergence;
- sell-route activation;
- rising sell pressure;
- changing execution urgency;
- inventory fragmentation/consolidation.

Potential downstream use:
existing Distribution/Pullback warning layer only after prospective validation.

## First scientific test

Use existing historical Solana cases as replay controls, but award ZERO prospective alpha credit.

For each case:
1. freeze all evidence that would have been public at T0;
2. compute baseline wallet/entity evidence;
3. add execution-fingerprint evidence;
4. collapse correlated wallets;
5. compare independent entity count before/after;
6. measure whether the challenger would have changed classification before outcome;
7. evaluate matched losers and ordinary launches.

Primary endpoints:
- false independence reduction;
- entity-collapse precision;
- incremental lead time;
- false positive delta;
- realized sellable outcome;
- whether fingerprint evidence survives wallet rotation prospectively.

## Promotion rule

No production use until prospective rows demonstrate incremental value over current entity/provenance logic.

Required:
- multiple forward rows;
- matched controls;
- no future-label leakage;
- no same-venue-only identity inference;
- no same-router-only identity inference;
- no current wallet PnL projected backward;
- measurable improvement over champion;
- no paid source required.

## Kill conditions

Kill or downgrade the hypothesis if:
- fingerprint similarity mostly reflects common public infrastructure;
- different entities regularly collide on the same fingerprint;
- wallets change fingerprint too easily for useful persistence;
- incremental entity resolution is negligible after existing funding/common-control logic;
- signal appears only retrospectively;
- outcome improvement disappears after sellability/slippage;
- maintaining the feature requires paid provider data.

## Immediate priority

P0:
- ingest the public replication package as a methodology/data benchmark;
- reproduce the five-feature cluster contract from public artifacts;
- map paper-backed fields to existing Alpha Lab entity/provenance owners;
- add no new scanner.

P1:
- test fee-payer / recipient / venue fingerprints on existing Solana wallet cohorts.

P2:
- add ALT / instruction-template / urgency challengers only if P1 shows incremental value.

P3:
- evaluate prospective rows under #1134 / #1340.

Success means:
**Alpha Lab can distinguish genuinely independent early actors from one rotating bot/operator fleet more accurately using only free/public evidence.**
