# Rotation Repair Edge — OKX derivatives restored, ETF latest session recovered, market-wide flow still missing

**Dato:** 2026-07-15 20:23:00.944 UTC / 22:23:00.944 CEST  
**Supplement received:** 2026-07-15 20:48:55 UTC  
**Status:** OPERATIONAL_RUNTIME_UPDATE  
**Område:** DATA PING / active edge event  
**Primary folder:** `02_DATA_PING/live_state_handover/event_updates/`  
**Depends on:** `DATA_PING_V4_20260715T202300Z`, `FARSIDE_ETF_RECOVERY_20260715T204855Z`, `ROTATION_REPAIR_EDGE_20260712_01`

## Accepted interpretation

The full OKX v1.2 integration passed and restores a usable venue-specific derivatives layer. Funding, open interest history, mark/index basis, account long/short ratio and contract taker-volume are observable again.

The user-supplied Farside API responses additionally restore the ETF layer through the latest completed session on 14 July. The 15 July zero rows are treated as incomplete and `PENDING`, not as zero flow.

Overall data quality remains MEDIUM. Flow confidence improves within the ETF sub-layer but remains LOW overall because market-wide CVD and verified spot aggressor flow are absent.

## Material changes

1. BTC remained above the 63.3K reclaim level at 64,904. ETH/BTC remained above 0.0285 and near the 0.0300 confirmation gate at 0.0296022.
2. ETH continued to outperform BTC over 24H and 7D.
3. OKX derivatives showed modest positive funding, slightly negative mark/index basis, falling one-hour OI in both assets, approximately flat BTC OI over 24H and a 3.43% ETH OI decline over 24H.
4. Current breadth was negative on 1H, mixed-to-positive on 24H and positive on 7D. The new fixed cohort has no valid prior comparison yet.
5. Farside recovery verified 14 July ETF flow at BTC +181.1M and ETH +58.3M. BTC rolling 3/5/7/10-session windows remain negative, while ETH rolling 3/5/7/10-session windows are positive.

## Constructive evidence

- BTC current fallback remains above 63.3K.
- ETH/BTC remains above 0.0285 and 1.33% below 0.0300.
- Latest settled GeckoTerminal shadow closes remained above the BTC reclaim and relative-structure repair levels, observation only.
- ETH outperformed BTC over 24H and 7D.
- Seven-day breadth remained positive across top-50 and top-100 risk cohorts.
- OKX funding was positive but not acutely elevated.
- One-hour OI fell in BTC and ETH, and ETH price remained positive while 24H ETH OI declined on OKX.
- No acute venue-specific leverage-stress signature was present.
- Latest completed BTC and ETH ETF sessions were both positive.
- ETH ETF rolling 3/5/7/10-session windows were positive.

## Cooling or contradictory evidence

- One-hour breadth was negative.
- Twenty-four-hour breadth was only mixed-to-positive rather than broad.
- BTC shadow current-day CLV was near the midpoint while the range compressed.
- Stablecoin proxy market cap and dominance declined.
- OKX basis was slightly negative for BTC and ETH.
- OKX taker-volume leg direction was not verified and cannot be used directionally.
- BTC ETF rolling 3/5/7/10-session windows remained negative despite the positive latest session.
- Market-wide CVD and canonical spot-taker evidence were absent.

## Unresolved blockers

- Canonical Binance CEST daily and hourly closes remain missing.
- Canonical close persistence cannot be updated.
- ETH/BTC remains below 0.0300.
- The current 15 July ETF session remains pending and must not be read as zero.
- Market-wide CVD and verified spot aggressor flow are unavailable.
- Official stablecoin aggregate and history are missing.
- Macro core series are missing.
- OKX data is venue-specific and cannot be treated as market-wide derivatives truth.

## Main-framework state

```text
ACTIVE_EVENT_ID: ROTATION_REPAIR_EDGE_20260712_01
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: DERIVATIVES_AND_LATEST_COMPLETED_ETF_OBSERVABILITY_RESTORED_BUT_CANONICAL_CLOSE_AND_MARKET_WIDE_FLOW_VERIFICATION_BLOCKED
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

## Operational conclusion

The OKX and Farside recoveries are meaningful operational repairs, not a market-state unlock. The current evidence remains consistent with a high-level hold and a still-live Type-2 candidate. Positive latest-session ETF flow removes the immediate two-negative-session path, but negative BTC rolling windows, weak short breadth and missing market-wide flow prevent clean breakout or rotation confirmation.

The correct action remains hold and wait. No chase, no new deployment and no trim are authorized from this packet.

## Research effect

This packet is eligible for prospective experiment rows only by available field. OKX derivatives and verified latest-completed ETF observations may participate in sensor-pair tests. Canonical close, spot-taker, market-wide CVD, official stablecoin and macro fields remain ineligible rather than negative.

For the SCTA holdout, P1 flow improved, P2's two-negative-session condition is not met, and P3 remains watch-only until the 12-session maturity mark.
