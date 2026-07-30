# DATA PING Framework Read

## Identity

```yaml
run_id: run_95c5ae6811704350a854fb1d1fff844a
snapshot_id: snap_609e377c7de24dfba3e4db211e448e46
snapshot_utc: 2026-07-30T16:51:14.252Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_SOURCE_QA
```

## Acceptance

The collector attempted all 60 core actions, so the absolute current CoinGecko, breadth, FRED, chain, DEX and OKX fields are usable as a bounded observation.

The run is not accepted as a longitudinal market predecessor because it declared `snap_bed564693b804b8c9c2b7476386abd3d`, which was explicitly retained as a bounded non-predecessor observation.

```yaml
bounded_market_observation: ACCEPTED
source_QA_ingest: ACCEPTED
packet_supplied_longitudinal_deltas: REJECTED
accepted_as_next_market_predecessor: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
```

## Current market

```yaml
BTC_CoinGecko_usd: 64745
ETH_CoinGecko_usd: 1915.79
ETHBTC_derived: 0.029589775272221792
total_market_cap_usd: 2294384474311.8335
total_volume_usd: 69321099743.06464
BTC_dominance_pct: 56.619093653292495
ETH_dominance_pct: 10.07954881171261
```

Main-framework rebinding to the last accepted market run gives:

```yaml
BTC_delta_pct: +1.5130
ETH_delta_pct: +1.1868
total_market_cap_delta_pct: +1.1561
total_volume_delta_pct: +16.0179
breadth_delta_percentage_points: +33.7079
```

A direct ETHBTC delta is not calculated because the last accepted value is direct owner data while the current ratio is derived from two USD legs.

## Breadth persistence

```yaml
advancers: 54
decliners: 20
unchanged: 15
advance_ratio_pct: 60.6742
median_return_24h_pct: +0.60
selective_gate_50: MET_BY_10.6742pp
broad_gate_55: MET_BY_5.6742pp
```

The immediately preceding bounded observation recorded breadth at 55.0562%. The current observation arrives 3 hours, 14 minutes and 54 seconds later and remains above 55%, with a further increase of 5.6180 percentage points.

```yaml
bounded_snapshot_1: 55.0562%
bounded_snapshot_2: 60.6742%
status: TWO_CONSECUTIVE_LIVE_SNAPSHOTS_ABOVE_55
settled_daily_persistence_claim: NO
```

This is stronger than a single marginal gate cross. It is still intraday live-snapshot persistence, not a settled daily confirmation.

## Breadth integrity boundary

The current membership hash is:

`db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739`

This matches the last accepted market run, which improves aggregate comparability. It differs from the immediately preceding bounded observation hash `49d41929bf0ebe9b7b16c37bb1e31d6808b0b199e0f051a17b766b41c12a6b81`.

Because neither bounded observation emitted the required constituent sidecar, the framework cannot determine whether the 5.6180 percentage-point breadth increase came from return transitions, membership turnover or both.

```yaml
aggregate_breadth_read: PERMITTED
constituent_transition_read: NOT_PERMITTED
membership_transition_attribution: UNKNOWN
sidecar_status: NOT_EMITTED
breadth_replayability: FAIL
```

This is the fourth consecutive live breach tracked in issue #224.

## Price and leverage follow-up

Relative to the prior bounded observation:

```yaml
BTC_price_delta_pct: -0.0401
ETH_price_delta_pct: -0.3428
ETHBTC_derived_delta_pct: -0.3028
total_market_cap_delta_pct: +0.1087
total_volume_delta_pct: +1.8402
BTC_OKX_OI_delta_pct: -0.0089
ETH_OKX_OI_delta_pct: -1.4692
```

Breadth expanded while BTC was flat, ETH softened and ETH open interest declined. This is more consistent with broader participation and some leverage cooling than with a fresh leverage-only acceleration.

Open interest remains above the last accepted baseline, however, and current funding is positive for both BTC and ETH. The leverage warning is therefore reduced intraday, not removed.

## ETHBTC owner gate

```yaml
direct_ETHBTC_owner: UNAVAILABLE_GEO_RESTRICTION
last_valid_direct_ETHBTC: 0.0297
last_valid_direct_gate: BELOW_0_0300
current_derived_ETHBTC: 0.029589775272221792
derived_distance_below_0_0300_pct: -1.3674
derived_gate_authority: NONE
```

The breadth improvement cannot independently authorize rotation. Direct ETHBTC owner evidence remains required.

## Framework decision

```yaml
classification: BROAD_BREADTH_INTRADAY_PERSISTENCE_WITH_FLAT_MAJORS_ETH_LEVERAGE_COOLING_DIRECT_ETHBTC_OWNER_UNAVAILABLE_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Prospective evidence

```yaml
observation_id: OBS-20260730-95c5ae68-BREADTH-PERSISTENCE-OWNER-OUTAGE
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

This is same-cluster follow-up evidence. It strengthens the breadth side of the setup but cannot create an independent rotation event while direct ETHBTC is absent.

## Deep capture

No new request is opened. `DCR-20260730-EVENT-003` is reused and extended to include:

- this second breadth snapshot above 55%;
- the intraday membership-hash transition;
- the later direct ETHBTC owner-recovery window;
- the exact 16:42:20Z point-in-time breadth sidecar, when retained.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
chase_ETH_or_large_caps: NO
add_new_risk: WAIT
market_read: BREADTH_NOW_CONSTRUCTIVE_BUT_ROTATION_NOT_RELEASED
next_key: DIRECT_ETHBTC_OWNER_RECOVERY_AND_SETTLED_FOLLOW_UP
```

The change is analytical, not an authorization to deploy capital.