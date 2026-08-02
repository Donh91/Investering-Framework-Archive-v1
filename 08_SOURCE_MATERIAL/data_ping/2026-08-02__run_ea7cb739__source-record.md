# DATA PING source record

```yaml
run_id: run_ea7cb739da3846e0bf5657b2cf757b32
snapshot_id: snap_25c72fb925fd427cb44886fb7f1932f9
snapshot_utc: 2026-08-02T06:32:59.303Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
collector_status: PARTIAL
transport_occurrences_in_user_message: 2
transport_deduplication: IDENTICAL_PACKET_ACCEPTED_ONCE
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 54
core_PARTIAL: 1
core_STALE: 2
core_UNAVAILABLE: 3
core_FAIL: 0
optional_FAIL: 1
counts_reconciled: true
```

## Lineage

```yaml
collector_predecessor: snap_03949c287c10bc8a52c16476ea34bc03
collector_predecessor_run: run_fe496808649a7d5e3db0c033587afbc1
required_canonical_predecessor: snap_0e19c112413d471d8270cad1a18148a7
predecessor_matches_required: false
```

## Current direct fields

```yaml
BTCUSDT: 63485.64
ETHUSDT: 1877.64
ETHBTC_direct: 0.02958
BTC_24h_pct: 0.663
ETH_24h_pct: 0.388
ETHBTC_24h_pct: -0.236
breadth_advance_ratio: 0.4888888888888889
breadth_advancers: 44
breadth_decliners: 28
breadth_unchanged: 18
breadth_membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
market_volume_change_24h_pct: -36.59498213674286
```

## Source boundaries

- ETF rows were explicitly `STALE` and older than independently reconciled ETF evidence already held by the framework. They are retained for source QA only and may not overwrite the newer ETF ledger.
- CFGI global, BTC and ETH were unavailable.
- Stablecoin global total, total DeFi TVL and realized-volatility windows were unavailable.
- The packet was pasted twice with identical run and snapshot IDs; no second observation or receipt is created.
