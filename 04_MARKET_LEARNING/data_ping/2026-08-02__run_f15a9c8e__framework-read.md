# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_f15a9c8e1d6b4a0f9e3c72b8145d6f20
snapshot_id: snap_9c2e7b4a1f6d43b8a05e9172c64fd3ab
snapshot_utc: 2026-08-02T17:33:41.038Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_PARTIAL_BREADTH_DERIVATIVES_AND_SOURCE_QA_OBSERVATION
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_3f013c5404c144e0bbeb9d7a976c364d
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_FOR_DIRECT_METHOD_COMPATIBLE_FIELDS
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted. Current absolute market, flow and derivatives fields are usable. The run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation.

## Current market

```yaml
BTC_usd: 63302.00
ETH_usd: 1867.51
direct_ETHBTC: 0.02950
BTC_24h_pct: 0.742
ETH_24h_pct: 0.244
ETHBTC_24h_pct: -0.472
latest_Copenhagen_settled_ETHBTC_close: 0.02938
```

BTC and ETH have recovered in USD, but BTC still leads relatively. Direct ETHBTC has improved from 0.02942 to 0.02950 while remaining below 0.0300, and the latest settled Copenhagen close remains 0.02938. The terminated threshold sequence is therefore not repaired.

## Breadth above 50, but not scoreable

```yaml
advancers: 46
decliners: 24
unchanged: 20
advance_ratio_pct: 51.1111
median_return_24h_pct: 0.1
included_count: 90
absolute_gate_35: MET
absolute_gate_50: MET
absolute_gate_55: NOT_MET
membership_hash: NOT_AVAILABLE
longitudinal_same_membership_comparison: NOT_AUTHORIZED
scored_selective_permission: NOT_ACCEPTED_MEMBERSHIP_HASH_MISSING
constituent_sidecar_available: NO
```

The absolute breadth aggregate has crossed the 50% selective reference. However, the membership hash was not materialized before freeze, so the increase from the prior 47.8% cannot be certified as a same-universe transition. The current aggregate is constructive absolute evidence, but it is provisional and cannot create a scored breadth permission.

## Short-window recovery and flow

```yaml
BTC_1h_return_pct: 0.1129
ETH_1h_return_pct: 0.2319
ETHBTC_1h_return_pct: 0.1358
BTC_1h_taker_buy_quote_share: 0.5482
ETH_1h_taker_buy_quote_share: 0.6419
ETHBTC_1h_taker_buy_quote_share: 0.6233
BTC_current_taker_ratio: 1.6210
ETH_current_taker_ratio: 1.5115
```

The newest one-hour window is positive across BTC, ETH and ETHBTC, and both current taker ratios have returned clearly above one. This reverses the prior immediate sell-side deterioration and supports a short-term stabilization read.

## Participation, leverage and venue structure

```yaml
market_volume_change_24h_pct: 9.4313
BTC_Binance_funding: 0.00008551
ETH_Binance_funding: 0.00000758
BTC_OKX_funding: 0.00003503
ETH_OKX_funding: -0.00000857
BTC_OI_4h_change_pct: 0.1577
ETH_OI_4h_change_pct: 0.1508
BTC_OI_24h_change_pct: -0.0835
ETH_OI_24h_change_pct: -1.3388
BTC_Binance_minus_OKX_mark_bps: 6.1979
ETH_Binance_minus_OKX_mark_bps: 5.8216
```

Volume has improved materially and short-window open interest growth is modest rather than extreme. ETH funding has cooled sharply on Binance and is negative on OKX. BTC Binance funding remains elevated and both Binance marks remain above OKX, so the move is not yet a clean cross-venue spot-led confirmation.

## Source boundaries

Public-web ETF and CFGI sources were unavailable in this run. No stale values are used. The independently reconciled ETF ledger remains unchanged. Stablecoin global total and DeFi total TVL remain unavailable. The GeckoTerminal WRAP/WETH row is excluded as a low-reserve source anomaly.

## Framework decision

```yaml
classification: ABSOLUTE_BREADTH_ABOVE_50_UNSCORED_WITH_MEMBERSHIP_HASH_MISSING_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_SHORT_WINDOW_BUY_SIDE_RECOVERY_VOLUME_IMPROVEMENT_MODEST_OI_REBUILD_ELEVATED_BTC_FUNDING_VENUE_DIVERGENCE_PUBLIC_WEB_UNAVAILABLE_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
operational_risk_class: WAIT_FOR_BETTER_WINDOW
risk_class_change: UPGRADE_FROM_DO_NOT_ADD_RISK
canonical_state_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

The absolute breadth pass and improved immediate flow justify reversing the prior operational downgrade. They do not authorize a top-up because membership continuity is unverified, ETHBTC remains below 0.0300, the collector lineage is invalid and BTC funding remains elevated.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds an absolute breadth reading above 50 and current direct owner data, but the missing membership hash, point-in-time constituent sidecar, pending extension and exact canonical predecessor path prevent scored transition acceptance. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_BETTER_WINDOW
reassessment_horizon: 3_TO_6_HOURS_OR_EARLIER_IF_BREADTH_REMAINS_ABOVE_50_WITH_MATERIALIZED_STABLE_MEMBERSHIP_HASH_AND_DIRECT_AND_SETTLED_ETHBTC_RECLAIM_0_0300_WITH_BTC_FUNDING_COOLING
```

**Top-up og købsvindue:** Afvent yderligere 3–6 timer med top-ups, fordi breadth på 51,1% og buy-side flow viser bedring, men membership-hashen mangler, ETH/BTC fortsat er 0,02950 under 0,0300, og BTC-funding stadig er forhøjet.