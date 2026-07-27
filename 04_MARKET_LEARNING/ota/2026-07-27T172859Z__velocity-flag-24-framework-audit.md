# OTA velocity flag 24, framework audit

- Timestamp: `2026-07-27T17:28:59Z`
- Run type: `VELOCITY_FLAG_NOT_FULL_PING`
- Preregistered items matured: `0`

## Accepted new information

1. Three full 64-character `raw_row_sha256` values were supplied for the re-fetched H7 row-5 BTCUSDT, ETHUSDT and ETHBTC source rows.
2. Reported closes match the values used in OTA Ping 23.
3. ETH/BTC touched `0.03000` intraday during the 2026-07-26 UTC session and settled below at `0.02989`.
4. ETH/BTC traded as high as `0.03020` during the still-open 2026-07-27 session and was approximately `0.02988` at the observation time.
5. H7 row 6, F1 window close and low-vol 5D maturity were still pending.

## Independent corrections

### H7 lineage

The new hashes close the omitted raw-row-hash gap, but do not yet justify `FULL_LINEAGE_PASS` under the stricter receipt standard because:

- no `response_sha256` values were supplied
- `retrieved_at_utc` is written as `2026-07-27T17:29:01.6xx+00:00`, not an exact timestamp
- no original Ping 23 raw-row hashes were published, so whole-row byte identity against the original retrieval cannot be independently established

The correct status is:

```yaml
row5_data_status: SETTLED_PROSPECTIVE_VALID
row5_raw_row_hashes: PRESENT
row5_close_value_reconfirmation: PASS
row5_full_row_original_parity: NOT_PROVEN
row5_response_hashes: MISSING
row5_lineage_status: PARTIAL_LINEAGE_PASS
H7_score_change: NONE
```

### 0.0300 wording

The 2026-07-26 session can be described as `INTRADAY_TOUCH_SETTLED_CLOSE_BELOW`.

The 2026-07-27 session is still open. It can only be described as `INTRADAY_BREAK_IN_PROGRESS_CURRENTLY_BELOW`. It has not yet been rejected on close.

```yaml
F4_reopen: NO
new_gate_test: NONE
settled_0_0300_confirmation: NO
```

## Framework state

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

No full OTA Ping, score, backtest or portfolio action was executed.