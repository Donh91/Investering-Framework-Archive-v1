# Task 2 · First source-pinned mechanical diagnosis and conditional R2–R7 simulation release

**Recorded:** 2026-10-14. **Research-only, NOT an R1-approved historical backtest, independent market-event test, or proof of economic edge.** Exact original source revision `098c50d36b222c4c8ffa179a5879d36a74194bc4`. Machine receipt with nine source+outcome Git blobs: [2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.json](2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.json). Current canonical owner: [Task 2 R0–R7 handoff](2026-10-13__TASK2_FULL_STACK_NO_HINDSIGHT_AUDIT_WORK_HANDOFF_v1.md), R1/Task1.5 #1596, EDGE #1530, Compass Risk-to-Action #1553. This is an **append-only experiment design**, not a second simulation engine, scheduler or queue authority.

## 1 · An actual low-cost calculation, strictly scoped

The original frozen 2026-10-12/13 Compass audit found 17 issued official Compass forecasts: six native scoring-v2, 11 native scoring-v3, and **nine** native-v3 12-hour outcomes at the pinned source. The two remaining v3 outcomes were **ABSENT_AT_SNAPSHOT**, not established as failed/censored. No v2 record is forcibly rescored under v3.

For each of the **nine** available v3 originals, the mechanical rule predicts BTC and ETH **UP** if the forecast's original `selected_features.btc_delta_since_prior_packet_pct` / `eth_delta_since_prior_packet_pct` is positive and **DOWN** when negative; zero must abstain. This is *change since the prior auto-market-state packet*, **NOT necessarily a strict one-hour momentum signal**. No AI API was needed to calculate the rule. Original forecast `horizons.NEXT_12H.expected_direction` and original outcome `direction_accuracy` were read by exact Git source/object path. Outcomes were used for **evaluation only**, never for building the mechanical rule. Decision time, original hash binding and matching target observation were previously read back; source-provider first-known remains unverified.

| 12h original outcome | Original Compass | Price-delta-sign-only rule |
| --- | ---: | ---: |
| BTC correct | 4 | 4 |
| BTC incorrect | 4 | 5 |
| BTC abstained | 1 | 0 |
| ETH correct | 3 | 4 |
| ETH incorrect | 5 | 5 |
| ETH abstained | 1 | 0 |

**Crucial diagnosis:** for **all eight** issued forecasts where Compass selected UP/DOWN, its direction matched the simple prior-packet price-delta rule **for BOTH assets**, i.e. **16/16 asset-direction matches**. The lone `MIXED`/abstain event differs by declining to forecast either asset. The simple rule forecasts BTC incorrectly and ETH correctly on that one extra event. There is no evidence in this tiny cohort that complex Compass features supplied *incremental directional differentiation*, but **abstention and capital protection may still have distinct value** and have not been priced or evaluated.

**Guardrails:** This two-day window is selected retrospectively for a diagnostic, has overlapping 12-hour market outcomes, includes duplicated source/target conditions, has no verified independent event-family N, excludes two v3 attempts without original outcomes, and lacks independent provider-first-known/issuance publication proof. It is **not a sealed holdout, not historical R2 admission, not a portfolio backtest, and not evidence of 50% forecast skill**. Percentages, confidence intervals, Sharpe, optimal thresholds, wealth curves or strategy winners from these rows would be misleading. Preserve all original misses/abstentions and the incomplete attempt denominator.

Reproduction procedure for a reviewer with a checkout containing pinned Git revision:

1. Read **all** official-v3 issued forecast JSONs in `04_MARKET_LEARNING/handlekompas/official/daily/2026/10/{12,13}` at exact pinned ref, and the corresponding original `official/outcomes/.../*_12h.json`. Do not fetch current moving HEAD instead.
2. Join on exact `compass_id`, original forecast `compass_sha256`, source packet hash and `scoring_contract=v3`. Keep all issuance attempts; classify absent outcomes separately.
3. For nine matching original 12h outcomes, derive sign of `btc_delta_since_prior_packet_pct` and `eth_delta_since_prior_packet_pct` in original `evidence_snapshot.selected_features`. Compare only to **original** `direction_accuracy.{btc,eth}.realized_pct` signs at the exact native v3 target clock. Original `MIXED` is abstention, never a hit/miss.
4. Assert original direction labels and computed simple rule produce the table above, plus eight forecast-issuance matches for each asset. Reject any source-hash, contract, target-clock or attempt-census mismatch; do not silently backfill two missing outcomes.
5. This is a deterministic research readback; classify the result `EXPLORATORY_ONLY`. Do not promote to any official weekly score, action signal or calibrated framework edge.

## 2 · All Deep Research coverage enters the pre-registered execution design

The existing [eight-report independent research packet](../../../06_RESEARCH_LAB/audit_summaries/2026-10-14__TASK2_DEEP_RESEARCH_INDEPENDENT_REVIEW_PACKET_v1.md), DR01–DR08 source summaries and the supplemental 7-page Resumé forensic correction are **mandatory read references**. Never assume that an experiment described by one of those reports was actually executed; do not reuse unsupported September simulated outputs or invented historical CFGI. The following are **gated research packets routed to the existing Task 2 R0–R7 owner**, not 12 automatically launched model calls:

| Work packet | Research arm and primary control | Gate |
| --- | --- | --- |
| P01–P02 | Complete issue/outcome denominator and independent historical CFGI era/first-known; v2/v3 timestamp reconciliation | **Now: R1 proof-building only** |
| P03 | CN/Compass direction+range versus persistence, price/volatility and simple trend | R1-admitted same-clock full attempts |
| P04 | CFGI composite, component and non-price residual vs price+momentum+volume+volatility | R1 and era-specific vendor-source vintage |
| P05 | Pullback/Tsunami warning lead-time and entire false-positive denominator | Original alerts and independent event clusters |
| P06 | Large-pullback trim and reentry versus capital-matched HOLD/cash | Original permissible trades, fees, slippage and execution |
| P07 | Rotation + altseason start versus ETH/BTC relative strength, breadth and trend | Noncircular phase labels, historical eligible universe |
| P08 | Exit **before altseason ends** versus stay invested and false-exit cost | Frozen pre-distribution warnings; no hindsight top selection |
| P09 | OI/funding/orderbook/stablecoins/ETF and free public macro controls | Natively captured first-known and revision semantics |
| P10 | MAEVE ENTRY/NONE/DCA/EXIT vs capital/time-matched alternatives | No post-entry features and complete nontrade opportunities |
| P11 | Alpha Lab launches ETH/Solana/Robinhood: selection vs random, misses, after-cost viability | Entire as-of launch universe and survivor delisting |
| P12 | AI versus cheap mechanical rules, calibration, action utility, API dollars/decision | R1 originals plus sealed future holdout and reproducible after-cost fills |

**Negative evidence must survive:** Retain prior bounded Round-2 pullback findings (46 anchors, 45 matched controls, 11 non-winning reload options), censored/unissued slots, all losses and every false alert. Do not optimize 144 frozen proposed variants on the same holdout or confuse old Round-2 with new Task 2 R2–R7. If predeclared independent market-family count is inadequate, outcome is `INSUFFICIENT_POWER` rather than a significant result.

## 3 · Source expansion: free API is not free historical availability

Potential **conditional** augmentations, not approved downloads: existing archived Binance/OKX OHLC/funding, free historical macro releases where ALFRED/FRED vintages can be authenticated, DefiLlama supply/flows with time-revision audit, CoinGecko history subject to current coverage/terms, Farside settled ETF releases and Blockchaincenter altseason definitions. Every field needs *native provider publication*, *vintage as originally known*, *retrieval/ingestion*, *decision issue* and *maturity* clocks; listing a free endpoint does not prove it existed on the historic decision day. Rates, limits, paid upgrades and backfill permissions must be checked before any collection. Original microcap candidate universe must include failed/delisted launches and executable liquidity.

## 4 · API/Codex sequencing, economics and deployment lock

**Use deterministic Python/GitHub tests for number-crunching** (cheapest, reproducible), then the **existing** GPT-6.1 Sol research-lab route for one evidence-bound independent adversarial critique *only after* actual relevant inputs/results exist. Sol must be supplied the Task 2 canonical handoff, all DR01–DR08 intake documents, the pinned test design and exact resulting stdout/receipt; preserve the existing one-active-mission slot and 3 USD/run + 40 USD/month limits. Sol is not a magical batch-runner and must not invent 2025 as-of CFGI from 2026 downloads. Codex owns bounded implementation via its existing intake/CI/review cycle. A model output never self-merges or self-promotes to canonical.

For net exit effectiveness, freeze **original investable asset universe**, original allowance to sell, time-to-target, benchmark market action, exact competing portfolio holdings/cash, fees, spreads, slippage/depth, lag and reentry availability. Report *false exit regret* alongside avoided drawdown, capital exposure and sensitivity to execution assumptions. Predicting that a top was nearby does not mean the action would have outperformed HOLD after costs.

**Release status today:** `R0_GIT_OBJECTS_MAPPED / R1_PIT_BLOCKED / R2-R7_HISTORICAL_NOT_ADMITTED`. We have executed **one tiny exploratory, nonadmitted nine-forecast sign diagnostic**, but **no newly admitted historical R2–R7 backtest, after-cost net wealth or production Kompas recalibration**. The next hard milestone is a source-first-known + complete-attempt R1 cohort and independent event-family verdict, then the first true bounded R2 matched-price rule test. No new supervisor, scheduler, authority, paid dataset, automatic trading or production rule changes.
