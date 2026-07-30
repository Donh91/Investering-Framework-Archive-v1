# Source pointer — DATA PING run_6ed8dcf0ec6a4d62a429c7f10fcb5f5b

```yaml
run_id: run_6ed8dcf0ec6a4d62a429c7f10fcb5f5b
snapshot_id: snap_83dbf24776894d07be9b506858820563
snapshot_utc: 2026-07-30T05:14:00Z
source_delivery: USER_PASTED_COMPACT_JSON_IN_MAIN_CHAT
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
collector_status: PARTIAL
root_failure: RUNTIME_BUDGET_EXHAUSTED
```

## Retained evidence

- full compact JSON was supplied in the main project conversation;
- no standalone raw JSON file or deterministic packet hash was uploaded;
- CoinGecko page receipts report PASS, but constituent rows were not included in the compact packet;
- no breadth sidecar artifact was supplied;
- no Binance, OKX, ETF, CFGI, FRED, chain, DEX or derivatives artifacts were produced for this run.

## Authority boundary

This pointer preserves lineage only. The run is accepted for source-QA and rejected for market-state replacement, prospective evidence, shadow-run counting and portfolio action.

## Related artifacts

- framework read: `04_MARKET_LEARNING/data_ping/2026-07-30__run_6ed8dcf0__framework-read.md`
- machine summary: `04_MARKET_LEARNING/data_ping/2026-07-30__run_6ed8dcf0__machine-summary.json`
- QA boundaries: `09_SOURCE_QA/data_ping/2026-07-30__run_6ed8dcf0__qa-boundaries.json`
- breadth retention issue: `#224`
- runtime semantics issue: `#229`