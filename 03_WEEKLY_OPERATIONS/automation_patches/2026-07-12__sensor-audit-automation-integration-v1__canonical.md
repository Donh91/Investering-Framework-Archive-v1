# Sensor Audit Automation Integration v1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** weekly operations / automation prompts / sensor governance  
**Primary folder:** `03_WEEKLY_OPERATIONS/automation_patches/`  
**Depends on:** `06_RESEARCH_LAB/audit_summaries/2026-07-12__sensor-survival-timing-placebo-regime-audit-v1__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-12__sensor-role-and-m1-evaluation-integrity-patch-v1__canonical.md`, `.agents/skills/prospective-evidence-ledger/SKILL.md`

## Purpose

Integrate the completed Sensor Survival Audit into the three active weekly automations without creating a new automation, engine, test or score.

## Automation receipts

### Sunday Closeout

```yaml
automation_id: 69cfb90fa3688191922260e436115c30
version: SUNDAY_CLOSEOUT_v1_3
schedule_changed: NO
status: ENABLED
updated_at_utc: 2026-07-12T14:46:35Z
```

Added:

- mandatory `INDEX_ADDENDUM_REGISTRY` discovery;
- prospective-evidence-ledger validation before row creation/maturity/rejection;
- A1/A2 urgency, A3 quarantine, C warning and D confirmation/veto role separation;
- no A/C/D blended score;
- C2 forward instrumentation under existing Pullback Edge lineage;
- event denominator and one-to-one/non-overlapping attribution fields;
- source and operational-availability timestamps;
- stablecoin availability/activity axis compression;
- T3/T6 breadth-blocked status;
- explicit drift checks for role reactivation and activity double-counting.

### Master Monday

```yaml
automation_id: 697fcc899f0481918e3cedbd396a3520
version: MASTER_MONDAY_vNext_v1_1
schedule_changed: NO
status: ENABLED
updated_at_utc: 2026-07-12T14:47:21Z
```

Added:

- registered-addendum startup order;
- same sensor-role freeze and denominator/attribution integrity;
- C2 forward-row status and A3 quarantine audit;
- BTC.D 21-versus-22 reproducibility conflict preservation;
- one stablecoin activity family instead of duplicate confirmation;
- frozen-universe breadth blocker reporting;
- prospective evidence validity/maturity/coverage separation.

### GitHub Archive Sync + Backup

```yaml
automation_id: 6a496f6abda881919cd69454adef01fb
version: GITHUB_ARCHIVE_SYNC_BACKUP_v1_5
schedule_changed: NO
status: ENABLED
updated_at_utc: 2026-07-12T14:48:07Z
```

Added:

- `AGENTS.md`, `INDEX_ADDENDUM_REGISTRY` and registered addenda as mandatory startup sources;
- Skill-receipt and prospective-evidence-integrity checks;
- sensor-governance drift checks;
- registered addenda included in 4/4 frozen-SHA snapshots;
- explicit targeted-research-snapshot contract;
- no weekly-counter increment from out-of-cycle targeted snapshots.

## Machine effect

```text
NEW_AUTOMATION: NO
SCHEDULE_CHANGE: NO
NEW_ENGINE: NO
NEW_TEST: NO
NEW_SCORE: NO
LIVE_THRESHOLD_CHANGE: NO
PORTFOLIO_AUTHORITY_CHANGE: NO
```

The change improves future evidence collection and archive discoverability. It does not convert retrospective audit results into forward rows and does not promote C2 or any other sensor.

## Drift conditions now monitored

```text
A3 live severity escalation
D treated as prediction
A/C/D blended scoring
BTC.D B1 warning/trim reactivation
stablecoin activity double-counting
missing operational latency timestamps
missing denominator or overlapping attribution
stale T3/T6 blocker labels
retrospective evidence represented as prospective
registered addendum omitted from startup
```
