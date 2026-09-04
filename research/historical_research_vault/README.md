# Historical Research Vault v1

**Status:** ACTIVE_RESEARCH_INFRASTRUCTURE  
**Authority:** NONE_BY_ITSELF  
**Location:** `research/historical_research_vault/`  
**Purpose:** Durable, audit-friendly source map and collection layer for historical replay research.

## Why this exists

The framework needs reproducible historical evidence for later Research Lab and Astra-class work without depending on one dashboard, one vendor, or a page still existing when a hypothesis is tested months later.

The vault is deliberately not a giant Git data dump.

It follows the repository dataset-storage policy:

- Git keeps source contracts, schemas, manifests, receipts, hashes, compact indexes and small deterministic replay tables.
- High-volume raw history stays in GitHub Actions artifacts or a durable bulk tier.
- Licensed/non-redistributable sources remain query-time or pointer-only.
- Missing observations remain missing. No silent interpolation, forward-fill, or current-universe substitution.
- A dataset is research evidence only. It has no market-state, model-weight, or portfolio authority.

Policy owner:
`research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/DATASET_STORAGE_POLICY_v1.md`

## V1 source map

| Source | V1 role | Current state | Durable raw archive |
|---|---|---|---|
| DefiLlama stablecoins | System liquidity history | Existing owner reused | Existing repo owner only, no duplicate pipeline |
| growthepie | ETH/L2 transmission history | Public endpoint probe verified | Disabled pending exact dataset redistribution review |
| Coin Metrics Community | BTC/ETH network + market history | Keyless probe verified for allowed bootstrap metrics | Disabled pending exact CC dataset scope freeze |
| CoinGecko | Market-price crosscheck | Query-time crosscheck only | Disabled by source-use/storage constraints |
| SQD Portal | Primary protocol-level on-chain replay | Public Portal docs verified, live PR probe required before final admission | Temporary T2 artifact only until Portal terms are frozen |

## Existing owner reuse

The vault must not duplicate a source that already has a governed owner.

DefiLlama stablecoin history is already collected by:

`script: scripts/data_terminal/defillama_stablecoin_owner.py`

with a historical backfill at:

`03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/backfill/global_history.jsonl.gz`

and a current pointer at:

`03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json`

The vault indexes this dataset instead of creating another copy.

## What V1 can do

`python scripts/research/historical_research_vault.py validate`

Validates source-registry / recipe integrity and refuses durable collection where the source contract has not cleared storage/redistribution review.

`python scripts/research/historical_research_vault.py collect-growthepie --chain base --metric stables_mcap --output-root <dir>`

Collects one bounded growthepie chain metric from the official API into a deterministic temporary capture package. The collector preserves the API's typed columns rather than inventing a normalized scalar.

`python scripts/research/historical_research_vault.py collect-coinmetrics --assets btc,eth --start-time YYYY-MM-DD --end-time YYYY-MM-DD --output-root <dir>`

Collects the verified keyless bootstrap metrics:
`PriceUSD,SplyCur,CapMrktCurUSD,TxCnt`.

`python scripts/research/historical_research_vault.py probe-coingecko --coin bitcoin`

Runs a metadata/provenance probe only. Raw payload archival is intentionally disabled.

## SQD Portal, primary protocol replay

SQD replaces The Graph as the active protocol-level replay path because the public Portal HTTP API can be called directly by GitHub Actions without requiring the user to operate Subgraph Studio on desktop.

The collector uses finalized EVM data only:

`python scripts/research/historical_research_vault.py collect-sqd --dataset ethereum-mainnet --from-block <N> --to-block <N> --address <0x...> --output-root <dir>`

or an event-topic filter:

`python scripts/research/historical_research_vault.py collect-sqd --dataset ethereum-mainnet --from-block <N> --to-block <N> --topic0 <0x...> --output-root <dir>`

Guardrails are deliberate:

- finalized-stream only;
- maximum 5,000 blocks per capture;
- at least one contract-address or topic0 filter is mandatory;
- dataset slug is validated before URL construction;
- raw response and normalized rows are hashed;
- output is temporary T2 artifact data, not a Git data dump;
- no interpolation or inferred rows;
- no framework or portfolio authority.

The public Portal currently supports unauthenticated use by default. SQD also supports opt-in per-request authorization for Portals. The collector therefore accepts an optional complete `Authorization` header through the runtime environment variable `SQD_PORTAL_AUTHORIZATION`, but no credential is required or committed for the default public Portal path.

A one-block keyless probe is part of the SQD admission PR so live behavior is verified rather than inferred from documentation.

## Deferred alternatives

The Graph is no longer an active vault source or blocker. It remains a deferred optional challenger if a future research question specifically requires an existing subgraph that SQD cannot reproduce efficiently.

Bitquery is a future enriched crosscheck candidate, not an active source. Dune is a future derived SQL/research crosscheck candidate, not an active raw-history owner.

This preserves the source-count discipline: do not add either until SQD has demonstrated incremental replay value or a concrete evidence gap requires them.

## Storage layout

```text
research/historical_research_vault/
  README.md
  LATEST.json
  SOURCE_REGISTRY_v1.json
  SOURCE_RECIPES_v1.json
  VAULT_BOOTSTRAP_RECEIPT_2026-09-04.json
  schemas/
    CAPTURE_MANIFEST_v1.schema.json
```

Temporary collector output is intentionally routed outside this folder.

Recommended runtime output:
`$RUNNER_TEMP/historical_research_vault/`

A future promoted dataset must use the existing T0/T1/T2/T3/T4 storage classes and registry gate.

## Research priority

V1 is intentionally narrow.

1. Reuse DefiLlama stablecoin history already present.
2. Add ETH/L2 transmission history from growthepie.
3. Add BTC/ETH independent network/market crosschecks from Coin Metrics Community.
4. Keep CoinGecko as price crosscheck rather than durable owner.
5. Use bounded SQD Portal replays when a concrete protocol-level question requires logs or contract-event history.

Do not add a sixth active source until one of the above has demonstrated unique replay value or a specific evidence gap cannot be answered by the current five.

## Automation policy

There is no scheduled collection workflow in V1.

The vault remains evidence-demand driven. A scheduled collector is justified only after bounded replays demonstrate repeatable incremental value that is worth the extra automation surface.

The PR gate validates contracts and tests. SQD admission additionally uses a one-block public Portal smoke test. Larger source probes remain bounded and temporary.

## Promotion gate

A vault dataset may not become durable owner data until it has:

- source identity;
- retrieval timestamp;
- raw payload or immutable source object;
- normalized representation;
- package/member SHA-256;
- schema version;
- coverage start/end;
- publication/settlement/retrieval timing;
- duplicate/overlap policy;
- missingness policy;
- raw-to-normalized parity receipt;
- storage class + retention decision;
- license/redistribution classification.

## Kill criteria

Kill or merge a vault source if any of these holds:

1. It duplicates an existing owner without unique replay value.
2. Its storage/license terms prevent reproducible use and an equivalent permitted source exists.
3. It cannot produce a deterministic receipt and coverage declaration.
4. It adds narrative context but no row-level evidence.
5. Three bounded replay attempts show no incremental research value over existing sources.
6. It materially increases automation fragility before proving value.

## Authority ceiling

Historical Research Vault evidence can support:

- historical replay;
- falsification;
- source crosschecks;
- experiment design;
- coverage-gap analysis.

It cannot directly change:

- market state;
- Core thresholds;
- model weights;
- portfolio permissions;
- live execution.

Those require the existing governance path.
