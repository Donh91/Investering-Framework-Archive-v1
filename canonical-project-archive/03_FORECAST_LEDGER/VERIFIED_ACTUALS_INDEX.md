# VERIFIED ACTUALS INDEX

Status: Active index
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT project memory
Applies to: Forecast Ledger, Cycle Navigator scoring, Weekly RAW, Master Monday

## Executive summary

This index routes all verified actuals and rejected range rows.

Verified actuals are used for scoring.
Rejected or unresolved rows are preserved but not used for scoring.

## Active files

- VERIFIED_ACTUALS_SOURCE_RULES.md
- VERIFIED_WEEKLY_RANGES_2026_Q2.md
- REJECTED_RANGE_ROWS.md

## Current canonical actuals covered

- Week 23 2026
- Week 24 2026
- Week 25 2026

## Not canonical yet

- Week 26 conflicting / rejected rows
- any later weekly ranges not explicitly user verified

## Operating rule

If verified actuals are unavailable, Forecast Ledger can remain pending, but exact range scoring should not be finalized.

## Governance notes

This index should be updated whenever a new weekly actual range is verified.

## Update log

- 2026-07-05: Created.