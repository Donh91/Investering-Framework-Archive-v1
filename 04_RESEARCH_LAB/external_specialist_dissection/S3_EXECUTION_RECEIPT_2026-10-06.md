# S3 Entity-Adjusted Cluster & Bundle Truth - Execution Receipt - 2026-10-06

Status: RELATIONSHIP_RESOLVER_MERGED / RAW_HISTORICAL_MEMBERSHIP_PARTIAL / RESEARCH_ONLY
Master issue: #1512
Alpha execution issue: Donh91/Meme-Alpha-Lab#105
Alpha PR: Donh91/Meme-Alpha-Lab#106
Merge commit: 20b2e42670212dfc3341f93fa43cd0f7c4c72f85

## What changed

S3 now has a deterministic relationship primitive under the existing Forensics Qualification Shadow.

Implemented:
- explicit relationship evidence-edge contract;
- separate entity-relationship and coordination states;
- infrastructure/common-CEX exclusions;
- raw, strict entity, supported entity, probable-sensitivity and coordination concentration views;
- deterministic HHI/largest-entity calculations;
- positive raw-chain reference fixture;
- negative real-world single-transfer control;
- tests that correlation/behavior cannot create DIRECTLY_LINKED.

No new scanner or scheduler was created.

## Permanent semantic improvement

The machine now separates:

`RELATIONSHIP`
from
`COMMON CONTROL`
from
`COORDINATION`
from
`TRADING SKILL`
from
`INSIDER STATUS`.

This is the key S3 improvement.

A provider cluster can be useful without becoming a same-owner claim.

## Positive reference case - CA3C / 5FBF

Wallets:
- 0xca3c851b9b1e045c3b0712603bc77fc4c0a788b0
- 0x5fbff11d54a73b70c4c2093b48d391a4c489b58c

Fresh raw Ethereum reconstruction confirmed:
- repeated PEPE transfers from 5FBF to CA3C;
- PEPE transfer from CA3C to 5FBF;
- direct native ETH transfers in both directions during the reference window.

Ruling:
`STRONGLY_LINKED / COMMON_CONTROL_UNKNOWN`.

Existing benchmark seed states were updated from PROBABLE_CLUSTER to STRONGLY_LINKED.

They were NOT upgraded to DIRECTLY_LINKED.

## Infrastructure false-link control

The same raw flow contained:
- 0x74de5d4fcbf63e00296fd95d33236b9794016631, verified Spender with MetaMask/AirSwap metadata;
- 0x881d40237659c251811cec9c364ef91dc08d300c, verified MetaSwap router/DEX.

They are explicit infrastructure exclusions and cannot merge economic entities.

## Negative real-world control - PEPE single transfer

Transaction:
0x1a9138e1aa77acb888cdc05bd80c41a60e15a6e771fc30351c88f66a67fb4da3

Observed:
- 2023-04-22 17:25:47 UTC;
- direct PEPE transfer from 0xb790ee1a15964569573f3105c26033c3353a5f17
  to 0xc0b3218b16c2ec45df47422a18a5b1f6e070312f;
- approximately 2.14T PEPE.

Ruling:
`POSSIBLE_LINK / COMMON_CONTROL_UNKNOWN`.

This fixture prevents a large direct transfer from being silently converted into same-owner evidence.

## Concentration views

The resolver retains all views:

### RAW
Every non-infrastructure wallet stays separate.

### STRICT_ENTITY
Collapse DIRECTLY_LINKED only.

### SUPPORTED_ENTITY
Collapse STRONGLY_LINKED + DIRECTLY_LINKED.

### PROBABLE_SENSITIVITY
Also collapse PROBABLE_CLUSTER, but only as sensitivity analysis.

### COORDINATION
Separate graph based on coordination evidence. It does not imply common control.

This lets later research quantify whether entity adjustment actually improves signal quality instead of forcing one opaque cluster score.

## Bubblemaps challenger audit

Canonical source note:
S3_BUBBLEMAPS_CHALLENGER_SOURCE_AUDIT_2026-10-06.md

Public Bubblemaps OpenAPI v0.3.1 documents:
- historical holders;
- historical token map;
- optional Magic Nodes;
- optional Time Nodes;
- nodes;
- relationships;
- clusters;
- token metrics;
- relationship subgraph endpoint;
- current chain enum including Robinhood.

The API uses X-ApiKey.

Current state:
`HIGH_VALUE_OPTIONAL_CHALLENGER / AUTH_REQUIRED / NO_LIVE_API_PROOF`.

Bubblemaps is not required for the internal resolver.

## Remaining source gap

Alpha adapter gap:
`HISTORICAL_CLUSTER_RAW_MEMBERSHIP_V1`.

Blocked/partial historical cases include:
- BRETT >100-wallet batch/OKX cluster;
- SHIB 0x1406 descendant split;
- PEPE full genesis/bundle set.

Do not invent wallet addresses from screenshots, aliases or narrative claims.

## Current scientific ruling

Relationship-resolution capability: IMPLEMENTED.
CA3C/5FBF relationship: STRONGLY_LINKED.
CA3C/5FBF common control: UNKNOWN.
Provider cluster accuracy: UNKNOWN.
Cluster-adjusted predictive edge: UNKNOWN.
Historical membership coverage: PARTIAL.

## Next value

The resolver itself does not need another engine.

Future S3 work should:
1. recover raw historical membership only when reproducible;
2. run matched cluster/organic controls;
3. test whether adjusted concentration improves qualification/drawdown outcomes;
4. compare provider clusters versus internal states through X0.

Until raw membership is available, heavy research capacity should move to the next queue lane rather than guessing missing clusters.
