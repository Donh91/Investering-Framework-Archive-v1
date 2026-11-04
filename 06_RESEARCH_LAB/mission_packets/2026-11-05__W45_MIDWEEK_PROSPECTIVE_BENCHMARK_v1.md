# W45 midweek forecast bridge, provenance audit & 4-day research pilot
Created 5 November 2026, 00:29 Europe/Copenhagen (4 November 23:29 UTC). Owner initiated in SITE thread.

**Status: RESEARCH-ONLY**, not an original Monday CN forecast, new market publisher,
site authority, Portfolio BUY/SELL, statistical edge, or retroactive forecast.

## 1. Monday input versus actual issuance, the main finding
W44 was available in the original Monday 2 November evidence with 168/168
hourly observations. The W45 *original* CN #32 freeze and its unmodified
SHA-256 `e933a2c8a08669a7acbe1542c24b1fddd4a5f7852131d83f2b98369834ac1be1` contain:
* BTC original whole-week envelope `72,000–84,000`, ETH `2,000–2,500`.
* Original three forecast windows:
  BTC day 1–2 `75,000–81,500`, day 3–4 `73,500–82,500`, day 5–7 `72,000–84,000`;
  ETH day 1–2 `2,120–2,380`, day 3–4 `2,050–2,440`, day 5–7 `2,000–2,500`.
* **No original seven daily expected-close points for BTC or ETH** and
  **no original seven individual daily low/high range plans**. Each 0/7.
* The original weekly envelope did not record verified quote parity
  (original quote `UNAVAILABLE`), regardless of its dollar-sign presentation.
* An existing one-shot **Monday 2 Nov 10:10 UTC** supplemental Sol call
  also returned 0/7 on both assets; cost receipt `$0.00604`.
* Do not silently elevate the three 2/2/3-day bands to seven day-specific
  predictions, or replace the original Monday freeze after outcomes.

**Assessment:** evidence completeness for W44 does not guarantee a scientifically
defensible daily *timing* path. Conversely, 0/7 is a real PRODUCT shortfall,
separate from valid source abstention. #1879 repaired structural source
admission, #1902 now flags that product shortfall prospectively.

## 2. Actual new research from source-locked W45 spot hours
Immutable research input snapshot is the adjacent JSON packet. The sample was
read only from original GitHub `03_DAILY_CAPTURE_LOGS/hourly` at main
`aa4885aa7d42a85d297a347dcd73708129cdfb89` and retains the exact
10 upstream file Git blob SHAs.

* Completed W44 168 contiguous PASS spot candles + 70 contiguous PASS
  W45 candles = 238 observed hours, **237 overlapping hourly returns**.
* Most recent bar ended `2026-11-04T22:00:00Z`; source BTCUSDT `80,240.18`
  and ETHUSDT `2,418.34`, quote-native **USDT**.
* The source's `timestamp_utc` denotes the candle-open clock; bar close
  is `timestamp_utc + 1h`. `source_window_end_utc` can be later,
  reflecting the capture batch. These clocks are **not interchangeable**.
  All captured source windows precede this research issue.
* Provider-first-known timestamps are not independently proven by the
  research packet; **PIT/edge admission remains false**.

## 3. What can be forecast prospectively this week
A new, **separately issued midweek research experiment** was frozen
4 Nov `23:29:12Z` for full prospective UTC days **Thursday 5 Nov
through Sunday 8 Nov**. Monday–Wednesday are already observed or partly
observed and cannot be transformed into original Monday predictions.

B0 is the neutral last-known-price persistence baseline. B1 is an uncalibrated
short-momentum challenger:
`forecast = anchor × exp(sum(clamp(0.35 × ln(anchor/prior24h) × 0.6^j, −0.02, +0.02), j=0..k−1))`.
For each k-day forward target an *illustrative terminal-close dispersion*
uses `anchor × exp(±1.5 × sample_sd(hourly log returns) × sqrt(24k))`.
This is **not** a predictive coverage probability, not a daily intraperiod
high/low forecast and not an original Monday range.

### BTC / USDT, research-only expected UTC daily closes
| Day | UTC date | B0, neutral | B1, decayed momentum | Heuristic terminal-close dispersion |
|---|---|---:|---:|---:|
| 4 | Thu 5 Nov | 80,240.18 | 81,074.83 | 77,964.35–82,582.44 |
| 5 | Fri 6 Nov | 80,240.18 | 81,579.78 | 77,040.68–83,572.55 |
| 6 | Sat 7 Nov | 80,240.18 | 81,884.25 | 76,339.36–84,340.33 |
| 7 | Sun 8 Nov | 80,240.18 | 82,067.49 | 75,753.07–84,993.08 |

### ETH / USDT, research-only expected UTC daily closes
| Day | UTC date | B0, neutral | B1, decayed momentum | Heuristic terminal-close dispersion |
|---|---|---:|---:|---:|
| 4 | Thu 5 Nov | 2,418.34 | 2,463.18 | 2,328.60–2,511.54 |
| 5 | Fri 6 Nov | 2,418.34 | 2,490.48 | 2,292.41–2,551.19 |
| 6 | Sat 7 Nov | 2,418.34 | 2,507.01 | 2,265.02–2,582.03 |
| 7 | Sun 8 Nov | 2,418.34 | 2,516.98 | 2,242.19–2,608.33 |

The models intentionally represent two hypotheses, not two credible calibrated
trade targets. B1's rising path merely extrapolates a portion of the preceding
24h momentum, which could fail immediately. Do not compare their USDT amounts
to an undeclared original CN weekly quote as if parities had been proven.

## 3A. PIT-aware W45 original 3-window progress (not seven daily predictions)
The original freeze was issued **2026-11-02 08:19:08 UTC**, so its first
admissible bar is from **09:00 UTC**. Do not count Monday's preceding 9 hours
as a prospective price test.

Against original bands using native observed Binance USDT extrema through
4 Nov 22:00 UTC:

| Frozen bucket | Valid source hours | Asset | Original numeric bounds (quote UNVERIFIED) | Observed USDT extrema | Numeric containment so far | Original width / midpoint |
|---|---:|---|---:|---:|---|---:|
| Day 1–2 | 39 / 39 post-freeze | BTC | 75,000–81,500 | 76,388.88–78,357.23 | Inside | 8.31% |
| Day 1–2 | 39 / 39 post-freeze | ETH | 2,120–2,380 | 2,237.38–2,309.00 | Inside | 11.56% |
| Day 3–4 | 22 / 48 so far | BTC | 73,500–82,500 | 75,736.38–81,196.01 | Inside so far | 11.54% |
| Day 3–4 | 22 / 48 so far | ETH | 2,050–2,440 | 2,226.44–2,450.00 | **10 above upper numeric bound** | 17.37% |

The ETH numeric range breach is a source-backed observed fact **in USDT**
versus a historically dollar-formatted original range whose quote was
**not independently verified**. Therefore it must NOT automatically become
a currency-parity-approved error score, quantified historical edge or a
complete-window outcome. The second bucket is still LIVE (22/48 valid
hours), not finalized. Very wide frozen bands can also achieve high
containment without useful decision precision, so width and matched
benchmarks matter.

## 4. For the website
The official current-week Graph B can already show a **genuine green hourly
observed path** and original frozen *three-window bands*. Its authentic original
blue seven-daily-close path remains **UNAVAILABLE**, correctly.

**Do not** let these experimental B0/B1 lines masquerade as the original
blue dashed Monday forecast. A future separately marked research preview may
show them with their own issue clock and line styling, but neither research
model has official site publication authority. The original GitHub Pages
issuer and #1902 Monday 7/7 product gate remain authoritative.

## 5. What this establishes for W46 production
* Data-availability and issue-time legitimacy are different tests. We must
  separately check market candle close, source batch end, provider first-known,
  original weekly freeze time and target first-close before 7/7 can be scored.
* Baselines B0 and B1 can be independently pre-registered prospectively for
  later **matched-clock same-quote comparison**; no edge or better CN is claimed.
* Future W46 Monday **9 November 2026** must issue seven distinct BTC and ETH
  expected closes PLUS seven independently reasoned low/high daily bands per asset,
  or carry the accurate `INCOMPLETE` product status despite green CI.
* No W45 rewind, no new paid API call, no new model scheduler, no synthetic
  original seven-day price path, no market action authority.

## Reproduction
`python scripts/research/verify_w45_midweek_shadow_benchmark.py
06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json`

Adversarial tests:
`pytest tests/research/test_w45_midweek_shadow_benchmark.py -q`.

This packet is an offline bounded experiment; accurate source-clock and
forecast-issuance provenance **must be reverified** before inclusion in any
formal Task 2 precision or economic-edge sample.
