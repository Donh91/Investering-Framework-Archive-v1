# 03_WEEKLY_OPERATIONS - Weekly Operations Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Master Monday, weekly backbone, range audits, automation handoffs and weekly operational continuity.

## Current production-routing notice

Binding current routing owner:

`../00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`

Current Master Monday is produced from the autonomous machine-output chain and exact current pointers exposed by the operational cockpit. Manual DATA PING submission is not an upstream prerequisite.

Historical Master Monday artifacts may contain DATA PING-derived lineage because that was correct for those frozen weeks. Do not project that historical lineage onto the current production architecture.

## Entering this folder

Start with current operational health, not historical weekly prose:

```text
../LATEST_OPERATIONS_DASHBOARD.json
../LATEST_HANDOFF.json
../00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json
../research/architecture_health/LATEST_AUTOMATION_HEALTH.json
../research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json
```

Then follow the current Master Monday / weekly pointers and exact receipts they name.

**Legacy filename trap:** `master_monday/latest_master_monday.json` is a preserved historical compatibility pointer from the older architecture. Its filename alone does not make it the current production pointer. Use it only if a current operational surface explicitly routes to it.

## What this folder should guarantee

Weekly synthesis must be reproducible from accepted evidence and must not quietly inherit stale state from a previous week.

A successful schedule is not enough. The chain should prove:

```text
correct autonomous inputs
-> exact current pointer / hash binding
-> correct time eligibility
-> deterministic/declared transforms
-> validation
-> publication
-> exact readback
-> downstream consumption
```

## High-value mission seeds

### 1. End-to-end automation chain audit

Trace scheduled trigger -> governed source owner -> generated machine artifact -> validator -> PR/merge when required -> current pointer -> consumer.

Look for green jobs that publish wrong/stale state and red jobs whose durable output actually succeeded.

### 2. Incident recurrence analysis

Cluster repeated incidents by root cause instead of counting issue files. Identify whether "new" failures are symptoms of one unresolved architecture weakness.

### 3. Weekly timing / information-set discipline

Verify that every weekly claim uses information actually available at the frozen decision time. Detect late revisions, future leakage and settlement mismatch.

### 4. Range / forecast baseline audit

Compare framework ranges and weekly forecasts against simple mechanical baselines, not only prior framework versions.

### 5. Automation simplification

Find workflows whose ownership, locks, schedules or receipts can be compressed without reducing observability or safety.

## Current-state rule

Any mission seed mentioning a current failure must be revalidated against the latest dashboard at session start. Do not preserve a stale RED or GREEN state in this README.

For current-state analysis, a historical path containing `data_ping`, `latest`, or an old week number is not current merely because it exists. Require the current routing surface to point to it.

## Authority ceiling

Default mode is `READ_ONLY`.

Do not change schedules, workflow permissions, writer topology, backup configuration or canonical weekly behavior during discovery. Workflow/security/backup changes are high-impact and must pass the current safety gates.

Do not call a workflow fixed until its required production proof and main readback exist.

## Astra-class challenge

A stronger model should be especially useful here if it can hold the entire chain in context and distinguish:

- trigger failure from producer failure;
- producer success from publication failure;
- publication success from consumer staleness;
- current autonomous production output from historical DATA PING lineage;
- current incident from historical incident residue;
- deterministic code defect from data-availability failure;
- automation health from scientific validity.

See:

```text
../00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md
../00_FMOS/README.md
../09_SOURCE_QA/README.md
../07_PROMPTS_AND_AGENTS/astra/README.md
```
