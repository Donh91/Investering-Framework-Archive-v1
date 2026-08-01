# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_d90398dd4a78451a84a942a77d3ce9d6
snapshot_id: snap_d088d3d626ce4aed9b3543016ffa5474
snapshot_utc: 2026-08-01T04:38:46.132Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_b4ec0a26ced94e2496fb685ee6ab9be6
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_NONCANONICAL
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted and the absolute current fields are usable. The run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation rather than the required accepted market snapshot.

## Current market

```yaml
BTC_usd: 63046.01
ETH_usd: 1869.58
direct_ETHBTC: 0.02966
BTC_24h_pct: -1.988
ETH_24h_pct: -1.948
ETHBTC_24h_pct: 0.101
Copenhagen_settled_ETHBTC_close: 0.02957
```

ETH is marginally stronger than BTC over the current 24-hour window and ETHBTC has recovered intraday, but both the direct current ratio and the latest settled Copenhagen close remain below 0.0300. The failed threshold sequence has not been repaired.

## Breadth rebound, still below permission zones

```yaml
advancers: 28
decliners: 44
unchanged: 17
advance_ratio_pct: 31.4607
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: -0.0472
prior_decision_bearing_bounded_advance_ratio_pct: 13.4831
change_percentage_points: 17.9776
membership_hash_unchanged: YES
gate_35_early_stabilization: NOT_MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The rebound is real and directly comparable at the included-universe level because the membership hash is unchanged. It materially reduces the extremity of the previous breadth collapse, but 31.5% remains a weak absolute reading and is still below the early stabilization reference at 35%, as well as both operative breadth gates.

## Price path and flow

```yaml
BTC_4h_return_pct: 0.1854
ETH_4h_return_pct: 0.3909
ETHBTC_4h_return_pct: 0.2364
BTC_12h_return_pct: 0.4591
ETH_12h_return_pct: 0.3731
ETHBTC_12h_return_pct: -0.0673
BTC_current_taker_ratio: 0.6433
ETH_current_taker_ratio: 1.3866
BTC_12h_taker_buy_quote_share: 0.5169
ETH_12h_taker_buy_quote_share: 0.4064
```

The four-hour rebound is constructive, especially for ETH and ETHBTC, but it is not yet a durable relative-leadership shift. Very short-term taker flow is mixed: ETH is buy-side while BTC is strongly sell-side, and ETH's twelve-hour taker share remains below 50%.

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2321
ETH_global_long_short_ratio: 2.6832
BTC_top_account_ratio: 2.2830
ETH_top_account_ratio: 2.1656
BTC_funding_rate: 0.0000387
ETH_funding_rate: 0.00005574
BTC_OI_24h_change_pct: 3.9253
ETH_OI_24h_change_pct: 0.8389
BTC_OI_4h_change_pct: -0.4158
ETH_OI_4h_change_pct: 0.3906
```

Positioning remains long-heavy. BTC open interest has eased over four hours, but remains materially higher over twenty-four hours, while ETH open interest is still rising over four hours. This is not yet a clean leverage reset and keeps failed-rebound risk elevated.

## Source boundaries

Public-web ETF and CFGI sources were unavailable in this run. The previously accepted 30 July ETF values remain BTC +233.1 million USD and ETH +12.8 million USD; they are carried forward only as prior settled evidence and are not treated as a new flow update. The GeckoTerminal `WRAP / WETH` pool row is excluded from interpretation because its reported reserve-volume combination is a clear source-QA anomaly.

## Framework decision

```yaml
classification: PARTIAL_STABILIZATION_FROM_EXTREME_BREADTH_WEAKNESS_WITH_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_LONG_HEAVY_POSITIONING_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It weakens the immediate severity of the previous breadth-collapse reading but does not create an independent event, repair ETHBTC threshold acceptance or unlock any policy permission.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds another direct ETHBTC owner observation and a stable-membership breadth rebound. The pending extension, exact point-in-time constituent sidecars and complete owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
reassessment_horizon: 12_TO_24_HOURS_OR_EARLIER_IF_BREADTH_EXCEEDS_35_THEN_50_AND_SETTLED_ETHBTC_RECLAIMS_0_0300
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 12–24 timer, fordi breadth-rebounden til 31,5% er konstruktiv men stadig under stabiliseringszonen, mens settled ETH/BTC fortsat er 0,02957 og long-tung positionering gør rebounden skrøbelig.