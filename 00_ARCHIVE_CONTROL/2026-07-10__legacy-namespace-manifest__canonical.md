# Legacy Namespace Manifest

**Dato:** 2026-07-10  
**Status:** CANONICAL_ARCHIVE_CONTROL  
**Område:** archive precedence / namespace consolidation  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** Archive Map & Routing; Canonical Index; GPT-5.6 Fresh Eyes Audit Implementation

---

## Decision

```text
ACTIVE_CANONICAL_NAMESPACE:
00_ARCHIVE_CONTROL/
01_CORE_FRAMEWORK/
02_DATA_PING/
03_WEEKLY_OPERATIONS/
04_MARKET_LEARNING/
05_CYCLE_NAVIGATOR/
06_RESEARCH_LAB/
07_PROMPTS_AND_AGENTS/
08_SOURCE_MATERIAL/
09_ARCHIVE_INBOX/

LEGACY_NAMESPACE:
canonical-project-archive/

LEGACY_NAMESPACE_STATUS:
READ_ONLY_HISTORICAL_CONTEXT
```

All new canonical and operational files must use the active top-level routing structure.

No new file may be placed under `canonical-project-archive/` unless it is a migration receipt or a redirect manifest.

---

## Precedence

```text
1. New top-level canonical files referenced by CANONICAL_INDEX
2. New top-level operational registries and ledgers
3. Legacy namespace files explicitly cross-linked by a current canonical note
4. Unindexed legacy files
5. Memory-only references
```

A legacy file never overrides a newer canonical file.

---

## Migration policy

Physical migration is not required immediately.

Preferred sequence:

1. identify a legacy file that remains behaviorally relevant;
2. classify it as canonical doctrine, historical context, source note, superseded or retirement candidate;
3. create a current top-level cross-link or distilled canonical note;
4. preserve original history;
5. avoid duplicate full documents.

```text
MASS_COPY_MIGRATION: FORBIDDEN
DISTILLED_LEARNING_AND_REDIRECTS: PREFERRED
```

---

## Legacy files with known current relevance

The fresh-eyes audit identified these legacy themes as requiring current cross-links or explicit status:

- F12 ETF-default falsification;
- F12.5 contested rule;
- FNP doctrine;
- Research Lab Phase I–III distilled findings;
- Sequence Immutability;
- older Rotation Engine principles;
- historical pullback and replay material;
- TechDev source context.

Their current operational status is governed by the Rule and Evidence Registry, not by the folder name or age of the source.

---

## Weekly audit requirement

Canonical Weekly Backbone must report:

```yaml
legacy_namespace_new_writes: 0_expected
legacy_files_crosslinked_this_week:
legacy_conflicts_found:
legacy_conflicts_resolved:
legacy_files_needing_classification:
```

Any new write to the legacy namespace is `ARCHIVE_DRIFT` unless explicitly approved as a migration receipt.
