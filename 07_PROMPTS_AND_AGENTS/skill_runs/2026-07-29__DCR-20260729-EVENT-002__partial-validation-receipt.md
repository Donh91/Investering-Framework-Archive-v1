# DCR-20260729-EVENT-002 partial validation receipt

```yaml
request_id: DCR-20260729-EVENT-002
response_received_at_utc: 2026-07-29T17:36:28.961Z
validation_result: PARTIAL_VALIDATED_MANIFEST_ONLY_CRITICAL_EVENT_PATH_RESOLVED_BREADTH_COMPOSITION_IRRECOVERABLE
request_disposition: PARTIAL_CLOSED
continuation_required: NO
```

## Integrity

```yaml
manifest_uploaded: YES
manifest_bytes: 6640
manifest_sha256_expected: efc0e0068b1d47ef437c259e7b4e11c740ed86560d5356bc9a2ebb886c772157
manifest_sha256_actual: efc0e0068b1d47ef437c259e7b4e11c740ed86560d5356bc9a2ebb886c772157
manifest_hash_match: PASS
zip_uploaded: NO
zip_hash_recalculated: NO
member_hashes_recalculated: NO
```

## Framework effect

```yaml
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
canonical_state_change: NONE
portfolio_action: NONE
final_holdout_opened: NO
```

## Resolved

- bounded Binance spot 1h and 5m event path;
- exact 08:30 UTC support rows;
- hourly open-interest anchors;
- funding and positioning observations when reported;
- deterministic event returns, ranges, close locations and taker shares;
- largest negative ETHBTC 1h move.

## Unresolved and closed

- exact historical CoinGecko constituent snapshots;
- rank-bucket and transition decomposition;
- historical hourly Binance mark, index and basis;
- 17:00 futures-taker anchor.

Repeating the request cannot recover the missing historical breadth pages. The gap is therefore closed as irrecoverable for this event rather than left pending.

## Permanent correction

- canonical breadth-sidecar retention addendum added;
- implementation tracked in issue `#224`;
- compact DATA PING schema unchanged;
- no retrospective reconstruction permitted.