# DATA PING Framework Read

```yaml
run_id: run-eec8e2d4c3114f0eac01
snapshot_id: snap-4ae65617f89d43488a2d
snapshot_utc: 2026-08-05T13:26:08.110Z
acceptance: BOUNDED_CURRENT_OWNER_WITH_LINKED_NONCANONICAL_PREDECESSOR
canonical_predecessor_advanced: false
canonical_state_change: NONE
portfolio_action: NONE
```

## Executive interpretation

The market remains in selective repair / fragile translation.

The latest hour produced a modest pullback in both BTC and ETH while final open interest declined on both assets. This is not evidence of a leverage-driven breakdown. BTC continues to hold the cleaner structure: its 24-hour price return remains positive, its 24-hour OI change remains negative, and its global long/short ratio is substantially lower than ETH's.

ETH shows mixed evidence. ETH spot buying is near or slightly above 50% on four- and twelve-hour windows and its futures taker ratio is positive, but ETH/BTC remains at 0.02913, approximately 2.9% below 0.0300. A strong one-hour ETHBTC taker-buy burst did not persist into the four- or twelve-hour windows. ETH also remains long-heavy and recently rebuilt OI inside an otherwise deleveraged 24-hour structure.

## Predecessor interpretation

The run contains a usable method-compatible predecessor reference to `run-4e87515bde8846aa9c51 / snap-bafd43eb4ab1fa90c0cb`.

This is meaningful because it permits a bounded longitudinal comparison. It does not authorize canonical advancement because:

1. it is not the accepted canonical predecessor from 29 July;
2. it is not the immediately prior bounded owner;
3. bounded observations remain non-binding until the accepted-log lifecycle ratifies them.

The correct framework treatment is therefore: improved lineage quality, bounded owner advancement, no canonical pointer movement.

## Market structure

```yaml
BTCUSDT: 64130.69
ETHUSDT: 1867.73
ETHBTC: 0.02913
BTC_24h_return_pct: 0.949597
ETH_24h_return_pct: 0.467912
ETHBTC_24h_return_pct: -0.477653
BTC_48h_return_pct: 0.968873
ETH_48h_return_pct: -0.958507
ETHBTC_48h_return_pct: -1.916611
```

BTC is still repairing in USD while ETH underperforms over both 24 and 48 hours. The transmission problem has not improved structurally.

## Flow and leverage

BTC spot taker-buy share is above 50% on one-, four- and twelve-hour windows. ETH is near neutral to slightly positive on four- and twelve-hour windows. ETHBTC is strongly positive only on the one-hour window and remains below 50% on four and twelve hours.

The OI anchors show 24-hour deleveraging in both assets, but recent ETH OI rebuilding on one- and four-hour horizons. This combination is compatible with a fragile rebound but not a confirmed transmission regime.

## ETF

The 4 August session remains fully confirmed:

```yaml
BTC_ETF_usd_m: 211.5
ETH_ETF_usd_m: 53.1
BTC_minus_ETH_usd_m: 158.4
```

The run adds no new ETF session. It reconfirms dual-positive flows with BTC absolute-dollar dominance.

## Breadth

The v3 breadth transform returned to the same membership hash as the supplied bounded predecessor. Within that comparable universe, the positive share slipped from 40.45% to 39.33%, decliners increased and equal-weight mean turned more negative.

This remains diagnostic only. The locked scoring owner is v1.1, so no 35%, 50% or 55% breadth gate is authorized.

## Framework state

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
current_situation: BTC_LED_REPAIR_WITH_INTRADAY_PULLBACK_24H_DELEVERAGING_AND_TRANSIENT_ETHBTC_BUY_BURST_WITHOUT_PERSISTENT_TRANSMISSION
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
active_trim_signal: NO
operational_risk_class: DO_NOT_ADD_RISK
```

## Decision translation

The pullback does not invalidate BTC repair, because leverage did not expand into the decline. It also does not open a buying window, because ETH/BTC remains below 0.0300, the ETHBTC buy burst lacks persistence, ETH positioning remains long-heavy and breadth is both sub-50 and method-incompatible with the locked gate owner.