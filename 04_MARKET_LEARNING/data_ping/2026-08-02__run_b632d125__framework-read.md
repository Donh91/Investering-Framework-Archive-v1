# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_b632d125165c4cf7a882a73f22a40333
snapshot_id: snap_3f013c5404c144e0bbeb9d7a976c364d
snapshot_utc: 2026-08-02T12:29:17.344Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA_OBSERVATION
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_4652543565bd4c05a8e02a803a70f0e6
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_immediate_bounded_predecessor: ACCEPTED_FOR_DIRECT_METHOD_COMPATIBLE_FIELDS_ONLY
diagnostic_breadth_comparison_to_last_valid_same_membership_run: ACCEPTED
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted. Current absolute market, breadth and derivatives fields are usable, but the run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation.

## Current market

```yaml
BTC_usd: 63212.01
ETH_usd: 1858.99
direct_ETHBTC: 0.02942
BTC_24h_pct: 0.172
ETH_24h_pct: -0.484
ETHBTC_24h_pct: -0.608
latest_Copenhagen_settled_ETHBTC_close: 0.02938
```

BTC is approximately flat to slightly positive over twenty-four hours while ETH is negative. Direct ETHBTC has fallen from 0.02958 to 0.02942 since the prior bounded owner observation and is only 0.00004 above the latest settled Copenhagen close. Both direct and settled values remain below 0.0300, so the terminated threshold sequence is not repaired.

## Breadth below the selective gate

```yaml
advancers: 43
decliners: 28
unchanged: 19
advance_ratio_pct: 47.7778
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.3744
membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
last_valid_same_membership_breadth_pct: 48.8889
change_from_last_valid_same_membership_percentage_points: -1.1111
gate_35_early_stabilization: MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The current membership hash matches the last valid breadth run, `run_ea7cb739da3846e0bf5657b2cf757b32`. The decline from 48.9% to 47.8% is therefore directly comparable and shows that the rebound has slipped rather than crossed the selective gate. The intervening parse-failure run is not forward-filled and does not interrupt this same-membership diagnostic comparison.

## Price path and flow

```yaml
BTC_1h_return_pct: -0.2738
ETH_1h_return_pct: -0.8658
ETHBTC_1h_return_pct: -0.6425
BTC_4h_return_pct: -0.7468
ETH_4h_return_pct: -1.2537
ETHBTC_4h_return_pct: -0.5753
BTC_12h_return_pct: 0.3316
ETH_12h_return_pct: 0.4136
ETHBTC_12h_return_pct: 0.0340
BTC_current_taker_ratio: 0.7586
ETH_current_taker_ratio: 0.5607
BTC_4h_taker_buy_quote_share: 0.4914
ETH_4h_taker_buy_quote_share: 0.4297
```

The latest one- and four-hour windows are negative across BTC, ETH and ETHBTC, with ETH materially weaker than BTC. Current taker ratios are sell-side for both assets, and four-hour taker buy-share is below 50% for both. The remaining positive twelve-hour return is therefore backward-looking and does not represent current spot-demand confirmation.

## Funding, leverage and venue structure

```yaml
BTC_Binance_funding: 0.00009197
ETH_Binance_funding: 0.00004594
BTC_OKX_funding: -0.00001812
ETH_OKX_funding: 0.00001615
BTC_OI_4h_change_pct: -0.0008
ETH_OI_4h_change_pct: -0.9837
BTC_OI_24h_change_pct: 0.0527
ETH_OI_24h_change_pct: -1.4308
BTC_OKX_OI_usd_change_from_prior_pct: 1.9916
ETH_OKX_OI_usd_change_from_prior_pct: 0.1698
market_volume_change_24h_pct: -22.3025
```

ETH open interest is falling on Binance alongside falling price, which is a partial leverage reduction rather than fresh long expansion. BTC Binance funding nevertheless remains elevated while OKX funding is negative, showing a material venue divergence. Volume contraction has improved from the prior extreme but remains substantial. This combination does not support a clean, broad, spot-led accumulation base.

## ETF and source treatment

The packet's BTC ETF row ends on 28 July and its ETH row ends on 27 July. Both are explicitly stale and older than the independently reconciled framework ledger. They are retained for source QA only and cannot overwrite newer evidence. CFGI remained unavailable. The GeckoTerminal WRAP/WETH row is excluded from market interpretation because of its low-reserve anomaly.

## Framework decision

```yaml
classification: SAME_MEMBERSHIP_BREADTH_RESLIP_BELOW_50_WITH_DIRECT_ETHBTC_NEAR_SETTLED_LOW_ETH_UNDERPERFORMANCE_SELL_SIDE_TAKER_FLOW_ELEVATED_BTC_BINANCE_FUNDING_VENUE_DIVERGENCE_PARTIAL_ETH_LEVERAGE_REDUCTION_STALE_ETF_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
risk_class_change: DOWNGRADE_FROM_WAIT_FOR_BETTER_WINDOW
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

This is same-cluster bounded follow-up evidence. The current breadth remains below 50% and has slipped on an unchanged universe, while ETHBTC and current flow have weakened. The observation therefore reverses the prior tentative improvement in operational risk class but does not create a canonical policy event or portfolio action.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run restores a valid deterministic breadth aggregate and same-membership comparison, but the point-in-time constituent sidecar, pending extension, exact canonical predecessor path and complete intraday owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
reassessment_horizon: 6_TO_12_HOURS_OR_EARLIER_IF_BREADTH_CLOSES_ABOVE_50_WITH_STABLE_MEMBERSHIP_DIRECT_AND_SETTLED_ETHBTC_RECLAIM_0_0300_AND_CURRENT_TAKER_FLOW_RETURNS_BUY_SIDE
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 6–12 timer, fordi breadth er gledet tilbage til 47,8% på samme medlemsunivers, ETH/BTC er faldet til 0,02942 tæt på settled 0,02938, og både de korte prisvinduer og det aktuelle takerflow er tydeligt salgssidede.