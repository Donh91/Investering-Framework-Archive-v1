# USAD v1 - Claude Cowork Gap Closure & Acquisition Readiness

**Date:** 2026-09-09  
**Status:** OPERATIONAL_HANDOFF / NO_COLLECTION_AUTHORITY  
**Purpose:** One long Claude Cowork run to close remaining identity, source-discovery, storage and acquisition-readiness gaps without duplicating existing framework work or bypassing collection governance.

## Role

Act as an independent research, data-engineering and source-acquisition challenger for the US Alternative Data Historical Vault v1.

This is not a new framework-engine project. Do not redesign the investment framework, create trading signals, calculate predictive performance, change DATA PING / Master Monday / Cycle Navigator, change portfolio permissions, or activate data collection.

Primary repositories:
- public control plane: `Donh91/Investering-Framework-Archive-v1`
- restricted data plane: `Donh91/secrets`

Do not modify the independent recovery Vault. Do not modify main branches, source activation, source governance, repository safety or backup configuration. If repository access is available, read current state first and produce reviewable files/package rather than activating anything.

## Current work already completed - do not duplicate

Read current main before beginning.

Public USAD package:
`06_RESEARCH_LAB/round3_new_information_v1/us_alternative_data/`

Already present:
- Phase 0 preflight
- machine-readable source-preflight matrix
- P0 draft source-contract candidates
- versioned entity-master seed
- P0 terms/access/retention readiness candidate

Private data-plane preparation already present:
- `schemas/usad_knowledge_time_record.schema.json`
- `collectors/collect_usad01_sec_insiders.py`
- `tests/test_usad01_sec_insiders.py`

USAD01 collector is deliberately OFFLINE ONLY. Live SEC collection is not activated. Do not remove or bypass the hard stop.

Existing P0 families:
- USAD01 SEC Forms 3/4/5 insiders
- USAD02 SEC 13F holdings
- USAD03 FINRA off-exchange
- USAD04 FINRA short positioning
- USAD05 USAspending contracts

Existing P1:
- USAD06 Congressional PTR
- USAD07 LDA lobbying
- USAD08 USPTO patents

Seed universe:
- COIN
- HOOD
- MSTR / Strategy
- MARA
- RIOT
- CLSK
- IREN

Known storage decisions:
- SEC insider quarterly archive history measured at about 879 MB compressed: use targeted universe + exact quarter ZIP SHA/bytes manifest + original EDGAR accession lineage, not all binaries in Git by default.
- SEC 13F bulk history measured at about 2.8 GB compressed: use transient official quarter ZIP retrieval + exact archive hash/bytes + targeted extraction + original filing/accession lineage.
- FINRA collection remains blocked on source-specific access/terms route.
- USAspending should use legal entity/UEI-first mapping; do not depend on legacy DUNS/D&B-derived fields unless separately cleared.
- USPTO currently has account/MFA access constraints.

## Non-negotiable temporal model

Every future observation must preserve, where applicable:
- `event_time`
- `period_end_time`
- `filing_time`
- `public_availability_time`
- `retrieval_time`
- `normalization_time`

Never silently substitute one for another. Unknown remains NULL/UNKNOWN. Do not infer public availability from transaction/event/period date.

## Autonomous execution protocol

Run this as one continuous Cowork mission.

1. Read current repository authority and USAD files first.
2. Build a concise gap ledger.
3. Research official primary sources.
4. Solve the identity/mapping blockers with source-backed evidence.
5. Red-team USAD01 engineering and provenance.
6. Audit additional official source families for incremental value.
7. Produce machine-usable CSV/JSON outputs and concise Markdown, not giant narrative reports.
8. Validate all outputs mechanically where possible.
9. Self-audit for look-ahead leakage, fuzzy entity matching, silent revisions, missing timestamps, giant-storage mistakes and duplicated framework ownership.
10. If one lane is blocked, record the blocker and continue all other lanes. Do not stop the whole mission to ask the user a question unless continuation would be unsafe.
11. Do not claim a source was scraped, archived or validated unless you actually performed and verified that operation.
12. End only after the deliverable package and unresolved-blocker ledger are complete.

## Mission A - solve the 13F identity blocker

Build the highest-integrity practical historical mapping:

CUSIP <-> security/issuer <-> SEC CIK <-> ticker history

for at minimum the seed universe.

Primary sources strongly preferred. Investigate SEC Schedule 13D/13G, issuer EDGAR filings, security descriptions and other official SEC evidence. Schedule 13D/13G is especially important because structured compliance has been required since December 18, 2024 and current XML carries issuer identity, title of class and CUSIP. Historical pre-structured filings may require a separate legacy parser/evidence class.

Do not assume one company has always had one CUSIP. Preserve security class, corporate actions, effective periods and ambiguity.

Output:
`USAD_CUSIP_ENTITY_MAP_CANDIDATE_v1.csv`

Minimum columns:
issuer_cik, legal_name, ticker, cusip, security_title, valid_from, valid_to, source_type, source_accession_or_identifier, source_url, source_publication_time, retrieval_time, confidence_class, ambiguity_note

Confidence means provenance quality, never investment confidence.

## Mission B - solve USAspending identity

Find a reproducible route from seed public companies to USAspending recipients.

Prefer legal recipient name, UEI, official recipient identifiers and source-backed parent/subsidiary relationships. Do not collapse subsidiaries into parents without explicit evidence. Do not assume ticker equals recipient.

Output:
`USAD_USASPENDING_ENTITY_MAP_CANDIDATE_v1.csv`

Minimum columns:
public_parent_cik, public_parent_name, ticker, recipient_legal_name, uei, recipient_id_if_public, parent_subsidiary_relationship, relationship_source, source_url, effective_from, effective_to, mapping_status, ambiguity_note

## Mission C - red-team USAD01

Audit the current SEC insider collector/spec for:
- amendments
- multiple reporting owners
- multiple transactions per accession
- derivative vs non-derivative transactions
- 10b5-1 metadata
- late filings
- quarter-boundary inclusion
- filing date vs EDGAR accepted timestamp
- duplicate accessions
- security-title/ticker changes
- direct vs indirect ownership
- footnote lineage
- SEC Ownership XML schema/version changes
- accession joins across all quarterly source-native tables
- deterministic source hashes and member hashes
- any path where provider values could leak into public manifests

Do not calculate whether insider transactions predict returns.

## Mission D - source expansion audit

Independently evaluate official primary source families. Start with the following, but reject any that fail marginal-value/storage/temporal-integrity tests.

### D1 SEC Schedule 13D/13G - HIGH PRIORITY
Potential use:
- >5% beneficial ownership
- activist/large-holder stake changes
- CUSIP identity bridge
- ownership-event research

Special requirement:
separate structured post-2024 handling from legacy HTML/text history. Preserve event date and EDGAR acceptance/public availability separately.

### D2 SEC Form N-PORT - HIGH PRIORITY CANDIDATE
SEC publishes monthly registered-fund portfolio holdings with official quarterly data sets from October 2019 onward. Recent full-quarter ZIPs are roughly 0.3-0.7 GB each, so full-bulk Git retention is not appropriate.

Assess whether targeted N-PORT extraction can provide materially more frequent institutional/fund ownership evidence than 13F for the seed universe. Preserve period end vs filing/acceptance/public availability. Evaluate issuer identifiers such as CUSIP/ISIN and whether N-PORT can strengthen the 13F identity bridge.

### D3 CFTC Commitments of Traders - HIGH PRIORITY CANDIDATE
Official weekly COT history is available in annual compressed files; CFTC says reports generally publish Friday 3:30pm ET using prior Tuesday positions. Historical files often encode report date, not actual release timestamp.

Assess:
- BTC/crypto-related futures venues/contracts, including current Coinbase Derivatives listings where relevant
- CME/financial-futures macro positioning
- Traders in Financial Futures
- Bank Participation and Weekly Swaps as adjacent candidates

Any future knowledge-time model must reconstruct defensible release availability and must not treat Tuesday report date as Friday-known data.

### D4 GovInfo / Federal Register - HIGH PRIORITY CANDIDATE
GovInfo exposes Federal Register XML bulk data from 2000 to present and programmatic API/bulk access.

Assess targeted event extraction for:
- SEC/CFTC crypto/RWA regulation
- stablecoin/payment regulation
- AI/semiconductor/quantum policy
- defense/strategic technology
- energy/data-center policy

Prefer document identifiers, publication dates, agencies, topics and source hashes rather than storing entire historical issues unless size analysis clearly justifies it.

### D5 SAM.gov Contract Opportunities - MEDIUM/HIGH PRIORITY
Potential pre-award government-demand signal before USAspending awards.

Current public API requires an API key and only provides the latest active version of each opportunity; archived/version history requires separate Data Services route. Investigate version/provenance feasibility before recommending collection.

### D6 SEC Form SHO - PROSPECTIVE CANDIDATE
Assess new institutional short-position/activity reporting under Form SHO / Rule 13f-2. Determine what is public, aggregated, machine-readable and historically available as of the current date. Do not assume deep history exists.

### D7 SEC Form N-PX - MEDIUM PRIORITY
Assess institutional-manager proxy voting records as a governance/activism source. Structured current filings can be very large. Evaluate targeted extraction only and compare marginal value against 13D/G, 13F and N-PORT.

### D8 Congressional PTR / LDA / USPTO
Continue existing P1 feasibility work, prioritizing official sources, temporal availability and legal access constraints.

### D9 Additional official sources
Search independently for other official U.S. federal/regulatory datasets that materially add a new information dimension. Favor SEC, CFTC, Treasury, Federal Reserve, GSA, GPO/GovInfo and other primary public authorities over aggregators.

Do not recommend a source merely because it contains a lot of data.

## Source matrix requirements

For every candidate output:
source_family, official_provider, official_url, machine_access_route, credentials_required, terms_or_license_issue, first_available_date, event_or_period_semantics, public_availability_semantics, update_cadence, estimated_history_size, largest_expected_object, revision_behavior, entity_identifiers, preferred_archive_mode, framework_overlap, incremental_value, major_risk, recommended_priority, rejection_reason_if_any

Archive mode must be one of:
FULL_BULK, TARGETED, MANIFEST_ONLY, DEFER

Priority:
P0, P1, P2, REJECT

## Mission E - storage and artifact discipline

Optimize for future questions without filling GitHub with giant binaries.

Preferred outputs:
- CSV for mappings and source inventories
- JSON for schemas, manifests and contracts
- concise Markdown for audit/reporting

Avoid XLSX, giant PDFs, giant SQLite/DB files and duplicated raw archives when CSV/JSON + immutable source lineage is sufficient.

When source bulk files are too large, preserve a reproducibility manifest containing at least source URL/identity, bytes, SHA-256, retrieval timestamp, source period/version/revision and exact extraction method.

Do not introduce paid infrastructure or commercial data purchases.

## Mission F - scrape/acquisition boundary

Do not perform broad historical scraping unless current repository authority explicitly shows that exact source contract is separately activated for collection.

A collector or draft contract is not activation.

Documentation research, metadata discovery, identity-map construction and very small technical examples needed to establish schemas are permitted.

If broad collection is not authorized, return:
`SCRAPE_STATUS: NOT_EXECUTED_GOVERNANCE_GATE`

Then provide an exact resumable/idempotent acquisition plan for execution after activation.

If there is source material the user can legally export/download manually that would unlock substantially better future research, identify the exact file/export, path and reason, but minimize manual work.

## Mission G - build activation-ready acquisition kits, not live activation

Where enough information is available, produce source-specific acquisition-kit recommendations containing:
- endpoint/download pattern
- exact user-agent/auth requirement
- pagination/version/revision behavior
- raw filename convention
- raw hash policy
- receipt fields
- dedupe key
- completeness test
- knowledge-time rule
- expected cadence
- historical backfill strategy
- prospective update strategy
- storage estimate
- fail-closed conditions

You may propose disabled collector/test code, but do not enable network collection or edit activation/governance records.

## Required deliverable package

Return a compact package containing at minimum:

1. `CLAUDE_USAD_GAP_CLOSURE_REPORT.md`
2. `USAD_CUSIP_ENTITY_MAP_CANDIDATE_v1.csv`
3. `USAD_USASPENDING_ENTITY_MAP_CANDIDATE_v1.csv`
4. `USAD_EXPANSION_SOURCE_MATRIX_v1.csv`
5. `USAD_SOURCE_EVIDENCE_MANIFEST_v1.csv`
6. `USAD_BLOCKER_LEDGER_v1.csv`
7. `USAD_ACQUISITION_PLAN_v1.csv`
8. `USAD_DELIVERABLE_MANIFEST_v1.json`
9. any small schema/contract recommendations that materially improve machine usability
10. optional disabled collector/test code only where it meaningfully closes a technical blocker

The deliverable manifest must list every produced file, SHA-256 if locally computable, purpose, source basis, whether it contains raw/provider values, and recommended destination (`PUBLIC_CONTROL_PLANE`, `RESTRICTED_DATA_PLANE`, `DO_NOT_ARCHIVE`).

## Final report structure

Keep the Markdown report concise relative to the underlying work:

- EXECUTIVE VERDICT
- WORK ACTUALLY PERFORMED
- CUSIP / 13F BLOCKER
- USAspending IDENTITY BLOCKER
- USAD01 RED TEAM
- NEW SOURCE CANDIDATES
- SOURCES REJECTED AS NOISE/OVERLAP
- TERMS / CREDENTIAL BLOCKERS
- STORAGE IMPACT
- TEMPORAL-INTEGRITY RISKS
- WHAT SHOULD BE COLLECTED FIRST AFTER ACTIVATION
- WHAT SHOULD NOT BE COLLECTED
- UNRESOLVED HUMAN DECISIONS
- SCRAPE_STATUS

## Acceptance criteria

Do not declare completion until:
- every mapping row has explicit evidence or explicit unresolved status;
- no fuzzy match is silently promoted to verified identity;
- every candidate source has availability-time semantics discussed;
- giant-source storage estimates are explicit;
- revision/amendment behavior is explicit;
- all output files are machine-readable and internally consistent;
- no outcome/performance analysis was performed;
- no live source activation occurred;
- no Quiver dependency was introduced;
- a second-pass self-audit has checked the deliverable package for hallucinated URLs, unsupported identifiers, silent timestamp inference, duplicated owners and accidental raw-value leakage.

Final principle:

> The objective is not to prove that alternative data has edge. The objective is to make future research capable of failing honestly.
