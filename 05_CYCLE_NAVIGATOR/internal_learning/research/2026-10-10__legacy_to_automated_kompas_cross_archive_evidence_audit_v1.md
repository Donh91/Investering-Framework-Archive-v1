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


---

## 8. 2026-10-10 PRE-AUDIT ADDENDUM: Auto Trading, first-era DATA PING and cross-owner contradictions

**Status:** AUDIT_PREPARATION / RESEARCH_ONLY. This section supplements the original cross-archive map, not a completed scientific audit. Do not declare whole-history coverage or reuse the same samples as independent corroboration.

### 8.1 Quantified high-value archives ALREADY PRESENT — don't pay to reacquire

| Cohort / exact owner | Count / span | Permitted research value | Must-not-assume |
|---|---|---|---|
| Historical hourly alt-market panel, private \`raw/HISTORICAL_ALTSEASON_FREE_HOURLY_PANEL_V1/2026/08/21/\` indexed via \`04_RESEARCH_LAB/auto_trading/maeve/CFGI_MAEVE_DATA_INVENTORY_V1.json\` and \`.../audit_summaries/2026-09-14__historical-market-archive-reconciliation-closure-v1.json\` | **851,882** source-linked hourly rows, **35** symbols, **2020-09-01 to 2026-07-31** | Large no-lookahead alt breadth/dispersion/volume/flow + negative-control panel. Single independent 24-hour SOLUSDT overlap checked with exact matching sampled fields; source-level raw admitted under declared coverage | Exact historical Top-100; survivorship-free membership; all derived fields valid; 851,882 independent episodes |
| MAEVE/CFGI private action ledger \`raw/MAEVE_PUBLIC_LEDGER_RECOVERY_V1/2026/09/09/\` | **432** positions (426 closed), **1,073** fills, **641** DCA legs, **318** matched posts | DCA vs first entry, no-trade matched controls, capital-weighted and fill-level timing; behavioural feature ablation | 93.19% position win = entry accuracy; full later public 1,427-position history recovered; private signals known |
| Private CFGI historical targeted 1h stage \`raw/CFGI_HISTORICAL_1H_EVENT_STAGE_V1/2026/08/21/\` | **478** historic BTC/ETH rows, **2025-01-03 to 2025-02-09** target windows; companion **25,506** hourly free features | Historic event-time stress and reversal interaction; leakage-adjudicated source timestamp joins | Continuous full-asset CFGI; MARKET coverage in these exact windows (zero provider rows, terminal) |
| Private CFGI PDLT bootstrap \`raw/CFGI_PDLT_HISTORICAL_BOOTSTRAP_V1/2026/08/07/\` | **1,230** observations / ~15-minute capture intervals of native **4h/1d** state | Timestamped intrastate change, regime transition, component divergence | Native 15-minute indicator series; historical breadth beyond its recorded window |
| Historical altseason lab \`06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/\` | **46** objectively labeled pullback episodes and **25,506** free hourly feature rows | Matched pullback-vs-continuation controls and severity/timing, with 2020–21 and 2025–26 source split | 46 earlier successful predictions; survivorship-free alt universe; ready-to-trade trim/reload policy |
| BlockHorizon private raw archive \`raw/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/\` | Complete private raw acquisition per Sept 14 archive-reconciliation receipt; *source-overlap equivalence not yet established* | Specific historical comparison only after same-vintage and universe join audit | A fully source-reconciled backtest owner or reason for duplicate repull |
| Existing weekly DATA PING/CN/RAW originals, legacy \`canonical-project-archive\` and new \`03_DAILY_CAPTURE_LOGS\` owners | Original CN posts begin Mar 30, 2026; modern forward ledger and hourly/weekly outcomes have separate owner contracts | Historical forecast-as-issued vs actuals, version transition and structured action-vs-risk reconstruction | Legacy public self-scores directly comparable with modern 70% containment + 30% Jaccard |

**Storage / ethics:** raw licensed, paid or restricted evidence stays in \`Donh91/secrets\`, in an approved artifact, or in its source-native location; public control plane records only pointers, sample counts, hashes, schemas, research verdicts. No wallets, credentials, provider raw exports, paid report bodies or user-private holdings in this report. Historical panel's bounded independent overlap check does not prove full-panel market-universe or derived-feature accuracy.

### 8.2 Oldest ChatGPT DATA PING conversations: genuine unresolved archival population

The current ChatGPT Investering project-file surface exposed **126 file records**, including **65 DATA PING-labelled files** (many have identical filenames but different attached file IDs). A targeted prior pass read **87 relevant Project-file records** (some partially through extracted-text fallback). These are valuable **documents and conversation-derived notes**, not necessarily raw frozen market packets.

The prior GitHub import of **44** unique sources is a different, narrower cohort. \`04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/SOURCE_COVERAGE_STATUS_20260804.md\` and \`SOURCE_THREAD_REGISTRY.json\` explicitly state that the original ChatGPT **conversation-thread census is PARTIAL**. Do not confuse accessible Project files with full direct access to every early chat transcript.

Unverified leads may be identified from prior-conversation summaries (e.g. March/April separate CFGI and Crypto State test runs, day/night DATA PING, Grok readbacks), but original message timestamps, prompt, output, availability at time and immutable proof must be recovered before a scientific forecast row is admitted. Do not manufacture 2026-03/04 historical predictions from later recollections or backfill with a reconstructed modern model state.

**Required census fields**: \`source_system\`, \`original_chat_or_file_identity\`, \`source_hash\`, \`original_message_or_issue_timestamp\`, \`retrieved_timestamp\`, \`claim_type\`, \`forecast_issued_at\`, \`forecast_horizon\`, \`freeze_proof\`, \`sensor_observed_at\`, \`sensor_first_knowable_at\`, \`provider_universe\`, \`unit\`, \`actual_source\`, \`actual_settlement\`, \`source_quality\`, \`is_duplicate\`, \`is_superseded\`, \`eligible_to_score\`, \`UNTESTABLE_reason\`. Stable IDs distinguish different "DATA PING_V2.txt" attachments.

### 8.3 Confirmed temporal-integrity / vintage research risks

Existing owner:
\`04_RESEARCH_LAB/auto_trading/experiments/E1X/TEMPORAL_INTEGRITY_AUDIT_REPORT.md\`.
Its planted-leak controls **14/14** passed. Actual owner probes documented:
- PDLT research discovery labels referenced a still-unclosed candle; label-time right truncation missed the defect. Use legally knowable completed-candle anchor.
- An AT-E3 candidate anchored CFGI-derived features to event time although first capture came **72–879 seconds later**. Negative candidate ruling stands; future entry features must use capture time.
- Copper/Gold historical signal events could appear before retrospective source publication time; historical signal summaries need knowledge-time reconciliation.
- ETF session-close feature claims could anticipate real publication by hours. In separate source-vintage audit, \`research/etf_temporal_integrity/2026-09-23/ETF_TEMPORAL_INTEGRITY_REPORT.md\` observed **39 revision events in 35 sessions**, including **two sign flips**. These counts belong to that exact multi-vintage observed cohort and are NOT universal ETF revision rates.
- Pre-remediation hourly derived return/OI features changed on a subset of persisted rows (E1X vintage probe **168/1086**, 15.5% on that probe). The bounded persistence defect was **remediated** under #941/AT-EXP-004; **source-level spot rows passed independent overlap check**, while affected **pre-fix derived history stays quarantined** for retrospectively scored alpha. Do not propagate "all DATA PING history corrupt" or "everything repaired retroactively."
- \`06_RESEARCH_LAB/m4_checkpoints/2026-10-05__RL-AUTOTRADING-EVIDENCE-004__FINAL_ADJUDICATION_v1.md\` rules the evidence machine PARTIALLY_READY, broad autonomous hypothesis search NOT_READY, and local attempt tracking real but global cross-family proposal denominator incomplete (owner issue **#1557**).

### 8.4 Important older research claims that conflict with newer evidence

1. **"June 2026 ETF outflows gave best early warning"** appears in old \`DATA PING_V2.txt\` research prose. Modern Research Lab M1 \`06_RESEARCH_LAB/2026-10-06__M1-M6_EVIDENCE_IMPACT_REGISTER_v1.md\` rejects the much stronger claim that ETF persistence has demonstrated independent decision edge. **Resolution required:** distinguish one retrospectively narrated June event from a multi-event first-knowable-time, price/breadth-matched incremental lift test. Do not silently keep both as established truth.
2. **"Defensive false-altseason calls prove profitable edge"**: some old archive identifies this as verified defensive behavior; M2 \`06_RESEARCH_LAB/m2_checkpoints/2026-10-05__RL-OFFENSIVE-FNP-002__FINAL_ADJUDICATION_v1.md\` explicitly **quarantines** FNP-001 as quantitative counterfactual evidence. Structural non-confirmation is not proven capital alpha; missed-upside and drawdown-avoided remain UNKNOWN.
3. **"CFGI stress is leading" vs "CFGI merely confirms after price/flows"** occur across case studies. Resolve with original time-stamped CFGI component updates versus first legal price/flow deterioration, plus matched non-event controls. \`W36–W39\` weekly derived summaries support event selection only, not lead-time demonstration.
4. **"CN public precision proves forecast edge"**: M3 rejects this as established, because high containment can result from wide bands and mechanical ATR controls perform competitively. Never call public displayed scores economic skill.
5. **"Signal family count = independent confirmation count"**: ETHBTC, BTC.D, breadth, TOTAL3, alt index and CFGI dominance may be partially dependent; use conditional ablation/mutual information and owner universe mapping before weighting.

### 8.5 Cross-owner failure example: Oct 6–8, 2026 (already owned; DO NOT DUPLICATE)

Issue **#1553** is the existing P0 Compass Risk-to-Action Reliability Mission. Directly fetched immutable official Compass target files:
- \`04_MARKET_LEARNING/handlekompas/official/daily/2026/10/06/CMP-20261006-627e461586fd.json\`: issued 14:37Z, official regime BULLISH/action HOLD_WAIT, protection BUILDING, SELL UNAVAILABLE.
- \`.../2026/10/07/CMP-20261007-38128ce3656b.json\`: issued 20:09Z, official NOW MIXED/action HOLD_WAIT, protection still BUILDING ordinary retest, SELL UNAVAILABLE; no documented eligible risk escalation in this packet.
- \`.../2026/10/08/CMP-20261008-59260dc1ace8.json\`: issued 13:33Z, data DEGRADED, direction UNAVAILABLE, SELL UNAVAILABLE.
- Latest \`research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json\` read Oct 10: **150 eligible typed rows**, **zero eligible warning series** for its exact denominator. Sept warning event ledger lists 12 events in one provisional family; not 12 independent successes.

This is **direct evidence of output semantics**; the proof of whether a prior P0 source warned earlier, why it did/didn't propagate, downstream delivery and actual eligible alternative action requires #1553's source-to-consumer timeline. No retrospective causal conclusion and NO free-standing automatic SELL logic. Read existing issue, don't recreate its action/notification/portfolio work.

### 8.6 New audit hypothesis shortlist — rank for incremental decision value

**A / HIGH — Original as-was prediction versus reality with action/reliability split.**
Historical DATA PING + published CN + legacy RAW/MM -> eligible immutable decision snapshots -> 12h/24h/72h/7d/14d/30d matured outcomes (only originally forecast horizons for scoring). Separate regime, direction, severity, timing, action permission, signal delivery, and costs. Test what the model *actually knew*, not a modern replay.

**B / HIGH — Early warning and delayed recognition of adverse *alt* tails when BTC stays healthy.**
Compare 35-asset hourly panel ETH/BTC/breadth/volume, ETF vintages, existing historical pullback episodes, and typed Compass. Asset universe/survivorship and run-clock parity explicit. Evaluate *first observable divergence -> official risk -> downstream action readiness*. Reuse #1553 and M6 / EDGE-001; no new severity owner before admission.

**C / HIGH — CFGI internal component dispersion and path-to-exit versus naïve score levels.**
Use MAEVE 432 parent positions + DCA legs and real no-trade opportunity controls; compare score, Technical minus Social/Whales/Orders/Trends, velocity, persistence, version eras, exit choice, capital deployment, fee/liquidity costs. Work with private data in place. Most important: restrict entry features to source-knowable timestamps; remove \`analisis_hora\` post-entry lookahead suspect fields. Historical MAEVE action reconstruction is NOT an Investering-framework trade track record; assess transferability separately under external-alpha #937.

**D / HIGH — Stale but good data, degraded states and source vintage as a market-signalling anti-pattern.**
Test degraded/UNKNOWN incidence by session, source, weekend/holiday and API/provider version; estimate selection bias in *which weeks were scoreable* and false reassurance after last-known-good states. Source health is **not** itself bullish/bearish. Connect time-to-delivery in #1553.

**E / MEDIUM — Hypothesis-family redundancy and confirmation delay economics.**
Ablate 3 independent families (ETHBTC persistence, breadth survival, BTC.D path) versus full shadow stack; matched negative controls and regime splits. Relate false positive prevention to false negative opportunity cost only with qualified real decision identities, under #1478/#1557 existing owners. Do not change gates from a retrospective selected winner.

**F / MEDIUM — Forecast copy-forward inertia / threshold vintage drift.**
Audit the exact published CN #13 -> #14 repeated price map and subsequent undershoots, plus earlier April/May conservative rotation vs optimistic price-level calls. Distinguish intentional unchanged forecast from template copying; freeze document issue and actual market time before diagnosis.

**G / CONDITIONAL — Historical BlockHorizon unique information.**
Only when source basis/overlap and point-in-time availability can be compared against 35-asset panel and DefiLlama owner; no bulk reacquisition, no promotion by archive size.

### 8.7 Existing-owner routing and pre-audit readiness gate

- Existing **#209 Market Anticipation Research Program** owns broad historical PIT comparisons and baselines.
- Existing **#1553** owns Oct risk-to-action and delivery.
- Existing **M6 / EDGE-001 / #1530** owns prospective distribution-warning economics and no-warning controls.
- Existing **#937** owns MAEVE external alpha; **#1557** owns cross-strategy trial-denominator integrity.
- Existing **#1478** owns FNP observer production/coverage gap.
- Existing CN precision learning and M3 benchmark own public score/freeze and baseline research. No parallel forecast/market owner.
- Existing Data Ping source QA and Historical Research Vault own raw provenance and coverage.

**Before a claimed comprehensive deep audit PASS, require:**
1. A deterministic source census separating Project-file records, full original ChatGPT thread messages (if actually accessible), legacy import files, canonical GitHub frozen forecasts, and private raw owner manifests. Report \`UNREAD\`, \`PARTIAL\`, \`UNTESTABLE\`, \`VERIFIED\` separately.
2. Immutable event-level freeze/outcome joins and correct owner/model version; no leaking old hindsight/reconstruction into prospective denominator.
3. Source-frequency/source-time/availability/revision alignment and dedup of correlated, overlapping episodes.
4. Explicit negative results, null actions, failed controls, censored right-tail cases, data outages and non-triggers; opportunity costs and false reassurance separately.
5. Within-era proper baselines, not arithmetic average across old and new scoring systems, no outcome-selected target/horizon.
6. Concrete owner handoff for each new falsifiable question; mark duplicates \`NOOP\`, irreproducible early sensor claims \`UNTESTABLE\`, data-restoration candidates \`SOURCE_RECOVERY\`. No new autonomous search or live threshold changes.

**Readiness verdict on 2026-10-10: \`NOT_READY_FOR_COMPLETE_AUDIT_PASS\`; \`READY_FOR_BOUNDED_SOURCE_CENSUS_AND_PIT_RECONCILIATION\`.** This is an evidence inventory and next-test plan, not proof of comprehensive original-message extraction, backtest execution or independent prospective alpha.