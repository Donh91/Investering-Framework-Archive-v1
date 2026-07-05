# CYCLE NAVIGATOR FULL TEXT BACKFILL QUEUE

Status: Active backfill queue
Date added: 2026-07-05
Applies to: Cycle Navigator historical post archive

## Purpose

Track which final Cycle Navigator X posts still need full raw text import into GitHub.

## Backfilled as records

- CN #9: final post record created.
- CN #11: final post record created.

## Source verified but raw import pending

- CN #1-#8: source summary exists, individual full text pending extraction.
- CN #10: final full text pending extraction.
- CN #12: source verified, compact record blocked by tool safety, needs smaller chunk import later.
- 8 Week Checkpoint: source verified, full checkpoint pending.

## Import method

Use one file per post when accepted.
If blocked, split into smaller chunks:

- metadata
- precision section
- market state section
- outlook section
- action/compass section
- model evaluation section
- key takeaway section

## Rule

Do not rewrite old posts during import.
Do not update old scores.
Preserve final version as found in project archive.

## Update log

- 2026-07-05: Created.