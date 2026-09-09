# US ALTERNATIVE DATA HISTORICAL VAULT v1 - Phase 0 Preflight

**Date:** 2026-09-09  
**Status:** SOURCE_NOTE / PREPARED_NOT_ACTIVE  
**Scope:** collection architecture, source feasibility, terms/access routing, storage preflight  
**Control plane:** `Donh91/Investering-Framework-Archive-v1`  
**Restricted data plane:** `Donh91/secrets`

## Purpose

This note records the Phase 0 preflight for the US Alternative Data Historical Vault v1 mission. It does not activate collection, create a trading signal, change DATA PING, change Round 3 scientific permissions, or authorize hypothesis testing/outcome scoring.

The mission remains collection-first. The design goal is to preserve what information was actually knowable at a given time, with immutable source lineage, without becoming dependent on Quiver Quantitative or another commercial aggregator.

## Current governance binding

Current restricted collection authority remains `PROSPECTIVE_COLLECTION_ONLY`. Existing private collection is active only for the currently activated Round 3 source set. New USAD sources must receive their own reviewed source/terms/activation path before live collection.

Raw or normalized restricted values belong only in `Donh91/secrets`. Public control-plane material may contain source contracts, schemas, hashes, counts, timestamp ranges, completeness and provider-value-free health metadata only.

## Overlap audit

Repository search and raw-directory inspection found no existing USAD owner or raw source family for SEC Form 3/4/5, SEC 13F, FINRA OTC/short data, USAspending, Congressional PTR, LDA lobbying or USPTO patents.

Existing restricted raw families at preflight are unrelated: BlockHorizon, MAEVE recovery, OKX OI, OKX realized funding, Deribit skew and TechDev archive.

Result: `NEW_INFORMATION`, with no current canonical dataset owner to extend.

## Source matrix

| ID | Source family | Official source | Earliest useful official history observed | Preferred archive mode | Preflight state |
|---|---|---|---|---|---|
| USAD01 | SEC Form 3/4/5 insider transactions | SEC DERA / EDGAR | 2006 | FULL_BULK_CANDIDATE subject to measured repo-size budget; otherwise targeted universe | TECHNICALLY_READY_FOR_CONTRACT |
| USAD02 | SEC 13F institutional holdings | SEC DERA / EDGAR | 2013 | TARGETED_UNIVERSE plus immutable archive-manifest/hash lineage | TECHNICALLY_READY_FOR_CONTRACT |
| USAD03 | FINRA ATS/non-ATS/off-exchange weekly summary | FINRA Equity API | rolling 4-year historic window + rolling 12-month production | TARGETED/HISTORIC_WINDOW_CAPTURE | BLOCKED_TERMS_CREDENTIAL_ACCEPTANCE |
| USAD04 | FINRA short volume / short interest | FINRA daily files + Equity API | daily consolidated NMS files from 2018-08-01; API Reg SHO rolling 12 months | HYBRID_OFFICIAL_FILES_AND_API | BLOCKED_PENDING_FINRA_TERMS_ROUTE |
| USAD05 | U.S. government contracts | USAspending API | source-defined federal award history | TARGETED_UNIVERSE by legal entity/recipient identity | TECHNICALLY_READY_FOR_CONTRACT |
| USAD06 | Congressional transaction disclosures | official House/Senate disclosure systems | source-dependent | TARGETED_DISCLOSURE_ARCHIVE | P1_DISCOVERY_REQUIRED |
| USAD07 | LDA corporate lobbying | U.S. Senate LDA | downloadable historic quarterly data + current REST route | TARGETED_UNIVERSE / official XML or REST | P1_TECHNICALLY_PROMISING |
| USAD08 | USPTO patent activity | USPTO Open Data Portal | source-dependent, broad historical patent archive | TARGETED_UNIVERSE | P1_BLOCKED_ACCOUNT_MFA |

## USAD01 - SEC insider transactions

Official SEC Insider Transactions Data Sets are quarterly flattened extracts from EDGAR Ownership XML, presented as filed. The official data library currently exposes history from January 2006 onward. Recent quarterly ZIP files are generally roughly 8-15 MB each.

Important semantics:

- raw quarterly dataset publication time is not the same as the original filing time;
- individual filing accession/acceptance time remains the preferred knowledge-time anchor when available;
- amendments must remain distinct and must not silently replace original filings;
- full filing remains primary evidence where a future analysis requires metadata absent from the flattened dataset.

Storage recommendation:

`FULL_BULK_CANDIDATE` only if a mechanical size audit confirms the entire compressed history fits the approved private GitHub storage budget without creating repository-health risk. Otherwise use targeted-universe raw filing preservation plus quarterly source-manifest hashes.

Official references:

- https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/about/privacy-information

## USAD02 - SEC 13F

SEC publishes quarterly Form 13F datasets extracted from structured EDGAR filings. Current official quarterly archives are approximately 70-95 MB each in recent periods, making a complete 2013-present binary archive a poor fit for ordinary GitHub storage.

Storage recommendation:

`TARGETED_UNIVERSE`.

For each historical quarter:

1. retrieve the official archive transiently;
2. hash the exact downloaded archive;
3. record URL, content length, retrieval time and any available response metadata;
4. extract only rows/raw filings relevant to the governed entity universe;
5. preserve the matched original filing/accession lineage;
6. store the archive-level hash/manifest even when the full bulk ZIP is not retained.

Never use quarter-end as information-availability time. Preserve filing/publication time separately.

Official references:

- https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## USAD03 - FINRA off-exchange / ATS / non-ATS

FINRA documents `weeklySummary` as a rolling 12-month production dataset and `weeklySummaryHistoric` as a rolling four-year historical dataset. Historical data older than one year is static, and FINRA explicitly advises against repeated downloads of static history.

This creates an archival urgency: the accessible historical window rolls forward and older weeks can disappear from the API window.

However, FINRA Equity API access is governed by FINRA API Terms of Service and Equity Data Specific Terms. Access uses FINRA Public/Firm/Organization credentials. Do not bypass this route by scraping licensed API material from the website.

Preflight result:

`BLOCKED_TERMS_CREDENTIAL_ACCEPTANCE` until the owner-specific FINRA access/terms path is explicitly green.

Official references:

- https://developer.finra.org/docs
- https://developer.finra.org/docs/api-explorer/query_api-equity-weekly_summary
- https://developer.finra.org/finra-api-terms-service
- https://developer.finra.org/specific-terms-equity-data

## USAD04 - FINRA short positioning

Treat two evidence families separately:

1. Reg SHO daily short-sale volume;
2. consolidated short interest.

FINRA's Reg SHO API dataset is rolling 12 months only. FINRA also publishes same-day Daily Short Sale Volume files and preserves original plus later updated versions; the consolidated NMS series is available from 2018-08-01.

A future collector should therefore use a hybrid source route rather than assuming the API alone provides complete history.

Preflight state remains blocked until the applicable FINRA terms/access route is formally resolved.

Official references:

- https://www.finra.org/finra-data/daily-short-sale-volume-transaction-data
- https://developer.finra.org/docs

## USAD05 - USAspending government contracts

USAspending's official API exposes comprehensive federal award data, currently requires no authorization, and supports bulk award/transaction ZIP/CSV generation.

A full federal spending archive would be unnecessarily large and noisy for this mission. The preferred design is a targeted legal-entity universe with exact recipient identifiers, while preserving award/modification lineage and public update timing.

Use legal entity / recipient identifiers as the primary join path. Ticker mapping is derivative and must never rewrite raw recipient identity.

Official references:

- https://api.usaspending.gov/
- https://api.usaspending.gov/docs/endpoints

## P1 observations

### USAD07 lobbying

The U.S. Senate LDA system exposes downloadable historic data and a current public query/REST route. This appears technically well suited to P1 after P0 architecture is proven.

Reference:

- https://www.senate.gov/legislative/Public_Disclosure/database_download.htm

### USAD08 patents

USPTO Open Data Portal now requires a USPTO.gov account, sign-in and MFA for ODP access. No automation or credential handling may be introduced until this is explicitly routed through the credential plane.

Reference:

- https://data.uspto.gov/apis/bulk-data/search

## Knowledge-time requirements

All future normalized records must preserve, where applicable:

- `event_time`
- `period_end_time`
- `filing_time`
- `public_availability_time`
- `retrieval_time`
- `normalization_time`

No one field may silently substitute for another. Unknown remains explicit `NULL` / `UNKNOWN`.

## Initial entity universe

Minimum seed universe:

- COIN
- HOOD
- MSTR / Strategy
- MARA
- RIOT
- CLSK
- IREN

Expansion candidates should be admitted through the versioned entity master, not hard-coded into raw records. Future RWA/stablecoin/fintech/AI/quantum entities may be added without rewriting historical raw data.

## Storage decision

Current recommendation:

- USAD01: `FULL_BULK_CANDIDATE` pending exact measured compressed-history size and repo-growth budget.
- USAD02: `TARGETED_UNIVERSE`; do not retain multi-GB full-quarter history in GitHub by default.
- USAD03: `TARGETED/HISTORIC_WINDOW_CAPTURE`, but no calls until FINRA terms/credential gate is green.
- USAD04: `HYBRID`, source-specific original/update preservation.
- USAD05: `TARGETED_UNIVERSE`.
- P1: defer until P0 architecture passes.

No paid infrastructure is authorized or required by this preflight.

## Activation boundary

This preflight does not authorize collection.

Before first USAD capture:

1. source-specific contracts must be reviewed and frozen;
2. applicable terms/access facts must be bound;
3. collector/schema/run provenance must be complete;
4. private storage/receipt paths must be validated;
5. collection activation must be a separate reviewed change;
6. scientific firewall remains `PROSPECTIVE_COLLECTION_ONLY` with hypothesis testing and outcome scoring off.

## Phase 0 verdict

```yaml
overlap_found: false
new_engine_created: false
analysis_started: false
outcome_scoring_started: false
paid_service_required: false
quiver_dependency: false
ready_for_source_contract_drafting: [USAD01, USAD02, USAD05]
blocked_pending_external_access_or_terms: [USAD03, USAD04, USAD08]
p1_after_p0: [USAD06, USAD07, USAD08]
```

Next governed step: prepare source-contract/schema/collector candidates for USAD01, USAD02 and USAD05 with all live network calls disabled until separate activation review.
