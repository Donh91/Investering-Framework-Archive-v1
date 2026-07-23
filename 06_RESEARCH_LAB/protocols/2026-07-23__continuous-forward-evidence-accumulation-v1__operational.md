# Continuous Forward Evidence Accumulation v1

**Date:** 2026-07-23  
**Status:** OPERATIONAL / SHADOW EVIDENCE INFRASTRUCTURE  
**Scope:** T1 FRLP, T2 BTC Partial versus WAIT, T4 Pullback Edge Outcomes, T5 FNP Cumulative  
**Depends on:** Active Test Registry, FRLP v0.1, Sensor Relationship & Incremental Value Standard, Claude BTC Range and Pullback PATCH1 validation

## 1. Purpose

Accumulate append-only, source-backed forward observations that can later be analysed retrospectively without reconstructing decisions or treating overlapping observations as independent evidence.

This protocol creates no new test ID, signal, engine, market state, gate, rebuy permission or portfolio authority.

## 2. Existing-owner routing

```text
T1 FRLP_V0_1:
weekly frozen range, baselines, verified actuals and multi-metric scoring

T2 GATE_BTC_PARTIAL_FT_1:
frozen WAIT versus BTC-partial divergence and realised opportunity/risk cost

T4 PULLBACK_EDGE_20260708_01_OUTCOMES:
pullback event survival, protection value and event outcomes

T5 FNP_CUMULATIVE:
lock-versus-opportunity cost across frozen horizons
```

Every new row must point to one existing `test_id`. No row may create a parallel owner.

## 3. Two-stage row lifecycle

### Stage A - frozen source row

Written only when the observation exists in real time and before its outcome window is known.

Required:

```text
evidence_id
test_id
source_packet_id
source_hash
observed_at_utc
asset
horizon
frozen_state
benchmark_state
observation_unit
independent_event_id
overlap_group_id
right_censored
source_quality
row_status=FROZEN_SOURCE
```

### Stage B - matured outcome row

Appended or completed only after the declared horizon matures from later verified data.

Required where applicable:

```text
matured_at_utc
end_return_pct
mfe_pct
mae_pct
max_drawdown_pct
drawdown_avoided_pct
missed_upside_pct
opportunity_cost_pct
false_permission_cost_pct
outcome_class
outcome_source
outcome_hash
unit_matched_control
row_status=MATURED_OUTCOME
```

Source rows are not outcome rows. A missing outcome remains pending or right-censored, never zero.

## 4. Observational-unit integrity

Each row must declare one of:

```text
DAY
INDEPENDENT_EVENT
WEEK
DECISION_DIVERGENCE
```

Rules:

1. Consecutive daily observations from one causal signal cluster share one `overlap_group_id`.
2. One causal cluster receives one `independent_event_id`.
3. Day-level rows may be retained for path analysis, but promotion and significance summaries must also use independent-event rows.
4. Signal and control statistics must use matched observational units.
5. A day-level null may not be presented as unit-matched evidence for independent-event samples.
6. Right-censored active events remain valid source rows but are excluded from completed-outcome counts.

## 5. Distribution fields

Hit rate or lift alone is insufficient. Matured rows must preserve the available outcome distribution fields:

```text
end_return_pct
mfe_pct
mae_pct
max_drawdown_pct
worst_path_pct
time_to_mfe_hours
time_to_mae_hours
drawdown_avoided_pct
missed_upside_pct
opportunity_cost_pct
false_permission_cost_pct
```

Fields unavailable from the accepted source chain remain `UNKNOWN`.

## 6. T1 FRLP binding

The canonical FRLP ledger remains the official weekly range owner.

For later research, every eligible T1 outcome must preserve:

```text
Winkler alpha 0.10
Winkler alpha 0.20
Jaccard
containment
breach days
direction bias
width ratio
adjustment alpha versus DUMB 1.5
adjustment alpha versus DUMB 2.0
week convention
source conflict status
```

Jaccard-only method selection is forbidden. Historical grid optima from PATCH1 do not replace forward FRLP rows or kill criteria.

## 7. T2, T4 and T5 binding

For decision and pullback rows, preserve:

```text
frozen action
benchmark action
actual decision divergence
time in state
recovery attempt count
MFE
MAE
maximum drawdown
drawdown avoided
missed upside
opportunity cost
false permission cost
final classification
```

A row with no actual decision divergence may remain a valid source observation, but it is not a valid divergence outcome.

## 8. Source anomaly handling

Every row includes `source_anomaly_flags`.

The known historical flag is:

```text
SOURCE_ANOMALY_2018_02_08_EARLY_CLOSE
```

New anomalies are preserved, not silently repaired. Any corrected or alternative-source result must be a separate challenger or revision row with explicit lineage.

## 9. Cadence

```text
DAILY:
scan new accepted DATA PING and framework decisions for eligible frozen T2/T4/T5 source rows

AT HORIZON MATURITY:
append verified 24H, 72H, 7D or declared-horizon outcomes

WEEKLY AFTER SETTLEMENT:
append or complete T1 FRLP actuals and scores
reconcile right-censored events
update coverage state

AFTER 20 TO 30 NEW ELIGIBLE OUTCOME ROWS:
relationship, overlap, survival and baseline review

QUARTERLY:
retrospective distribution, regime stability and simplification audit
```

## 10. Write discipline

1. Append only through an isolated task branch.
2. Prevent duplicates by `evidence_id` and source hash.
3. Validate schema and exact field count.
4. Never rewrite frozen fields.
5. Outcome corrections create revision rows, not silent replacements.
6. Open and validate a bounded PR.
7. Merge only after zero-deletion and duplicate checks.
8. Read back the merged row and update `latest_state.json` only after main readback.

## 11. Retrospective-analysis readiness

A future analysis must report separately:

```text
source rows
matured outcome rows
independent events
overlapping day rows
right-censored rows
source anomalies
regime distribution
matched-unit controls
prospective rows
historical event-study-only rows
```

No retrospective narrative may be counted as a prospective row.

## 12. Authority boundary

```text
NEW_TEST: NO
NEW_ENGINE: NO
CANONICAL_RANGE_CHANGE: NO
ACTIVE_TEST_CHANGE: NO
CURRENT_ALERT: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
DEPLOYMENT_CHANGE: NO
PORTFOLIO_ACTION: NO
```
