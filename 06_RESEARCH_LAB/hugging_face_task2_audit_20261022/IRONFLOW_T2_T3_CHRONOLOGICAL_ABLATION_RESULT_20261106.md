# 46 | Ironflow actual T02/T03 out-of-time historical ablation, NO demonstrated incremental edge
**Recorded:** 2026-11-06 | **Source:** Ironflow (ironflow.sh), CC BY 4.0 | **Original owner:** Task 2 #1596 / Derivatives #387, branch PR #1988
**Actual run:** GitHub Actions [#42311881876](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311881876), original exact head `f25807330bafdd64e704171b730cfc7de588d6c6`. Historical T1 + model code job SUCCESS, source artifact ID **13548801929** and SHA256 `838b20f4adb91f1f35a09891a5aa821ea5bd905f7e638d187a19f6a1027c3805`, expires 2026-12-06. Research values were inspected from actual archived JSON, not inferred from run labels.

## Scientific scope and registered comparisons
- **264 unique UTC day anchors**, BTC/ETH/HYPE x (29 Oct2025 +29 Sep2026 +30 Oct2026). Each observation uses previous fully settled 24h and next 24h low; distinct daily anchors limit per-asset 24h overlap but **not cross-asset/daily market shock dependence**.
- Binary target: next-day intraday high-to-current-close downside threshold, specifically future minimum low / current 23:00 UTC completed-hour close <=0.98. This is a risk label, **not a real portfolio fill or signal**.
- Historical chronological tests: (A) train 2025-Oct 87, evaluate 2026-Sep 87; (B) train 2025-Oct + Sep2026 174, evaluate Oct2026 90. Multiple assets pooled with market dummies; calendar day clustered bootstrap 1,200 replicates.
- Model families: **constant prior**, **past-24h return + realized volatility + market dummies**, and **same price baseline plus prior-24h liquidation-intensity, OI percent change, settled-funding cumulative rate**. Fixed sklearn logistic C=1.0 with training-only standardization (fit on historical train, transform test) and clipped test z-scores. No future outcomes as features.
- Scientific caveat: Analysis choices were created after the investigator had seen 2026-10 aggregate outcomes, so "out-of-time" is chronological partitioning, **NOT sealed untouched holdout**. No original 2025/Oct2026 Ironflow first-known source proof (public snapshots released Nov2026) and NO live model/trading promotion.

## Exact observed prediction scores
| Historical train -> evaluation | Test n | Constant Brier | Price/vol/market Brier | Plus derivative features Brier | Price AUC | Plus derivatives AUC | Brier improvement (+ is better) | Day-cluster 95% interval |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2025-Oct -> 2026-Sep | 87 | 0.269917 | 0.240046 | 0.237498 | 0.560642 | 0.572533 | **+0.002548** | [-0.006076,+0.010967] |
| 2025-Oct+2026-Sep -> 2026-Oct | 90 | 0.243086 | 0.242791 | 0.244536 | 0.601734 | 0.596634 | **-0.001745** | [-0.008841,+0.004885] |

The derivative features **slightly improve one historical test and worsen the next**. Both day-cluster intervals include zero, so no supported consistent incremental performance or confidence gain. Calendar day clusters are only 29 and 30 and correlated BTC/ETH/HYPE; these CIs are methodological diagnostics, not production statistical guarantees. No independent transaction-cost/alert opportunity has been quantified. **Current label: `NO_REPLICATED_INCREMENTAL_EDGE_YET`, `SCIENCE_RESEARCH_ONLY`.**

## Surprising research contribution
The initial overlapping hourly cohort in [#45](IRONFLOW_EXECUTED_6_LANE_EMPIRICAL_REPORT_20261106.md) seemed favorable for ETH; removing within-asset overlap and comparing with same-clock price/volatility reduces any clear claim. BTC September 2026 and HYPE October 2026 show an *opposite* association under day blocking. This illustrates why the system must not turn a large liquidation print into a canonical SELL/RISK_DOWN or copy-trade automatically. The apparent 1% intensity threshold is a historical diagnostic and MUST NOT be tuned or used prospectively without preregistered tests.

## CI scope and diagnostics
- The first exploratory OOT experiment run succeeded in its **own fully provisioned Ironflow workflow**, including sklearn package install and full Parquet re-read.
- Global **Automation Production Health Gate** at [run #42311881886](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311881886) failed at `pytest --collect-only` because sklearn was imported at module scope in new research test, while global collector has pandas but not sklearn. It is NOT evidence the live automation is unhealthy; it's a test/environment dependency mismatch.
- Corrective change to lazily import sklearn inside evaluation functions landed on same PR branch as commit `7da21b905cc5bbecb82324e51355f4476c4628b5` pending fresh CI and current head verification. Do not assume fix passed until actual global gate succeeds.

## Next eligible research and blockers
1. Replicate with many non-overlapping windows and separate regimes (2015... unavailable; Ironflow liquidations May2025 onward). Freeze thresholds and model before later truly untouched months, verify original source availability/latency for forward collection.
2. Test independent Binance crowding/taker controls and lagged incremental information beyond price, realistic actionable-size quote/delay, false-alert rate and burden. Decline canonical changes unless clear after-cost gain.
3. Stratify market and calendar regime; avoid pooling cross-asset clusters. Test alternative event triggers only with preregistration / multiple-testing correction. A small positive in an isolated market is a research candidate, not full-framework edge.
4. Continue T07 original source first-known and delivery, T09 exact-chain CA/altseason transfer separately. Fail closed on historical-source snapshot first-known.
5. S1 own role is to supervise PR CI and owner QA, not re-classify this negative result as an unfinished mandate requiring endless "improvement".
