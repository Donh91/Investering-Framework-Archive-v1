# Rotation Repair Edge Event Update: W30 Settled Closeout

**Source snapshot:** `MASTER_MONDAY_CLOSEOUT_W30_20260720T054959Z`  
**Accepted at:** 2026-07-20 08:09:51 CEST  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Authority:** MAIN_FRAMEWORK / CHATGPT

## Decision delta

```yaml
review_type: MASTER_MONDAY_FINAL_SETTLED_WEEKLY_CLOSEOUT
decision_delta_class: SETTLED_STRUCTURE_CONFIRMATION_WITH_SHORT_HORIZON_WARNING
material_delta: W30_SETTLED_BTC_CLOSE_ABOVE_63300_AND_ETHBTC_ABOVE_0275_WITH_P1_SURVIVAL_HELD_BUT_DYNAMIC_BREADTH_WEAK_AND_1H_4H_SPOT_FLOW_NEGATIVE
action_changed: false
alert_change: DE_ESCALATED_ONE_LEVEL_MAINTAINED_NOT_CLEARED
```

## Settled weekly structure

```yaml
BTC:
  close: 64415.75
  weekly_change_pct: 0.7749482168
  CLV: 0.6862938838
  above_63300: true
  above_61900: true
  above_59400: true
ETH:
  close: 1862.12
  weekly_change_pct: 2.750126912
  CLV: 0.5700896496
ETHBTC:
  close: 0.02891
  weekly_change_pct: 1.975308642
  CLV: 0.4375
  above_0_0275: true
  above_0_0300: false
  higher_low_vs_previous_week: true
```

## P1 holdout

```yaml
reference_price: 62065.06
post_reference_peak: 65600.0
settled_weekly_close: 64415.75
provisional_peak_advance_retention_pct: 66.498724165
sessions_elapsed: 6
seven_day_review_date: 2026-07-21
seven_day_review_status: NOT_DUE
any_post_reference_close_below_62200: false
status: SURVIVAL_HELD_PROVISIONAL_REVIEW_NOT_DUE
```

## Positive evidence

- Settled BTC weekly close is above 63.3K and 61.9K.
- Direct ETH/BTC settled weekly close is above 0.0275 and printed a higher weekly low.
- BTC ETF total and IBIT are positive for four completed sessions in succession.
- BTC seven-session ETF flow is positive at +70.6M USD.
- BTC and ETH 24H Binance spot taker flow remain positive.
- BTC and ETH 24H OI declined modestly, reducing leverage pressure.

## Warning evidence

- Direct ETH/BTC remains below 0.0300 confirmation.
- Dynamic breadth membership changed and cannot provide a persistence delta.
- Absolute dynamic breadth is weak: 14.08% positive at 1H, 23.94% at 24H and 40.85% at 7D.
- BTC and ETH Binance spot taker flow are negative at 1H and 4H.
- BTC and ETH futures taker ratios remain below or approximately equal to 1.
- FIXED_RISK35 remains unknown and reconstruction is forbidden.
- Official stablecoin history and market-wide CVD remain unavailable.

## Main Framework decision

```yaml
framework_edge_state: REPAIR_PRESENT_MATURING_SETTLED_WEEKLY_CONFIRMATION_WITH_BREADTH_AND_SHORT_HORIZON_FLOW_WEAKNESS
pullback_warning: ACTIVE_DE_ESCALATED_ONE_LEVEL_MAINTAINED_NOT_CLEARED
short_term_stabilization: SETTLED_STRUCTURAL_REPAIR_CONFIRMED_SHORT_HORIZON_COOLING_ACTIVE
rotation: NO_ROTATION
broad_recovery: NOT_CONFIRMED
large_cap_window: WATCH_ONLY_NOT_OPEN
new_entry_signal: NOT_ACTIVE
active_trim_signal: NO
portfolio_action: NONE
user_action: HOLD_AND_WAIT
risk_posture: ELEVATED_VIGILANCE_DE_ESCALATED_NO_FURTHER_CLEARANCE
```

The settled weekly close removes the prior partial-candle blocker and confirms that structural repair survived W30. It does not confirm rotation or broad recovery because ETH/BTC remains below 0.0300 and participation and short-horizon flow are weak. The existing warning remains de-escalated by one level but receives no further clearance.
