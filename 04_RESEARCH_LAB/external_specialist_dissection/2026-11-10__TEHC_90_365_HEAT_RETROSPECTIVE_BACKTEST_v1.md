# S7 x Task2 | Tehc heat 90/365, offline historic reconstruction and empirical null

Research date: 2026-11-10.
Status: RETROSPECTIVE_REPLICATION_POSITIVE, PREDICTIVE_SKILL_UNPROVEN, ORIGINAL_PIT_UNATTESTED.
Owners: existing [Meme Alpha Lab #154](https://github.com/Donh91/Meme-Alpha-Lab/issues/154), [Archive S7 #1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512) and [Task 2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596).
This is one owner-approved method study, not a new engine, cron, trading authority or public Kompas score.

## A. Exact sources actually read, without signup

Official documentation: https://tehcscreener.com/api . The live public API was queried on 2026-11-10; the responses were valid JSON. Source data are credited to TehcScreener (powered by Allium); upstream raw Allium, source first-known historical dates and release/vintage history are NOT attested. No original source bulk data has been copied to this public repo, and no GitHub native source HTTP-header/byte-hash receipt was saved in this turn.

| Actual read-only URL | Observed original response coverage |
|---|---|
| https://tehcscreener.com/api/v1/launchpads/series?window=all | 1,031 daily days, 2024-01-14..2026-11-09, 8 listed pads |
| https://tehcscreener.com/api/v1/bots?window=all&group=bot | 1,613 daily days, 2022-06-11..2026-11-09, 11 bots |
| https://tehcscreener.com/api/v1/trench | 1,002 historic published score-days, 2024-02-12..2026-11-09 |
| https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440 | 721 daily candles, 2024-11-20..2026-11-10; LAST PARTIAL CANDLE EXCLUDED |
| https://api.kraken.com/0/public/OHLC?pair=SOLUSD&interval=1440 | 721 daily candles, identical day scope; LAST PARTIAL CANDLE EXCLUDED |
| https://api.kraken.com/0/public/OHLC?pair=ETHUSD&interval=1440 | 721 daily candles, inspected for crosscheck, not part of outcome calculation |

Tehc latest /status synced_at=2026-11-10 08:59:58 UTC; daily through=2026-11-09. Public source docs: no API key, 120 requests/min/IP, reuse of statistics/charts requires credit; the vendor's upstream source rights and retroactive changes are NOT certified. Kraken original docs explicitly state current final OHLC candle is unfinished: https://docs.kraken.com/api-reference/market-data/get-ohlc-data . Data were gathered by read-only interactive tool calls, NOT any recurring capture.

## B. Reconstruct 90/365 without website dependence

Using listed launchpads and bots on each calendar day, aggregate daily pad USD volume, launch token counts, bot USD volume and bot USD fees. For day t, rank each against ONLY earlier trailing 90 days and earlier trailing 365 days, inclusive tie policy. A fixed 60/40 blend of the two percentiles, then published component weights 35/20/25/20, yields our UNSMOOTHED heat. Compare to simple equal-weight baseline. Independently test cooldown on declines with fixed factor 0.65 (on decreases previous smoothed x 0.65 + raw x 0.35; rises immediate). This is a clear versioned candidate method, NOT an exact byte-equivalent replication of Tehc's partially undocumented tie/coverage rules.

Require 30 prior complete days; reject missing source data/gaps, no zero-filling. The vendor supplies a historic 1002-day indexed tape but does not prove every historic value and component was actually publicly published at the event date. Both vendor and our replay are RETROSPECTIVE, not eligible original PIT feature tapes, regardless of using only past dates within the reconstructed history.

Market comparison uses Kraken BTC/USD and SOL/USD closed daily candles. Activity day t is considered only at hypothetical NEXT full daily close t+1, then prospective-on-paper outcomes measured at t+4 (3-day hold) or t+8 (7-day hold). This intentionally avoids using same-day price or the unfinished last Kraken daily candle. It does NOT prove the vendor data were delivered by t+1 historically. No trade, fills, slippage or net PnL claim.

## C. Actual historical calculations on original JSON

- Shared daily aggregation: 1,031 days.
- 1,001 historic days could be aligned between our calculated composite after warmup and the publisher's historic scores.
- UNSMOOTHED 4-factor heat vs published vendor index: mean absolute deviation 7.958 score points.
- WITH fixed downside cooldown: mean absolute deviation 4.754 points; Pearson correlation +0.948.
- 2026-11-09 vendor latest score 36, internal raw 29.17, internal cooled 29.17: source coverage, tie, initial/smoothing, historical vintages and differences remain, so no dishonest exact 36/100 recreation.

The independent calculation **approximately reproduces the direction/pattern of the index**. This is NOT evidence of economic value or independent primary raw source provenance.

### Basic descriptive 3-day market backtest, still NOT PIT

Interactive historical market replay produced 713 overlapping 3-day windows from 2024-11-19 to 2026-11-01. The fully fail-closed offline CLI also requires seven complete preceding 1d price observations for the price-only baseline, so it may skip the earliest 2024 windows; 2025 and 2026 yearly figures are unchanged.

| Predefined comparison | 2025 (365 overlapping days) | 2026 (305, through Nov 01) |
|---|---:|---:|
| Vendor heat vs future 3d SOL/BTC relative log return, Pearson r | -0.040 | +0.049 |
| Our UNSMOOTHED heat vs future 3d SOL/BTC relative log return | -0.014 | +0.012 |
| Vendor heat vs absolute future 3d SOL log return | -0.025 | +0.006 |
| Simple 7-prior-daily-return SOL volatility vs same future absolute log return | +0.062 | +0.199 |
| Days vendor heat cold (<40) | 139 | 81 |
| Days vendor heat hot (>=60) | 126 | 160 |

A sensitivity subset of every seventh 2026 day Jan 01..Oct 31 leaves just 44 approximately non-overlapping 7-day outcome windows (11 cold, 25 hot). Even those are not independent regimes, not inferential confidence intervals. Many of the apparent 305 examples share future days.

Scientific verdict: market-wide directional/realized-volatility incremental edge for these factors is NOT demonstrated. In particular the vendor-relative-return sign flips between years, and price-only volatility looks at least as informative for realized movement. Do not tune or deploy a market model from this post-hoc historical tape. This is not proof Alpha Lab token-quality usefulness is absent.

## D. Better hypothesis: Alpha Lab FIRST-PARTY launch supply vs buyer quality

Reuse existing S4 native Pons V2 CurveBuy/CurveSell, full first-seen token mint denominator, first buyer qualification, wash/sybil controls, observed liquidity, and realistically sellable 1/3/7-day exits, plus S7 attention chronology. Proposed falsifier: more daily launches without proportionate independent buyer retention forecasts worse launch-survival or executable outcomes after age/liq/regime controls. Include all dead tokens, not only vendor top-50 activity-ranked tokens. Do not equate higher fees or bot volume with positive organic buyer capital. Tehc/Allium are the same source family, NOT two independent source votes.

A second candidate is Robinhood RWA-pool versus genuine meme token flow; RWA volume is pool-hop inclusive, do not simply subtract from chain total. Optional perp spot divergence is medium priority but original Ironflow derivatives incremental null remains a stop warning. No speculative features added to official Kompas.

## E. Repo paths, repeat and stop gates

New STD-LIB-only script:
- scripts/research/s7_tehc_heat_retrospective_v1.py
- tests/research/test_s7_tehc_heat_retrospective_v1.py

Offline rerun using five authorized locally downloaded JSON files, with no network call made by the script:

    python -m scripts.research.s7_tehc_heat_retrospective_v1 \
      --pads /tmp/tehc_pads_all.json \
      --bots /tmp/tehc_bots_all.json \
      --vendor /tmp/tehc_trench.json \
      --btc /tmp/kraken_xbtusd_1440.json \
      --sol /tmp/kraken_solusd_1440.json > /tmp/tehc_research.json

    python -m unittest tests.research.test_s7_tehc_heat_retrospective_v1 -v

The script prints input SHA-256s to make that rerun independently inspectable. Do not use a post-hoc edited external data payload as original PIT truth.

**Decision:** Archive S7 adopt METHOD_ONLY, MAL #154 investigate a single sealed prospective all-mint Pons cohort, Task2 #1596 keep as non-authoritative shadow challenger, Kompas official 1–3d NO NEW WEIGHT. If independent first-known and outcome denominator cannot be established, mark INCONCLUSIVE and retain negative result. If price-only or native Pons baseline is not beaten out-of-cohort, STOP. No new paid API, GitHub workflow, cron, identity, trade or new supervisor. Merge/release remains with existing original owners and native CI/reviewer/main-readback.
