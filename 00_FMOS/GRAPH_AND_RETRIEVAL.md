# FMOS v0.2 — Knowledge Graph and Retrieval

## 1. Graph purpose

The graph is the framework's navigable memory: a machine index for lineage, contradiction, replay, calibration and context assembly.

## 2. Node families

RAW_CAPTURE, SOURCE_RECEIPT, MEASUREMENT, EVIDENCE_ATOM, FORECAST, OUTCOME, KNOWLEDGE_OBJECT, METHOD, SOURCE, SUBJECT, CONFLICT_SET, GOVERNANCE_DECISION, OWNER_ARTIFACT, RUN, RETRIEVAL_BUNDLE, CALIBRATION_RESULT.

## 3. Edge types

Typed and append-only: DERIVED_FROM, OBSERVED_IN, PRODUCED_BY, SUPPORTS, CONTRADICTS, DUPLICATES, ALIASES, TESTS, MATURES_AT, SCORED_BY, SUPERSEDES_FOR_USE, ANNOTATES, ROUTED_TO, ACCEPTED_BY, CANONICALIZED_BY, CONFOUNDED_BY, DEPENDS_ON, CORRECTS, SETTLES.

Each edge has `knowledge_at_utc`, `produced_by_run_id`, source and target IDs, and optional valid-time scope.

## 4. Root ancestry

Every derived object carries transitive `l0_root_ids`. Evidence counts use distinct roots, not object count. This prevents one Data Ping or one model statement from becoming many pseudo-independent confirmations.

Retrieval partitions:
- EXTERNAL_MEASUREMENT
- OWNER_ACCEPTED
- MODEL_ANALYSIS
- MODEL_SELF
- OPEN_CONFLICT
- NEGATIVE_EVIDENCE
- MISSING_CONTEXT

`MODEL_SELF` never counts as independent support.

## 5. Retrieval modes

CURRENT_STATE, AS_OF, SUBJECT, EVENT_WINDOW, CONTRADICTION, BACKTEST, AUDIT, MASTER_MONDAY, DATA_PING_HANDOVER, PORTFOLIO_CONTEXT.

Bundles must include request and cutoff, source commit SHA, owner pointers with file hash, authority summary, open conflicts, negative evidence, omitted-due-to-budget, freshness/degraded state, root-deduplicated evidence and bundle hash.

## 6. Retrieval ranking

Hard filters first: authority, knowledge time, subject registry, owner scope and settlement state. Then deterministic ranking: authority → conflict relevance → recency → source quality → root diversity.

Semantic/vector retrieval is deferred until measured misses exceed a defined threshold. Hybrid retrieval may be added later, never as the only retrieval method.

## 7. Graph materialization

Authoritative graph = append-only edge records. Derived outputs include JSON adjacency indexes, subject pages, conflict maps, GraphML export, Mermaid summaries, owner dependency maps and replay snapshots. All derived graph products are disposable and rebuildable.
