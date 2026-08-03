# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_20260803T153028895Z_9c714e2a
snapshot_id: snap_20260803T153028895Z_6b2d8f41
snapshot_utc: 2026-08-03T15:30:28.895Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_DERIVATIVES_AND_SOURCE_QA_OBSERVATION_WITH_TEMPORAL_RECEIPT_ANOMALIES_AND_SUPERSEDED_BREADTH_METHOD
collector_predecessor_matches_required_canonical: NO
collector_predecessor: snap_20260803T122759180Z_4b8e2c6f
required_canonical_predecessor: snap_0e19c112413d471d8270cad1a18148a7
canonical_longitudinal_deltas_accepted: NO
same_thread_bounded_comparison: ACCEPTED_FOR_METHOD_COMPATIBLE_FIELDS
current_absolute_market_accepted: YES
current_derivatives_accepted: YES
current_ETF_numeric_update_accepted: NO
supplied_breadth_gate_authority: REJECTED_SUPERSEDED_FILTER_V1
accepted_as_next_market_predecessor: NO
accepted_as_latest_decision_bearing_bounded_observation: YES
```

The declared predecessor is the previous bounded observation, not the canonical market predecessor. The packet therefore cannot advance the canonical market chain. Its live spot, derivatives and same-method comparison against the previous bounded run are usable inside the bounded lane.

## Main-thread QA adjustment

```yaml
source_reported_PASS: 54
source_reported_PARTIAL: 3
source_reported_UNAVAILABLE: 3
main_thread_adjusted_PASS: 48
main_thread_adjusted_PARTIAL: 9
main_thread_adjusted_UNAVAILABLE: 3
downgraded_action_ids: [20,21,22,23,24,25]
reason: SOURCE_TIMESTAMPS_AFTER_FREEZE_OPEN_CANDLE_END_LABELS_NOT_SETTLED_TIMESTAMPS
```

Actions 20-22 report source timestamps at 21:59:59Z and actions 23-25 at 15:59:59Z, although the packet froze at 15:30:28Z. These six receipt rows are downgraded to temporal-partial. This does not remove the explicitly supplied settled 2 August daily rows, but it blocks the future timestamps from being treated as final observations.

The ETF missing-ledger rows also reference E3, which belongs to CFGI. ETF session identification is retained, but no current ETF numerical value is accepted from this run.

## Current market and bounded change

```yaml
BTC_usd: 63731.00
ETH_usd: 1866.58
direct_ETHBTC: 0.02927
settled_Copenhagen_ETHBTC_close: 0.02973
BTC_change_since_previous_bounded_pct: 1.7557
ETH_change_since_previous_bounded_pct: 1.2844
ETHBTC_change_since_previous_bounded_pct: -0.5099
BTC_24h_change_pct: 0.958
ETH_24h_change_pct: 0.422
ETHBTC_24h_change_pct: -0.577
BTC_24h_high: 63992.71
```

BTC has reclaimed the lower edge of the 63.6-64.0K confirmation band intraday and nearly tested 64K. ETH also rebounded, but less strongly, while ETH/BTC fell to 0.02927. The move is therefore BTC-led repair rather than rotation.

No settled persistence above 0.0300 exists. Rotation permission remains closed.

## Derivatives improvement and remaining asymmetry

```yaml
BTC_current_OI_change_from_previous_bounded_pct: -2.1696
ETH_current_OI_change_from_previous_bounded_pct: -0.2694
BTC_OI_24h_change_pct: -0.08324
ETH_OI_24h_change_pct: 3.66123
BTC_global_long_short_ratio: 1.7137
ETH_global_long_short_ratio: 2.5537
BTC_futures_taker_buy_sell: 1.0170
ETH_futures_taker_buy_sell: 1.1033
BTC_current_funding: 0.00003136
ETH_current_funding: 0.00003175
```

BTC shows meaningful short-term repair: price rose, current OI fell by 2.17% from the prior bounded run, the 24-hour OI change returned close to flat, long crowding cooled, and futures taker flow recovered above one.

ETH improved less cleanly. Current OI declined only slightly from the previous run and remains 3.66% higher over twenty-four hours. ETH long/short positioning remains elevated at 2.55, while ETH/BTC weakened. Positive taker flow reduces immediate pressure but does not neutralize the still-heavy ETH leverage configuration.

Funding is positive for both assets. The deleveraging evidence is therefore strongest in BTC and incomplete in ETH.

## Breadth treatment

```yaml
supplied_filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
supplied_previous_advance_ratio: 0.20
supplied_current_advance_ratio: 0.4333333333
supplied_membership_hash_match: true
same_v1_universe_rebound: VALID_DIAGNOSTIC
current_framework_filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1
latest_verified_v1_1_reference: 0.3571428571
current_v1_1_breadth: UNKNOWN
v1_gate_scoring_authority: NONE
```

The same-hash v1 comparison confirms a real rebound from 20% to 43.3% inside that old universe. It is useful as directional corroboration that participation improved during the BTC rebound. It cannot establish the current framework's 35%, 50% or 55% gates because v1 was superseded by v1.1. The current v1.1 breadth remains unknown, and the last compatible v1.1 reference remains 35.7%.

## Macro and market context

```yaml
crypto_total_market_cap_24h_pct: 0.7529
crypto_volume_24h_pct: 29.1040
BTC_dominance_change_since_previous_bounded_pp: 0.2696
ETH_dominance_change_since_previous_bounded_pp: -0.0052
VIX_latest: 15.99
```

The rebound occurred with substantially higher crypto volume and lower VIX. BTC dominance increased while ETH dominance was nearly flat to slightly lower, reinforcing the BTC-led interpretation.

## Framework decision

```yaml
classification: BOUNDED_BTC_LED_STABILIZATION_ATTEMPT_WITH_BTC_DELEVERAGING_AND_TAKER_RECOVERY_BUT_ETHBTC_WEAK_ETH_OI_STILL_HIGH_CURRENT_V1_1_BREADTH_UNKNOWN_TEMPORAL_RECEIPT_ANOMALIES_AND_NONCANONICAL_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
risk_substate: STABILIZATION_ATTEMPT_UNCONFIRMED
risk_class_change: NONE_IMMEDIATE_PRESSURE_EASED_NO_STATE_UPGRADE
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

The run is materially better than the 12:27 UTC observation, but it satisfies only part of the existing upgrade conditions. BTC has reclaimed the lower confirmation area intraday, OI pressure has eased in BTC, and taker flow recovered. Missing are a settled hold, ETH/BTC persistence above 0.0300, current compatible v1.1 breadth above 50%, and convincing ETH deleveraging.

The defensive state therefore remains intact, while the near-term downside pressure is reduced from acute to unconfirmed stabilization.

## Required confirmation

An upgrade still requires compatible evidence of:

- BTC holding 63.6-64.0K on settled confirmation without renewed OI acceleration;
- ETH/BTC settled above 0.0300 for at least two Copenhagen sessions;
- v1.1 breadth above 50% on at least two compatible captures;
- continued taker ratios above one while BTC and especially ETH long crowding and OI cool.

A loss of 63.6K followed by renewed OI expansion would classify the rebound as failed repair rather than confirmation.

**Top-up og købsvindue:** Afvent næste settled København-close eller mindst 6-12 timer og undlad nye top-ups endnu, fordi BTC's rebound og deleveraging er konstruktive, men ETH/BTC falder, ETH-leverage er fortsat høj, og den aktuelle v1.1-breadth ikke er verificeret.
