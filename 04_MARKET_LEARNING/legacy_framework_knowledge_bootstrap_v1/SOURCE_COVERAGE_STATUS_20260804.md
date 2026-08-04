# Data Ping source coverage status

Generated: 2026-08-04T16:25:00Z

Status: PARTIAL_SOURCE_DISCOVERY

## What has been reviewed

The legacy bootstrap currently uses:

- material already present in the canonical GitHub archive
- current-thread Data Ping material supplied during implementation
- compact user-context summaries available to the active ChatGPT session
- observed live Daily Director output showing that legacy hypothesis rows can be consumed as research context

## What has not been reviewed

The full set of archived ChatGPT Project conversations for Data Ping v1 through v8 has not been enumerated or read from the ChatGPT application project archive.

The active execution context does not expose a project-conversation browser, conversation index, or direct connector for reading all historical project chats. Personal-context retrieval returned only one older compressed Data Ping summary and did not expose the underlying conversations.

Therefore the bootstrap must not be described as a complete Data Ping v1-v8 extraction.

## Current evidence boundary

All existing legacy rows remain:

- RESEARCH_CONTEXT_ONLY
- canonical_evidence: false
- prospective_hit_count: 0
- candidate_freeze_allowed: false
- automatic_model_weight_change: false
- portfolio_authority: false

Rows whose source transcript is not attached must retain `SOURCE_TRANSCRIPT_NOT_YET_ATTACHED`.

## Required completion path

A complete historical extraction requires one or more of:

1. ChatGPT Project conversations exported or copied into files and uploaded for ingestion.
2. Relevant Data Ping conversations opened and their contents supplied to the active thread.
3. A future supported project-conversation connector that exposes conversation titles and message bodies.

Each ingested conversation must receive:

- stable source ID
- title and approximate date range
- content hash
- extraction receipt
- observation-to-source lineage
- duplicate and contradiction checks
- explicit separation between retrospective observations and prospective evidence

## Canonical statement

The GitHub architecture is ready to ingest the archived Data Ping conversations, but the complete ChatGPT Project archive has not yet been directly reviewed by the implementing agent.
