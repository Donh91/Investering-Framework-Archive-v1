# SOURCE CONFLICT PROTOCOL

Status: Active operational protocol
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: DATA PING, verified actuals, Forecast Ledger, Master Monday

## Executive summary

Source conflicts must be preserved, classified and resolved explicitly.

They must not be hidden by choosing the most convenient source.

## Conflict types

- price conflict
- range conflict
- version conflict
- timing conflict
- interpretation conflict
- source freshness conflict

## Resolution order

1. User-verified actuals.
2. Verified source-specific data pull.
3. Highest active DATA PING for live context.
4. Canonical archive rules.
5. Historical archive context.

## Operational implication

If unresolved, mark the row as CONFLICT or PRICE_UNVERIFIED.

## Governance notes

Do not score exact ranges from unresolved source conflict data.

## Update log

- 2026-07-05: Created.