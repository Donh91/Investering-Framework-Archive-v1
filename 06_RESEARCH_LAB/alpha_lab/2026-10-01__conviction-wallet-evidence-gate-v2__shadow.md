# Conviction Wallet Intelligence - Evidence Gate v2

Date: 2026-10-01
Parent: #1419
Status: HISTORICAL GATE COMPLETE / PROSPECTIVE SHADOW PREREGISTRATION READY

## New denominator evidence: EsqEki
Candidate address:
`EsqEkirkY6s1RPsb3YaJZcP4APQz77BWmBAVCsbNNhpj`

Current third-party wallet analytics snapshot (Birdeye, observed 2026-10-01):
- realized PnL ~+$3.38m
- unrealized PnL ~-$9.18m
- total PnL ~-$5.79m
- volume ~$103.04m
- ~49.8k transactions
- reported win rate 18.75%
- distribution of tracked outcomes includes many losing positions

Interpretation:
This strongly falsifies any naive hypothesis that the suspected Sigil funding wallet is valuable because it simply wins often. If the entity link survives, the potentially useful fingerprint is asymmetric selection/sizing/conviction in rare positions, not high raw win rate.

A separate 30-day tracker (uwuu.ai, refreshed 2026-09-30) reports a highly concentrated recent period: ~18 trades across 2 tokens, ~50% win rate, with almost all gains driven by BP and a smaller BUTTHOLE loss. This is not directly comparable to Birdeye's longer aggregate and must not be merged numerically. It nevertheless reinforces fat-tail/concentration behavior.

## Current live-behavior context
Public wallet-tracking posts in Aug 2026 reported EsqEki accumulating roughly $228k-$254k of ANSEM around ~$237m-$239m market cap, while holding substantial staked SOL. This is useful as a forward-looking behavioral observation but it occurred before this hypothesis was preregistered and therefore earns ZERO prospective alpha credit.

## Model revision
Replace the weak feature:
`wallet_win_rate`

with a vector:
- selectivity_rate
- capital_weighted_hit_rate
- payoff_asymmetry
- early_entry_quality
- conviction_accumulation
- retained_upside
- max_loss_per_failed_bet
- winner_concentration
- denominator_size
- beneficial_control_confidence

A low win-rate wallet may still be valuable if losses are bounded and rare early conviction positions create very large executable gains.

## Independence rule
Execution wallets connected by direct consolidation, common funding, exchange-deposit linkage or strong beneficial-control evidence are one cluster vote, not multiple votes.

## Prospective challenger
Preregister event name:
`CONVICTION_CLUSTER_DETECTED_V0`

Shadow event candidate conditions, intentionally qualitative until historical reconstruction supports thresholds:
1. candidate token is independently discovered by existing Alpha Lab path;
2. >=2 beneficial-control clusters with prior research qualification enter/accumulate;
3. clusters are independently funded to useful confidence;
4. activity is intentional capital deployment, not transfer/airdrop/reward/MM/router;
5. at least one cluster shows repeat accumulation or meaningful retained exposure;
6. liquidity/sellability and identity gates pass;
7. event frozen before outcome/social hindsight.

Fields:
- observed_at
- token_ca
- chain
- cluster_count
- qualified_cluster_ids_hash
- entry_age_by_cluster
- capital_deployed_by_cluster
- accumulation_count
- beneficial_control_confidence
- funding_independence_state
- provenance_state
- liquidity_state
- sellability_state
- catalyst_state
- broad_social_propagation_state
- historical_denominator_refs
- outcome_24h
- outcome_72h
- outcome_7d
- max_drawdown_7d
- executable_outcome_state

## Promotion policy
No automatic trading.
No Tier A exists yet.
Current research priorities:
- Sigil/FARTCOIN: B-research candidate
- Hdxk/GOAT: B-research candidate
- ORBIO 0xe2eb...d43a: B-research candidate

Tier A requires repeat independent winner evidence plus denominator-adjusted superiority and prospective confirmation.

## Historical cohort
High-information verified/strong candidates now include FARTCOIN, GOAT, PNUT, PEPE, WIF, MEW, NEIRO and GRIFFAIN. Do not bulk-reconstruct all until 3-5-case pipeline proves reproducible.

## Gate verdict
The research hypothesis survives, but in a narrower and more useful form:
**do not copy wallets; detect independent conviction clusters and score their behavior conditional on their full denominator.**

The historical phase has produced enough evidence to preregister the shadow event. Further historical expansion is subordinate to denominator quality and prospective falsification.

No BUY/SELL authority.
