# M3 Forward Decision Collection Protocol v0.1

**Date:** 2026-07-12  
**Status:** ACTIVE_FORWARD_COLLECTION / ZERO_SCORING_AUTHORITY  
**Purpose:** Replace exhausted historical reconstruction with clean prospective decision rows.

## Starting state

```text
M3_eligible_rows: 13
independent_eligible_event_windows: 1
current_window: PULLBACK_EDGE_20260708_01
M3_LEDGER_COVERAGE_READY: NO
```

## Activation rule

Create a row only when the main framework makes or accepts a material point-in-time decision or state transition.

Eligible row families:

```text
FRAMEWORK_STATE_CHANGE
PULLBACK_ALERT_CHANGE
ROTATION_STATE_CHANGE
REBUY_OR_DEPLOY_STATE_CHANGE
PROFIT_OR_EXIT_PREPARATION_CHANGE
RAW_1_3D_FREEZE
RAW_5_7D_FREEZE
RAW_2_3W_FREEZE
MASTER_MONDAY_RATIFIED_FORECAST
FORECAST_LEDGER_FREEZE
CYCLE_NAVIGATOR_PUBLIC_FREEZE
EVENT_CLOSE_DECISION
```

Routine unchanged DATA PING observations do not create decision rows.

## Required issuance proof

A row is eligible only when all are present:

- exact `issued_timestamp_utc` from the original run, publication or framework acceptance;
- actual readable source text;
- source path or public URL;
- source run ID or forecast ID where applicable;
- exact frozen excerpt;
- source status `SOURCE_BACKED`, `PUBLIC_SOURCE_BACKED` or `OFFLINE_GITHUB_SNAPSHOT_BACKED`;
- source existed before the outcome window;
- no retrospective framework acceptance.

A Git commit timestamp by itself is archive time, not proof of original issuance time.

## Event-window rule

- Continue an existing event-window ID while the same event is evolving.
- Create a new event-window ID only after a genuinely new framework event, forecast window or materially independent state sequence begins.
- A closed event must never be silently reopened.
- A later deterioration after formal close receives a new event ID.

## Row-freeze sequence

```text
source run/publication occurs
→ framework decision or acceptance is explicit
→ append Group D decision row immediately
→ commit row to GitHub
→ preserve commit receipt
→ leave outcome fields blank
→ score only when the pre-frozen horizon closes and verified actuals exist
```

## Prohibited recovery methods

```text
NO metadata-only issuance timestamps
NO retrospective source rewriting
NO reconstructed Master Monday as original raw source
NO summary-to-original promotion
NO duplicate rows for unchanged states
NO outcome fields at decision creation
NO invented numeric loss weights
```

## Coverage gates for full M3 review

```text
minimum_M3_eligible_rows: 30
minimum_independent_event_windows: 3
maximum_share_from_one_event_window: 50%
minimum_source_families: 3
```

Passing these gates allows a governance review. It does not automatically promote a challenger.

## Objective structure

Rows remain compatible with the approved dual-objective evaluation:

### Capital protection

- missed >=Storm / terminal-risk events;
- maximum drawdown;
- early-rebuy damage;
- late-exit damage.

### Opportunity cost

- false-positive trim;
- missed upside;
- missed rotation;
- late rebuy.

Do not collapse the objectives into a fabricated scalar score.

## Weekly control

Sunday Closeout must report:

```text
M3_ROWS_ADDED_THIS_WEEK
M3_ELIGIBLE_ROWS_TOTAL
M3_EVENT_WINDOWS_TOTAL
M3_LARGEST_WINDOW_SHARE
M3_SOURCE_FAMILIES_TOTAL
M3_COVERAGE_STATUS
M3_ROWS_REJECTED_AND_REASON
```

## Boundary

This protocol creates auditable evidence only. It cannot make market calls, portfolio actions, scores or rule promotions.
