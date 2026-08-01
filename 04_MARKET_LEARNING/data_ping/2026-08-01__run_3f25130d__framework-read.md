# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_3f25130db9c1450b8db4b0e2ea078e75
snapshot_id: snap_685db69aef8844428134c86e180d88dd
snapshot_utc: 2026-08-01T07:39:54.779Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_d088d3d626ce4aed9b3543016ffa5474
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_NONCANONICAL
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted and the absolute current fields are usable. The run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation rather than the required accepted market snapshot.

## Current market

```yaml
BTC_usd: 63041.29
ETH_usd: 1869.39
direct_ETHBTC: 0.02966
BTC_24h_pct: -1.429
ETH_24h_pct: -0.898
ETHBTC_24h_pct: 0.542
Copenhagen_settled_ETHBTC_close: 0.02957
```

ETH is relatively stronger than BTC over the current 24-hour window, but the direct ETHBTC ratio is unchanged from the prior bounded observation and the latest settled Copenhagen close remains below 0.0300. The terminated threshold sequence is not repaired.

## Breadth stabilization has stalled below permission zones

```yaml
advancers: 26
decliners: 47
unchanged: 16
advance_ratio_pct: 29.2135
median_return_24h_pct: -0.10
equal_weight_mean_return_24h_pct: -0.1393
prior_decision_bearing_bounded_advance_ratio_pct: 31.4607
change_percentage_points: -2.2472
membership_hash_unchanged: YES
gate_35_early_stabilization: NOT_MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The same included universe has slipped from 31.5% to 29.2%. This does not recreate the earlier 13.5% extreme, but it shows that the first rebound has not yet developed into persistent breadth recovery. The reading remains below the early 35% stabilization reference and both operative breadth gates.

## Price path and flow

```yaml
BTC_1h_return_pct: 0.0962
ETH_1h_return_pct: 0.1564
ETHBTC_1h_return_pct: 0.1012
BTC_4h_return_pct: 0.0088
ETH_4h_return_pct: 0.1204
ETHBTC_4h_return_pct: 0.1350
BTC_12h_return_pct: -0.0268
ETH_12h_return_pct: -0.0705
ETHBTC_12h_return_pct: -0.0337
BTC_current_taker_ratio: 0.7228
ETH_current_taker_ratio: 1.2065
BTC_12h_taker_buy_quote_share: 0.4957
ETH_12h_taker_buy_quote_share: 0.4143
```

Very short-term ETH and ETHBTC flow is constructive, but the twelve-hour path remains flat-to-negative and ETH's twelve-hour taker share is still well below 50%. BTC taker flow is explicitly sell-side. This is a fragile rebound rather than durable relative rotation.

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2041
ETH_global_long_short_ratio: 2.6738
BTC_top_account_ratio: 2.2373
ETH_top_account_ratio: 2.1586
BTC_funding_rate: 0.00003639
ETH_funding_rate: 0.00002532
BTC_OI_24h_change_pct: 3.3924
ETH_OI_24h_change_pct: 0.3459
BTC_OI_4h_change_pct: 0.0430
ETH_OI_4h_change_pct: 0.2226
```

Long positioning remains elevated. Open interest is still higher over twenty-four hours and has stopped declining over four hours. Together with the 12.3% fall in market volume, this does not provide a clean leverage reset or high-confidence accumulation base.

## Source boundaries

Public-web ETF and CFGI sources were unavailable in this run. The separately reconciled ETH ETF evidence through 30 July remains oscillating around zero and is not a new directional input here. The GeckoTerminal WRAP/WETH row is excluded from interpretation because its reported reserve-volume combination is a clear source-QA anomaly.

## Framework decision

```yaml
classification: PARTIAL_STABILIZATION_STALLED_WITH_STABLE_MEMBERSHIP_BREADTH_RESLIP_TO_29_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_LONG_HEAVY_POSITIONING_LOW_VOLUME_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It shows that the initial breadth rebound has paused below the stabilization zone. It does not create an independent event, repair ETHBTC threshold acceptance or unlock any policy permission.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds another direct ETHBTC owner observation and a stable-membership breadth reslip. The pending extension, exact point-in-time constituent sidecars and complete owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
reassessment_horizon: 12_TO_24_HOURS_OR_EARLIER_IF_BREADTH_EXCEEDS_35_THEN_50_AND_SETTLED_ETHBTC_RECLAIMS_0_0300
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 12–24 timer, fordi breadth er faldet tilbage til 29,2% efter den første rebound, ETH/BTC fortsat er 0,02966 med settled close 0,02957, og lavere volumen kombineret med long-tung positionering viser, at stabiliseringen endnu ikke er robust.
