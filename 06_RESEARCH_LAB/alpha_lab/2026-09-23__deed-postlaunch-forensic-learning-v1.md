# DEED post-launch forensic learning packet v1

Date: 2026-09-23
Status: HISTORICAL_POST-LAUNCH_LEARNING / ZERO_PROSPECTIVE_CREDIT
Owner: #1087 Alpha Lab
Chain: Robinhood Chain (4663)
Token: Deed Estate (DEED)
Observed contract: 0x5e55f18453545d0d4314c5106a2d8db934298e95

## Why this case matters

DEED was previously conceptually relevant to Alpha Lab as a pre-launch project/CA discovery experiment. Post-launch evidence now makes it useful for a different question: can the same system that finds a project early avoid treating coordinated distribution and promotional activity as independent positive confirmation?

This packet does not label any person or project as fraudulent as a factual conclusion. Social posts supplied by the owner allege insider seeding, paid KOL promotion and early selling. Those allegations require transaction-level reproduction before canonical attribution.

## Independently verified context

- Robinhood Chain is permissionless/EVM-compatible. Anyone can deploy contracts; chain presence is not endorsement.
- Blockscout indexes DEED at the exact contract above with 1,000,000,000 total supply.
- Public market surfaces recorded a severe launch-day boom/bust. Exact peak/current values vary by venue and observation time, so the learning target is the distribution/provenance graph, not a single price print.
- DEED's own pre-launch whitepaper explicitly stated that no public DEED deployment had yet been broadcast at crawl time. This makes the transition from project-only memory to exact deployed CA a useful Project→CA test case.

## Owner-supplied social allegations to reproduce, not assume

The screenshots allege:
1. roughly 1% of supply was sent to wallets associated with unipcs and DumbCrayonEater before the shill wave;
2. unipcs exited around $350k market cap;
3. promotional KOLs were paid;
4. launch/distribution structure made retail exit liquidity.

State: UNVERIFIED_ALLEGATIONS_PENDING_CHAIN_REPRODUCTION.

## High-value forensic checks extracted from the screenshots

For any newborn token, freeze and inspect:

1. CREATION_DISTRIBUTION
   - every recipient in creation/initial distribution transactions;
   - amount and % total supply;
   - whether receipt is mint/transfer/buy;
   - timestamp relative to pool open/publication.

2. ROUND_NUMBER_DORMANT_RECIPIENTS
   - round-number balances;
   - fresh/no-history wallets;
   - funding/transfer source;
   - whether multiple wallets share origin.

3. PRETRADING_FREE_TRANSFERS
   - wallets receiving supply without market purchase before trading;
   - exact source transaction and relationship to deployer/launch wallet.

4. COORDINATED_EXIT
   - whether recipients sell in similar slices/order/time windows;
   - common proceeds destination, bridge or funding root;
   - realized proceeds where reproducible.

5. DEPLOYER_PROVENANCE
   - deployer funder;
   - age/history of deployer;
   - single-use vs reused;
   - bridge funding alone is weak evidence, not guilt.

6. CREATOR_FEE_FLOW
   - who can claim fees;
   - whether claimed;
   - destination;
   - whether flow matches public product/economic claims.

7. HOLDER_CONCENTRATION
   - top holders excluding pool, LP lock, routers and known infrastructure;
   - cluster by common funding/control only when evidence supports it;
   - historical recipients who sold must not disappear from risk analysis merely because they are no longer top holders.

8. PROMOTION_CLOCK
   - Tdistribution, Tpool_open, Tfirst_party_publication, Ttracked_wallet_entry, TKOL_wave, Texit;
   - social/KOL promotion after privileged distribution is a distinct risk pattern.

## New Alpha Lab distinction

Do not conflate:
- SELF_INITIATED_BUY
- PRIVILEGED_PRELAUNCH_TRANSFER
- GIFT/DUST/SEED
- CREATOR/DEV_ALLOCATION
- PAID_PROMOTER_ALLOCATION
- UNKNOWN_TRANSFER

A wallet's reputation cannot convert a privileged/free allocation into independent convergence.

## Proposed shadow-only risk primitives

These are evidence fields, not scores or thresholds:
- privileged_supply_pct_before_public_trade
- fresh_recipient_count_before_public_trade
- common_funder_cluster_count
- pretrade_transfer_recipient_count
- tracked_wallet_privileged_transfer_count
- recipient_exit_common_destination_state
- creator_fee_destination_alignment_state
- historical_launch_recipient_sellthrough_pct
- promotion_after_privileged_distribution_state
- deployer_single_use_state
- deployer_funding_provenance_state

UNKNOWN must remain UNKNOWN.

## Critical learning for FOMO wallet experiment

DEED directly attacks the naive wallet-convergence thesis. If a tracked wallet received free/privileged supply, that wallet must be excluded from independent convergence for that token unless a later self-initiated market buy can be separately evidenced under the frozen rules.

This supports the existing fail-closed FOMO remediation rather than creating a new scanner.

## Critical learning for Project→CA

Early project discovery is only half the job. At deployment, Project→CA should hand off to an origin/distribution forensic gate before wallet/caller corroboration can increase confidence.

Sequence:
PROJECT_FIRST_SEEN -> EXACT_CA_BINDING -> ORIGIN/DISTRIBUTION RECEIPT -> MARKET/SELLABILITY -> INDEPENDENT CORROBORATION.

No distribution receipt means no claim that early tracked-wallet activity is independent organic demand.

## Falsification

The social thesis is weakened or falsified if chain reproduction shows:
- the alleged wallets bought through the public market rather than received privileged supply;
- the alleged 1% amount is materially wrong;
- transfers occurred after open public trading with no privileged access;
- sell/proceeds claims cannot be reproduced;
- address attribution to named handles is unsupported.

Even if allegations fail, the case remains useful as a regression for transfer-vs-buy and privileged-distribution semantics.

## Decision

KEEP AS HIGH-VALUE HISTORICAL REGRESSION.
Do not grant Alpha Lab prospective credit.
Do not add a new risk score yet.
Use DEED to test the existing Project→CA origin layer and FOMO provenance gate.
Next machine task: transaction-level reproduction of the initial distribution and alleged tracked-wallet allocations using chain receipts, then freeze a DEED origin/distribution regression fixture if reproducible.
