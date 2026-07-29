# DCR-20260729-EVENT-002 framework read

**Request:** `DCR-20260729-EVENT-002`  
**Capture status:** `PARTIAL`  
**Validation:** `PARTIAL_VALIDATED_MANIFEST_ONLY_CRITICAL_EVENT_PATH_RESOLVED_BREADTH_COMPOSITION_IRRECOVERABLE`

## Governance result

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

The capture supplements the already accepted `run_0bc8a5d0d0464542b29b4d50f2f8e19c`. It does not constitute a new DATA PING or a new policy decision.

## Recovered event path

Window: `2026-07-29T08:30:00Z` to `2026-07-29T17:00:00Z`.

```yaml
BTCUSDT:
  return_pct: -0.7677
  range_pct: 1.7614
  close_location: 0.1643
  spot_taker_buy_share: 0.4996
  open_interest_change_pct: -1.7567
  read: PRICE_DOWN_AND_OI_DOWN_DELEVERAGING_COMPATIBLE

ETHUSDT:
  return_pct: -0.9350
  range_pct: 1.9827
  close_location: 0.2162
  spot_taker_buy_share: 0.4512
  open_interest_change_pct: 0.0827
  read: PRICE_DOWN_WITH_OI_NEAR_FLAT_TO_SLIGHTLY_UP_SIDE_UNKNOWN

ETHBTC:
  return_pct: -0.1681
  range_pct: 1.0516
  close_location: 0.7097
  spot_taker_buy_share: 0.6495
  read: BUY_SHARE_ABOVE_HALF_WITH_NEGATIVE_RETURN_ABSORPTION_CANDIDATE_ONLY
```

BTC declined with falling open interest, which is compatible with deleveraging rather than fresh leverage expansion. ETH declined while open interest was almost unchanged and slightly higher. That does not identify whether new positions were predominantly short or long and is retained without directional attribution.

ETHBTC had a high spot taker-buy share while the ratio still declined over the full window. This is a useful failed-buy-pressure or absorption candidate for later research, but it is not a rotation confirmation and must not be promoted without replayable row-level evidence and independent recurrence.

The largest negative ETHBTC hourly move occurred from `13:00` to `13:59:59.999 UTC`, at `-0.4047%`.

## Breadth limitation

```yaml
exact_predecessor_constituent_snapshot: UNAVAILABLE
exact_current_constituent_snapshot: UNAVAILABLE
current_universe_substitution: NOT_PERFORMED
rank_bucket_decomposition: UNKNOWN
advancer_decliner_transition_matrix: UNKNOWN
largest_breadth_deterioration_timestamp: UNKNOWN
```

The aggregate breadth relapse remains valid because the accepted DATA PING had an unchanged universe hash. The deep capture cannot explain which constituents or rank buckets caused it because the exact historical page payloads were not retained. Repeating the same request cannot repair this gap.

## Request disposition

```yaml
request_status: PARTIAL_CLOSED
continuation_required: NO
critical_event_path: RESOLVED
breadth_composition: IRRECOVERABLE_FOR_THIS_EVENT
historical_mark_index_basis: NON_BLOCKING_UNAVAILABLE
```

## Permanent learning

Issue `#224` tracks prospective retention of exact breadth constituent sidecars. The compact DATA PING remains unchanged, while replayable constituent rows must be emitted as bounded sidecar evidence whenever Top-100 retrieval succeeds.

No retrospective reconstruction, A-class upgrade, threshold change or portfolio action is permitted.