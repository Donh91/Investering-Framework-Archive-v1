# Compass Horizon Edge: Weekly 5–7D vs 2–3W, price ranges, direction and portfolio utility

**Date:** 2026-10-11 (Europe/Copenhagen)
**Status:** RESEARCH_ONLY / EVIDENCE-BOUNDED / NO_EDGE_PROMOTION
**Owner:** existing Compass and Cycle Navigator owners; route prospective multiweek execution to **Archive issue #1516** and risk-to-action delivery/economics to **#1553 / existing DEL/M6 owners**.
**Purpose:** answer which horizon is more useful for *price placement*, *direction / turning sequence*, and *portfolio action*, without changing existing Official Compass, website, CN freezes, scores, decision thresholds, weights, automation, or execution permissions.
**Privacy:** only already-public source-backed repository facts are cited here; no private/restricted data or personal positions.

## 1. Executive adjudication

**Most qualified working hypothesis, not established forecasting alpha:**
- **5–7D** is the preferred **primary price-range / tactical planning test horizon**. It offers a bounded observation window, quicker error settlement and clearer comparison with mechanically frozen volatility bands. This does **not** mean current CN weekly bands reliably beat baselines or locate executable entries.
- **14–21D (2–3W)** is the preferred **market-path / regime-transition / portfolio risk-budget context horizon**. It can distinguish a transient weekly retest from genuine structural deterioration or progressing rotation. An *incremental 2–3W directional or economic edge over 5–7D is currently unproved*. The richer forward path sought in #1516 is not evidence until frozen, mature and scored.
- **12–72H** is the necessary execution/freshness checkpoint, **not** a competing long-horizon thesis. A 2–3W view must never override fresh governed action authorization.
- **Hybrid to FALSIFY:** 2–3W sets the scenario/risk context; 5–7D tests the near-term price corridor and retest; 12–72H checks current evidence and the existing permission to act. No current portfolio action or UI change follows from recording this hypothesis.

**Answer to user:** If forced to prioritize one for *range measurement*, study the week. If forced to prioritize one for *capital preservation and avoiding a premature microcap/alt exit or deploy*, study the 2–3W sequence. Economic superiority of either, and of their combination, remains UNKNOWN.

## 2. Verified source inventory and what it actually demonstrates

### M3 prospective and retrospective range evidence

- M3 final adjudication **rejects** a strong claim that weekly CN price ranges show established incremental skill over simple volatility bands.
- W39–W40 research reconstruction: **4 asset-week rows / 2 correlated week families**; CN 100% daily containment and mean Jaccard **0.504487**; DUMB1.5 Jaccard **0.547552**, containment **75%**; DUMB2.0 Jaccard **0.460933**, containment **89.2857%**. CN loses Jaccard in **3/4** paired rows against each ATR baseline.
- CN loses Winkler against DUMB1.5 in **2/4**, against DUMB2.0 **3/4**. Its aggregate Winkler advantage is highly influenced by **W39 BTC**. Excluding that row, CN mean Winkler ≈ **14.09**, DUMB1.5 ≈ **12.66**, DUMB2.0 ≈ **13.41** (lower is better).
- CN ranges were generally wider; W40 simple bands had equally complete containment with superior sharpness. The public **70% containment + 30% Jaccard** Price Range Precision is an *accountability* metric, not proof of tradable price-range alpha.
- The W39–W40 baseline was **reconstructed from pre-freeze inputs after the fact**, not itself originally frozen. Do not present it as an original prospective baseline.
- An **independent native forward benchmark** now exists, first prospective W41 frozen row under `05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W41.json`; it uses a four-week median asymmetric excursion and is withheld from the CN model. Compare matured W41+ rows only against their actual independent native freezes.
- Historic M5 degraded negative evidence was adverse to CN-vs-ATR range skill. Do not pool that method era with current W39+ scores.

Public source:
- `06_RESEARCH_LAB/m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md`
- `06_RESEARCH_LAB/m3_replay/2026-10-05__RL-CN-SKILL-BASELINE-003__reconstructed-baseline-v1.json`
- `05_CYCLE_NAVIGATOR/range_baselines/README.md`
- `04_MARKET_LEARNING/range_skill/2026-07-08__m5-range-skill-audit-degraded-execution__canonical.md`

### Official Compass direction evidence, independent of range containment

The 2026-10-10 *public-scope master audit* reports, from a pinned population: **142 official freezes**, **426 forecast-horizon rows**, **319 observed outcomes**, **107 missing outcomes**. All matching hashes and reproduced scoring calculations passed within that bounded source set; original publication/first-knowledge admission is still unresolved.

- In a *selected 21-row* 12H BTC directional UP/DOWN comparison, the Official Compass and persistence baseline made identical calls, **9 correct / 12 incorrect**. This is not evidence of incremental short-horizon direction alpha.
- At BTC 168H (7D), **29 scored forecasts**, **27 correct / 2 incorrect**, but **all 29 forecasts were SIDEWAYS**, with **55 abstentions** in the audited cohort. Wide ±5% SIDEWAYS tolerance and abstentions explain why this must **not** be marketed as a 93%-accurate ability to call tradable UP/DOWN direction.
- Present the original denominator and abstention/coverage explicitly. Overlapping freezes are dependent; do not count them as independent weeks.
- No admitted costed matched portfolio strategy comparison or verified warning-to-usable-action delivery was established in that audit.

Public source:
- `05_CYCLE_NAVIGATOR/internal_learning/research/2026-10-10_master_audit_work_receipt_v2/EXECUTIVE_REPORT_AND_HANDOVER.md`
- `04_MARKET_LEARNING/handlekompas/SCORING_CONTRACT_v2.md`

### 2–3W and strategic governance

- The **2–3W CN base case** is a distinct **14–21-day directional narrative**; it is **not automatically a prospectively frozen BTC/ETH 14/21D numeric price interval**.
- The existing Strategic Compass owner is **21–30D**, not 14–21D: `04_MARKET_LEARNING/handlekompas/strategic/README.md` and `STRATEGIC_COMPASS_SCORING_CONTRACT_v1_1.md`. Its checkpoints are T+7/T+14 monitoring, T+21 checkpoint, T+30 final outcome. Do not silently equate that anchor with the existing 2–3W weekly description.
- Multiweek forecasts overlap heavily. Historical CN 2–3W qualitative outcomes, strategic checkpoints and 7D numeric ranges cannot be compared through a common headline "accuracy" score without matched frozen claims and identical outcome definitions.
- The 2026-10-10 master audit does **not** establish a head-to-head economic or price-range winner for 7D versus 14–21D. The appropriate state is **INSUFFICIENT MATCHED EVIDENCE**.
- Issue **#1516 already owns** Forward Path Engine v1: checkpoints NOW, 3–7D, 8–14D, 15–21D, 22–30D; source-bound BTC/ETH scenarios, turning points, pullback depth, confirmation/invalidation, prospective freeze and outcomes. Do not clone the engine, ledger or owner.
- Issue **#1553** already owns the risk-to-action reliability gap, including the distinction between real protection warnings and governed SELL/TRIM decisions. Do not convert research into action authority.

## 3. Critical distinction: price range, path, direction, warning, utility

| Question | What should be measured | What must not substitute |
|---|---|---|
| Weekly price interval | Full realized high/low containment, breach severity, width, midpoint error, Jaccard, Winkler | High public precision / wide band alone |
| Tradable direction | Directional UP/DOWN skill against equal-horizon persistence and simple naive control, with abstentions | SIDEWAYS within broad ±5% tolerance |
| 2–3W path | Correct ordering and timing of up/retest/breakdown/repair, event-level lead-lag, false/missed turning points | A plausible narrative after the event |
| Protective warning | Emitted-before-risk, usable lead time, false-alarm count, warning severity, actionable delivery timestamp | A later risk annotation or retrospective recognition |
| Portfolio economic utility | *Same capital and risk* after real decision delay, fees/slippage, downside, upside foregone and turnover, separately for current holders and fresh cash | Forecast hit rates or hypothetical frictionless exits |
| Microcaps/memes | Asset-specific beta, liquidity, market impact and executable tradability | BTC/ETH weekly ranges or Top100 breadth as a substitute |

**A weekly band can contain the entire week's price and still say nothing about whether the high or low occurred first.** For a trim and re-entry, order, depth, time-to-trough and usable warning lead time may matter more than interval containment. Conversely, a 2–3W thesis may be directionally right but too late to protect portfolio drawdown.

## 4. Pre-registered additive challenge, to be implemented by the EXISTING #1516 / #1553 owners only

**Null H0:** Neither horizon nor their combined interpretation improves same-risk, after-cost action utility over (a) buy-and-hold for incumbents, (b) cash/wait for new capital, and (c) naive frozen price/volatility-based controls.

**H1:** Weekly has better **range sharpness / location utility** than the multiweek representation *when comparable intervals exist*. Evaluate with identical issue/freeze anchoring and score semantics; do not compare a 7D 90%-wide band to a 21D discretionary narrative.

**H2:** 14–21D improves **transition/reversal forecasting** and avoids whipsaw relative to week-only reading when the market makes sequential pullback/recovery and rotation attempts. It can also be worse because of slow response: both directions must be measured.

**H3 (hybrid):** Multiweek contextual posture + weekly price-risk map + 12–72H fresh governed permission improves *net* after-cost portfolio utility over **each** individual horizon, without additional harmful churn.

**Predeclared head-to-head arms on the SAME eligible as-of decision states**:
- B0: existing-holder passive hold; new-cash wait, separately.
- B1: simple persistence / independent frozen weekly volatility interval (use exact W41+ native forecast); no model interpretation.
- A7: frozen 5–7D Compass + risk owner, with existing action permissions.
- A21: frozen 14–21D path from #1516 only **once it actually exists prospectively**, not from rewritten legacy prose.
- A7x21: conflict-aware dual-horizon interpretation, no new live action and no assumed trade sizing.
- All arms require identical asset universe, knowledge cutoff, observation/action-delivery lag and executable costs. If a given arm cannot produce an eligible recommendation or fill, record **ABSTAIN/UNKNOWN** and keep the denominator.

**Must log immutably**:
`forecast_id, source_commit, freeze_at_utc, first_knowledge_at_utc, asset/universe, horizon_start/target, candidate_arm, available_features, directional_forecast, event_order_forecast, interval_bounds(if pre-frozen), interval_coverage, actual_high_low, width, midpoint_error, Jaccard, Winkler, upper/lower_tail_miss, MAE/MFE, reversal_time_error, warning_emitted_at, delivered_at, first_executable_at, regime, abstention, missingness, baseline_id, outcome_due, outcome_hash, cost_model_version, incumbent_vs_cash_cohort`.

Existing forward-only files and source owners take precedence; **do not create these as a competing live schema**. This is a research field checklist/owner handover only. When actual fields are unavailable, use UNKNOWN rather than invented values.

## 5. Experiment discipline, stop conditions and compounding loop

1. **Admit only source-time-valid rows.** Input `knowledge_time <= forecast_freeze_time`; prohibit retrospective inferences, same-week realized bars, repaired label leakage, unverified publication times or current completed outcome facts in a historical feature.
2. **Same observation family:** weekly/14–21D intervals should be scored on comparable UTC weekly boundaries where possible; for event tests group multiple overlapping freezes into one shock/family. BTC and ETH same week do not create two independent market-regime episodes.
3. **Prospective native 7D baseline W41+ first.** Do not retrofreeze or revise W39/W40. For 14–21D use #1516 after schema, producer, freeze and PIT admission; otherwise report `NOT_YET_TESTABLE`.
4. **Separate three outcomes:** range calibration, direction/path discrimination and economically realizable decision benefit. A gain in one does not prove the others.
5. **Abstention is an output.** Report coverage, proportion of UP/DOWN versus SIDEWAYS/NO_EDGE and selection bias. High classification accuracy from 5%-tolerance SIDEWAYS cannot count as successful market turning-point recognition.
6. **Predeclare baselines and utility conventions before outcome inspection.** Same exposure limit, starting capital, tradeability, timestamp and capital state; costs include round-trip fees, slippage and market-impact sensitivity. Never assume a small/micro token is sellable at its displayed midpoint. Taxes remain a separately governed investor-specific sensitivity, not a universal invented fill.
7. **Report negatives and uncertainty.** Examine upside foregone from caution, false-positive trim/rebuy, delayed warning and gross-vs-net improvement. Distinguish statistically independent episode families, sample size and regimes. Use walk-forward or pre-registered forward experiments; parameter selection/threshold optimization requires new trial accounting.
8. **Selection guard:** freeze the primary ranking criterion as *net, drawdown-aware utility*, then secondary 7D interval Winkler/width, directional signed return/baseline lift, turning point timing and warning usefulness. Do not select a winner ex-post based on whichever statistic happened to shine.
9. **Review cadence:** evaluate matured observations through existing weekly Master Monday / CN precision learning / Strategic Compass maturity / DEL and M6 governance. No new schedule or API spend. Only material evidence changes should be escalated, after exact-lineage verification.
10. **Promotion kill-gate:** do not change official Compass until prospective, source-bound and independent comparisons demonstrate robust incremental value in more than a single favorable volatility episode, after costs and abstention sensitivity, with adversarial review and explicit owner approval. If evidence conflicts or a lane is unavailable, **NO PROMOTION** and retain the original Compass.

**Proposed research status field:** `WEEKLY_RANGE_EDGE = NOT_DEMONSTRATED`; `TWO_THREE_WEEK_DIRECTION_EDGE = NOT_ESTABLISHED`; `HYBRID_PORTFOLIO_UTILITY_EDGE = UNTESTED`. These are **research conclusions, not live output/scores**.

## 6. Owner routing / nonduplication

- **Primary owner: Archive #1516**, inject this file as its bounded source-linked horizon-utility acceptance companion. Its current work on 14–21D freezes, event checkpoints, forward path and learning is authoritative. No parallel Forward Path Engine issue and no competing ledger.
- **Scientific baseline owner: M3 / CN precision / range_baselines**. Retain M3 FINAL adjudication, historical negative evidence, W41 native-prospective benchmark, and its exact methodology semantics.
- **Decision utility + warnings: #1553 and existing Decision Economics Ledger / M6 / protective warning owners**. They own incumbent/new-cash separation, real emission/delivery/action feasibility and costs. This note does not authorize REDUCE or EXIT.
- **Research adversary: existing Research Lab route** for falsification, not automatic market promotion.
- **Master Monday** can ingest *matured, explicitly eligible outcomes*, not this unscored hypothesis as a performance improvement.

## 7. Implemented now vs pending

**Implemented now, via this additive note only:** freeze the research question, exact negative results, interpretive limitations, hypothesis and test arms, owner routing, required audit fields and no-modification boundary in the Compass research folder.

**NOT implemented or claimed:** a new interval model, #1516 Forward Path production, matched 14–21D outcome scores, after-cost portfolio backtest, new confidence, live alert, new action, site panel, weekly automation, canonical promotion or evidence of incremental alpha.

**Success criterion:** on eligible *prospective paired* independent event families, one arm yields reproducibly higher *net* risk-adjusted decision utility and lower important misses than simpler alternatives without extra false warnings/churn. Else retain original Compass unchanged and report `NO_DEMONSTRATED_EDGE`.

## Source links / read first

1. https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516
2. https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553
3. https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/06_RESEARCH_LAB/m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md
4. https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/05_CYCLE_NAVIGATOR/internal_learning/research/2026-10-10_master_audit_work_receipt_v2/EXECUTIVE_REPORT_AND_HANDOVER.md
5. https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/04_MARKET_LEARNING/handlekompas/strategic/README.md
6. https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/04_MARKET_LEARNING/handlekompas/STRATEGIC_COMPASS_SCORING_CONTRACT_v1_1.md
7. https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/05_CYCLE_NAVIGATOR/range_baselines/README.md

**No modifications to existing Compass, scores, source authorities, algorithms or portfolio actions.**
