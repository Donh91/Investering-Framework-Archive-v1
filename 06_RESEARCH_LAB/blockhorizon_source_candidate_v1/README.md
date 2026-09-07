# BlockHorizon Source Candidate v1

**Status:** API_PENDING / RESEARCH_ONLY  
**Authority:** NONE_BY_ITSELF  
**Added:** 2026-09-07  
**Purpose:** Preserve BlockHorizon as a high-priority Bitcoin on-chain source candidate so it is not forgotten while API/MCP access is pending.

## Source endpoints

- https://www.blockhorizon.io
- https://charts.blockhorizon.io/dashboard

## Current treatment

Do not promote BlockHorizon into canonical runtime authority yet.

Until API/MCP access, data rights, timestamps, revision behavior and calculation methodology are validated, treat the site as:

- historical research candidate
- challenger/crosscheck source
- future ingestion candidate
- non-authoritative for portfolio actions, thresholds or canonical state

## Future action when access is available

1. Perform a bounded, exhaustive scrape/index of the public site, dashboard, chart catalog, documentation and historical export surfaces.
2. Preserve discovery metadata, metric names, definitions, source timestamps, update cadence, provenance and access method.
3. Test export/API/MCP surfaces before relying on browser scraping.
4. Recover the maximum useful historical series without silently changing historical semantics.
5. Crosscheck overlapping metrics against existing owner/independent sources before admission.
6. Verify terms, retention rights and redistribution/storage constraints before persistent bulk archival.
7. Record any discovered revision/backfill behavior and fail closed on ambiguous timestamps.

## High-value metric families to inspect

Priority candidates include, where actually exposed and validated:

- MVRV / MVRV Z-Score
- NUPL
- SOPR / aSOPR
- Realized Price / Realized Cap
- URPD and related UTXO price-distribution views
- supply age / HODL structure
- miner / issuance / circulating-supply metrics
- PlanB-derived and cycle-model outputs as challenger evidence only

## Potential future daily-log contribution

If source quality and machine access pass admission, evaluate whether selected slowly moving on-chain fields should be appended to daily capture logs as contextual evidence, not intraday triggers.

Candidate daily fields should be chosen only after validation and may include:

- selected on-chain valuation state
- realized-price distance/state
- SOPR/aSOPR regime state
- NUPL regime state
- supply-age/HODL regime summaries
- source freshness timestamp
- source revision/version marker if available

No daily-log field is authorized by this note alone.

## Re-entry trigger

Resume this work when the user returns with BlockHorizon API/MCP details, credentials/access instructions, or confirmation that machine-readable endpoints are available.

At that point, begin with source-contract and data-rights validation, then historical recovery, then crosschecks, then any admission proposal.
