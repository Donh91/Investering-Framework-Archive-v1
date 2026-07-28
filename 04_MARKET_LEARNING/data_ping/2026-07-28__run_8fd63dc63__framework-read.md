# DATA PING framework read — run 8fd63dc63

```yaml
snapshot_utc: 2026-07-28T05:00:00Z
chronology: FIRST_POST_OTA24_DATA_PING
classification: BROAD_RISK_OFF_WITH_BREADTH_COLLAPSE_AND_ETH_DELEVERAGING
source_status: PARTIAL_BUT_MARKET_USABLE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## 1. Material change since predecessor

The market deteriorated sharply over the 9.65-hour comparison interval:

| Field | Predecessor | Current | Change |
|---|---:|---:|---:|
| Total market cap | 2.298T | 2.251T | -2.03% |
| Total market volume | 65.34B | 68.81B | +5.30% |
| CoinGecko BTC | 64,798 | 63,245 | -2.40% |
| CoinGecko ETH | 1,935.12 | 1,878.89 | -2.91% |
| Derived ETH/BTC | 0.029864 | 0.029708 | -0.52% |
| Breadth advance ratio | 21.35% | 5.62% | -73.68% |
| OKX BTC | 64,908 | 63,293.2 | -2.49% |
| OKX ETH | 1,948.62 | 1,879.89 | -3.53% |
| OKX BTC OI USD | 1.978B | 2.015B | +1.88% |
| OKX ETH OI USD | 1.482B | 1.354B | -8.65% |

Price weakness broadened while activity increased. This is materially more serious than a narrow BTC pullback.

## 2. Breadth collapsed

```yaml
included_assets: 89
advancers: 5
decliners: 70
unchanged: 14
advance_ratio: 5.62%
median_return_24h_pct: -3.00%
BTC_outperformance_count: 43
ETH_outperformance_count: 47
membership_hash: UNAVAILABLE
```

Only five included assets advanced. The median asset fell 3.0%, and more assets outperformed ETH than BTC because ETH underperformed during the selloff.

The missing membership hash reduces audit completeness, but the fixed filtering method and 89-row count remain method-compatible with the predecessor. The breadth result is usable with an explicit QA caveat.

## 3. ETH transmission under material stress

```yaml
ETHBTC_derived: 0.0297081192
distance_below_0_0300_pct: 0.97
margin_above_0_0275_pct: 8.03
BTC_24h_pct: -3.14
ETH_24h_pct: -3.81
```

ETH underperformed BTC and the derived ratio fell back below 0.0300. Direct Binance ETH/BTC was unavailable, so this packet cannot hard-score H7 row 7 or a settled gate.

The correct interpretation is:

```yaml
H7_original_score: UNCHANGED
H7_current_follow_through: UNDER_MATERIAL_STRESS
0_0300_settled_confirmation: NOT_PROVEN
0_0275_load_bearing_gate: HOLDS_ON_DERIVED_REFERENCE_ONLY
rotation_confirmation: NO
```

## 4. Derivatives show asymmetric deleveraging

OKX current funding changed from positive to negative or neutral:

```yaml
BTC_current_funding: -0.00499%
ETH_current_funding: -0.00010%
BTC_settled_funding: +0.00242%
ETH_settled_funding: +0.00049%
BTC_basis_bps: -4.97
ETH_basis_bps: -4.09
```

Open-interest change versus the predecessor:

```yaml
BTC_OI_USD_change_pct: +1.88
ETH_OI_USD_change_pct: -8.65
```

BTC OI increased into a falling market while ETH OI collapsed. This is a cautionary divergence:

- BTC may be accumulating new short exposure or defensive hedging;
- ETH experienced clear leverage liquidation or position reduction;
- neither supports a clean rotation upgrade.

The exact positioning direction cannot be known from OI alone, so no stronger claim is made.

## 5. ETF print is now verified

The previously quarantined 2026-07-27 Farside rows are now current and usable:

```yaml
BTC_ETF_net_flow_usd_m: -11.6
ETH_ETF_net_flow_usd_m: +11.7
combined_net_flow_usd_m: +0.1
```

This is effectively flat in aggregate but mildly ETH-supportive in composition.

It provides a counterweight to the risk-off tape, not confirmation of rotation, because:

- ETH price underperformed BTC;
- breadth collapsed;
- ETH OI fell 8.65%;
- direct settled ETH/BTC confirmation was absent.

## 6. Sentiment remained neutral

```yaml
CFGI_global: 48_NEUTRAL
CFGI_BTC: 51_NEUTRAL
CFGI_ETH: 57_NEUTRAL
```

The values do not show panic despite broad price weakness. Source timestamps were not supplied, so the sentiment layer is supportive as context but not precise enough for event timing.

## 7. Macro and liquidity context

```yaml
DGS2: 4.33
DGS10: 4.69
yield_curve_10y_minus_2y: +0.36pp
VIX: 18.58
broad_dollar_index: 120.7105
```

The macro update is incremental, not a direct explanation for the intraday crypto move.

Chain TVL weakened:

```yaml
Ethereum_TVL_change_vs_predecessor_pct: -1.91
ETH_Dex_top_pool_volume_change_pct: -8.45
```

Stablecoin global total remained unavailable. Chain-distribution values cannot be aggregated into a substitute global total.

## 8. Relation to Cycle Navigator #18

The published W31 forecast defines:

```yaml
BTC_day_1_2_range: 63600_to_65900
ETH_day_1_2_range: 1870_to_1995
BTC_bear_invalidation: settled_close_below_62200_and_failed_reclaim
```

At this snapshot:

- BTC around 63.25K was below the Day 1-2 forecast floor of 63.6K;
- ETH around 1,879 remained inside its Day 1-2 range, close to the lower boundary;
- BTC had not produced a settled close below 62.2K;
- the 63.1K repair area had been intraday-tested around OTA #24 but was partially reclaimed by the snapshot.

The forecast is under early pressure, but the weekly bear invalidation is not met.

## 9. Framework decision

```yaml
repair_structure: UNDER_MATERIAL_INTRADAY_PRESSURE
breadth_confirmation: FAILED
ETH_transmission: UNDER_MATERIAL_STRESS
ETF_flow: MIXED_NEAR_FLAT_WITH_ETH_OFFSET
sentiment: NEUTRAL
leverage: ETH_DELEVERAGING_BTC_OI_RISING
settled_0_0300: NO
settled_0_0275_failure: NO
rotation_permission: NO
rebuy_permission: NO
new_entry_permission: NO
portfolio_action: NONE
```

No canonical transition is justified before settled evidence and the next H7 row at 2026-07-28T22:00:00Z.
