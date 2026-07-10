# Index Addendum — DATA PING Hybrid v0.5.1 and Edge Event Archive

**Date:** 2026-07-10  
**Status:** CANONICAL_INDEX_ADDENDUM  
**Reason:** Canonical DATA PING edge-state, runtime, calibration and weekly reconciliation files added after the latest main `CANONICAL_INDEX.md` update.

---

## New canonical anchor — DATA PING Hybrid v0.5.1

Path:

```text
02_DATA_PING/protocols/2026-07-10__data-ping-hybrid-v0-5-1-auto-edge-escalator-consolidated__canonical.md
```

Status:

```text
CANONICAL
+
DATA_PING_EDGE_PROTOCOL
+
STATEFUL_ALERT_AND_DOWNGRADE_STANDARD
+
CALIBRATION_HYGIENE
```

Operational effect:

- only the consolidated v0.5.1 file is active
- dynamic gate functions replace permanent price hard-coding
- EDGE_STATE and ALERT_STATUS are separate
- downgrade check is mandatory
- hour-by-hour ledger is default in the same thread when available
- DATA PING owns evidence; main framework owns judgment and canonical history
- calibration requires framework-approved anchors
- fixed methodology is separated from framework-owned runtime configuration

Supersession:

```text
02_DATA_PING/protocols/2026-07-07__data-ping-alert-router-v0-1__canonical.md
STATUS: SUPERSEDED_AS_ACTIVE_EDGE_PROTOCOL
RETAIN: HISTORICAL_CONTEXT
```

---

## New operational runtime anchor

Path:

```text
02_DATA_PING/live_state_handover/2026-07-10__active-gate-and-edge-event-registry__canonical.md
```

Status:

```text
CANONICAL_RUNTIME_CONFIGURATION
```

Contains:

- framework-owned active gate registry
- current active edge-event ID
- framework-approved historical anchors
- current framework state
- missing/stale runtime handling

Current active event:

```text
PULLBACK_EDGE_20260708_01
FRAMEWORK_EDGE_STATE: WATCH
ALERT_STATUS: RESOLVING
EVENT_STATUS: OPEN_RESOLVING
```

---

## New append-only event ledger

Path:

```text
02_DATA_PING/live_state_handover/2026-07-08__pullback-edge-20260708-01__event-ledger.md
```

Status:

```text
OPERATIONAL_EVENT_LEDGER
+
APPEND_ONLY
```

Contains:

- canonical first PRESENT anchor
- source-backed early NEAR_PRESENT candidate
- PRESENT → NEAR_PRESENT → WATCH → RESOLVING path
- material truth-layer state transitions
- current event status and close authority

---

## New active calibration file

Path:

```text
04_MARKET_LEARNING/stress_flush/2026-07-08__pullback-edge-20260708-01__calibration-v3.md
```

Status:

```text
CALIBRATION_ACTIVE
+
PROVISIONAL_LEARNING_ONLY
```

Version chain:

```text
VERSION_1: SUPERSEDED
VERSION_2: SUPERSEDED
VERSION_3: CORRECTED_ACTIVE
```

Matured outcome:

```text
24H: MATURED
72H: PENDING
7D: PENDING
EVENT_CLOSE: PENDING
```

Current provisional learning candidate:

```text
Market-stress detection may have value.
Tactical trim execution appears provisionally weak at 24H.
No final learning is ratified before sufficient maturity.
```

---

## New Canonical Weekly Backbone addendum

Path:

```text
03_WEEKLY_OPERATIONS/canonical_backbone/2026-07-10__edge-event-archive-reconciliation-addendum__canonical.md
```

Status:

```text
CANONICAL
+
CWB_V3_OPERATIVE_ADDENDUM
+
ARCHIVE_RECONCILIATION
```

Operational effect:

Future weekly backbone runs must inspect and reconcile:

- archive-candidate queue
- active runtime gate/event registry
- open edge-event ledgers
- matured and pending outcomes
- supersession and source lineage
- newest DATA PING, Master Monday, Cycle Navigator and governance discussions

RAW observations must not be promoted directly into canonical learning.

---

## Operational pending queue

Path:

```text
00_ARCHIVE_CONTROL/2026-07-10__archive-candidate-queue__operational.md
```

Status:

```text
OPERATIONAL_PENDING_QUEUE
```

Contains only unresolved items:

- canonical first WATCH anchor
- canonical first NEAR_PRESENT anchor
- 72H outcome
- 7D outcome
- event-close row
- final framework learning

---

## Precedence rule

```text
1. Main CANONICAL_INDEX.md is read first.
2. This addendum must then be read for 2026-07-10 DATA PING Hybrid and edge-event updates.
3. The newest canonical file wins over older conflicting protocol files.
4. Runtime registry values are framework-owned and may be superseded by a newer explicit registry.
5. Pending outcome rows remain pending until matured and written.
```
