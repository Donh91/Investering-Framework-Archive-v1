# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_a6843a76a2ab4d47a32cb3e6492d03ce
snapshot_id: snap_b4ec0a26ced94e2496fb685ee6ab9be6
snapshot_utc: 2026-07-31T23:35:19.436Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_54bda23836584972bfef107098e467ae
collector_predecessor_class: RUNTIME_LIMITED_SOURCE_QA_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted and the absolute current fields are usable. The run cannot advance the canonical market predecessor because its collector predecessor is a runtime-limited QA snapshot rather than the required accepted market snapshot.

## Current market

```yaml
BTC_usd: 62981.94
ETH_usd: 1864.01
direct_ETHBTC: 0.02960
BTC_24h_pct: -3.015
ETH_24h_pct: -3.348
ETHBTC_24h_pct: -0.303
Copenhagen_settled_BTC_close: 62947.78
Copenhagen_settled_ETH_close: 1861.81
Copenhagen_settled_ETHBTC_close: 0.02957
```

ETH continues to underperform BTC and the new settled Copenhagen ETHBTC close remains materially below 0.0300. The direct current ratio also remains below the gate. The earlier single-session threshold acceptance has not recovered.

## Severe stable-membership breadth weakness

```yaml
advancers: 12
decliners: 60
unchanged: 17
advance_ratio_pct: 13.4831
median_return_24h_pct: -0.90
equal_weight_mean_return_24h_pct: -0.8517
gate_50: NOT_MET
gate_55: NOT_MET
prior_decision_bearing_bounded_advance_ratio_pct: 16.8539
membership_hash_unchanged: YES
constituent_sidecar_available: NO
```

Because the membership hash is unchanged from the preceding decision-bearing bounded observation, the aggregate deterioration from 16.9% to 13.5% is directly comparable at the included-universe level. Exact asset-level replay remains unavailable without the point-in-time constituent sidecar.

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2082
ETH_global_long_short_ratio: 2.6284
BTC_top_account_ratio: 2.3681
ETH_top_account_ratio: 2.2744
BTC_taker_buy_sell_ratio: 0.9975
ETH_taker_buy_sell_ratio: 0.9289
BTC_funding_rate: 0.00004933
ETH_funding_rate: 0.00007215
BTC_OI_24h_change_pct: 2.8526
ETH_OI_24h_change_pct: -0.5389
BTC_OI_4h_change_pct: -0.3989
ETH_OI_4h_change_pct: -0.4333
```

Long positioning remains elevated while current taker flow is neutral-to-sell-side, especially for ETH. Four-hour open interest has eased slightly, but BTC open interest remains higher over twenty-four hours. This does not yet show a clean leverage reset or a durable rebound base.

## ETF, macro and source boundaries

The settled 30 July ETF prints remain BTC +233.1 million USD and ETH +12.8 million USD. They are supportive but are one session old and do not outweigh current breadth and relative-strength deterioration. VIX remained 17.09 on the latest available macro observation. CFGI was stale or unavailable and does not influence the current decision.

## Framework decision

```yaml
classification: SEVERE_STABLE_MEMBERSHIP_BREADTH_DOWNTREND_WITH_SETTLED_ETHBTC_BELOW_0030_ETH_UNDERPERFORMANCE_LONG_HEAVY_POSITIONING_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It strengthens the defensive reading but does not create an independent prospective event or unlock any policy permission.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds another current direct ETHBTC owner observation, a new settled Copenhagen close and a severe stable-membership breadth aggregate. The pending extension, exact point-in-time breadth sidecars and complete owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
reassessment_horizon: 2_TO_4_DAYS_OR_EARLIER_IF_BREADTH_RECOVERS_ABOVE_35_THEN_50_AND_SETTLED_ETHBTC_RECLAIMS_0_0300
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 2–4 dage, fordi breadth er faldet videre til 13,5%, den nye settled ETH/BTC-close er 0,02957, og long-tung positionering med svagt takerflow fortsat gør endnu et flush mere sandsynligt end et stabilt købsvindue.
