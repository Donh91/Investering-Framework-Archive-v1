# Legacy-to-Automated Kompas — Cross-Archive Evidence Audit v1

**Date:** 2026-10-10
**Authority:** RESEARCH_ONLY_NON_CANONICAL
**Scope:** Pre-automation DATA PING V1–V8, archived Cycle Navigator and Master Monday March–August 2026, Grok/X, CFGI, Claude/Research Lab, historical replay, and comparison with the 2026 W37–W40 four-settlement checkpoint.
**Status:** SOURCE-BOUND RESEARCH SYNTHESIS / INCOMPLETE GLOBAL EVENT CENSUS
**No effect:** Market rules, weights, official Compass freezes, published scores, portfolio permissions, execution, and historical score rewrites.

## 1. Critical distinction: archive size vs evaluable forecasts

The archive contains substantial historical material. This is not equivalent to having an uninterrupted, event-level frozen-forecast/evidence/outcome join for every period.

- **Current project-file surface (2026-10-10):** enumerated **126 available Project files**, of which **65** have `DATA PING` in their filename (counting the "Tiltag og updates fra DATA PING" note), and **87** matching DATA PING / CoinGecko / Grok / Research / CN-related document records were batch-read at the available extracted-text level (~375k characters returned). Many share the same filename but have distinct file IDs/content; a local last-file-named `DATA PING_V2.txt` is NOT a substitute for the other uploaded files. One large update document reported partial/full-text fallback warning, so this is not a complete line-level census of every word or every source. These Project records are not automatically canonical GitHub observations; a deduplicated provenance/forecast-time crosswalk remains required. The older 44-source ZIP is a separate, narrower ingest cohort.
- Legacy archive ingest: **44 unique sources**, **39 core or semi-good context sources**, five hash-only, with **24 extracted research-context claims**. Owner: `04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/intake/2026-08-04/SOURCE_PACK_INGESTION_SUMMARY.md`, exact machine observations at `.../LEGACY_KNOWLEDGE_EXTRACT.jsonl`. Context-only, not prospective scored hits. Source thread registry: `04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/SOURCE_THREAD_REGISTRY.json`; full pre-GitHub conversation census remains explicitly partial, not complete.
- Original/recovered published CN posts exist back to **CN #1 dated 2026-03-30**, e.g. `canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/`. March–June legacy MM register identifies reconstructed rows and gaps at May 4 and June 1; reconstructed is not equivalent to original raw MM.
- `canonical-project-archive/06_CYCLE_NAVIGATOR/archive_manifests/cycle_navigator_forecast_actual_rows_sourcebacked_v0_2.csv` has **9 recovered source-backed/partial rows** (CN #1–8 plus MM W28), not a complete CN history. Draft memory rows must not be scored.
- Weekly actuals `canonical-project-archive/03_FORECAST_LEDGER/VERIFIED_WEEKLY_RANGES_2026_Q2.md` and `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_actuals_reconciliation_report_v0_1.md` include variant-vs-final decisions. W23/W27 source-basis variants must not be spliced to maximize scores.
- Modern internal four-settlement `05_CYCLE_NAVIGATOR/internal_learning/checkpoints/2026/W40_C001.json` spans only completed W37–W40; it must not substitute for legacy archaeology or be averaged with old score methodologies.
- A 65-week BTC envelope/ATR audit (`05_CYCLE_NAVIGATOR/calibration/2026-07-08__cn-rd-audit-regime-phase-range-calibration__canonical.md`) is a **historical benchmark experiment, not 65 independently published Cycle Navigator forecasts**.

## 2. Fresh direct archival comparisons worth admitting to the next retrospective challenge

### Case L1 — CN #9, published May 25, 2026

Original archived publication:
`canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_009_PUBLISHED_X_POST_2026-05-25.md`

Forecast for May 25–31:
- BTC **$80,000–$88,000**
- ETH **$2,350–$2,750**
- Market framing BTC-led strength, narrow broader participation, no confirmed broad rotation, hard wait for microcaps.

Archived W22 actual candidate from `canonical-project-archive/06_CYCLE_NAVIGATOR/archive_manifests/cycle_navigator_memory_seed_forecast_actual_manifest_v0_1.md` and the reconciliation report:
- BTC low/high **$72,785.65 / $77,664.65** (Yahoo source-basis variant also stays below BTC $80k).
- ETH low/high **$1,974.80 / $2,134.24**.

**Research finding:** BOTH reported weekly actual ranges lie completely below the published weekly bands; BTC actual high is ~$2,335 below forecast low, ETH actual high ~$216 below forecast low. The market-structure/no-rotation call is a separate matter and may be correct; do not let that high-level call conceal directional/range placement misses. **Evidence qualification:** W22 actuals are archived as user-verified/memory-derived, not a newly independently fetched same-basis final venue record. Treat this as **PROVISIONAL HISTORICAL RANGE MISS**, pending source-time convention reconciliation, not an automatic public rescore.

### Case L2 — CN #13, published June 22; evaluated by CN #14

`canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_013_PUBLISHED_X_POST_2026-06-22.md`
`canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_014_PUBLISHED_X_POST_2026-06-29.md`

CN #13 forecast BTC **$62.8–67.2k** / ETH **$1.67–1.84k** for June 22–28. The subsequent published CN #14 evaluation reports:
- BTC realized **$58.1–65.5k**, reported weekly BTC score **45%**.
- ETH realized **$1.51–1.78k**, reported weekly ETH score **48%**.
- Overall published retrospective precision **68%** with structural/rotation labels substantially higher.

**Finding:** The defensive/regime thesis apparently survived while projected downside magnitude and timing missed materially. The combined public "overall" hides the failure cost for users relying on downside warnings. Preserve old published numbers as-is; never recompute them under newer methodology.

### Case L3 — Unchanged price map across CN #13 → CN #14 after a downside miss

The **current-week market outlook and day 1–2 / 3–4 / 5–7 BTC and ETH ranges** in archived CN #14 June 29 post reproduce CN #13 June 22 text, including BTC $62.8–67.2k and ETH $1.67–1.84k, despite the CN #14 introduction documenting the prior downside miss.

Compare CN #14's June 29–July 5 window to archived W27 actuals in the reconciliation report:
- BTC **$57,778.72–$63,403.77** (CoinGecko/Yahoo user-verified basis), below the repeated $62.8k lower boundary.
- ETH **$1,549.83–$1,802.38**, below the repeated $1.67k lower boundary.

**New hypothesis:** Legacy weekly forecast template/carry-forward inertia after an adverse regime move. This is **a source-backed candidate** for lack of forecast adaptation; it is not proof of a software defect or of a specific cause. A targeted audit should check content provenance, issue date/freeze timestamps and deliberate-versus-unintentional carry-forward before assigning fault or scores.

### Case L4 — Cross-era direction asymmetry

In early summer the actual downside often ran below optimistic price corridors while public regime/alt-rotation remained conservative. In automated W40 the internal scorecard reports the inverse: **BTC advanced +2.44%**, but the frozen "volatile consolidation/retest" regime narrative underweighted the upside path (regime family 50); 2–asset weekly price corridors contained the actual extrema.

**Provisional generalization:** Not a stable one-direction bullish or bearish bias. The more consistent research target is **path shape, timely adaptation and the separation of regime category from position/range decisions**. Cannot infer causation from these selected windows.

## 3. Historic research with actual negative results — DO NOT ERASE

- `04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md`: 21 BTC.D B1 fires, ten-day median BTC return **+2.7401%**; tested mechanical protective trims lagged buy-and-hold terminal returns. BTC.D B1 early-warning weight frozen at zero. M4 `FALLING_EXPANDING_NO_RECENT_RECLAIM` event cohort **18** episodes: 7d median ETH/BTC **−1.4129%**, 14d **−3.3583%**, 30d **−7.9761%**. Historical signal label is not an automatic deploy permission.
- `04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/results/chatgpt_wave1_1_2026-07-28/WAVE1_1_REPORT.md`: 48 H7-like events, beta-neutral alt 5d median **−1.34%** and 30d **−9.44%**; linear purged BTC 5d directional prediction near chance with no reliable incremental ETF predictive lift; final holdout excluded. All research-only.
- `05_CYCLE_NAVIGATOR/calibration/2026-07-08__cn-rd-audit-regime-phase-range-calibration__canonical.md`: 65-week quantile/envelope mean Jaccard **0.298**, DUMB2.0 **0.496**, DUMB1.5 **0.530**; envelope lost DUMB2.0 in **55/65**. This is a baseline research result, NOT a score of published CN forecasts.
- `06_RESEARCH_LAB/m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md`: **general incremental CN range alpha over mechanical volatility baselines not demonstrated**. Its W39–W40 small sample contains realized extrema but usual CN bands are wider; public 70%-containment + 30%-Jaccard score is accountability, not alpha. An independent native prospective benchmark begins W41.
- `06_RESEARCH_LAB/m2_checkpoints/2026-10-05__RL-OFFENSIVE-FNP-002__FINAL_ADJUDICATION_v1.md`: prospective FNP economic measurement remains insufficient; strong claim of systematic over-defensiveness NOT supported; opposite optimal-defense claim also NOT supported. Historical FNP-001 is **quarantined from quantitative policy replay** due to lineage problems, superseding stronger June narrative that called it verified economic proof.

## 4. CFGI, source inventory vs actual predictive evidence

- Historic `06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/CFGI_COVERAGE.json` shows vendor-reported API coverage from March **2022** through August 2026 for MARKET/BTC/ETH and 15m, 1h, 4h, 1d. **These are provider coverage metadata, NOT proof that the whole vendor time series has been captured and preserved as owned raw rows.** No CFGI history is imputed for 2021.
- `06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/BACKTEST_SUMMARY.json`: **46** objectively labeled pullback episodes and **25,506** free hourly feature rows in historical lab; CFGI enrichment **PENDING_TARGETED_ENRICHMENT** and machine-realistic trim/reload **NOT_TRAINED_YET**. Episode labels are outcomes, NOT 46 proven prediction successes.
- `03_DAILY_CAPTURE_LOGS/cfgi_weekly/2026/W36...W39/WEEKLY_CFGI_DERIVED_SUMMARY.json`: W36 42 captures (MARKET score 30→55), W37 42 (49.5→45), W38 42 (51.5→66), W39 41 (**68→38.5**, BTC 68.5→36.5, ETH 68.5→32.5). W40 current derived summary marked `SOURCE_UNAVAILABLE`/zero captures. Do not infer the data are absent from all other owners, only that this summarized lane has no rows.
- `04_MARKET_LEARNING/cfgi/2026-09-21__cfgi-september-2026-monthly-report-deep-dive.md`: Sept 21 running-month snapshot: market composite average ~56, Technical 65 versus Social 47, Trends 42, Whales 41, Orders 49. **Hypothesis:** technical-versus-participation component dispersion can warn of fragile moves, and the subsequent W39 weekly score deterioration is a promising event study. Do **not** infer a proven leading indicator from monthly snapshot and later weekly endpoint without exact timestamps/price controls.
- `research/data_architecture/CFGI_SIGNAL_VALUE_SCORECARD_v1.md`: component lift requires controls and matured observations, not collection volume alone.

## 5. Grok, TechDev, Claude and Situation Room

- Grok-assisted recovery of original CN #1–#14 public text/score sections is valuable for **provenance and historical reconstruction**. Grok is NOT independently reliable as score owner: `04_MARKET_LEARNING/shadow_sources/2026-07-12__grok-execution-quality-and-framework-evolution-audits__shadow-assessment.md` caught impossible CN #15 score chronology, incorrect ETF flow approximations, incompatible OI and BTC.D source universes. Accept source-backed linked posts, not Grok-generated "overall accuracy."
- `06_RESEARCH_LAB/shadow_layer_historical_effectiveness_v1/01_EXECUTIVE_VERDICT.md` and `04_HISTORICAL_EFFECTIVENESS_FINDINGS.md`: strongest recurring information families are ETH/BTC persistence, breadth survival, BTC.D path, ETF absorption versus ecosystem transmission, leverage/liquidation/reclaim quality, sequence survival and FNP. Old Fake Rotation Type 3 55–75% failure, pre-trigger reliability and microcap failure-rate claims are not reproduced. Large correlated composites require incremental-value tests.
- `06_RESEARCH_LAB/historical_sensor_recovery_v1/validation_v1/08_DATA_GAPS_AND_UNTESTABLE.md`: April/May exact sensor definitions survived better than contemporaneous high-quality state rows. A modern reconstructed signal must not masquerade as what the old framework knew then.
- Historical TechDev is useful as macro/shadow challenge but its timing/after-the-fact revision cannot create forecast points. `06_RESEARCH_LAB/audit_summaries/2026-07-13__techdev-category-outcome-calibration-and-b1-reconciliation-v1__canonical.md`.
- Situation Room `04_MARKET_LEARNING/external_research/situation_room_shadow/README.md`: source is discovery only and needs independent primary corroboration before eligible shadow use. It cannot be retrospectively promoted to source authority in older DATA PING.

## 6. What the next research checkpoint must actually do

**Do not create another independent data owner or broad research engine.** Extend the existing CN precision learning, M3 baseline, Historical Sensor Recovery, historical pullback lab and FNP owners.

P0-A **Legacy issue-level forensic reconciliation:** audit CN #9, #11–#14 (then #1–#8) as (source issuance timestamp, fixed horizon, actual price convention, realized interval, public self-score versus objectively re-evaluable parameter), including explicit regime-direction/timing/downside/rotation mismatch types. Prioritize confirmation of the #13→#14 cloned forecast text and issue date.
P0-B **Historical DATA PING point-in-time crosswalk:** enumerate genuinely attached/archived v1–v8 source files and machine rows by timestamp. Freeze source family and instrument basis. Bucket `CONTEMPORANEOUS_FROZEN`, `OBSERVATION_NOT_FORECAST`, `RECONSTRUCTED`, `SOURCE_ONLY_HASH`, `UNTESTABLE`. Recover decision-time and actual-time joins; never count per-ping overlapping observations as independent episodes.
P0-C **CFGI and context event study:** W36–W39 component and 24h/72h price alignment, dated late Sept shock, matched non-event continuation controls, negative controls, contribution of CFGI components beyond ETH/BTC, breadth and ETF. Expand June 2026 flush where archived provider rows truly exist. Annotate verified Situation Room catalyst times only.
P1-D **Cost of delayed confirmation:** use M2/T2 actual decision divergence owner once non-zero rows and matured outcomes exist; do not revive quarantined FNP-001 percentage claims.
P1-E **Forecast-skill baselines:** compare historic and current issue cohorts only within method eras, with contemporaneously available naive bands; add missed-tail severity and turning-point reaction latency rather than headline public precision alone.
P2-F **Grok and Claude reliability:** tag external statements as primary-source locator, source-bound raw value, qualitative hypothesis or invalid/conflicted measurement; verify source/time/universe before inclusion.

**Success measure:** evidence-graded dated comparison rows with a falsifiable answer to whether Kompas detects genuine direction changes and alpha/capital transmission early enough to improve risk-adjusted action. **Not success:** more named indicators, more pages of qualitative agreement, public score inflation, or retrospective tuning.

## 7. Evidence boundary / QA

This is a targeted audit spanning principal existing archival and modern research owners. It is **NOT** a complete line-by-line re-evaluation of every Data Ping thread, uploaded transcript, or every historical prediction. Some original raw chat threads remain unexported or incomplete by the legacy coverage receipt. Numerical results above belong to distinct samples, owners, scoring conventions and selection designs and MUST NOT be combined into a synthetic whole-framework hit rate. Older high self-reported public scores do not establish economic edge. A new prospective test or score adjustment requires independent governance.