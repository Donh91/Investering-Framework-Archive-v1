# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_20260803T122759180Z_7f3c9d1a
snapshot_id: snap_20260803T122759180Z_4b8e2c6f
snapshot_utc: 2026-08-03T12:27:59.180Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_DERIVATIVES_ETF_AND_SOURCE_QA_OBSERVATION_WITH_SUPERSEDED_BREADTH_METHOD
collector_predecessor_matches_required_canonical: NO
collector_predecessor: snap_20260803_mm_gapfill_001
required_canonical_predecessor: snap_0e19c112413d471d8270cad1a18148a7
canonical_longitudinal_deltas_accepted: NO
method_compatible_gapfill_comparison: DIAGNOSTIC_ONLY
current_absolute_market_accepted: YES
current_derivatives_accepted: YES
current_ETF_rows_accepted_as_RECONFIRMATION: YES
supplied_breadth_gate_authority: REJECTED_SUPERSEDED_FILTER_V1
accepted_as_next_market_predecessor: NO
accepted_as_latest_decision_bearing_bounded_observation: YES
```

The packet is materially stronger than the preceding bounded run on source coverage: all sixty core actions were attempted, direct ETF rows are present, breadth has a membership hash, and Binance/OKX derivatives are complete. It still cannot advance the canonical market predecessor because its declared predecessor is a Master Monday gap-fill rather than the canonical accepted market snapshot. The breadth hash proves reproducibility only for the supplied v1 universe; it does not repair compatibility with the current v1.1 economic universe.

## Current market

```yaml
BTC_usd: 62631.42
ETH_usd: 1842.91
direct_ETHBTC: 0.02942
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
BTC_12h_return_pct: -1.5888
ETH_12h_return_pct: -2.4117
ETHBTC_12h_return_pct: -0.8094
BTC_12h_close_location: 0.200625
ETH_12h_close_location: 0.196581
```

BTC and ETH are trading close to the lower end of their twelve-hour ranges. ETH has underperformed BTC over that window and direct ETH/BTC is back at 0.02942. The settled Copenhagen ratio of 0.02973 did not convert into live persistence above 0.0300. Rotation therefore remains closed.

## Change since the last decision-bearing bounded observation

The last bounded observation at 06:21 UTC recorded BTC 62,840, ETH 1,859.36 and ETH/BTC 0.02960. The present run is approximately:

```yaml
BTC_change_since_prior_bounded_pct: -0.3319
ETH_change_since_prior_bounded_pct: -0.8847
ETHBTC_change_since_prior_bounded_pct: -0.6081
BTC_OI_24h_change_acceleration_pp: +1.8316
ETH_OI_24h_change_acceleration_pp: +2.882855
BTC_global_long_short_change: +0.1628
ETH_global_long_short_change: +0.0855
BTC_futures_taker_ratio_change: -0.4321
ETH_futures_taker_ratio_change: -0.1327
```

This is a worse leverage/price combination: prices and ETH/BTC weakened while open interest and long crowding increased, and futures taker flow moved further below one. BTC funding cooled from the earlier 0.01% current print, and ETH current funding turned slightly negative, but the three-print means remain positive. Funding relief is therefore not yet enough to offset the rising OI and sell-side futures flow.

## Breadth treatment

```yaml
supplied_filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
supplied_advance_ratio_pct: 20.0
supplied_membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
current_verified_filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1
current_verified_reference_pct: 35.7142857143
v1_to_v1_1_longitudinal_comparison: FORBIDDEN
v1_absolute_gate_scoring: NOT_AUTHORIZED_CURRENT_FRAMEWORK
```

The 20% figure is not silently substituted for the verified 35.7% v1.1 reading. It is retained as directional corroboration that broad participation is not healthy, but no exact deterioration magnitude and no gate transition are scored from it. The last compatible breadth state remains above the early 35% line and below the 50% rotation gate.

## ETF treatment

The direct Farside rows confirm BTC +233.1M on 30 July followed by -265.4M on 31 July, while ETH printed +12.8M and +9.0M. This is consistent with the already reconciled W31 totals of BTC -61.5M and ETH +10.0M. Relative ETH support remains visible, but it is not a rotation unlock because ETH/BTC persistence and compatible breadth confirmation are absent.

## Support proximity and leverage risk

```yaml
Cycle_Navigator_BTC_primary_risk_level: 62200
current_BTC: 62631.42
BTC_12h_low: 62300.00
Cycle_Navigator_ETH_downside_condition: 1820
current_ETH: 1842.91
ETH_12h_low: 1828.62
BTC_OI_24h_change_pct: 2.13263
ETH_OI_24h_change_pct: 3.941295
BTC_futures_taker_buy_sell: 0.6161
ETH_futures_taker_buy_sell: 0.9346
```

Neither primary support condition is yet settled as broken, but both assets have tested close to their defensive thresholds while leverage has continued to build. This raises the probability of another flush or volatile support retest before a reliable accumulation window.

## Framework decision

```yaml
classification: BOUNDED_CURRENT_OWNER_DERIVATIVES_AND_ETF_RECONFIRMATION_WITH_INVALID_CANONICAL_LINEAGE_SUPERSEDED_BREADTH_V1_ETHBTC_BELOW_0030_PRICES_NEAR_SUPPORT_RISING_OI_LONG_CROWDING_AND_SELL_SIDE_FUTURES_FLOW
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
risk_class_change: NONE_DEFENSIVE_EVIDENCE_STRENGTHENED_WITHIN_EXISTING_STATE
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

The run strengthens the already ratified defensive action layer but does not create a new policy event. It must not overwrite the canonical predecessor, the v1.1 breadth reference, Master Monday, or Cycle Navigator #19.

## Required next confirmation

A safer upgrade requires all of the following in compatible data:

- BTC holds or reclaims 63.6–64.0K without renewed OI acceleration;
- ETH/BTC settles above 0.0300 for at least two Copenhagen sessions;
- v1.1 breadth exceeds 50% on at least two compatible captures;
- BTC and ETH futures taker ratios recover above one while long crowding cools.

A settled BTC close below 62.2K with OI still rising, or ETH below 1.82K, would strengthen the downside path and keep capital protection first.

**Top-up og købsvindue:** Afvent mindst de næste 6–12 timer og undlad nye top-ups, fordi BTC og ETH ligger tæt på 62,2K/1,82K-risikoniveauerne, ETH/BTC fortsat er under 0,0300, og stigende OI sammen med long-crowding og sell-side futuresflow gør endnu et flush mere sandsynligt end et sikkert købsvindue.