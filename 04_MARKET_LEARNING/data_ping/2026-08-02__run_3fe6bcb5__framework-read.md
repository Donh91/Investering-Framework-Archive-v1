# DATA PING Framework Read

## Identity and acceptance

```yaml
run_id: run_3fe6bcb574124cdcbcd763f808c18439
snapshot_id: snap_4652543565bd4c05a8e02a803a70f0e6
snapshot_utc: 2026-08-02T09:34:39.531Z
collector_status: PARTIAL_ALL_CORE_ACTIONS_ATTEMPTED
main_framework_acceptance: BOUNDED_CURRENT_OWNER_AND_DERIVATIVES_OBSERVATION_WITH_BREADTH_AGGREGATE_UNAVAILABLE
collector_predecessor_matches_required: NO
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor: snap_25c72fb925fd427cb44886fb7f1932f9
collector_predecessor_class: BOUNDED_NON_PREDECESSOR
packet_supplied_longitudinal_deltas: REJECTED_AS_CANONICAL
diagnostic_comparison_to_prior_bounded_observation: ACCEPTED_FOR_DIRECT_METHOD_COMPATIBLE_FIELDS_ONLY
accepted_as_next_market_predecessor: NO
```

All sixty core actions were attempted. The run provides current direct market feeds and derivatives, but cannot advance the canonical predecessor because its declared predecessor is another bounded observation. It also cannot produce a current breadth decision because deterministic aggregation failed after the raw CoinGecko rows were retrieved.

## Current market

```yaml
BTC_usd: 63292.01
ETH_usd: 1872.73
direct_ETHBTC: 0.02958
BTC_24h_pct: 0.284
ETH_24h_pct: 0.141
ETHBTC_24h_pct: -0.202
settled_Copenhagen_ETHBTC_close: 0.02938
```

BTC and ETH remain above their prior settled closes in USD, but BTC continues to outperform ETH. Direct ETHBTC is unchanged from the preceding bounded observation and remains below 0.0300. The latest settled Copenhagen close of 0.02938 confirms that the terminated threshold sequence is not repaired.

## Breadth decision unavailable

```yaml
current_breadth_aggregate: UNAVAILABLE_PARSE_FAILURE
raw_top100_rows_available: YES
membership_hash: null
prior_valid_breadth_pct: 48.8889
prior_valid_breadth_status: PRIOR_EVIDENCE_ONLY_NOT_CURRENT
breadth_gate_35_current: UNKNOWN_NOT_EVALUATED
breadth_gate_50_current: UNKNOWN_NOT_EVALUATED
breadth_gate_55_current: UNKNOWN_NOT_EVALUATED
forward_fill_prior_breadth: FORBIDDEN
```

The raw pages cannot be manually reconstructed or forward-filled under the collector contract. The previous 48.9% reading remains useful historical context but cannot be treated as a current gate result. This is a material decision-coverage loss because the prior observation sat only 1.1 percentage points below the 50% selective gate.

## Price path and flow

```yaml
BTC_1h_return_pct: -0.4917
ETH_1h_return_pct: -0.4211
ETHBTC_1h_return_pct: 0.0677
BTC_4h_return_pct: -0.6228
ETH_4h_return_pct: -0.6916
ETHBTC_4h_return_pct: -0.0676
BTC_12h_return_pct: 0.8488
ETH_12h_return_pct: 1.6204
ETHBTC_12h_return_pct: 0.7839
BTC_current_taker_ratio: 0.4681
ETH_current_taker_ratio: 0.6290
BTC_4h_taker_buy_quote_share: 0.5742
ETH_4h_taker_buy_quote_share: 0.4406
```

The twelve-hour path still contains a recovery, especially for ETH, but the latest one- and four-hour price windows have rolled over. The instantaneous taker ratios are sharply sell-side for both assets. BTC retains buy-side settled-window taker share over four hours, while ETH remains below 50%, so the newest flow deterioration is not a broad spot-demand confirmation.

## Funding, leverage and venue divergence

```yaml
BTC_Binance_funding: 0.00008497
ETH_Binance_funding: 0.00006701
BTC_OKX_funding: 0.00002298
ETH_OKX_funding: 0.00001938
BTC_OI_4h_change_pct: 0.1367
ETH_OI_4h_change_pct: 0.3289
BTC_OI_24h_change_pct: -0.0172
ETH_OI_24h_change_pct: -0.7156
BTC_Binance_minus_OKX_mark_bps: 12.1174
ETH_Binance_minus_OKX_mark_bps: 8.9091
```

Funding has cooled from the previous Binance snapshot but remains elevated relative to OKX. Open interest is rebuilding over four hours while the latest price windows weaken. The positive Binance-versus-OKX mark gaps are unusually large and reduce confidence that the rebound is a clean, uniform spot-led move. Twenty-four-hour OI is flat to lower, so leverage has not fully re-expanded, but the short-window direction remains adverse for immediate top-up timing.

## ETF and source treatment

The packet's BTC and ETH ETF rows are stale and older than the reconciled framework ledger. They are retained only as source-QA evidence and are forbidden from overwriting the newer ledger. CFGI remained unavailable. The GeckoTerminal WRAP/WETH row is excluded from market interpretation because of its low-reserve anomaly.

## Framework decision

```yaml
classification: CURRENT_OWNER_WEAKENING_WITH_BREADTH_AGGREGATE_UNAVAILABLE_DIRECT_AND_SETTLED_ETHBTC_BELOW_0030_SELL_SIDE_CURRENT_TAKER_FLOW_ELEVATED_CROSS_VENUE_FUNDING_RECENT_OI_REBUILD_STALE_ETF_AND_INVALID_PREDECESSOR_LINEAGE
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

This is same-cluster bounded follow-up evidence. It does not create a new policy event because the current breadth gate is unavailable, ETHBTC remains below threshold, the collector lineage is invalid and direct short-window flow has weakened.

## DCR treatment

DCR-20260730-EVENT-003 remains open. This run adds current owner and derivatives evidence but fails to materialize the current breadth aggregate. The missing membership hash, point-in-time constituent sidecar, pending extension and complete intraday owner path remain unresolved. Reuse DCR-003; do not create DCR-004.

## Operational translation

```yaml
existing_positions: HOLD
new_microcaps: NO
additional_top_up_now: WAIT_FOR_BETTER_WINDOW
risk_class_change: NONE
reassessment_horizon: NEXT_FULL_DATA_PING_IN_3_TO_6_HOURS_OR_EARLIER_IF_VALID_BREADTH_AGGREGATE_RETURNS_ABOVE_50_WITH_DIRECT_AND_SETTLED_ETHBTC_RECLAIMING_0_0300_AND_FUNDING_COOLING
```

**Top-up og købsvindue:** Afvent næste fulde DATA PING om 3–6 timer før top-ups, fordi den aktuelle breadth-gate ikke kan beregnes, ETH/BTC fortsat er 0,02958 med settled close 0,02938, og det nyeste takerflow er tydeligt salgssidet trods fortsat forhøjet funding og kort OI-opbygning.
