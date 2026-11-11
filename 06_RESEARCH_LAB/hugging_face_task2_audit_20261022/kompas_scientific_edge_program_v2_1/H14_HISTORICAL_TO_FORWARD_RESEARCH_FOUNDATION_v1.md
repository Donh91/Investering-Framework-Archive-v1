# Kompas Pro H14 | historical-to-forward research foundation v1

Status: `RESEARCH_DESIGN_ONLY / NO_NEW_EVIDENCE / RELEASE_GATED`. Created 2026-11-10 under existing Task 2 issue [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), with existing Cycle Navigator #1516, risk-to-action #1553, source #1827, site #1578, CRE and S1 #1156. This document does not replace an owner, horizon registry, producer, forecast, scheduler, or authorized scientific protocol.

## Mission and non-duplication

Make all 14 Kompas Pro horizons progressively *testable*, not necessarily numerically forecastable. The canonical inventory is `07_PROMPTS_AND_AGENTS/action_compass/KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json`; public display contract is `05_CYCLE_NAVIGATOR/site/premium-v2/kompas-horizon-status.mjs`. The adjacent `H14_EXPERIMENT_CROSSWALK_v1.json` is a **read-only research experiment map**, never a second issuance registry. Existing approved Task 2 v2.1 program, CRE Stage 1 and Research Parallel Lanes remain the only owners/execution paths.

The criterion for success is *incremental, source-legal, later verified decision quality over the simplest same-clock alternative*, with honest abstentions, costs, failures, and uncertainty. More horizon rows or closer historical fit are not success. No source-backed numerical claim may be invented to fill a missing public horizon.

## Evidence atlas: read before new experiments

| Original evidence | Verified lesson / constraint | Application |
|---|---|---|
| `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/TASK2_RPL8_WAVE4_CN_W44_POSTFREEZE_WIDTH_PAIRED_20261107.md` and PR #2002 | W44 original CN bounds contained both BTC and ETH extrema while narrower, independent B1 had larger Jaccard; one market week, not two independent cohorts | Joint extrema coverage **and** sharpness/width, quote and original issuance clocks |
| `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/IRONFLOW_FULL18M_EMBARGO_CORRECTED_SCIENCE_V2_20261107.md` | 1,074 eligible historical asset-days, mean equal-month Brier lift -0.001710, CI overlaps zero after 25h label embargo; 2026-02-12 OI gap and next-day lookback censoring | Derivatives are a candidate, not a default model improvement; archive missingness and undercalibration |
| `06_RESEARCH_LAB/compass_research_engine_v1/PREREGISTRATION.md` and `CRE_NEXT12H_PROSPECTIVE_PROTOCOL_v1.json` | NEXT_12H hypothesis versus same-clock momentum persistence exists, admission/authentic first-known receipt still gated | Never score an observed momentum NOW as an original 12h future forecast |
| `06_RESEARCH_LAB/shared_row_model_tournament_v1/` | Same-row baseline competition, selection, negative controls, multiplicity and release gates | Avoid comparing models on different admissible populations |
| `06_RESEARCH_LAB/historical_altseason_pullback_v1/` and `06_RESEARCH_LAB/m6_methods/2026-10-05__gap-sensitive-episode-power-method-v1.md` | Sparse event families and 2022-24 gap; drawdown episode powers require 7/14/30-day clustering sensitivity | Long-cycle and risk research cannot pretend many correlated rows are independent cycles |
| `05_CYCLE_NAVIGATOR/weekly/2026/W46/` | Same-Monday owner-approved revision issued 2026-11-09 10:52:34Z, 7 original daily closes and ranges per BTC/ETH; first eligible score 11:00Z | Preserve first issue, amendment lineage, score only post-cutoff actual observations; 7 daily closes need their own future scoring |
| Bridge `reports/claude/automated/2026/11/CLAUDE-AUDIT-04a-20261110T041336Z.md` on `claude/log` | Price-only warning recall sensitive to asymmetric crash miss costs; no universal winner across k | Freeze risk miss-cost grid before new outcome tests |
| Bridge `reports/claude/automated/2026/11/CLAUDE-AUDIT-04b-20261110T051442Z.md` on `claude/log` | 33 healthy official packets Oct 4-9 held BUILDING while in-packet breadth fell 0.83→0.08; risk driver weekly-only, 6 of 8 degraded packets in stale midday slot | Shadow-only *risk-state stall* forensic with negative-control quiet periods, plus upstream freshness investigation |
| Bridge `reports/claude/automated/2026/11/CLAUDE-AUDIT-03b-20261110T021333Z.md` on `claude/log` | 7 daily closes have no independently completed scorer, legacy fallback risks moving scoring window | P0 research accounting gap: score day-level close accuracy separately, with original freeze and UTC target |

Bridge files are advisory, not independent live authorization. Recheck exact branch/commit/date and native owner PR before changing code. Claude's suggested breadth <=0.15 threshold was selected after examining the Oct episode and is **exposed exploratory shadow only**, not prospective action or threshold authority.

## Research time-machine protocol

1. **Define the event before outcomes.** One original `issued_at_utc`, target start/end, instrument, quote, venue, model code/version, source raw first-known, delivery clock, authority class, and immutable original blob/hash. Record all first-issued, amended, suppressed, unavailable, invalid, and abstained attempts. Never select a later favorable attempt.
2. **Three separate time domains:** `source_event_time` is not `provider_first_known_time`, which is not `collector_received_time`, which is not `public_issued_at`, which is not `user_received_at`. Original market tape may be known after its timestamp. `source_window_end_utc` is a collector batch window, not individual candle close; use canonical `timestamp_utc + 1h` for completed hourly bar end where that contract applies.
3. **Admissibility ladder:** `ARCHIVAL_OUTCOME_TRUTH`, `RECONSTRUCTED_DEVELOPMENT`, `ORIGINAL_ISSUED_CLOCK_ONLY`, `SOURCE_PIT_ADMITTED`, `DELIVERY_PIT_ADMITTED`, `MATURED_MATCHED_PAIR`, `QUALIFIED_FORWARD_TEST`. Missing custody stops advancement but does not erase useful descriptive negatives. Exposed historical fitting cannot certify genuine prospective edge.
4. **Original-vs-retro firewall:** never represent a retrospectively recreated signal as an issued 2021-2026 market prediction. The first independently immutable pre-outcome forecast and future prospectively captured source must anchor any forward validation.
5. **Cohort cardinality:** report N issued, N abstained/unavailable, N PIT-admitted, N matured, N baseline paired, N independent days/weeks/episodes, N source gaps, and N delivered. BTC+ETH on one crisis day are not two independent shocks. Cluster by calendar block and market episode, purging overlapping target labels from training and respecting true label maturity.
6. **Privacy and usage:** public archives are not a substitute for private source values. `Donh91/secrets` stays private with Round 3 `PROSPECTIVE_COLLECTION_ONLY` and analysis/scoring `OFF`; raw or normalized restricted values never go to public GitHub, connected web research, reports, prompt bodies or model input. If private authority is needed, return `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`. No new paid datasets or model calls by this document.

## Independent questions, not 14 model clones

Use Research Parallel Lanes in 6-8 bounded investigations: (A) original issuance/consumer time; (B) same-clock BTC nowcast and 12h falsification; (C) 24h to 7d original price and interval skill, including per-day W46; (D) 8-56d exploratory forward baseline and abstention power; (E) 1-12m cycle/regime and independent episode inventory; (F) pullback/SELL false negatives versus quiet controls, including crash miss-cost and delivery; (G) indicator ablations and simplicity; (H) UI provenance and missingness. Parallelize actual read-only jobs only where independent. Their hypotheses and falsifiers are in the existing Task 2 program and the companion crosswalk.

### Baselines, fixed before reading test outcomes

- Direction: last eligible price trend/persistence, class prevalence, always-UP/DOWN, no-edge/abstain, and official last-packet stance. On a new dataset do not choose whichever naive variant lost after seeing scores.
- Levels/terminal close: last qualified close, driftless random walk, source-legal volatility-scaled intervals, frozen original CN and independently first-known B1 (if same target/quote). Do not reinterpolate W46 weekly bounds into daily issued prices.
- Risk: no-warning/HOLD, price+vol-only, ordinal official risk as-issued, source-admitted shadow. Include missed drawdowns, late warnings, false alarms and quiet periods; predeclare miss-cost k, never optimise it from crash history.
- Economic decision: hypothetical HOLD, do-nothing, and source-legal entry/trim/re-entry with decision time, latency, fees, spread, slippage, funding/carry and missed upside. No wallet-specific investment directive, no real trades.

### Scoring is horizon and target specific

For terminal close report MAE, scaled absolute error, directional accuracy **versus matched baselines**, median error and paired uncertainty. For original probability forecasts only, Brier/log score, calibration and proper scores; never convert `7/10 evidence` to 70% probability. For terminal price intervals use eligible per-target coverage, width and proper interval score with declared quantiles. For weekly high/low extrema show containment, excursion distance, width ratio and overlap/Jaccard **separately**; do not fabricate an independently probabilistic joint Winkler score. For risk warnings report early/late detection, false positive rate, missed-event rate, lead time, area under precision-recall when meaningful, and k-sensitive decision loss. Report missingness and no-issue denominators alongside every result.

## Four milestones, within existing owners

- **M0 evidence census:** check all 14 canonical horizon IDs, original issue vs observed vs shadow, first-known, target maturity, result owner, source and missingness. The H14 crosswalk is *coverage metadata*, not a newly published signal. First identified operational gap is independent W46 7-daily-close scoring, separate from interval scoring.
- **M1 executed retrospective controls:** reproduce Task2 #2002, 12h CRE null baseline, corrected Ironflow negative, Claude risk-stall chronology, prior CN score, matched quiet controls. One hypothesis per lane with immutable anchors. Never recycle prior N as new tests.
- **M2 forward-only development:** owner-approved preregistration, stable delivery/first-known clocks, source/quote integrity, native immutable forecast release, proper due-outcome scoring with embargo. Each horizon activates only with its own qualified first-known producer and sufficient independent sample.
- **M3 promotion review:** independent prospective holdout, negative controls, out-of-regime and family uncertainty, measured economic utility and owner security/release gates. Canonical producer remains unchanged unless a separate reviewed original owner PR is genuinely merged and read back from main and natural consumers.

## Repeatable existing-cadence research, not a new scheduler

- Existing **CRE Shadow Lab** can inspect one due/matured H14 hypothesis or gap per its existing due tick, only if its saved instruction and owner scope permit. Never claim that this document updates the ChatGPT automation.
- Existing **S2 Master Monday/CN** remains the natural frozen weekly issuer; it should create no extra forecasts for research. The next due close may be scored only after genuine maturity.
- Existing **S1 hourly** may process a fully qualified original Task2/CN/CRE remediation PR, respecting max 3 PR, Monday lock, exact-head review, safety/custody and main consumer readback. S1 does not become a research/model issuer.
- Use existing Task2 #1596 / source #1827 / risk #1553 / CN #1516 / site #1578 / CRE domain homes for evidence and ownership. No new PR per speculative idea, no new task, agent, API route, workflow, secret or recurring paid job.
- Process new reports by **material delta**: original source or hash changed; first-known became eligible; a horizon matured; new falsification; source gap repaired; a reviewed PR merged. If no new material input, record `NO_NEW_EVIDENCE` and do not rescore.

## Deep Research handoff

See `H14_CHATGPT_DEEP_RESEARCH_BRIEF_v1.md` for a copy/paste prompt to run **ChatGPT Deep Research in the same user conversation**, with GitHub files and cross-reference audit. Its returned report is research input only. The user-facing synthesis and any code/policy edits continue through original Task2 owner and governed GitHub PRs, never through unverified model-written "completed" claims.

**Definition of done for this foundation:** reviewable branch + PR with the crosswalk and reference playbook, valid 14-ID coverage, no canonical signal changes. **Not done:** complete archive inventory, prospective PIT admission, valid long-horizon forecasts, deployment, scheduler change, or measured predictive edge.