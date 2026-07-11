# Pullback Edge 72H Close Calibration Addendum

**Event:** `PULLBACK_EDGE_20260708_01`  
**Date:** 2026-07-11  
**Status:** EVENT_CLOSED / 7D_CALIBRATION_PENDING  
**Authority:** Main framework interpretation based on accepted DATA PING truth-layer rows

---

## What the event actually did

The event identified a real but short-lived stress episode around the active BTC survival gate. After the canonical PRESENT anchor at BTC 61,784.48, price moved only another 0.3883% lower before recovering.

At 24H, BTC was 2.0184% above the anchor. At 72H, BTC was 3.9873% above the anchor, while the active 63.3K reclaim gate had been reclaimed and held at the horizon.

```yaml
canonical_present_anchor: 61784.48
post_anchor_low: 61544.56
post_anchor_additional_downside_pct: 0.3883
horizon_24h_close: 63031.52
horizon_24h_close_move_pct: 2.0184
horizon_72h_close: 64248.00
horizon_72h_close_move_pct: 3.9873
horizon_72h_high: 64692.83
horizon_72h_max_rebound_pct: 4.7073
```

---

## Calibration judgment

```yaml
market_stress_detection:
  result: PARTIALLY_SUPPORTED
  interpretation: Detected genuine gate stress and weak breadth, but the stress was brief and rapidly repaired.

tactical_trim_execution:
  result: NOT_SUPPORTED_AT_24H_AND_72H
  interpretation: The post-alert downside was too small relative to the rebound to justify a new tactical trim.

alert_downgrade_logic:
  result: SUPPORTED
  interpretation: PRESENT was correctly downgraded through NEAR_PRESENT and WATCH as price and supporting layers repaired.

event_close_logic:
  result: SUPPORTED
  interpretation: Closure after 72H maturity avoided keeping a stale warning alive after reclaim and repair.
```

---

## What remains unresolved

This event does not establish that the wider market is healthy.

```text
BROAD_RECOVERY: NOT_FULLY_CONFIRMED
ROTATION: NO_ROTATION
ETHBTC_0.0300_CONFIRMATION: NOT_MET
7D_BREADTH: WEAK
STABLECOIN_DEPLOYMENT: UNKNOWN
CVD: UNAVAILABLE
REBUY: LOCKED
LARGE_CAP_DEPLOYMENT: NOT_OPEN
```

The event is closed because the specific pullback warning resolved, not because all offensive conditions are satisfied.

---

## Governance learning

1. Stress detection and execution value must remain separate.
2. A mechanically valid warning can still have no tradeable trim edge.
3. Downgrade and close rules prevented warning inertia.
4. Gate reclaim plus maturity should close the event even when broader recovery remains incomplete.
5. A new deterioration after closure requires a new event ID.

---

## Pending 7D row

```yaml
measurement_horizon: 7D
maturity_time: 2026-07-15T14:03:00Z
status: PENDING
purpose: FINAL_EVENT_CALIBRATION
may_change_event_close_status: NO
may_change_final_signal_assessment: YES
```

The 7D row may refine the calibration judgment but does not silently reopen the closed event.
