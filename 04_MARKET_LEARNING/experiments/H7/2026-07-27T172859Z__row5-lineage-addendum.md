# H7 row 5 lineage addendum

## Supplied re-fetch evidence

| Symbol | Close | raw_row_sha256 |
|---|---:|---|
| BTCUSDT | 64858.02000000 | `a1b551b451d1f86f37b8ef11b50e8927bfb878d2fcd490728d8e753c6bc8f072` |
| ETHUSDT | 1925.91000000 | `16c38bc73b7e70251b0eeb5da03de5c8aa99f99e05ce74498e6e1e93ff88f927` |
| ETHBTC | 0.02969000 | `22ebc7884a4c34ab18c9a7339941c5e03b75969851b07800693eb5ca9164df09` |

Basis: `SETTLED_CEST`  
Source endpoint: `https://data-api.binance.vision/api/v3/klines`  
Requested candle open: `2026-07-26T21:00:00Z`

## Audit decision

The close values are reconfirmed and the three raw-row hashes are now present. However, the evidence block omits response hashes and uses an inexact retrieval timestamp. It also does not expose the original Ping 23 row hashes for a whole-row equality check.

```yaml
settlement_and_close_values: PASS
raw_row_hash_presence: PASS
response_hash_presence: FAIL_MISSING
exact_retrieval_timestamp: FAIL_INEXACT
original_to_refetch_whole_row_parity: NOT_PROVEN
lineage_grade: PARTIAL_LINEAGE_PASS
FULL_LINEAGE_PASS: NO
```

The existing H7 experiment score is not rescored or invalidated. This addendum affects audit completeness only.