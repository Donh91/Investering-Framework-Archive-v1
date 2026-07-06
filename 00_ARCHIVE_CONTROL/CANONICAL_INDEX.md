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

### Farside ETF Flow Ledger

```text
Current canonical ETF-flow source integration as of 2026-07-06: Farside ETF Flow Ledger for DATA PING.
```

Relevant file:

```text
02_DATA_PING/source_integrations/2026-07-06__farside-etf-flow-ledger-data-ping-integration__canonical.md
```

Status:

```text
CANONICAL
```

Operational effect:

```text
Farside API is accepted as primary machine-readable ETF-flow source for DATA PING.
BTC, ETH and SOL ETF-flow must be logged as print-vs-trend ledgers.
BTC 2026-07-02 first positive print is verified, but BTC W27 trend remains negative.
ETH ETF flow is relatively stronger and near-neutral weekly.
SOL ETF flow is shadow-only selective L1 context.
Farside NAV metadata is source context only.
```

### Master Monday archive version chain

```text
Current canonical Master Monday archive process as of 2026-07-06: Master Monday Version-Chain Protocol.
```

Relevant file:

```text
03_WEEKLY_OPERATIONS/master_monday/process/2026-07-06__master-monday-archive-version-chain-protocol__canonical.md
```

Status:

```text
CANONICAL
```

Operational effect:

```text
Master Monday is archived as a weekly version chain, not one overwriteable file.
PRE_DATA_PING, DATA_PING_DERIVED, FRAMEWORK_RATIFIED_FINAL and CYCLE_NAVIGATOR_HANDOFF are separate states.
DATA PING-derived Master Mondays belong in 03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/02_data_ping_derived_raw.md.
They do not overwrite automation-generated pre-DATA-PING Master Monday files.
Only FRAMEWORK_RATIFIED_FINAL should drive Cycle Navigator and weekly scoring unless explicitly marked provisional.
```

### Cycle Navigator mobile-first visual template

```text
Current canonical Cycle Navigator image standard as of 2026-07-06: Mobile-first three-section visual template.
```

Relevant file:

```text
05_CYCLE_NAVIGATOR/templates/2026-07-06__cycle-navigator-mobile-first-image-template__canonical.md
```

Status:

```text
CANONICAL
```

Operational effect:

```text
Future Cycle Navigator weekly images should be vertical / mobile-first and iPhone-readable.
Keep only three image sections: Week Outlook, Altseason Countdown and Track Record Summary.
Remove separate Weekly Outlook and Precision Methodology panels from the image.
Preserve the established phase timeline and do not invent new actual phases.
Highlight Selective Alt Rotation as the phase to watch closely before broad altseason.
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

### 2026-07-06, Farside ETF Flow Ledger DATA PING Integration

Path:

```text
02_DATA_PING/source_integrations/2026-07-06__farside-etf-flow-ledger-data-ping-integration__canonical.md
```

Status:

```text
CANONICAL
+
DATA_PING_SOURCE_INTEGRATION
+
MASTER_MONDAY_FLOW_CALIBRATION
```

Contains:

```text
Farside API as primary machine-readable ETF-flow source
BTC ETF flow ledger with latest print, 3D/5D/7D net, weekly net and streaks
ETH ETF flow ledger with core ex-ETHE and ETHE legacy-drag split
SOL ETF flow ledger as selective L1 shadow-only sensor
Relative ETF flow snapshot for BTC vs ETH vs SOL
Farside NAV metadata classification as source context only
Holiday / zero-row / staking-fee metadata rules
Print-vs-trend status labels
Governance boundary for DATA PING and Master Monday
```

Use for:

```text
DATA PING V4+
Master Monday W28 flow calibration
RAW 1–3D and RAW 5–7D confidence
ETF-era absorption diagnostics
Early Rotation Watch diagnostics
FNP opportunity-cost visibility
Cycle Navigator calibration context
```

Operational state at archive time:

```text
BTC ETF latest print verified positive at +223.5M on 2026-07-02.
BTC W27 ETF net remains negative at -526.1M.
ETH ETF latest print positive at +29.0M and W27 near-neutral at -13.7M.
SOL W27 small positive at +5.7M, shadow-only.
ETF missing blocker removed.
Flow trend not confirmed.
Validated de-escalation candidate, not confirmed recovery or rotation.
Rebuy remains locked pending persistence.
```

---

### 2026-07-06, Master Monday Archive Version-Chain Protocol

Path:

```text
03_WEEKLY_OPERATIONS/master_monday/process/2026-07-06__master-monday-archive-version-chain-protocol__canonical.md
```

Status:

```text
CANONICAL
+
MASTER_MONDAY_ARCHIVE_PROCESS
+
WEEKLY_OPERATIONS_GOVERNANCE
```

Contains:

```text
Master Monday weekly version-chain folder structure
PRE_DATA_PING vs DATA_PING_DERIVED vs FRAMEWORK_RATIFIED_FINAL separation
Rule that DATA PING-derived Master Mondays must not overwrite system-generated pre-DATA-PING Master Mondays
Rule that final ratified Master Monday is the only normal Cycle Navigator / weekly score basis
Weekly folder standard: 03_WEEKLY_OPERATIONS/master_monday/YYYY-W##/
File standard: 01_system_generated_pre_data_ping.md, 02_data_ping_derived_raw.md, 03_framework_ratified_final.md, 04_cycle_navigator_handoff_notes.md
```

Use for:

```text
Master Monday archiving
GitHub Archive Sync
Canonical Backbone weekly run checks
Cycle Navigator handoff discipline
Weekly RAW Learning Snapshot source traceability
```

Operational effect:

```text
Master Mondays are now stored as process states, not overwritten outputs.
DATA PING-derived Master Mondays are preserved as audit/history but not automatically final.
FRAMEWORK_RATIFIED_FINAL must be explicit before Cycle Navigator uses the file as final basis.
```

---

### 2026-07-06, W28 DATA PING-derived Master Monday raw

Path:

```text
03_WEEKLY_OPERATIONS/master_monday/2026-W28/02_data_ping_derived_raw.md
```

Status:

```text
DATA_PING_DERIVED
+
OPERATIONAL_HISTORY
+
NOT_FINAL_UNLESS_PROMOTED
```

Contains:

```text
DATA PING V4-derived W28 Master Monday state
BTC 61.9K survival test passed
BTC 63.3K reclaimed intraday but no completed close above 63.3K yet
3 BTC closes above 61.9K
3 ETH/BTC closes above 0.0275
ETF print positive, trend not confirmed
24H breadth weak, 7D breadth strong
OI down while price higher
F2-watch improved, no clean F2, no rotation
```

Use for:

```text
Audit trail for how active DATA PING V4 changed W28 Master Monday
Potential source for later 03_framework_ratified_final.md
Cycle Navigator handoff only after ratification
```

---

### 2026-07-06, Cycle Navigator Mobile-First Image Template

Path:

```text
05_CYCLE_NAVIGATOR/templates/2026-07-06__cycle-navigator-mobile-first-image-template__canonical.md
```

Status:

```text
CANONICAL
+
CYCLE_NAVIGATOR_VISUAL_TEMPLATE
+
MOBILE_FIRST_STANDARD
```

Contains:

```text
Mobile-first Cycle Navigator image standard
Three required image sections only: Week Outlook, Altseason Countdown, Track Record Summary
Removal of separate Weekly Outlook and Precision Methodology panels from the image
Altseason Countdown phase-line guardrails
Selective Alt Rotation as the phase to watch closely
CN #15 reference values and future image prompt block
```

Use for:

```text
Future Cycle Navigator weekly images
Visual consistency after CN #15
Mobile/iPhone-friendly X posting
Cycle Navigator template generation
```

Operational effect:

```text
Future images should be simpler, vertical and iPhone-readable while preserving the established Cycle Navigator phase logic.
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
