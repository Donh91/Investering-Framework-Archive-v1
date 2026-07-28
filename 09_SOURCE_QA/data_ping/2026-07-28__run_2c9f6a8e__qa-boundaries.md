# DATA PING source-QA boundaries — run 2c9f6a8e

```yaml
run_id: run_2c9f6a8e74b24d65a1f3c0978e5b4132
snapshot_utc: 2026-07-28T12:45:00Z
qa_status: PARTIAL_WITH_DIRECT_MARKET_AUTHORITY_MISSING
```

## Passed families

- CoinGecko: 4/4 PASS
- FRED: 4/4 PASS
- OKX cross-check: 10/10 PASS
- GeckoTerminal: PASS
- DeFiLlama chain TVL: PASS

## Failed or unavailable families

### Binance

All 23 context calls and all 11 final calls failed with geo restriction. Consequences:

- no direct ETH/BTC;
- no settled Binance OHLC;
- no Binance spot-taker data;
- no Binance funding history;
- no Binance OI anchors;
- no cross-venue mark comparison;
- no realized-volatility family.

OKX perpetual data remains a challenger cross-check and cannot replace Binance spot authority.

### Public web

BTC ETF, ETH ETF and all three CFGI actions were unavailable. No value may be carried forward as current and no missing value may be converted to zero or neutral.

### Breadth

The aggregate returned 89 included assets, but the membership hash was not computed. Breadth is accepted as a soft current-state observation only. It cannot serve as a hard promotion or replication artifact.

### Stablecoins

Global total remains unavailable. Chain distribution cannot be summed into a synthetic global total under the active contract.

## Temporal and authority boundary

```yaml
ETHBTC_derived_ratio_available: YES
ETHBTC_direct_ratio_available: NO
0_0275_gate_scoring_allowed: NO
0_0300_gate_scoring_allowed: NO
H7_rescore_allowed: NO
ETF_flow_update_allowed: NO
CFGI_update_allowed: NO
```

## Backtest isolation

This packet was generated after the frozen historical research runs and is not admitted into Wave 1 or Wave 1.1 training, scoring or holdout data.

```yaml
backtest_effect: NONE
final_holdout_opened: NO
framework_state_change: NONE
portfolio_action: NONE
```
