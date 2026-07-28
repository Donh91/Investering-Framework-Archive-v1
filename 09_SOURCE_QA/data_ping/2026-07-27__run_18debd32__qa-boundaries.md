# DATA PING source-QA boundaries — run 18debd32

```yaml
run_id: run_18debd32d9b4476db4a514d81f1a0058
snapshot_utc: 2026-07-27T19:21:16.902Z
qa_status: PARTIAL_WITH_DIRECT_MARKET_FEEDS_RESTORED
```

## Passed source families

- Binance context: 23/23 PASS
- Binance final: 11/11 PASS
- OKX cross-check: 10/10 PASS
- CoinGecko: 4/4 PASS
- FRED: 4/4 PASS
- GeckoTerminal: PASS
- DeFiLlama chains TVL: PASS

## Missing or bounded families

### Public web

All five public-web actions were unavailable:

- BTC ETF
- ETH ETF
- global CFGI
- BTC CFGI
- ETH CFGI

No zero, neutral or stale value may be inferred from unavailability.

### Stablecoins

The global total was unavailable. Chain-distribution rows are descriptive and cannot be summed into a global total under the active method contract.

### Realized volatility

The collector requested 24-hour, 72-hour and 168-hour realized-volatility windows but had only 13 settled hourly candles. The feature was correctly marked unavailable.

### Optional DeFi total TVL

The bounded response exceeded the configured payload budget. Failure is retained as `RESPONSE_TOO_LARGE`, not converted to missing-zero.

## Temporal boundary

The packet was frozen at 19:21 UTC, before the 2026-07-27 Europe/Copenhagen daily settlement used by H7 row 6.

Therefore:

```yaml
ETHBTC_0_0300_observation: LIVE_ONLY
H7_row_6_authority: NOT_AVAILABLE_AT_PACKET_FREEZE
F1_final_authority: NOT_AVAILABLE_AT_PACKET_FREEZE
```

Later OTA #24 evidence may be linked for final adjudication but must not be represented as known by this collector at its freeze time.

## Market-method boundary

- Direct Binance ETH/BTC is authoritative for live pair observation.
- CoinGecko ETH/BTC is derived and remains descriptive only.
- OKX perpetual swap data cannot silently replace Binance spot.
- No current flow conclusion is allowed without ETF data.
- Breadth weakness is admissible because the membership hash is present.

## QA conclusion

```yaml
packet_usable: YES
full_sensor_coverage: NO
direct_market_identity: PASS
settled_gate_adjudication: NOT_ALLOWED_AT_FREEZE
rotation_upgrade: NOT_ALLOWED
portfolio_action: NONE
```
