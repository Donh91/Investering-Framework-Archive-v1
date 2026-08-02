# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_fe496808649a7d5e3db0c033587afbc1
snapshot_id: snap_03949c287c10bc8a52c16476ea34bc03
snapshot_utc: 2026-08-01T17:51:41.284Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_91d8483f485146cc99b8c8de39d9a0ef
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_WITH_MEMBERSHIP_CHANGE_CAUTION
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted and the absolute current fields are usable. The run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation rather than the required accepted snapshot.

## Current market

```yaml
BTC_usd: 62777.99
ETH_usd: 1861.79
direct_ETHBTC: 0.02965
BTC_24h_pct: -0.581
ETH_24h_pct: -0.707
ETHBTC_24h_pct: -0.135
latest_Copenhagen_settled_ETHBTC_close: 0.02957
```

ETHBTC has recovered slightly from the preceding bounded reading of 0.02962, but the current ratio and the latest settled Copenhagen close remain below 0.0300. The terminated threshold sequence is not repaired.

## Breadth near the selective gate, with another membership discontinuity

```yaml
advancers: 42
decliners: 30
unchanged: 16
advance_ratio_pct: 47.7273
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.3420
prior_bounded_advance_ratio_pct: 39.3258
reported_change_percentage_points: 8.4014
membership_hash_changed: YES
raw_rows: 99
included_count: 88
gate_35_early_stabilization: MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The absolute breadth reading is the strongest since the collapse and is only 2.3 percentage points below the 50% selective gate. However, the membership hash changed again and the universe contains one fewer included row, so the full rise cannot be treated as an exact like-for-like constituent transition. The result supports improving conditions, but not yet a scored breadth permission.

## Price path and flow

```yaml
BTC_1h_return_pct: -0.1186
ETH_1h_return_pct: -0.0700
ETHBTC_1h_return_pct: 0.0
BTC_4h_return_pct: -0.2716
ETH_4h_return_pct: -0.0150
ETHBTC_4h_return_pct: 0.2702
BTC_12h_return_pct: -0.2894
ETH_12h_return_pct: -0.0519
ETHBTC_12h_return_pct: 0.1687
BTC_current_taker_ratio: 0.7284
ETH_current_taker_ratio: 0.8817
```

ETH is holding up better than BTC across four and twelve hours, and ETHBTC relative returns are constructive. Yet current taker flow has reverted below one for both assets, meaning the prior buy-side impulse has not persisted. Price breadth is improving faster than direct spot demand.

## Leverage and participation

```yaml
BTC_global_long_short_ratio: 2.0562
ETH_global_long_short_ratio: 2.6127
BTC_funding_rate: 0.00005372
ETH_funding_rate: 0.00004660
BTC_OI_24h_change_pct: -1.7562
ETH_OI_24h_change_pct: -1.0100
BTC_OI_4h_change_pct: 0.1545
ETH_OI_4h_change_pct: 0.2517
market_volume_change_24h_pct: -48.1894
```

Twenty-four-hour open interest has declined for both assets, which is a constructive leverage-cleaning feature. Long ratios remain elevated, open interest is rising again over four hours, and total market volume has contracted by almost half. The combination is too thin to treat the near-50 breadth reading as a robust accumulation base.

## Source boundaries

Public-web ETF and CFGI sources were unavailable in this run. The separately reconciled ETH ETF evidence through 30 July remains directionless around zero. The GeckoTerminal WRAP/WETH row is excluded from market interpretation because its reserve-volume relationship is a source-QA anomaly.

## Framework decision

```yaml
classification: BREADTH_NEAR_SELECTIVE_GATE_WITH_MEMBERSHIP_DISCONTINUITY_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_SELL_SIDE_TAKER_FLOW_EXTREME_VOLUME_CONTRACTION_PARTIAL_LEVERAGE_CLEANING_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It strengthens the stabilization case but does not cross the 50% breadth gate, repair ETHBTC threshold acceptance, establish persistent demand or create an independent policy event.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds another direct owner observation and an absolute breadth reading near 50%, but the changed membership hash and absent constituent sidecar prevent exact transition attribution. The pending extension and complete intraday owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_BETTER_WINDOW
risk_class_change: NONE
reassessment_horizon: 6_TO_12_HOURS_OR_EARLIER_IF_BREADTH_HOLDS_ABOVE_50_WITH_STABLE_MEMBERSHIP_AND_DIRECT_AND_SETTLED_ETHBTC_RECLAIM_0_0300
```

**Top-up og købsvindue:** Afvent yderligere 6–12 timer med top-ups, fordi breadth på 47,7% nærmer sig 50%-gaten, men membership-skiftet, ETH/BTC under 0,0300, salgssidet takerflow og næsten halveret volumen endnu ikke bekræfter et robust købsvindue.