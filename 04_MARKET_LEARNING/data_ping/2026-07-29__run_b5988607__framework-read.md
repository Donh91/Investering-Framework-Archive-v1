# DATA PING framework read — run_b5988607a8f349558a19f78198fdfde2

**Snapshot UTC:** 2026-07-29T05:11:52.428Z  
**Deep-capture retrieval UTC:** 2026-07-29T06:08:18.248Z  
**Collector status:** PARTIAL, usable for main-framework ingest  
**Predecessor:** `run_aa5ebdf331d34cd8bb27d71a71198cbe`

## Framework classification

```yaml
classification: FIRST_SETTLED_ETHBTC_ACCEPTANCE_ABOVE_0_0300_FAILED_TO_PERSIST_INTRADAY_WITH_PARTIAL_BREADTH_REPAIR_NO_ROTATION
ETH_relative_strength: FIRST_SETTLED_ACCEPTANCE_FAILED_PERSISTENCE
selective_large_cap_rotation: NOT_CONFIRMED
broad_alt_rotation: NOT_CONFIRMED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Critical settlement sequence

The validated Binance owner rows establish the first Europe/Copenhagen-settled ETHBTC close above 0.0300:

```yaml
2026-07-26_close: 0.02969
2026-07-27_close: 0.02995
2026-07-28_close: 0.03007
first_settled_acceptance_above_0_0300: YES
```

That acceptance did not persist after settlement:

```yaml
first_post_settlement_hour_close: 0.02998
latest_deep_capture_hour_close: 0.02987
current_DATA_PING_live: 0.02982
current_in_progress_Copenhagen_daily: 0.02980
```

The in-progress daily row is excluded from settled-close conclusions. The first settled acceptance is valid evidence, but Rotation Architecture v2 requires positive settled persistence. One close followed by an immediate loss of the level is not persistence.

## Current market read

```yaml
BTCUSDT: 63974.29
ETHUSDT: 1907.93
ETHBTC: 0.02982
ETHBTC_1h_return_pct: -0.602611
ETHBTC_4h_return_pct: -1.230872
ETHBTC_12h_return_pct: -1.132201
ETHBTC_1h_taker_buy_share: 0.322525
ETHBTC_4h_taker_buy_share: 0.485542
ETHBTC_12h_taker_buy_share: 0.570474
BTC_OI_24h_pct: -1.693776
ETH_OI_24h_pct: -1.310410
```

ETHBTC closed near the bottom of the 1h, 4h and 12h windows, while short-horizon taker demand weakened sharply. BTC open interest and ETH open interest remained lower over 24 hours, so this is not presently a broad leverage unwind, but the relative-strength attempt lost momentum.

## Breadth and flow

```yaml
breadth_advancers: 33
breadth_decliners: 39
breadth_unchanged: 17
breadth_advance_ratio: 37.0787pct
breadth_membership_hash: 8541eb36d887ad54bdaa8d9f777a0e884fc2f85ef37b2f4114f165d6e4aaa173
selective_large_cap_gate: 50pct
broad_alt_gate: 55pct
```

Breadth recovered materially from the last measured 12.36% reading, but 37.08% remains below both rotation gates. BTC dominance increased while ETH dominance declined between the two latest packets. This supports partial market repair, not broad rotation.

Latest settled ETF context remains mixed: BTC −11.6M USD and ETH +11.7M USD for 2026-07-27. CFGI rows are stale and cannot confirm the current move.

## Prospective evidence adjudication

```yaml
event_id: ROTATION-2026-W31-ETHBTC-0030-FIRST-SETTLED-ACCEPTANCE-FAILED-PERSISTENCE-001
receipt_id: PDR-20260729-52aa8a0a9bf2
receipt_kind: DENIAL
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
new_policy_event: YES
new_unique_overlap_cluster: NO
A_class_increment: 1
A_rows_total: 2
rotation_unique_overlap_clusters: 1
economic_ranking_ready: NO
```

This is not a retrospective A-class receipt for the earlier settlement. The receipt freezes the current, timely no-action decision after the deep-capture evidence became available: rotation permission remains denied because settled persistence failed and breadth remained below both gates.

## Deep-capture disposition

```yaml
request_id: DCR-20260729-EVENT-001
integrity: PASS
coverage: PARTIAL
critical_settlement_gap: RESOLVED
exact_prior_CoinGecko_snapshot: UNRECOVERABLE_IN_CURRENT_RUNTIME
Coinbase_crosscheck: UNAVAILABLE
Kraken_crosscheck: UNAVAILABLE
request_status: PARTIAL_CLOSED
new_follow_up_prompt_required: NO
```

The current DATA PING independently supplies a valid current breadth aggregate and membership hash. It does not reconstruct the unavailable historical breadth snapshot.

## Frozen RAW integrity

The RAW 1–3D and 5–7D forecast frozen at 2026-07-29T04:58:35Z is not rewritten. This packet is a later observation against that forecast. BTC and ETH remain inside the frozen central ranges, while the loss of ETHBTC 0.0300 supports the forecast's `HOLD_AND_DO_NOT_CHASE` translation. Outcome horizons remain pending.
