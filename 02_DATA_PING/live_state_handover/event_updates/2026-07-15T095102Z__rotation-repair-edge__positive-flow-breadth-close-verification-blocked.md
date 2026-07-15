# Rotation Repair Edge — Positive Flow and Breadth, Close Verification Blocked

**Accepted run:** `DATA_PING_V4_20260715T095102Z`  
**Review time:** 2026-07-15T10:03:26Z  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Data quality:** LOW

## Framework decision

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: STRENGTHENED — CLOSE VERIFICATION BLOCKED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
PORTFOLIO_ACTION: NONE
```

## New positive evidence

- CoinGecko fallback placed BTC at 64,680, still above the 63.3K reclaim level.
- Derived ETH/BTC was 0.029072, above 0.0285 and below the 0.0300 confirmation gate.
- Breadth was broad across all measured horizons: 74.3% at 1H, 85.7% at 24H and 62.9% at 7D.
- The latest completed 14 July ETF session was positive for both BTC (+181.1M) and ETH (+58.3M).
- Price, breadth and the latest completed ETF session were aligned positively.

## Verification blockers

- Binance Spot and Futures were unavailable because of an explicit eligibility-location error.
- The settled 14 July CEST BTC, ETH and ETH/BTC closes remain missing and were not inferred from prior partial candles.
- No new hourly close ledger or persistence extension is available.
- Direct ETH/BTC, spot-taker flow, funding, OI, basis and leverage measurements are missing.
- The stablecoin proxy cohort is incomplete and not cross-ping comparable.
- Current 15 July ETF session remains pending.

Missing fields remain UNKNOWN rather than negative. Earlier verified intraday persistence remains historical evidence but is not extended by this run.

## SCTA July-14 holdout cross-check

- The 14 July BTC ETF session was positive, so the frozen P2 condition requiring two contradictory completed ETF sessions is **not met**.
- The flow component of P1 improved because ETF flow stopped contradicting on the second completed session.
- P1 as a whole remains unresolved because truth-layer completed CEST close confirmation is unavailable in this run.
- P3 remains watch-only and cannot be judged before the 12-session maturity mark.

## Lineage

The run declares `DATA_PING_V4_20260714T203757Z` as its predecessor. No readable accepted receipt or payload for that run was found in the canonical archive. The gap is preserved explicitly and no missing packet is reconstructed.

CN #16 remains frozen. This run is prospective outcome evidence only.
