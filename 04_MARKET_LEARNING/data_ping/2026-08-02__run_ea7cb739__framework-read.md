# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_ea7cb739da3846e0bf5657b2cf757b32
snapshot_id: snap_25c72fb925fd427cb44886fb7f1932f9
snapshot_utc: 2026-08-02T06:32:59.303Z
transport_duplicate: YES_IDENTICAL_PACKET_DEDUPED
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_MARKET_OBSERVATION_WITH_DIRECT_OWNER_BREADTH_DERIVATIVES_AND_SOURCE_QA
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_03949c287c10bc8a52c16476ea34bc03
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_WITH_MEMBERSHIP_CHANGE_CAUTION
accepted_as_next_market_predecessor: NO
```

The two packet copies in the user message are byte-equivalent at the semantic identity level and are ingested once. All sixty core actions were attempted. Current absolute market fields are usable, but the run cannot advance the canonical market predecessor because its declared predecessor is another bounded observation.

## Current market

```yaml
BTC_usd: 63485.64
ETH_usd: 1877.64
direct_ETHBTC: 0.02958
BTC_24h_pct: 0.663
ETH_24h_pct: 0.388
ETHBTC_24h_pct: -0.236
latest_Copenhagen_settled_ETHBTC_close_from_reconciled_H7_row11: 0.02938
```

BTC and ETH have rebounded in USD, but BTC is outperforming ETH and direct ETHBTC remains below 0.0300. The latest reconciled settled Copenhagen close is 0.02938, so the terminated threshold sequence remains unrepaired.

## Breadth just below the selective gate

```yaml
advancers: 44
decliners: 28
unchanged: 18
advance_ratio_pct: 48.8889
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.3733
prior_bounded_advance_ratio_pct: 47.7273
reported_change_percentage_points: 1.1616
membership_hash_changed: YES
included_count: 90
configured_exclusion_count: 11
observed_excluded_count: 10
gate_35_early_stabilization: MET
gate_50_selective: NOT_MET
gate_55_broad: NOT_MET
constituent_sidecar_available: NO
```

The absolute breadth reading is the strongest in the recent rebound and is only 1.1 percentage points below the 50% selective gate. The membership hash changed again and included count moved from 88 to 90, so the reported increase cannot be treated as exact like-for-like transition evidence. Breadth is improving, but no scored permission has been crossed.

## Price path and flow

```yaml
BTC_1h_return_pct: -0.2150
ETH_1h_return_pct: -0.2594
ETHBTC_1h_return_pct: -0.0676
BTC_4h_return_pct: 0.7485
ETH_4h_return_pct: 1.0360
ETHBTC_4h_return_pct: 0.2713
BTC_12h_return_pct: 1.1884
ETH_12h_return_pct: 0.7664
ETHBTC_12h_return_pct: -0.3706
BTC_4h_taker_buy_quote_share: 0.5418
BTC_12h_taker_buy_quote_share: 0.5245
ETH_4h_taker_buy_quote_share: 0.5202
ETH_12h_taker_buy_quote_share: 0.4500
```

The four-hour rebound is constructive and taker share is buy-side over four hours for both assets. Persistence is incomplete: ETH's twelve-hour taker share remains below 50%, ETHBTC is negative over twelve hours and the final one-hour window is weak.

## Leverage, funding and participation

```yaml
BTC_Binance_funding: 0.00009818
ETH_Binance_funding: 0.00008266
BTC_OKX_funding: 0.00004041
ETH_OKX_funding: -0.00000580
BTC_OI_24h_change_pct: -0.0994
ETH_OI_24h_change_pct: -0.7705
BTC_OI_4h_change_pct: 0.4113
ETH_OI_4h_change_pct: 0.9673
market_volume_change_24h_pct: -36.5950
```

Twenty-four-hour open interest remains modestly lower, but both assets are rebuilding open interest over four hours. Binance funding is elevated, particularly for BTC, and diverges materially from OKX. Combined with volume still down about 36.6%, the rebound is vulnerable to leverage-driven reversal and does not yet resemble a clean spot-led accumulation base.

## ETF and source treatment

The packet exposed BTC ETF data only through 28 July and ETH ETF data only through 27 July. Both rows are explicitly stale and older than the independently reconciled framework ledger, which already contains BTC through 29 July and ETH through 30 July. The packet's ETF values are retained for source QA only and are forbidden from overwriting the newer ledger. CFGI remained unavailable.

## Framework decision

```yaml
classification: BREADTH_JUST_BELOW_50_WITH_MEMBERSHIP_DISCONTINUITY_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_ELEVATED_BINANCE_FUNDING_RECENT_OI_REBUILD_LOW_VOLUME_STALE_ETF_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. Breadth is close to the selective gate, but ETHBTC remains below threshold, membership is discontinuous, funding is elevated and participation is still thin. No independent policy event or purchase permission is created.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds direct owner data and an absolute breadth reading near 50%, but the changed membership hash, missing constituent sidecar and invalid predecessor prevent exact transition scoring. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_BETTER_WINDOW
risk_class_change: NONE
reassessment_horizon: 6_TO_12_HOURS_OR_EARLIER_IF_BREADTH_HOLDS_ABOVE_50_WITH_STABLE_MEMBERSHIP_AND_DIRECT_AND_SETTLED_ETHBTC_RECLAIM_0_0300_WITH_FUNDING_COOLING
```

**Top-up og købsvindue:** Afvent yderligere 6–12 timer med top-ups, fordi breadth på 48,9% endnu ikke har passeret 50%-gaten, ETH/BTC fortsat ligger under 0,0300, og høj Binance-funding med ny firetimers OI-opbygning gør rebounden for skrøbelig til et robust købsvindue.
