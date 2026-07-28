# DATA PING source-QA boundaries — run cc9b4e7c

```yaml
run_id: run_cc9b4e7cc8d34277957d521a7519cd63
snapshot_utc: 2026-07-28T09:55:00Z
qa_status: PARTIAL_WITH_DIRECT_BINANCE_FAILURE_AND_STALE_SENTIMENT
```

## Passed source families

- CoinGecko: 4/4 PASS
- FRED: 4/4 PASS
- OKX cross-check: 10/10 PASS
- Farside BTC and ETH settled rows: PASS
- GeckoTerminal: PASS
- DeFiLlama chain TVL: PASS

## Failed source families

All Binance context and final actions failed with the same geo-restriction evidence.

```yaml
Binance_context: FAIL_23_OF_23
Binance_final: FAIL_11_OF_11
shared_error_category: GEO_RESTRICTION
```

The failures are executed failures, not skipped actions. No Binance spot, direct ETH/BTC, settled OHLC, taker, funding-history, OI-history, basis or realized-volatility value may be inferred.

## Stale source families

```yaml
CFGI_global:
  value: 50
  source_timestamp: 2026-07-27T19:03:00Z
CFGI_BTC:
  value: 47
  source_timestamp: 2026-07-28T02:33:00Z
CFGI_ETH:
  value: 60
  source_timestamp: 2026-07-27T23:03:00Z
```

These rows are retained for lineage but excluded from current confirmation.

## Direct-versus-derived authority

The current ETH/BTC value is derived from CoinGecko BTC and ETH USD observations.

```yaml
derived_ETHBTC: 0.0296428234
use_for_market_description: ALLOWED
use_for_direct_gate_scoring: FORBIDDEN
use_for_H7_settlement: FORBIDDEN
```

## ETF boundary

The settled 2026-07-27 Farside rows are usable:

- BTC: -11.6 USDm
- ETH: +11.7 USDm

They are session-level flow observations and do not replace current spot confirmation.

## Breadth boundary

The membership hash is present and the breadth row is auditable. The advance ratio may be used as current breadth evidence. It cannot establish a durable state transition from one snapshot.

## Stablecoin and DeFi boundaries

- Global stablecoin total remains unavailable.
- Chain distribution cannot be summed into a global total under the active method.
- Optional global DeFi TVL failed because the response exceeded the bounded payload budget.

## QA conclusion

```yaml
packet_usable: YES
full_sensor_coverage: NO
current_market_identity: PASS_WITH_OKX_AND_COINGECKO
settled_direct_gate_adjudication: NOT_ALLOWED
current_sentiment_confirmation: NOT_ALLOWED_STALE
rotation_upgrade: NOT_ALLOWED
portfolio_action: NONE
```
