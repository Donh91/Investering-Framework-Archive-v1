# H7 post-signal follow-through

- Snapshot: `2026-07-27T17:10:00Z`
- Run: `run_b43a7f8d213c4e63a5e60ca9cb19d764`
- Existing matured score: `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

## Observation

Comparable CoinGecko data show ETH underperforming BTC over the 2.52-hour comparison interval and the derived ETH/BTC ratio falling 0.3057%. Breadth fell from 37.50% to 23.86% advancers. OKX ETH OI USD fell 3.36% while BTC OI USD rose 0.95%.

## Adjudication

```yaml
follow_through: WEAKENED_MATERIALLY
matured_event_rescore: NO
matured_event_invalidation: NO
rotation_confirmation: NO
```

The current run lacks a direct ETH/BTC feed and therefore cannot score a direct gate or settled H7 row. H7 row 6 remains pending until its predefined settlement time.

No framework or portfolio consequence.