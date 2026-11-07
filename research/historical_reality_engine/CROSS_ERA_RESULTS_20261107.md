# HRE cross-era historical stress baselines | 7 November 2026

**Status:** FIVE_NATIVE_SOURCE_VERIFIED_REPLAY_EPISODES / EXPLORATORY / NO_VERIFIED_KOMPAS_EDGE.
**Owner:** [Task2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), scientific owner; affected risk [#1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553), Cycle Navigator [#1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516), S1 [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156).
**Native original result:** [PR #2012](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2012), merged `aea48ec8b9c3f07fde3b04cc60e0759ffef10e88`, [Actions run 42391907367](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42391907367), both independent research jobs SUCCESS, exact-head 5/5 observed workflows SUCCESS, 18/18 targeted source/timing regression tests PASS. The machine-readable [cross-era results and artifact receipts](CROSS_ERA_NATIVE_RESULTS_20261107.json) preserve the full confusion matrices and source/period limitations.

## What was tested

Separate predeclared periods spanning 2022 Terra/UST, 2022 FTX, March 2023 USDC/SVB, August 2024 volatility and February 2026 stress. For each, the native runner downloaded three public monthly BTCUSDT and ETHUSDT hourly source archives and validated hosted SHA256 CHECKSUMs, **30 source ZIPs/checksums total across two native compute jobs**, with raw provider close-time normalization and missing hours preserved.

The tested rules were unchanged from the earlier R1 pilot: a daily UTC cutoff, last *completed* hourly close, forecast outcome defined as worst forward low during the next 72 hours <= -8%, and two completely simple price-only early-warning comparators based on prior 24h drawdown and prior 72h high/low. No Terra/FTX/SVB-specific knowledge or later shock news was passed in as a feature. The scenario date is selected ex post for the historical case study and is NOT an original model event-time prediction.

### Price-only warning recall for the severe-outcome daily cutoffs

| Period | BTC: baseline caught/qualifying | ETH: baseline caught/qualifying | Qualifier |
| --- | ---: | ---: | --- |
| Terra 2022 | 5/20 | 8/31 | 85 scored daily cutoffs per asset |
| FTX 2022 | 1/4 | 1/11 | 86 cutoffs per asset |
| USDC 2023 | 0/4 | 0/7 | 77 cutoffs per asset |
| August 2024 | 1/8 | 3/16 | 86 cutoffs per asset |
| February 2026 | 1/10 | 3/23 | 84 cutoffs per asset |

These are counts of **overlapping 72h severe-outcome daily windows** selected around known eras, **not independent Black Swans**, hence not legitimate statistical hit rates or source-admitted original investor warning precision.

Across these five selected episodes the fixed reactive baseline marks only 8/46 BTC and 15/88 ETH severe-outcome daily windows. The alternative fixed price-only comparator marks 11/46 BTC and 22/88 ETH, but with more false alarms across several periods. Neither should be used to tune live 4/5 warnings; no calibrated, independent, prospective benefit has been shown.

### The best next research questions, not conclusions

1. Are these misses primarily due to *source-limited price-only observability*, or would genuinely first-known liquidity/derivatives/news/stablecoin, exchange-specific and breadth data have improved the warning before the severe downside while remaining sane on matched quiet periods?
2. What is the earliest lawful observation point for each distinct crisis or rebound, versus when a price-only alert first fired? Compare actual issue/delivery times for 2026 only if preserved, not retrospectively constructed 2022 signals.
3. Can a bounded crisis vulnerability radar improve alert lead time and after-cost capital preservation across **independent** crisis families while avoiding false exits in similar non-crisis volatility?
4. In 2021 weekly range pilot only 2 eligible complete weeks each; repair historical source windows/compare other sources and score width-adjusted interval metrics before claiming a CN model improvement.
5. After frozen source-admitted signals exist, compare the real versioned Official Kompas response and existing risk decisions. Without original-era source availability, abstain rather than substituting a modern indicator.

## Native execution and restrictions

- Independent 2022 job `hre-extended-2022-terra-ftx` ID 128461050873, artifact 13581583044, ZIP SHA256 `11acf7d455804812860a3c3583ff17752ba3e5be84c7aa54f63be11d99835448`.
- Independent 2023/2024/2026 job `hre-extended-2023-2024-2026` ID 128461051004, artifact 13581123842, ZIP SHA256 `d727ab80af695f62cf985f61ef8f77a909713fdedcb106bd3911540ae4085667`.
- Both performed via the **existing read-only, PR-triggered Research Parallel Lanes Skill Contract CI**, without new workflow, schedules, bots, billed models or private-source mutation.
- 30-day Actions artifacts are NOT durable T3 raw storage; keep the compact official job/experiment receipt and original source re-download recipe on main.
- The source ZIPs are retrospective archived truth tapes; their current SHA256 is not proof the file revision was available before the 2022/2023/2024 market event. Everything is nonauthoritative for actual 2020-2025 production.
- No verified natural S1 unattended execution, Grok original report or Sol MAX provider POST occurred during this study.

**Scientific outcome:** Two genuine research Actions jobs are completed and evidence has improved. The price-only controls commonly signal too late for the selected downside windows. **Actual historical Kompas/CN edge, crisis foresight, investable altseason rotation and stronger future production settings remain UNPROVEN.** Continue only through original Task2/source/Risk/CN owners with preregistered independent tests.
