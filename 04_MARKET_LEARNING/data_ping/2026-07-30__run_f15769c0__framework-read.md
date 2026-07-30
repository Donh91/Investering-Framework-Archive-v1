# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_f15769c054e94c9d9c48a72385b5cf19
snapshot_id: snap_748607ede85744af92c3e94878539287
snapshot_utc: 2026-07-30T21:46:24.921Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_AND_SOURCE_QA
is_duplicate: NO
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_155aa63ee97245cb8e4d763f113056e4
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
accepted_as_next_market_predecessor: NO
```

The absolute current market fields are usable. The run cannot advance the accepted market predecessor because its declared predecessor is the immediately preceding bounded observation, which has no longitudinal predecessor authority.

## Current market

```yaml
BTC_usd: 64764.38
ETH_usd: 1921.07
direct_ETHBTC: 0.02966
distance_to_0_0300_pct: -1.1333
BTC_dominance_pct: 56.57244779483326
ETH_dominance_pct: 10.100609626887977
total_market_cap_usd: 2295520921872.1294
total_volume_usd: 59503524596.50426
```

## Breadth rebound

```yaml
advancers: 66
decliners: 9
unchanged: 14
advance_ratio_pct: 74.1573
median_return_24h_pct: 1.50
selective_gate_50: MET
broad_gate_55: MET
prior_bounded_advance_ratio_pct: 43.8202
bounded_change_percentage_points: 30.3371
membership_hash_unchanged: YES
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
settled_daily_persistence_claim: NO
constituent_sidecar_available: NO
```

The unchanged membership hash makes the aggregate rebound more comparable than the earlier cross-hash observations: the included universe is unchanged, so the improvement is not caused by membership turnover. Exact constituent-level transition attribution remains unavailable because no sidecar was emitted.

This is a strong live breadth rebound, but it is also a rapid intraday reversal from below 50% to above 70%. It must therefore be treated as constructive but not yet durable.

## Relative leadership

```yaml
BTC_24h_pct: 1.741
ETH_24h_pct: 1.441
ETHBTC_24h_pct: -0.269
BTC_12h_pct: 0.7299
ETH_12h_pct: 0.3493
ETHBTC_12h_pct: -0.3694
relative_leader: BTC
ETHBTC_threshold_0_0300: BELOW
```

Broad altcoin participation improved, but the direct owner ratio did not confirm rotation. ETH/BTC remains below 0.0300 and BTC continues to outperform ETH over both the 12-hour and 24-hour views.

## Flow, leverage and risk

```yaml
BTC_taker_buy_sell_ratio: 1.1366
ETH_taker_buy_sell_ratio: 1.1108
spot_taker_state: BUY_SIDE_IMPROVED
BTC_funding_mean_latest_3: 0.00008256
ETH_funding_mean_latest_3: 0.00003502
BTC_OI_24h_change_pct: 3.2259
ETH_OI_24h_change_pct: 2.4794
OKX_BTC_OI_change_from_prior_bounded_pct: -1.2769
OKX_ETH_OI_change_from_prior_bounded_pct: -0.7350
volume_change_from_prior_bounded_pct: -7.9003
VIX: 20.66
VIX_daily_change: 2.45
```

The flow picture is mixed but improved: taker ratios are above one for both majors, while current OKX open interest has cooled relative to the prior bounded observation. However, 24-hour Binance open interest remains higher, funding is positive, market volume has fallen, and VIX rose materially. This does not support unrestricted risk deployment.

## ETF and missing-data boundary

The packet-supplied ETF values are stale at 2026-07-27 and are ignored for current-state interpretation. CFGI, the stablecoin global total and total DeFi TVL remain unavailable. These gaps do not invalidate the direct price and breadth observation, but they reduce confidence in a broad liquidity confirmation.

## Framework decision

```yaml
classification: STRONG_LIVE_BREADTH_REBOUND_WITH_STABLE_MEMBERSHIP_BUT_DIRECT_ETHBTC_BELOW_0030_BTC_RELATIVE_LEADERSHIP_LOWER_VOLUME_POSITIVE_FUNDING_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

This is same-cluster follow-up evidence. It upgrades the breadth side of the setup but does not authorize rotation or create a new independent prospective event because direct ETH/BTC remains below 0.0300, the collector lineage is invalid, and the breadth constituent sidecar is absent.

## Deep capture treatment

DCR-20260730-EVENT-003 remains open. The current run adds another direct owner observation and a strong current breadth aggregate with the same membership hash, but it does not execute the pending extension and does not recover the missing point-in-time constituent sidecars or complete intraday owner path.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
aggressive_top_up: NO
bounded_existing_high_conviction_top_up: SMALL_TRANCHE_ONLY
reserve_requirement: MAJORITY_RETAINED
reassessment_horizon: 1_TO_3_DAYS_OR_DIRECT_ETHBTC_ACCEPTANCE_ABOVE_0_0300_WITH_SURVIVING_BREADTH
```

**Top-up og købsvindue:** Køb højst en lille første tranche i de stærkeste eksisterende beholdninger nu og behold hovedparten i reserve de næste 1–3 dage, fordi breadth er genvundet kraftigt, men ETH/BTC stadig ligger under 0,0300 og BTC fortsat leder.
