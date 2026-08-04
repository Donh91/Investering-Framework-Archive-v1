# DATA PING Framework Read

```yaml
run_id: run_18f02b7aa0334c9e
snapshot_id: snap_d23ae2d89bec47a8
snapshot_utc: 2026-08-04T09:01:37.097Z
acceptance: BOUNDED_CURRENT_OWNER_SPOT_DERIVATIVES_ETF_SENTIMENT_AND_SOURCE_QA_OBSERVATION
canonical_predecessor_advanced: false
canonical_state_change: NONE
portfolio_action: NONE
new_policy_event: false
new_A_class_receipt: false
new_shadow_dual_run: false
operational_risk_class: DO_NOT_ADD_RISK
risk_substate: BTC_LED_STABILIZATION_SHORT_TERM_FLOW_IMPROVING_WEAK_TRANSMISSION
```

## What improved

The short-term structure improved relative to the previous bounded observation:

- BTC and ETH futures taker ratios moved from below one to 1.0815 and 1.1801.
- BTC and ETH 24-hour open interest are now down 1.56% and 0.33%, indicating broader deleveraging rather than leverage expansion.
- ETH spot taker-buy share is above 50% across the four- and twelve-hour windows.
- The supplied v1 breadth universe reports 58.4% positive assets with positive mean and median returns.
- Global and ETH CFGI are current at 44, consistent with neutral rather than euphoric conditions.

These features reduce the immediate flush risk and support continued stabilization.

## What did not improve enough

- BTC and ETH prices are slightly below the previous bounded snapshot.
- ETH/BTC remains at 0.02922, with the latest settled Copenhagen close at 0.02931.
- The direct ratio remains below 0.0300 and the H7 transmission sequence remains terminated.
- BTC ETF flow is +170.1M while ETH ETF flow is -11.9M, preserving BTC-led absorption rather than ecosystem transmission.
- Current funding is elevated on both assets despite the 24-hour OI reduction.
- BTC spot taker-buy share remains below 50% across one-, four- and twelve-hour windows.
- ETH global long/short positioning remains elevated at 2.3602.
- Current compatible v1.1 breadth is unknown.

## Breadth authority

The 58.4% result is not ignored, but it cannot authorize a framework gate.

```yaml
supplied_filter: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
supplied_positive_share: 0.5842696629
supplied_membership_hash: 49d41929bf0ebe9b7b16c37bb1e31d6808b0b199e0f051a17b766b41c12a6b81
scoring_owner: BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1
current_scoring_owner_value: UNKNOWN
absolute_gate_permission: CLOSED
longitudinal_gate_permission: CLOSED
```

The supplied universe contains 89 assets, while the prior v1 observation contained 90. The hash makes this snapshot reproducible, but no current v1.1 constituent reclassification is possible from the summary packet alone.

## Framework interpretation

```yaml
market_cycle: EARLY_BULL_ATTEMPT_BTC_LED_EXTENDED_TRANSITION
current_market_state: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
current_substate: BTC_LED_STABILIZATION_SHORT_TERM_FLOW_IMPROVING
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
active_trim_signal: NO
```

The correct reading is not bearish deterioration and not bullish confirmation. BTC continues to hold the repair structure while leverage has cooled and short-term futures demand has improved. However, ETH/BTC, ETF divergence and missing compatible breadth prevent a transition from fragile repair to confirmed recovery or selective alt rotation.

## Decision conditions

A state upgrade still requires joint evidence:

1. BTC holds the repair and preferably settles above 64K without renewed OI acceleration.
2. ETH/BTC settles above 0.0300 with persistence.
3. Current v1.1 breadth exceeds 50% on a compatible capture.
4. Funding and long crowding remain controlled while spot participation improves.

A deterioration warning returns if BTC settles below 62.2K, especially if OI rebuilds during the decline. Hard structural deterioration remains a settled break below 59.4K–59.0K.

## Final effect

```yaml
immediate_pressure: EASED_RELATIVE_TO_PRIOR_BOUNDED_OBSERVATION
transmission: WEAK_UNCONFIRMED
rotation_permission: CLOSED
entry_permission: CLOSED
risk_permission: DO_NOT_ADD_RISK
canonical_effect: NONE
portfolio_effect: NONE
A_class_increment: 0
shadow_dual_run_increment: 0
```