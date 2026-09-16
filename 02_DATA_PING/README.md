# 02_DATA_PING - Data Truth Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** DATA PING protocol history, explicit packet interpretation/replay, source QA, collector diagnostics, version governance and compatibility handoffs.

## Current production-routing notice

Binding current routing owner:

`../00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`

Manual user-submitted DATA PING is **not** the default upstream feed and is **not a prerequisite** for current Master Monday or Cycle Navigator production. Current-state CN/MM work must resolve the autonomous GitHub Actions / governed collector outputs and exact current machine pointers first.

This folder remains current for explicit DATA PING/RAW packet interpretation, replay/correction, protocol compatibility, source QA, collector diagnostics and historical lineage where DATA PING was genuinely upstream.

## Entering this folder

Do not infer the active runtime from one historical handoff or version-named file.

Resolve current state from root operational surfaces first:

```text
../LATEST_OPERATIONS_DASHBOARD.json
../LATEST_HANDOFF.json
../00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json
```

Then follow the exact current owner/pointers named by current governance and receipts. Only route into a DATA PING runtime when the task is explicitly a DATA PING/RAW task or a current pointer actually names that artifact.

Historical handoff files are intentionally preserved and may remain older than the current autonomous collector/runtime generation.

## DATA PING's job

For explicit packet/protocol work, DATA PING captures verified observations and state under its applicable contract. It does not own unrestricted interpretation or portfolio execution, and its historical/manual packet path must not be silently promoted into the normal production upstream for CN or Master Monday.

Core truth rules:

```text
MISSING != NEGATIVE
UNAVAILABLE != ZERO
STALE != CURRENT
PROXY != CANONICAL
SOURCE CALL DECLARED != SOURCE CALL EXECUTED
RECEIPT PRESENT != RECEIPT VALID
DATA_PING_IN_FILENAME != CURRENT_PRODUCTION_AUTHORITY
```

Never fabricate a source call, hash, receipt, validator result, freshness timestamp or fallback value to make a packet complete.

## High-value mission seeds

### 1. Mixed-snapshot / temporal-coherence audit

Find where a packet can combine individually valid observations that do not belong to one coherent decision-time state.

### 2. Pointer and target integrity

Audit pointer -> target -> hash -> source timestamp -> acceptance linkage, including stale/latest conflicts.

### 3. Source failure self-repair

Test whether source failures degrade honestly to `UNAVAILABLE` while preserving the best bounded fallback path, without proxy promotion or silent substitution.

### 4. Delta/unit arithmetic audit

Re-run known hard classes such as order-of-magnitude, units, percentage-point vs percent, session selection and latest-eligible calculations.

### 5. Compression without truth loss

Ask whether the collector can expose a smaller decision-ready packet while preserving complete provenance, freshness and missing-data semantics.

## Astra-class qualification challenge

A stronger model should reproduce bugs and edge cases from frozen historical packets and current runtime code rather than merely inspect prose.

Good tests include:

- stale live anchor;
- mixed snapshot state;
- BTC OI x10-type arithmetic defect;
- ETF latest-eligible session selection;
- breadth universe disagreement;
- missing/blocked source where the correct result is `UNAVAILABLE`;
- duplicate/replay behavior;
- exact current-main source binding.

Freeze expected behavior before replay where possible.

## Authority ceiling

Default mode is `READ_ONLY` or bounded replay.

Do not:

- change market thresholds;
- promote a proxy source;
- alter active DATA PING authority;
- create a new collector family because one source is inconvenient;
- backfill values without explicit canonical permission;
- turn DATA PING alone into portfolio action;
- route current CN/Master Monday through manual DATA PING merely because a historical contract or filename exists.

Code fixes later require the governed branch -> PR -> CI -> main readback path.

## Useful adjacent surfaces

```text
../00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md
../09_SOURCE_QA/README.md
../research/README.md
../07_PROMPTS_AND_AGENTS/astra/README.md
```
