# W30 CN / RAW Bridge

**Source:** Claude W30 Master Monday evidence recovery  
**Status:** `DETERMINISTIC_FEATURE_HANDOFF / NON_CANONICAL`

## Snapshot and comparability

```yaml
snapshot_utc: 2026-07-26T12:26:13Z
comparison_snapshot_id: dp_snapshot_1785058122538
comparison_age_hours: 1.88
comparison_scope: MIXED
```

Comparability rules:

- CoinGecko dominance and settled Farside rows are directly comparable.
- DATA PING rounded spot values are only approximately comparable.
- ETH/BTC before-value in the comparison was derived from rounded pair prices; the recovery package used a direct market.
- OKX derivatives are not directly comparable to Binance-based DATA PING derivative history.

## Core state vector

```yaml
BTC:
  live_usd: 64517.60
  return_24h_pct: 0.69
  return_48h_pct: -0.67
  close_2026_07_25_utc: 64375.00
  distance_to_65600_pct: -1.65
  distance_to_62200_pct: 3.73
  volatility_48h_vs_30d_median: 0.54

ETH:
  live_usd: 1887.10
  return_24h_pct: 1.49
  return_48h_pct: 0.13
  relative_vs_btc_24h_pp: 0.79
  volatility_48h_vs_30d_median: 0.44

ETHBTC:
  live: 0.02926
  return_24h_pct: 0.79
  return_48h_pct: 0.76
  settled_gate_0_0300_count_14d: 0
  settled_reference_0_0275_count_14d: 14
  distance_to_0_0300_pct: -2.47
  distance_to_0_0275_pct: 6.40
  volatility_48h_vs_30d_median: 0.64
```

## Flow features

```yaml
ETF:
  latest_common_session: 2026-07-24
  btc_net_flow_usd_m: -240.1
  eth_net_flow_usd_m: -70.7
  btc_sum_2_sessions_usd_m: -465.2
  eth_sum_2_sessions_usd_m: -44.4
  btc_sum_7_sessions_usd_m: 245.3
  weekend_status: NON_SESSION

Breadth:
  universe_size: 80
  advancers: 58
  decliners: 13
  unchanged: 9
  advance_ratio: 0.725
  median_return_24h_pct: 0.95
  pct_outperforming_btc_24h: 51
  pct_outperforming_eth_24h: 37
  outlier_only: false
  sector_breakdown: MISSING
```

## Positioning features

```yaml
BTC_OKX:
  funding_pct_8h: 0.0023
  oi_change_24h_pct: -1.53
  basis_pct: -0.0578
  price_oi_label_24h: PRICE_UP_OI_DOWN
  global_long_short_ratio: 1.74
  top_account_ratio: 1.218
  top_position_ratio: 0.95

ETH_OKX:
  funding_pct_8h: 0.0018
  oi_change_24h_pct: 2.10
  basis_pct: -0.0546
  price_oi_label_24h: PRICE_UP_OI_UP
  global_long_short_ratio: 1.71
  top_account_ratio: 1.258
  top_position_ratio: 0.925
```

## Liquidity features

```yaml
stablecoin_total_usd_b: 306.79
stablecoin_change_1d_pct: -0.03
stablecoin_change_7d_pct: 0.06
stablecoin_change_30d_pct: -1.66
usdt_usd_b: 184.29
usdc_usd_b: 73.54
exchange_stablecoin_balances: MISSING
```

## Macro features

```yaml
DGS2_pct: 4.37
DGS10_pct: 4.71
VIX: 18.70
HY_OAS_pct: 2.77
DXY_yahoo: 101.47
FOMC_decision_utc: 2026-07-29T18:00:00Z
FOMC_press_conference_utc: 2026-07-29T18:30:00Z
FOMC_SEP: NONE_EXPECTED
FOMC_confounds_leading_claim: true
```

## Eligibility

```yaml
eligible_for_longitudinal_use:
  spot_and_settled_closes: true
  ETF: true
  CoinGecko_dominance: true
  breadth_core: true
  volatility: true
  OKX_derivatives_as_venue_tagged_series: true

blocked_or_limited:
  cross_venue_derivative_continuity: true
  sector_breadth: true
  exchange_stablecoin_balances: true
  per_asset_CFGI: true
  low_vol_score: INTERNAL_CONFLICT
  Stage1_count: INTERNAL_CONFLICT
```

## Interpretation boundary

The bridge records features and eligibility only. It does not classify recovery, rotation, altseason, rebuy, deployment or portfolio action.