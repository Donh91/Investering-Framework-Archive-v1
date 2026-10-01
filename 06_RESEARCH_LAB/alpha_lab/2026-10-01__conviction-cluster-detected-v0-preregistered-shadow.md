# CONVICTION_CLUSTER_DETECTED_V0 - Prospective Shadow Contract

Date: 2026-10-01
Parent: #1419
Status: PREREGISTERED_SHADOW_CHALLENGER
Trading authority: NONE

## Purpose
Test whether independent, historically qualified beneficial-control clusters provide incremental prospective information when they accumulate the same newly discovered token.

## Eligible upstream candidates
Only tokens already discovered/identified through existing Alpha Lab paths. This contract creates no parallel discovery scanner.

## Event eligibility
Freeze an event only when:
1. exact token identity is resolved;
2. >=2 research-qualified beneficial-control clusters show intentional capital deployment;
3. cluster independence is not contradicted by direct consolidation/common control/funding evidence;
4. transfers, airdrops, rewards, LP/MM/router/solver activity are excluded or UNKNOWN;
5. liquidity and sellability are PASS or explicitly UNKNOWN;
6. event timestamp precedes outcome evaluation.

## Frozen features
- event_id
- observed_at
- token_ca
- chain
- launch_age
- cluster_count
- qualified_cluster_ids_hash
- cluster_tiers_at_freeze
- first_entry_ts_by_cluster
- capital_deployed_usd_by_cluster
- repeat_buy_count_by_cluster
- retained_exposure_state
- beneficial_control_confidence
- funding_independence_state
- provenance_state
- liquidity_state
- sellability_state
- catalyst_state
- social_propagation_state
- denominator_refs
- source_health

## Outcome horizons
24h, 72h, 7d:
- executable_return
- max_drawdown
- liquidity_change
- sellability_state
- rug/scam/identity failure
- cluster distribution behavior

## Evaluation
Compare against:
A. matched Alpha Lab candidates without qualified-cluster convergence;
B. single-cluster candidates;
C. venue/time matched base rate.

Primary question:
Does multi-cluster convergence add information after controlling for candidate quality, liquidity, launch age and broad social propagation?

## Hard anti-leakage rules
- no historical event may earn prospective credit;
- no wallet tier may be upgraded from the event outcome before the outcome window closes;
- no threshold may be edited because a known winner would have missed it;
- related execution wallets count as one cluster;
- current social labels do not rewrite historical beneficial ownership;
- UNKNOWN is not PASS;
- no BUY/SELL output from V0.

## Initial research-qualified seeds
B_RESEARCH:
- Sigil/FARTCOIN beneficial-control cluster hypothesis
- Hdxk/GOAT trader, pending full address + denominator
- Robinhood wallet 0xe2eba6a5ddf2c0f1ddec262c466551f18396d43a, pending repeatability

None are Tier A.

## Promotion gate
V0 can only be proposed for champion integration after enough frozen prospective events exist to evaluate incremental information versus controls. Architecture completeness is not evidence.
