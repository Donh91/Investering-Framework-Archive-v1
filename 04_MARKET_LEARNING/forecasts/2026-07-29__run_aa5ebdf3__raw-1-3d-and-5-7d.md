# Prospective RAW 1–3D and RAW 5–7D — run_aa5ebdf331d34cd8bb27d71a71198cbe

**Forecast freeze UTC:** 2026-07-29T04:58:35Z  
**Source snapshot UTC:** 2026-07-29T00:11:40.027Z  
**Status:** PROSPECTIVE_RAW_NON_POLICY  
**Authority:** research/forecast only. No automatic market-state or portfolio authority.

## Frozen source state

```yaml
BTCUSDT: 64069.99
ETHUSDT: 1925.29
ETHBTC: 0.03006
BTC_24h_range: 62742.47-64200.00
ETH_24h_range: 1856.88-1929.67
ETHBTC_24h_range: 0.02953-0.03012
BTC_OI_24h_pct: -2.320224
ETH_OI_24h_pct: -0.580165
ETHBTC_taker_buy_share_12h: 0.612812
breadth: UNKNOWN
settled_Copenhagen_ETHBTC_close: UNKNOWN
ETF_current: UNKNOWN
CFGI_current: UNKNOWN
```

## RAW 1–3D

```yaml
classification: CONSTRUCTIVE_BUT_NARROW_AND_CATALYST_SENSITIVE
central_path:
  BTC: 62800-65800
  ETH: 1860-2010
  ETHBTC: 0.02970-0.03055
upside_extension:
  BTC: 66800
  ETH: 2050
downside_tail:
  BTC: 61900
  ETH: 1810
```

BTC is pressing the top of its current range while ETH and ETHBTC show stronger relative demand. Falling 24h open interest alongside higher live prices reduces the evidence for a leverage-driven blow-off. The main weakness is missing breadth confirmation and the unresolved exact Copenhagen-settled ETHBTC close. The near-term path therefore favors continued repair or consolidation over immediate broad alt rotation.

## RAW 5–7D

```yaml
classification: REPAIR_CAN_EXTEND_BUT_ROTATION_AND_BROAD_PARTICIPATION_REMAIN_UNCONFIRMED
central_path:
  BTC: 61900-67200
  ETH: 1820-2080
  ETHBTC: 0.02920-0.03120
bull_condition:
  - BTC holds completed closes above the repaired 63.3K area
  - direct Copenhagen-settled ETHBTC accepts above 0.0300
  - breadth recovers materially
bear_condition:
  - ETHBTC loses 0.0300 after failed settled acceptance
  - BTC loses 63.3K and then 61.9K
  - price strength continues without breadth
```

The seven-day upside case requires the narrow ETH-led move to broaden. Without that, the more likely structure is BTC resilience plus selective ETH/large-cap strength, followed by renewed volatility or alt underperformance.

## Simple translation

```yaml
price_range_translation:
  next_1_3_days:
    BTC_most_likely: 62800-65800
    ETH_most_likely: 1860-2010
  next_5_7_days:
    BTC_most_likely: 61900-67200
    ETH_most_likely: 1820-2080

action_translation:
  now: HOLD_AND_DO_NOT_CHASE
  new_microcaps: NO
  large_caps: WATCH_ONLY
  add_risk_only_if:
    - settled_ETHBTC_above_0_0300_is_verified
    - breadth_improves
    - BTC_holds_repaired_support
  defensive_trigger:
    - BTC_below_63300_weakens_the_repair
    - BTC_below_61900_materially_increases_pullback_risk
  portfolio_action: NONE
```

The ranges are prospective scenario bands, not guaranteed highs or lows. They must remain frozen for later comparison with verified outcomes.
