# US ALTERNATIVE DATA HISTORICAL VAULT v1 - Phase 0 Preflight

**Date:** 2026-09-09  
**Status:** SOURCE_NOTE / PREPARED_NOT_ACTIVE  
**Scope:** collection architecture, source feasibility, terms/access routing, storage preflight  
**Control plane:** `Donh91/Investering-Framework-Archive-v1`  
**Restricted data plane:** `Donh91/secrets`

## Purpose

This note records the Phase 0 preflight for the US Alternative Data Historical Vault v1 mission. It does not activate collection, create a trading signal, change DATA PING, change Round 3 scientific permissions, or authorize hypothesis testing/outcome scoring.

The design goal is to preserve what information was actually knowable at a given time, with immutable source lineage and no dependency on Quiver Quantitative or another commercial aggregator.

## Current governance binding

Current restricted collection authority remains `PROSPECTIVE_COLLECTION_ONLY`. Existing private collection is active only for the separately activated Round 3 source set. New USAD sources require their own reviewed source, terms/retention and activation path before live collection.

Raw or normalized restricted values belong only in `Donh91/secrets`. Public control-plane material may contain contracts, schemas, hashes, counts, timestamp ranges, completeness and provider-value-free health metadata.

## Overlap audit

Repository search and private raw-directory inspection found no existing USAD owner or raw source family for SEC Form 3/4/5, SEC 13F, FINRA OTC/short data, USAspending, Congressional PTR, LDA lobbying or USPTO patents.

Result: `NEW_INFORMATION`.

## Source matrix

| ID | Source family | Official source | Observed history | Archive mode | Preflight state |
|---|---|---|---|---|---|
| USAD01 | SEC Form 3/4/5 insider transactions | SEC DERA / EDGAR | Jan 2006-Jun 2026 | TARGETED_UNIVERSE + quarterly archive hash/manifest + original filing lineage | TECHNICALLY_READY_FOR_CONTRACT |
| USAD02 | SEC 13F institutional holdings | SEC DERA / EDGAR | Jul 2013-May 2026 | TARGETED_UNIVERSE + quarterly archive hash/manifest + original filing lineage | TECHNICALLY_READY_FOR_CONTRACT |
| USAD03 | FINRA ATS/non-ATS/off-exchange weekly summary | FINRA Equity API | rolling 4-year historic + rolling 12-month production | TARGETED_HISTORIC_WINDOW_CAPTURE | BLOCKED_TERMS_CREDENTIAL_ACCEPTANCE |
| USAD04 | FINRA short volume / short interest | FINRA files + Equity API | consolidated NMS daily files from 2018-08-01; API Reg SHO rolling 12 months | HYBRID_OFFICIAL_FILES_AND_API | BLOCKED_PENDING_FINRA_TERMS_ROUTE |
| USAD05 | U.S. government contracts | USAspending API | source-defined federal award history | TARGETED_UNIVERSE by legal entity/recipient identity | TECHNICALLY_READY_FOR_CONTRACT |
| USAD06 | Congressional transaction disclosures | official House/Senate disclosure systems | source-dependent | TARGETED_DISCLOSURE_ARCHIVE | P1_DISCOVERY_REQUIRED |
| USAD07 | LDA corporate lobbying | U.S. Senate LDA | official historic downloads + current route | TARGETED_UNIVERSE | P1_TECHNICALLY_PROMISING |
| USAD08 | USPTO patent activity | USPTO Open Data Portal | broad historical archive | TARGETED_UNIVERSE | P1_BLOCKED_ACCOUNT_MFA |

## Storage-size preflight

### USAD01 - SEC insider transactions

SEC exposes 82 quarterly ZIP archives from 2006 Q1 through 2026 Q2. The published compressed sizes sum to approximately **879.17 MB**, about **0.86 GiB**, before Git history overhead and future growth.

Therefore full-bulk ZIP retention in Git is rejected as the default.

Preferred design:

1. transiently retrieve the official quarterly archive;
2. hash the exact archive and record byte count, URL and retrieval metadata;
3. extract only governed-universe rows and preserve original EDGAR filing/accession lineage;
4. retain quarterly archive manifest/hash even when the full ZIP is not retained;
5. preserve amendments separately.

SEC describes these datasets as quarterly, flattened, and presented without change from the structured Forms 3, 4 and 5 submissions. The full filing remains the primary source when metadata absent from the flattened dataset matters.

Official references:

- https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces

### USAD02 - SEC 13F

SEC exposes 53 quarterly/period ZIP archives from July 2013 through May 2026. Published compressed sizes sum to approximately **2,813.79 MB**, about **2.75 GiB**, before Git history overhead and future growth.

Full-bulk retention in Git is rejected.

Preferred design:

1. retrieve each official archive transiently;
2. hash the exact archive and record URL, byte count and retrieval metadata;
3. extract only rows/original filings relevant to the governed entity universe;
4. preserve matched filing/accession lineage;
5. retain archive-level manifest/hash without retaining all multi-GB ZIP payloads.

Quarter-end is never treated as information-availability time. Filing/public availability time remains separate.

Official references:

- https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## FINRA boundary

FINRA documents `weeklySummary` as rolling 12-month production data and `weeklySummaryHistoric` as a rolling four-year historical dataset. Older static history should not be repeatedly downloaded. The rolling window creates archival urgency, but FINRA Equity API access is governed by FINRA API Terms and Equity Data Specific Terms and uses a credentialed access route.

USAD03 and the API-dependent part of USAD04 therefore remain fail-closed until the owner-specific terms/access route is explicitly green. Do not substitute website scraping.

USAD04 must also treat Reg SHO daily short-sale volume and consolidated short interest as separate evidence families. FINRA's same-day Daily Short Sale Volume files preserve original and later updated files, allowing a hybrid collection strategy.

Official references:

- https://developer.finra.org/docs
- https://developer.finra.org/docs/api-explorer/query_api-equity-weekly_summary
- https://developer.finra.org/finra-api-terms-service
- https://developer.finra.org/specific-terms-equity-data
- https://www.finra.org/finra-data/daily-short-sale-volume-transaction-data

## USAD05 - USAspending

USAspending's official API exposes federal award data without API authorization and supports bulk award/transaction download routes. Full federal spending retention would be unnecessarily large for this mission.

Preferred design: targeted legal-entity/recipient collection with award/modification lineage. Legal identity and recipient identifiers are primary; ticker mapping is derivative only.

Official references:

- https://api.usaspending.gov/
- https://api.usaspending.gov/docs/endpoints

## P1 observations

USAD07 lobbying appears technically suitable after P0, using official Senate LDA historic downloads/current query routes.

USAD08 patents remains blocked because USPTO Open Data Portal access requires account sign-in/MFA. Credentials must remain in the credential plane.

## Knowledge-time requirements

Every future normalized observation must preserve where applicable:

- `event_time`
- `period_end_time`
- `filing_time`
- `public_availability_time`
- `retrieval_time`
- `normalization_time`

No timestamp may silently substitute for another. Unknown remains explicit `NULL` / `UNKNOWN`.

## Initial entity universe

Seed universe:

- COIN
- HOOD
- MSTR / Strategy
- MARA
- RIOT
- CLSK
- IREN

Expansion must occur through the versioned entity master, never by rewriting historical raw records.

## Activation boundary

This preflight does not authorize collection.

Before first USAD capture:

1. source-specific contracts must be reviewed/frozen;
2. source-specific terms/access/retention facts must be bound;
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

Next governed step: validate the draft P0 source contracts and knowledge-time schema, then proceed only through a separate terms/retention and activation review before any live collection.
