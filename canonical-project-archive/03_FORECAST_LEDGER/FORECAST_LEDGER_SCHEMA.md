# FORECAST LEDGER SCHEMA

Status: Active operational schema
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: Forecast Ledger, Weekly RAW, Master Monday, Cycle Navigator

## Executive summary

The Forecast Ledger keeps each market call accountable by separating creation, source, expectation, outcome and learning.

## Canonical fields

Minimum row fields:

- forecast_id
- created_at
- source_context
- horizon
- base_btc
- base_eth
- btc_range_low
- btc_range_high
- eth_range_low
- eth_range_high
- direction_bias
- structure_bias
- invalidation
- main_drivers
- confidence
- price_source
- outcome_status
- actual_high
- actual_low
- actual_source_status
- score_status
- miss_reason
- calibration_note

## Status values

- PENDING
- HIT
- PARTIAL
- MISS
- PRICE_UNVERIFIED
- CONFLICT
- UNRESOLVED

## Operational implication

Rows with unverified actual ranges may be logged, but should not be used for exact range precision.

## Governance notes

Keep forecast range, ping-sample range and verified actual range separate.

## Update log

- 2026-07-05: Created.