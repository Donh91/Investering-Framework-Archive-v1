# MAR #209 | Grok Bridge #195 WP04B/WP04C, independent method closure and owner decisions

Date: 2026-11-15. Status: REVIEW_ONLY / SOURCE_CLOCK_REMEDIATION_REQUIRED / SCIENTIFIC_ADMISSION_BLOCKED. Classification: RESEARCH_ONLY, retrospective public-source challenger, not canonical market evidence. Original owner: Archive issue #209. Related owners: Task2 #1596, Compass #1516, risk-to-action #1553, source owner #1827, existing draft #2162. No new engine, model, alert, scheduler, source authority, portfolio permission or trading authority.

## Decision in Danish

Den nyttige leverance er en reproducerbar negativ og metodisk læring, IKKE at makro generelt er værdiløst. Groks forskning i Bridge #195 består faktisk af tre filer, inklusive allerede udførte Stage B/C/D/E-resultater. Den var ikke stoppet før resultaterne. Testene peger imod dokumenteret ekstra 14-21-dages BTC-præcision fra netop USD/renter/VIX og imod en sikker gearing-edge. Men originalkoden har fejl og kildebegrænsninger. Ingen resultater må bruges til at ændre Kompas Pro, prognosevægte, advarsler, positioner eller paper-execution uden ny owner/admission-kontrol.

Dette dokument afslutter den tilladte **uafhængige metode-audit**. Det er IKKE en uafhængig reproduktion af Groks historiske rådatasæt, resultater eller fulde 2018-2026 simulering. De tests forbliver uafhængigt **UNVERIFIED**. Kun den specifikke metodeaudit og syntetiske fejlklasser kan erklæres gennemført.

## Provenance and scope

- Grok original: https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/195, head inspected 5d92bf6708532d761e6034e1898afe845d13ab06; three immutable report artifacts, PR remains OPEN. Part 1 blob 5e5ca7dd53ad2443170a4971071bc894667a8168; Part 2 eebbecf6a1103c1c71c57fc53bc7b8fa875e93eb; Part 3 838e36455a06f14ac0dcf73b0d7445090b2bde5c.
- Grok's original Archive snapshot: c0c19cbf874680e096908d6ea766bdb3c8621135. Current Archive main was independently checked by fetching source files again: WP04B_TRIGGER_ADDENDUM_v1.json blob ca8362f5bd231b55f456c1b2554b243d2129a350 and RESEARCH_CONTRACT.yaml blob 979e40191372ae0eea17ea925c8a99479fc58112 still match the frozen snapshot.
- Governance gap is genuine: OWNER_READINESS_GATE_v1.json blob 7e9880ee143dd6c8c38b513673fd009f4654cec4 still sets macro_enumeration_authorized=false and leverage_enumeration_authorized=false. Grok used latest-vintage NON_OWNER public histories; this does not automatically clear that gate. Explicit owner adjudication required.
- The project already has a related source-first longer-horizon design in draft Archive PR #2162. Do NOT duplicate its hypothesis register, scorer, source registry, pipeline or experimental dispatch.
- Codex commented on the earlier PR head 790f4bdb42b4ab128e03744a471b2973ec7c8ef2: source-order defect at discussion_r4579176439 and missing dollar-only availability dates at discussion_r4579176444. That review is COMMENTED, not APPROVED and not an independent review of PR #195 latest head.
- Framework-native method read: canonical-context-router, research-lab-red-team, research-parallel-lanes, conclusion-challenge-loop and archive-governance; supplemented with Data validation/data-quality review. No paid tool use and no private Round 3 value access.

**Question:** Can the original frozen WP04B signals legitimately improve BTC 14-21d forecasts, detect stress earlier, or improve after-cost decision utility beyond cheap controls, once data clocks, availability, blocked owners and correlation are respected?

## Five bounded review lanes (one chat, not five AI agents)

| Lane | Subquestion | Method actually performed | State |
|---|---|---|---|
| R1 source clock | Can reported feature dates be first-known and stable? | Direct read of prep.py, wp04b_macro.py and analysis.py, Codex cross-check, synthetic date collision and publication-mask tests | COMPLETE_VERIFIED for synthetic failure patterns only; original PIT history BLOCKED |
| R2 event mechanics | Are macro/leverage episodes capable of timely alerts? | Exact reported state-machine control inspection, one-shot/reset and funding-cadence contradiction audit | METHOD_DEFECT_EVIDENCED; historical counts NOT_INDEPENDENTLY_REPLAYED |
| R3 forecast skill | Does MIWF beat B0, B1 and placebo? | Verified reported Brier arithmetic, target definitions, purging code and statistical claims against source report | REPORTED_NEGATIVE; ORIGINAL_RAW_REPLICATION_UNVERIFIED |
| R4 paper economics | Does an after-cost allocation rule beat buy/hold and SMA200? | Code-level position-delay/cost audit, table arithmetic, overlapping samples and economic transfer review | DESCRIPTIVE_ONLY; NO_ECONOMIC_EDGE_ADMITTED |
| R5 owner and integration | Which existing owner can accept what? | Archive #209 frozen contract, #2162 G1 status, #1596, #1553, #1827 and S1 tier freeze reconciliation | ROUTED_FOR_REVIEW; NO_OPERATIONAL_CHANGE |

There were NO remotely spawned independent agents, NO new GitHub Actions jobs, NO public raw-market replay, NO ALFRED vintage pull and NO OKX owner comparison in this review. Reported Grok compute is not claimed as new compute in this artifact.

## What Grok actually ran and reported (unverified numerical findings)

- Macro strict: 22 episodes, three independent reported events (2019-08-14, 2023-03-03, 2026-03-18). Macro as-of: 23 episodes, four independent reported events (2020-02-26, 2022-06-16, 2023-03-09, 2025-01-09). Sensitivity is very high: only the March 2023 cluster overlaps both clock interpretations. Both have far too few independent warnings for reliable precision/recall.
- MIWF: expanding refits every 91 days, target 14d and 21d direction and -10% drawdown, overlapping daily rows 3,219 to 3,226; purported 2000-replicate moving-block bootstrap and Holm correction. C = price plus four macro z features; B1 = price only; B0 = historical base rate. Reported BSS(C vs B1): DIR14 -0.025, DD14 -0.024, DIR21 -0.019, DD21 -0.013. Direct arithmetic checks using published Brier values agree at reported precision. Not 3,200 independent event samples. This is evidence AGAINST a robust edge claim, not a validated proof of absence.
- Paper BTC 2018-01 to 2026-10, 20bps/switch reported: buy/hold CAGR 22.0%, max DD -81.4%; macro C 24.3%, max DD -73.1%; SMA200 22.0%, max DD -60.0%. The simple benchmark has 21.4 percentage points less maximum drawdown than buy/hold in that single historical path. At 50bps/switch macro C falls to 20.0% CAGR. This is an imperfect BTC-only comparator, not a microcap/wallet claim or a proven deployable SMA rule.
- Leverage Binance challenger 2022-2026: 73 episodes, 26 independent reported events, 1,110 spot-only controls, mean sign-adjusted difference -0.91pp at 24h with reported raw permutation p=0.091 and Holm p=0.18; at 72h +0.14pp and p=0.874. Pre-registered threshold not passed. Historical LUNA, yen-carry and October 2025 cascade misses were hindsight diagnostics only, not advance warnings.
- Grok's source manifests and output JSON hashes are embedded in the Bridge reports but the downloaded raw files, full standardized panel and independent execution receipts are NOT available in this archival review. A hash of an unavailable artifact cannot independently establish the numeric result.

## Material findings and corrections

### P1-01: Funding window is not the frozen hourly window

Grok leverage code calls rz(fund) with 2160 funding observations and a 720-observation minimum. Funding is settled approximately once every eight hours. 2160 settlements cover approximately 720 calendar days, whereas 2160 eligible hourly rows cover approximately 90 days; 720 settlements cover approximately 240 days versus 30 hourly days. This is not a trivial detail: thresholds and event counts can change. The same script calls method='ffill' for fz_asof and f_asof on the hourly panel and relies on it for eligibility/reset despite describing an 8h observation cadence with no silent forward-fill. Adjudicate whether an explicit last-known settled funding state is legally separate from forward-filling a required observation. DO NOT silently alter the July contract. Severity HIGH for exact-frozen-chain claim; current count of 26 is not owner-admitted.

### P1-02: Historical dollar vintage and exact first-known clock remain unverified

H.10 source is the latest-vintage Federal Reserve series, with a hand-derived Tuesday-after-next-Monday availability date. No ALFRED historical vintage or individual release timestamp was verified. Holiday publication delays and revisions can alter first-eligible rows. The in-code assertion only proves that the assigned availability timestamp is not after the model row; it does NOT prove that the assigned timestamp is the true initial public availability. Event dates and Brier comparisons should remain RECONSTRUCTED_NON_PIT, not canonical forecast skill.

### P2-03: Tied publication-day ordering can select a non-latest value date

In Grok macro_daily_asof and MIWF panel construction, sort_values('a').groupby('a').last() does not tie-break on source value date, while multiple daily H.10 value dates may share one release date. A deterministic adversarial synthetic 100-row tied publication example selected z=44 instead of the latest value-date z=99 with pandas 2.2.3. This demonstrates the failure class, not that Grok's actual H.10 five-date batches changed results. Use an explicit (available_at, value_date) stable sort / last value-date contract, with fixture for reversed insertion order, duplicate revisions and holiday dates, then recompute all related outputs.

### P2-04: As-of eligibility excludes dollar-only releases

Grok macro_daily_asof constructs newpub from avail_ust_vix only, although its stated rule is an update from any macro component. A synthetic day with avail_dtw only is omitted in the old mask and included with union publication dates. The producer also assigns avail_ust_vix to the outer joined calendar even where Treasury/VIX may lack a valid source row, so naive union is insufficient: publication dates must derive from non-null source-specific observations, with source revision policy. Recompute daily eligible rows, qualification transitions, event dates and downstream labels before deciding whether reported numbers are stable.

### P2-05: 72h control outcomes are not independent at 24h event cluster spacing

The leverage design excludes events inside 24h, then evaluates 72h forward outcomes. Two legitimate events 25h apart share 47h of their forward windows. The permutation samples 26 spot-only controls against the mean of all 1,110 controls without a time-block or era-matched null distribution; burst regimes, overlapping outcome windows and funding cadence can make nominal p-values too optimistic. Use a time-stratified moving-block/cluster inference or non-overlapping 72h cohorts as a sensitivity check. Do not turn p=0.091 into an edge or infer a new alert threshold.

### P2-06: The Brier baseline is not enough to prove deployable utility

The 200-day trend rule is a useful cheap control for BTC paper-risk decisions, but neither a probabilistic DD21 calibration benchmark nor proof of a real wallet result. Independent validation must fix first-known source clock, next-bar settlement, buy/hold comparability, costs per actual fill, realistic cash yield/funding/fees, position/path-dependent opportunity cost, skipped upside, adverse fills, execution venue and delisted microcap cohorts. Post-hoc 10 macro placebo strategies cannot justify prospective strategy selection. The published macro CAGR uplift (+2.3pp vs buy/hold at 20bps) is statistically indistinguishable from luck under Grok's own reported CI; the incremental economics are not admitted.

### P2-07: Small event samples, interpretive choices and observational dependence

The July WP04B addendum freezes broad numeric trigger logic, but Grok chose I1-I8 and L1-L6 for ambiguous areas in November. Historical replay of them can aid diagnosis, but a modified interpretation after inspecting outcomes would be a new exploratory specification, NOT a clean confirmatory rerun. Distinguish independent event clusters from 3,200 overlapping daily target rows. The strict-versus-asof alternative counts must not be treated as two independent replications.

### P3-08: A missing-warning crisis is not necessarily a successful negative signal

The one-shot active episode lockout explains a substantive early-warning DESIGN LIMIT. It is causal code reasoning, not evidence that a proposed re-arm rule is predictive. Re-arm could multiply alerts, false positives, whipsaw costs and missed upside. Do not optimize a v2 to hit named crashes in the same 2020-2026 sample. Enforce alert lead time, false-alarm burden per eligible regime, minimum separation, missed-true-stress penalty, action exposure and cheap alert baseline in a newly frozen contract.

## Synthetic verification actually executed

Independent small synthetic checks were executed locally (pandas 2.2.3), and a research-only standalone fixture is attached alongside this note:

research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/2026-11-15__GROK_WP04B_SYNTHETIC_REVIEW_FIXTURE_v1.py

Expected illustrations: latest-date tie with 100 rows returns 99 by explicit stable value-date ordering vs 44 in one legacy random input; dollar-only availability false in legacy mask vs true when eligible source days are considered; 2160 every-8h samples span 720 days vs 90 days hourly; two 72h horizons spaced 25h overlap 47h.

These are **synthetic diagnostic tests**, not imported original script tests, historical replays, result corrections or production CI proof. If a pandas version changes the exact legacy tie selection, the invariant to test is *latest source value date*, NOT the exact erroneous number 44.

## Controlled decision registry (scoped by evidence class)

| Item | Method verdict | Framework action |
|---|---|---|
| Grok code and public source manifest | ADOPT AS CHALLENGER_REFERENCE_ONLY | Archive source link and diagnose after CI/owner admission |
| Historical 3/4 macro events | INSUFFICIENT_EVIDENCE and CLOCK_SENSITIVE | No precision/recall or risk threshold claim |
| MIWF 14d/21d macro set | PROVISIONAL_NEGATIVE, REPLICATION_PENDING | No macro-weight promotion; retain negative finding without declaring general macro impossible |
| Binance leverage 24h reversal | NO_DEMONSTRATED_EDGE, VENUE_NON_OWNER | Do not promote or transfer to OKX/microcap; source/cadence repair first |
| BTC SMA200 strategy | REFERENCE_BASELINE_ONLY | Compare forecast probabilities to climatology, portfolio utility to SMA200 and buy/hold under identical timing/costs |
| Re-armable WP04B v2 | SPECULATIVE_REDRAFT, OWNER_APPROVAL_AND_GATES_REQUIRED | Do not launch new historical experiment or prospective holdout in this PR |
| Live Compass / CN / S1 / paper wallet | NO_AUTHORITY | No production change, no task creation, no trading, no portfolio mutation |

This report deliberately **downgrades** Grok's unqualified REJECT/KILL for 14-21d macro and its 'complete replay' phrasing to provisional negative and non-owner-replayable subject to PIT/clock review. It **upholds** the narrower observations: no demonstrated edge in reported sample, one-shot lockout, missing vintage and need for cheap benchmarks. It **rejects** any leap from BTC trend backtest to long-tail token economics.

## Next smallest owner work after this audit

1. METHOD REPAIR FIRST, no predictive retuning. Under existing MAR #209: independently extract the exact old script snippets from Bridge #195, write synthetic negative tests before fixes, define true source-first-known availability and the required 2160 *eligible hourly* interpretation, then rerun Stage A on independently downloaded keyless public data. Output a BEFORE/AFTER event-delta table for strict/asof macro and Binance leverage, including every changed event day, reason, cluster, left/right censor and provenance digest. If source terms do not permit rehosting the rows, retain scripts, source manifests, counts and hashes only. Exact result must have a fresh independently executed run receipt.
2. OWNER ADMISSION: The original OWNER_READINESS_GATE currently forbids historical enumeration. Owner must explicitly classify public latest-vintage replay as diagnostic NON_OWNER data while keeping canonical PIT/OKX requirements. No metadata edit to silently mark current Gate B PASS.
3. SECOND STAGE, only after source/clock repair and Claude tier0-2 foundation release: rerun frozen MIWF B0/B1/C with revised input lineage and original target definitions, report every delta from the old 4 BSS values; add log-loss, calibration, era breakdown, trial multiplicity and overlapping-label uncertainty. If prospective prereg is desired, create a separate v2 frozen BEFORE the new independent sample, without mining the historical shocks. Original #2162 retains G0/G1 and 21-30d/4-8w ownership; do not duplicate.
4. ECONOMIC ADMISSION: An action-linked paper comparison may begin only after a first-known decision and fill-time series with costs and exposure is frozen. Existing Task2 #1596, risk #1553 and Compass #1516 remain sole execution/science owners. A BTC baseline cannot stand in for a microcap portfolio. No wallet, trade, new scheduler, paid API or live alert.
5. INDEPENDENT REVIEW: Claude checks source clocks, exact changed-head code, challenge test mutation sensitivity and owner boundaries. If any P1 remains, preserve DRAFT/REVIEW_ONLY; never mark APPROVE_METHOD because this report exists. Archive original Bridge report unmodified.

## Falsification, stopping and economic discipline

- Macro null: after method repair, only a time-qualified, source-admitted C-vs-B1 AND C-vs-B0 increment under Holm/multiplicity and across disjoint eras could warrant prospective shadow consideration, not direct promotion.
- Leverage null: match spot-only controls in time/regime/venue, use non-overlapping 72h or valid block inference; if no value net of alert latency and false alarms, record negative and stop rather than add models.
- Kill expansion when: PIT is unavailable; venue lineage fails owner admission; pre-registered sample is too small; C does not beat B0 and B1; result flips under clock revision; placebo matches effect; or after-cost action advantage fails against SMA200 + buy/hold. Negative results count as completed evidence, not empty research.
- Resource cap: zero new paid calls, no new workflows, no forced research dispatch until existing Claude tier 0-2 foundation is proven. A deterministic source-clock repair has higher priority than model complexity. No silent future execution is claimed.

## Measurable owner goals, without a new score engine

| Gate | Success definition | Owner / priority |
|---|---|---|
| G0 Documentation | Original Grok evidence remains immutable; one original-owner-linked method packet; zero new duplicate research owner, workflow or API calls | MAR #209, now |
| G1 Source clocks | Every eligible row has a value date, independently justified first-known timestamp and a deterministic tie resolution; no invented same-day availability | MAR #209 and #1827, prerequisite |
| G2 Replay parity | Before/after delta reconciliation for **all** reported macro and leverage events, clustered counts, missing data and censored rows, across strict and as-of modes; independent execution receipt | MAR #209 and existing HRE/Task2, prerequisite |
| G3 Forecast skill | Corrected model compared against B0 climatology and B1 price-only, 14/21d direction and DD, original frozen splits, full error/calibration distributions, Holm plus regime uncertainty; retain negative outcomes | Task2 #1596 / #2162, after foundation gates |
| G4 Early warning | Lead time measured **before** shock recognition, false alarms per eligible period, missed warnings, 24h/72h correlated outcomes, delivery latency and counterfactual cost against price-only warning | MAR #209 / risk #1553, future pre-registration only |
| G5 Economic utility | No claim without next-fill accounting, costs and opportunity cost; matched buy/hold and SMA200 BTC baselines; no microcap inference from BTC | Risk #1553, no current deployment |
| G6 Controlled adoption | Zero new live forecasts, alert triggers, portfolio rules, wallet fills, schedules or new engines until a separate original-owner, independent review and valid prospective evidence gate | All existing owners |

A gate is **blocked**, not failed, when original PIT/OKX source is unavailable. Success of G0 does not imply G1-G6 are achieved.

## Self-critical review and limitations

1. **Independent calculation scope:** Verified arithmetic from Grok's published summary and reproduced synthetic flaw classes. NOT independently re-run the exact 2015-2026/2018-2026 raw datasets. No independent confidence interval or causal-effect claim.
2. **Potential overinterpretation of tie-order bug:** the 100-row adversarial collision proves unsoundness in a class; the actual H.10 weekly groups are smaller and may not change under a specific pandas build. We require BEFORE/AFTER raw-data delta evidence before marking events invalid.
3. **Potential overinterpretation of funding window:** the July owner contract and Grok L2 differ; the original numeric chain may have deliberately meant settlements for the funding component. If the owner resolves this, preserve both definitions explicitly and classify any changed one as a new version, not as proof of an implementation bug.
4. **Observed signal negatives:** the negative BSS values are plausible, but a corrected as-of panel may change sign, calibration and event inventory. A model trained on revised macro can be a useful historical exploratory proxy without original PIT legitimacy. Do not claim zero probability of a small edge.
5. **Method and ethics:** Retain original failed data, all null states, cold eras and incomplete owners. No private provider values were viewed or exported. No new research hypothesis was selected based on good historical results.
6. **Finality:** This is a completed method-audit artifact prepared for owner and independent reviewer consideration, NOT a completed scientific blind replication, Archive main merge, framework deployment or closed issue #209. Those cannot be asserted without new evidence.

## Acceptance gate for this research-only PR

- [ ] Both artifacts limited to this original-owner research program and reviewed.
- [ ] Synthetic fixture actually executes on final PR HEAD, at least four tests green.
- [ ] No changes to WP04B frozen JSON, model predictions, source owner state, website, market weights or GitHub workflow.
- [ ] Codex feedback on original Bridge #195 is explicitly preserved, not marked resolved by this paper.
- [ ] Independent Claude/Codex review addresses P1 source clock, funding semantics, inference dependence and non-owner lineage.
- [ ] Owner chooses to archive a method-audit only; NOT to promote historical outcomes, v2 alerts or trading.
- [ ] Exact-head CI if applicable, squash merge under normal rules, and post-merge file readback on main; only then change status from DRAFT to ARCHIVED_REVIEW_RECEIPT.

**Recommendation:** APPROVE AS SOURCE-PINNED RESEARCH-ONLY REVIEW after current gates, continue source-clock repairs under #209 and do not initiate a new framework engine. Preserve Grok Bridge #195 intact as source evidence.
