# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_828270a191a344ebb848f18725e561a5
snapshot_id: snap_14af341f78aa43ca8b34d0cd2c0b7ca8
snapshot_utc: 2026-07-31T17:05:06.612Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_3540e1d4d3fe4e288a5cdebe40b80135
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
accepted_as_next_market_predecessor: NO
```

The current absolute fields are usable, but this run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation.

## Current market

```yaml
BTC_usd: 62916.00
ETH_usd: 1867.29
direct_ETHBTC: 0.02969
BTC_24h_pct: -2.998
ETH_24h_pct: -2.751
ETHBTC_24h_pct: 0.304
BTC_24h_low: 62466.00
ETH_24h_low: 1848.70
```

ETH is losing slightly less than BTC and ETHBTC has improved intraday, but the direct ratio remains below 0.0300 and has not regained settled acceptance.

## Breadth deterioration

```yaml
advancers: 15
decliners: 57
unchanged: 17
advance_ratio_pct: 16.8539
median_return_24h_pct: -0.70
gate_50: NOT_MET
gate_55: NOT_MET
prior_bounded_advance_ratio_pct: 28.0899
membership_hash_unchanged: YES
constituent_sidecar_available: NO
```

The stable membership hash makes the aggregate deterioration from 28.1% to 16.9% directly comparable at the included-universe level. The absence of a constituent sidecar still prevents exact asset-level replay, but the absolute reading is severe and unambiguously risk-off for broad altcoin participation.

## Positioning and leverage

```yaml
BTC_global_long_short_ratio: 2.2723
ETH_global_long_short_ratio: 2.6337
BTC_top_account_ratio: 2.4459
ETH_top_account_ratio: 2.2884
BTC_taker_buy_sell_ratio: 1.2564
ETH_taker_buy_sell_ratio: 1.3824
BTC_OI_4h_change_pct: 4.6365
ETH_OI_4h_change_pct: 0.4756
BTC_funding_rate: 0.00008122
ETH_funding_rate: 0.00000166
```

Buy-side taker flow has improved during the selloff, but it is accompanied by elevated long ratios and rising open interest. This combination can represent dip buying, yet it also increases liquidation and failed-rebound risk. It is not sufficient to override the breadth collapse.

## Macro and liquidity boundary

VIX fell to 17.09 on the latest available observation, which is a constructive macro offset. Public-web ETF and CFGI sources were unavailable in this run. The previously accepted 30 July ETF prints remain BTC +233.1 million and ETH +12.8 million; they are not overwritten, but they do not neutralize the current market weakness.

## Framework decision

```yaml
classification: SEVERE_STABLE_MEMBERSHIP_BREADTH_WEAKNESS_WITH_DIRECT_ETHBTC_BELOW_0030_INTRADAY_RELATIVE_IMPROVEMENT_BUT_RISING_LEVERAGE_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It restores direct owner visibility but shows that the broad altcoin environment has weakened further. It does not create an independent prospective event or unlock any portfolio permission.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds current direct ETHBTC owner data and a severe, stable-membership breadth reading. The pending extension, exact point-in-time breadth sidecars and complete owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
reassessment_horizon: 1_TO_2_DAYS_OR_BREADTH_ABOVE_50_WITH_SETTLED_ETHBTC_ACCEPTANCE_ABOVE_0_0300
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 1–2 dage, fordi breadth er kollapset til 16,9%, ETH/BTC stadig er under 0,0300, og stigende open interest sammen med meget long-tung positionering øger risikoen for endnu et ben ned.
