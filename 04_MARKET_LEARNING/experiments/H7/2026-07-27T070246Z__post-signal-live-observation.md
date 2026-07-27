# H7 post-signal live observation

```yaml
experiment_id: H7_TRANSMISSION_RATE_CHALLENGER
observed_at_utc: 2026-07-27T07:02:46.401Z
observation_type: LIVE_INTRADAY_NOT_SETTLED
existing_score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
score_change: NONE
state_effect: NONE
```

## Observation

```yaml
BTCUSDT_last: 65396.00
BTCUSDT_24h_pct: 1.487
ETHUSDT_last: 1966.82
ETHUSDT_24h_pct: 4.316
ETHBTC_direct_last: 0.03009
ETHBTC_24h_pct: 2.837
```

The first market snapshot after H7 maturation remains directionally supportive: ETH leads BTC and the direct ETH/BTC pair trades slightly above 0.0300.

## Why this is not a new score

- the observation is live rather than a settled CEST row;
- H7 has already matured and must not be retriggered;
- the 0.0300 gate requires a preregistered settlement basis;
- latest settled BTC and ETH ETF flows are negative;
- breadth is positive but only seven included assets outperform ETH.

```yaml
post_signal_continuation: INDICATED_LIVE
post_signal_settled_confirmation: PENDING
rotation_confirmation: NO
portfolio_action: NONE
```
