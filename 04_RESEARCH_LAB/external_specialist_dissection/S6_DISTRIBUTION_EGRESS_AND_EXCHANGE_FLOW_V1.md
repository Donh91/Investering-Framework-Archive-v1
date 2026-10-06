# S6 - Distribution Egress and Exchange Flow v1

Status: IMPLEMENTATION_READY / RESEARCH_ONLY / EXTEND_EXISTING
Priority: P1
Master issue: #1512
Canonical owner: Meme Alpha Lab Distribution / Exit Overhang + Wallet Alpha

## Purpose

Test whether attributable movement of token supply toward genuine exit infrastructure adds information beyond:
- wallet sells already observed;
- latent Distribution / Exit Overhang;
- holder concentration;
- executable liquidity.

This lane does not create a new wallet engine, distribution engine, or sell signal.

## Distinction

Existing Distribution / Exit Overhang asks:
"How much economically relevant supply could sell?"

S6 asks:
"Is economically relevant supply actually moving toward a destination compatible with exit, and how strong is the evidence for that interpretation?"

These are different variables.

## Evidence chain

Preferred hierarchy:

1. DIRECT_EXECUTION
   - on-chain swap/sell semantics prove disposition at the observed timestamp/size.

2. VERIFIED_DESTINATION_ROLE
   - destination role is reproducibly established from first-party contract semantics or independently verifiable explorer/registry evidence.

3. RAW_TRANSFER_PATH
   - transfer path is known but final exit meaning is unresolved.

4. EXTERNAL_PROVIDER_LABEL
   - Arkham/Nansen/other entity label is challenger evidence only.

5. UNKNOWN
   - no defensible destination interpretation.

Provider labels never overwrite raw path evidence.

## Destination classes

- SELF_OR_LINKED
- DEX_POOL
- DEX_ROUTER
- AGGREGATOR
- BRIDGE
- CEX_DEPOSIT_SUPPORTED
- CEX_DEPOSIT_CHALLENGER
- CEX_HOT_WALLET_SUPPORTED
- MARKET_MAKER_INFRA
- BURN
- TREASURY
- UNKNOWN

## Egress interpretation states

- UNKNOWN
- INTERNAL_TRANSFER
- TRANSIT_ONLY
- EXIT_INFRA_EGRESS_SUPPORTED
- EXIT_INFRA_EGRESS_CHALLENGER
- DIRECT_SELL_SUPPORTED
- DATA_CONFLICT

A transfer to a router, aggregator, bridge or pool contract is not automatically a sale.

A CEX label is not automatically a supported CEX deposit.

## Required observation

For each observed movement preserve:
- egress_id;
- chain;
- token;
- source wallet/entity;
- destination address;
- timestamp;
- tx hash/log index where available;
- token amount;
- source remaining balance/supply denominator when known;
- destination class;
- destination evidence class;
- label provider if external;
- label observed_at;
- semantic validity at the event timestamp;
- direct-sale evidence if any;
- route/intermediate status;
- evidence refs;
- source snapshot hash.

## Derived research features

Where denominators are known:
- attributable_egress_fraction_of_source_remaining;
- attributable_egress_fraction_of_circulating_supply;
- egress_to_executable_liquidity_ratio;
- first_exit_infra_egress_latency;
- cumulative_exit_infra_egress_1h/6h/24h;
- qualified_wallet_egress_share;
- cluster_adjusted_egress_share.

UNKNOWN denominators remain null.

## Critical negative controls

- self-transfer is not exit;
- transfer among strongly linked wallets is not independent distribution;
- bridge transfer is not exit;
- router/aggregator transit is not exit;
- ERC20 transfer to a pool/router does not prove sale without swap/trace semantics;
- prior CEX funding of a wallet is not later CEX egress;
- common CEX funding does not imply common control;
- current provider label cannot be back-applied historically unless validity/provenance supports the event timestamp;
- missing destination label is UNKNOWN, not non-exchange;
- exchange hot wallet and exchange deposit address are distinct semantics;
- token burn is not market distribution;
- transfer to treasury is not market distribution by default.

## First capability proof

Reuse the already verified PEPE relationship fixture:
- 0x5fbf... -> MetaSwap 0x881d...
- destination is verified router/DEX infrastructure.

Expected S6 interpretation:
TRANSIT_ONLY, not DIRECT_SELL_SUPPORTED and not CEX egress.

This gives a real negative-control fixture from prior raw research.

Synthetic fixtures may test CEX/provider disagreement semantics but cannot count as market evidence.

## Hypotheses

### H-S6-001
Supported exit-infrastructure egress from qualified early winners predicts worse subsequent drawdown/continuation outcomes than otherwise similar wallets that merely transfer internally.

### H-S6-002
CEX/pool egress adds information beyond realized sell fraction and latent Distribution Overhang.

### H-S6-003
Provider-labeled exchange egress has lower scientific value than raw-path-supported egress unless label validity is reproducibly timestamped.

### H-S6-004
Cluster-adjusted egress is more informative than nominal wallet-count egress when related wallets are present.

## Evaluation

Compare:
1. latent overhang only;
2. realized sell fraction only;
3. raw transfer activity only;
4. supported exit-infra egress;
5. supported egress + cluster adjustment;
6. provider challenger labels.

Outcomes reuse existing Alpha outcome owners:
- 6h / 24h / 72h returns;
- MFE / MAE;
- liquidity path;
- terminal/rug/dead state where applicable;
- realizable exit quality.

## Promotion

Possible conclusions:
- EGRESS_INCREMENTAL_VALUE_SUPPORTED
- REALIZED_SELLS_SUFFICIENT
- OVERHANG_SUFFICIENT
- PROVIDER_CHALLENGER_ADDS_VALUE
- DESTINATION_SEMANTICS_TOO_WEAK
- NO_INCREMENTAL_VALUE
- INSUFFICIENT_EVIDENCE

No conclusion grants portfolio action.

## Implementation rule

Extend:
research/forensics_qualification_shadow_v1/

Do not:
- create a parallel wallet/forensics engine;
- make Arkham/Nansen canonical;
- infer a sell from transfer alone;
- change current Distribution Overhang states from this first capability build.

First build:
destination evidence contract + deterministic resolver + raw router negative-control fixture + tests.

Later:
bounded raw egress collection and provider challenger source audits.

## Authority

RESEARCH_ONLY.
No alert authority.
No automatic trade execution.
No portfolio action.
No canonical candidate qualification.
