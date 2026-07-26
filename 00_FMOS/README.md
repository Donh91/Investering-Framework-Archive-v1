# Framework Memory & Operations System (FMOS) v0.2

Status: ARCHITECTURE_RATIFIED_FOR_SHADOW_BUILD  
Role: additive machine-memory, lineage, retrieval and automation substrate under the existing investment framework.  
System of record: `Donh91/Investering-Framework-Archive-v1`.

FMOS does not replace DATA PING, Master Monday, Forecast Ledgers, Cycle Navigator, source-QA, experiments, shadow layers, governance or portfolio authority. It preserves and connects them.

## Core decision

GitHub is the durable machine memory and governance substrate. ChatGPT is the reasoning and governance brain. Deterministic code performs normalization, validation, indexing and replay. LLM extraction is a versioned A1-only sidecar. Claude is an external challenger. Codex/GitHub Actions are bounded repository workers.

## v0.2 invariants

1. Existing work is never reset or silently rewritten.
2. Raw evidence and receipts are append-only except governed tombstones.
3. `latest != canonical`, `confidence != authority`.
4. Every accepted claim remains traceable to immutable L0 roots.
5. Every record carries knowledge time; AS_OF uses knowledge time, not event time.
6. Every write is read-back verified before success is claimed.
7. Derived indexes, graph views and retrieval bundles are rebuildable.
8. No FMOS worker can directly create portfolio action or canonical investment state.
9. Master Monday and DATA PING continue unchanged as owner systems.
10. GitHub is optimized for machine use; human readability is secondary but preserved where cheap.

See `ARCHITECTURE.md`, `GRAPH_AND_RETRIEVAL.md`, `AUTOMATION_TOPOLOGY.md`, and `MIGRATION_PLAN.md`.
