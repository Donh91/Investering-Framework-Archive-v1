# DATA PING framework read — run_0bc8a5d0d0464542b29b4d50f2f8e19c

**Snapshot UTC:** 2026-07-29T16:51:00.829Z  
**Collector status:** PARTIAL, usable for bounded main-framework ingest  
**Predecessor:** `run_49cf4c174e254c4ebabb6cf2042109ea` / `snap_2f1f711eeaa543f28059d7efeffd0512`

## Framework classification

```yaml
classification: BTC_LED_DEFENSIVE_REPAIR_WITH_DIRECT_ETHBTC_BELOW_0_0300_AND_MATERIAL_BREADTH_RELAPSE
ETH_relative_strength: FAILED_PERSISTENCE_CONFIRMED_BY_RESTORED_DIRECT_OWNER
selective_large_cap_rotation: NOT_CONFIRMED
broad_alt_rotation: NOT_CONFIRMED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Direct market state

```yaml
BTCUSDT: 63780.00
ETHUSDT: 1893.32
ETHBTC_direct: 0.02970
ETHBTC_distance_to_0_0300_pct: -1.00
BTC_24h_change_pct: -0.191
ETH_24h_change_pct: -1.454
ETHBTC_24h_change_pct: -1.230
```

The Binance owner source recovered after the immediately preceding geo-restriction outage. Direct ETHBTC remained below 0.0300 and therefore confirms that the previously adjudicated first settled acceptance did not regain persistence. This is not a new threshold decision: rotation permission was already denied in `PDR-20260729-52aa8a0a9bf2`.

## Breadth relapse

```yaml
previous_advance_ratio: 0.4157303371
current_advance_ratio: 0.2696629213
delta_percentage_points: -14.60674158
relative_change_pct: -35.135135
advancers: 24
decliners: 51
unchanged: 14
median_return_24h_pct: -0.4820991410
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
```

The universe hash is unchanged, so the breadth deterioration is comparable rather than a membership artefact. Participation fell sharply while BTC and ETH declined only 0.62% and 1.12% on the comparable CoinGecko fields. This is a material price/breadth divergence and supports defensive BTC-led repair, not broadening.

## Derivatives and flow

```yaml
BTC_OI_24h_change_pct: -1.619638
ETH_OI_24h_change_pct: -0.746692
BTC_futures_taker_buy_sell_ratio: 1.0313
ETH_futures_taker_buy_sell_ratio: 0.8780
BTC_funding_latest3_mean: 0.0000788833333
ETH_funding_latest3_mean: 0.00004917
BTC_ETF_2026_07_28_usd_m: -49.7
ETH_ETF_2026_07_28_usd_m: 9.4
```

Open interest fell over 24 hours on both assets, so the deterioration is not presently a fresh leverage expansion. ETH futures taker flow was sell-dominant, consistent with the relative weakness. Funding remained positive but not sufficient to override the direct ETHBTC and breadth evidence.

## Prospective adjudication

```yaml
observation_id: OBS-20260729-0bc8a5d0-BREADTH-RELAPSE
parent_receipt_id: PDR-20260729-52aa8a0a9bf2
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
shadow_dual_run_valid_increment: 1
shadow_dual_run_valid_runs: 5
```

The run is a high-value same-cluster confirmation: the owner source recovered, ETHBTC remained below the threshold, and breadth relapsed. State and action permission did not change, so another A-class denial would double count the same policy decision.

## Deep-capture adjudication

```yaml
request_id: DCR-20260729-EVENT-002
request_type: EVENT_DRIVEN_DEEP_CAPTURE
trigger_classes:
  - BREADTH_DISPLACEMENT
  - PRICE_BREADTH_DIVERGENCE
  - ETHBTC_FAILED_PERSISTENCE_FOLLOW_UP
status: PREPARED
canonical_effect: NONE
portfolio_effect: NONE
```

The aggregate is sufficient for current policy, but the standard packet does not preserve constituent-level rows or the intraday decomposition of the breadth collapse. A bounded capture is therefore justified for research, calibration and later failed-move analysis. It must not create retrospective A-class evidence.

## Simple translation

```yaml
market_message: BTC_IS_HOLDING_BETTER_THAN_THE_REST_BUT_PARTICIPATION_IS_WEAKENING
existing_positions: HOLD
new_microcaps: NO
chase_ETH_or_large_caps: NO
large_caps: WATCH_ONLY
add_risk: WAIT
BTC_63300: NEAR_TERM_REPAIR_SUPPORT
BTC_61900: MATERIAL_PULLBACK_RISK_LEVEL
portfolio_action: NONE
```
