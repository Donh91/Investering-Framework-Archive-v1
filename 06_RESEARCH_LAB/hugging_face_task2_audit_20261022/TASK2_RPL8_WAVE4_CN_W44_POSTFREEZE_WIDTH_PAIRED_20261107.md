# Task 2 #1596 · Research Parallel Lanes v1 · Wave 4, W44 post-freeze original CN/B1 paired range

**Dato:** 2026-11-07  
**Status:** SOURCE-LOCKED_POSTFREEZE_REPLAY / HISTORICAL_DESCRIPTIVE_ONLY / NO_PREDICTIVE_EDGE_ADMISSION  
**Original owner:** Task2 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), original Cycle Navigator source #1516  
**Scope:** W44 2026-10-26..2026-11-02 UTC, one target week / BTC & ETH, same actual hourly path, *not two independent weeks or prospective independent shock cohorts*  
**Implementation:** `scripts/research/task2_cn_w44_postfreeze_paired_v1.py`, adversarial test `tests/research/test_task2_cn_w44_postfreeze_paired_v1.py`, executed under original read-only PR gate.

## Non-duplication and exact original issuance

Existing CN historic R2 owner report `06_RESEARCH_LAB/audit_summaries/2026-10-25__CN_BASELINE_LOCATION_SHARPNESS_REPLAY_v1.md` already compared 8 earlier W33–W42 weekly target groups / 48 asset-window outcomes and flagged broad-width scoring. Do not re-run those as "new independent evidence". W44 completed AFTER that dated research and has a genuinely different weekly target.

Actual original **CN W44 forecast**, **original independent four-week B1 forecast**, and **site publication freeze receipt** all FIRST appear at the SAME original Git commit `ca7563d4e47117b963d7c9c92db080a996d35cf8`, committed `2026-10-26T06:57:50Z`. Original site freeze is `2026-10-26T06:57:49Z`, official score eligibility begins at the **first completed UTC hourly source bar at/after `2026-10-26T07:00:00Z`**. This is separate from unknown historical upstream vendor first-publication, public account delivery, true quote parity and investment fill.

Immutable original source Git blobs at the new on-demand audit:
- W44 CN original freeze `4920c9f5c23279ecd540948b19cbd92c34dbebdf`.
- W44 B1 original forecast `c2422efa183e5d1bc9199fab8d458b0cfdf17414`.
- W44 original site/public freeze receipt `a7214cac7222d3aecdab8a07631f878fc795e4b9`.
- W44 original final hourly **OUTCOME_TRUTH**, NOT original issue-time features: `03_DAILY_CAPTURE_LOGS/weekly/2026/W44/WEEKLY_HOURLY_ENRICHED.csv`, `962d5e44fe5274692ad6b63e2a9da5e4035e5a35`. The original weekly source pack `03_DAILY_CAPTURE_LOGS/weekly/2026/W44.json` has blob `b5b30a81a6a161c8ebe022a3438b78f09fc511ac`, validates 168/168 continuous hours; final hourly outcome was committed 2026-11-02 after the week, never represented as an issue-time input.
- The W45 source scorecard for completed W44, **not a current W45 outcome**, blob `f69d6dfe31ce1e50660312ddb370fe0ebb16c0fd`, states the full CN W44 BTC and ETH ranges were contained. This is continuity/accountability and not incremental-alpha authority.

The read-only code reconstructs original 168 UTC hours, excludes **six pre-freeze hour-close observations**, and compares only the **162 completed hourly outcomes from Oct26 07:00 through Nov2 00:00 UTC inclusive**. It fails closed if original source SHA, time ordering, source gap, first valid time, B1 original independent status or prior W44 official scorecard change. No historical score or published range is rewritten.

## Source-clock correction discovered by native PR CI, 7 November 2026

The original on-branch CI failed with `MISSING_OR_DUPLICATE_HOURLY_SOURCE`. This was a **research clock interpretation defect**, not proven missing market hours. `source_window_end_utc` is the hourly collector's **batch request-window end**, which may repeat for multiple distinct completed hourly candles. It is **not** an individual candle close, first known provider publication, collector detection, nor user delivery. This is independently documented by the original `scripts/research/task2_hourly_source_window_clocks_v1.py` (Git blob `59b34fc2f862d1774dca37429e31762da5f0538e`) and `scripts/daily_capture/build_weekly_calibration.py` (Git blob `b1f5349847d4ef9e3e0446db4387baaf80a83fa8`) whose week/hourly-gap identity is `timestamp_utc`.

A fresh source readback found **168/168** unique, contiguous canonical nominal UTC-hourly candle opens, but **55/168** rows had collector batch windows ending later than the corresponding nominal candle. Those 55 batch-clock differences are **not 55 missing hourly candles**; the batch end spans 1–6 hours after nominal start across this frozen W44 source. The prior code improperly used this repeated batch field as its unique hourly timeline and native CI correctly rejected it. The repaired source-locked code now derives nominal completed candle end as `timestamp_utc + 1 hour`, validates uninterrupted first/last 168h and enforces that each collector batch end remains whole-hour and between nominal +1h and +24h. It does not rewrite original CSV, original CN/B1 or scorecard; does not claim source first-known or actual delivery; and retains the original six pre-issuance completed-hour exclusions and 162 post-issue observed candle endpoints.

The native new positive/adversarial fixture suite separately tests legitimate repeated batch timestamps, deliberately premature and implausibly late batch ends, misaligned subhour timestamps and the exact known 55-count. This is an actual methodology repair, **not** a new market edge or increased independence. Record source-clock inference as corrected only if the *new PR-head CI* completes successfully; prior failed CI remains a preserved negative case.

## Empirical match on 162 eligible post-issue hours

| Model | BTC range | BTC full LOW+HIGH inside? | Width % of previous-close anchor | Jaccard of actual LOW/HIGH |
|---|---:|---|---:|---:|
| CN original W44 | $75,000 – $86,000 | **YES** | 13.7236% | 0.5132 |
| Preissued independent B1 | $76,840.31 – $81,734.79 | NO | 6.1063% | **0.8670** |

BTC post-issue observed LOW/HIGH `76,325.98 / 81,971.00 USDT`. CN band is **2.247×** as wide. B1 lower miss `$514.33` and upper miss `$236.21` against the proxy series, yet its narrower box overlaps the realized range better.

| Model | ETH range | ETH full LOW+HIGH inside? | Width % of previous-close anchor | Jaccard of actual LOW/HIGH |
|---|---:|---|---:|---:|
| CN original W44 | $2,150 – $2,550 | **YES** | 17.1683% | 0.5437 |
| Preissued independent B1 | $2,167.54 – $2,388.01 | NO | 9.4626% | **0.9550** |

ETH post-issue observed LOW/HIGH `2,174.08 / 2,391.55 USDT`. CN interval is **1.814×** as wide. B1 upper miss only `$3.54`, but a strict joint-containment score still gives B1 a binary MISS.

**New mechanism:** one legitimately preissued simple independent B1 baseline and one originally issued CN band on the same W44 target are **ranked differently by different existing descriptive metrics**: CN captures **2/2** full joint ranges versus B1 **0/2**, while B1 is materially more width-efficient and has a greater observed Jaccard overlap for both assets. These are *different utility dimensions*, not contradictions and not evidence that B1 was a better actionable risk forecaster in independent new market shocks. Mere 100% public Price Range Precision or 2/2 containment must never be interpreted as alpha or copied into new model confidence.

## Scientific, security and progression gates

- The original forecast bands are labelled USD and historical outcome source is Binance BTCUSDT/ETHUSDT. Exact USD/USDT currency equivalence is NOT proven; this is a reproducible proxy-based retrospective diagnostic only, not exact-quote original forecasting skill.
- W44 two assets share ONE calendar market regime; **independent episode n remains UNKNOWN**. No statistically meaningful generalization, untouched independent holdout, original vendor price first-known or user delivery proof.
- This is **joint minimum/maximum** interval target. Do not manufacture a proper joint Winkler interval score by treating two extrema as independent scalar outcomes. Existing M3 adjudication [Oct5 CN skill baseline](../m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md) already rejected established CN week-range superiority and remains unchanged.
- No market rule, current live CN site, forecast, historical original score, source vendor collection, model weight, private raw provider value, Round3 research/data firewall, autonomous workflow or real trading order changed.

**Next original owner scientific admission:** re-use the existing canonical W44+future weekly CN/B1 source artifacts, source-first-known, instrument quote parity, complete post-freeze hour evidence and multiple independent prospective week/event families. Report containment, width, relative placement and breaches on the same cohort, and predeclare investor decision loss separately. W45 is not fully matured before Sunday 2026-11-08 24:00 UTC; do not score it as a complete seven-day outcome on Nov7.
