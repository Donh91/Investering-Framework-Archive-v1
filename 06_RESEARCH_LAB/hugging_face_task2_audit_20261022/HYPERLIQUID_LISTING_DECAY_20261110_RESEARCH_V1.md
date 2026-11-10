# Hyperliquid new-listing decay: independent audit and falsification study v1
**Owner:** existing Task 2 #1596 / Ironflow source program #1747, derivatives #387. Cross-domain beneficiary: Meme Alpha Lab #22, its existing Spot/Perp Flow Divergence benchmark. **2026-11-10.**
**Status:** `RESEARCH_ONLY / SHADOW / AGGREGATE_CLAIMS_CHECKED / EMPIRICAL_18M_REPLAY_REQUESTED_ON_THIS_PR`.
**Authoritative truth:** native PR exact-head CI and attached bounded artifact after it exists. No current market prediction, Alpha score, investment advice or live trading authority.

## Executive finding
0xArchive's X post (9 Nov 2026) claims 95/116 Hyperliquid listings declined by day 30, 37/40 most recent declined, median return -33.8% versus -15.7% on older coins, and a 5%-of-equity-per-short / 30-day exit / no-stop strategy yielded +74.6% in 44 trades, 84% winners, 17.6% max drawdown after fees and funding during Mar 2025-Jun 2026. These are **publisher claims, not independently reconciled trade rows**. Their public `0xArchiveIO/0xarchive-quant` Rust backtester exists, but the claimed individual 44 trade paths and immutable study receipt were not identified in the accessible public repository. No adoption of reported return as framework skill.

## Executed numerical checks (derived exclusively from the claims)
- All listed observations: 95/116 = **81.90%** falling, Wilson 95% CI **73.90%-87.84%**.
- Recent: 37/40 = **92.50%**, Wilson 95% CI **80.14%-97.42%**.
- Prior 76 implied by nested cohort: (95-37)/(116-40) = 58/76 = **76.32%**, Wilson 95% CI **65.64%-84.46%**.
- Recent minus prior fall frequency **+16.18 percentage points**. Fisher exact 2-sided **p=0.04147**, odds ratio **3.8276**. This simple row-independent test is *NOT valid independent evidence* if listings share regime and were selected with hindsight; multiple testing, clustering, token-market selection and publisher data unavailable.
- Reported 84% of 44 is compatible with 37/44 = 84.09%, Wilson 95% CI **70.63%-92.07%**, but wins are not IID; cannot derive expectancy from win rate.
- Arithmetic sanity illustration ONLY: `44 * 0.05 * 0.338 = 0.7436`, close to 74.6%, but this multiplies an **overall median** from a different population by trade count, ignores overlapping positions, winners/losers, compounding, fees, execution and funding. It is not a portfolio PnL reconciliation and cannot substantiate 74.6%.
- Unstopped isolated 5%-notional short if spot-price multiplies by 2/3/6/21 has approximately -5/-10/-25/-100 percentage points initial-account PnL before margin, liquidation and fees. 5% **allocation** is not a capped-loss risk budget; correlations and concurrent shorts matter.

## Independent contradictory / disconfirming evidence
Coincise's free listing register says its prior **2026-09-02 matched-control test could not distinguish a listing-specific component from zero, with one market dominating aggregate**. It correctly says its published first-trade-to-today returns use unequal windows and are not first-30-day returns, therefore **cannot refute this 30-day claim**. Its methodology notes 45 of its first 46 snapshot-detected listings had zero trades at first sighting, so market listing/seed mark must not be mistaken for an executable first trade. Source: https://coincise.co/hyperliquid/listings and https://coincise.co/methodology. Review status: independent, not reproduced.

## Research hypothesis hierarchy and falsifiers
1. **H-DECAY-1: 30-day new-perp underperformance.** Compare exact same-UTC-clock 30d *price* return against contemporaneous older-market controls; pair same-token prelisting spot move where available. Falsify listing-specific claim if matched median new-minus-control CI includes zero or deteriorates materially across data/entry variants. A descriptive fall frequency alone does not prove tradeable short alpha.
2. **H-DECAY-2: prelisting pump / token-age effect, not listing causation.** Distinguish underlying token genesis, new perp market genesis, and quote/seed mark. Match event-entry momentum, 24h volatility, traded notional, broad BTC/ETH regime and sector. Exclude lookahead and same-symbol false joins; probe 1/3/7/14/30d decay. A market listing is not always original token creation.
3. **H-DECAY-3: early listing spike -> exhaustion -> dip survival.** Do not automatically reject exceptional future winners. Measure false-negative penalty, MFE/MAE, first-dip reclaim, organic buyer/LP persistence, post-dip continuation and eventual 90d survival. A lower median can conceal a positively skewed moonshot tail.
4. **H-DECAY-4: pure beta and momentum selection.** Test equal-weight core-alt short; age/market-cap/vol/momentum-matched placebo entrants; non-overlapping monthly blocks; opposite-direction and shifted entry clocks (0/+1/+3/+7 days); funding cost and turnover/slippage. A profitable bear-regime short is not a unique listing edge.
5. **H-DECAY-5: independent benefit of spot/perp/OI/funding.** Reuse existing Alpha Lab `research/benchmarks/SPOT_PERP_FLOW_DIVERGENCE_V1/README.md`, no duplicate leverage engine. Add derivatives only if they improve matched baseline and survive out-of-sample.

## Implemented first-pass engine and tests in this PR
- `scripts/research/hyperliquid_listing_decay_v1.py` accepts already-pinned Ironflow hourly Parquet. It studies core perps only, excludes HIP-3/spot, records every first-observed-trade proxy after a 45-day left-censor buffer, and uses a UTC entry at first trade hour after the daily close following that first traded calendar day (clock anchor = listing day + 2d, **not 0xArchive exact fill reproduction**).
- Uses original observed candle open at entry and at +1/+3/+7/+14/+30 days, never filled future candle close or a mark on zero-volume seeds.
- An asset without executable +30d exit remains in denominator as `NO_EXECUTABLE_30D_EXIT`; intermediate observable horizons remain reported.
- Controls are 60d+ observed core perps matched on observable 24h momentum, realised variation and trade notional **at entry time**. Critically future control exit existence is NOT a selection criterion: selected delisted controls become `CONTROL_EXIT_CENSORED`. This is a heuristic developmental matcher, not a causal identification design.
- Captures short MAE/MFE, paired excess return, entry-delay sensitivity 0/+1/+3/+7d, 20bps round-trip fee/slippage assumption and 40bps stress. **Hourly funding, delisting settlement, margin liquidation and dynamic book PnL are intentionally NOT computed**, so the output MUST NOT be labeled after-funding portfolio performance.
- Requires consecutive monthly input, no duplicated market-hour, valid positive OHLCV, source member SHA-256; rejects bad input rather than manufacture periods.
- Synthetic regression tests cover clocks, 30d maturity, censoring, control selection independent of future survival, cost sensitivity, and month gaps. Native CI must provide exact-HEAD validation; local synthetic-only test is not historical edge evidence.

## Data authority and limitations
Source dataset: `ironflow/hyperliquid-candles-1h`, pinned existing owner SHA `9f262cc27d89112b8c56550cf4c9455346f5eece`, files May 2025-Oct 2026, licensed CC BY 4.0, credit **Ironflow (ironflow.sh)**. Existing owner `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/SOURCE_MANIFEST_IRONFLOW_20261106.json`; existing native Action `ironflow-task2-source-pilot.yml` has already demonstrated source downloads and a 72-file run. Its prior 18m model comparison showed **no confirmed incremental derivative feature edge**, a separate question that must not be rewritten by this study. This study cannot reproduce 0xArchive's March-May 2025 records before Ironflow starts May 25 2025; it will not pretend to reconstruct 116 historical original exchange listings or the 44-trade PnL.

The latest 18-month Ironflow source is a dataset **published November 2026**. All May 2025-Oct 2026 trade observations are retrospective *research development*, never prospective original-market observation or live advance warning. Round 3 private experimental analysis remains OFF; this study accesses public Ironflow data only. Keep raw public-monthly parquet off Git and keep all outputs as short-lived read-only GitHub Actions artifacts, not durable custody.

## Exact native CI research request
Reuse the **existing** `full18m-history-walkforward` job; no new workflow, schedule, owner, identity, secret, writer or subscription. First run unit fixtures, then use already downloaded/pinned `/tmp/ironflow18/candles` for three experiments:
1. original synthetic-validated 30d cohort with exact entry baseline and 20 bps illustrative round-trip friction;
2. same entrants with 7-day entry delay;
3. same entrants with 40 bps illustrative friction.
Write raw aggregate/row-level **public-source-only** JSON inside existing short-lived Actions artifact; no raw parquet mirroring. Result is acceptable as completed descriptive research only if native source-hash binding, SHA, all tests, cohort accounting, censor counts, same-clock controls and endpoint coverage are verified. Otherwise **EVIDENCE_INCOMPLETE**, not `PASSED`.

## Claude / Grok / S1 handoff without duplicate authority
- **Claude (independent adversarial reviewer):** audit clock semantics, future selection, match definition, delist settlement, same-period control availability and whether low-volume tokens actually have executable +30d open. Demand exact cohort and 44 trade ledger from 0xArchive before accepting their ROI; record `APPROVE/CHANGES/INSUFFICIENT` with exact HEAD.
- **Grok Bridge:** independently challenge 0xArchive listing-date source, 116 denominator, survivorship/market-beta null, sample selection and Coincise discrepancy; propose same-time placebo basket and falsification thresholds. Report to existing Bridge, no additional research PR factory.
- **S1:** keep original scientific domain owner #1596 / #1747 and Alpha Lab #22. Use native exact-HEAD CI, review and branch/custody release gates, merge only when ready. Do not route this shadow study to production, automated trading or weekly Compass.
- **Alpha Lab:** prospective 1/3/7/14/30d maturity ledger, FNP on rejected high-tail survivors, listing vs token genesis distinction; no watch-score promotion until truly prospective frozen performance exceeds simple baselines.
