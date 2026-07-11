# TechDev Wave 1 Historical Outcome Audit v1

**Date:** 2026-07-11  
**Status:** SCORED_PRIORITY_SAMPLE / CATEGORY_SEPARATED  
**Protocol:** `01_CORE_FRAMEWORK/governance/2026-07-11__techdev-historical-outcome-scoring-protocol-v1__canonical.md`  
**Cutoff:** 2026-07-11

## Actual-data anchors

- Project BTC daily historical files cover the 2021-2024 windows used below.
- The project Yahoo Finance BTC-USD archive covers later daily history through 2026.
- The 2025 BTC record high remained around 126K, below the 160K, 180K and 200K target floors.
- User-verified project actuals are used for the July 2026 low and current state.

This is a priority-selected sample. It is not an accuracy percentage for all 257 claim rows.

## Scored rows

| ID | Source and original claim | Category | Outcome | Reason |
|---|---|---|---|---|
| W1-01 | Full #2, 233K BTC and top around mid-Dec 2021 to early-Feb 2022 | PRICE + TIMING | NOT_SUPPORTED | Window high remained below 70K. Neither target nor timing was reached. |
| W1-02 | Full #5, revised 140-230K while the bull thesis remained active | PRICE_TARGET | NOT_SUPPORTED | The revised lower bound was not reached before the 2022 decline. |
| W1-03 | Full #12, 29-35K as highest-probability bottom | TERMINAL_BOTTOM | NOT_SUPPORTED | The region was visited, but BTC later reached approximately 15.5K in 2022. Range visit does not validate a terminal-bottom call. |
| W1-04 | Full #14, 170-230K around September 2022 | PRICE + TIMING | NOT_SUPPORTED | The September window and target both failed. |
| W1-05 | Full #41, approximately 160-180K in December 2023 | PRICE + TIMING | NOT_SUPPORTED | 2023 high remained below 45K. |
| W1-06 | Full #50-#52, late-2022 ending-region and next major impulse into 2023 | ROADMAP | PARTIAL | The broad bottoming and 2023 recovery direction were useful, but magnitude and several earlier timing claims were not. |
| W1-07 | Full #54/#60, FTX as possible final spring and 15-20K bottom region | BOTTOM_REGION | SUPPORTED | BTC’s final 2022 low was within the stated 15-20K region, followed by a sustained 2023 recovery. |
| W1-08 | Market Update #1, 20W/HTF reclaim as correction-ending confirmation | STATE_GATE | SUPPORTED | BTC reclaimed major trend levels during the January 2023 reversal and did not return to the 2022 low. |
| W1-09 | Market Update #15, quicker path and 2023 top favored | ROADMAP + TIMING | PARTIAL | Direction was bullish, but the implied high-degree completion and magnitude in 2023 were not delivered. |
| W1-10 | Market Update #42, first top May-Sep 2024 and second top Mar-Jul 2025 | ROADMAP_SEQUENCE | PARTIAL | A major March 2024 local high and later higher 2025 high fit the broad two-stage idea, but the first stated window and subwave detail were imprecise. |
| W1-11 | Topping Signals #5-#7, Top Gauge possibly triggered then called triggered in March 2024 | TOPPING_SIGNAL | PARTIAL | It identified local heat near the March high, but was not a macro top. The later “uncertain” reclassification confirms trigger fragility. |
| W1-12 | Topping Signals #1-#8, Tether RSI, BB width and Pi Cross remained not triggered | MECHANICAL_SIGNAL | SUPPORTED_AS_NO_TRIGGER | The mechanical system avoided falsely declaring those three thresholds hit. This is not proof of exit superiority. |
| W1-13 | Market Update #49, July 2024 cycle far from over | BROAD_DIRECTION | SUPPORTED | BTC later made materially higher highs. The exact analog and 48-53K bottom map are separate claims. |
| W1-14 | Market Update #54, mid-October 2024 breakout expected | TIMING_WINDOW | SUPPORTED | The Q4 2024 breakout and move through prior highs followed close to the stated window. |
| W1-15 | Market Update #64, 160-180K Q1/Q2 2025 with April emphasis | PRICE + TIMING | NOT_SUPPORTED | The target floor was not reached in the declared period. |
| W1-16 | Market Update #71, 160-180K around August/September 2025 | PRICE + TIMING | NOT_SUPPORTED | BTC made a new high near 126K, materially below 160K. |
| W1-17 | Market Update #72, 160-180K during 2025 | PRICE_TARGET | NOT_SUPPORTED | The full 2025 window matured below the target floor. The separate >250K 2026 claim remains open. |
| W1-18 | Market Update #74, 180-200K in 2025 and approximately 300K in 2026 | PRICE_TARGET | 2025 NOT_SUPPORTED / 2026 OPEN | The 2025 leg failed. The full 2026 window has not matured. |
| W1-19 | Market Update #80, trunk-up recalibration and slower business-cycle timeline | MODEL_REVISION | OPEN / NOT_SCOREABLE_AS_PRIOR_SUCCESS | This is a new model and exit-policy revision. It cannot repair the expired 2025 targets. |
| W1-20 | Market Update #90, 52-57K final leg expected to begin in publication week | PRICE + TIMING | PARTIAL | The move lower developed much later. User-verified July low near 57.8K was close to, but above, the zone. Timing failed; region was a near miss. |
| W1-21 | Market Update #90 BITI and ETHD entries, stops and targets | TRADE | NOT_EVALUABLE_IN_WAVE_1 | Original setups are source-backed, but complete independently verified adjusted ETF paths and execution assumptions are not yet frozen. |
| W1-22 | Repeated 2023-2025 ETH/BTC and BTC.D altseason windows | ROTATION_TIMING | NOT_SUPPORTED_ON_TIMING | Repeated “imminent” windows did not produce the durable broad rotation implied. The long-run directional thesis remains a separate open concept. |
| W1-23 | Author-reported RSI/MACD and later dot/trackline backtests | MECHANICAL_SYSTEM | NOT_EVALUABLE | Rules changed after publication and independent reproduction has not been completed. |
| W1-24 | Global liquidity and business cycle as explanatory drivers | MODEL_DEFINITION | NOT_EVALUABLE_AS_CAUSAL_ACCURACY | Several directional calls were useful, but the corpus alone cannot establish causal or independent predictive edge over simpler trend and liquidity baselines. |

## Category summary

```yaml
mature_supported: 5
mature_partial: 5
mature_not_supported: 8
not_evaluable: 3
open_or_mixed_open: 3
```

Counts are row labels in this priority sample, not a blended accuracy score.

## What the outcomes show

### Stronger evidence

- Broad regime direction improved materially around the late-2022 bottom and 2023 recovery.
- The July 2024 “cycle far from over” view was directionally useful.
- The September 2024 breakout window was one of the cleaner timing successes.
- The non-Top-Gauge mechanical topping indicators did not falsely trigger during the 2024 monitoring sequence.

### Weaker evidence

- Exact BTC top targets were repeatedly too high.
- Exact timing windows were repeatedly extended.
- The 2021-2022 one-more-impulse thesis remained alive through several support failures and model changes.
- Altseason and rotation timing was repeatedly early.
- Top Gauge behaved more like a local heat indicator than a standalone macro-exit signal.
- Mechanical trading claims are not promotion-ready without independent reproduction under frozen rules.

## Decision boundary

This audit supports keeping TechDev as a macro and roadmap input. It does not support standalone execution authority, exact-timing authority or automatic rotation permission.
