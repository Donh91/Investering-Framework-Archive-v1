# FMOS WP-00 — Path-Level Owner Registry v1

**Status:** `COMPLETE / RATIFIED_SHADOW_CONTROL`  
**Effective date:** 2026-07-26  
**Repository baseline:** `42458ed42330eac252d26d2ad4b4d5cd97b26b42`

## Purpose

WP-00 converts the bootstrap owner map into an operational routing and authority registry. It defines, at path level, who owns each repository area, how it may be written, how fresh it must be, and how newer material may supersede older material.

The machine-readable authority is `WP00_PATH_OWNER_REGISTRY_v1.json`.

## Universal rules

1. No direct writes to `main`.
2. Every material write uses an explicit non-default task branch, PR, validation and main-branch readback.
3. `latest` does not mean `canonical`.
4. Missing data remains `UNKNOWN`.
5. Historical files are preserved unless an explicit retirement/tombstone workflow applies.
6. Frozen prospective inputs cannot be rewritten after outcomes become observable.
7. FMOS, Codex, GitHub Actions and automations have zero portfolio authority.
8. A write is successful only after `READBACK_VERIFIED`.

## Owner classes

| Owner class | Responsibility |
|---|---|
| `ARCHIVE_CONTROL` | canonical navigation, routing, precedence and discoverability |
| `FRAMEWORK_GOVERNANCE` | interpretation, permission, state and ratification |
| `DATA_PING_TRUTH_LAYER` | collection, contracts, source QA and accepted pointers |
| `WEEKLY_OPERATIONS` | Master Monday preparation and operational cadence |
| `MARKET_LEARNING` | forecast, maturity, calibration and historical learning |
| `CYCLE_NAVIGATOR` | public output and accountability |
| `RESEARCH_LAB` | shadow research and experiments |
| `AGENT_OPERATIONS` | skills, runbooks, code, tests and receipts |
| `SOURCE_MATERIAL` | raw external evidence and immutable packages |
| `ARCHIVE_INBOX` | temporary unclassified intake |
| `FMOS_CONTROL` | lineage, retrieval, replay and automation topology |

## High-authority paths

| Path | Owner | Write policy | Freshness | Supersession |
|---|---|---|---|---|
| `AGENTS.md` | Archive Control | PR-only, high safety | every agent run | replace in place; history in Git |
| `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md` | Archive Control | safepoint PR | every framework run | explicit canonical precedence |
| `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md` | Archive Control | safepoint PR | every archive run | append or explicit retirement |
| `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md` | Archive Control | safepoint PR | before routing | replacement with migration note |
| `01_CORE_FRAMEWORK/governance/**` | Framework Governance | high-safety PR | before interpretation/state change | explicit canonical decision only |
| `02_DATA_PING/operational_handoffs/latest_accepted_log_state.json` | DATA PING | transactional PR | every consumer run | advance only after acceptance |
| `02_DATA_PING/operational_handoffs/latest_decision_context_state.json` | Main Framework | transactional PR | before interpretation | ratified pointer advance |
| `02_DATA_PING/thread_handoffs/latest_thread_handover_state.json` | DATA PING | transactional PR | thread boot/replay | newer verified handover |
| `.github/workflows/**` | Agent Operations | security-reviewed PR | before automation change | tested workflow version |

## Domain routing

- `00_FMOS/**`: FMOS control objects and machine-memory architecture.
- `01_CORE_FRAMEWORK/**`: canonical framework architecture and governance.
- `02_DATA_PING/**`: collector truth layer, protocols, source QA, handovers and Data Terminal.
- `03_WEEKLY_OPERATIONS/**`: weekly operational workflows and receipts.
- `04_MARKET_LEARNING/**`: Master Monday, forecasts, maturity and derived learning.
- `05_CYCLE_NAVIGATOR/**`: public-product accountability artifacts.
- `06_RESEARCH_LAB/**`: shadow tests, experiments and prospective ledgers.
- `07_PROMPTS_AND_AGENTS/**`: skills, runbooks, implementation tasks and execution receipts.
- `08_SOURCE_MATERIAL/**`: raw source evidence, packages and hash pointers.
- `09_ARCHIVE_INBOX/**`: temporary intake requiring routing or quarantine within seven days.
- `scripts/**` and `tests/**`: deterministic implementation and validation.

## Resolution order

Every repository-first worker resolves authority in this order:

1. `AGENTS.md`
2. Canonical index
3. Addendum registry
4. Archive map and routing
5. Skill registry
6. Domain owner pointer
7. Current object
8. Historical context

Conversation memory and copied automation prompts never outrank repository authority.

## Cross-repository boundary

- `Donh91/Eksperimenter-framework-` remains the non-canonical experiment owner.
- Cycle Navigator remains separately owned; the canonical archive stores pointers and evidence unless explicit write authority is given.
- Cross-repository material cannot self-promote into canonical framework state.

## Completion decision

WP-00 is complete because the registry now contains:

- path-level ownership;
- owner classes;
- write permissions;
- freshness policies;
- supersession rules;
- resolution order;
- cross-repository boundaries;
- explicit next-stage pointer.

**Next work package:** `WP01_MACHINE_READABLE_OBJECT_AND_RECEIPT_SCHEMAS`.
