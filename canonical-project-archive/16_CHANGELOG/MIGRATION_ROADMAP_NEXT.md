# MIGRATION ROADMAP NEXT

Status: Active roadmap
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: future migration batches, Archive Sync, project continuity

## Executive summary

The archive now has enough structure and governance to support selective backfill.

The next work should avoid creating new logic unless it preserves existing framework knowledge.

## Priority 1 - historical backfill

Backfill compact summaries from existing project material into the correct folders:

- DATA PING V1-V4 lineage
- Cycle Navigator historical posts
- verified weekly actuals
- Research Lab key findings
- TechDev issue summaries
- Forecast Ledger examples

## Priority 2 - weekly operation templates

Create templates for:

- weekly RAW row
- Forecast Ledger row
- Sequence/PTR row
- source conflict row
- weekly Cycle Navigator record
- Master Monday report

## Priority 3 - archive quality control

Create:

- duplicate detection note
- deprecated file register
- archive health check template
- weekly migration QA note

## Priority 4 - secondary repos

Only after the primary archive is stable, decide how to mirror or reference:

- Donh91/Cycle-navigator-
- Donh91/Eksperimenter-framework-

## Governance notes

Do not migrate everything raw. Migrate what future runs must understand.

## Update log

- 2026-07-05: Created.