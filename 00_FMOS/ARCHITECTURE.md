# FMOS v0.2 — Full Architecture

## 1. Architectural objective

Turn the repository estate into an auditable, replayable and queryable machine brain without losing any existing framework work.

The architecture is additive. Existing owner artifacts remain authoritative. FMOS adds immutable capture and receipts, deterministic evidence atoms, a provenance graph, conflict and supersession records, owner pointers and authority transitions, retrieval bundles, point-in-time replay, bounded automation, and calibration/learning projections.

## 2. Five planes

### Plane A — Immutable Capture
Paths: `00_FMOS/04_ingest_receipts/`, `05_raw_capture/`, `15_run_receipts/`, `16_quarantine/`, `16_dead_letter/`.
Protocol: write → readback hash verification → ACK. Failure produces `CAPTURE_UNCONFIRMED`, never a false success claim.

### Plane B — Deterministic Evidence
Paths: `06_evidence_atoms/`, `06_measurements/`, `02_source_registry/`, `03_subject_registry/`, `03_authority_registry/`.
Structured DATA PING payloads, market measurements, forecasts, settlements and source receipts are normalized by code only. Outputs must be byte-stable for the same input and method version.

### Plane C — Semantic Memory
Paths: `07_knowledge_objects/`, `08_relations/`, `09_conflicts/`, `09_supersession/`.
Knowledge Objects are projections, not the write primitive. LLM-derived objects are capped at A1_CANDIDATE and include model, prompt and extractor version. Relations are authoritative append-only edge records; in-object relations are caches only.

### Plane D — Materialized Machine Views
Paths: `10_state/`, `11_queues/`, `12_retrieval/`, `13_replay/`, `14_indexes/`, `18_graph_exports/`.
All content is rebuildable from immutable roots. Views carry source commit SHA and build receipt.

### Plane E — Governance and Owner Consumption
Paths: `03_authority_registry/`, `19_promotions/`, `20_owner_adapters/`, plus existing owner paths outside FMOS.
FMOS may propose, route and validate. Only the owning subsystem may accept or canonicalize. A4/A5 transitions require a promotion receipt and explicit governance evidence.

## 3. Orthogonal state model

Every semantic object has three separate dimensions:
- `authority_class`: A0_RAW, A1_CANDIDATE, A2_EVIDENCE, A3_OWNER_ACCEPTED, A4_CANONICAL, A5_GOVERNANCE.
- `verification_state`: UNVERIFIED, STRUCTURE_VALIDATED, SOURCE_VALIDATED, INDEPENDENTLY_REPRODUCED, CONFLICTED.
- `lifecycle_state`: ACTIVE, SUPERSEDED_FOR_USE, FROZEN, DEPRECATED, TOMBSTONED.

## 4. Temporal envelope

Required where applicable: `event_at_utc`, `published_at_utc`, `source_retrieved_at_utc`, `settled_at_utc`, `knowledge_at_utc`, `corrected_at_utc`, `decision_at_utc`.

Normative replay rule: `AS_OF(T) includes a record iff knowledge_at_utc <= T`.
Event/effective time determines what the record describes, never whether it was knowable at T.

## 5. Existing owner systems preserved

- DATA PING remains the collector standard and deterministic feature source.
- Main framework remains interpretation and decision owner.
- Master Monday remains weekly adjudication, maturity and learning cadence.
- Forecast Ledgers remain forecast identity, maturity and score owners.
- Cycle Navigator remains cycle-state owner.
- Source-QA remains source and method quality owner.
- Shadow layers remain non-binding learning layers.
- Experimental repos remain non-canonical by default.

FMOS links and retrieves these systems; it does not absorb their authority.

## 6. Repository strategy

Phase 1 uses the canonical archive repo as the single system of record. Cross-repo copies use routing records and are never independently authoritative. A separate memory-lake repo is deferred until measured Git performance or permissions require it.

## 7. Safety boundaries

CI must reject modification of append-only records, unknown authority values or subjects, imperative portfolio fields in memory objects, missing knowledge time or lineage, writes outside workflow path whitelists, authority promotion without promotion receipt, and secrets or privacy-unscreened raw captures.
