# FMOS v0.2 — Automation Topology

## 1. Principle

No monolithic agent. Work is decomposed into small workflows with one responsibility, explicit budgets, receipts and failure isolation.

## 2. Event-time workflows

### Capture Adapter
Input: current framework turn or artifact. Output: ingest receipt + raw capture + readback ACK. No semantic interpretation.

### DATA PING Normalizer
Input: accepted DATA PING packet. Output: deterministic measurements/evidence atoms and lineage. No portfolio interpretation.

## 3. Daily workflows

1. Capture reconciler
2. Schema and secret validator
3. Deterministic normalizer
4. Subject/alias validator
5. Relation builder
6. Maturity detector
7. Queue health and backlog SLO
8. Retrieval index incremental rebuild

Priority: DATA_PING > GOVERNANCE > MASTER_MONDAY > RESEARCH > OTHER.

## 4. Weekly workflows

Run before/around Master Monday in precedence order:
1. receipt completeness;
2. orphan and lineage audit;
3. duplicate/root collapse;
4. conflict and supersession audit;
5. forecast maturity/scoring workpack preparation;
6. source-QA drift report;
7. replay manifest build;
8. retrieval quality evaluation;
9. graph/index full rebuild;
10. archive and backup verification.

Each workflow creates its own run receipt and PR. Failure in one does not suppress the others.

## 5. Master Monday integration

Master Monday continues as the weekly owner cadence. FMOS supplies a bounded bundle containing current canonical pointers, matured forecasts awaiting adjudication, unresolved conflicts, source/method drift, calibration deltas, missing evidence and prior-week decision lineage.

Master Monday output is captured as governance evidence and linked back to every affected forecast, method and state object.

## 6. State machine

Receipts: `QUEUED → IN_PR → MERGED → READBACK_VERIFIED → DONE`.
Other terminal states: `QUARANTINED`, `DEAD_LETTER`, `TOMBSTONED`, `CANCELLED_BY_GOVERNANCE`.
Only READBACK_VERIFIED is success.

## 7. Runtime allocation

- GitHub Actions: deterministic validation, normalization, indexing, graph builds and replay tests.
- Codex: bounded repository changes, repair PRs and structured workpacks.
- ChatGPT: architecture, governance, interpretation and final owner routing.
- Claude: opt-in challenger/auditor, never automatic authority.

Scheduled ChatGPT tasks are not relied on for arbitrary project-file or thread ingestion.
