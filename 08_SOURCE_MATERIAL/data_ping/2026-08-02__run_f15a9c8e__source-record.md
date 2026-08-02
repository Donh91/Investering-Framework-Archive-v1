# DATA PING source record

```yaml
run_id: run_f15a9c8e1d6b4a0f9e3c72b8145d6f20
snapshot_id: snap_9c2e7b4a1f6d43b8a05e9172c64fd3ab
snapshot_utc: 2026-08-02T17:33:41.038Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
PASS: 54
PARTIAL: 1
UNAVAILABLE: 5
FAIL_core: 0
optional_FAIL: 1
collector_predecessor_id: snap_3f013c5404c144e0bbeb9d7a976c364d
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Current direct observations

```yaml
BTCUSDT: 63302.00
ETHUSDT: 1867.51
ETHBTC_direct: 0.02950
BTC_24h_pct: 0.742
ETH_24h_pct: 0.244
ETHBTC_24h_pct: -0.472
settled_Copenhagen_ETHBTC_close: 0.02938
breadth_advance_ratio: 0.511111111111
breadth_advancers: 46
breadth_decliners: 24
breadth_unchanged: 20
breadth_membership_hash: NOT_MATERIALIZED_BEFORE_FREEZE
BTC_current_taker_ratio: 1.6210
ETH_current_taker_ratio: 1.5115
BTC_Binance_funding: 0.00008551
ETH_Binance_funding: 0.00000758
BTC_OI_4h_change_pct: 0.157662
ETH_OI_4h_change_pct: 0.150770
market_volume_change_24h_pct: 9.4313
```

## Source boundaries

Public-web ETF and CFGI endpoints were unavailable. Stablecoin global total and DeFi total TVL were unavailable. The breadth aggregate was materialized, but its membership hash was not materialized before freeze. The GeckoTerminal WRAP/WETH row remains a low-reserve anomaly and is not used for market interpretation.

This file preserves the supplied packet as a compact source record. Framework interpretation is stored separately.