# Index Addendum — DATA PING Alert Router v0.1

**Date:** 2026-07-07  
**Status:** CANONICAL_INDEX_ADDENDUM  
**Reason:** Canonical operational patch added after latest main `CANONICAL_INDEX.md` update.

---

## New canonical anchor

### DATA PING Alert Router v0.1

Path:

```text
02_DATA_PING/protocols/2026-07-07__data-ping-alert-router-v0-1__canonical.md
```

Status:

```text
CANONICAL
+
DATA_PING_EXECUTION_COMPRESSION
+
ALERT_HYGIENE_PATCH
```

Contains:

```text
DATA PING Alert Router v0.1
Large-cap pre-altseason buy-window alert logic
5-7D pullback / sell-rebuy warning logic
No-buy regime override
Rebuy window state machine
Segment hierarchy for large/mid/small/micro/memes
Notification hygiene rules
DATA PING prompt patch
Weekly RAW / Master Monday / GitHub Archive integration rules
```

Use for:

```text
DATA PING V4+
DATA PING V5+ handover
Weekly RAW Learning Snapshot
Master Monday
GitHub Archive Sync
Cycle Navigator calibration context
Future automation health checks
```

Operational effect:

```text
Do not reactivate old daily concepts as separate noisy automations.
Fuse their useful decision output into one thin Alert Router block inside DATA PING.
The router only emphasizes decision-relevant changes:
- PREPARE_BUY_LARGE_CAPS
- START_SMALL_LARGE_CAPS
- BUILD_LARGE_CAPS
- PULLBACK_RISK_5_7D
- TRIM_A_BID
- REBUY_WINDOW_FORMING
- NO_BUY_REGIME
- INVALIDATED
Routine NO_ACTION / unchanged WATCH states should stay compact or silent.
```

Boundary:

```text
Alert Router must never overrule DATA PING truth layer.
Pre-Trigger is not a buy signal by itself.
No-buy regime overrides all buy and rebuy outputs.
Microcap-only pumps are not real rotation.
```
