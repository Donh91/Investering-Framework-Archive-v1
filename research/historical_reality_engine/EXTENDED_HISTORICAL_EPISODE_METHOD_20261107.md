# HRE Phase R2: five expanded historical regimes, fixed preselected cases

**Owner:** Task2 #1596. **Original base study:** PR #2010, native Action run 42390995602, source-safe scientific receipt `NATIVE_FIRST_RESULTS_EVIDENCE_20261107.json`.

## Research question

Do simple price-reactive risk warnings fail in qualitatively different risk events and matched non-event periods, and can source-legal observations across each historical period define more convincing forward research hypotheses without using crisis outcomes or revised information as features?

This study adds **preselected case windows** to the existing public Binance SPOT BTCUSDT and ETHUSDT monthly 1h baseline implementation. All ZIPs and their provider CHECKSUM files are fetched on the native GitHub runner. The source class is still POSTHOC_PRICE_TRUTH_TAPE_NOT_ORIGINAL_PROVIDER_FIRST_KNOWN. This is not native 2022/2023/2024/2026 Kompas publication, nor original news/ETF/macro knowledge.

### Preselected episodes before outcome score computation

| ID | UTC source months | Anchor UTC | Hypothesis only |
| --- | --- | --- | --- |
| terra_2022 | Apr-Jun 2022 | 2022-05-08 00:00 | Gradual deterioration versus external sudden peg failure |
| ftx_2022 | Oct-Dec 2022 | 2022-11-06 00:00 | Counterparty/news shock versus observable earlier market weakness |
| usdc_2023 | Feb-Apr 2023 | 2023-03-10 00:00 | Stablecoin depeg contagion versus stress/rebound false alarms |
| aug_2024 | Jul-Sep 2024 | 2024-08-05 00:00 | Fast macro/volatility shock versus prolonged trend weakness |
| feb_2026 | Jan-Mar 2026 | 2026-02-12 00:00 | Source gap and downside risk under 2026 market regime |

Each native episode reports valid daily UTC cutoffs, 72h future severe-low outcomes, simple price-only baseline and simple price-only alternative confusion counts; also the seven pre-anchor daily cutoffs, if source/time eligible, as **descriptive audit**. Event anchors are retrospectively named case-study dates; labeling a pre-anchor risk flag does not establish prior independent crisis forecasting.

### Provenance and no hindsight

- Use only fully closed hourly bars. **Do not use the vendor's raw intrabar last-trade close field to infer bar finalization.** Full UTC nominal hour is mandatory.
- A missing source hour in ANY input lookback or outcome horizon invalidates the affected daily cutoff. No interpolation; report missing/abstained populations.
- Source file SHA-256 and current hosted checksum are verified. Archived ZIP may have appeared or been revised years after the event, and cannot be credited as original provider-time release without separate evidence.
- Retain full positive/false-positive/missed/quiet denominator and overlapping 72h label caveat.
- No post-event UST, FTX, USDC, ETF or macro narrative can become a pre-event feature unless period-legal source first-known is proven; this price-only control does not use these features at all.
- A price-only warning crossing 8% threshold is not a 4/5 production Pullback Risk class or SELL instruction.
- Cross-event results must be aggregated by independent episode family (at most five here) instead of treating hundreds of overlapping daily cutoffs as independent statistical observations.
- This pilot is exploratory and after-event-selected, so never represent a positive pattern as prospective validated edge. Later freeze out-of-time holdouts and test cost-adjusted utility.

## Parallel runtime

Two **genuinely separate GitHub Actions** jobs are added to the existing PR-only Research Parallel Lanes Skill Contract CI, selected by title prefix `research(hre2):`: one 2022 Terra/FTX and one 2023/2024/2026 case, no new workflow, cron, secret, GitHub identity, Grok Routine or paid API. Existing R1 research jobs are not needlessly rerun.

Success only when native Action job IDs and SHA-256 source-bound artifacts exist. These are time-limited artifacts; create compact durable owner research evidence after verified execution, not before. If one independent job fails, other job may succeed, but full R2 cannot be called PASS. Source HTTP failure or missing history is a scientific/data blocker, not license to fill bars or force an outcome.

## Next gate beyond this exploratory control

Original currently versioned native Kompas/CN rule replay requires realistic feature family availability at each historic cutoff, current archived model version and original first-known where applicable. No native model-era forecasting skill is implied by this price-only code. Broader macro/news/stablecoin/ETHBTC data must pass T1 and then period PIT before economic claims. Owner #1596 coordinates, #1516 weekly, #1553 risk, #1918 rotation, S1 #1156 for actual qualified original PR closure.

No automatic scientific model/risk promotion, no live trades, no auto MAX billing. External Grok review can be requested against immutable source/run receipts after a successful native run.
