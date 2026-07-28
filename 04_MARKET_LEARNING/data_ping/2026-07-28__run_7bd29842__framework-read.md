# DATA PING framework read — run 7bd29842

```yaml
snapshot_utc: 2026-07-28T17:12:27.297Z
classification: ETH_RELATIVE_STRENGTH_INTRADAY_BREAK_ATTEMPT_WITH_PARTIAL_BREADTH_REPAIR_NOT_ROTATION
source_status: NEAR_FULL_WITH_EXPLICIT_PARTIALS
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Material change

ETH led the rebound. CoinGecko BTC rose 0.99% from the predecessor, ETH rose 2.51%, and the derived ETH/BTC ratio rose 1.50%. Breadth improved from 6.74% to 20.22%, but remains far below a participation threshold that could support selective or broad rotation.

## Direct ETH/BTC

Binance direct ETH/BTC returned and traded at 0.03002. The 24-hour high was 0.03010 and the latest settled hourly close was 0.03007.

The latest completed CEST daily close remained 0.02995. Therefore:

```yaml
0_0300_intraday_touch: YES
0_0300_settled_daily_close: NO
H7_row7_settlement: NOT_YET_DUE
ETH_relative_strength: INTRADAY_CANDIDATE
selective_large_cap_rotation: NOT_CONFIRMED
broad_alt_rotation: NOT_CONFIRMED
```

A touch is not confirmation.

## Participation

```yaml
advancers: 18_of_89
advance_ratio: 20.22%
median_return_24h: -0.8%
breadth_membership_hash: MISSING
```

Participation repaired sharply from the extreme low, but four of five included assets still failed to advance. The missing membership hash also blocks hard promotion use.

## Flow and leverage

Direct ETH/BTC taker-buy share was 82.69% over one hour, 65.06% over four hours and 61.57% over twelve hours. ETH spot taker share also exceeded BTC across the displayed windows.

Funding was modest rather than crowded. Open interest fell 0.79% for BTC and 2.05% for ETH over 24 hours. The move therefore looks more spot-led and deleveraged than leverage-driven, but it is not yet settled confirmation.

ETF data still refers to the settled 27 July session: BTC -11.6 million USD and ETH +11.7 million USD. It cannot confirm the current intraday move.

## Decision

```yaml
rotation_permission: DENIED_UNSETTLED_AND_BREADTH_WEAK
rebuy_permission: NO_CHANGE_LOCKED
new_entry_permission: NO_CHANGE_NOT_ACTIVE
portfolio_action: NONE
```

This is the first prospective policy-relevant decision captured after Wave 1.4 activation.