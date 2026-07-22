# Investering Framework Archive v1

Dette repository fungerer som udvidet canonical projektarkiv for Investering-frameworket.

Det er ikke kun backup.

Det er et struktureret arkiv til:

- framework-regler
- DATA PING-protokoller
- Master Monday / Weekly RAW / Canonical Backbone
- Research Lab læring
- Cycle Navigator historik
- governance og precedence
- prompt- og agentstandarder
- kilde- og researchmateriale

---

## Start here

Brug først:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
```

Derefter:

```text
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
```

Index fortæller hvad der er aktuelt canonical.

Archive map fortæller hvor nye filer skal placeres.

---

## Top-level structure

```text
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
changelog/
```

---

## Core rule

```text
Newer canonical files override older conflicting archive assumptions.
```

Older files are not automatically wrong.

They may be historical, legacy, source material or superseded.

---

## Current active operational anchor

Reconciled from the canonical runtime pointers on 2026-07-22:

```text
DATA PING V6 is the active operational feed.
Latest canonical accepted log: DATA_PING_V6_20260719T200033Z.
DATA PING V7 is prepared but not active.
Highest complete main-framework-accepted DATA PING version wins.
```

Authoritative operational pointers:

```text
02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
```

The README does not freeze current market state, recovery, rotation, gates or portfolio action. Those must be read from the latest authoritative pointers and ratified framework output.

Reconciliation receipt:

```text
changelog/2026-07-22__data-ping-runtime-archive-reconciliation-receipt.md
```

Indexed in:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
```

---

## Archive principle

```text
Raw inputs are evidence.
Distilled notes are archive.
Canonical notes are rules.
Index entries are navigation.
```

The goal is not to save everything.

The goal is to preserve what future framework runs must understand.
