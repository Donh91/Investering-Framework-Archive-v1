# TechDev Counterfactual Benchmark Package v1

**Date:** 2026-07-11  
**Status:** EXECUTED / PRIORITY_COUNTERFACTUALS / NO_LIVE_ACTION  
**Parent protocol:** `01_CORE_FRAMEWORK/governance/2026-07-11__techdev-historical-outcome-scoring-protocol-v1__canonical.md`  
**Scope:** Step 2 requested by the user, macro regime, rotation, Top Gauge exit timing and exact BTC target plausibility

## Executive verdict

```yaml
macro_regime_incremental_value: PRESENT_IN_LATE_2022_EPISODE_BUT_NOT_YET_GENERALIZED
rotation_timing_edge: NOT_DEMONSTRATED
simple_first_cross_persistence: BETTER_DISCIPLINE_BUT_INSUFFICIENT
top_gauge_macro_exit_edge: NOT_DEMONSTRATED
simple_risk_exit_rules_vs_2021_top: MATERIALLY_EARLIER
exact_btc_target_edge_vs_volatility_baseline: NOT_SUPPORTED_IN_TESTED_SAMPLE
live_framework_change: WEIGHTING_CLARIFIED_NO_MARKET_ACTION
```

This package tests selected high-value claims against simple alternatives. It is not a blended TechDev accuracy score and is not exhaustive across all 257 source-backed claim rows.

## Data and no-leakage rules

- BTC daily OHLC: project Investing.com and Yahoo Finance historical archives.
- ETH daily OHLC: project Investing.com historical archive.
- ETH/BTC: daily ETH close divided by BTC close, explicitly `DERIVED`.
- 2025-2026 rotation extension: previously executed M4 and CN R&D rows, FMP settled data through 2026-07-07.
- Moving averages and volatility use only data available on the signal date.
- No later TechDev revision repairs an earlier claim.
- Taxes, fees, slippage and re-entry timing are not modeled unless stated.

## A. Macro regime versus 20W plus 200D trend

Baseline confirmation requires both:

```text
settled weekly BTC close > 20-week moving average
daily BTC close > 200-day moving average
```

The first simultaneous confirmation after the late-2022 bottoming calls was the settled week ending **2023-01-15**, BTC close **20,879.8**.

| Row | Source date | Source-backed macro position | Trend state at call | Baseline confirmation | Lead | Pre-confirmation max adverse excursion | BTC return after 180d | Baseline return to same endpoint | BTC return after 365d |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| MR-01 | 2022-12-04, Full #57 | Accumulation and upcoming major recovery | Not confirmed | 2023-01-15 | 42d | -4.6% | +59.2% | +30.5% | +145.4% |
| MR-02 | 2022-12-27, Full #60 | 15-20K bottom region and next major impulse | Not confirmed | 2023-01-15 | 19d | -2.1% | +82.4% | +45.9% | +160.1% |
| MR-03 | 2023-01-08, Market Update #2 | HTF momentum shift building toward next move up | Not confirmed | 2023-01-15 | 7d | -1.2% | +77.3% | +45.3% | +174.3% |
| MR-04 | 2023-04-11, Market Update #15 | Quicker 2023 macro path favored | Already confirmed | Same day | 0d | n/a | -7.6% | -7.6% | +122.5% |

### Macro interpretation

TechDev added genuine early scenario value in the late-2022 episode, preceding a conservative trend confirmation by 7-42 days while the remaining adverse move was small. Once both trend baselines had already confirmed, the April 2023 roadmap added no measurable regime-entry advantage.

```text
RATIFIED_USE:
TechDev macro context may raise research attention before trend confirmation.
It may not create deployment permission.
Independent framework confirmation remains required.
```

This is one major bottom episode, not proof of multi-cycle superiority.

## B. Rotation calls versus simple ETH/BTC first-cross plus persistence

Historical baseline:

```text
ETH/BTC close crosses above its trailing 100-day moving average
AND at least 3 of the current plus next 4 closes remain above it
```

| Row | TechDev source date | Ratio at call | 90d ratio return | 180d ratio return | First baseline confirmation | Delay | Initial hold above 100D | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| ROT-01 | 2023-04-11, MU #15 | 0.06256 | -1.2% | -6.5% | 2023-04-16 | 5d | 3d | Narrative was early, first cross also failed durability |
| ROT-02 | 2023-07-03, MU #24 Part 2 | 0.06278 | -1.3% | -13.4% | None within 180d | n/a | n/a | Baseline correctly withheld confirmation |
| ROT-03 | 2023-11-27, MU #34 Part 2 | 0.05443 | +10.6% | -5.6% | 2024-01-10 | 44d | 16d | Delayed relative-strength burst, not durable 180d rotation |

The 2025-2026 M4 extension independently found that:

- 4 of 5 resolved 0.0275 gate crosses died in less than 14 days, approximately 80% false positives.
- A 0.0300 hold survived 27 days and still later collapsed.
- BTC.D, breadth and stablecoin deployment were unavailable, so full rotation validation remained blocked.
- All 11 in-sample crosses with BTC below EMA50 failed, but that feature remains exploratory because it was found in the same sample.

### Rotation interpretation

Simple first-cross plus persistence is preferable to acting on a narrative expectation alone, but it does not establish durable rotation. TechDev timing and a single ratio persistence rule both remain insufficient.

```text
RATIFIED_USE:
TechDev rotation = SHADOW_ONLY.
ETH/BTC first-cross = REPAIR_MARKER.
Alt deployment still requires BTC.D, breadth, deployment and follow-through.
```

## C. Top Gauge versus simple exit rules at the 2021 peak

Top Gauge Issue #2, published 2021-11-15, reported a reading of 76 and expected the gauge to exceed 100 before the Bitcoin top. The observed cycle high had already printed on 2021-11-10 at **68,990.6**. Therefore Top Gauge did not provide a pre-peak macro exit trigger in this episode.

Counterfactuals use the 2021-11-10 high and the subsequent 2022 cycle low of **15,504.2**:

| Counterfactual | Signal date | Exit reference | Loss from peak | Additional decline to cycle low avoided | Interpretation |
|---|---:|---:|---:|---:|---|
| Hold through cycle low | n/a | 15,504.2 | -77.5% | 0.0pp | No exit protection |
| 15% close-drawdown rule | 2021-11-18 | 56,955.3 | -17.4% | 60.1pp | Earliest simple rule tested |
| Daily close below 50D MA | 2021-11-18 | 56,955.3 | -17.4% | 60.1pp | Same date as drawdown rule |
| Weekly close below 20W MA | 2021-12-05 | 49,405.5 | -28.4% | 49.1pp | Slower, still large protection |
| Top Gauge >100 | No pre-peak trigger | n/a | Not executable | n/a | Failed as terminal-top exit trigger |

This is an exit-timing comparison only. It does not model taxes, fees, re-entry or a permanent core allocation.

### Top Gauge interpretation

Top Gauge may still describe local heat, as the 2024 sequence suggested, but this benchmark does not support standalone macro-exit authority. Simple price-risk rules were materially more actionable in the 2021 episode.

## D. Exact BTC targets versus a volatility-scaled naive upper range

Baseline:

```text
publication-date BTC close
× exp(1.645 × trailing-90d daily log-return sigma × sqrt(window days))
```

This is a one-sided 95% volatility-scaled upper plausibility bound, not a full price model.

| Row | Original source-backed claim | Source confidence | Start close | Window | Naive 95% upper | Actual maximum | TechDev target floor | Target floor above naive upper | Outcome |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| PT-01 | Full #2, 233K around mid-Dec 2021 to early-Feb 2022 | Primary | 64,134.5 | 87d | 109,755.7 | 66,311.2 | 233,000 | +112.3% | NOT_SUPPORTED |
| PT-02 | Full #36, 80-120K and ATHs in H1 2023 | Conditional primary roadmap | 20,847.4 | 355d | 71,644.1 | 31,395.4 | 80,000 | +11.7% | NOT_SUPPORTED |
| PT-03 | Full #41, 160-180K by end-2023 | Close secondary scenario | 24,101.7 | 503d | 97,189.2 | 44,697.6 | 160,000 | +64.6% | NOT_SUPPORTED |

### Target interpretation

All three tested target floors were above the volatility-scaled 95% upper bound, and none were reached. The naive range was not perfect, but it was materially better calibrated to realized magnitude.

```text
RATIFIED_USE:
Exact TechDev targets remain LOW weight and CONTEXT_ONLY.
Use them as scenario imagination, never as position-sizing anchors.
Volatility-scaled ranges remain the minimum comparison baseline.
```

## Combined decision

| Lane | Counterfactual result | Final framework role |
|---|---|---|
| Macro regime | Early value in one late-2022 bottom episode | MEDIUM context, independent confirmation required |
| Rotation | Narrative timing early; simple persistence also fragile | SHADOW_ONLY, multi-gate confirmation required |
| Top Gauge | No pre-peak 2021 trigger; simple risk rules earlier | LOCAL_HEAT_ONLY, no standalone exit |
| Exact targets | Failed all three tested ranges versus naive baseline | LOW / CONTEXT_ONLY |

## Boundaries

```text
ONE_OVERALL_ACCURACY_PERCENT: FORBIDDEN
BENCHMARK_SAMPLE_EQUALS_ALL_CLAIMS: NO
CURRENT_MARKET_STATE_CHANGED: NO
REBUY_UNLOCKED: NO
ALT_ROTATION_UNLOCKED: NO
PORTFOLIO_ACTION_FROM_THIS_AUDIT: NONE
```
