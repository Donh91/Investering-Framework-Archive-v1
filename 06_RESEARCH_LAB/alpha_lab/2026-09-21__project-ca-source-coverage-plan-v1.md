# Project→CA Discovery Source Coverage Plan v1

Date: 2026-09-21
Status: RESEARCH_ONLY / PRE-P1-ACTIVATION
Owner: #1087
Purpose: turn the source-priority hypothesis into a falsifiable coverage design before prospective counters start.

## Core decision

Do not add another scanner. Reuse the Project Memory owner and treat each source family as an observation channel with explicit health, cost, latency, authority and expected discovery role.

## Frozen source families

### S1 ECOSYSTEM_DIRECTORY
Role: cheap project discovery, including no-token projects.
Authority: discovery only.
Health proof: successful collection plus parseable project universe count.
Failure mode: directory curation lag, missing projects, mutable pages.

### S2 ONCHAIN_FACTORY_DEPLOYMENT
Role: exact launch/deployment discovery.
Authority: very high for occurrence, not project ownership.
Health proof: bounded block range + RPC/log completion receipt.
Failure mode: non-factory launches, copied names/socials.

### S3 GITHUB_ARTIFACT
Role: prelaunch project discovery/material change.
Authority: artifact existence only.
Health proof: API/search response with rate-limit/coverage receipt.
Failure mode: forks, copied README, spam, unrelated chain references.

### S4 PACKAGE_REGISTRY
Role: shipping/maturity/material change.
Authority: package/version existence.
Health proof: registry response + package/version timestamp.
Failure mode: squatting, empty packages, no ownership proof.

### S5 FIRST_PARTY_WEB_DOCS_APP
Role: mechanic semantics, product-live evidence, CA candidate.
Authority: medium after authentication, never sufficient for on-chain identity.
Health proof: fetch success + observed_at + content hash.
Failure mode: mutable marketing, stale claims, spoofing.

### S6 AUTHENTICATED_SOCIAL
Role: publication clock, launch/CA candidate.
Authority: candidate evidence.
Health proof: retrievable post/account provenance and timestamp.
Failure mode: deletion, API gaps, impersonation.

### S7 VERIFIED_CHAIN_CONTROL
Role: exact identity/control corroboration.
Authority: high where deterministic.
Health proof: block/tx/contract evidence.
Failure mode: proxy/migration/control-root complexity.

### S8 PONS_FACTORY_METADATA
Role: launch occurrence + candidate project linkage.
Authority: occurrence high, project ownership medium/low.
Health proof: exact block/log/event + decoded fields.
Failure mode: self-asserted/copyable project metadata.

### S9 WALLET_CALLER
Role: corroboration and timing context only.
Authority: none for project identity.
Health proof: receipt-level provenance and independent entity.
Failure mode: seeded receipts, correlated crowd, copy trading.

### S10 MARKET_AGGREGATOR
Role: market eligibility, liquidity/sellability/context.
Authority: market context, not project identity.
Health proof: source timestamp + pair/quote/supply semantics.
Failure mode: stale/wrong pair, MC/FDV confusion.

## Coverage accounting

Every scheduled source observation must yield exactly one health class:
- HEALTHY_NONEMPTY
- HEALTHY_ZERO
- PARTIAL
- DEGRADED
- UNAVAILABLE
- NOT_DUE

Only HEALTHY_ZERO may support a claim that the source saw no eligible projects/events.

For each source/day or source/run freeze:
- source_family
- run_id
- scheduled_window
- observed_at_utc
- coverage_start/end
- health_class
- raw_item_count
- parsed_item_count
- emitted_project_trial_count
- error_class/null
- evidence_hash
- estimated_cost
- latency_ms if available

## Cross-source dedup rule

The denominator unit is the project trial, not the number of URLs.
Mirrors, directory copies and social reposts can increase corroboration but never create multiple independent projects.
Dedup keys are deterministic project identity candidates plus evidence linkage, with UNKNOWN retained when uncertain.

## What source quality means

A source is useful if it prospectively improves one or more of:
1. earlier project first-seen;
2. lower false-negative rate;
3. exact identity/binding;
4. material-change detection;
5. lower Deep-Dive burden;
6. lower cost/latency for equivalent coverage.

It is not useful merely because it contains historical winners.

## 30-trial source ablation

For the first 30 future eligible project trials, record source-family availability without changing routing thresholds.

Compare:
A - deterministic low-cost set S1-S4;
B - A + identity/first-party set S5-S8;
C - B + corroboration/context S9-S10.

Questions:
- How many unique projects are first seen by each family?
- What is the marginal unique recall of each family?
- What is median lead time by first-seen family?
- Which family creates false identity links?
- Which family increases DD load without qualified watches?
- Which sources are redundant mirrors?
- What is cost per unique eligible project and per qualified watch?

No family may be removed before 30 trials solely for zero wins. A persistently unhealthy source may be operationally disabled without interpreting its missing observations as evidence.

## Historical replay checks

Use only to validate representation:
- Boost Town: S1/S5 should discover project; S8/S7/S10 can later bind/verify.
- lpTOKEN.fun: S1/S3/S5 should retain project while token state stays NO_PROJECT_TOKEN.
- QLWY: S5/S7 must preserve bridge continuity and prevent NEW_TOKEN inference.
- MEEP: S1/S5/S8 can converge without granting alpha.
- DARK/BiX: S5 semantic richness may differ, but generic AI words cannot promote.
- NET/SAFIX: S1/S5 discovery plus S7/S8 identity must expose join/conflict state.

Zero prospective credit.

## Activation boundary

This plan requires no new runtime before P1. When P1 is accepted, implementation should attach source receipts to the existing Project Memory adapter rather than create a parallel source ledger.

No automatic source weights. No BUY/SELL authority. No autonomous source removal. Source priority remains a hypothesis until prospective ablation evidence matures.
