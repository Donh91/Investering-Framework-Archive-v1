# H7 post-signal observation — 2026-07-27T14:39:04.061Z

## Existing adjudication

`EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

The matured score is unchanged.

## Current observation

The current run lacks a direct ETH/BTC market feed because Binance access failed under geo restriction. CoinGecko provides only a derived ratio:

- predecessor derived ratio: `0.0300391`
- current derived ratio: `0.029985074`
- change: `-0.1799%`
- current distance to 0.0300: `-0.04975%`

Comparable OKX prices show ETH underperformed BTC during the interval:

- BTC: `-0.7829%`
- ETH: `-1.6229%`

Breadth also deteriorated from a 58.43% to a 37.50% advance ratio.

## Governance treatment

```yaml
observation_type: POST_SIGNAL_DEGRADED_SOURCE_FOLLOW_UP
follow_through: WEAKENED
H7_rescore: NO
H7_invalidation: NO
rotation_confirmation: NO
canonical_state_change: NONE
```

A derived ratio cannot settle or hard-score the direct ETH/BTC gate. The current observation weakens immediate momentum but does not alter the already completed five-row prospective H7 event.
