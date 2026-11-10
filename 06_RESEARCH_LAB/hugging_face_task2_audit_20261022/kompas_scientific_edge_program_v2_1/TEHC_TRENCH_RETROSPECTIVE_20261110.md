# Task 2 + Alpha S7 | Tehc Trench retrospective study | 2026-11-10

**Classification: RETROSPECTIVE_VENDOR_BACKFILL_ONLY / NO_ADMITTED_PREDICTIVE_EDGE.**  
**Existing owners only:** Archive Task2 issue #1596, Research S7 issue #1512, Meme Alpha Lab #154 (API) and #155 (Allium), existing S1 #1156. No new research queue, forecast producer, paid data acquisition, scheduler, live indicator, model action or portfolio change.

## Sources actually queried

- Tehc API: https://tehcscreener.com/api . Public read-only daily series fetched and JSON parsed on 2026-11-10. Launchpad endpoint https://tehcscreener.com/api/v1/launchpads/series?window=all returned 1,031 days from 2024-01-14 through 2026-11-09, with **8 distinct pad series**. Bot endpoint https://tehcscreener.com/api/v1/bots?window=all&group=bot returned 1,613 days from 2022-06-11 through 2026-11-09, with **11 bot series**. Official index https://tehcscreener.com/api/v1/trench returned 1,002 daily published historical score entries from 2024-02-12 through 2026-11-09.
- Kraken public spot USD OHLC for XBTUSD, ETHUSD and SOLUSD: https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440 , etc. Each public response contained 721 daily bars, last in-progress November 10 UTC bar intentionally excluded, leaving 720 completed UTC days beginning 2024-11-20.
- Tehc /api/v1/status indicated upstream sync at 2026-11-10T08:59:58Z. Nov 9 index 36/100, COLD; original index raw component values launchpad volume $1.2475bn, new tokens 67,100, bot volume $183.55m and bot fees $1.240m.
- The vendor index described 16 tracked pads, but this exact long-window launchpad endpoint exposed only 8; population mismatch and survivorship prevent exact methodology certification. Historic daily series may have been revised by the provider after their own day labels. No historical source-retrieval timestamp, immutable original first-known, original primary Allium row hashes, as-of constituent membership or first consumer delivery attested. The original raw response bodies were NOT copied into this public repository, and the precise 2026-11-10 retrieval bytes are not reproducibly pinned; code is reproducible but an API re-query may yield different numbers. Original data licensing/provenance must be checked before durable bulk archival.
- Allium is upstream for some Tehc outputs. Comparing Tehc and Allium cannot serve as independent data corroboration. Pons V2 original on-chain events in Meme Alpha Lab remain the source-independent launch denominator.

## Offline own index recipe (source only, never model authority)

Code: scripts/research/task2_tehc_trench_backfill_v1.py  
Adversarial fixtures: tests/research/test_task2_tehc_trench_backfill_v1.py

For each completed day t with at least 365 preceding source days, sum the currently provided pad/bot series into four daily fields (USD launchpad volume, token launch count, USD bot trading volume, USD bot fees). Use ONLY dates earlier than t to create an exact trailing 90d and 365d percentile ranking. Blend each field 60% short/40% long, then weight the fields: 35% pad volume, 20% launches, 25% bot volume, 20% fees. Alternative smoothed index holds 65% of the preceding score and moves 35% toward the raw score on down-days, and jumps straight to raw score on up-days. Compute equal-weight and no-cooldown baselines. Inclusive-tie version is used only to challenge the vendor; midrank ties are a safer separate version when values are repeated. The exact site score implementation and vintage input populations are NOT verified.

| Direct computed diagnostic | Result |
|---|---:|
| Matched days after 365-day warmup | 666 |
| Pearson raw-weighted vs vendor index | 0.8825 |
| Pearson smoothed vs vendor index | 0.9125 |
| Mean absolute vendor-point error: raw | 10.16 |
| Mean absolute vendor-point error: smoothed | 6.95 |
| Mean absolute vendor-point error: equal-weight | 9.73 |
| Nov 9 actual vendor published score | 36.0 |
| Nov 9 own 8-pad/11-bot raw proxy | 29.2 |

Recent 40-day MAE was 5.93 raw versus 7.35 smoothed. Smoothing does not always improve measurement. This is correlation with a third-party *construction*, NOT predictive correlation with returns. The own index is independently computed from vendor daily aggregates, NOT yet independent from the vendor or its historical revisions. Even 0.91 correlation cannot prove economic alpha.

## Retrospective SOL/ETH/BTC spot-outcome tests

Exploratory non-PIT rule: score source day t; assume hypothetical subsequent entry benchmark at the following UTC day's close (t+1), compare the same Kraken USD close at t+4 (3 day horizon) and t+8 (7 day horizon). No fills/fees/slippage or proof the source was actually released by that next-close benchmark. This is not an implementable backtested portfolio return.

### Full own-365-warmup cohort: 658 overlapping 3-day outcome rows (source t 2025-01-13 through 2026-11-01)

| Vendor band at t | N | SOL +3d mean | SOL/BTC relative +3d mean | SOL -5% or worse +3d frequency |
|---|---:|---:|---:|---:|
| COLD, score below 40 | 220 | +0.03% | -0.07% | 20.0% |
| MID, 40-59 | 164 | -0.70% | -0.32% | 23.8% |
| HOT, score at least 60 | 274 | +0.06% | -0.13% | 17.9% |
| ALL | 658 | -0.14% | -0.16% | 20.1% |

Pearson heat vs next 3d SOL/BTC relative gain: 0.0073. Pearson heat vs next 3d absolute SOL move: -0.0497. The year 2025 versus 2026 conditioning differed. Sampling every seventh day from the same initial index left 94 rows: 30 cold, 42 hot; repeated market regimes and shared assets STILL mean these are not necessarily independent risk episodes. Null result: COLD alone does not demonstrate a 72h bounce, utility or volatility warning.

### Exploratory state transitions, a DIFFERENT 713-row vendor-history cohort

Transition study starts 2024-11-19 and includes pre-own-365 warmup vendor scores, so do NOT combine its denominator with the 658-row own-index reconstruction.
 
| Vendor state at t, compared to t-1 | N | SOL +3d mean | SOL/BTC relative mean | SOL <= -5% frequency |
|---|---:|---:|---:|---:|
| COLD and warming by at least 5 index points | 30 | -0.86% | -0.30% | 30.0% |
| COLD and cooling by at least 5 points | 54 | +0.50% | -0.43% | 14.8% |
| First crossing from below 40 to 40+ | 24 | +1.75% | +1.10% | 12.5% |
| COLD with at least a 10-point one-day increase | 8 | -1.77% | -0.06% | 37.5% |

2026-only COLD-warming 5+ had N=13 and 3-day SOL -1.53%. In a seven-day-spaced alternate subset only N=7 cold-warming examples survived and mean SOL was -3.26%. The thresholds, crossover, and outcome choice are hindsight-exposed; 24 crossing examples DO NOT establish statistically credible price-entry edge. Cold-warming can be the beginning of capitulation/bot churn, not necessarily opportunity. Preserve all negative findings.

## Actual next falsifiable experiment for Alpha Lab

**Most promising question is Launch Supply versus Qualified Demand, not SOL outright direction.**

- Independently derive total exact-chain+CA Pons origins from official first-party factory/curve events, all launches including zero liquidity, dead and never-priced; compare independent original buyer count, verified 24/72h retention, source-time LP, distribution, sellability at fixed size, real slippage after fees, and 1d/3d/7d survival; never exclude rugs and no-price.
- A Tehc-style activity prior must be contrasted with each individual public component, no-cooldown, a price-only baseline, native Pons buy/retention without external data, and an equal-weight index. Preregister thresholds before new future cohorts. Do not cherry-pick after viewing event outcomes or optimize over overlapping SOL 3-day windows.
- Separate Robinhood tokenized-stock/RWA routes, bridge/routing duplicate value and bots from meme demand; do not infer unique persons from wallets or double count multihop swap volume. Tehc is Allium-derived, so measure actual native chain/RPC agreement and provider source ages. For Kompas only optional daily 1-3d / 5-7d SHADOW attention/risk context; no authorized change to CN/Kompas direction, BTC price, or buy/sell state.
- Alternative derivatives-vs-spot context is a separate optional experiment with independent Hyperliquid builder receipts and no immediate promotion.

## Safety, provenance and owner handoff

The code intentionally runs only with six local public JSON snapshots given as CLI inputs, never makes network requests, and never schedules any run or writes canonical state. Example invocation:

    python -m scripts.research.task2_tehc_trench_backfill_v1 --pads local/pads.json --bots local/bots.json --trench local/trench.json --btc local/kraken_btc.json --eth local/kraken_eth.json --sol local/kraken_sol.json --as-of-utc 2026-11-10T12:00:00Z --ties inclusive

Synthetic adversarial test:

    python -m unittest discover -s tests/research -p test_task2_tehc_trench_backfill_v1.py -v

Only a native exact-head CI, independent owner review, qualified merge, original main readback and prospective source-clock-confirmed outcome sample could change code status. Original Pons/Alpha Lab issue #154 and public Research Lab #1512 own source and cohort acceptance; Task2 #1596 owns science; S1 #1156 owns eligible release orchestration. Private Round3 restricted data stays PROSPECTIVE_COLLECTION_ONLY with analysis OFF. If source first-known, complete population, user availability or independent N fail, keep INCONCLUSIVE/SHADOW_ONLY, never invent 14-horizon production skill or upgrade a forecast.