# Open Questions Register v1.2

**Dato:** 2026-07-10  
**Status:** CANONICAL  
**Område:** unresolved governance / evidence gaps / operating review  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Supersedes:** Open Questions v1.1 as the active navigation layer  
**Depends on:** GPT-5.6 Fresh Eyes Audit Implementation; Rule and Evidence Registry; Active Test Registry

---

## Version note

The exact text of legacy IDs `OQ-001`, `OQ-002` and `OQ-015` was not available in the execution context used for this update.

They are therefore not falsely closed.

```text
LEGACY_OQ_001_STATUS: SOURCE_TEXT_REQUIRED
LEGACY_OQ_002_STATUS: SOURCE_TEXT_REQUIRED
LEGACY_OQ_015_STATUS: SOURCE_TEXT_REQUIRED
```

When the original v1.1 file is located, map those IDs into the current questions below and append a source-backed closure or continuation receipt.

---

## Current open questions

### OQ-12 — F12 reproducibility

```yaml
status: OPEN_CRITICAL
question: What exact source-backed inputs, windows, thresholds and state transitions make F12 independently reproducible?
blocker: ORIGINAL_SPEC_AND_THRESHOLD_PROVENANCE_INCOMPLETE
next_action: import original sources and produce versioned reactivation packet
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-12.5 — CONTESTED state exit

```yaml
status: OPEN_CRITICAL
question: What exact entry, maximum review duration and exit rules move F12.5 to DEFAULT, FALSIFIED or NOT_EVALUABLE?
blocker: SPEC_INCOMPLETE
next_action: freeze state machine before operational reuse
owner: GOVERNANCE
```

### OQ-W28-LINEAGE — Forecast source chain

```yaml
status: OPEN_CRITICAL
question: Which ratified Master Monday source produced the locked W28 Forecast Ledger?
blocker: 03_framework_ratified_final_not_accessible
next_action: locate source or create explicit ratification receipt; keep W28 unscored
owner: ARCHIVE_MASTER_MONDAY
```

### OQ-CN-TRACK — Public track-record unlock

```yaml
status: OPEN
question: When may public historical score bars and track-record language be restored?
answer_condition:
  - independently_verified_actuals
  - frozen_baselines
  - separate_range_phase_rotation_scores
  - complete_lineage
  - no_retroactive_adjustment
current_state: LOCKED
owner: CYCLE_NAVIGATOR_GOVERNANCE
```

### OQ-BTC-PARTIAL — Offensive asymmetry

```yaml
status: OPEN_NEEDS_ROWS
question: Does partial BTC permission beat WAIT on opportunity-cost-adjusted outcome without unacceptable drawdown?
blocker: 0_valid_divergence_rows_at_audit
next_action: daily timestamped divergence rows
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-FNP — Correct restraint versus genuine miss

```yaml
status: OPEN_NEEDS_ROWS
question: Which locks prevent loss and which create expensive false negatives by asset tier and regime?
blocker: insufficient_cumulative_live_rows
next_action: frozen-horizon cumulative ledger
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-PULLBACK — Reproducible classification

```yaml
status: OPEN_HIGH
question: What exact asset-specific bands, anchors and hard triggers make Pullback Policy v0.2 reproducible?
current_state: GUIDANCE_ONLY
next_action: source-backed specification or continued guidance-only status
owner: GOVERNANCE
```

### OQ-ROTATION — Multi-axis survival value

```yaml
status: OPEN_DATA_DEPENDENT
question: Does ETHBTC plus breadth, BTC.D, deployment and flow survival reduce fake rotation enough to justify the delay?
blocker: incomplete_forward_multi_axis_data
next_action: forward rows when fields are production-grade
owner: RESEARCH_LAB
```

### OQ-CONSENSUS — Multi-ping aggregation value

```yaml
status: OPEN_TEST
question: Does multi-ping aggregation reduce false flips versus latest ping alone without excessive delay?
current_authority: FEATURE_ONLY
next_action: instrument false_flip_count and delay
owner: DATA_PING_RESEARCH_LAB
```

### OQ-CHIEF — Reproducibility

```yaml
status: OPEN_TEST
question: Does the same frozen framework input produce the same action class across repeated runs?
blocker: no_reproducibility_series
next_action: repeated frozen input packets
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-LEGACY — Namespace consolidation

```yaml
status: OPEN_MEDIUM
question: Which legacy namespace files remain behaviorally relevant and need current cross-links?
current_state: legacy_namespace_read_only
next_action: classify on demand; no mass copy migration
owner: ARCHIVE
```

### OQ-TECHDEV — Claim calibration

```yaml
status: OPEN_NEEDS_ROWS
question: How accurate are TechDev roadmap, timing, range and trade claims when scored separately?
blocker: original_source_rows_not_imported
next_action: claim and revision ledger
owner: RESEARCH_LAB
```

---

## Closed by current governance

```yaml
- question: May DATA PING independently confirm recovery, rotation, rebuy or deployment?
  status: CLOSED
  answer: NO_MAIN_FRAMEWORK_OWNS_JUDGMENT

- question: May missing data be treated as negative evidence?
  status: CLOSED
  answer: NO_UNKNOWN_MAY_BLOCK_PERMISSION_BUT_IS_NOT_BEARISH_EVIDENCE

- question: May historical CN precision be marketed while reconciliation is incomplete?
  status: CLOSED
  answer: NO_PUBLIC_TRACK_RECORD_LOCKED

- question: Should new engines be added before current tests produce rows?
  status: CLOSED_UNTIL_2026_08_09
  answer: NO_NEW_ENGINE_FREEZE_ACTIVE
```

---

## Maintenance rule

Every question must end as one of:

```text
CLOSED_SOURCE_BACKED
OPEN
BLOCKED
MERGED
RETIRED
```

Do not leave questions in vague permanent review states.
