# DATA PING source-QA boundaries — run 8fd63dc63

```yaml
run_id: run_8fd63dc63e47476086215a67dba27573
snapshot_utc: 2026-07-28T05:00:00Z
qa_status: PARTIAL_WITH_BINANCE_GEO_FAILURE_AND_PUBLIC_WEB_RECOVERY
```

## Passed source families

- Public web: 5/5 PASS
- CoinGecko: 4/4 PASS
- FRED: 4/4 PASS
- OKX: 10/10 PASS
- GeckoTerminal: PASS
- DeFiLlama chains TVL: PASS

## Failed source families

All 34 Binance context and final actions failed with the same geo-restriction evidence.

```yaml
calls_attempted: 34
calls_skipped: 0
error_category: GEO_RESTRICTION
error_deduplicated: true
```

Consequences:

- no direct ETH/BTC observation;
- no settled Binance CEST or UTC candles;
- no Binance spot taker data;
- no Binance funding or OI history;
- no Binance basis or cross-venue mark comparison;
- no Binance realized-volatility features.

No OKX or CoinGecko value may silently substitute for these missing direct Binance methods.

## ETF freshness correction

The 2026-07-27 Farside rows passed the current settled-session checks in this run:

```yaml
BTC_ETF: -11.6_USDm
ETH_ETF: +11.7_USDm
market_use: USABLE
```

These rows supersede OTA #24's earlier same-day `QUARANTINED` status, because OTA #24 observed a stale-cache presentation while this later run reached a current settled payload.

The correction is chronological, not retroactive: OTA #24 was correct to quarantine the payload available at 04:30 UTC.

## Breadth audit limitation

```yaml
method: COINGECKO_TOP100_FILTERED_v2
included_count: 89
advance_ratio: 5.62%
membership_hash_status: UNAVAILABLE
reason: LOCAL_HASH_NOT_COMPUTED
```

The breadth aggregate is usable for directional context because the filter method, raw count, deduped count and included count are supplied. It is not granted full row-level membership parity without the hash.

## Direct versus derived ETH/BTC

```yaml
direct_ETHBTC: UNAVAILABLE
derived_ETHBTC: 0.0297081192
derived_authority: DESCRIPTIVE_ONLY
hard_gate_scoring: FORBIDDEN
H7_row_7_scoring: FORBIDDEN
```

## Stablecoins and DeFi

The global stablecoin total remains unavailable. Chain distribution is partial and cannot be summed into a global total.

The optional DeFi total TVL request failed because the response exceeded the bounded payload budget. This remains `EXECUTED_FAIL_RESPONSE_TOO_LARGE`.

## Temporal boundary

The packet was frozen after OTA #24 but before H7 row 7 settlement.

```yaml
F1_maturity: KNOWN_FROM_OTA24
LOW_VOL_maturity: KNOWN_FROM_OTA24
H7_row_6: KNOWN_FROM_OTA24
H7_row_7: NOT_YET_MATURE
```

## QA conclusion

```yaml
packet_usable: YES
full_sensor_coverage: NO
market_direction_context: USABLE
settled_direct_gate_adjudication: NOT_ALLOWED
rotation_upgrade: NOT_ALLOWED
portfolio_action: NONE
```
