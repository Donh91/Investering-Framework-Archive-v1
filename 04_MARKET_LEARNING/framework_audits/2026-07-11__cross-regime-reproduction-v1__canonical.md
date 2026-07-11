# Cross-Regime Reproduction — Methodology and Results

**Date:** 2026-07-11  
**Datasets:** `btc spliced.csv`, `btc regime.csv`, `altcoin phase.csv`  
**Status:** INDEPENDENT GPT REPRODUCTION

## A. DUMB_1.5 versus DUMB_2.0

- Weekly window: Monday through Sunday.
- Start: 2013-01-07.
- Last full week: 2026-06-22 through 2026-06-28.
- Eligible weeks: 702.
- Anchor: prior Sunday close.
- ATR: Wilder ATR14 using daily true range: `max(high-low, abs(high-prev_close), abs(low-prev_close))`.
- Forecast bands:
  - DUMB_1.5 = anchor ± 1.5×ATR14
  - DUMB_2.0 = anchor ± 2.0×ATR14
- Actual interval: weekly intraday low/high.
- Primary score: interval Winkler, alpha 0.10, normalized by anchor close.

| Segment | n | 1.5 wins | 2.0 wins | Median 1.5 | Median 2.0 |
|---|---:|---:|---:|---:|---:|
| All | 702 | 34.3% | 65.7% | 58.70 | 34.22 |
| 2013–2016 | 207 | 37.7% | 62.3% | 71.19 | 43.19 |
| 2017–2020 | 209 | 34.4% | 65.6% | 76.37 | 40.62 |
| 2021–2024 | 209 | 31.1% | 68.9% | 52.86 | 26.08 |
| 2025–2026 | 77 | 33.8% | 66.2% | 35.03 | 18.37 |

Verdict: **REPRODUCED**. This does not by itself change FRLP B3. Forward rows remain the binding experiment.

## B. Regime labels and seven-day drawdown risk

- Sample: 2013-01-02 through the last row with seven future closes.
- n = 4,921.
- Event: minimum settled close during the next seven days is at least 8% below the current close.
- Label: supplied walk-forward regime label.

| Regime | n | Probability |
|---|---:|---:|
| Downtrend | 1,504 | 18.2% |
| Transition | 950 | 21.6% |
| Uptrend | 2,467 | 18.0% |

Verdict: **SUBSTANTIVE CONCLUSION REPRODUCED; EXACT EQUALITY NOT REPRODUCED**. Uptrend and Downtrend are almost identical; Transition is modestly higher. Regime labels remain weak forward-risk discriminators and should be descriptive, not predictive.

## C. Defensive regime filter / insurance claim

Strategy:
- invested when the previous day's `regime_wf` is Uptrend or Transition
- cash when previous day's state is Downtrend
- no fees or cash yield

2013-01-01 to 2026-07-02:
- Buy-and-hold terminal multiple: 4,554.37×
- Strategy terminal multiple: 1,072.93×
- Relative return shortfall: 76.4%
- Buy-and-hold max drawdown: 90.98%
- Strategy max drawdown: 90.99%
- Drawdown improvement: approximately 0 percentage points

2023-01-01 to 2026-07-02:
- Buy-and-hold terminal multiple: 3.718×
- Strategy terminal multiple: 2.845×
- Relative return shortfall: 23.5%
- Buy-and-hold max drawdown: 53.08%
- Strategy max drawdown: 37.48%
- Drawdown improvement: 15.59 percentage points

Verdict: **REPRODUCED**. Defensive value is cycle-dependent, not an unconditional system property.

## D. Alt-phase labels and forward ETH/BTC

- n = 1,213 rows with a complete 30-day forward window.
- Forward return: ETH/BTC close at t+30 divided by current close minus one.

| Label | n | Median forward 30d | Positive rate |
|---|---:|---:|---:|
| ALT_SEASON | 198 | -4.22% | 31.3% |
| BTC_SEASON | 702 | -2.22% | 39.3% |
| NEUTRAL | 313 | -5.15% | 29.4% |

Verdict: **REPRODUCED FOR THE SUPPLIED LABELS**. This does not falsify the concept of altseason; it falsifies directional use of this supplied label definition without further definition audit.

## E. Not independently reproduced

- Exact fixed-gate drift claim `40%↔112%` because the reference-level definition was not included in the row exports.
- TechDev #89–95 stance because source pages were image-only in the Fable run.
- BTC regime generator parameters beyond using the supplied walk-forward labels.

These remain calibration findings, not binding rules.
