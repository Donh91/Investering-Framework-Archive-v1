# VERIFIED ACTUALS SOURCE RULES

Status: Active operational rule
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT project memory
Applies to: Forecast Ledger, Weekly RAW, Cycle Navigator, Master Monday

## Executive summary

Verified actuals are the scoring ground truth for weekly range evaluation.

DATA PING snapshots can support live context, but they are not verified weekly actual ranges.

## Source priority

Use this order:

1. User-verified actual range rows.
2. Source-specific historical OHLC pull reviewed by the user.
3. Consistent CoinGecko or Yahoo Finance range check.
4. DATA PING snapshot context, marked non-verified.
5. External commentary, never as exact actual range by itself.

## Canonical rule

Do not score exact range precision from unresolved source conflicts.

If actual data is missing or conflicting, mark:

- PRICE_UNVERIFIED
- CONFLICT
- PENDING_VERIFICATION

## Operational implication

Forecast Ledger and Cycle Navigator scoring must distinguish forecast range, ping sample range and verified actual range.

## Governance notes

Rejected actual rows must be preserved as rejected, not silently reused.

## Update log

- 2026-07-05: Created.