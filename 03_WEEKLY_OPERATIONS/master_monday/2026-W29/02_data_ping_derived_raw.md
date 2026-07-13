# Master Monday — DATA PING-derived raw

**Dato:** 2026-07-13  
**Week:** 2026-W29  
**Status:** DATA_PING_DERIVED  
**Source snapshot:** `DATA_PING_V4_20260713T150608Z`  
**Verified previous week:** `VERIFIED_WEEKLY_RANGE_2026W28_20260713T060943977Z`  
**Data quality:** LOW  
**Can drive Cycle Navigator:** NO, unless ratified in `03_framework_ratified_final.md`

---

## Source integrity

```yaml
accepted_log_readback: PASS
accepted_log_hash: PASS
latest_payload_timestamp_utc: 2026-07-13T15:06:08Z
spot_source: COINGECKO_FALLBACK
current_etf_session: PENDING
futures: MISSING
market_wide_cvd: UNAVAILABLE
official_stablecoin_history: MISSING
macro_core: UNAVAILABLE
current_direct_ethbtc: MISSING
```

No missing field is inferred or carried forward as current.

---

## W28 verified outcome

```yaml
btc_actual_range_usdt: 61306.84-64700.00
btc_weekly_close_usdt: 63920.40
eth_actual_range_usdt: 1713.44-1833.40
eth_weekly_close_usdt: 1812.28
ethbtc_direct_range: 0.02758-0.02843
ethbtc_direct_close: 0.02835
```

The preserved W28 forecast was BTC `60,900-65,400` and ETH `1,540-1,760`.

Unscored outcome read:

- BTC remained fully inside the preserved forecast band.
- The expected recovery-range structure with an upside test was directionally correct.
- ETH exceeded the forecast ceiling, showing stronger relative repair than forecast.
- ETH/BTC held above `0.0275`, but did not reach `0.0300`.
- Broad rotation was not confirmed.

Official scoring remains blocked because the W28 ratified-source lineage is unresolved. Forecast values remain frozen and may only be used as unscored history.

---

## Current market snapshot

```yaml
btc_usd: 62667
eth_usd: 1777.83
btc_dominance_pct: 56.0357
ethbtc_derived: 0.0283695
latest_verified_btc_close: 63920.40
latest_verified_eth_close: 1812.28
btc_prior_closes_above_61900: 10
btc_prior_closes_above_63300: 3
ethbtc_prior_closes_above_0275: 11
btc_current_band: ABOVE_61900_BELOW_63300
ethbtc_current_structure: DERIVED_ABOVE_0275_BELOW_0300_DIRECT_MISSING
```

Breadth:

```yaml
breadth_1h_pct: 88.57
breadth_24h_pct: 8.57
breadth_7d_pct: 37.14
fixed_sample: 35
```

ETF, latest completed session 2026-07-10:

```yaml
btc_latest_usd_m: 90.4
btc_3session_usd_m: -89.8
btc_5session_usd_m: 197.4
btc_7session_usd_m: 124.9
btc_10session_usd_m: -773.2
eth_latest_usd_m: 18.4
eth_3session_usd_m: 36.7
eth_5session_usd_m: 84.3
eth_7session_usd_m: 128.1
eth_10session_usd_m: 57.8
```

Stablecoin proxy is contracting with LOW confidence. Stablecoin dominance rose mainly because total crypto market cap fell. It is one activity family and must not be double-counted.

---

## DATA PING-derived interpretation

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: TRIGGERED
ACTIVE_EVENT: ROTATION_REPAIR_EDGE_20260712_01
EVENT_STATUS: OPEN_TRIGGERED
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
```

W28 validated real price repair. Monday has not invalidated that repair, because BTC remains above `61.9K` and ETH/BTC remains above `0.0275`. However, current BTC is back below `63.3K`, 24H and 7D breadth are weak, direct current ETH/BTC is unavailable, and current-session ETF/futures/CVD/stablecoin confirmation is incomplete.

The correct state is therefore:

```text
Repair edge near present.
Open triggered observation.
Not organic broad recovery.
Not rotation.
Not permission to rebuy.
```

---

## Sensor-governance status

```yaml
A1_A2_urgency: ACTIVE_CONTEXT_ONLY
A3_quarantine: MAINTAINED
C2_forward_instrumentation: SOURCE_READY_ACCEPTED_LOG
C2_mature_rows: 0
D_confirmation_veto_role: MAINTAINED
A_C_D_blended_score: FORBIDDEN
btc_d_b1_canonical_fire_count: 22
btc_d_b1_live_warning_reactivation: NO
breadth_blocker: ACTIVE
prospective_evidence_validity: PASS_SOURCE_CHAIN
prospective_evidence_maturity: OPEN_NOT_MATURE
prospective_evidence_coverage: INSUFFICIENT_FOR_PROMOTION
```

---

## Raw horizon read

### 1–3 days

Constructive-fragile. The immediate battle is `61.9K` support versus a reclaim of `63.3K`. A short bounce can occur because 1H breadth is strong, but it is not trustworthy while 24H breadth remains below 10%.

### 5–7 days

Base case is another repair/range test rather than a clean breakout or broad rotation. BTC can preserve the repair while alts remain selective. The active event should be judged by survival, not by the first green session.

### 2–3 weeks

The path remains conditional:

```text
BTC support survival
→ 63.3K reclaim and hold
→ 64.7K/65.4K test
→ direct ETH/BTC persistence
→ breadth survival
→ deployment confirmation
→ selective large-cap permission
```

Failure before breadth and deployment would be another ETF-era repair attempt, not a confirmed transition.
