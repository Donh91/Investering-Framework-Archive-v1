# Task 2 — use existing data first; measure missing data's marginal value

**Decision:** 2026-10-16 authenticated owner instruction: continue every scientifically legitimate diagnostic possible on currently held data. Absence of one desired external source MUST NOT halt unrelated existing-data analyses. This is an addendum within existing Task 2 #1596 / #1530 / #1553, not a new engine, schedule, queue, score or owner.

**Evidence pin:** frozen original R1 v2 Git blob `9e728b835de294e5777222c171a89874a69dae95` at `04_MARKET_LEARNING/handlekompas/research/2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json`. Verified by deterministic `scripts/research/task2_existing_data_coverage.py` and 10 positive/negative tests, executed successfully on the original PR head under Native Handlekompas CI. For this reviewed research-only PR head, no GitHub workflow is changed; reproduce with `python -m unittest tests.research.test_task2_existing_data_coverage -v`. CI coverage on subsequent heads must be read from exact-head checks, not inferred from the earlier head. The generated /tmp report is an aggregate technical diagnostic, NOT a fresh original market capture or a score.

## A. What is **actually available** in this frozen cohort

| Dimension | Existing evidence | Proper inference |
|---|---|---|
| Original Compass attempts | **11/11** retained, no winner-only selection in this scoped attempt set | Descriptive attempt-level audit now |
| Original 12h outcomes at the original snapshot | **9 present / 2 absent** (later availability is separately labeled) | Can describe complete original snapshot, cannot silently promote late outcomes |
| Features used at original issue | **24 feature IDs × 11 = 264 feature observations** | A measurement/reuse census, **not** 264 independent events |
| Explicit *local retrieval* timestamps | **99/264**, covering CFGI, dominance, ETF, stablecoins and altseason score fields | Earlier Git/archive retrieval evidence, not vendor original first-publication |
| Retrieval clock absent on feature | **143/264** | Still usable in **ex-post reconstruction** with a reconstructed label, NOT certified original as-of |
| Funding timestamp used as observation but in fact settlement | **22/264** | Test original contemporaneous OKX quote separately, never mistake future settlement for observed quote |
| Independent vendor publication or revision proof | **0/264** | Historical confirmatory admission stays blocked |
| Documented first user delivery / first executable opportunity | **0/11** | Investor after-cost utility cannot be claimed |
| Distinct original source packets / raw capture dependencies | **10 / 7** | Shared evidence and overlapping BTC/ETH horizons mean effective N is smaller than 11 |
| Independently certified event-family assignments | **0/11** | Do not use 11 raw attempts as 11 independent shock experiments |
| Scientifically admitted forecasts | **0/11** | Historical certified R2 performance remains blocked, **not** all research |

## B. Run three noninterchangeable lanes, without waiting for perfect data

**Lane 1 — AVAILABLE_NOW / no paid model required**. Replay existing immutable archive metadata and allowed public-price/capture datasets to map attempt/abstain/missingness, source latency, model/version changes, class balance, late warning rates, cohort overlap, false positive/false negative *descriptors*, PRICE ONLY baseline controls and signal-family coverage. Existing data can support sensitivity, coverage and counterexample tests NOW. Report ex-post association only when the original decision-time provenance is missing; label all hindsight reconstruction honestly. Never join private inputs to a public file.

**Lane 2 — AVAILABLE_WITH_AS_OF_RECOVERY / data-quality-falsifying**. Attempt read-only reconstruction of known original captures and provider-version timestamps from existing Git objects, exact original Actions artifacts in private `Donh91/secrets` main `09c4ca83da0ff507c862f6418d6ea566625f3f2b`, original API receipts and historically versioned endpoint material **if accessible under existing authority and budget**. Save source origin, retrieval date, provider event/release/revision date independently, timestamps' meanings, original versus reconstructed versions and missingness. Later API responses are `RECONSTRUCTED_EX_POST` until a separate original first-known receipt proves the historical value. Do not buy, re-request or fabricate missing 2025 MARKET CFGI coverage merely to fill a table.

**Lane 3 — PROSPECTIVE_CONFIRMATORY / natural data accrual**. Continue native immutable source captures, full forecast/no-forecast/abstain denominator, first source-publication/first-delivery times and independent outcome families, then matched preregistered baseline ablations on eligible observations. Reserve certified historical R2 and economic edge conclusions for admitted same-clock outcomes. Do not suspend Lane 1 or 2 while Lane 3 waits.

## C. Test exactly **which additional data materially improves** the Compass

Perform staged comparisons on **identical eligible decisions, timestamps, target horizons, universe, costs and missingness**; out-of-sample train-only choice and event-family blocks. Start `price+momentum+volatility+volume` versus: +breadth/ETHBTC/BTC dominance; +OKX quote/OI/funding; +CFGI composite and nonprice residual; +settled ETF+stablecoin flows; +verified rotation/altseason. Correlated components (e.g., CFGI price, volatility and volume) cannot be treated as independent extra signals. Require family-shuffled placebo and one-candle delay controls, estimate absolute lift and uncertainty, and include all nonalerts/abstentions. If data are incomplete, run a *paired available-case sensitivity* with complete-case attrition and missingness bias explicitly reported; never impute original first-known.

Priority hypothesis for incremental collection is **source clock and as-of universe provenance first**, then original warning delivery, then matched independent outcome events, before paying for high-dimensional extra features. This is a provisional research priority, NOT a measured feature-value ranking. Extra API/paid data are justified only if a frozen baseline predicts meaningful additional decision information, free/historical alternatives are inadequate, source-clock validity is checkable, and expected marginal learning exceeds expense.

Other EXISTING research populations may run separately under their own exact owners, not pooled into this tiny R1 cohort:
- Native BTC/ETH hourly/altseason archive: 851,882 hourly/context rows across 35 symbols (historical availability metadata, not 851,882 independent trials); owner: `06_RESEARCH_LAB/historical_altseason_pullback_v1`.
- CFGI recovered 1h 2025 event data: 478 BTC/ETH rows from two selected windows, **zero MARKET** rows, not a 2020–2026 continuous CFGI history. Compare windows descriptively; source/source-clock qualifiers apply.
- MAEVE private research: previously inventoried 1,073 fills within 432 parent positions, not independent fills; reserve labels and counterfactual opportunities remain required.
- Intraday 1/4/24h shadow, CN frozen weekly ranges, M6/pullback, ETF and Alpha Lab all have existing owners; evaluate without retroactively merging populations or letting one blocked data source halt the others.

## D. Sol 6.1 API: specific reason to call, otherwise STOP

- Existing `TASK2-R1-CFGI-PIT-FALSIFICATION-002` **already has a completed GPT-6.1 Sol High receipt**, estimated $0.438430; its frozen-input replay is **CLEAN_NOOP**. Paid result verdict is `INSUFFICIENT_EVIDENCE`, not an invitation to retry until PASS.
- An additional paid Sol 6.1 pass is justified only for a **new source-vintage verified bundle**, a new independently authenticated comparator/ablation outcome, or a reproducible conflicting high-consequence code/science fault. Freeze `mission_id + original source blob SHA(s) + hypothesis + comparator + timestamp meaning + outcome-blind context hash + prior receipt IDs`. No duplicate-paid call for identical fingerprints.
- Use only EXISTING `RESEARCH_LAB_SOL_ANALYSIS`/approved senior lane, real GitHub owner-gated trigger and budget admission, never Work or Codex cloud. At most one new active mission, $40 monthly hard stop, $4 global reserve, lane cap $10, no trade/score/threshold authority. If no new evidence or a liability-uncertain prior attempt: `SKIP_SOL_COST` and do deterministic diagnostics instead.

## E. Stop-rule / completion criteria

1. **No circular gate**: each lead owner is classified `AVAILABLE_DATA_ANALYSIS`, `SOURCE_RECONSTRUCTION`, `NATURAL_WAIT`, `ADMISSION_ONLY_BLOCKED` or `COMPLETE`. The latter three never prevent work on the first two. Do not create another owner or parallel queue.
2. **One recovery attempt per exact as-of-source request and bounded source window** when API access is approved. A real source-unavailable or terminal zero-row receipt is `NO_FILL_TERMINAL`, not a prompt for infinite retries.
3. **One paid Sol review per materially changed frozen evidence bundle**; after report verification mark done. Do not re-run old R1, and never relabel `0/11` as success because an archive or API response now exists.
4. For all tests: document N attempts, N covered, N original outcomes, N censored, N independent events, baseline, feature subset, additional cost, and out-of-sample validity. Score informational and investor-action value separately; missing investor evidence => economics UNKNOWN.
5. Maintain **per-family information gain and cost versus a price-only control**. The family with largest future statistically supported, independent, actionable lift earns first recommendation for continued collection. Until measured, feature lift = UNKNOWN, not 0.
6. Preserve frozen forecasts/outcomes and historical code, market rules, site presentation authority, budget caps, private/public boundary and recovery independence.

**Exit for this bounded work item:** metadata inventory/source chronology verified + negative CI + this handoff merged/read back. Actual no-hindsight scientific admission (0/11) and after-cost economic validation remain **independent future evidence gates**, not reasons to stall the finished diagnostic.
