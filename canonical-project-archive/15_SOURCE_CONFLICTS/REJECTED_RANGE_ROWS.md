# REJECTED RANGE ROWS

Status: Active exclusion log
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT project memory
Applies to: Forecast Ledger, Cycle Navigator scoring, source conflict review

## Executive summary

Rejected or disputed actual range rows must be preserved as exclusions.

They must not be silently reused for scoring.

## Rejected rows

### Week 26 - 2026 - rejected message

Rejected row context:
User explicitly rejected a Week 26 range message dated 2026-06-29 08:07.

User instruction:
Se bort fra denne besked. Afvist.

Status:
Rejected. Do not use as canonical actuals.

## Governance rule

If a rejected row later appears in archive context, classify it as rejected unless the user explicitly reinstates it.

## Operational implication

Week 26 should remain pending or separately verified before exact scoring.

## Update log

- 2026-07-05: Created.