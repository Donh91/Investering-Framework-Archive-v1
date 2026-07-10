# DATA PING Alert Router v0.1 — Superseded Notice

**Date:** 2026-07-07  
**Superseded:** 2026-07-10  
**Status:** SUPERSEDED / HISTORICAL_CONTEXT  
**Domain:** DATA PING / execution compression / alert hygiene  
**Original path retained:** `02_DATA_PING/protocols/2026-07-07__data-ping-alert-router-v0-1__canonical.md`  
**Superseded by:** `02_DATA_PING/protocols/2026-07-10__data-ping-hybrid-v0-5-1-auto-edge-escalator-consolidated__canonical.md`

---

## Supersession decision

DATA PING Alert Router v0.1 is no longer the active edge-state or pullback-alert protocol.

Its original full content is preserved in Git commit history.

The active canonical protocol is:

```text
DATA PING Hybrid v0.5.1 — Auto Edge Escalator Consolidated
```

The newer protocol supersedes v0.1 because it adds and clarifies:

- dynamic framework-owned active gates
- stateful `EDGE_STATE` versus `ALERT_STATUS`
- automatic EDGE MODE / DEEP EDGE MODE
- mandatory downgrade and resolving logic
- hour-by-hour path ledger
- persistent edge-event IDs and event ledger
- framework-owned historical anchors
- calibration row versioning and outcome maturity
- DATA PING invariance and source fallback rules
- strict separation between sensor evidence and framework judgment

---

## Historical value retained

The following v0.1 concepts remain historical design context where they do not conflict with v0.5.1:

- decision-relevant alert compression
- large-cap window monitoring
- 5–7D pullback monitoring
- no-buy override
- rebuy separation
- segment hierarchy
- notification hygiene
- archive only material state changes

Use the consolidated v0.5.1 file for all current and future operation.
