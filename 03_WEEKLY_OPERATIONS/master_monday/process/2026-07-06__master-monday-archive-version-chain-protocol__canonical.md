# Master Monday Archive Version-Chain Protocol

**Dato:** 2026-07-06  
**Status:** CANONICAL  
**Område:** Weekly Operations / Master Monday archive process  
**Primary folder:** `03_WEEKLY_OPERATIONS/master_monday/process/`  
**Related folders:** `03_WEEKLY_OPERATIONS/master_monday/`, `05_CYCLE_NAVIGATOR/weekly_posts/`, `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`  
**Supersedes:** none  
**Depends on:** `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`, `01_CORE_FRAMEWORK/engines/2026-07-05__canonical-weekly-backbone-engine-v3-framework-operating-system__canonical.md`

---

## 1. Purpose

This protocol defines how Master Monday outputs must be archived when multiple versions exist during the same weekly process.

The goal is to prevent three different outputs from being mixed together:

```text
1. System-generated Master Monday before fresh DATA PING output
2. DATA PING-derived Master Monday generated inside / after the active DATA PING thread
3. Framework-ratified final Master Monday used for Cycle Navigator and weekly evaluation
```

These are not duplicates. They are stages in the weekly decision chain.

---

## 2. Core rule

```text
Master Monday is not a single-file event.
It is a versioned weekly process.
```

Therefore the archive must preserve:

```text
PRE_DATA_PING
→ DATA_PING_DERIVED
→ FRAMEWORK_RATIFIED_FINAL
→ CYCLE_NAVIGATOR_HANDOFF
→ WEEKLY_RAW_LEARNING / BACKTEST
```

---

## 3. Folder structure

Weekly Master Monday runs should be saved in a weekly run folder:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/
```

Recommended files:

```text
01_system_generated_pre_data_ping.md
02_data_ping_derived_raw.md
03_framework_ratified_final.md
04_cycle_navigator_handoff_notes.md
```

Optional additions:

```text
05_revision_log.md
06_backtest_reference.md
```

---

## 4. Version classes

### 4.1 PRE_DATA_PING

Used for a Master Monday generated automatically before the active DATA PING thread has supplied its newest data.

```yaml
status: PRE_DATA_PING
archive_role: provisional_system_output
can_drive_cycle_navigator: false
can_drive_weekly_score: false
```

Placement:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/01_system_generated_pre_data_ping.md
```

Purpose:

```text
Preserve what the system/automation would have concluded from archive + prior verified data before latest DATA PING context.
```

---

### 4.2 DATA_PING_DERIVED

Used for a Master Monday generated in or after an active DATA PING thread.

```yaml
status: DATA_PING_DERIVED
archive_role: thread_adjusted_operational_output
can_drive_cycle_navigator: false unless later ratified
can_drive_weekly_score: false unless later ratified
```

Placement:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/02_data_ping_derived_raw.md
```

Purpose:

```text
Preserve how the newest active DATA PING changed, refined or challenged the automated/system Master Monday.
```

Important:

```text
DATA_PING_DERIVED is operationally important but not automatically final.
It must not be confused with system-generated automation output or ratified final output.
```

---

### 4.3 FRAMEWORK_RATIFIED_FINAL

Used for the final Master Monday ratified by the ChatGPT/framework governance layer after considering archive state, DATA PING, source conflicts and current operational context.

```yaml
status: FRAMEWORK_RATIFIED_FINAL
archive_role: official_weekly_working_basis
can_drive_cycle_navigator: true
can_drive_weekly_score: true
```

Placement:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/03_framework_ratified_final.md
```

Purpose:

```text
This is the official working version for Cycle Navigator, Weekly RAW Learning Snapshot, backtest references and weekly score calibration.
```

Promotion rule:

```text
A DATA_PING_DERIVED file can be promoted to FRAMEWORK_RATIFIED_FINAL only when the framework explicitly ratifies it as final.
```

---

### 4.4 CYCLE_NAVIGATOR_HANDOFF

Used when the Master Monday final state is translated into public Cycle Navigator structure, tags, visuals or post guidance.

```yaml
status: CYCLE_NAVIGATOR_HANDOFF
archive_role: bridge_to_public_output
can_drive_cycle_navigator: true
```

Placement:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/04_cycle_navigator_handoff_notes.md
```

Cycle Navigator itself should still be stored separately under:

```text
05_CYCLE_NAVIGATOR/weekly_posts/
```

The Cycle Navigator file should link back to the ratified Master Monday final:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/03_framework_ratified_final.md
```

---

## 5. Naming standard

Inside each weekly folder, use stable numbered filenames:

```text
01_system_generated_pre_data_ping.md
02_data_ping_derived_raw.md
03_framework_ratified_final.md
04_cycle_navigator_handoff_notes.md
```

Do not add random date prefixes inside the weekly folder unless multiple same-type revisions occur.

If a revision occurs, use:

```text
02_data_ping_derived_raw__rev2.md
03_framework_ratified_final__rev2.md
```

and document why in:

```text
05_revision_log.md
```

---

## 6. Status and precedence

Precedence order:

```text
FRAMEWORK_RATIFIED_FINAL
> DATA_PING_DERIVED
> PRE_DATA_PING
```

Operational rule:

```text
If a later final exists, it supersedes earlier pre-data and data-ping-derived outputs for decision purposes.
Earlier files remain historically valid as audit trail.
```

Archive status labels:

```text
PRE_DATA_PING
DATA_PING_DERIVED
FRAMEWORK_RATIFIED_FINAL
CYCLE_NAVIGATOR_HANDOFF
SUPERSEDED_BY_FINAL
```

---

## 7. What gets indexed

Add to `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md` when the file is:

```text
- this protocol
- a FRAMEWORK_RATIFIED_FINAL Master Monday
- a weekly Master Monday folder containing final decision state
- a major DATA_PING_DERIVED update that materially changed the weekly state
```

Do not index every revision unless it changes the official weekly state.

---

## 8. Relationship to DATA PING governance

DATA PING remains:

```text
NON_BINDING_DATA_COLLECTOR_ONLY
```

A Master Monday generated from DATA PING is not final just because the data was fresh.

Correct role:

```text
DATA PING supplies evidence.
ChatGPT/framework governance interprets, ratifies and classifies.
GitHub archive preserves the version chain.
```

---

## 9. Relationship to automation-generated Master Monday

The scheduled/automation-generated Master Monday should not be overwritten by later DATA PING-derived output.

Instead:

```text
System-generated output goes in 01_system_generated_pre_data_ping.md
DATA PING-derived output goes in 02_data_ping_derived_raw.md
Final ratified output goes in 03_framework_ratified_final.md
```

This preserves the difference between:

```text
What the system knew before DATA PING
vs
What DATA PING changed
vs
What the framework finally ratified
```

---

## 10. Cycle Navigator rule

Cycle Navigator must not be based directly on a PRE_DATA_PING or unratified DATA_PING_DERIVED file unless explicitly marked as provisional.

Normal path:

```text
03_framework_ratified_final.md
→ 04_cycle_navigator_handoff_notes.md
→ 05_CYCLE_NAVIGATOR/weekly_posts/YYYY-W##__cycle-navigator__post-and-calibration.md
```

---

## 11. Canonical summary

```text
Master Monday archive logic is now version-chain based. Each week should preserve pre-data system output, DATA PING-derived output, framework-ratified final output and Cycle Navigator handoff separately. DATA PING-derived Master Mondays belong under 03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/02_data_ping_derived_raw.md and must not overwrite or replace system-generated pre-data Master Mondays. Only FRAMEWORK_RATIFIED_FINAL should drive Cycle Navigator and official weekly scoring unless explicitly marked provisional.
```
