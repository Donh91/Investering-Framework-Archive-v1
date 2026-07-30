# DATA PING ingest receipt — run 5f1b7219

```yaml
processed_at_utc: 2026-07-30T19:45:00Z
run_id: run_5f1b7219edb64d48a5e9961ee7ce9849
snapshot_id: snap_155aa63ee97245cb8e4d763f113056e4
source_record: 08_SOURCE_MATERIAL/data_ping/2026-07-30__run_5f1b7219__source-record.md
framework_read: 04_MARKET_LEARNING/data_ping/2026-07-30__run_5f1b7219__framework-read.md
machine_summary: 04_MARKET_LEARNING/data_ping/2026-07-30__run_5f1b7219__machine-summary.json
source_QA: 09_SOURCE_QA/data_ping/2026-07-30__run_5f1b7219__validation.json
```

## Adjudication

```yaml
bounded_current_observation: ACCEPTED
source_QA: ACCEPTED
packet_longitudinal_deltas: REJECTED
market_successor: REJECTED_INVALID_PREDECESSOR
accepted_predecessor_unchanged: snap_0e19c112413d471d8270cad1a18148a7
```

## Main findings

- Direct Binance ETHBTC owner recovered at `0.02968`, below `0.0300`.
- Filtered breadth fell to `43.8202%`, below both the 50% and 55% gates.
- The prior two bounded breadth snapshots above 55% did not persist.
- BTC led ETH over the settled 12-hour window.
- Positioning is mixed: positive funding and higher 24-hour OI, but taker ratios below 1 and long-heavy ETH accounts.
- Packet ETF rows are stale and were not allowed to overwrite the newer OTA evidence.
- DCR-003 receives supplemental owner evidence but its extension remains unexecuted and its requested sidecars remain unresolved.

## State effect

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: HOLD
new_policy_event: NO
new_A_class_receipt: NO
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
canonical_state_change: NONE
```

## User-facing operational line

**Top-up og købsvindue:** Afvent cirka 2–4 dage med hovedparten af købene, fordi breadth er faldet tilbage under 50%, og direkte ETH/BTC stadig ligger under 0,0300, hvilket øger sandsynligheden for et bedre købsvindue.
