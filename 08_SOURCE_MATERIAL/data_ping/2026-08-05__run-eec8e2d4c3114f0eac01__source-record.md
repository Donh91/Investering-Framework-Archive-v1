# DATA PING Source Record

```yaml
run_id: run-eec8e2d4c3114f0eac01
snapshot_id: snap-4ae65617f89d43488a2d
snapshot_utc: 2026-08-05T13:26:08.110Z
collector_version: 15.2.0
collection_status: PARTIAL
packet_sha256: 1cad4c489f7cdab3d5b19993aacb43164107ccad66156052e8f5100276946e7c
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
main_thread_acceptance: BOUNDED_CURRENT_OWNER_WITH_LINKED_NONCANONICAL_PREDECESSOR
```

## Execution quality

```yaml
planned_core_actions: 60
attempted_core_actions: 60
core_pass: 57
core_partial: 2
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
BTCUSDT: 64130.69
ETHUSDT: 1867.73
ETHBTC: 0.02913
BTC_open_interest: 106930.031
ETH_open_interest: 2309933.354
BTC_current_funding: 0.00004088
ETH_current_funding: 0.00001391
```

## Change versus immediate prior bounded owner

Immediate prior bounded owner:

```yaml
run_id: run_f6dc99c81a9d410db226a70e9f678ee5
snapshot_id: snap_84870ae0a3984d5eba1b8b6ef7b16d3c
snapshot_utc: 2026-08-05T12:26:16.969Z
```

```yaml
BTC_change_pct: -0.537014
ETH_change_pct: -0.608250
ETHBTC_change_pct: -0.068611
BTC_open_interest_change_pct: -0.174176
ETH_open_interest_change_pct: -0.762240
```

The one-hour move was a price pullback accompanied by lower final open interest on both assets, not a leverage expansion into the decline.

## Supplied predecessor linkage

The packet declares predecessor availability and references:

```yaml
predecessor_snapshot_id: snap-bafd43eb4ab1fa90c0cb
predecessor_run_id: run-4e87515bde8846aa9c51
```

This is a valid bounded comparison anchor, but it is not the canonical accepted predecessor and it is not the immediately prior bounded owner. It therefore improves longitudinal lineage without authorizing canonical-chain advancement.

Change versus the supplied predecessor:

```yaml
BTC_change_pct: -0.033343
ETH_change_pct: -0.158230
ETHBTC_change_pct: -0.137127
BTC_open_interest_change_pct: -0.496721
ETH_open_interest_change_pct: -0.313323
```

## Flow and positioning

```yaml
BTC_spot_taker_buy_share_1h: 0.580430
BTC_spot_taker_buy_share_4h: 0.523949
BTC_spot_taker_buy_share_12h: 0.520061
ETH_spot_taker_buy_share_1h: 0.495749
ETH_spot_taker_buy_share_4h: 0.507678
ETH_spot_taker_buy_share_12h: 0.508213
ETHBTC_spot_taker_buy_share_1h: 0.832605
ETHBTC_spot_taker_buy_share_4h: 0.410672
ETHBTC_spot_taker_buy_share_12h: 0.423511
BTC_futures_taker_ratio: 0.9992
ETH_futures_taker_ratio: 1.3116
BTC_global_long_short: 1.2482
ETH_global_long_short: 2.2819
```

The one-hour ETHBTC buy burst did not persist into the four- or twelve-hour windows. ETH remains materially more long-heavy than BTC.

OI-anchor changes:

```yaml
BTC_OI_1h_pct: 0.419009
BTC_OI_4h_pct: -0.184925
BTC_OI_24h_pct: -1.832351
ETH_OI_1h_pct: 0.741685
ETH_OI_4h_pct: 0.701185
ETH_OI_24h_pct: -1.205915
```

This shows recent ETH OI rebuilding inside a still-deleveraged 24-hour structure.

## ETF

```yaml
latest_settled_session: 2026-08-04
BTC_net_flow_usd_m: 211.5
ETH_net_flow_usd_m: 53.1
BTC_minus_ETH_usd_m: 158.4
status: BOTH_DIRECT_OWNER_PASS
```

No new ETF session was introduced; the run independently reconfirmed the existing owner row.

## Breadth

```yaml
method: COINGECKO_TOP100_FILTERED_v3
filter: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
included_count: 89
advancers: 35
decliners: 41
unchanged: 13
positive_share_full_universe: 0.393258426966
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: -0.179775280899
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
locked_scoring_owner: BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1
scored_gate_permission: NOT_AUTHORIZED
```

The membership hash matches the 09:10 bounded run, allowing a same-universe directional comparison to that run: advancers fell from 36 to 35, decliners rose from 39 to 41, and the positive share fell from 40.45% to 39.33%. It does not match the immediately prior bounded owner and remains incompatible with the locked v1.1 scoring owner.

## Missing or degraded

- CFGI BTC is stale.
- Stablecoin global total remains unavailable after registered fallbacks.
- Total DeFi TVL remains unavailable and optional.
- Realized volatility 24h/72h/168h remains unavailable under the supplied settled-history budget.
- GeckoTerminal retains two low-reserve source anomalies.

## Main-thread result

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REPAIR_WITH_INTRADAY_PULLBACK_24H_DELEVERAGING_AND_TRANSIENT_ETHBTC_BUY_BURST_WITHOUT_PERSISTENT_TRANSMISSION
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