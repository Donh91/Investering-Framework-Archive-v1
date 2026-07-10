# Canonical Weekly Backbone — Edge Event Archive Reconciliation Addendum

**Dato:** 2026-07-10  
**Updated:** 2026-07-10  
**Status:** CANONICAL  
**Område:** Canonical Weekly Backbone / archive reconciliation / edge-event lifecycle / evidence discipline  
**Primary folder:** `03_WEEKLY_OPERATIONS/canonical_backbone/`  
**Related folders:** `00_ARCHIVE_CONTROL/`, `01_CORE_FRAMEWORK/`, `02_DATA_PING/`, `04_MARKET_LEARNING/`, `05_CYCLE_NAVIGATOR/`, `06_RESEARCH_LAB/`  
**Depends on:** Canonical Weekly Backbone Engine v3.0; DATA PING Hybrid v0.5.1 consolidated; GPT-5.6 Fresh Eyes Audit Implementation  
**Supersedes:** none; this is an operative addendum to CWB v3.0

---

## 1. Canonical decision

Every future Canonical Weekly Backbone run must reconcile the archive state of DATA PING edge events and the evidence state of active rules/tests, not only summarize the latest market state.

This addendum is mandatory whenever open/recently closed edge events, active tests or unresolved lineage items exist.

---

## 2. Mandatory weekly inspection set

After reading `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, every run must inspect:

```text
- newest active DATA PING thread / highest active DATA PING version
- newest Master Monday version chain
- newest Cycle Navigator post and handoff
- newest framework-governance discussion
- current archive-candidate queue
- current runtime gate/event registry
- open edge-event ledgers
- matured and pending 24H / 72H / 7D / EVENT_CLOSE rows
- supersession and source-lineage status
- shadow context availability
- Rule and Evidence Registry
- Active Test Registry
- Open Questions Register v1.2
- legacy namespace drift
- public track-record lock status
- W28 and future forecast lineage
```

If any item is inaccessible, report exact missing inputs. Do not silently omit them.

---

## 3. Archive candidate reconciliation

For every pending candidate:

```text
1. Classify as CANONICAL_RULE / RUNTIME_CONFIG / RAW_LEDGER / CALIBRATION / WEEKLY_LEARNING / SHADOW_CONTEXT / NO_ARCHIVE.
2. Deduplicate against existing canonical and operational files.
3. Write or append to the correct domain location.
4. Mark superseded rows explicitly.
5. Update index or index addendum for canonical/operationally important files.
6. Remove processed candidates from the pending queue.
7. Leave unresolved candidates with exact blocker and next maturity/action.
```

Routine unchanged pings must not inflate the canonical index.

---

## 4. Edge event lifecycle

The weekly run must track each event through:

```text
EVENT_START
→ RAW / HOURLY / CLOSE LEDGERS
→ STATE TRANSITIONS
→ 24H OUTCOME
→ 72H OUTCOME
→ 7D OUTCOME
→ EVENT_CLOSE
→ MAIN-FRAMEWORK LEARNING
```

One event ID persists through state changes until main framework formally closes it.

DATA PING cannot create canonical event IDs, canonical anchors or event-close decisions.

---

## 5. Calibration safety

Weekly Backbone must verify:

- framework-approved reference time and trigger price exist;
- older calibration versions are preserved as `SUPERSEDED`;
- no silent overwrite occurred;
- exact horizon state is not backfilled from a distant prior run;
- interval counts are not mislabeled as clock duration;
- pending outcomes remain `PENDING`;
- source candidates are not promoted to canonical anchors without framework acceptance;
- sensor state is not promoted to framework judgment.

If any check fails:

```text
CALIBRATION_INTEGRITY_STATUS: FAIL / PARTIAL
run_status: MANUAL_BACKFILL_PASS or BLOCKED depending severity
```

---

## 6. Learning promotion rule

Never promote RAW observations directly into canonical learning.

A learning candidate may move to `WEEKLY_LEARNING` only when:

1. required outcome horizons have matured or main framework explicitly accepts a shorter evidence basis;
2. source lineage is complete;
3. framework interpretation is separated from sensor measurements;
4. the learning changes future calibration, governance or operational behavior.

For pullback/trim events, always separate:

```text
MARKET_STRESS_DETECTION_VALUE
from
TACTICAL_EXECUTION_EDGE_VALUE
```

---

## 7. Governance-theater check

Every active rule/test must report:

```text
rows_total
valid_rows
decision_divergence
baseline_status
behavior_changed
evidence_status
promotion_condition
kill_condition
last_review
```

If a rule has documentation but no behavioral evidence, classify it:

```text
WRITTEN_NOT_PROVEN
```

If a test has schema/init rows but no valid rows, report `VALID_ROWS: 0`.

Do not count prompts, schemas, initialized ledgers or retrospective explanations as evidence rows.

---

## 8. New-engine freeze enforcement

Through 2026-08-09:

```text
NEW_ENGINE_FREEZE: ACTIVE
```

Weekly Backbone must flag:

- any new named engine;
- any new shadow layer;
- any new test outside the Active Test Registry;
- any duplicate scoring concept;
- any pseudo-row created while a test is DATA_BLOCKED.

Allowed changes are bug fixes, lineage repair, data completion, row production, archive consolidation, reproducibility corrections and retirement/compression.

---

## 9. Forecast and public-scoring integrity

Every official forecast must have:

```text
source Master Monday
→ framework ratification
→ frozen Forecast Ledger
→ Cycle Navigator handoff
→ verified actual
→ score row
```

If incomplete:

```text
FORECAST_LINEAGE_STATUS: INCOMPLETE
SCORING_STATUS: BLOCKED
```

While public track record is locked:

- no historical precision bars;
- no blended precision score;
- no `88% precision` language;
- CN third panel must be `Forward Test Status`;
- range, phase and rotation remain separate.

---

## 10. Missing-data discipline

```text
DATA_MISSING = UNKNOWN
DATA_MISSING != BEARISH_EVIDENCE
```

Missing critical data may block permission or reduce confidence. It may not be counted as a negative sensor observation.

---

## 11. Rule/test survival review

Every weekly run must classify each active rule/test:

```text
KEEP
MODIFY
SUSPEND
KILL
BLOCKED
```

Required weekly evidence block:

```yaml
RULE_AND_TEST_REVIEW:
  rules_reviewed:
  tests_reviewed:
  rows_added:
  valid_rows_added:
  decision_divergence_days:
  baseline_results:
  behavior_changes:
  manual_interventions:
  missing_field_rate:
  items_suspended:
  items_killed:
  new_engine_freeze_breaches:
```

No promotion is implied by elapsed time alone.

---

## 12. Mandatory weekly output additions

Every weekly run must include:

```text
EDGE_EVENT_RECONCILIATION:
  open_event_ids:
  closed_event_ids:
  events_with_24h_matured:
  events_with_72h_matured:
  events_with_7d_matured:
  pending_event_close_rows:
  calibration_integrity_status:
  superseded_rows_verified:
  unresolved_anchors:

ARCHIVE_CANDIDATE_RECONCILIATION:
  candidates_processed:
  candidates_archived:
  candidates_skipped_as_duplicate:
  candidates_left_pending:
  index_updates:
  archive_drift_detected:

EVIDENCE_PRODUCTION_STATUS:
  active_rule_rows:
  active_test_rows:
  valid_rows:
  data_blocked_tests:
  lineage_blocked_forecasts:
  public_track_record_lock:
  legacy_namespace_new_writes:
```

Existing mandatory v3.0 fields remain required:

- repository completeness;
- VERSION_UPGRADE_DIAGNOSTIC;
- CANONICAL_LEARNING_QUEUE;
- ARCHIVE_RECOMMENDATION;
- run status.

---

## 13. Post-audit automation rule

After a successful weekly reconciliation:

```text
1. Update canonical archive.
2. Update CANONICAL_INDEX or a clearly linked index addendum.
3. Clear processed archive candidates.
4. Leave unresolved candidates in the pending queue.
5. Never archive duplicate canonical rules.
6. Never promote RAW observations into canonical learning.
7. Promote weekly learning only after sufficient maturity.
8. Report archive drift, missing lineage and write failures.
9. Update rows_total and valid_rows in the registries.
10. Preserve the new-engine freeze unless main framework explicitly lifts it.
```

---

## 14. Current event handoff

As of this addendum:

```yaml
edge_event_id: PULLBACK_EDGE_20260708_01
event_status: OPEN_RESOLVING
framework_edge_state: WATCH
framework_alert_status: RESOLVING
matured_outcomes:
  - 24H
pending_outcomes:
  - 72H
  - 7D
  - EVENT_CLOSE
provisional_learning:
  market_stress_detection: POSSIBLE_VALUE
  tactical_trim_execution: PROVISIONALLY_WEAK
final_learning_status: PENDING
```

This current-event block is runtime context. Future runs must read the active runtime registry and event ledger rather than hard-code these values.
