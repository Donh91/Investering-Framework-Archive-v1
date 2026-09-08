# BlockHorizon Source Candidate v1

**Status:** MANUAL_EXPORT_SEED_ACTIVE / API_PENDING / RESEARCH_ONLY / PRIVATE_RAW_ARCHIVE_AUTHORIZED  
**Authority:** NONE_BY_ITSELF  
**Added:** 2026-09-07  
**Updated:** 2026-09-08  
**Purpose:** Preserve BlockHorizon as a high-priority Bitcoin on-chain historical research source while keeping raw values, source rights, revision semantics and framework authority separate.

## Current state

A user-initiated historical-export seed exists and has been validated into provider-value-free metadata. The current seed contains 32 downloaded CSV retrieval files representing 29 unique content hashes across valuation, profitability, STH/LTH cohorts, realized behavior, coin-age structure, cost-basis distributions, network context and challenger metrics.

The repository owner explicitly confirmed on 2026-09-08 that the BlockHorizon downloads are authorized for private internal archival and research. That owner attestation clears the previous framework-level private-retention hold. It does not grant public redistribution authority.

## IMPORTANT FOR ALL AGENTS - PRIVATE RAW DATA LOCATION

The raw BlockHorizon CSV files belong **only** in the private restricted data plane:

```text
repository: Donh91/secrets
raw root: raw/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
private receipts: receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
```

Agents must not copy raw rows, complete CSVs, provider-value samples or reconstructed private values into this public repository, public issues, public pull requests, public logs or public-facing outputs.

To use private BlockHorizon evidence, an authorized agent must read the private archive README and exact bundle manifest, then bind the input to an immutable private commit, exact path, byte count and SHA-256. Public files may contain only provider-value-free bindings, hashes, counts, date ranges, schema/completeness and validation state.

The current restricted-plane archive scaffold and owner attestation were merged at private commit:

```text
Donh91/secrets@bd9db93be27079bbc4f6c54ecd79527c9f08ba3c
```

The initial private bundle manifest currently records the expected 32 raw CSV retrieval files and remains transfer-pending until every file is physically present and hash-verified. See `CURRENT_PRIVATE_BINDING.json`.

Source endpoints:

- https://www.blockhorizon.io
- https://charts.blockhorizon.io/dashboard
- https://www.blockhorizon.io/policy/terms-and-conditions

## Current treatment

Do not promote BlockHorizon into canonical runtime authority.

Treat it as:

- historical research source;
- challenger/crosscheck source;
- future ingestion candidate;
- non-authoritative for portfolio actions, thresholds or canonical state.

## Durable assets

```text
SOURCE_CONTRACT_v1.json
SEED_INVENTORY_METADATA_v1.json
METRIC_REGISTRY_v1.json
VAULT_ARCHITECTURE_v1.md
ASTRA_RESEARCH_PROTOCOL_v1.md
tools/blockhorizon_seed_validator.py
CURRENT_PRIVATE_BINDING.json
```

## Data-plane rule

```text
public control plane -> source contract, code, metric registry, hashes/counts/date ranges and value-free bindings
restricted plane -> original raw exports, private normalized research views, immutable private receipts
credential plane -> credentials only, never ordinary repository files
```

The public Research Lab owner controls research semantics. The private repository stores values and has no independent framework or market-rule authority.

## Analysis firewall

The 2026 export can support retrospective historical research, but it is not automatically a true information-time replay of prior cycles. Current-methodology reconstructions, later model refits and any unknown provider backfill/revision can create hindsight contamination.

The research protocol therefore separates:

```text
RETROSPECTIVE_DESCRIPTIVE
CONTEMPORANEOUS_REPLAY
PROSPECTIVE_FORWARD
```

No historical result self-promotes into canonical rules.

## Next collection priority

P0 remaining:

1. aSOPR
2. URPD
3. HODL Waves
4. Supply Last Active full age-band family
5. Spent Volume full age-band family

P1 after that:

- STH SOPR
- STH CDD
- LTH CDD

The machine-readable queue is in `METRIC_REGISTRY_v1.json`.

## Re-entry triggers

Resume collection whenever:

- the user supplies additional manual exports for validation and private archival;
- BlockHorizon exposes validated machine-readable access;
- a private bundle is physically uploaded and needs hash/readback reconciliation.

Additional exports should be preserved raw in the restricted data plane first, then represented publicly only through provider-value-free bindings and the metric registry.
