# DATA PING main-framework read

```yaml
run_id: run_586b93af2ad54a49b13f7453e7ea40e2
snapshot_utc: 2026-07-27T07:02:46.401Z
source_status: PARTIAL_BUT_USABLE
market_substate: ETH_LED_GATE_TOUCH_WITHOUT_SETTLED_OR_FLOW_CONFIRMATION
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Executive read

The run shows a clear short-horizon ETH-led move:

- BTC +1.487% over 24 hours on Binance final;
- ETH +4.316%;
- direct ETH/BTC +2.837% at 0.03009;
- ETH also leads across the supplied 1h, 4h, 12h, 24h and 48h windows.

The direct ETH/BTC market has therefore moved slightly above the 0.0300 reference level on a live basis. This is a **live touch**, not a settled gate confirmation. A future gate adjudication must use the preregistered settlement basis and cannot be inferred from this intraday snapshot.

## Why the framework is not upgraded

### 1. No settled 0.0300 confirmation

```yaml
direct_ETHBTC_live: 0.03009
distance_above_0_0300_pct: 0.3
settled_gate_confirmation: NO
```

The 0.0275 load-bearing level continues to hold with a wide margin. The 0.0300 level has been touched live, but the packet does not provide the required settled observation for a hard gate.

### 2. ETF flow contradicts price transmission

The latest settled US sessions remain negative:

```yaml
BTC_ETF_2026_07_24_usd_m: -240.1
ETH_ETF_2026_07_24_usd_m: -70.7
flow_confirmation: NO
```

The move remains price-led rather than institutionally flow-confirmed.

### 3. Breadth is positive but not broad ETH-led rotation

```yaml
advance_ratio: 0.5843
median_return_24h_pct: 0.3
assets_outperforming_BTC: 27
assets_outperforming_ETH: 7
```

More assets advanced than declined, but only seven of 89 included assets outperformed ETH. This is consistent with ETH and selected large caps leading, not a broad altcoin rotation.

Exact breadth improvement versus earlier snapshots is not hard-scored because the collector had no accepted same-thread predecessor and the membership hash is specific to this run.

### 4. Derivatives participate, but are not extreme

```yaml
Binance_funding_current:
  BTC: 0.00005793
  ETH: 0.0001
OI_change_24h_pct:
  BTC: -2.620201
  ETH: 1.533814
futures_taker_buy_sell_ratio:
  BTC: 1.1195
  ETH: 1.2694
```

BTC rose while OI fell, which is compatible with a cleaner deleveraging or short-covering component. ETH rose with modest OI expansion and stronger taker buying. This supports participation but does not prove durable spot-led transmission. Funding and basis do not show an obvious extreme leverage condition in this snapshot.

### 5. Macro and liquidity confirmation remain incomplete

- 2-year and 10-year Treasury yields increased over the recent observations;
- VIX is 18.70;
- the broad dollar series is only updated through 17 July;
- global stablecoin capitalization is unavailable;
- CFGI is stale;
- realized volatility cannot be computed from the available settled window.

These gaps prevent a full liquidity or risk-regime confirmation.

## Experiment impact

```yaml
H7:
  existing_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
  current_run_effect: LIVE_SUPPORTIVE_OBSERVATION_ONLY
  post_signal_settled_row_scored: NO

F1:
  current_status: NO_FAILURE_OBSERVED_TO_DATE
  final_score: WITHHELD_UNTIL_WINDOW_CLOSE

F4:
  status: CLOSED_GATE_UNMET_NOT_REOPENED

F5:
  status: TRIGGERED_NOT_RETRIGGERED
```

This snapshot strengthens the descriptive case behind H7, but it does not score the first post-signal settled CEST row. F1 remains open until its full window closes.

## Final classification

```yaml
classification: ETH_LED_TRANSMISSION_CANDIDATE_STRENGTHENING
confirmation_level: LIVE_NOT_SETTLED
flow_support: NEGATIVE
breadth_support: PARTIAL_NARROW
macro_support: NOT_CONFIRMED
rotation_permission: NO
rebuy_permission: NO
new_entry_permission: NO
portfolio_action: NONE
```

No Master Monday, Precision Score, backtest or canonical framework change was executed from this run.
