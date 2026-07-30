# DATA PING Framework Read

## Identity

```yaml
run_id: run_5f1b7219edb64d48a5e9961ee7ce9849
snapshot_id: snap_155aa63ee97245cb8e4d763f113056e4
snapshot_utc: 2026-07-30T19:24:39.157Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OBSERVATION_WITH_DIRECT_OWNER_AND_SOURCE_QA
```

## Eligibility decision

```yaml
is_duplicate: NO
collector_predecessor_matches_required: NO
collector_predecessor: snap_609e377c7de24dfba3e4d763f113056e46
required_predecessor: snap_0e19c112413d471d8270cad1a18148a7
all_core_actions_attempted: YES
direct_ETHBTC_owner_available: YES
breadth_aggregate_available: YES
breadth_constituent_sidecar_available: NO
market_successor_eligible: NO
```

The collector used the immediately preceding bounded snapshot, which is explicitly prohibited as a longitudinal predecessor. Therefore:

```yaml
bounded_current_observation: ACCEPTED
source_QA_ingest: ACCEPTED
packet_supplied_longitudinal_deltas: REJECTED
accepted_as_next_market_predecessor: NO
```

## Current market

```yaml
BTC_Binance_usd: 64857.65
ETH_Binance_usd: 1924.95
direct_ETHBTC: 0.02968
BTC_24h_pct: 1.143
ETH_24h_pct: 1.067
BTC_dominance_pct: 56.5775
ETH_dominance_pct: 10.0809
total_market_cap_usd: 2292616555992.538
total_volume_usd: 64607711547.642
```

The direct ETHBTC owner is recovered, but the ratio remains `0.00032` below `0.0300`, approximately `1.07%` under the threshold.

## Rebinding to accepted baseline

The packet's own comparison is non-canonical because its predecessor is invalid. Using the archived accepted-baseline rebind chain only for bounded diagnostics gives approximately:

```yaml
BTC_vs_accepted_baseline_pct: +1.45
ETH_vs_accepted_baseline_pct: +1.26
total_market_cap_vs_accepted_baseline_pct: +1.08
total_volume_vs_accepted_baseline_pct: +8.13
breadth_vs_accepted_baseline_percentage_points: +16.85
rebind_authority: DIAGNOSTIC_ONLY_NOT_SUCCESSOR_LINEAGE
```

Majors remain above the last accepted baseline, but that does not override the failed rotation gates.

## Breadth relapse

```yaml
included_assets: 89
advancers: 39
decliners: 36
unchanged: 14
advance_ratio_pct: 43.8202
median_return_24h_pct: 0.0
selective_gate_50: NOT_MET_BY_6.1798pp
broad_gate_55: NOT_MET_BY_11.1798pp
prior_bounded_breadth_pct: 60.6742
bounded_change_percentage_points: -16.8540
```

The earlier two live snapshots above 55% did not persist. This is a material reversal of the breadth signal, even though it is retained as bounded same-cluster evidence rather than a canonical successor comparison.

The membership hash matches the prior 95c5 snapshot, which improves aggregate comparability. However, no constituent sidecar was emitted, so exact return-transition attribution remains unavailable.

```yaml
aggregate_breadth_read: PERMITTED
constituent_transition_read: NOT_PERMITTED
breadth_replayability: FAIL
```

## ETHBTC and relative leadership

```yaml
direct_ETHBTC: 0.02968
threshold_0_0300: NOT_MET
ETHBTC_12h_pct: -0.3029
ETHBTC_4h_pct: -0.0675
ETHBTC_1h_pct: 0.0
BTC_12h_pct: +1.0950
ETH_12h_pct: +0.7868
relative_leader_12h: BTC
```

The direct owner recovery resolves uncertainty about the current ratio but does not improve the gate. The post-acceptance sequence remains `SINGLE_SESSION_ACCEPTANCE_THEN_REJECTION`, with current owner data still below `0.0300`.

## Positioning and leverage

```yaml
BTC_funding_latest3_mean: 0.0000825633
ETH_funding_latest3_mean: 0.0000350167
BTC_OI_change_24h_pct: +3.2311
ETH_OI_change_24h_pct: +1.1720
BTC_taker_buy_sell_ratio: 0.9628
ETH_taker_buy_sell_ratio: 0.8962
BTC_global_long_short_ratio: 1.2482
ETH_global_long_short_ratio: 2.0120
BTC_Binance_basis_bps: -4.2927
ETH_Binance_basis_bps: -3.5764
```

OI has risen with price over 24 hours, but current taker flow is below 1 for both assets and ETH positioning is long-heavy. Funding is positive while basis remains slightly negative. This is mixed positioning, not clean broad risk-on confirmation.

## Macro and source limits

Yields and VIX eased in the latest available FRED observations, which is mildly supportive. The packet's ETF values are stale at 27 July and are not permitted to overwrite the newer OTA reconciliation. CFGI and stablecoin global total remain unavailable.

## H7 and experiment treatment

H7 remains matured and scored after five settled rows. This run is a post-maturity follow-up only.

```yaml
H7_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
H7_score_change: NONE
H7_follow_through: WEAKENED
new_policy_event: NO
new_A_class_receipt: NO
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
```

## DCR-003 treatment

This packet supplies useful supplemental owner evidence:

- current direct ETHBTC owner state is recovered;
- settled direct follow-up is corroborated;
- breadth aggregate and membership hash are current.

It does not execute the existing DCR extension and does not recover:

- exact requested 16:42:20 constituent sidecar;
- exact two-snapshot constituent transition;
- complete 1h and 5m owner rows in the transmitted packet;
- challenger-venue ETH/BTC path.

```yaml
DCR_003_status: PARTIAL_OWNER_RECOVERY_FROM_NONCANONICAL_DATA_PING_EXTENSION_STILL_UNEXECUTED
new_DCR_required: NO
```

## Framework decision

```yaml
classification: BREADTH_RELAPSE_BELOW_50_WITH_DIRECT_ETHBTC_OWNER_RECOVERED_BELOW_0030_BTC_RELATIVE_LEADERSHIP_MIXED_LEVERAGE_AND_INVALID_PREDECESSOR_LINEAGE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: HOLD
canonical_state_change: NONE
accepted_market_predecessor_change: NONE
```

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
chase_altcoins: NO
top_up_now: NO
capital_reserve: KEEP_MAJORITY_AVAILABLE
next_key: BREADTH_RECOVERY_ABOVE_50_TO_55_PLUS_DIRECT_ETHBTC_ACCEPTANCE_ABOVE_0_0300
```

**Top-up og købsvindue:** Afvent cirka 2–4 dage med hovedparten af købene, fordi breadth er faldet tilbage under 50%, og direkte ETH/BTC stadig ligger under 0,0300, hvilket øger sandsynligheden for et bedre købsvindue.
