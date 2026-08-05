# DATA PING Source Record

```yaml
run_id: run-ba9245b5c2ce4988b790
snapshot_id: snap-36ac33d4ca5e427e984c
snapshot_utc: 2026-08-05T15:40:04.992Z
collector_version: 15.2.0
collection_status: PARTIAL
packet_sha256: 86075eb864917f31336ae4f8f3a4a354fb071d7c3ef8f4d9209cd41ae89fd665
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
main_thread_acceptance: BOUNDED_CURRENT_OWNER_WITH_CONTIGUOUS_METHOD_COMPATIBLE_PREDECESSOR
```

## Execution quality

```yaml
planned_core_actions: 60
attempted_core_actions: 60
core_pass: 55
core_partial: 4
core_stale: 1
core_fail: 0
core_unavailable: 0
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
BTCUSDT: 64582.01
ETHUSDT: 1879.58
ETHBTC: 0.02910
BTC_open_interest: 109220.626
ETH_open_interest: 2324131.362
BTC_current_funding: 0.00003326
ETH_current_funding: 0.00003336
```

## Contiguous predecessor linkage

The packet references the immediately preceding bounded owner:

```yaml
predecessor_run_id: run-eec8e2d4c3114f0eac01
predecessor_snapshot_id: snap-4ae65617f89d43488a2d
predecessor_snapshot_utc: 2026-08-05T13:26:08.110Z
elapsed_seconds: 8036.882
lineage_status: DIRECT_ONE_STEP_CONTIGUOUS_METHOD_COMPATIBLE
```

This is the first supplied predecessor in the current sequence that matches the latest bounded pointer exactly. It creates a valid bounded transition but does not itself advance the accepted canonical predecessor.

## Change versus contiguous predecessor

```yaml
BTC_change_pct: 0.703750
ETH_change_pct: 0.634460
ETHBTC_change_pct: -0.102987
BTC_open_interest_change_pct: 2.142144
ETH_open_interest_change_pct: 0.614650
```

BTC and ETH rebounded in USD, while ETH/BTC weakened. Open interest rose faster than price, particularly in BTC, showing that the rebound was partially leverage-assisted.

## OI anchor structure

```yaml
BTC_OI_change_1h_pct: 2.292946
BTC_OI_change_4h_pct: 2.106871
BTC_OI_change_24h_pct: -0.340600
ETH_OI_change_1h_pct: 0.781336
ETH_OI_change_4h_pct: 0.307648
ETH_OI_change_24h_pct: -1.456036
```

Both assets remain below their 24-hour OI anchors, but short-window leverage rebuilt materially during the rebound.

## Flow and positioning

```yaml
BTC_spot_taker_buy_share_1h: 0.602027
BTC_spot_taker_buy_share_4h: 0.560453
BTC_spot_taker_buy_share_12h: 0.529905
ETH_spot_taker_buy_share_1h: 0.500728
ETH_spot_taker_buy_share_4h: 0.513413
ETH_spot_taker_buy_share_12h: 0.511612
ETHBTC_spot_taker_buy_share_1h: 0.175718
ETHBTC_spot_taker_buy_share_4h: 0.340009
ETHBTC_spot_taker_buy_share_12h: 0.411223
BTC_futures_taker_ratio: 1.0036
ETH_futures_taker_ratio: 0.9764
BTC_global_long_short: 1.2237
ETH_global_long_short: 2.3344
```

BTC spot buying is persistent across 1h, 4h and 12h. ETH spot buying is only modestly positive in USD. ETHBTC taker-buy share is below 50% on all supplied windows and extremely weak on 1h, confirming continued relative selling rather than transmission.

## Breadth — same universe comparison

```yaml
method: COINGECKO_TOP100_FILTERED_v3
filter: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
included_count: 89
advancers: 42
decliners: 33
unchanged: 14
positive_share_full_universe: 0.471910112360
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.358426966292
```

The membership hash matches the contiguous predecessor. Therefore the transition is directly comparable:

```yaml
prior_advancers: 35
current_advancers: 42
prior_decliners: 41
current_decliners: 33
positive_share_change_percentage_points: 7.865169
equal_weight_mean_change_percentage_points: 0.538202
```

Breadth improved materially but remains below 50%. The supplied v3 transform is still incompatible with the locked v1.1 scoring owner, so the move is diagnostic and cannot open a formal gate.

## ETF source status

```yaml
BTC_current_run_status: PARTIAL
ETH_current_run_status: PARTIAL
latest_session_identified: false
current_run_values_usable: false
prior_direct_owner_forward_filled: false
```

No ETF values from this run are authorized for market use. The separate ETF owner remains unchanged at the previously direct-confirmed 2026-08-04 session.

## Sentiment and macro context

```yaml
CFGI_global: 45
CFGI_ETH: 43
CFGI_BTC: 46_STALE
VIX_latest: 16.50
VIX_change_1_observation: 0.64
```

Sentiment softened during the rebound and VIX increased on its latest available observation, adding caution rather than confirmation.

## Missing or degraded

- Current-run BTC and ETH ETF rows were not resolved.
- CFGI BTC remains stale.
- Stablecoin global total remains unavailable after registered fallbacks.
- Total DeFi TVL remains unavailable and optional.
- Realized volatility 24h/72h/168h remains unavailable under the supplied history budget.
- GeckoTerminal retains two low-reserve source anomalies.

## Main-thread result

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REBOUND_WITH_IMPROVING_SAME_UNIVERSE_BREADTH_BUT_SHORT_WINDOW_LEVERAGE_REBUILD_AND_CONTINUED_ETHBTC_RELATIVE_SELLING
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