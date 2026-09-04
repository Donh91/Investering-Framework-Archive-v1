# Framework Memory & Operations System (FMOS) v0.2

Status: ARCHITECTURE_RATIFIED / WP-00_COMPLETE / SHADOW_BUILD_ACTIVE  
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

## Migration status

- `WP-00`: **COMPLETE** — path-level ownership, permissions, freshness and supersession registry.
- `WP-01`: **NEXT** — machine-readable object and receipt schemas.
- Later stages: capture/normalization queues, lineage/root collapse, retrieval index, graph and replay.

## Active WP-00 control objects

- `WP00_PATH_OWNER_REGISTRY_v1.md`
- `WP00_PATH_OWNER_REGISTRY_v1.json`
- `OWNER_SYSTEM_MAP_v0_1.md` retained as superseded bootstrap history.

See `ARCHITECTURE.md`, `GRAPH_AND_RETRIEVAL.md`, `AUTOMATION_TOPOLOGY.md`, `MIGRATION_PLAN.md`, and the WP-00 registry.

## Agent / next-generation model mission card

This section is **navigation only**. FMOS owners above and current machine state remain authoritative.

A repository-aware model should treat FMOS as the place to ask:

```text
Can the framework reconstruct current truth without conversation memory?
Can every important claim be traced to an immutable root?
Can current context be compressed without losing authority, time or failure semantics?
Can duplicate aliases and stale pointers be detected mechanically?
Can a fresh model discover the right owner before loading large context?
```

High-value mission seeds:

1. **Lineage/root collapse audit** - find places where many derived artifacts obscure a small number of real evidence roots.
2. **Context routing benchmark** - measure whether a fresh agent can reach the correct current owner with minimal context and zero stale-authority mistakes.
3. **Duplicate/alias compression** - detect semantically identical paths/candidates/receipts without merging distinct evidence.
4. **AS_OF replay** - verify knowledge-time reconstruction and prevent future information from leaking into historical state.
5. **Machine memory survival** - test whether the framework remains understandable after model replacement, chat loss or provider change.
6. **Ownership drift** - compare the WP-00 owner registry with actual current writers, consumers and workflow behavior.

Default authority is `READ_ONLY`.

Do not turn FMOS into a parallel framework brain, independent market authority or portfolio executor. Its value is reliable memory, routing, lineage and replay.

For Astra-class or successor-model onboarding, read:

```text
../07_PROMPTS_AND_AGENTS/astra/README.md
../07_PROMPTS_AND_AGENTS/astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json
```
