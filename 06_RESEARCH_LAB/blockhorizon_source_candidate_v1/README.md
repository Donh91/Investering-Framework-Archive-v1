# BlockHorizon Source Candidate v1

**Status:** MANUAL_EXPORT_SEED_ACTIVE / PRIVATE_RAW_ARCHIVE_COMPLETE / API_PENDING / RESEARCH_ONLY  
**Authority:** NONE_BY_ITSELF  
**Added:** 2026-09-07  
**Updated:** 2026-09-08  
**Purpose:** Preserve BlockHorizon as a high-priority Bitcoin on-chain historical research source while keeping raw values, source rights, revision semantics and framework authority separate.

## Current state

The original BlockHorizon historical-export seed is now complete in the restricted data plane.

Verified original bundle:

- 32/32 expected CSV retrieval files present;
- 29 unique expected content hashes;
- all three expected exact-content duplicate filename groups preserved;
- 6,472,210 expected bytes verified;
- SHA-256 readback PASS;
- zero expected hash mismatches.

The private archive was finalized on `Donh91/secrets` main at:

```text
2cb7d1789ff9e9a934d1dcb36e6ba8541c3fdb2f
```

The immutable completion receipt is:

```text
receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/2026/09/08/2026-09-08__raw_archive_completion_receipt_v1.json
```

The repository owner explicitly confirmed on 2026-09-08 that the BlockHorizon downloads are authorized for private internal archival and research. This does not grant public redistribution authority.

## IMPORTANT FOR ALL AGENTS - PRIVATE RAW DATA LOCATION

The raw BlockHorizon files belong **only** in the private restricted data plane:

```text
repository: Donh91/secrets
raw root: raw/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
private receipts: receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/YYYY/MM/DD/
```

Agents must not copy raw rows, complete CSVs, provider-value samples or reconstructed private values into this public repository, public issues, public pull requests, public logs or public-facing outputs.

To use private BlockHorizon evidence, an authorized agent must read `CURRENT_PRIVATE_BINDING.json`, the private archive README and the exact completion receipt, then bind the input to an immutable private commit, exact path, byte count and SHA-256. Public files may contain only provider-value-free bindings, hashes, counts, date ranges, schema/completeness and validation state.

Expected duplicate retrieval filenames remain preserved in the raw archive because they are part of the original retrieval manifest. Exact-content duplicates count once analytically unless retrieval provenance itself is the research object.

Redundant JSON mirrors uploaded alongside CSV equivalents were removed from the current private tree. Supplemental CSV retrievals remain private and are tracked separately from original-bundle completeness.

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

## Additional metrics already recovered

The private raw archive also contains supplemental research CSVs including:

- aSOPR / Adjusted SOPR;
- SOPR Short Term Supply.

These are now registered as research inputs. Exact-content re-downloads remain one analytical content object unless retrieval-revision analysis requires otherwise.

## Next collection priority

P0 remaining:

1. URPD
2. HODL Waves
3. Supply Last Active full age-band family
4. Spent Volume full age-band family

P1 after that:

- CDD Short Term Supply
- CDD Long Term Supply

The machine-readable queue is in `METRIC_REGISTRY_v1.json`.

## Re-entry triggers

Resume collection whenever:

- the user supplies additional manual exports for validation and private archival;
- BlockHorizon exposes validated machine-readable access;
- a private retrieval revision needs hash/readback reconciliation.

Additional exports should be preserved raw in the restricted data plane first, then represented publicly only through provider-value-free bindings and the metric registry.
