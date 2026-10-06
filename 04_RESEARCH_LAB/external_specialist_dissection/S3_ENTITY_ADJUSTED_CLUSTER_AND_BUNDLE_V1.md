# S3 - Entity-Adjusted Cluster & Bundle Truth v1

Status: ACTIVE_RESEARCH_SPEC / P0 / RESEARCH_ONLY
Master queue: README.md
Master issue: #1512
Execution owner: Donh91/Meme-Alpha-Lab existing Forensics Qualification Shadow

## Core question

Can Alpha Lab replace naive wallet/holder counts and third-party cluster labels with a conservative graph of economically relevant relationships that improves launch qualification and distribution-risk research?

The target is not to prove human identity.

The target is to estimate:
- how many economically independent entities are present;
- how concentrated supply/early entry is after supported links;
- whether a launch is bundle/coordination compatible;
- whether linked supply later creates distribution overhang.

## Existing owner audit

Already owned by:
- research/forensics_qualification_shadow_v1/README.md
- CLUSTER_ADJUSTED_OWNERSHIP
- FIRST_SECONDS_BUNDLE_SNIPER_MICROSTRUCTURE
- DISTRIBUTION_EXIT_OVERHANG

Therefore:
- DO NOT create a new cluster engine;
- DO NOT create another scheduler;
- DO NOT replace relationship-state governance;
- extend the existing shadow with a deterministic evidence-edge contract and reproducible reference cases.

## Permanent distinction

`RELATIONSHIP != COMMON_CONTROL != TRADING_SKILL != INSIDER_STATUS`

A pair can be STRONGLY_LINKED without evidence that one human controls both wallets.

A common exchange source is not common-control evidence.

A direct token transfer is a real graph edge but alone does not prove common ownership.

## Evidence edge taxonomy

### Strong deterministic edges
- DETERMINISTIC_DELEGATION
- CONTRACT_CONTROL_RELATIONSHIP
- VERIFIED_MULTISIG_CONTROL
- REPEATED_RECIPROCAL_DIRECT_TRANSFER
- COMMON_NON_CEX_FUNDER_WITH_CORROBORATION

### Direct but non-ownership edges
- DIRECT_NATIVE_TRANSFER
- DIRECT_TOKEN_TRANSFER
- REPEATED_DIRECT_TRANSFER
- PROJECT_TREASURY_LINK
- CREATOR_DEPLOYER_LINK

### Behavioral corroboration
- REPEATED_CROSS_TOKEN_COENTRY
- REPEATED_COEXIT
- SYNCHRONIZED_FUNDING_WINDOW
- MATCHED_AMOUNT_MOTIF
- FIRST_BLOCK_BUNDLE_COMPATIBLE
- SHARED_EXECUTOR_NON_INFRA

### Discount / exclusion edges
- COMMON_CEX_FUNDER
- BRIDGE
- ROUTER
- LP_POOL
- BURN
- EXCHANGE_HOT_WALLET
- MARKET_MAKER_INFRA
- AIRDROP_DISTRIBUTION
- PROJECT_TREASURY_INFRA

Infrastructure may explain transaction paths without supporting wallet linkage.

## Relationship resolver

The deterministic resolver should be conservative.

### UNKNOWN
No admissible evidence, or only infrastructure/common-CEX evidence.

### POSSIBLE_LINK
One admissible direct or behavioral edge without independent corroboration.

### PROBABLE_CLUSTER
At least two independent admissible edge families support coordination, but common control is not directly established.

### STRONGLY_LINKED
Repeated reciprocal/direct economic transfers or multiple independent strong relationship families support a durable wallet relationship.

This still does NOT mean common human control.

### DIRECTLY_LINKED
Only deterministic control/delegation/project-control evidence can establish this state.

No amount of correlation alone upgrades to DIRECTLY_LINKED.

## Reference case A - 0xca3c / 0x5fbf

Existing benchmark:
MOG / SPX / PEPE / WOJAK recurring selector.

Public reporting previously attributed:
- 0xca3c851b9b1e045c3b0712603bc77fc4c0a788b0
- 0x5fbff11d54a73b70c4c2093b48d391a4c489b58c

to one smart-money entity.

Prior Alpha state:
PROBABLE_CLUSTER pending direct reconstruction.

### Raw-chain reconstruction 2026-10-06

Blockscout Ethereum evidence shows:

Address age:
- 0xca3c first observed transaction: 2022-11-05 23:50:35 UTC
- 0x5fbf first observed transaction: 2023-12-10 08:55:47 UTC

Direct evidence within 2023-12-10 to 2023-12-12 includes:
- repeated PEPE transfers 0x5fbf -> 0xca3c;
- one PEPE transfer 0xca3c -> 0x5fbf;
- one direct native ETH transfer 0x5fbf -> 0xca3c;
- repeated economic interaction over multiple blocks/times.

Examples:
- tx 0xf52ed5...: 0x5fbf -> 0xca3c PEPE
- tx 0xf308e2...: 0x5fbf -> 0xca3c PEPE
- tx 0xfb5c35...: 0xca3c -> 0x5fbf PEPE
- tx 0x404fe1...: 0x5fbf -> 0xca3c PEPE
- tx 0xdbb04c...: 0x5fbf -> 0xca3c PEPE
- tx 0x7a1bb2...: direct native ETH 0x5fbf -> 0xca3c

Ruling:
`STRONGLY_LINKED / COMMON_CONTROL_UNKNOWN`

Reason:
the relationship is directly supported by repeated reciprocal economic transfers, but there is no deterministic key/control/delegation proof.

### Infrastructure false-positive control

The same replay exposes:
- 0x74de5d4f... = verified contract "Spender", tagged MetaMask Swaps Spender / AirSwap Spender;
- 0x881d4023... = verified MetaSwap router, tagged MetaMask/Router/DEX.

These must be infrastructure exclusions, not cluster members or funders.

An EOA:
- 0x4d53f9106edd415ea63c847c9aa8d12b31880e05

sent native ETH to 0x5fbf and remains a legitimate funding-provenance lead. Its ownership/relationship is UNKNOWN until separately reconstructed.

## Reference case order

1. CA3C/5FBF
   Raw EVM relationship evidence exists now. Use as positive relationship / common-control-unknown fixture.

2. PEPE direct-transfer/cabal controls
   Use direct transfers plus CEX-funder false-link controls.

3. BRETT >100 OKX-funded cluster
   High VOI but blocked by missing raw address set. Common OKX source alone must not merge entities.

4. SHIB 0x1406 descendant split
   Test split lineage versus manipulation assumption.

5. Organic/CEX-funded controls
   Required denominator so common infrastructure is not mistaken for coordination.

## Cluster-adjusted concentration

Only after relationship states are reproducible may holder/buyer rows be collapsed into economic entities.

Compute:
- RAW_TOP10_SHARE
- CLUSTER_ADJUSTED_TOP10_SHARE
- INDEPENDENT_EARLY_BUYER_COUNT
- LARGEST_ECONOMIC_CLUSTER_SHARE
- CLUSTER_HHI
- PROJECT_PROXIMATE_CLUSTER_SHARE

Rules:
- UNKNOWN/POSSIBLE wallets stay separate by default;
- PROBABLE_CLUSTER may be reported as a sensitivity scenario, not canonical collapse;
- STRONGLY_LINKED can support an entity-adjusted research view with explicit common-control UNKNOWN;
- DIRECTLY_LINKED can be deterministically collapsed where the relationship semantics justify it;
- always retain raw holder/wallet counts alongside adjusted values.

## Cluster persistence

High-value extension:
test whether linked wallet groups recur across independent launches.

Freeze:
- cluster version;
- member wallets;
- evidence edges;
- first/last observed relationship;
- later token co-entry/co-exit;
- winners and losers;
- infrastructure exclusions.

Outcome:
cluster recurrence may become a coordination or wallet-skill context feature, never an insider label by itself.

## External challengers

Bubblemaps, Arkham and similar tools can provide:
- candidate cluster membership;
- entity labels;
- transfer/funding hints.

They remain challengers.

For every provider claim compare:
- provider relationship state;
- internal deterministic relationship state;
- raw evidence;
- later outcome.

Feed conflicts to X0 DISAGREEMENT_ALPHA_V1.

## Falsifiers

Demote/kill if:
- raw graph evidence rarely changes naive concentration;
- common-CEX/router effects explain most apparent clusters;
- provider clusters cannot be reproduced enough to grade;
- cluster-adjusted concentration adds no value after raw concentration/liquidity controls;
- false-link rate is material;
- maintenance cost exceeds information value.

## Next implementation

1. Add a deterministic evidence-edge schema to the existing Forensics Shadow.
2. Add a conservative relationship resolver.
3. Encode CA3C/5FBF as a raw-chain verified fixture.
4. Unit-test infrastructure/common-CEX/direct-transfer controls.
5. Update benchmark seed states only where raw evidence changes the relationship state.
6. Then choose one negative/control pair before touching BRETT.
7. No prospective threshold promotion until matched historical replay is frozen.

## Authority

Research only.
No insider accusation from cluster state.
No automatic BUY/SELL.
No common-control inference from one weak edge.
No provider cluster label becomes truth.
