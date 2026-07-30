# DATA PING Framework Read

## Identity

```yaml
run_id: run_4dd78b1e713b4258aedcade193b29b8b
snapshot_id: snap_bed564693b804b8c9c2b7476386abd3d
snapshot_utc: 2026-07-30T13:36:19.781Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_SOURCE_QA
```

The preceding `run_7793a18a...` packet included in the same user message is an exact duplicate of an already archived QA-only run. It creates no new record.

## Acceptance and lineage

This run attempted all 60 core actions and produced usable current CoinGecko, breadth, FRED, chain, DEX and OKX observations. It is therefore more informative than the two runtime-exhausted attempts.

It is not accepted as the next longitudinal predecessor because it declared `snap_610937bd8f6c4be3adf836a2281c9328`, which belongs to a rejected QA-only run. The correct market predecessor remains:

```yaml
run_id: run_0bc8a5d0d0464542b29b4d50f2f8e19c
snapshot_id: snap_0e19c112413d471d8270cad1a18148a7
snapshot_utc: 2026-07-29T16:51:00.829Z
```

```yaml
bounded_market_observation: ACCEPTED
packet_supplied_longitudinal_deltas: REJECTED
accepted_as_next_market_predecessor: NO
source_QA_ingest: ACCEPTED
```

## Current market read

```yaml
BTC: 64771 USD
ETH: 1922.38 USD
ETHBTC_derived: 0.02967964
total_market_cap: 2.2919T USD
BTC_dominance: 56.6797%
ETH_dominance: 10.1145%
```

Main-framework rebinding to the last accepted market run gives:

```yaml
BTC_delta: +1.24%
ETH_delta: +1.46%
ETHBTC_derived_delta: +0.21%
total_market_cap_delta: +1.05%
total_volume_delta: +13.92%
BTC_dominance_delta: +0.0973 percentage points
ETH_dominance_delta: +0.0374 percentage points
```

This is a constructive price repair, but the derived ETHBTC ratio remains about 1.07% below 0.0300 and cannot replace the direct Binance owner series.

## Breadth

```yaml
advancers: 49
decliners: 32
unchanged: 8
advance_ratio: 55.0562%
median_return_24h: +0.20%
selective_gate_50: MET
broad_gate_55: MET_BY_ONLY_0.0562_PERCENTAGE_POINTS
```

The aggregate breadth level is usable as a current snapshot. It has crossed both the 50% and 55% gates, but only narrowly at the broad gate.

The membership hash changed from `db981d...` in the last accepted run to `49d419...` now. Current breadth may therefore be scored as an absolute aggregate, but constituent transition counts and direct membership-matched decomposition are not permitted.

No constituent sidecar was emitted, so breadth replayability remains `FAIL` under issue #224.

## Derivatives

```yaml
OKX_BTC_last: 64781.5
OKX_ETH_last: 1922.4
BTC_basis_bps: -4.38
ETH_basis_bps: -7.59
BTC_current_funding: +0.00630%
ETH_current_funding: approximately flat and slightly negative
BTC_OI_delta_vs_last_accepted: +2.98%
ETH_OI_delta_vs_last_accepted: +5.70%
```

Price and open interest have rebuilt together, particularly for ETH. This is a useful leverage-reentry warning, not rotation confirmation. ETH funding is not stretched, while both bases remain negative.

## Framework classification

```yaml
classification: BROAD_BREADTH_REBOUND_WITH_OWNER_ETHBTC_UNAVAILABLE_DERIVED_RATIO_BELOW_0_0300_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

Breadth has repaired materially, but direct ETHBTC authority is unavailable and the available derived ratio remains below the required level. Rotation permission therefore stays denied.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
chase_ETH_or_large_caps: NO
add_new_risk: WAIT
watch_condition: DIRECT_ETHBTC_OWNER_RECOVERY_PLUS_BREADTH_PERSISTENCE
```

The market is more constructive than at the last accepted ping, but this is not sufficient for deployment.

## Prospective evidence

```yaml
observation_id: OBS-20260730-4dd78b1e-BREADTH-REBOUND-OWNER-OUTAGE
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_policy_event: NO
new_A_class_receipt: NO
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
```

This is a same-cluster bounded follow-up. The policy decision remains unchanged, so counting another A-class denial would duplicate the same independent event.

## Deep capture

`DCR-20260730-EVENT-003` is opened because:

1. breadth is now above 50% and narrowly above 55%;
2. direct ETHBTC owner authority is unavailable;
3. the first fully settled daily follow-up after the 0.0300 acceptance can now be captured;
4. the exact current constituent snapshot should be recovered immediately if still retained.

The request has no canonical or portfolio authority.