# Framework Read — Extended 72H DATA PING

```yaml
run_id: run-d0fe59090ade0770962af29d
snapshot_utc: 2026-08-05T09:12:51.935761Z
classification: BOUNDED_EXTENDED_72H_LONGITUDINAL_EVIDENCE_SUPPLEMENT
base_bounded_owner_run_id: run-4e87515bde8846aa9c51
state_owner_advanced: false
canonical_predecessor_advanced: false
canonical_state_change: NONE
portfolio_action: NONE
```

## Executive read

The expanded sequence strengthens the existing framework distinction between **BTC absorption** and **ecosystem transmission**.

Across the valid settled interior of the requested 72-hour window:

- BTC gained 1.53%.
- ETH gained only 0.21%.
- ETH/BTC lost 1.35%.
- BTC repaired almost 3% from its observed low while contract OI fell 1.18% and global long/short crowding fell from 1.89 to 1.27.
- ETH repaired in USD while OI rose modestly and global long/short remained extremely elevated near 2.38.
- BTC had buy-side spot participation over the full window and over the latest 24 hours.
- ETH and ETH/BTC remained below 50% buy share over the latest 24 hours.
- ETH/BTC showed a final six-hour burst, but the latest 12- and 24-hour averages did not confirm persistence.

The correct interpretation is therefore:

> Price repair survived. BTC absorption improved. ETH transmission did not survive the full sequence.

## What the extended run adds beyond the compact run

The compact bounded run already established positive dual ETF flow, cleaner BTC leverage and a short-term ETH/BTC rebound. The extended packet shows what occurred before that endpoint and prevents the endpoint from being overread:

1. ETH/BTC began near 0.02957, reached 0.02978, then fell to 0.02906 and ended at 0.02917.
2. Settled Copenhagen ETH/BTC closes deteriorated from 0.02973 to 0.02931 to 0.02917.
3. The final hourly rebound was real but small compared with the preceding multi-day relative decline.
4. BTC repaired with leverage reduction and broad reduction in long crowding.
5. ETH retained long-heavy positioning and finished with a futures taker ratio of 0.6986.

This converts the short-window rebound from a potentially ambiguous observation into a clearer classification: **micro rebound inside unresolved transmission weakness**.

## Price and flow structure

```yaml
BTC_sequence_return_pct: +1.5349
ETH_sequence_return_pct: +0.2146
ETHBTC_sequence_return_pct: -1.3527
BTC_rebound_from_low_pct: +2.9920
ETH_rebound_from_low_pct: +2.3832
ETHBTC_rebound_from_low_pct: +0.3785
```

BTC remained the effective leader. ETH's USD repair was mostly participation in BTC-led stabilization rather than autonomous relative leadership.

The ETF structure is supportive but does not overturn this conclusion:

- BTC two-session ETF net: +$381.6M.
- ETH two-session ETF net: +$41.2M.
- BTC absorbed approximately 9.26 times the net dollar flow of ETH over those two sessions.

Positive ETH flow improves repair quality. It does not establish transmission when ETH/BTC and longer-window taker participation remain weak.

## Breadth and ecosystem health

Breadth was 36 advancers, 39 decliners and 14 unchanged within the 89-asset v3 universe. Median return was exactly zero and equal-weight mean was slightly positive.

That is **neutral-fragile breadth**, not expansionary breadth.

The membership hash matches the preceding v3 observation, so the directional comparison is valid. The transform still uses the superseded v1 exclusion set and therefore cannot score or open the locked v1.1 breadth gate.

Framework consequence:

```yaml
breadth_directional_read: IMPROVED_TO_NEUTRAL_FRAGILE
breadth_scored_gate_permission: NOT_AUTHORIZED
rotation_effect: NONE
```

## Leverage quality

BTC's sequence is comparatively constructive:

- contract OI fell 1.18%;
- global long/short fell from 1.8944 to 1.2722;
- top-account long/short fell from 1.9326 to 1.3294;
- price nevertheless ended 1.53% above the first valid hourly open.

This is consistent with repair accompanied by leverage cleansing rather than a purely leverage-driven pump.

ETH is less clean:

- contract OI rose 0.37%;
- global long/short increased from 2.3568 to 2.3841;
- top-account long/short increased from 1.8620 to 1.8969;
- latest futures taker ratio fell to 0.6986;
- relative price still declined 1.35% against BTC.

This is not an immediate collapse signal, but it raises the fragility of the ETH rebound and blocks an aggressive interpretation.

## Volatility and basis

Latest 24-hour realized volatility was below the 48-hour reading for BTC, ETH and ETH/BTC. Volatility therefore cooled during the latest portion of the sequence.

Current Binance and OKX basis readings remained mildly negative, with only small near-live mark differences. No venue dislocation or leverage stress sufficient to override the transmission read was observed.

## Macro context

VIX declined to 15.86, the broad trade-weighted dollar index was lower over four observations, and the 10Y–2Y spread was +0.45 percentage points.

This is a constructive background for continued repair. It remains context rather than an alt-rotation trigger.

Stablecoin global deployment could not be validated. That missing deployment sensor is material to any claim that liquidity has moved from BTC absorption into ecosystem expansion.

## Framework classification

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REPAIR_WITH_POSITIVE_DUAL_ETF_FLOW_BUT_72H_ETHBTC_UNDERPERFORMANCE_AND_ETH_LONG_HEAVY_POSITIONING
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
operational_risk_class: DO_NOT_ADD_RISK
```

## Decision translation

The large packet does not make the current state more bullish than the compact run. It makes the reasoning more reliable:

- BTC repair is genuine enough to keep stabilization active.
- dual ETF inflows reduce immediate downside pressure;
- BTC leverage quality improved;
- ETH has not yet demonstrated durable relative leadership;
- breadth is not broad enough and is not gate-compatible;
- stablecoin deployment remains unverified.

Therefore, the framework should continue to **watch for transmission rather than anticipate it**.

## Learning value

This run receives one longitudinal sequence-evidence increment because it resolves the path between snapshots. It receives no A-class increment, no shadow dual-run increment and no forecast or Cycle Navigator change because it is not independent evidence of a new state and its endpoint is nearly identical to the preceding bounded owner run.