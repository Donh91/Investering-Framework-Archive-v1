# Conviction Cluster V0 - integration handoff

Date: 2026-10-01
Owner: #1419
Status: READY_FOR_EXISTING_OWNER_IMPLEMENTATION / SHADOW_ONLY

## Fresh-read decision
Do not build a parallel wallet scanner.

The repository already contains the correct substrate in `scripts/api_agent/meme_alpha_clean_g3.py`:
- `MEME_ALPHA_CURRENT_TOKEN_BUYER_GRAPH_v1`
- as-of `compute_asof_wallet_quality()`
- conservative `adjust_wallet_entities()`
- strong-controller collapse
- same-funder retained as relationship evidence rather than silently collapsed identity
- prospective freeze support through `freeze_shadow_observation()`

The existing runtime also explicitly forbids portfolio/trade/buy/sell/position-size/canonical-promotion outputs.

## Integration point
New contract:
`research/api_agent/meme_alpha/experiments/CONVICTION_CLUSTER_DETECTED_V0_INTEGRATION_CONTRACT.json`

Flow:
existing discovery -> exact token identity -> current-token buyer graph -> as-of wallet denominator -> entity adjustment -> conviction-cluster shadow evaluation -> immutable freeze -> 24h/72h/7d outcomes -> matched-control evaluation.

Pons remains a discovery adapter under Moonshot, with Blockscout only post-discovery exact-CA enrichment. Project->CA remains upstream discovery/binding. No owner is replaced.

## Implementation delta
Extend CLEAN_G3-derived shadow packet with a sibling research-only cluster summary. Do not modify current G3 champion semantics.

Required logic:
1. consume only buyer rows available by cutoff;
2. consume only wallet outcomes matured before cutoff;
3. group STRONG_CONTROLLER addresses as one beneficial-control cluster;
4. do not count SAME_FUNDER alone as same identity, but mark independence uncertain where material;
5. exclude/UNKNOWN non-intentional transfer, reward, airdrop, LP/MM/router/solver provenance;
6. count only research-qualified clusters;
7. freeze V0 event only when >=2 sufficiently independent qualified clusters coexist;
8. retain one-cluster and zero-cluster rows as controls;
9. mature outcomes at 24h/72h/7d;
10. compare incremental information against controls before any promotion proposal.

## Fail-closed rules
- missing denominator -> no qualified cluster
- unresolved beneficial control -> do not double-count
- missing sellability/liquidity -> UNKNOWN, never PASS
- post-cutoff wallet history -> forbidden
- historical FARTCOIN/GOAT/ORBIO cases -> zero prospective credit
- no user alert from V0
- no BUY/SELL/position sizing
- no new scheduled scanner

## Seed research entities
These are research priorities only and are not hard-coded champion truth:
- Sigil/FARTCOIN beneficial-control cluster hypothesis
- Hdxk/GOAT, pending full deterministic identity + denominator
- 0xe2eba6a5ddf2c0f1ddec262c466551f18396d43a on Robinhood, pending repeatability

## Acceptance tests
Positive:
- two genuinely independent qualified clusters, all required states usable -> V0 frozen shadow event.

Negative:
- two addresses linked by STRONG_CONTROLLER -> one cluster, no two-cluster event.
- two addresses only sharing a funder -> preserve relation, do not assert same identity; independence may remain UNKNOWN.
- one qualified cluster + one wallet without matured denominator -> no V0 event.
- transfer/airdrop/reward masquerading as buy -> no qualifying cluster vote.
- outcome data available only after cutoff -> cannot influence frozen features.
- liquidity/sellability unknown -> remains UNKNOWN.
- historical winner fixture -> never earns prospective credit.

## Cost/operations
No model call on ordinary no-change runs.
Use deterministic buyer/provenance/denominator evidence first.
Escalate intelligence only for material entity/provenance conflict.
No new schedule is justified until V0 has natural eligible events.
