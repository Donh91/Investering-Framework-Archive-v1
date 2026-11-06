# 47 | T06 first independent Binance × Hyperliquid same-UTC-day cross-venue challenge
**Date:** 2026-11-06 | **Status:** BOUNDED RETROSPECTIVE_SOURCE_CROSSCHECK, not an original 2026-10 market alert | **Owner:** Derivatives #387 and Task 2 #1596.
**Sources:** Verified on 2026-11-06 with connected Binance public market-data tool: `get_futures_usds_open_interest_statistics` and `get_futures_usds_taker_buy_sell_volume`, BTCUSDT/ETHUSDT, 1h, October 7 / October 23 2026. Reference Hyperliquid Ironflow original pinned trade files verified in actual PR #1988 Actions [#42311443044](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311443044), artifact `13548452685` SHA256 `fabb7923d5da81482429c931529874257dbc35e15b3b2b9154b4d836b1ca1e6d`. No Binance raw values stored beyond bounded aggregate table below.

## UTC boundary correction
Binance taker Buy/Sell tool query for `startTime=2026-10-23T00:00:00Z` originally returned rows **2026-10-22T23:00Z to 2026-10-23T22:00Z**, one-hour earlier than intended. To get the proper UTC 00:00..23:00 set of 24 1h rows, query `startTime=01:00Z` on target date and `endTime=00:59:59Z` on following date, limit 30; explicit first/last timestamp verified on all four BTC/ETH/date results. OI 00:00..23:00 needs the exact unshifted midnight time window. **The 1h Binance taker source may label periods by the ending hour; this offset is an observed returned-row window adjustment, NOT proof of exchange publication availability.** Never blindly join result order to Ironflow candle START timestamps.

## Empirical cross-venue taker direction
Negative means taker-sell flow exceeded buy flow. Binance denominator is *base-volume sum* (notional-normalized only approximately comparable to Ironflow USD quote-notional weights). Ironflow denominator is total USD-quote trade notional. Thus **sign and broad direction are worth comparing**, but numerical differences are not exact same-instrument measurements.

| Day | Asset | Binance taker imbalance | Hyperliquid taker imbalance | Signs |
|---|---|---:|---:|---|
| 2026-10-07 | BTC | **-3.79%** | **-11.63%** | both sell dominant |
| 2026-10-07 | ETH | **-7.84%** | **-5.86%** | both sell dominant |
| 2026-10-23 | BTC | **+0.19%** | **+0.42%** | both buy dominant |
| 2026-10-23 | ETH | **-0.34%** | **-8.10%** | both sell dominant but widely different magnitudes |

## Binance hour-start vs hour-end OI USD changes in the same days
| UTC day | Asset | Binance OI USD at first hourly reading | Binance OI USD last hourly reading | Observed change |
|---|---|---:|---:|---:|
| 2026-10-07 | BTC | $8.18239bn | $7.98777bn | **-2.379%** |
| 2026-10-07 | ETH | $6.23861bn | $6.16753bn | **-1.139%** |
| 2026-10-23 | BTC | $7.80573bn | $7.48405bn | **-4.121%** |
| 2026-10-23 | ETH | $5.56971bn | $5.47425bn | **-1.714%** |

All four Binance OI queries returned exactly 24 hourly observations, timestamped 00:00..23:00 UTC. Observation clock and publication knowability of public API historical returned rows was **not** independently established; these are retrospective, not usable as prior issued forecasts. No Hyperliquid OI day-to-day parity compared yet: not included in current summary artifact, must calculate exact same-clock row snapshots before claiming cross-venue OI disagreement.

## Scientific red team and next test
- A larger negative Binance BTC OI change occurred on **Oct 23 (-4.12%)** than the Oct 7 risk date (-2.38%), showing why a simple 'OI is falling' alarm is likely noisy without price, volume, realized liquidation, per-venue coverage and regime.
- Both venues show BTC selling Oct 7 and small BTC buying Oct 23, suggesting a potential contextual variable but **not evidence of advance warning**, since the flow is observed within those days.
- ETH Oct 23 sell imbalance differs sharply in magnitude across venues. This demands source-event time, venue-specific flow anatomy and same-clock price bars rather than pretending Binance is equivalent to Hyperliquid.
- This is only 2 dates / 2 markets, selected *after* observing the events: no model edge, confidence or statistical robustness, and no automatic canonical signal changes.
- Next: add a bounded independent 1h exchange native source collector to EXISTING research owner with exact as-of clocks, compare BTC/ETH OI and flow at same timestamps and source release lag, then run >=60d prospective tests and controls. Binance plugin reachability in this interactive session is not proof the GitHub runner has equivalent access (HTTP 451 reported historically), so fail with explicit `BINANCE_RUNNER_AUTHORITY_UNAVAILABLE` instead of fabricating.
