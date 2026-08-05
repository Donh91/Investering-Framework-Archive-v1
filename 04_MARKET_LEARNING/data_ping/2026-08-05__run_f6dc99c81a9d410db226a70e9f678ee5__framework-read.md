# Framework read — run_f6dc99c81a9d410db226a70e9f678ee5

## Acceptance

`BOUNDED_CURRENT_OWNER_WITH_DIRECT_SPOT_DERIVATIVES_SETTLED_CANDLES_PARTIAL_ETF_SENTIMENT_MACRO_AND_SOURCE_QA`

This run is accepted as the latest decision-bearing bounded observation. It is 11,752.967 seconds after the prior bounded owner and contains a material independent update. It does not advance the canonical accepted predecessor because the collector supplied no accepted predecessor lineage and the framework state remains non-confirmatory.

## Change versus prior bounded owner

Prior owner: `run-4e87515bde8846aa9c51` at `2026-08-05T09:10:24.002Z`.

| field | prior | current | change |
|---|---:|---:|---:|
| BTCUSDT | 64,152.08 | 64,476.94 | +0.506390% |
| ETHUSDT | 1,870.69 | 1,879.16 | +0.452774% |
| ETHBTC | 0.02917 | 0.02915 | -0.068564% |
| BTC OI | 107,463.826 | 107,116.602 | -0.323108% |
| ETH OI | 2,317,193.659 | 2,327,675.836 | +0.452365% |

BTC and ETH both rose in USD, but ETH again failed to outperform BTC. BTC leverage contracted while ETH leverage rebuilt modestly.

## Transmission read

The strongest information is the split between ETHUSDT and ETHBTC execution:

- ETHUSDT spot taker-buy share is above 50% across 1h, 4h and 12h.
- ETHBTC spot taker-buy share is only 23.46% / 34.07% / 35.80% across the same windows.
- ETH futures taker ratio is positive at 1.0938, but global ETH long/short remains elevated at 2.3445.
- ETHBTC is down 0.4777% over 24h and 1.9166% over 48h.

Therefore current ETH demand is best interpreted as market-beta repair against USD, not ecosystem transmission against BTC. The rising ETH OI and positive futures aggression do not qualify as healthy rotation while relative spot flow is strongly sell-side.

## BTC read

BTC is the cleaner repair leg:

- price +0.51% versus prior bounded owner;
- OI -0.32% versus prior bounded owner;
- 24h return +0.95%;
- 48h return +0.97%;
- futures taker ratio near neutral at 1.0023;
- global long/short 1.31, materially less crowded than ETH.

BTC price strength with declining OI is consistent with continued absorption and reduced leverage dependence.

## Breadth read

Current breadth is 35 advancers, 41 decliners and 13 unchanged, with zero median and negative equal-weight mean. The membership hash changed from the prior bounded owner, so the small directional deterioration cannot be treated as an exact same-universe delta. The supplied v3/v1 transform also remains incompatible with the locked v1.1 scoring owner. Breadth is diagnostic and does not authorize a gate.

## ETF read

ETH ETF flow for 2026-08-04 is directly available at +$53.1M. BTC ETF parsing failed in this run. The previously verified +$211.5M BTC session remains valid source memory, but it is not forward-filled into the current packet and does not cure the current retrieval gap.

ETF evidence therefore remains supportive in the known latest settled history, but current-run cross-asset ETF comparison is not independently complete.

## Framework classification

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: BTC_LED_REPAIR_WITH_ETHUSD_PARTICIPATION_BUT_ETHBTC_RELATIVE_SELLING_AND_RECENT_ETH_OI_REBUILD
transmission_state: ABSORPTION_WITHOUT_CONFIRMED_ECOSYSTEM_TRANSMISSION
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

## What would change the read

A constructive change requires persistence rather than one-hour spikes: ETHBTC reclaim toward and above 0.0300, ETHBTC spot taker-buy share above 50% across at least 12–24 hours, compatible v1.1 breadth expansion, and ETH leverage growth that is accompanied by relative spot outperformance rather than only USD beta.