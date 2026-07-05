# DATA PING TRIGGER PROTOCOL v1.0

Status: Active operational rule
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: DATA PING, RAW, Forecast Ledger, Sequence/PTR, Master Monday

## Executive summary

Every relevant DATA PING, extended snapshot or execution snapshot should trigger silent framework processing.

Visible output should stay compact unless escalation is needed.

## Canonical content

For each relevant ping, process silently:

1. Sensor QA row.
2. RAW 1-3d row.
3. RAW 5-7d row.
4. Sequence/PTR row.
5. Source conflict row.
6. FNP diagnostic if relevant.
7. Calibration tags.
8. Master Monday eligibility note.

## Source rule

Use the highest active DATA PING version as live feed.

Current expected live feed: DATA PING V4.

Older versions are archive context unless reactivated.

## Operational implication

The user should not need to ask for RAW logging, forecast IDs, calibration or ledger updates after each ping.

## Governance notes

Do not substitute DATA PING snapshots for verified weekly actual ranges.

## Update log

- 2026-07-05: Created.