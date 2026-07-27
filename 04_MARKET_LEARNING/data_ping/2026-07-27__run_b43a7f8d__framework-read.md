# DATA PING framework read

- Run: `run_b43a7f8d213c4e63a5e60ca9cb19d764`
- Snapshot: `2026-07-27T17:10:00Z`
- Predecessor: `snap_05a6df8461ae4bdfa72e893da17295fb`
- Contract: `DATA_PING_RUN_FIRST_STATELESS_v1` v15.1.1
- Collector status: `PARTIAL`
- Framework use: `USABLE_WITH_STRICT_SOURCE_LIMITS`

## Accepted substate

```yaml
market_substate: ETH_TRANSMISSION_FOLLOW_THROUGH_DETERIORATING_WITH_BREADTH_CONTRACTION
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Comparable change from predecessor

Elapsed comparison age: 9,055.939 seconds, approximately 2 hours 31 minutes.

| Field | Change |
|---|---:|
| CoinGecko total market cap | -0.7402% |
| CoinGecko total volume | +8.3783% |
| CoinGecko BTC | -0.2354% |
| CoinGecko ETH | -0.5404% |
| CoinGecko derived ETH/BTC | -0.3057% |
| Breadth advance ratio | 37.50% -> 23.86% |
| OKX BTC last | -0.2042% |
| OKX ETH last | -0.0243% |
| OKX BTC OI USD | +0.9500% |
| OKX ETH OI USD | -3.3574% |

CoinGecko shows ETH underperforming BTC over the interval, while the separately timed OKX last-price observations show ETH approximately flat and BTC lower. This cross-source difference prevents a precise relative-price conclusion without a direct ETH/BTC feed. The robust common conclusion is that the earlier ETH impulse did not broaden and breadth weakened materially.

## ETH/BTC gates

- Current derived CoinGecko ratio: `0.029893421762165496`
- Distance to 0.0300: `-0.3553%`
- Distance above 0.0275: `+8.7034%`
- Direct ETH/BTC source: unavailable

The derived ratio is below 0.0300, but it has no authority to adjudicate the direct gate. The morning live touch remains unconfirmed. The 0.0275 load-bearing level continues to hold with a wide margin.

## Breadth

```yaml
included_assets: 88
advancers: 21
decliners: 56
unchanged: 11
advance_ratio: 0.238636
median_return_24h_pct: -0.6
outperforming_BTC: 14
outperforming_ETH: 5
membership_hash: UNAVAILABLE_POST_FREEZE
```

Breadth deteriorated for a second consecutive comparison. This is the strongest negative development in the run and is inconsistent with broad altcoin rotation.

## Derivatives

Only OKX current observations are usable.

```yaml
BTC_funding_current: 0.0000127514
ETH_funding_current: 0.00000520284
BTC_basis_bps: -4.5812
ETH_basis_bps: -4.9569
BTC_OI_USD_change_from_predecessor: +0.9500%
ETH_OI_USD_change_from_predecessor: -3.3574%
```

ETH open interest continued to contract while BTC open interest recovered. Funding is near neutral and the negative basis narrowed. The pattern is consistent with ETH deleveraging after the earlier impulse, not with accelerating leveraged rotation.

## ETF and sentiment treatment

The current run exposes a stale BTC ETF row for 2026-07-23, despite an accepted 2026-07-24 BTC row in the earlier run. It must not overwrite the accepted latest settled value. ETH 2026-07-24 at `-70.7M USD` is usable and matches the accepted owner value.

All CFGI values are unavailable. No sentiment update is admitted.

## Experiments

### H7

The matured H7 label remains:

`EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

This run is post-signal follow-through evidence only. Follow-through is classified `WEAKENED_MATERIALLY`, but the already matured event is neither rescored nor invalidated.

### F1

`NO_FAILURE_OBSERVED_TO_DATE` remains appropriate. BTC is still well above both threshold candidates, but the test window remains open until `2026-07-28T00:00:00Z`. Final score is withheld.

F4 remains closed. F5 is not retriggered.

## Data quality boundary

- 60/60 core actions attempted
- 21 PASS
- 1 PARTIAL
- 1 STALE
- 34 FAIL
- 3 UNAVAILABLE
- 35 total FAIL including the optional action
- Binance context and final groups failed under geo restriction
- direct ETH/BTC and all Binance-derived feature families unavailable
- global stablecoin total unavailable
- breadth membership hash unavailable because post-freeze compute was correctly forbidden

`max_nonfinal_source_timestamp_utc` is now populated while `max_final_source_timestamp_utc` remains null. This is a metadata improvement because the packet distinguishes absence of final-group data from the latest valid nonfinal timestamp.

## Governance

No Master Monday, Precision Score, replay, backtest, canonical state change or portfolio action was executed.