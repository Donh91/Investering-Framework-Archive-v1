# DATA PING framework read — run_aa5ebdf331d34cd8bb27d71a71198cbe

**Snapshot UTC:** 2026-07-29T00:11:40.027Z  
**Collector status:** PARTIAL, usable for main-thread ingest  
**Framework predecessor on GitHub:** `run_4fd139e79f5b4a1ba4d7d5c4c2d6aa10`  
**Collector-declared predecessor:** `snap_1c77e4a6b3f24e3ca66f0a92c36f955d`  
**Lineage note:** the collector-declared predecessor was not located in the current canonical archive during this run. No missing packet was reconstructed.

## Framework classification

```yaml
classification: ETH_RELATIVE_STRENGTH_PERSISTS_AT_NEW_COPENHAGEN_SETTLEMENT_BOUNDARY_WITH_GATE_VALUE_AND_BREADTH_UNRESOLVED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Market read

```yaml
BTCUSDT_live: 64069.99
BTCUSDT_24h_high_low: 62742.47-64200.00
ETHUSDT_live: 1925.29
ETHUSDT_24h_high_low: 1856.88-1929.67
ETHBTC_live: 0.03006
ETHBTC_24h_high_low: 0.02953-0.03012
ETHBTC_12h_return_pct: 1.690419
ETHBTC_24h_return_pct: 0.367156
ETHBTC_12h_taker_buy_share: 0.612812
BTC_OI_24h_change_pct: -2.320224
ETH_OI_24h_change_pct: -0.580165
```

ETH continued to outperform BTC and remained above 0.0300 live after a new Copenhagen daily settlement boundary. The packet confirms that the relevant daily candle ended at `2026-07-28T21:59:59.999Z`, but it does not expose the settled ETHBTC OHLC row or exact close. A live value after settlement cannot be substituted for the missing settled close.

BTC and ETH traded near the upper part of their 24-hour ranges while open interest fell over 24 hours. This is more consistent with spot-led repair and position reduction than a fresh leverage expansion. Funding remained positive but not extreme. ETHBTC spot-taker share remained above 60% over 1h, 4h and 12h, supporting persistent relative demand.

## Missing decision-critical evidence

```yaml
settled_Copenhagen_ETHBTC_daily_close: UNKNOWN
breadth_aggregate: UNKNOWN
breadth_membership_hash: UNKNOWN
ETF_BTC_current: UNKNOWN
ETF_ETH_current: UNKNOWN
CFGI_global_BTC_ETH: UNKNOWN
stablecoin_global_total: UNKNOWN
realized_volatility_24h_72h_168h: UNKNOWN
collector_predecessor_archive_pointer: UNRESOLVED
```

The raw Top-100 pages were collected, but the final breadth aggregate was not completed before freeze. Missing breadth is `UNKNOWN`, not negative evidence. Public-web unavailability also prevents current ETF and CFGI updates.

## Prospective evidence adjudication

```yaml
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_independent_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total_after_run: 1
reason: SAME_ROTATION_ATTEMPT_WITH_NEW_SETTLEMENT_BOUNDARY_BUT_DECISION_VALUE_MISSING
```

The run remains inside the existing 0.0300 rotation-attempt cluster. Because the exact settled daily close is absent, no settled acceptance or rejection decision can be frozen from this packet. A second A-class row would therefore be both unsupported and potentially duplicative.

## Deep-capture adjudication

```yaml
request_id: DCR-20260729-EVENT-001
request_type: EVENT_DRIVEN_DEEP_CAPTURE
trigger_classes:
  - ETHBTC_THRESHOLD
  - BREADTH
  - SOURCE_INTEGRITY
status: PREPARED
canonical_effect: NONE
portfolio_effect: NONE
```

A bounded recovery request is justified because a registered ETHBTC threshold event crossed a new settlement boundary while the exact settled gate value and breadth aggregate are unavailable. The request is limited to the missing settlement row, the already-collected Top-100 breadth rows and a narrow event window. It does not request a duplicate full DATA PING.

## RAW prospective view frozen after ingest

```yaml
forecast_freeze_utc: 2026-07-29T04:58:35Z
source_snapshot_utc: 2026-07-29T00:11:40.027Z
RAW_1_3D: CONSTRUCTIVE_BUT_NARROW_AND_CATALYST_SENSITIVE
RAW_5_7D: REPAIR_CAN_EXTEND_BUT_ROTATION_AND_BROAD_PARTICIPATION_REMAIN_UNCONFIRMED
forecast_authority: PROSPECTIVE_RESEARCH_ONLY
portfolio_authority: NONE
```
