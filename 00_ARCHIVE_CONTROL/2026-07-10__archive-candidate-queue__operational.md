# Archive Candidate Queue — 2026-07-10

**Dato:** 2026-07-10  
**Status:** OPERATIONAL_PENDING_QUEUE  
**Område:** archive control / unresolved candidates / weekly reconciliation  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** Canonical Weekly Backbone Edge Event Archive Reconciliation Addendum; GPT-5.6 Fresh Eyes Audit Implementation

---

## Queue state

```text
PROCESSED_ITEMS_PRESENT: NO
ONLY_UNRESOLVED_ITEMS_REMAIN: YES
PROCESSED_HISTORY_LOCATION:
- changelog/2026-07-10__canonical-archive-audit-data-ping-edge-event.md
- changelog/2026-07-10__gpt-5-6-fresh-eyes-audit-implementation-receipt.md
```

---

## A. Active edge-event candidates

### A1. Canonical first WATCH anchor

```yaml
archive_class: RUNTIME_CONFIG
edge_event_id: PULLBACK_EDGE_20260708_01
status: PENDING
field: canonical_first_watch_time
blocker: EXACT_FRAMEWORK_ACCEPTED_ANCHOR_NOT_ESTABLISHED
action: SEARCH_EARLIER_SOURCE_BACKED_RUNS_THEN_MAIN_FRAMEWORK_ACCEPT
```

### A2. Canonical first NEAR_PRESENT anchor

```yaml
archive_class: RUNTIME_CONFIG
edge_event_id: PULLBACK_EDGE_20260708_01
status: PENDING_EARLIER_HISTORY_CHECK
earliest_source_backed_candidate_time: 2026-07-08T11:15:00Z
earliest_source_backed_candidate_run: DATA_PING_V4_20260708T111500Z
blocker: CANDIDATE_NOT_CANONICAL_FIRST_WITHOUT_EARLIER_HISTORY_CHECK_AND_FRAMEWORK_ACCEPTANCE
action: RETAIN_CANDIDATE_WITHOUT_PROMOTION
```

### A3. 72H outcome

```yaml
archive_class: CALIBRATION
edge_event_id: PULLBACK_EDGE_20260708_01
status: PENDING
maturity_time: 2026-07-11T14:03:00Z
action: APPEND_WHEN_MATURED
```

### A4. 7D outcome

```yaml
archive_class: CALIBRATION
edge_event_id: PULLBACK_EDGE_20260708_01
status: PENDING
maturity_time: 2026-07-15T14:03:00Z
action: APPEND_WHEN_MATURED
```

### A5. Event close row

```yaml
archive_class: CALIBRATION
edge_event_id: PULLBACK_EDGE_20260708_01
status: PENDING_MAIN_FRAMEWORK
action: APPEND_AFTER_FORMAL_EVENT_CLOSE
```

### A6. Final framework learning

```yaml
archive_class: WEEKLY_LEARNING
edge_event_id: PULLBACK_EDGE_20260708_01
status: PROVISIONAL_NOT_PROMOTED
candidate_learning:
  market_stress_detection: MAY_HAVE_VALUE
  tactical_trim_execution: PROVISIONALLY_WEAK
blocker: 72H_7D_AND_EVENT_CLOSE_NOT_COMPLETE
action: MAIN_FRAMEWORK_REVIEW_AFTER_MATURITY
```

---

## B. Fresh-eyes governance and lineage candidates

### B1. W28 Forecast Ledger source repair

```yaml
archive_class: LINEAGE
status: OPEN_CRITICAL
current_correction: 03_WEEKLY_OPERATIONS/master_monday/2026-W28/05_forecast-ledger-lineage-correction.md
blocker: RATIFIED_MASTER_MONDAY_SOURCE_NOT_LOCATED
action: LOCATE_SOURCE_OR_CREATE_EXPLICIT_RATIFICATION_RECEIPT
scoring_status: BLOCKED
```

### B2. F12 reproducibility packet

```yaml
archive_class: CANONICAL_RULE
status: SPEC_INCOMPLETE
current_correction: 01_CORE_FRAMEWORK/governance/2026-07-10__f12-f12-5-reproducibility-freeze__canonical.md
blocker: ORIGINAL_THRESHOLDS_WINDOWS_AND_STATE_TRANSITIONS_NOT_IMPORTED
action: IMPORT_SOURCE_BACKED_SPEC_THEN_INDEPENDENT_REPRODUCTION_TEST
operational_state: NOT_EVALUABLE
```

### B3. F12.5 CONTESTED exit rules

```yaml
archive_class: CANONICAL_RULE
status: SPEC_INCOMPLETE_GOVERNANCE_RISK
blocker: ENTRY_EXIT_AND_MAX_REVIEW_DURATION_UNDEFINED
action: FREEZE_STATE_MACHINE_OR_KEEP_SUSPENDED
operational_state: NOT_EVALUABLE
```

### B4. Pullback Policy v0.2 reproducibility

```yaml
archive_class: CANONICAL_RULE
status: GUIDANCE_ONLY
current_correction: 01_CORE_FRAMEWORK/governance/2026-07-10__pullback-policy-v0-2-reproducibility-correction__canonical.md
blocker: EXACT_BANDS_ANCHORS_AND_HARD_TRIGGERS_MISSING
action: SOURCE_BACKED_SPEC_OR_RETAIN_GUIDANCE_ONLY
```

### B5. Public CN track-record reconciliation

```yaml
archive_class: CALIBRATION
status: LOCKED
current_template: 05_CYCLE_NAVIGATOR/templates/2026-07-06__cycle-navigator-mobile-first-image-template__canonical.md
blocker:
  - INDEPENDENT_ACTUALS_INCOMPLETE
  - BASELINE_RECONCILIATION_INCOMPLETE
  - CATEGORY_SCORE_SEPARATION_INCOMPLETE
action: CONTINUE_FRLP_FORWARD_TEST_AND_KEEP_FORWARD_TEST_STATUS_PANEL
```

### B6. Legacy Open Questions v1.1 source mapping

```yaml
archive_class: ARCHIVE_CONTROL
status: SOURCE_TEXT_REQUIRED
current_register: 01_CORE_FRAMEWORK/governance/2026-07-10__open-questions-register-v1-2__canonical.md
legacy_ids:
  - OQ-001
  - OQ-002
  - OQ-015
blocker: ORIGINAL_QUESTION_TEXT_NOT_AVAILABLE_IN_EXECUTION_CONTEXT
action: LOCATE_V1_1_AND_APPEND_SOURCE_BACKED_MAPPING
```

### B7. Legacy namespace classification

```yaml
archive_class: ARCHIVE_CONTROL
status: ONGOING
current_manifest: 00_ARCHIVE_CONTROL/2026-07-10__legacy-namespace-manifest__canonical.md
blocker: RELEVANT_LEGACY_FILES_NOT_YET_ALL_CROSSLINKED
action: CLASSIFY_ON_DEMAND_NO_MASS_COPY
```

### B8. TechDev original-source row import

```yaml
archive_class: FORWARD_TEST_DATA
status: PENDING_SOURCE_EXTRACTION
current_ledger: 06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md
blocker: ORIGINAL_ISSUE_ROWS_NOT_IMPORTED
action: IMPORT_ORIGINAL_CLAIMS_AND_REVISIONS_WITHOUT_RETROACTIVE_REWRITE
```

### B9. Existing-test row production

```yaml
archive_class: FORWARD_TEST_DATA
status: ACTIVE_NEEDS_ROWS
registry: 06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
priority:
  - FRLP
  - BTC_PARTIAL_VS_WAIT
  - FNP
  - EDGE_EVENT_OUTCOMES
  - ROTATION_SURVIVAL_WHEN_DATA_COMPLETE
  - MULTI_PING_AGGREGATION
  - CHIEF_REPRODUCIBILITY
action: PRODUCE_ROWS_NOT_NEW_SPECS
```

---

## Queue rule

Future Canonical Weekly Backbone runs must:

1. read this queue;
2. process matured items;
3. preserve source lineage and supersession;
4. remove completed candidates from the queue;
5. retain unresolved candidates with exact blockers;
6. record processed history in changelog/audit receipt;
7. update Rule and Evidence Registry and Active Test Registry counts;
8. report archive drift, lineage failures and new-engine-freeze breaches.
