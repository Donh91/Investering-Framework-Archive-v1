# Targeted DATA PING Prompt — ETF 5 August Direct Owner Validation

```text
TARGETED ETF DIRECT-OWNER VALIDATION — BTC AND ETH 2026-08-05

REQUEST ID
DP-ETF-DIRECT-OWNER-20260806-01

PURPOSE
Resolve a material same-session conflict before any 2026-08-05 ETF value enters the owner ledger.

Two DATA PING packets both failed critical validation check INV-006 and therefore have no owner authority:

- run-20260805T232345Z-6f82 reported BTC +2.8M and ETH 0.0M;
- run-20260806T074239Z-81d4 reported BTC +244.4M and ETH +60.8M.

A Claude OTA run at 2026-08-06T07:49:36.027Z did not retrieve ETF values.

ROLE
Work only as Direct Source Collector + Table Finalization Validator + Revision Auditor + Receipt Layer.
Do not classify market regime, transmission, rotation, entry, rebuy or portfolio action.

Set:
"framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK"

REQUIRED DIRECT SOURCES
1. Farside Bitcoin ETF all-data page.
2. Farside Ethereum ETF all-data page.
3. A second independent retrieval of each page after a minimum 60-second interval.
4. If available, official issuer or exchange-source crosschecks for non-zero fund rows; use only as QA, not as replacement owner.

TARGET SESSION
2026-08-05 US trading session only.

REQUIRED EXTRACTION
For BTC and ETH separately provide:
- exact session date;
- every issuer/fund row exactly as displayed;
- total net flow;
- positive, negative, zero and dash counts;
- whether total is displayed or locally summed;
- table footer/publication date;
- retrieval timestamp UTC;
- whether the session row is final, partial, revised or unresolved;
- page/table identity;
- source URL;
- raw minimal table-row excerpt;
- raw payload or normalized row SHA-256;
- parser version.

MANDATORY CONFLICT TEST
Explicitly determine whether the earlier values +2.8M / 0.0M could have arisen from:
- a partially published table;
- dashes interpreted as zero;
- only one issuer row being available;
- delayed issuer updates;
- page cache or stale generation;
- parser truncation;
- revision after publication;
- wrong session selection.

Do not merely report the latest values. Explain the earlier-versus-later discrepancy using source evidence, or mark it UNRESOLVED.

HASH AND RECEIPT REQUIREMENTS
For every invocation and receipt:
- arguments_sha256 must be non-null;
- payload_sha256 or normalized-row sha256 must be non-null;
- one invocation must map to exactly one receipt;
- preserve error evidence hashes;
- compute the final targeted packet SHA-256 before freeze;
- no post-freeze source calls.

FAIL-CLOSED RULES
- A dash is UNKNOWN, never zero.
- Do not forward-fill 4 August values.
- Do not accept a row until both retrievals agree or a documented revision explains the difference.
- Do not average conflicting totals.
- Do not infer finality from clock time alone.
- If hashes or table identity are missing, return VALIDATION_FAILED.
- If the row remains in publication transition, return SESSION_NOT_FINAL and no owner nomination.

REQUIRED OUTPUT
1. Executive verdict.
2. BTC issuer table and total.
3. ETH issuer table and total.
4. Two-retrieval comparison.
5. Earlier-versus-later discrepancy explanation.
6. Finality and revision assessment.
7. Source-QA receipts and hashes.
8. Owner nomination decision.
9. Main-thread reconciliation package.

OWNER NOMINATION
Nominate the 2026-08-05 BTC and ETH rows only if:
- session identity is exact;
- two direct retrievals agree, or a revision chain is documented;
- dashes and zeros are distinguished;
- issuer rows tie exactly to totals;
- required hashes are present;
- packet validation passes.

MAIN-THREAD RECONCILIATION PACKAGE
For each asset provide:
- item_id
- session
- issuer_rows
- total_usd_m
- direct_or_derived
- source_url
- source_footer_date
- retrieval_1_utc
- retrieval_2_utc
- row_finality
- revision_status
- earlier_candidate_values
- discrepancy_explanation
- raw_row_sha256_1
- raw_row_sha256_2
- arguments_sha256
- payload_sha256
- packet_sha256
- owner_nomination: YES | NO
- unresolved_dependencies
- canonical_effect_claimed: NONE
- portfolio_effect_claimed: NONE
- requires_main_thread_crosscheck: YES

STOP CONDITION
Stop when both 2026-08-05 rows are owner-grade validated or explicitly classified unresolved/not final. Do not broaden into ETF market interpretation.
```
