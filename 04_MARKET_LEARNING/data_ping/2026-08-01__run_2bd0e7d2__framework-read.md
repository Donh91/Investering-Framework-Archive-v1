# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_2bd0e7d23ffb4cf88136ea631b165109
snapshot_id: snap_91d8483f485146cc99b8c8de39d9a0ef
snapshot_utc: 2026-08-01T13:16:16.635Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_685db69aef8844428134c86e180d88dd
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_WITH_MEMBERSHIP_CHANGE_CAUTION
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted and the absolute current fields are usable. The run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation rather than the required accepted market snapshot.

## Current market

```yaml
BTC_usd: 63102.58
ETH_usd: 1869.36
direct_ETHBTC: 0.02962
BTC_24h_pct: -0.984
ETH_24h_pct: -0.770
ETHBTC_24h_pct: 0.203
latest_Copenhagen_settled_ETHBTC_close: 0.02957
```

ETH remains marginally stronger than BTC over the current 24-hour window, but direct ETHBTC has slipped from 0.02966 to 0.02962 and the latest settled Copenhagen close remains 0.02957. The terminated 0.0300 threshold sequence remains unrepaired.

## Breadth above early reference, with membership discontinuity

```yaml
advancers: 35
decliners: 39
unchanged: 15
advance_ratio_pct: 39.3258
median_return_24h_pct: 0.0
prior_bounded_advance_ratio_pct: 29.2135
reported_change_percentage_points: 10.1124
membership_hash_changed: YES
gate_35_early_stabilization: MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The absolute reading has crossed the 35% early-stabilization reference for the first time after the collapse. However, the membership hash changed, so the full increase from 29.2% to 39.3% is not an exact like-for-like constituent transition. This is evidence of improving breadth conditions, not proof of durable broad participation.

## Price path and flow

```yaml
BTC_1h_return_pct: 0.0439
ETH_1h_return_pct: 0.1157
ETHBTC_1h_return_pct: 0.0675
BTC_4h_return_pct: 0.0801
ETH_4h_return_pct: -0.0321
ETHBTC_4h_return_pct: 0.0
BTC_12h_return_pct: 0.2610
ETH_12h_return_pct: 0.2258
ETHBTC_12h_return_pct: -0.0337
BTC_current_taker_ratio: 1.3806
ETH_current_taker_ratio: 1.7928
BTC_12h_taker_buy_quote_share: 0.5054
ETH_12h_taker_buy_quote_share: 0.4125
```

Current taker ratios are buy-side for both assets and are the strongest constructive element in this run. The longer twelve-hour ETH taker share remains below 50%, and ETHBTC is still flat-to-negative over four and twelve hours. Flow improvement is therefore early rather than persistent.

## Positioning, leverage and participation

```yaml
BTC_global_long_short_ratio: 2.1017
ETH_global_long_short_ratio: 2.6456
BTC_top_account_ratio: 2.1279
ETH_top_account_ratio: 2.1338
BTC_funding_rate: 0.00002576
ETH_funding_rate: 0.00004994
BTC_OI_24h_change_pct: 3.0025
ETH_OI_24h_change_pct: -0.6010
BTC_OI_4h_change_pct: -0.0936
ETH_OI_4h_change_pct: -0.2324
market_volume_change_24h_pct: -17.0069
```

Four-hour open interest has declined for both assets and ETH open interest is lower over twenty-four hours, which is a modest leverage-cleaning improvement. BTC open interest remains about 3% higher over twenty-four hours, long ratios remain elevated and market volume has contracted sharply. Participation is therefore still too weak for a robust accumulation signal.

## Source boundaries

Public-web ETF and CFGI sources were unavailable in this run. Separately reconciled ETH ETF evidence through 30 July remains directionless around zero and is not treated as a new flow update. The GeckoTerminal WRAP/WETH row is excluded from interpretation because its reserve-volume relationship is a clear source-QA anomaly.

## Framework decision

```yaml
classification: EARLY_BREADTH_STABILIZATION_ABOVE_35_WITH_MEMBERSHIP_DISCONTINUITY_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_BUY_SIDE_CURRENT_TAKER_FLOW_LOW_VOLUME_AND_INVALID_PREDECESSOR_LINEAGE
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

The reading is better than the prior stalled stabilization and reduces immediate downside urgency. It does not repair ETHBTC threshold acceptance, cross the 50% breadth gate or establish persistent participation. It remains same-cluster bounded follow-up evidence.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds a current direct owner observation and an absolute breadth reading above 35%, but the changed membership hash reinforces the need for exact point-in-time constituent sidecars. The extension and complete owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_BETTER_WINDOW
risk_class_change: DO_NOT_ADD_RISK_TO_WAIT_FOR_BETTER_WINDOW
reassessment_horizon: 12_TO_24_HOURS_OR_EARLIER_IF_BREADTH_HOLDS_ABOVE_35_AND_REACHES_50_WITH_DIRECT_AND_SETTLED_ETHBTC_RECLAIMING_0_0300
```

**Top-up og købsvindue:** Afvent fortsat 12–24 timer med top-ups, fordi breadth på 39,3% viser tidlig stabilisering men medlemsuniverset har ændret sig, mens ETH/BTC er faldet til 0,02962 og den kraftigt lavere volumen endnu ikke bekræfter et robust købsvindue.
