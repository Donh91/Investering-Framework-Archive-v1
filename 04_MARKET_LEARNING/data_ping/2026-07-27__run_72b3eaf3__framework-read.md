# DATA PING framework read — run_72b3eaf3c8984befa318702e0c4e4f63

- Snapshot: `2026-07-27T14:39:04.061Z`
- Predecessor: `snap_f6488d4e57684f07b87ee148e75dc7d0`
- Collector status: `PARTIAL`
- Main-thread usability: `YES_WITH_STRICT_SOURCE_LIMITS`

## Framework state

```yaml
market_substate: ETH_LED_MOMENTUM_COOLING_WITH_GATE_UNCONFIRMED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Delta versus accepted morning ping

The comparable live sources show a material cooling during the approximately 7.6-hour interval:

- CoinGecko BTC: `65,474 -> 64,988`, delta `-0.7423%`
- CoinGecko ETH: `1,966.78 -> 1,948.67`, delta `-0.9208%`
- derived ETH/BTC: `0.0300391 -> 0.029985074`, delta `-0.1799%`
- OKX BTC last: `65,445 -> 64,932.6`, delta `-0.7829%`
- OKX ETH last: `1,968.05 -> 1,936.11`, delta `-1.6229%`
- total crypto market cap: `-0.3540%`
- total market volume: `+24.1567%`

ETH therefore underperformed BTC during the interval even though ETH remains stronger on the supplied 24-hour CoinGecko comparison.

## 0.0300 gate

The current packet has no direct ETH/BTC venue feed because all Binance actions failed under geo restriction.

The only current ratio is the CoinGecko-derived value:

```yaml
derived_ETHBTC: 0.029985074
relative_to_0_0300: -0.04975%
direct_feed_available: NO
settled_confirmation: NO
gate_adjudication_permitted: NO
```

The morning live touch above 0.0300 was not a settled confirmation and cannot be rescued or invalidated by this derived proxy. Current evidence is non-confirming.

## Breadth deterioration

Breadth weakened materially:

- advance ratio: `58.43% -> 37.50%`
- advancers: `52 -> 33`
- decliners: `22 -> 41`
- median 24-hour return: `+0.3% -> 0.0%`
- assets outperforming BTC: `27 -> 23`
- assets outperforming ETH: `7 -> 7`

This is not broad rotation confirmation. The market shifted from moderately positive breadth to mixed/negative participation.

## Derivatives and participation

Only OKX current data are usable.

- BTC OI USD: `-1.2684%` versus predecessor
- ETH OI USD: `-3.4594%` versus predecessor
- BTC current funding: `+0.006654%`
- ETH current funding: approximately `-0.000232%`
- BTC basis: `-7.39 bps`
- ETH basis: `-8.10 bps`

The combination is consistent with cooling and partial deleveraging, particularly in ETH. It is not evidence of escalating leverage-driven risk.

## Flow and macro context

- BTC ETF latest settled value remains `-240.1 USDm` for 2026-07-24.
- ETH ETF latest available value is stale at `+14.9 USDm` for 2026-07-23 and is not usable for current confirmation.
- CFGI inputs are stale or unavailable.
- FRED observations are effectively unchanged apart from VIX `18.70 -> 18.58`.
- global stablecoin total remains unavailable.

## Experiment treatment

### H7

Existing score remains:

`EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

This run is a degraded-source post-signal observation. It weakens immediate follow-through but does not rescore or invalidate the already matured five-row H7 event.

### F1

BTC remains well above both unresolved threshold candidates. Status remains:

`NO_FAILURE_OBSERVED_TO_DATE`

Final score remains withheld until the window closes at `2026-07-28T00:00:00Z`.

### F4 and F5

- F4 remains closed and is not reopened.
- F5 remains triggered and is not retriggered.

## Data-quality boundary

The packet attempted all planned actions, but 35 receipts failed and one was unavailable. All 34 Binance core actions plus the optional DeFi total TVL action failed. The packet is usable only for CoinGecko, OKX, BTC ETF, FRED, chain TVL, DEX and limited stablecoin-chain observations.

`meta.max_final_source_timestamp_utc` is null despite valid current timestamps from OKX and CoinGecko. This is treated as a metadata defect, not evidence that the packet lacks current observations.

## Conclusion

The morning ETH-led push has cooled, breadth has deteriorated, and the 0.0300 gate remains unconfirmed. The evidence does not authorize rotation, rebuy, new entry or portfolio action.
