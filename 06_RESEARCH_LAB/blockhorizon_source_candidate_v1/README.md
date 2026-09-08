# BlockHorizon Source Candidate v1

**Status:** MANUAL_EXPORT_SEED_ACTIVE / API_PENDING / RESEARCH_ONLY / TERMS_HOLD  
**Authority:** NONE_BY_ITSELF  
**Added:** 2026-09-07  
**Updated:** 2026-09-08  
**Purpose:** Preserve BlockHorizon as a high-priority Bitcoin on-chain historical research source while keeping raw values, source rights, revision semantics and framework authority separate.

## Current state

A user-initiated historical-export seed now exists locally and has been validated into provider-value-free metadata. The current seed contains 29 unique CSV datasets across valuation, profitability, STH/LTH cohorts, realized behavior, coin-age structure, cost-basis distributions, network context and challenger metrics.

Raw BlockHorizon values are **not persisted to GitHub** at this stage.

Reason: the current BlockHorizon product page advertises full-history exports, while the published Terms and Conditions also prohibit copying/distribution/mirroring without written consent. Until the planned retention/mirror use is explicitly permitted, the repository stays fail-closed at metadata/hash level only.

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
CURRENT_PRIVATE_BINDING.json  # added only after a hash-bound restricted receipt is merged
```

## Data-plane rule

```text
public control plane -> source contract, code, metric registry, hashes/counts/date ranges and value-free bindings
restricted plane -> raw/normalized provider values only after the provider-rights gate clears
credential plane -> credentials only, never ordinary repository files
```

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

Resume collection when either:

- the user supplies additional manual exports for local validation;
- BlockHorizon exposes validated machine-readable access;
- provider rights/retention terms are explicitly cleared for the planned private storage.

Additional exports may be validated immediately. GitHub raw persistence remains blocked independently until the rights gate clears.
