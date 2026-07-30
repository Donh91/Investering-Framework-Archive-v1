# Source pointer - DATA PING run_4dd78b1e713b4258aedcade193b29b8b

```yaml
run_id: run_4dd78b1e713b4258aedcade193b29b8b
snapshot_id: snap_bed564693b804b8c9c2b7476386abd3d
snapshot_utc: 2026-07-30T13:36:19.781Z
source_delivery: USER_PASTED_COMPACT_JSON_IN_MAIN_CHAT
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
collector_status: PARTIAL
all_core_actions_attempted: YES
```

## Main-framework treatment

```yaml
bounded_market_observation: ACCEPTED
longitudinal_predecessor: REJECTED
source_QA_event: ACCEPTED
required_market_predecessor: snap_0e19c112413d471d8270cad1a18148a7
```

## Material retained fields

- CoinGecko current market values and dominance;
- filtered breadth aggregate and membership hash;
- FRED rows and yield curve;
- DefiLlama chain distribution and chain TVL;
- GeckoTerminal DEX sample;
- OKX current prices, basis, funding and open interest;
- Binance and public-web failure receipts;
- declared predecessor and comparison rows.

## Integrity limitations

- the complete one-line packet exists only in the project conversation;
- no raw response bytes were uploaded;
- no CoinGecko constituent sidecar was supplied;
- packet comparison rows use a rejected QA-only predecessor;
- Binance direct owner data is unavailable;
- DCR-20260730-EVENT-003 is required for direct ETHBTC and current breadth-sidecar recovery.