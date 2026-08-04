# Legacy archive intake controls v1

Status: ACTIVE_RESEARCH_ONLY
Authority: NONE
Canonical evidence: NO

This note preserves only the framework-specific controls extracted from the reviewed archive-export method report. The source report contains no actual Data Ping conversations, run history, market observations, decisions, errors or handovers and must not be treated as a historical export.

## Accepted controls

1. Preserve original run IDs exactly. Missing run IDs do not justify dropping a source record.
2. Preserve normalized timestamps and the original date string when available. Invalid or uncertain dates remain null or explicitly uncertain, never invented.
3. Raw ChatGPT exports remain outside the public repository. Public GitHub receives only sanitized structured observations, source hashes and intake receipts.
4. Every ingested conversation receives a stable source ID, source hash, extraction receipt and observation-to-message lineage.
5. Contradictory claims are retained as separate records. Later claims may supersede earlier claims only through an explicit relation, not silent reconciliation.
6. Uncertain records enter a review queue. Unsafe, irrelevant or unparsable records receive a rejection reason without publishing sensitive source text.
7. Extraction output must be deterministically ordered and integrity-checkable from the same source snapshot.
8. Structured findings are an index over source material, not a replacement for provenance. Where the raw source cannot be published, the receipt and message-level lineage must preserve auditability.

## Explicit exclusions

The following parts of the source report are not adopted into the bootstrap:

- the proposed large generic conversation-export JSON schema
- the synthetic example conversation
- arbitrary relevance weights and score threshold
- generic GitHub workflow, CODEOWNERS and PR-template guidance
- illustrative file-size plans and project timelines
- legal or platform summaries not derived from framework history

These exclusions prevent a method proposal from being mistaken for recovered Data Ping knowledge or from duplicating existing FMOS delivery controls.

## Intake classification

The source is classified as `METHOD_PROPOSAL_ONLY` and contributes zero historical observations, zero prospective evidence and zero framework authority.
