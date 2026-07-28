# DATA PING framework read — run_4fd139e79f5b4a1ba4d7d5c4c2d6aa10

```yaml
snapshot_utc: 2026-07-28T19:43:35.031Z
predecessor: snap_dd787b28a480498cb8e6de387c59ac7d
status: PARTIAL
classification: ETH_RELATIVE_STRENGTH_INTRADAY_PERSISTENCE_WITH_BREADTH_RELAPSE_AND_NO_SETTLED_DAILY_CONFIRMATION
```

## Current read

The broad market weakened again after the earlier rebound, while direct ETH/BTC remained above 0.0300 intraday.

```yaml
BTC_CoinGecko: 63,691 USD
ETH_CoinGecko: 1,912.42 USD
BTC_delta_vs_predecessor: -0.49%
ETH_delta_vs_predecessor: -0.67%
Total_market_cap_delta: -0.32%

Binance_ETHBTC_live: 0.03009
Binance_ETHBTC_24h_high: 0.03010
latest_settled_CEST_daily_close: 0.02995
settled_daily_confirmation_above_0_0300: NO
```

The current direct ETH/BTC value is stronger than the predecessor, but no new Copenhagen-settled daily candle exists. The latest completed daily close therefore remains below 0.0300.

## Participation

```yaml
advancers: 11_of_89
advance_ratio: 12.36%
previous_advance_ratio: 20.22%
delta: -7.87_percentage_points
median_24h_return: -1.9%
```

Breadth gave back 38.9% of its earlier advance ratio. This is incompatible with selective large-cap or broad-alt rotation confirmation.

## Flow and positioning

ETH/BTC taker buying remained elevated:

```yaml
ETHBTC_taker_buy_share:
  1h: 71.89%
  4h: 67.47%
  12h: 60.35%
```

Leverage did not expand broadly:

```yaml
Binance_OI_24h:
  BTC: -0.50%
  ETH: -2.08%
OKX_OI_USD_vs_predecessor:
  BTC: -0.95%
  ETH: -1.12%
```

The relative ETH bid therefore remains narrow and is not accompanied by broad participation or general OI expansion.

## Prospective evidence decision

This run belongs to the existing overlap cluster:

`ROTATION-2026-W31-ETHBTC-0030-ATTEMPT`

It does not create a second A-class row because:

- no new settled CEST daily confirmation exists;
- the policy state remains NO_ROTATION;
- action permission remains NONE;
- the observation is part of the same intraday threshold attempt.

```yaml
parent_receipt: PDR-20260728-0874091766e8
new_A_class_row: NO
A_rows_total: 1
duplicate_counting_prevented: YES
```

## Missing and boundaries

- Public-web adapter unavailable: no current ETF or CFGI update.
- Previous ETF and CFGI values are not reused as current-run evidence.
- Breadth membership hash remains unavailable.
- Stablecoin global total remains unavailable.
- Realized-volatility windows remain unavailable with only 13 settled hourly candles.
- H7 row 7 was not mature at this snapshot.

## Governance

```yaml
ETH_relative_strength: INTRADAY_PERSISTENCE_NARROW
selective_large_cap_rotation: NOT_CONFIRMED
broad_alt_rotation: NOT_CONFIRMED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```