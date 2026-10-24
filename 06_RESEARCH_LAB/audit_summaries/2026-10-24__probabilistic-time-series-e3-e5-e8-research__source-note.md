# Research intake | Probabilistic time series, calibration, regime shifts and backtest bias

**Dato:** 2026-10-24  
**Status:** SOURCE_NOTE / RESEARCH_ONLY / NON_BINDING  
**Område:** Fable P1b E3/E5/E8; Task 2 and Compass scientific evaluation  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `canonical-project-archive/05_RESEARCH_LAB/fable_research/`, `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/`  
**Supersedes:** None  
**Authority:** No market rule, automatic schedule, code owner, threshold, weight, forecast, trading signal or portfolio action is created.

## 1. Why this belongs in the archive

This is a one-time literature appraisal, not a scheduled research service. It evaluates whether methods can improve *scientific evaluation* and uncertainty auditing of the **already named Fable P1b tests** rather than silently importing another meaning of E3/E5/E8 (these labels are overloaded elsewhere in the repository).

Verified source anchors (read 2026-10-24):
- [Fable P1b executed ratification](../../canonical-project-archive/05_RESEARCH_LAB/fable_research/p1b_ohlc_flow_upgrade/P1b_Executed_Ratification_2026-07-06.md), Git blob `d2136f286db5c038b6f195b124c4256c8a981e3d`.
- [Task 2 acceptance matrix, 23 October](../hugging_face_task2_audit_20261022/22_TASK2_ACCEPTANCE_MATRIX_20261023.md), Git blob `6bbb8092e708661dff0e6d9fa24bb87bab72b91d`.
- [T05 confidence calibration finding](../existing_system_improvement_12x/T05_CONFIDENCE_CALIBRATION.md), Git blob `60a14745fb833f19b1f25e3e78895108f4c15287`.
- Existing scientific owners [Task 1.5 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), #1530 and Task 2 R0-R7. No competing owner is established.

Interpretation of these **historical, legacy-namespace** Fable results:
- **E3-FULL, close-persistence / 2-of-3 closes:** not supported as a price edge in P1b; ETF-era N1/N2/N3 hit rates 0.344/0.44/0.409, with flow-conditioned cells n≈9-12. A discipline rule, *not* a proven forecast.
- **E5-OHLC, hybrid v0.2 gate:** comparatively fewer false-death classifications than binary under close and wick trigger; P1b reports 13 pullback episodes. This is an historical classification comparison, not proof of future probabilistic calibration.
- **E8-FULL, FNP opportunity-cost prior:** historical METER_B median 7.8%, bootstrap CI 6.6-10.3%, p90 11.8%; 13 episodes with 11 entries referenced in supporting recommendation rows. Episode-low-informed anchors make it a *measurement prior*, not live-realizable prediction or trading action.

Do not promote these to current production or Task 2 information-edge evidence. The [23 Oct Task 2 matrix](../hugging_face_task2_audit_20261022/22_TASK2_ACCEPTANCE_MATRIX_20261023.md) explicitly leaves full R1 information admission and investor edge NOT_ADMITTED; the 16 matched source-complete BTC/ETH direction slots showed 7 correct on each side and paired lift zero, all development-only.

## 2. Screened methods and evidence strength

Methodological credibility and *transfer to the framework* are separate assessments. Peer review is not proof of crypto out-of-sample edge.

| Source / publication class | Specific idea | Evidence appraisal | Archive relevance / limitation |
| --- | --- | --- | --- |
| **Sun & Yu, NeurIPS 2025, peer-reviewed conference**: [CPTC, regime-change conformal prediction](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12271b64c483ad8f6192eb6aaa102044-Abstract-Conference.html) | Combine change-point state inference with online conformal interval updates; evaluated on 6 mixed synthetic/real data sets. | **Method: moderate-to-strong** (published, theoretical and empirical); **crypto transfer: unproven**. | E5 post-shift false-death episodes; E8 intervals around downside/upside opportunity cost. Regime detection must itself be based on past-available data. |
| **Wu et al., ICLR 2025, peer-reviewed conference**: [Error-quantified conformal inference (ECI)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/cab5ae2704d3e01f06a92512a5376b87-Abstract-Conference.html) | Update online quantiles using *magnitude* of miscoverage, not merely a binary error flag. | **Method: moderate-to-strong**; proven long-run coverage in specified setting, not guaranteed conditional market coverage. | Low-complexity E8/E5 research challenger; record width, miscoverage magnitude and time-to-recover after volatility shocks. |
| **Gibbs & Candès, JMLR 2024, peer-reviewed journal**: [Adaptive online conformal inference](https://jmlr.org/beta/papers/v25/22-1218.html) | Adapt interval calibrator to local drift; tested, among other tasks, on stock-volatility data. | **Method: strong baseline**; finance-adjacent, still not directly crypto. | Preferred simpler research baseline before CPTC/complex models. Evaluation of intervals, not changes to Compass decisions. |
| **Bao et al., JMLR 2025, peer-reviewed journal**: [CAP, calibration after adaptive pick](https://www.jmlr.org/beta/papers/v26/24-0452.html) | Address selection-dependent error when intervals are published only for chosen events. | **Method: moderate-to-strong in its formal setting**; needs adaptation to dependent, episode-selected crypto data. | Especially important if E5/E8 reports only triggered alerts: score the full eligible event universe and separately selected-event reliability; do not confuse FCR with nominal single-interval coverage. |
| **Arian et al., Knowledge-Based Systems 2024/2025, peer-reviewed journal**: [Backtest overfitting comparison](https://doi.org/10.1016/j.knosys.2024.112477) | In a synthetic controlled setting, compare combinatorial purged CV (CPCV) and walk-forward with PBO/DSR diagnostics. | **Method: moderate**; controlled simulation does not establish universal superiority of CPCV for this data. | E3 parameter/flow selection and E5 gate-comparison negative controls; CPCV as sensitivity analysis, chronology-respecting *walk-forward remains necessary* for deployment-like evaluation. |
| **Shahbazi & Baheri, Forecasting, published 1 Sep 2026, peer-reviewed journal**: [PACE heterogeneous-horizon conformal ensemble](https://doi.org/10.3390/forecast8050077) | Mix multiple window lengths; reported higher extreme-regime empirical coverage on two synthetic and three real series. | **Method: exploratory-to-moderate**, limited data; authors explicitly state heuristic PACE lacks strong-adaptivity guarantee and sometimes widens intervals. | E8/E5 ablation only after simpler adaptive baseline; avoid automatic adoption from nominal coverage gain alone. |
| **Schweizer et al., arXiv 26 May 2026, PREPRINT, not verified peer reviewed**: [Distribution-aware conformal prediction (DCP)](https://arxiv.org/abs/2605.26569) | Plug-in pairing of probabilistic predictors and nonconformity scores. | **Method: preliminary**, comparisons author's own; formal claims are setting-specific. | Candidate future method benchmark; not near-term priority with tiny E8 cohort. |
| **Gneiting, Balabdaoui & Raftery, JRSS-B 2007, peer-reviewed methodological foundation**: [Calibration and sharpness](https://doi.org/10.1111/j.1467-9868.2007.00587.x) | Prefer calibrated *and sharp* distributions; proper scores and calibration diagnostics. | **Foundational strong method**; no claim of crypto edge. | Universal evaluation vocabulary for proposed probabilistic studies: coverage alone can be gamed by needlessly wide bands. |

Sources screened on 2026-10-24. The table distinguishes *published peer-reviewed works* from the preprint and does not treat venue/year as an effect estimate.

## 3. Ranked application, without generating signals

**P0 | Evidence/provenance before method sophistication.** Historical P1b folder is a ratification and recommendation summary; [data-file note](../../canonical-project-archive/05_RESEARCH_LAB/fable_research/p1b_ohlc_flow_upgrade/P1b_Data_Files_Note_2026-07-06.md) says raw `experiment results 2.json`, `btc ohlc master.csv`, ETF-flow file and source manifest were thread uploads, not the canonical text archive. No source-row replay or new numerical confidence conclusion without recovering eligible original artifacts and immutable availability clocks. Neither source *existence* nor provider backfill proves first-known timestamps. Preserve Task 2 R1/R2/R3 gates.

**P1 | E5 paired, event-level robustness.** Freeze binary-vs-hybrid classification definitions and the full eligible episode population. Compare paired false-death and true-death cases by episode and regime (quiet / trending / shock) against unchanged rules. Use exact close-vs-wick interpretation, publication/availability clocks, event-cluster resampling, and leave-one-episode-out sensitivity. *Do not* treat repeated bars or overlapping episodes as independent Bernoulli samples. Missing denominators or small counts mean report uncertainty / NOT_ESTIMABLE rather than a confident superiority claim.

**P1 | E8 opportunity-cost interval reliability.** Retain the existing ~9% [7-12] prior and ~12% p90 only as historical ledger measurements. As eligible forward observations accumulate, pre-register an asymmetric quantile/baseline historical band vs simple online adaptive conformal calibration, evaluate empirical 50/80/90% coverage, event-regime undercoverage, median interval width, Winkler/interval score, tail exceedance and recovery after regime breaks. With 13 historical episodes, the p90 is effectively determined by approximately one or two upper-tail observations; naive iid-bootstrap tail confidence is fragile. Episode-block uncertainty and reporting `LOW_SAMPLE` are more honest than tightened bands.

**P1 | E3 conditional failure atlas, not hypothesis rescue.** The present outcome is *price edge NOT SUPPORTED*. Re-express the fixed N1/N2/N3 experiment by prior-available volatility/regime/flow availability, price-only comparator and false whipsaw episodes. Maintain original close/wick semantics. No post-hoc 'best' flow subgroup, parameter choice or profit claim. Multiple exploratory slices count toward the selection ledger.

**P2 | Adaptive methods as shadow-only falsifiable challengers.** Start with a simple quantile / historical residual interval and a JMLR online conformal baseline; only then test ECI/CPTC/CAP or exploratory PACE/DCP as *one additional frozen family*. If outcomes and authentic frozen probabilities do not exist, no Brier/log score, PIT probability calibration or claimed probability forecast can be calculated. Directional vote labels must not be retrofitted into probabilities.

## 4. Reproducible evaluation design and fail-closed gates

1. **Freeze prior:** target, unit, horizon, clock, full issue universe including abstentions, source/vintage, data availability, event segmentation, model version, selected feature family, hyperparameter trial count and baselines; include cost of failed gate and interval wideness. Market regimes must be frozen using data knowable *before* each issue time.
2. **Dev vs holdout:** split chronological data into development, calibration and untouched prospective evaluation, with purge/embargo covering outcome overlap and source publication lag. Run within-episode block bootstrap and a CPCV sensitivity analysis where valid, but never use future folds to train an allegedly real-time forecast. Report effective independent event count.
3. **Score:** empirical interval coverage at each pre-registered nominal level; conditional/worst-regime coverage with low-sample marks; mean width and interval score / WIS; tail undercoverage; pre/post-change coverage recovery time; calibration/decision abstention/coverage denominator. A model that achieves 90% by infinite-width bands fails sharpness.
4. **Negative controls:** timestamp-shifted features, shuffled and deliberately future-contaminated features must be *detected/rejected* by the provenance gate, not counted as challengers. Selective-event-only scoring must be compared to the complete prior-eligible population. Repeat all scores with placebo regime assignments.
5. **Promote nothing automatically:** acceptance is a reviewed research admission decision only if original time-bound observations and outcomes are admissible, stronger-than-baseline *paired* improvement is repeatable across distinct future episodes, adverse sensitivity and false-coverage controls survive, and #1596 / Task 2 owners review results. If maturity, provenance or independence is insufficient, return `NOT_ADMITTED / LOW_SAMPLE / NO_PROSPECTIVE_EVIDENCE` as applicable.

## 5. Verdict and next concrete action

**Verdict: archive-worthy HIGH relevance for measurement discipline, LOW evidence for immediate improved market edge.** The most useful near-term work is *not* another forecast engine: repair source evidence for P1b (if available), preserve paired E5 episode denominators, redesign E8 cost uncertainty honestly, and defend E3 from post-selection. Current Task 2 already has a source-admission bottleneck, so no expensive model tournament should precede that gate.

**Handoff:** Reuse current #1596, #1530 and Task 2 R0-R7 as scientific owner tracks. This note is an isolated research source note for human review; it is not a new mission, scanner, scheduled Friday task, Codex-ready defect, output service or release request. No code, credentials, secret provider data, live rules, trading signals or portfolio instructions are included.


## 6. Owner-authorized implementation contract, 24 October 2026

**Mandate:** Implement all research relevance within existing framework ownership, but never infer that a literature note is an admitted predictive edge. This is an execution specification and not a claim that code, tests, historical data, or production have been changed.

### A. P0 evidence gate (existing Task 2 owners)
- Resolve original Fable P1b machine files and manifests if accessible; bind each to immutable source SHA, availability time, unit, episode ID and exact experiment configuration.
- Report `ORIGINAL_DATA_UNAVAILABLE` if any essential file cannot be authenticated. Do not substitute public hindsight series for original point-in-time inputs.
- Preserve Task 2 R1 `NOT_ADMITTED`; use current original census and independent-event constraints. No Round 3 unblinding.
- Acceptance: one row per source artifact, digest and provenance status, missing artifacts explicit, no restricted provider values in public output.

### B. P1 E5 classification robustness
- Research-only paired binary-vs-hybrid per-episode replay, with original close/wick distinction and pre-frozen outcome labels.
- Report event denominators, paired contingency matrix, false-death/true-death rates, event-cluster confidence interval and leave-one-episode-out sensitivity.
- Regimes defined using only pre-issue information; missing regime -> UNKNOWN, not inferred from outcomes.
- Acceptance: synthetic fixture verifies that duplicate bars cannot inflate event count; missing source clocks block admission; zero output changes to live hybrid gate.

### C. P1 E8 uncertainty audit
- Retain FNP historical prior as ledger-only, never promote historical 7.8% median or ~12% p90 to a calibrated live interval.
- Define research-only asymmetric quantile intervals at 50/80/90%, evaluate coverage, mean width, interval score, regime-conditioned coverage and tail exceedance on *matured independent* episodes.
- Compare frozen historical-quantile baseline with online adaptive conformal; ECI/CPTC/CAP remain challenger-only after adequate observations.
- Acceptance: explicit LOW_SAMPLE and NOT_ESTIMABLE on insufficient events; censored and overlapping episodes excluded or appropriately grouped; future outcome not used for earlier prediction.

### D. P1 E3 selection-bias audit
- Preserve existing price-edge NOT_SUPPORTED verdict and discipline-only status.
- Frozen N1/N2/N3 definitions; full eligible episode universe including negative and abstained outcomes; report all tested regime/flow cells and multiple-comparison count.
- Acceptance: any retrospective best-subgroup selection is tagged EXPLORATORY, not a new live threshold.

### E. P2 Compass and Task 2 interfaces
- No forecast probability reconstruction from directional labels; T05 structured confidence sidecar requires exact original header/output hash and prospective candidate lineage.
- Prepare non-operative evaluation schema with `issue_id, issue_at_utc, source_available_at_utc, outcome_matures_at_utc, horizon, target, regime_known_at_issue, episode_id, interval_lower, interval_upper, nominal_coverage, observed_value, admitted, censor_reason, model_version, baseline_id`.
- Evaluate WIS/interval score, coverage, sharpness, tail misses and regime recovery only for admitted, naturally matured rows.
- Any UI disclosure must distinguish historical diagnostic, research-only forward test and independently admitted production forecast. Do not publish probability or improved skill claims without measured prospective evidence.

### F. Release and resource gates
- Existing owner tracks: #1596, #1530, #1553, #1156. No competing owner or scheduler.
- GitHub Actions minutes exhausted until November 1 per owner operational context. This is not permission to bypass CI, fake checks or merge production changes without actual platform gates.
- No paid compute/API, new scheduled jobs, new secrets or credential access, no restricted data transfer to public repo.
- This source-note PR is documentation-only; follow-on executable implementation belongs in existing research owner branches after source admission and actual test review.

### Done criteria
1. Research note merged with platform/governance gates and post-merge readback, or explicit blocker recorded.
2. Original source evidence admitted or explicit unavailable state.
3. E3/E5/E8 reproducible evaluation fixtures and paired baseline results, only if original data and required clocks pass.
4. Compass-facing uncertainty fields remain shadow-only until independent prospective admission.
5. Each claim reports actual test command, commit SHA, review, CI and production state separately.
