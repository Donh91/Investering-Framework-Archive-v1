# 00_ARCHIVE_CONTROL - Authority & Routing Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Resolve what is current, where material belongs, which source wins, and how agents cross repository boundaries.

## Read first

```text
CANONICAL_INDEX.md
INDEX_ADDENDUM_REGISTRY.md
ARCHIVE_MAP_AND_ROUTING.md
CROSS_REPO_DATA_BOUNDARY.md
CROSS_REPO_AGENT_CONTEXT_MAP.json
SKILL_REGISTRY.md
```

Then resolve the current owner/status files referenced by those surfaces.

## What a capable model should notice here

This folder is not a library of equally authoritative documents. It is a precedence and routing layer.

A strong agent should actively look for:

- canonical owners that are not discoverable;
- discoverable files whose own status is legacy/superseded;
- stale navigation prose that conflicts with current machine state;
- duplicate or competing owners;
- pointer -> target mismatches;
- cross-repository authority leaks;
- public references that accidentally imply private-data authority;
- archive routes that no longer match the actual repository topology;
- index/addendum drift;
- files named `LATEST` that are being treated as truth without a governing contract.

## High-value mission seed

```text
AUTHORITY_AND_CONTRADICTION_AUDIT
```

Reconstruct a graph of current authority from canonical index, addendum registry, machine routing, owner files and live pointers. Find contradictions, unreachable owners, stale routes and duplicate authority.

Do not fix them during the discovery pass.

Required first-pass result:

```yaml
current_authority_graph:
unreachable_current_owners:
stale_navigation:
duplicate_authority_candidates:
pointer_target_conflicts:
cross_repo_boundary_risks:
recommended_repairs:
confidence_and_unresolved:
```

## Authority ceiling

Default mode is `READ_ONLY`.

Do not change canonical index, archive routing, precedence or source governance merely because a cleaner structure is imaginable. Those changes are high-impact and require the active safepoint / recovery sequence plus explicit write authority.

## Astra / successor-model challenge

If you are a higher-capability model, do not simply validate the existing archive design. Ask whether the routing system still minimizes context load and contradiction risk at current repository scale.

Propose a simpler authority-resolution architecture only if you can demonstrate lower ambiguity without creating a second source of truth.

See:

```text
07_PROMPTS_AND_AGENTS/astra/README.md
07_PROMPTS_AND_AGENTS/astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json
```
