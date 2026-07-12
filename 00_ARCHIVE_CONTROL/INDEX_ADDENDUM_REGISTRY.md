# Index Addendum Registry

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_REGISTRY  
**Område:** archive discoverability / index addenda  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`

## Purpose

This registry provides a low-impact discovery layer for valid index addenda that are not yet listed directly in `CANONICAL_INDEX.md`.

It does not replace the canonical index. It prevents repository-aware agents from overlooking newer addenda merely because a direct index modification would require the high-impact safepoint workflow.

## Mandatory use

Repository-aware agents must read:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
```

before resolving current cross-domain authority.

A registry entry is a navigation pointer only. The referenced file's own status, owner, evidence class and supersession rules still determine authority.

## Active registry

| Addendum or routing anchor | Domain | Discovery status |
|---|---|---|
| `00_ARCHIVE_CONTROL/2026-07-10__index-addendum-data-ping-hybrid-edge-event-archive.md` | DATA PING / edge events | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-10__index-addendum-gpt-5-6-fresh-eyes-audit-implementation.md` | framework governance | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-1.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-2.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-3.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-10__legacy-namespace-manifest__canonical.md` | legacy routing | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-external-vault-activation.md` | backup / vault | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-investering-agent-skills-v0-1.md` | agent workflows | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-cmc-btc-d-defillama-completion-and-replay.md` | truth layer / research completion | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-full-sensor-simulation-backtest-v1.md` | full sensor backtest | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-sensor-survival-timing-placebo-regime-audit-v1.md` | sensor audit / machine improvement | REGISTRY_DISCOVERABLE |

## Registration contract

When an index addendum is created or materially updated, `archive-governance` must:

1. verify the addendum path exists;
2. verify its owner paths exist;
3. add or update exactly one row in this registry;
4. classify it as `INDEX_LISTED`, `REGISTRY_DISCOVERABLE`, `SUPERSEDED` or `BROKEN_POINTER`;
5. avoid modifying `CANONICAL_INDEX.md` unless the high-impact safepoint and vault workflow has been completed;
6. record the registry change in the pull request or skill-run receipt.

## Failure states

```text
ADDENDUM_PATH_MISSING
ADDENDUM_OWNER_MISSING
ADDENDUM_NOT_REGISTERED
ADDENDUM_DUPLICATE_ENTRY
ADDENDUM_SUPERSESSION_UNRESOLVED
```

A missing or broken addendum must not be silently treated as current authority.

## Maintenance rule

This registry is append-and-correct, not append-only in the literal sense. Existing rows may be updated when an addendum becomes index-listed, superseded or broken. Historical files remain preserved in Git history.

Direct changes to `CANONICAL_INDEX.md` remain governed by the repository high-impact safety policy.
