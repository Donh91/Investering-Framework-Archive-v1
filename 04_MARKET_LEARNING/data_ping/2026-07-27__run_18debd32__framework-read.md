# DATA PING framework read — run 18debd32

```yaml
snapshot_utc: 2026-07-27T19:21:16.902Z
classification: ETHBTC_LIVE_RETOUCH_WITH_BREADTH_FAILURE_AND_NO_FLOW_CONFIRMATION
source_status: PARTIAL_BUT_MARKET_USABLE
chronology: PRE_OTA24_MATURITY
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## 1. Change since the 17:10 UTC predecessor

Method-compatible fields show a weak market tape with rising activity:

| Field | Change |
|---|---:|
| Total market cap | -0.10% |
| Total market volume | +3.30% |
| CoinGecko BTC | -0.06% |
| CoinGecko ETH | -0.16% |
| Derived ETH/BTC | -0.10% |
| Breadth advance ratio | 23.86% -> 21.35% |
| OKX BTC | +0.17% |
| OKX ETH | +0.67% |
| OKX BTC OI USD | -0.09% |
| OKX ETH OI USD | -0.49% |

The market did not broaden. Breadth weakened again to 19 advancers, 56 decliners and 14 unchanged across 89 included assets. Median 24-hour return remained -0.6%. Only 11 assets outperformed BTC and five outperformed ETH.

## 2. Direct ETH/BTC feed restored

Binance returned direct live ETH/BTC at `0.03001`, only 0.033% above 0.0300, after a 24-hour high of 0.03020.

```yaml
0_0275: HOLDS
0_0300_live_touch: YES
0_0300_settled_confirmation_at_snapshot: NO
F4_reopened: NO
rotation_gate_met: NO
```

The later OTA #24 settled evidence has higher authority and records the 2026-07-27 CEST close at 0.02995. Therefore this packet is correctly classified as a pre-settlement retouch, not a gate passage.

## 3. Multi-horizon price structure

### BTC

```yaml
1h_return_pct: -0.218
4h_return_pct: +0.295
12h_return_pct: -0.824
24h_return_pct: +0.799
48h_return_pct: +1.096
```

### ETH

```yaml
1h_return_pct: -0.233
4h_return_pct: +0.357
12h_return_pct: -1.486
24h_return_pct: +2.844
48h_return_pct: +3.682
```

### Direct ETH/BTC

```yaml
1h_return_pct: +0.033
4h_return_pct: +0.100
12h_return_pct: -0.631
24h_return_pct: +2.027
48h_return_pct: +2.556
```

ETH retained strong 24-hour and 48-hour relative leadership, but the 12-hour sequence had already faded materially from the intraday high. The live retouch near 0.0300 was therefore not accompanied by clean all-horizon continuation.

## 4. Spot-flow structure

Taker-buy shares remained below 50% for BTC and ETH across the 1-hour, 4-hour and 12-hour windows.

```yaml
BTC_taker_buy_share:
  1h: 45.14%
  4h: 49.15%
  12h: 47.07%
ETH_taker_buy_share:
  1h: 47.86%
  4h: 46.59%
  12h: 45.50%
ETHBTC_taker_buy_share:
  1h: 57.09%
  4h: 56.44%
  12h: 41.23%
```

This is a mixed microstructure signal: short-window direct relative-pair demand improved, while the longer 12-hour ETH/BTC window and both USD pairs remained seller-dominated.

## 5. Derivatives

```yaml
funding_latest_3_mean:
  BTC: +0.00588%
  ETH: +0.00659%
OI_change_24h:
  BTC: -1.89%
  ETH: -0.84%
Binance_basis_bps:
  BTC: -3.72
  ETH: -4.95
futures_taker_buy_sell_ratio:
  BTC: 0.961
  ETH: 1.081
```

Funding was positive but not extreme. Both assets had lower 24-hour open interest, which is more consistent with leverage reduction than a fresh leveraged breakout. ETH futures taker ratio remained slightly buy-dominant, while BTC remained sell-dominant.

Long/short ratios were elevated, so the positioning layer did not support aggressive interpretation of a marginal live gate touch.

## 6. Missing confirmation layers

```yaml
ETF_BTC: UNAVAILABLE
ETF_ETH: UNAVAILABLE
CFGI_global: UNAVAILABLE
CFGI_BTC: UNAVAILABLE
CFGI_ETH: UNAVAILABLE
stablecoin_global_total: UNAVAILABLE
realized_volatility: UNAVAILABLE_ONLY_13_SETTLED_HOURLY_CANDLES
```

No fresh ETF or sentiment layer was available. The collector correctly withheld realized volatility because only 13 settled hourly candles were available for requested 24-hour, 72-hour and 168-hour windows.

## 7. Experiment lifecycle at this timestamp

```yaml
H7:
  effect: LIVE_SUPPORTIVE_BUT_UNSETTLED
  rescore: NO
F1:
  status_at_snapshot: NOT_YET_MATURED
  final_score: WITHHELD_AT_THIS_TIMESTAMP
F4: CLOSED_NOT_REOPENED
F5: TRIGGERED_NOT_RETRIGGERED
```

Later OTA #24 maturity artifacts supersede this packet for F1 closure and H7 row 6 settlement. This packet remains valuable as the pre-settlement path showing that ETH/BTC briefly retouched 0.0300 while breadth was still deteriorating.

## 8. Framework decision

```yaml
price_transmission: PRESENT_BUT_FADING_INTRADAY
breadth_confirmation: NO
ETF_flow_confirmation: UNAVAILABLE
settled_gate_confirmation: NO
leverage_confirmation: NO
market_substate: ETHBTC_LIVE_RETOUCH_WITH_BREADTH_FAILURE_AND_NO_FLOW_CONFIRMATION
rotation_permission: NO
rebuy_permission: NO
new_entry_permission: NO
portfolio_action: NONE
```
