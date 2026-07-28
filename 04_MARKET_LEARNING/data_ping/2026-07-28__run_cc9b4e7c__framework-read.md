# DATA PING framework read — run cc9b4e7c

```yaml
snapshot_utc: 2026-07-28T09:55:00Z
classification: WEAK_INTRADAY_REBOUND_WITH_CAPITULATORY_BREADTH_AND_ETH_RELATIVE_FADE
source_status: PARTIAL_MARKET_USABLE_GATE_AUTHORITY_BLOCKED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## 1. Change since the 05:00 UTC predecessor

| Field | Change |
|---|---:|
| Total market cap | +0.26% |
| Total market volume | -3.10% |
| CoinGecko BTC | +0.36% |
| CoinGecko ETH | +0.14% |
| Derived ETH/BTC | -0.22% |
| Breadth advance ratio | 5.62% -> 8.99% |
| OKX BTC | +0.33% |
| OKX ETH | +0.13% |
| OKX BTC OI USD | +0.45% |
| OKX ETH OI USD | +1.15% |

The market bounced modestly from the preceding snapshot, but the bounce did not broaden. ETH recovered less than BTC, derived ETH/BTC weakened, and only eight of 89 included assets advanced.

## 2. Breadth remains capitulatory

```yaml
included_assets: 89
advancers: 8
decliners: 69
unchanged: 12
advance_ratio: 8.99%
median_return_24h: -2.70%
outperformed_BTC: 45
outperformed_ETH: 57
membership_hash: 8541eb36d887ad54bdaa8d9f777a0e884fc2f85ef37b2f4114f165d6e4aaa173
```

Breadth improved from an extreme 5.62% to 8.99%, but remains far below neutral participation. This is stabilization inside broad weakness, not breadth confirmation.

## 3. ETH transmission weakened further

The only current ETH/BTC observation was the derived CoinGecko ratio:

```yaml
derived_ETHBTC: 0.0296428234
change_since_predecessor: -0.22%
distance_below_0_0300: -1.19%
margin_above_0_0275: +7.79%
```

Direct Binance ETH/BTC was unavailable because of geo restriction. Therefore:

```yaml
0_0275_direct_gate_score: BLOCKED
0_0300_direct_gate_score: BLOCKED
H7_rescore: NOT_ALLOWED
rotation_confirmation: NO
```

The derived ratio indicates relative fading, but cannot hard-score a direct gate.

## 4. ETF flow diverged

Settled 2026-07-27 flows:

```yaml
BTC_ETF_USDm: -11.6
ETH_ETF_USDm: +11.7
net_cross_asset_USDm: +0.1
```

ETH received a modest positive ETF print while BTC was modestly negative. Yet ETH underperformed BTC in the current market snapshot. The flow is therefore supportive at the asset-specific institutional layer, but insufficient to overcome broad risk-off pressure or confirm transmission.

## 5. Derivatives show rebuilding under negative funding

```yaml
OKX_current_funding:
  BTC: -0.00145%
  ETH: -0.00243%
OKX_settled_funding:
  BTC: -0.00192%
  ETH: -0.00122%
OI_change_since_predecessor:
  BTC_USD: +0.45%
  ETH_USD: +1.15%
```

Open interest rose while funding was negative. This may reflect short rebuilding, hedging or renewed two-sided leverage. Direction cannot be determined from these fields alone. It does not qualify as bullish leverage confirmation.

## 6. Cycle Navigator #18 live-map status

```yaml
published_BTC_weekly_range: 62200_to_67200
published_ETH_weekly_range: 1800_to_2075
published_day_1_2_BTC: 63600_to_65900
published_day_1_2_ETH: 1870_to_1995
observed_BTC: 63470
observed_ETH: 1881.43
```

BTC was approximately 0.20% below the Day 1–2 lower map boundary but remained above the 63.1K repair area. ETH remained inside its Day 1–2 range. This is an intraday observation, not a settled score or invalidation.

## 7. Stale and missing confirmation layers

```yaml
CFGI_global: STALE_50
CFGI_BTC: STALE_47
CFGI_ETH: STALE_60
Binance_context: UNAVAILABLE_GEO
Binance_final: UNAVAILABLE_GEO
stablecoin_global_total: UNAVAILABLE
DeFi_total_TVL: RESPONSE_TOO_LARGE
```

Stale CFGI values are retained for lineage but excluded from current-state confirmation.

## 8. Framework decision

```yaml
price_structure: REBOUNDING_FROM_INTRADAY_STRESS
breadth: EXTREMELY_WEAK
ETH_relative_strength: FADING
ETF_flow: MIXED_WITH_ETH_POSITIVE
leverage: REBUILDING_WITH_NEGATIVE_FUNDING_UNRESOLVED
settled_63_1K_failure: NO_EVIDENCE_THIS_RUN
settled_direct_0_0300: UNAVAILABLE
market_substate: WEAK_INTRADAY_REBOUND_WITH_CAPITULATORY_BREADTH_AND_ETH_RELATIVE_FADE
rotation_permission: NO
rebuy_permission: NO
new_entry_permission: NO
portfolio_action: NONE
```

No forecast, experiment or backtest result is changed by this current-state packet.