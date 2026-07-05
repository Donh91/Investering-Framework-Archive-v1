# PUBLISHED X POST INGESTION PROTOCOL

Status: Active protocol
Date added: 2026-07-05

## Rule

When the user provides a Cycle Navigator post that was published on X, save it in this folder as the published record.

## Steps

1. Identify CN number.
2. Identify date or week range.
3. Preserve text as provided.
4. Add metadata header.
5. Save one file per post.
6. Add register entry.

## Missing info

If date or CN number is unclear, mark unknown and preserve the text.

## Blocked raw import

If a long post cannot be written, create a metadata record and add it to retry queue.

## Rule

Do not rewrite published posts.
Corrections belong in separate notes.

## Update log

- 2026-07-05: Created.