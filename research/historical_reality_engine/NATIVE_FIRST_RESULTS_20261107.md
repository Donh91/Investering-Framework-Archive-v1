# Historical Reality Engine | First native 3-lane results, 7 November 2026

**Status:** ACTUAL_JOBS_COMPLETED / RETROSPECTIVE_ONLY / NO_PREDICTIVE_EDGE_CLAIM.
**Original scientific owner:** [Task 2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). **Source:** Public Binance SPOT monthly 1h BTCUSDT/ETHUSDT archives, each downloaded and authenticated against upstream .CHECKSUM SHA-256 during original GitHub Actions run. Those current ZIP files ARE NOT a record of first original public availability of specific 2020/2025 prices.
**Initial execution:** [PR #2010](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2010), actually merged `c07f0030856619fed0c402bf745a0be091376faf`. [Native Actions run 42390995602](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602), 6/6 skill CI jobs SUCCESS, 5/5 observed PR workflows SUCCESS, 15/15 source tests PASS. Detailed machine ledger [NATIVE_FIRST_RESULTS_EVIDENCE_20261107.json](NATIVE_FIRST_RESULTS_EVIDENCE_20261107.json).

## 1. Verified source data and a real new scientific trap

The first native runs did NOT pass unconditionally. Source validation caught **two independently reproduced source issues**:

1. Binance monthly archive `close_time` can represent the last-trade timestamp *inside* the nominal 1-hour candle, rather than the moment the 1h bucket became complete. Examples in job logs: 2020-02 open `1582110000000`, source close `1582112132286`, only 35.5 minutes later; 2021-02 open `1613012400000`, source close `1613014854773`. Code now waits for the full nominal UTC hourly bucket end before it can use that candle in a historical decision. This prevents accidental use of a future close before the hour ended.
2. Some monthly source candles are **missing**, despite otherwise source-matching SHA-256. February/March 2020 has 1,433 observed out of 1,440 expected 1h buckets for both BTC and ETH, seven gaps each. September/October 2025 has 1,464/1,464 for both assets in this source window. Input or outcome windows crossing missing observations ABSTAIN; they are not interpolated. Complete 24-hour UTC dates required for weekly forecast training and evaluation.

The strict source behavior is valuable and testable. A passing SHA-256 proves the file as currently published, not completeness, availability in the original historical year, or market predictive value.

## 2. Crash stress control, price-only, NOT existing official Kompas

Predefined label: worst low during next 72 completed hours at least -8% below last fully closed hour. Historical warnings are evaluated at UTC daily midnight, with one fixed price-only 24h drawdown baseline versus a second simple volatility/drawdown candidate. These **daily labels overlap in their 72h target periods** and cannot count as independent crisis events.

| Asset and era | Valid daily cutoffs | Baseline TP/FP/FN/TN | Challenger TP/FP/FN/TN |
|---|---:|---:|---:|
| BTC 2020 | 60 | 2 / 7 / 15 / 36 | 2 / 7 / 15 / 36 |
| ETH 2020 | 60 | 5 / 6 / 18 / 31 | 7 / 10 / 16 / 27 |
| BTC 2025 | 55 | 0 / 1 / 4 / 50 | 0 / 1 / 4 / 50 |
| ETH 2025 | 55 | 2 / 2 / 11 / 40 | 2 / 3 / 11 / 39 |

**What is learned:** Simple reactive price thresholds miss many of the material subsequent drawdown windows. Changing price-only thresholds trades recall for false alarms in ETH 2020. The 2025 BTC fixed price controls missed all 4 overlapping eligible daily outcome windows meeting the -8% threshold. These **are not forecasts emitted by Kompas**, not independent event counts, and do not prove a more complex model could have predicted the Black Swan in advance. They justify the next separate source-available vulnerability/false-warning investigation, not a production escalation to 4/5.

## 3. Cycle Navigator weekly *naive* benchmark, 2021

The retrospective harness froze one Monday 00:00 UTC source-bound decision and produced seven separately enumerated expected closes and low/high intervals for each asset. Both price-only arms use the same last-close expectation. A fixed +/-2% times sqrt(day) band is compared with a broader/adaptive range based on 28 earlier daily absolute returns; the actual separate day high/low must both lie within the predicted interval.

| Asset | Qualified Monday weeks | Days | Fixed-band full coverage | Adaptive-band full coverage | Expected-close MAE |
|---|---:|---:|---:|---:|---:|
| BTC 2021 | 2 | 14 | 4/14 = 28.6% | 10/14 = 71.4% | 2.6394% |
| ETH 2021 | 2 | 14 | 2/14 = 14.3% | 8/14 = 57.1% | 5.5336% |

These are **two weeks each**, not evidence of reliable 2020-2026 CN forecast performance. Larger coverage alone can result from much wider intervals; check sharpness, matched forecast-age sample and untouched chronological holdouts before choosing a method. Some historical weeks do not pass strict complete-day source gates and must remain omitted, not filled. No original 2021 weekly forecast existed in this archive. The original 2026 W45 0/7 remains unchanged.

## 4. Evidence and cost

All three jobs were actual independently launched read-only GitHub Actions research computations:
- `hre-replay-source-qa` job 128458333205, artifact [13581378037](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602/artifacts/13581378037), ZIP digest `sha256:c240822926c7350b0c8bb7d27f82e1a584f916f7d42b0c255d21e13bfc75fee6`.
- `hre-replay-crisis-baselines` job 128458333220, artifact [13581134154](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602/artifacts/13581134154), ZIP digest `sha256:73f6b2077987cfe3c8e3eee171632209576bd20788635fd4a577de4e5ec5f691`.
- `hre-replay-cn-weekly-controls` job 128458333234, artifact [13581601360](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602/artifacts/13581601360), ZIP digest `sha256:6f87a32fb3055a9c5e08a92161f16e02ca72ffa56c0e4afe308c695bf55b58cd`.

These are 30-day GitHub artifacts; **durable T3 raw history is not yet established**. This compact public-safe scientific receipt survives after artifact expiry; source ZIP SHA hashes remain in the actual artifact until expiry. No Sol API charge or external AI output was involved. Do not claim a natural unattended S1 repair from this manually triggered interactive research PR.

## 5. No more “what is next?”: objective next scientific work

A. **HR-001 & HR-007, Task2 #1596 and Risk #1553:** Evaluate real source gaps by source month, preserve availability, compare price-only crisis warnings with materially different *pre-event observable* vulnerability data, matched quiet periods, timestamped news and 2022/2023 event families. Score disjoint event-family clusters and false warning burden; do not port fixed retrospective threshold to live Risk.

B. **HR-009, CN #1516:** Expand 2021/2024/2026 weekly windows and independent source coverage, compare interval score and relative sharpness, not coverage alone; include real original 2026 first-issued forecasts only after source-admission. No synthetic W45 7/7 history.

C. **HR-013, Skill Quality Gate:** The real bar-close vs provider-last-trade data leak and missing hour abstention are good candidate repeated procedures. Propose candidate source-vintage/time-window verification skill under `07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/`, evaluate against preexisting data QA skill and no-skill baseline with independent negative cases; only qualified candidate may enter canonical registry and be discoverable across repository-aware threads.

D. **HRE/S1 handoff:** Current S1 saved automation now contains HRE Task2 discovery logic but no natural scheduled HRE action is yet proven; source-bound next original PR, new issue comment and native S1 outcome required. Grok independent review optional after a frozen source job/result and original case digest. Sol MAX payment only through #1476 explicit mission/receipt/budget policy, no silent automatic purchases.

**No edge admission:** This pilot proves data-custody mechanics, a correct closed-bar semantic, and functioning independent Actions research jobs. It neither proves Official Kompas predictive accuracy across 2020-2026 nor any trading economics. Continue from the original owners, preserve negatives, and demand untouched future data to measure actual improvements.
