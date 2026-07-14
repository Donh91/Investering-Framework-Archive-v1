# Rotation Repair Edge — Breadth and Flow Deterioration Continuation

**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Accepted run:** `DATA_PING_V4_20260714T071658Z`  
**Source timestamp:** 2026-07-14T07:16:58Z  
**Framework review time:** 2026-07-14T07:38:55Z  
**Data quality:** MEDIUM  
**Status:** MATERIAL_CONTINUATION / NO_NEW_EVENT

## Framework decision

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: NOT_OPEN
PORTFOLIO_ACTION: NONE
```

## Material change

The short-horizon rebound seen in the prior accepted packet did not persist. Breadth fell back to 25.7% on 1H, 20.0% on 24H and 25.7% on 7D. Binance spot-taker proxies were negative for BTC across 15M, 1H, 4H and 24H, while ETH was negative across the same horizons with 4H near balanced. BTC open interest remained elevated at +6.2% over 24H and positioning remained long-skewed. The latest completed BTC ETF session remained -$424.7M, with 3-, 5- and 10-session windows negative. The selected stablecoin proxy continued to contract.

## Why the state remains below PRESENT

BTC remained above the 61.9K survival gate both currently and on the latest completed CEST close. Direct ETH/BTC remained above 0.0275 with 12 completed daily closes above the repair gate. No completed daily survival breakdown, no ETH/BTC repair-gate loss and no acute funding stress were present.

## Data-quality note

The packet reported `DATA_PING_V4_20260714T062424Z` as its immediate predecessor, but that intermediate packet was not available in the current archive. The accepted lineage therefore advances from `DATA_PING_V4_20260714T051915Z` directly to this run while preserving the predecessor gap explicitly. No values from the missing packet were reconstructed.

The improved CFGI collection is accepted as a data-layer improvement only. Sentiment remains non-binding and is not used as flow or as a framework state trigger.

No threshold, event identity, sensor weight, score, portfolio rule or Cycle Navigator forecast is changed.