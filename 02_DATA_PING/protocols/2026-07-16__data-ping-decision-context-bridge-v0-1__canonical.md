# DATA PING Decision Context Bridge v0.1

**Status:** CANONICAL_OPERATIONAL_PROTOCOL  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Effective:** 2026-07-16  
**Scope:** DATA PING V5 and all later DATA PING thread versions  
**Authority:** CONTEXT_AND_DECISION_DELTA_ONLY

## Purpose

Create one stable, cross-thread decision context above the existing accepted DATA PING log, thread-handover protocol and prospective-evidence machinery.

This is not a new market engine, score, test, sensor pair, backtest or portfolio authority.

The bridge exists to prevent a new DATA PING V6, V7 or later thread from losing:

- the latest accepted DATA PING identity and provenance;
- active event continuity;
- event-scoped runtime gates;
- the current decision state;
- frozen prospective claims and maturity dates;
- the exact evidence required for a material decision change;
- the distinction between data improvement and decision improvement.

## Existing owners reused

The bridge must reuse, not replace:

1. `02_DATA_PING/operational_handoffs/latest_accepted_log_state.json`
2. the canonical DATA PING thread-handover protocol and latest handover pointer;
3. `.agents/skills/prospective-evidence-ledger/SKILL.md`;
4. the active event registry referenced by the latest accepted-log pointer;
5. existing test, forecast and evidence owners.

## Stable bootstrap order

Every Main Framework review of a DATA PING in V5, V6, V7 or later must resolve in this order:

```text
LATEST_DECISION_CONTEXT_STATE
-> LATEST_ACCEPTED_LOG_STATE
-> ACCEPTED_PAYLOAD_AND_RECEIPT
-> ACTIVE_EVENT_REGISTRY
-> PROSPECTIVE_EVENT_RECORD
-> CURRENT_THREAD_PACKET
```

A missing or unreadable owner must remain explicit. No value may be reconstructed from memory.

## Bounded decision-delta classes

Each accepted DATA PING must receive exactly one descriptive delta class:

```text
NO_MATERIAL_DECISION_DELTA
OBSERVABILITY_OR_DATA_QUALITY_DELTA
EARLY_WARNING_CANDIDATE
CONFIRMATION_CANDIDATE
INVALIDATION_CANDIDATE
ACTION_CHANGE_RATIFIED_BY_MAIN_FRAMEWORK
```

These classes are routing labels, not scores and not automatic signals.

### NO_MATERIAL_DECISION_DELTA

New values do not alter the active event interpretation, warning state or action.

### OBSERVABILITY_OR_DATA_QUALITY_DELTA

Data continuity, source quality or field coverage improves or deteriorates without sufficient market evidence for a state change.

### EARLY_WARNING_CANDIDATE

At least one existing event-scoped warning path becomes materially more plausible. Typical evidence families are:

- failed reclaim or loss of a current repair/survival gate;
- deterioration persisting across compatible fixed-cohort breadth observations;
- negative spot aggression persisting across relevant horizons;
- completed ETF flow deterioration rather than a partial session;
- price weakness reinforced by participation and flow rather than price alone.

No fixed vote count is introduced. Main Framework judgement remains required.

### CONFIRMATION_CANDIDATE

An existing confirmation path becomes materially more plausible through verified persistence and cross-family agreement. A single intraday print, partial candle, partial ETF row or one-venue proxy is insufficient.

### INVALIDATION_CANDIDATE

A frozen event claim or repair thesis reaches an event-scoped failure condition. Main Framework must distinguish local cooling, failed reclaim and full event invalidation.

### ACTION_CHANGE_RATIFIED_BY_MAIN_FRAMEWORK

May only be written after explicit Main Framework ratification. DATA PING, Custom GPT, OTA, a quality score or an automated job cannot create it.

## Decision-relevant evidence lanes

The bridge carries only five bounded lanes:

1. **Structure:** current price, canonical settled closes and event-scoped gates.
2. **Participation persistence:** fixed-cohort breadth across compatible pings.
3. **Completed institutional flow:** ETF completed sessions, windows and concentration.
4. **Spot-flow persistence:** verified venue-specific or multi-venue aggression, never mislabeled market-wide CVD.
5. **Prospective outcomes:** frozen claims, maturity dates, actual outcomes and false-positive/false-negative review.

Macro, CFGI, stablecoin proxies, DEX and derivatives remain contextual or confirmation/veto inputs according to their existing owners. They do not gain new authority here.

## Mandatory update after each accepted DATA PING

After acceptance and main-branch readback, Main Framework must update:

- `02_DATA_PING/operational_handoffs/latest_decision_context_state.json`
- the current event record under `02_DATA_PING/decision_value/prospective_events/`

The update must record:

- latest accepted DATA PING ID and hash;
- decision-delta class;
- changed evidence only;
- current decision state;
- next maturity or decision-changing observation;
- missing fields and their actual impact;
- no-action rationale when action remains unchanged.

## Prospective discipline

The existing prospective-evidence-ledger Skill controls row validity, maturity, frozen fields, duplicate detection and event-window independence.

This bridge may point to or summarize a prospective record. It may not create retrospective pseudo-rows, mutate frozen claims or promote a rule.

## Public output rule

Public-facing state must use:

```text
New Entry Signal: Not Active
```

Internal sensitive fields may remain private and must not be copied into a public mirror unless explicitly allowlisted.

## Safety boundaries

```text
new engine: NO
new score: NO
new test: NO
new universal threshold: NO
retrospective backfill: NO
automatic gate firing: NO
automatic portfolio action: NO
Custom GPT authority increase: NO
Main Framework authority: UNCHANGED
```
