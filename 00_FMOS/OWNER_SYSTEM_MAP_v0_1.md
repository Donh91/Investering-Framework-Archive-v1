# Owner System Map — WP-00 Complete

**Status:** `SUPERSEDED_BY_WP00_PATH_OWNER_REGISTRY_v1`  
**Superseded on:** 2026-07-26

This bootstrap map has been completed and operationalized by:

- `00_FMOS/WP00_PATH_OWNER_REGISTRY_v1.md`
- `00_FMOS/WP00_PATH_OWNER_REGISTRY_v1.json`

The new registry defines path-level ownership, owner classes, write permissions, freshness policies, supersession rules, authority resolution order and cross-repository boundaries.

## Preserved bootstrap decisions

| Domain | Owner / authority location | FMOS role |
|---|---|---|
| Canonical framework archive | repository root and governance artifacts | index, preserve, retrieve |
| DATA PING | runtime/contracts and handover artifacts | capture and normalize, never interpret portfolio |
| Main framework state | main-thread handovers and accepted state artifacts | pointer and lineage |
| Master Monday | `04_MARKET_LEARNING/master_monday/` | weekly bundle and capture |
| Forecast/maturity state | forecast ledgers and handover state | maturity detection and replay |
| Source QA | source material, method receipts and conflict registries | quality graph |
| Research | `08_SOURCE_MATERIAL/` and research artifacts | A0/A1/A2 memory |
| Skill/agent runs | `07_PROMPTS_AND_AGENTS/skill_runs/` | run lineage |
| Experiments | separate experimental repository and linked archive artifacts | non-canonical routing |
| Cycle Navigator | separate repository and archived references | owner pointer, no overwrite |

Continuity remains additive. Framework reset is forbidden. DATA PING, Master Monday, Forecast Ledgers, Research Lab and Cycle Navigator retain their existing owner authority.

**Next work package:** `WP01_MACHINE_READABLE_OBJECT_AND_RECEIPT_SCHEMAS`.
