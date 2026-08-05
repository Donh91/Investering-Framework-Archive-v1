# DATA PING Source Record

```yaml
run_id: run-aebc326ae71e48109b9b
snapshot_id: snap-554c617f944e41ad91bf
snapshot_utc: 2026-08-05T18:05:27.894Z
collector_version: 15.2.0
collection_status: PARTIAL
packet_sha256: 3d81d67d0eb57dd519c5efc14a73a4ccc3ef0d5aab998c5c70532db856cc9a38
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
main_thread_acceptance: BOUNDED_CURRENT_OWNER_WITH_CONTIGUOUS_METHOD_COMPATIBLE_PREDECESSOR
```

## Execution quality

```yaml
planned_core_actions: 60
attempted_core_actions: 60
core_pass: 57
core_partial: 1
core_stale: 1
core_fail: 0
core_unavailable: 1
execution_order_status: PASS
status_reconciliation: PASS
receipt_bijection_status: PASS
breadth_transform_status: PASS
settled_candle_filter_status: PASS
freeze_invariants_status: PASS
freeze_count: 1
post_freeze_call_count: 0
validator_pass: true
```

## Direct current owner snapshot

```yaml
BTCUSDT: 64784.38
ETHUSDT: 1917.46
ETHBTC: 0.02959
BTC_open_interest: 109303.898
ETH_open_interest: 2337427.519
BTC_current_funding: 0.00002038
ETH_current_funding: 0.00004845
```

## Contiguous predecessor linkage

```yaml
predecessor_run_id: run-ba9245b5c2ce4988b790
predecessor_snapshot_id: snap-36ac33d4ca5e427e984c
predecessor_snapshot_utc: 2026-08-05T15:40:04.992Z
elapsed_seconds: 8722.902
lineage_status: DIRECT_ONE_STEP_CONTIGUOUS_METHOD_COMPATIBLE
```

The supplied predecessor exactly matches the immediately prior bounded owner. This creates a second consecutive valid one-step bounded transition, while the accepted canonical predecessor remains separate and unchanged.

## Change versus contiguous predecessor

```yaml
BTC_change_pct: 0.313354
ETH_change_pct: 2.015344
ETHBTC_change_pct: 1.683849
BTC_open_interest_change_pct: 0.076242
ETH_open_interest_change_pct: 0.572091
```

ETH and ETH/BTC outperformed sharply while open interest rose much less than price. This is cleaner than the preceding leverage-assisted rebound and is the strongest live transmission attempt in the current bounded sequence.

## OI anchor structure

```yaml
BTC_OI_change_1h_pct: 0.287882
BTC_OI_change_4h_pct: 1.875374
BTC_OI_change_24h_pct: -0.154519
ETH_OI_change_1h_pct: 0.663514
ETH_OI_change_4h_pct: 0.277523
ETH_OI_change_24h_pct: -0.293680
```

Both assets remain slightly below their 24-hour OI anchors. Short-window leverage rebuilt, but price expansion—especially in ETH—was materially larger than the final OI change versus the predecessor.

## Flow and positioning

```yaml
BTC_spot_taker_buy_share_1h: 0.492875
BTC_spot_taker_buy_share_4h: 0.517290
BTC_spot_taker_buy_share_12h: 0.519700
ETH_spot_taker_buy_share_1h: 0.600296
ETH_spot_taker_buy_share_4h: 0.537101
ETH_spot_taker_buy_share_12h: 0.526068
ETHBTC_spot_taker_buy_share_1h: 0.653223
ETHBTC_spot_taker_buy_share_4h: 0.464881
ETHBTC_spot_taker_buy_share_12h: 0.437825
BTC_futures_taker_ratio: 1.0619
ETH_futures_taker_ratio: 1.2800
BTC_global_long_short: 1.1805
ETH_global_long_short: 2.2227
```

ETH/USD buying is persistent across all supplied windows. ETHBTC buying is strong on 1h but remains below 50% on 4h and 12h, so the relative move is not yet persistent. ETH positioning remains materially more long-heavy than BTC.

## ETHBTC threshold context

```yaml
direct_ETHBTC: 0.02959
distance_to_0_0300_pct: -1.366667
distance_above_0_0275_pct: 7.600000
in_progress_high: 0.02952_from_24h_ticker
settled_0_0300_confirmation: false
```

The direct value materially narrowed the distance to 0.0300, but no settled close or threshold touch is supplied. The formal rotation gate remains closed.

## Breadth

```yaml
method: COINGECKO_TOP100_FILTERED_v3
filter: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
membership_hash: 7d2f46aa15ca6246858b18a7da06339c7705db13df1f1014d85303eec80f5dd8
included_count: 90
advancers: 42
decliners: 30
unchanged: 18
positive_share_full_universe: 0.466666666667
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.263333333333
```

The membership hash changed from the predecessor, so no same-universe longitudinal breadth delta is authorized. The current absolute reading remains below 50%, and the v3 transform remains incompatible with the locked v1.1 scoring owner.

## ETF and sentiment

```yaml
BTC_ETF_session: 2026-08-04
BTC_ETF_usd_m: 211.5
ETH_ETF_session: 2026-08-04
ETH_ETF_usd_m: 53.1
new_ETF_session: false
CFGI_global: 46
CFGI_ETH: 43
CFGI_BTC: 46_STALE
VIX_latest: 16.50
```

The ETF rows re-confirm the existing direct owner and do not introduce a new session.

## Missing or degraded

- Stablecoin global total is unavailable after all registered fallbacks.
- Optional total DeFi TVL is unavailable.
- Realized volatility 24h/72h/168h is unavailable under the supplied history budget.
- BTC CFGI remains stale.
- GeckoTerminal retains two low-reserve source anomalies.

## Main-thread result

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REPAIR_WITH_EMERGING_ETH_RELATIVE_REBOUND_BUT_NO_SETTLED_0030_OR_MULTI_WINDOW_ETHBTC_FLOW_PERSISTENCE
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

The full user-supplied packet remains preserved in the originating conversation transport.