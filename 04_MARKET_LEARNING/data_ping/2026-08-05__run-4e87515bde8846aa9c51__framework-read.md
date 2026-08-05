# DATA PING Framework Read

```yaml
run_id: run-4e87515bde8846aa9c51
snapshot_id: snap-bafd43eb4ab1fa90c0cb
acceptance: BOUNDED_CURRENT_OWNER_OBSERVATION
canonical_predecessor_advanced: false
canonical_state_change: NONE
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
risk_substate: BTC_LED_REPAIR_WITH_DUAL_ETF_INFLOWS_AND_SHORT_TERM_ETHBTC_REBOUND_BUT_NO_CONFIRMED_TRANSMISSION
```

## Market read

The market was nearly flat relative to the immediately preceding bounded observation:

```yaml
BTC: 64152.08
ETH: 1870.69
ETHBTC: 0.02917
BTC_change_vs_prior_bounded_pct: -0.044826
ETH_change_vs_prior_bounded_pct: 0.146149
ETHBTC_change_vs_prior_bounded_pct: 0.275009
```

ETH and ETH/BTC improved slightly over the short comparison interval, but ETH/BTC remains 2.77% below 0.0300 and approximately 6.07% above the 0.0275 load-bearing level. The improvement is therefore a rebound inside the existing weak-transmission regime, not a phase change.

## ETF flow

The 4 August US session is fully resolved:

```yaml
BTC_ETF_usd_m: 211.5
ETH_ETF_usd_m: 53.1
BTC_minus_ETH_usd_m: 158.4
```

Both assets attracted positive flows. BTC nevertheless received roughly four times the ETH dollar flow. Reproduced rolling windows show strong short-window BTC absorption and improving ETH flows:

```yaml
BTC_3_session: 116.2
BTC_5_session: 381.4
BTC_7_session: 320.1
BTC_10_session: -76.0
ETH_3_session: 50.2
ETH_5_session: 30.1
ETH_7_session: 51.2
ETH_10_session: 79.5
```

The dual-positive session removes the prior same-session ETF data gap. It improves the environment for repair but does not confirm capital transmission because BTC still dominates the flow, ETH/BTC remains below 0.0300 and AUM-normalized intensity is unavailable.

## Leverage and flow

BTC open interest continued to decline, including approximately 1.20% over 24 hours and 0.65% relative to the preceding bounded run. ETH open interest remained 0.64% lower over 24 hours but rebuilt approximately 0.39% relative to the preceding run.

BTC spot taker-buy share stayed above 50% over 1h, 4h and 12h. ETH and ETH/BTC produced strong one-hour buying, and ETH/BTC also exceeded 50% over four hours. Their 12-hour readings remained below 50%.

ETH funding on Binance was slightly negative and OKX funding remained close to neutral, but the ETH global long/short ratio remained elevated at 2.3841. The correct classification is a short-term ETH/ETHBTC rebound with cleaner aggregate leverage, not durable rotation confirmation.

## Breadth interpretation

The v3 diagnostic universe retained the same membership hash as the preceding run and improved:

```yaml
prior_advancers: 30
current_advancers: 36
prior_positive_share_full_universe: 0.337079
current_positive_share_full_universe: 0.404494
prior_median_return_pct: -0.222472
current_median_return_pct: 0.0
```

This is legitimate same-method directional improvement. However, 39 assets still declined versus 36 advancing, and the v3 transform uses the superseded v1 exclusion set rather than the locked v1.1 scoring owner.

```yaml
breadth_directional_read: IMPROVING_FROM_WEAK_TO_NEUTRAL_FRAGILE
breadth_gate_35: NOT_AUTHORIZED
breadth_gate_50: NOT_AUTHORIZED
breadth_gate_55: NOT_AUTHORIZED
rotation_effect: NONE
```

## Framework result

```yaml
market_phase: SELECTIVE_REPAIR / FRAGILE_TRANSLATION
current_situation: BTC_LED_REPAIR_WITH_DUAL_POSITIVE_ETF_FLOW_AND_SHORT_TERM_ETH_REBOUND
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
active_trim_signal: NO
portfolio_action: NONE
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
A_class_increment: 0
shadow_dual_run_increment: 0
```

This run improves the short-term repair picture. It resolves the ETF gap and shows a real short-window ETH/ETHBTC response. It does not activate selective alt rotation because settled ETH/BTC remains below 0.0300, 12-hour transmission is still sell-side, ETH positioning is long-heavy and the only available breadth transform cannot score the canonical gate.