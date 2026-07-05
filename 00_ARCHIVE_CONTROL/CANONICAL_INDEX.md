# Canonical Archive Index

**Dato:** 2026-07-05  
**Status:** Canonical archive control  
**Formål:** Hurtig oversigt over aktuelle canonical eller operationelt vigtige arkivfiler.

---

## How to use this index

This file is the navigation layer.

Use it to find the latest operative rule before relying on older archive files.

Rule:

```text
If a newer canonical file conflicts with an older archive file, the newer canonical file wins.
```

---

## Current live operational anchors

### DATA PING live feed

```text
Highest active DATA PING version wins.
Current active feed as of 2026-07-05: DATA PING V4.
```

Relevant file:

```text
changelog/2026-07-05_framework_operations_update_data_ping_v4_shadow_macro.md
```

Status:

```text
CANONICAL_ARCHIVE
```

Primary domain:

```text
03_WEEKLY_OPERATIONS/operations_updates
```

Secondary domains:

```text
02_DATA_PING/protocols
04_MARKET_LEARNING/recovery_attempts
04_MARKET_LEARNING/macro_shadow
05_CYCLE_NAVIGATOR/templates
```

### Canonical Backbone engine

```text
Current canonical engine as of 2026-07-05: Canonical Weekly Backbone Engine v3.0.
CWB v2.1 remains LEGACY_FALLBACK.
```

Relevant file:

```text
01_CORE_FRAMEWORK/engines/2026-07-05__canonical-weekly-backbone-engine-v3-framework-operating-system__canonical.md
```

Status:

```text
CANONICAL
```

Operational effect:

```text
GitHub-first Framework Operating System.
CANONICAL_INDEX.md is read first.
Highest active DATA PING version is discovered automatically.
Shadow rows must be checked or explicitly marked inaccessible.
Every weekly run must include VERSION_UPGRADE_DIAGNOSTIC and ARCHIVE_RECOMMENDATION.
```

---

## 2026-07 entries

### 2026-07-05, DATA PING V4 + Shadow Ledger + Macro Ops Update

Path:

```text
changelog/2026-07-05_framework_operations_update_data_ping_v4_shadow_macro.md
```

Status:

```text
CANONICAL_ARCHIVE
+
WEEKLY_LEARNING
+
GOVERNANCE_OPERATIONS_UPDATE
```

Contains:

```text
DATA PING V4 Sensor Discipline Doctrine
Recovery Attempt Quality Doctrine
GeckoTerminal / DEX shadow-only rule
FRED targeted-series rule
Grok role governance
Breadth hierarchy
FNP / opportunity-cost status
Shadow Ledger Automation Patch
DATA PING Trigger Protocol v0.1 handover
Cycle Navigator staged rotation language
Master Monday must-read notes
Current operational state
```

Use for:

```text
Master Monday
Weekly RAW Learning Snapshot
Canonical Backbone
GitHub Archive Sync
Auto Stabilizer
DATA PING V5+ handover
Cycle Navigator calibration
```

Operational state at archive time:

```text
Recovery-attempt alive.
Quality fragile.
No chase.
No rebuy.
No confirmed rotation.
Keep logging.
```

---

### 2026-07-05, FRED Classic Targeted Series Production Upgrade

Path:

```text
04_MARKET_LEARNING/macro_shadow/2026-07-05__fred-classic-targeted-series-production-upgrade__canonical.md
```

Status:

```text
CANONICAL
```

Contains:

```text
FRED Classic v1.2 targeted-series production status
FRED_MACRO_STATUS = BACKTEST_READY_FULL
43/43 observations PASS
5/5 metadata PASS
8/8 vintage/backtest PASS
FRED Bulk = discovery only
FRED Targeted Series = production macro context
FRED Vintage = backtest integrity layer
Macro Shadow digest and boundary rules
```

Use for:

```text
Master Monday macro calibration
Weekly RAW macro context
Research Lab historical replay
Point-in-time backtest control
Macro Shadow Layer
```

Boundary:

```text
FRED Macro context cannot determine recovery, rotation, rebuy, deployment, official row or FNP/PATH alone.
```

---

### 2026-07-05, Canonical Weekly Backbone Engine v3.0

Path:

```text
01_CORE_FRAMEWORK/engines/2026-07-05__canonical-weekly-backbone-engine-v3-framework-operating-system__canonical.md
```

Status:

```text
CANONICAL
```

Contains:

```text
GitHub-first Framework Operating System
CANONICAL_INDEX.md-first rule
Highest active DATA PING discovery
DATA PING TRIGGER PROTOCOL v0.1 shadow ingestion
Repository completeness scoring
Run-status logic: AUTO_PASS / MANUAL_BACKFILL_PASS / BLOCKED
Adaptive weekly VERSION_UPGRADE_DIAGNOSTIC
Canonical Learning Queue
Archive recommendation rule
CWB v2.1 = LEGACY_FALLBACK
CWB v3.0 = CANONICAL_CURRENT when GitHub connector access exists
```

Use for:

```text
Canonical Backbone
Master Monday readiness
Weekly RAW Learning Snapshot
GitHub Archive Sync
Auto Stabilizer
DATA PING V5+ handover
Framework version governance
```

Operational rule:

```text
Read GitHub first when access exists.
Use CANONICAL_INDEX.md as the navigation layer.
Use highest active DATA PING version.
Do not silently ignore shadow rows.
Do not score unverified ranges.
Always end with version-upgrade diagnostic and archive recommendation.
```

---

## Folder map

Full routing rules:

```text
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
```

---

## Placement rule for future updates

### Governance / framework-wide rules

Place in:

```text
01_CORE_FRAMEWORK/governance/
```

Examples:

```text
F12
F12.5
FNP
Kill Criteria
Research Lab governance
Precedence maps
```

### DATA PING behavior

Place in:

```text
02_DATA_PING/
```

Examples:

```text
DATA PING Trigger Protocol
Version governance
Source QA
Custom GPT patches
Sensor rules
```

### Weekly operations

Place in:

```text
03_WEEKLY_OPERATIONS/
```

Examples:

```text
Master Monday
Weekly RAW
Canonical Backbone
Automation patches
Operations updates
Verified range audits
```

### Market learning

Place in:

```text
04_MARKET_LEARNING/
```

Examples:

```text
ETF-era absorption
Recovery Attempt Quality
Rotation survival
Stress / flush learning
FRED macro shadow
FNP opportunity-cost learning
```

### Cycle Navigator

Place in:

```text
05_CYCLE_NAVIGATOR/
```

Examples:

```text
Weekly posts
Visual templates
Altseason language
Precision score calibration
Checkpoints
```

### Research Lab

Place in:

```text
06_RESEARCH_LAB/
```

Examples:

```text
Claude / Grok audit summaries
Historical replay summaries
Forward tests
Red-team outputs
```

### Prompts and agents

Place in:

```text
07_PROMPTS_AND_AGENTS/
```

Examples:

```text
Claude prompt standards
Custom GPT prompt patches
GitHub archive agent prompts
Research Lab prompt templates
```

### Source material

Place in:

```text
08_SOURCE_MATERIAL/
```

Examples:

```text
TechDev source notes
CoinGecko reports
FRED references
Glassnode notes
Screenshots / external evidence
```

### Unclear

Place temporarily in:

```text
09_ARCHIVE_INBOX/to_classify/
```

---

## Index maintenance rule

Add a file to this index if it is:

- canonical
- operationally important
- governance relevant
- used by Master Monday
- used by DATA PING
- used by Cycle Navigator
- used by Research Lab
- a major weekly learning update

Do not index every source note.

---

## Archive health note

The archive should stay useful.

Avoid archive inflation.

Preferred pattern:

```text
Many raw inputs
→ one distilled canonical note
→ index entry
```

Not:

```text
Every chat output
→ canonical source
```
