# Audit Receipt — Claude OTA BTC ETF 4 August and In-Progress ETHBTC

```yaml
archived_at_utc: 2026-08-05T19:19:00Z
ota_run_timestamp_utc: 2026-08-05T19:16:53.370Z
reference_data_ping_run_id: run-aebc326ae71e48109b9b
classification: PASS_WITH_MAIN_THREAD_CORRECTIONS_AND_WINDOW_QUARANTINE
source_record_written: true
framework_reconciliation_written: true
qa_record_written: true
latest_OTA_status_updated: true
ETF_owner_updated: true
prospective_accumulation_updated: true
remote_readback_verified: true
canonical_predecessor_changed: false
prospective_accumulation_increment: 0
portfolio_effect: NONE
```

## Reconciliation summary

- No H7 or daily-settlement maturity occurred.
- BTC ETF 4 August +211.5M matches the direct DATA PING owner.
- The supplied BTC issuer breakdown was retained as user-supplied fresh-payload detail.
- ETH ETF 4 August is not pending in the main thread; the direct owner already records +53.1M.
- The OTA 3-session BTC sum +116.2M matches the repository owner.
- OTA 5-session +118.4M and 7-session +80.3M do not match the repository owner values +381.4M and +320.1M.
- OTA 20-session +153.0M is not reproducible because the repository owner contains only 15 direct rows.
- The claim that all four BTC windows are positive was not promoted.
- The live ETHBTC rebound was corroborated near 0.02959, but 0.0300 was not touched or settled.
- The flow-side anti-transmission statement was superseded by direct ETH ETF 4 August +53.1M; the latest same-session ETF sign is dual-positive with BTC dollar dominance.
- H7 row 15 remains not formed and all policy permissions remain unchanged.

## Durable paths

- `08_SOURCE_MATERIAL/claude_ota/2026-08-05__standalone-ota-btc-etf-4aug-inprogress-ethbtc__source-record.md`
- `04_MARKET_LEARNING/claude_ota/2026-08-05__standalone-ota-btc-etf-4aug-inprogress-ethbtc__framework-reconciliation.md`
- `09_SOURCE_QA/claude_ota/2026-08-05__standalone-ota-btc-etf-4aug-inprogress-ethbtc__reconciliation.json`
- `04_MARKET_LEARNING/claude_ota/LATEST_CLAUDE_OTA_STATUS_v1.json`
- `04_MARKET_LEARNING/etf/LATEST_ETF_FLOW_STATUS_v1.json`
- `04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/architecture/PROSPECTIVE_ACCUMULATION_STATUS_v1.json`