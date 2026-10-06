# S3 Bubblemaps Challenger Source Audit - 2026-10-06

Status: DOCUMENTED_CAPABILITY / AUTH_REQUIRED / OPTIONAL_CHALLENGER / NOT_CANONICAL
Master queue: README.md
Master issue: #1512
Lane: S3_ENTITY_ADJUSTED_CLUSTER_AND_BUNDLE_V1

## Public implementation evidence

Bubblemaps maintains a public documentation repository:

- https://github.com/bubblemaps/api-docs
- current OpenAPI file: openapi.json
- OpenAPI title: Bubblemaps Data API
- OpenAPI version: 0.3.1
- server: https://api.bubblemaps.io
- reviewed openapi.json blob: 99e7e28d9fdda366fd5a30edfbd49c2f63edccd3

This is API-contract evidence, not evidence for hidden/proprietary clustering internals.

## Authentication

The documented API uses:

`APIKeyHeader`
header name:
`X-ApiKey`

Relevant endpoints therefore remain:
`AUTH_REQUIRED / NO_LIVE_API_PROOF_IN_THIS_RUN`

Do not infer coverage/reliability merely from published OpenAPI.

## Relevant endpoints

### GET /v0/tokens/holders/{chain}/{token_address}

Supports:
- holder limit;
- historical unix timestamp;
- refresh;
- optional address metadata.

Potential use:
external historical-holder challenger.

### GET /v0/tokens/map/{chain}/{token_address}

Supports:
- historical timestamp;
- `use_magic_nodes`;
- `use_time_nodes`;
- `return_nodes`;
- `return_relationships`;
- `return_clusters`.

The API description explicitly says time nodes are temporal groupings of transfers through CEX/DEX/whitelisted contracts and can be included in cluster computation.

Potential use:
provider-vs-internal cluster challenger.

### POST /v0/relationships/subgraph

Accepts:
- 2 to 1000 addresses;
- optional context token key.

Returns grouped transfer relationships.

Potential use:
bounded external relationship challenger for a preselected wallet cohort.

### GET /v0/tokens/metrics/{chain}/{token_address}

Returns supply stats and map scores.

Use:
challenger/diagnostic only. Do not import composite scores as edge.

## Documented chain enum

The current OpenAPI enum includes:
- eth
- base
- solana
- tron
- bsc
- sonic
- ton
- avalanche
- polygon
- monad
- hyperevm
- arbitrum
- robinhood
- arc

Robinhood therefore appears in the documented API contract.

This does NOT prove current data completeness, historical depth or freshness for Robinhood.

## Why this source is unusually relevant to S3

Unlike a screenshot-only cluster provider, this API can in principle expose:
- historical holders;
- map nodes;
- provider relationships;
- provider clusters;
- Magic Node / Time Node variants;
- subgraph relationships.

That makes the provider output measurable against the internal relationship resolver.

## Required challenger experiment

If API access is available later, do not integrate it broadly.

Start with frozen cases:

1. CA3C/5FBF positive relationship fixture.
2. PEPE B790 -> C0B single-transfer control.
3. one organic/no-link control.
4. later, SHIB/PEPE/BRETT cluster claims when raw address sets are available.

For each case freeze:
- provider request timestamp;
- endpoint/options;
- historical timestamp parameter if used;
- magic/time-node flags;
- returned nodes;
- returned relationships;
- returned cluster membership;
- raw response hash;
- schema hash.

Compare against:
- internal relationship state;
- internal coordination state;
- infrastructure exclusions;
- raw chain evidence.

Feed mismatches to X0 DISAGREEMENT_ALPHA_V1.

## Critical semantic test

The most important research question is not:
"does Bubblemaps find clusters?"

It is:
"when Bubblemaps groups wallets, which part reflects economic-control evidence, which part reflects coordination, and which part reflects shared infrastructure/time-node heuristics?"

Alpha Lab deliberately separates those concepts.

A provider cluster must therefore NOT automatically collapse wallets into one economic entity.

## Source-audit requirements before live admission

Required:
- repeated availability probes;
- schema stability;
- historical timestamp behavior;
- map freshness/cache semantics;
- chain-specific coverage;
- Magic Node / Time Node sensitivity;
- null/missing behavior;
- rate limits and cost;
- retention/licensing;
- reproducibility of known positive and negative controls.

## Current verdict

Bubblemaps is a HIGH_VALUE_OPTIONAL_CHALLENGER for S3.

It is not required to make progress because Alpha Lab now has a deterministic raw-evidence relationship resolver.

Best role:
provider disagreement surface + cluster discovery challenger.

Not allowed:
provider cluster -> common ownership truth;
provider score -> trading edge;
provider availability -> canonical dependency without source audit.
