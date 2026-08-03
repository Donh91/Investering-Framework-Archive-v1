# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_8a4f73c1d9e64bbba275efa260803621
snapshot_id: snap_5cc75db8af16450ea9cdb89b38ff6567
snapshot_utc: 2026-08-03T06:21:29.117Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_PARTIAL_BREADTH_DERIVATIVES_AND_SOURCE_QA_OBSERVATION
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_9c2e7b4a1f6d43b8a05e9172c64fd3ab
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_FOR_DIRECT_METHOD_COMPATIBLE_FIELDS
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted. Current market, settled owner, partial breadth and derivatives are usable. The run cannot advance the canonical predecessor because its declared predecessor is another bounded observation.

## Current market and settled owner

```yaml
BTC_usd: 62840.00
ETH_usd: 1859.36
direct_ETHBTC: 0.02960
BTC_24h_pct: -0.951
ETH_24h_pct: -0.872
ETHBTC_24h_pct: 0.135
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
```

The 2 August Copenhagen session contained a genuine one-session ETH leadership rebound and lifted settled ETHBTC from 0.02938 to 0.02973. The current direct ratio has since eased to 0.02960. Both values remain below 0.0300, so the terminated threshold sequence is not repaired and rotation permission remains closed.

## Breadth deterioration

```yaml
advancers: 22
decliners: 52
unchanged: 16
advance_ratio_pct: 24.4444
median_return_24h_pct: -0.5
absolute_gate_35: NOT_MET
absolute_gate_50: NOT_MET
absolute_gate_55: NOT_MET
membership_hash: NOT_AVAILABLE
longitudinal_same_membership_comparison: NOT_AUTHORIZED
```

The current absolute breadth reading is decisively weak and has fallen below the 35% early-stabilization reference. The packet reports a fall from 51.1%, but the membership hash is missing in both contexts, so the exact longitudinal magnitude is not scoreable as a same-universe transition. The current 24.4% absolute state is nevertheless independently decision-relevant and invalidates the previous tentative breadth improvement.

## Immediate flow versus broad participation

```yaml
BTC_1h_return_pct: 0.0592
ETH_1h_return_pct: 0.2647
ETHBTC_1h_return_pct: 0.2031
BTC_1h_taker_buy_quote_share: 0.5540
ETH_1h_taker_buy_quote_share: 0.5327
ETHBTC_1h_taker_buy_quote_share: 0.7948
BTC_current_taker_ratio: 1.0482
ETH_current_taker_ratio: 1.0673
```

The latest hour is mildly constructive and ETHBTC has buy-side flow. This is too narrow to offset the weak twenty-four-hour prices and 24.4% breadth. It is classified as an intrahour bounce inside a weak participation environment, not as broad accumulation confirmation.

## Funding, positioning and open interest

```yaml
BTC_Binance_funding: 0.00010000
ETH_Binance_funding: 0.00001559
BTC_three_settled_funding_mean: 0.00008883
ETH_three_settled_funding_mean: 0.00005680
BTC_global_long_short_ratio: 1.9958
ETH_global_long_short_ratio: 2.5039
BTC_top_account_ratio: 2.0893
ETH_top_account_ratio: 2.0609
BTC_OI_4h_change_pct: 0.1107
ETH_OI_4h_change_pct: 0.6277
BTC_OI_24h_change_pct: 0.3010
ETH_OI_24h_change_pct: 1.0584
```

Open interest is rising while both assets are lower over twenty-four hours, and long/short ratios are elevated. BTC funding is at 0.01%, with the settled three-print mean still high. This combination increases long-crowding and liquidation risk rather than supporting an immediate top-up.

## Venue and source treatment

Binance marks are below their indices, and Binance marks are also below OKX marks by about 8.3 bps for BTC and 11.0 bps for ETH. Public-web ETF and CFGI data were unavailable. No old ETF values are forward-filled. Stablecoin global total and DeFi total TVL remain unavailable. VIX recovered on bounded retry. The WRAP/WETH low-reserve pool is excluded as a source anomaly.

## Framework decision

```yaml
classification: ABSOLUTE_BREADTH_COLLAPSE_TO_24_BELOW_35_WITH_MEMBERSHIP_HASH_MISSING_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_ONE_HOUR_ETH_REBOUND_BUT_BROAD_PARTICIPATION_WEAK_LONG_HEAVY_POSITIONING_RISING_OI_ELEVATED_BTC_FUNDING_PUBLIC_WEB_UNAVAILABLE_AND_INVALID_PREDECESSOR_LINEAGE
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

The absolute breadth collapse and crowded leverage configuration outweigh the one-session ETHBTC improvement. This is same-cluster bounded evidence and does not create a new canonical policy event.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run supplies current owner, settled owner and derivatives evidence but still lacks the membership hash, point-in-time constituent sidecar, pending extension and canonical predecessor path. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: DO_NOT_ADD_RISK
required_next_object: MASTER_MONDAY_GAP_FILL_OR_NEXT_FULL_DATA_PING_WITH_HASH_AND_ETF_REVERIFICATION
reassessment_horizon: 6_TO_12_HOURS
```

**Top-up og købsvindue:** Undlad nye top-ups de næste 6–12 timer, fordi breadth er faldet til 24,4% under 35%-referencen, ETH/BTC stadig er under 0,0300, og stigende OI sammen med høj long-positionering og BTC-funding øger risikoen for endnu et tilbageslag.