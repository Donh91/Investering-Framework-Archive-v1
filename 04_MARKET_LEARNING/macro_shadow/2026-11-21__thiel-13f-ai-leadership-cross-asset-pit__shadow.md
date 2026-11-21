# Thiel 13F, AI leadership and crypto-contagion: point-in-time Research Lab intake

**Dato:** 2026-11-21
**Status:** SHADOW_ONLY / SOURCE_VERIFIED_PARTIAL / RESEARCH_DESIGN_ONLY / NOT_SCORED
**Område:** Macro Shadow + existing Task 2 scientific research, cross-asset downside early-warning
**Primary folder:** `04_MARKET_LEARNING/macro_shadow/`
**Related folders:** `06_RESEARCH_LAB/`, `04_MARKET_LEARNING/external_research/`
**Supersedes:** Nothing
**Depends on:** Existing PAICE PIT equity-risk study, Task 1.5/Task 2 #1596, Research Lab intake #1512, Strategist #1157, risk-to-action #1553 and HRE source-clock failsafe.
**Owner-approved research intake:** User approved the bounded exploratory mission on 2026-11-21. This does not confer model promotion, market action, live risk-level changes, production scheduling, paid API dispatch, merge or private data access.
**Observed main at preflight:** `11e0855b1a42e469c02bf64a7bd615f6a033f391` at 2026-11-21 11:50:51Z; read the then-current main again before any subsequent action.

## 0. Decision, incremental question and existing overlap

**Primary falsifiable proposition:** Adding publicly knowable information about institutional 13F position changes, AI/semiconductor leadership deterioration, equity breadth and credit/funding stress may provide *incremental* early warning of material BTC/ETH/alt downside relative to the already-published same-clock framework risk state and a mechanical price/volatility baseline, at an acceptable false-alert burden.

**H0:** No economically meaningful incremental warning after correct disclosure-time, legal data-vintage, index/crypto beta, event dependence and false-alarm controls.
**H1:** An identifiable public, temporally ordered risk-transmission pattern improves warning lead-time and/or calibrated decision utility net of false alarms against those baselines.
**Scope:** source qualification, falsification design and later gated shadow research; not a new feature/engine. The case may end as `EXPLANATORY_ONLY`, `REJECTED_FALSIFIED` or `SOURCE_BLOCKED_WITH_TRIGGER`.

**Deduplication:** Extend `04_MARKET_LEARNING/macro_shadow/2026-10-18__paice-equity-earnings-inflation-credit-crypto-drawdown-pit__shadow.md` (merged in PR #1672); do not create a separate macro scorer. Reference the 2026-11-21 existing BTC downside research note under `04_RESEARCH_LAB/external_specialist_dissection/` for W45-W47 failure attribution and existing PR #2284 for VIX/72h stress. Those own any overlapping replay or repair. Reuse Task 2 #1596, existing Risk-to-Action #1553, Strategist #1157, Research Lab #1512, and S1 #1156 without opening a second research queue or a fourth active implementation handoff. MASTER_PLAN_v1 is not modified.

## 1. Source and claim separation, 2026-11-21 preflight

| Claim / observation | Source and actual knowledge clock | Evidence classification / constraint |
| --- | --- | --- |
| Thiel Macro reported **537,742 NVDA shares** as of **2025-06-30** | Official SEC 13F Q2 information table: https://www.sec.gov/Archives/edgar/data/1562087/000131586325000630/xslForm13F_X02/thielmacro2q2025.inftbl.xml | **VERIFIED_HOLDINGS_AT_Q2_END**, not the date/price of any later sale |
| Thiel Macro reported three positions in its Q3 **2025-09-30** 13F, **none NVDA** | Official SEC Q3 filing index https://www.sec.gov/Archives/edgar/data/1562087/000131586325000812/0001315863-25-000812-index.htm and information table https://www.sec.gov/Archives/edgar/data/1562087/000131586325000812/xslForm13F_X02/thielmacro3q2025.inftbl.xml | **VERIFIED_Q3_DISCLOSED_HOLDINGS**, not a proof of precise exit time, proceeds, short exposure or beneficial exposures outside 13F |
| Q3 filing became publicly available **2025-11-14**, SEC index lists accepted **17:08:17** | Same SEC filing index; acceptance clock displayed by SEC, timezone interpretation requires binding before intraday replay | **PUBLIC_FIRST_KNOWN_NOT_EARLIER_THAN_2025-11-14**; NEVER backdate market signal to Sep-30 or an unknown trade date |
| Founders Fund advised portfolio companies concerning SVB around March 2023, bank failed Mar 10 | Fed SVB supervision report https://www.federalreserve.gov/publications/2023-April-SVB-Evolution-of-Silicon-Valley-Bank.htm ; contemporaneous venture report https://www.semafor.com/article/03/09/2023/some-vc-firms-are-urging-founders-to-pull-money-from-troubled-silicon-valley-bank | Distinct legal entity and **SEPARATE_EVENT**, press-observable time required; confidential withdrawals are not publicly predictive features; do not infer that one VC *caused* the run |
| User-provided Nov 2026 chart/social post says Thiel exited at the NVDA top and implies predictive genius | Screenshot provided in conversation; post is an external argument, not primary trade-level proof | **ANECDOTAL / HINDSIGHT_RISK**; historical graph can select winners after seeing outcomes |
| NVDA Nov 20, 2026 official close reported at USD **125.53**; screenshot shows indicative USD 128.59 | Yahoo Finance historical price page https://finance.yahoo.com/quote/NVDA/history/ (as retrieved 2026-11-21); exchange and vendor as-of must be captured at native replay | **SOURCE_BACKED_PRICE_DIAGNOSTIC**, not a November 2025 outcome available when filing was published, and not an independently verified causal effect |

**Crucial nuance:** An SEC 13F is a dated public **holdings snapshot** with a reporting lag, not a trade ledger, timing oracle, full-book exposure map or proof of a genius consistently calling market tops. 13F selection, fund survivorship, amendments, different disclosures, missing short/derivative exposures and delayed public availability must be part of denominator and controls. The 2023 SVB withdrawal cannot be merged with a 2025 13F as if one standardized, tradable public signal existed.

## 2. Research lanes, dependencies, falsifiers, and kill rules

### L1: Institutional exit-source validity (first, precondition for the rest)
- **Question:** Could a real investor have observed the claimed exit *before* the adverse market move, or only a delayed report?
- **Sources:** original SEC 13F filing/accession/acceptance, amendment history, manager identity, exact quarterly tables; contemporaneous timestamped news only.
- **Design:** freeze issuer period end, filing acceptance, wire timestamp, permissible next tradable close and missing reports. Repeat across a complete fixed manager universe, including exits that did *not* precede a drawdown.
- **Null/control:** 13F changes at public filing time, matched random filer, filing without NVDA divestment, filings after equity decline.
- **Kill:** if the apparent success requires knowing the sale before public disclosure, selecting just one prescient manager, inventing the exact trade timestamp or ignoring false alerts. This lane may survive only as `SOURCE_CONTEXT_ONLY`.

### L2: Equity/AI leadership deterioration (parallel after L1 source admission)
- **Question:** Do observable semiconductor/megacap declines, failed rebounds, breadth thinning, concentration and volume/volatility structure lead crypto stress or merely share market beta?
- **Candidate families:** NVDA, SOXX/SMH, Nasdaq-100, index equal-weight vs cap-weight breadth, small vs large equity participation, VIX and yield/credit curves where available.
- **Baselines:** same-clock 1/5/20-day equity momentum, BTC/ETH persistence, BTC vol/ATR, existing published Compass/Pullback severity and always-HOLD.
- **Falsifier:** lead disappears after realistic source clocks, contemporaneous BTC momentum, adjusted common factors, matched alerts and non-event windows. Reject redundant features.

### L3: Cross-asset transmission order
- **Question:** Is there repeatable direction *equities/credit → BTC → ETH/alt* rather than same-session correlation, crypto leading equities, or policy-news shocks affecting both?
- **Candidate stages:** equity leadership/credit deterioration, stablecoin/ETF stress with true publication delays, BTC downside skew, ETH/BTC and alt breadth degradation.
- **Controls:** both forward and reverse lead-lags, market holidays, US cash-hours vs 24/7 crypto, liquidity shocks, time-varying beta, regime/era matched controls, crisis and no-crisis cohorts.
- **Falsifier:** no stable independent directional lead after cohort embargo, alternative ordering, official availability and crypto-first cases; suppress simplistic causal-chain language.

### L4: Hidden risk and mechanism adjudication
- **Question:** Does an observable cross-market deterioration **change** any authorized existing risk-consumer decision, or just explain a move afterward?
- **Method:** trace first-known source → canonical ingestion → risk classification → Compass/CN projection → delivery → outcome. Distinguish contemporaneous risk proof, model band lower-tail miss and consumer-wiring failure.
- **Comparators:** existing PAICE case, #1553 risk-to-action, W45-W47 downside mission and 2026-10-07/08 original forecast/recovery records; never rewrite frozen past forecasts.
- **Kill:** if existing upstream data already knew the risk but the downstream consumer dropped it, send a bounded wiring defect to the *existing owner* instead of creating a new predictive feature.

### L5: Negative controls, selection and false alarms
- **Question:** How frequently do institutions exit and AI leaders dip **without** a crypto crash?
- **Design:** full denominator of preregistered filings/dates, delisted companies and no-event controls, sham managers, lagged/randomized features, clustered events, alternative crisis thresholds and placebo look-ahead features that must fail admission.
- **Kill:** any method relying on cherry-picked successful exits, peak-only cases, posterior window choice, repeated overlapping alerts treated as independent, or headline coincidence.

### L6: Decision divergence and research-to-product handoff (last, dependent)
- **Question:** Could an eligible pre-issued challenger have warned earlier at the **same false-alert budget**, maintained reasonable coverage and changed a genuine consumer classification?
- **Metrics, only on eligible independently matured data:** risk-alert lead/lag and coverage, false-alarm days/year, event recall at matched alert budget, bootstrap by independent event family, interval sharpness, abstention, net economic utility only if an actual authorized action/price/cost policy exists. Brier/log score only for as-issued probabilities.
- **Outcome:** At most ONE primary delta per claim family, with Strategist #1157 disposition; research-to-code only if a reproducible current-owner failure and genuinely incremental evidence exist.
- **Kill:** improved post-hoc explanation alone or extra alert noise with no verified decision benefit.

## 3. Pre-registration and replay firewall

**Initial case is NOT pre-registered as a successful test.** Freeze the following *before* any future outcome scoring:
1. Original source URLs, immutable document bytes/hash and publication clock; issuer period, first public timestamp and file amendments; USD/USDT, equity split adjustments, venue and market-hours boundaries.
2. Fixed asset/universe membership without survivor filtering; source availability by era. Explicit `UNKNOWN` and `SOURCE_UNAVAILABLE` for missing paid earnings and derivatives series; no replacement by subsequently revised economics.
3. Episode-onset definition **before** adverse outcome; candidate horizons 24h, 72h, 7d, 14d and 28d *subject to source coverage*, with a defined non-event denominator, dependent-window embargo, sample-power assessment and negative-control crisis definitions.
4. Separate `ORIGINAL_ISSUED`, `FROZEN_RETROSPECTIVE` and `CHALLENGER_DEVELOPMENT` labels. A later downloaded historical tape proves historical price, not the original investor's contemporaneous ability to know it.
5. Frozen existing-rules champion and simplest-price control at identical clock, signal coverage, alert budget, asset, sample and quote. All compare after the exact public disclosure, **not** at filing quarter-end.
6. False-positive cost (unnecessary risk-off, missed upside) and false-negative cost (late downside notice, undercoverage). Null or negative outcomes are first-class evidence.
7. Full Round 3 firewall: **PROSPECTIVE_COLLECTION_ONLY**, no informal Round 3 hypothesis test, outcome scoring, effect size, PnL or parameter tuning. Round 1/2 are closed. November 2026 observed decline is **RETROSPECTIVE_DIAGNOSTIC**, never a sealed independent holdout after inspiring this study.

Follow `.agents/skills/research-parallel-lanes/references/HRE_REPLAY_SOURCE_CLOCK_FAILSAFE.md`: check fully completed bars, provider timestamp units, missing hourly buckets, overlapping target labels, original vs retrospective labels and true first-available UTC. Freeze source first, then run independent lanes only where existing authorized compute permits; no new workers or API spend.

## 4. Minimal candidate evidence row (reuse existing owner ledger; NOT a second ledger)

```yaml
case_id: RL-CROSS-ASSET-THIEL-20261121
source_evidence_class: SEC_13F | EXCHANGE_PRICE | PUBLIC_NEWS | SOURCE_UNAVAILABLE
claim_class: VERIFIED_FACT | SOURCE_BACKED | HYPOTHESIS | ANECDOTAL | RETROSPECTIVE
manager_or_event_id: null
issuer_period_end_utc: null
source_published_at_utc: null
collector_first_observed_at_utc: null
usable_decision_cutoff_utc: null
source_url: null
source_hash_sha256: null
source_legal_class: PUBLIC | RESTRICTED | UNKNOWN
event_universe_membership: null
champion_version_sha: null
risk_input_first_eligible_at: null
forecast_issue_id: null
consumer_seen_at_utc: null
decision_divergence: NONE | CANDIDATE | VERIFIED | UNKNOWN
falsifier_result: PENDING | SUPPORTED | FALSIFIED | DATA_BLOCKED
missing_reason: null
observation_maturity: NOT_MATURE | ELIGIBLE | CENSORED
scientific_status: RESEARCH_ONLY_NOT_ADMITTED
```

Do NOT populate values from retrospective guesses or mirror restricted source values in public GitHub. The row layout is a schema example, not an executed or registered prospective prediction. Preserve counterexamples and failed/no-alert cases.

## 5. Shortest safe route to an actual result

- **G0, immediately valid:** source and overlap audit; cite SEC exact filings, timestamp and publicly knowable distinction; record candidate evidence class and unresolved clocks. This document is G0 only.
- **G1, next bounded original-owner action:** #1596 Research Lab/Task 2 owners decide whether pre-existing original-source datasets contain sufficient breadth/AI/credit and equity-to-crypto controls for a non-overlapping study; check full source coverage and eligibility **before** modelling or paying vendors.
- **G2, conditional:** preregister one study under the *existing* Task 2/HRE owner with a frozen no-skill baseline and negative controls, or return `SOURCE_BLOCKED_WITH_TRIGGER`. Existing #2284 VIX stress and W45-W47 downside work own their overlapping pieces.
- **G3, conditional on a mature and nonleaky result:** send ONE material difference to #1157 for explicit disposition. If accepted, existing #1553/#1516/#1827/CN consumer owner implements a small reversible shadow patch on a distinct PR, CI, independent review and real original consumer readback.
- **G4:** 7/28-day prospective evaluation under existing collection only, with false-alert and missed-upside costs. No forecast-policy promotion without a separately authorized gate.

**Stop/kill:** fail early if source cannot be shown pre-known, manager denominator impossible, already-covered equity stress baseline dominates, existing consumer-wiring bug fully explains failure, insufficient independent crises, or known approved experiment already measures the same thing. Preserve a short negative finding rather than extra architecture. Escalate `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` only if a future test genuinely requires inaccessible restricted input.

**Budget:** USD 0 paid API for this intake. No new collectors, schedules, model tokens, crypto trades or external paid data. Existing native workflow only with separate actual authorization and verified cost if necessary later.

## 6. Honest completion and review contract

- This note establishes **source triage and test design only**. No simulated strategy results, significance, causal proof, risk-level upgrade, end-to-end agent execution or user-delivered alert is claimed.
- Independent Research Lab red-team checks hindsight, selective Thiel case, manager denominator, source first-known, reasonable falsifiers and alternative explanations.
- #1512 intake ensures dedup and actionable disposition; #1157 adjudicates research; #1596 remains actual scientific owner; #1156 coordinates only after an eligible handoff.
- No integration to Master Monday, official Compass, site, paid provider pipeline, portfolio, risk thresholds or production model in this research-only PR.
- On any future PR, require exact-head CI/review and post-merge source + true consumer readback; green CI or issue comment alone is not completion.

**Provisional Research Lab verdict:** `MODIFY_EXISTING_TEST`, with L1 source verification partially complete and all predictive/economic questions `NOT_EVALUATED`. Current owner handoff state: `NOT_DISPATCHED` pending #1596/#1512 dedup and #1157 scientific admission.
## 7. G1 public-source and first-known feasibility census (2026-11-21)

**Evidence class:** \`SOURCE_COVERAGE_READ_ONLY\`, not a dataset, replay or scoring result. This bounds the source search conducted against the current public Archive and official SEC/available vendor documentation. A zero-result keyword search **does not prove an asset dataset does not exist** elsewhere. All source status statements are as of this bounded inspection, and not a promise of current vendor access or historical ingest.

| Candidate data family | First-party / original-owner evidence | G1 admissibility and next condition |
| --- | --- | --- |
| Thiel Macro 13F | Q2 source via SEC accession \`0001315863-25-000630\`, publicly filed 2025-08-14, 537,742 shares NVDA at 2025-06-30; Q3 via \`0001315863-25-000812\`, public filing 2025-11-14, no NVDA reported at 2025-09-30. See SEC filing index https://www.sec.gov/Archives/edgar/data/1562087/0001315863-25-000812-index.html and 13F FAQ https://www.sec.gov/rules-regulations/staff-guidance/frequently-asked-questions-about-form-13f. | **PUBLIC_DISCLOSURE_ADMISSIBLE_FOR_L1_SOURCE_ONLY**. Q2→Q3 change is observable **only when Q3 became public**. Exact Q3 acceptance clock and exchange cut-off must be pinned before the first actionable US session is declared. Nov 17 2025 is a *candidate* next full cash-session decision date because Nov 14 filing was after US regular hours, not verified intraday execution. No original trade timestamp/price. |
| Full historical manager 13F universe | EDGAR contains original 13F filings, but no point-in-time, amended, fixed-manager denominator has been frozen for this study. SEC 13F rules permit up to 45 days reporting delay and omit short-equity/short-option exposure. | **NOT_READY_FOR_EFFICACY_TEST**. Freeze manager cohort independently of winners, filing-level acceptance and amendments, ticker/security ID, in-scope long holdings and missing/not-filed causes. Do not screen only successful famous exits. |
| Historical NVDA / SOXX / SMH / QQQ / equal-weight equity breadth | Public finance vendors and index/ETF reference offerings identified, but no exact, lawfully reusable full-event equity OHLC + publication/adjustment receipt was verified in the existing Archive for this mission; a code-keyword hit alone is not a dataset. Nasdaq SEP describes coverage of active/delisted stocks as a commercial database: https://data.nasdaq.com/databases/SEP/documentation?anchor=sample-data . | **OWNER_AND_LICENSE_NOT_CONFIRMED**. First locate existing legal equity-source provider or verify truly free historical close + split and delisted-member data. Do not start paid datasets or convert modern adjusted bars into independently proven original publication timestamps. |
| Rates / spreads / VIX / financial conditions | Existing canonical \`04_MARKET_LEARNING/macro_shadow/2026-07-05__fred-classic-targeted-series-production-upgrade__canonical.md\` (blob \`4ef86936af061766e8a92919eff35c2c2acbb912\`) shows targeted FRED demo 43/43 observations, 5/5 metadata, 8/8 vintage probes; supported series include DGS10, VIXCLS, BAMLH0A0HYM2, NFCI. Daily capture weekly \`RELIABILITY_LEDGER.csv\` as read 2026-11-21 reports \`fred_macro 142/645\` across its own historical sampling, *not* individual series coverage. | **PARTIAL / PROSPECTIVE CONTEXT AVAILABLE**. Demo \`BACKTEST_READY_FULL\` is owner-defined acquisition capability, not verified PIT series for every historical stress episode. Construct release/vintage/date joins per candidate, classify stale and holiday gaps; do not assume 645 attempts are 645 independent data days. |
| Historical BTC/ETH markets and crisis/non-crisis labels | Existing \`research/historical_reality_engine/README.md\` (blob \`89f71c655e52cc9d96a4d4c6cb1c963ab4f2c304\`) documents native source-QA for 2020-2026; HRE readback 2026-11-07 and 2022-26 cross-era episodes. Existing \`06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/T2_V1_1_V1_2_RECONCILIATION_v1.json\` (blob \`48b1d3748e34b6e9a92922a017389bb8be76d8ed\`) has dependent cross-asset crisis families; \`framework_warning_data_joined:false\`, \`T3_scoring_performed:false\`. | **RETROSPECTIVE_TRUTH_AVAILABLE, WARNING-JOIN_NOT_ADMITTED**. Historical OHLC is not an authenticated original 2020-2025 issued market warning. No live edge claim; preserve same-quote, complete bar, missingness and dependence controls. |
| Original Compass and risk/consumer records | #1596 original Task1.5 and 2026-11-21 BTC downside mission describe actual W45-W47 issuer/risk-price mismatches; existing 2026-11-15 \`06_RESEARCH_LAB/astra_program_20261116/sources/KOMPAS_G1.md\` (blob \`9ca28bb000fa3e7b6095a79a4da83447266ad106\`) establishes missing long-horizon original issuer comparators and source-clock gaps. | **COHORT_SPECIFIC_ONLY**. Match every candidate public feature to a genuine original forecast issue/consumer at the exact legal cutoff. No retrospective reconstruction of an original issuer decision; #1553 owns prospective risk-to-action consumer tests. |

### G1 finding 1, clock-appropriate horizons are different

A quarterly 13F position-change disclosure is at best a **slow, publicly delayed institutional exposure context**. It must NOT be evaluated as if it were a real-time preceding 24h/72h sell transaction or lead signal at quarter-end. Subject to full manager denominator and power, exploratory 13F effects may be tested at **30/90d post-disclosure** (or another *precommitted* slow horizon), with source clock from EDGAR acceptance and full next-tradable session alignment. 24h/72h crypto outcome windows may be tested separately only as *public-filing reaction studies*, not hidden earlier-sale predictions.

Daily/hourly equity leadership, credit/VIX and crypto microstructure may warrant separate **24h/72h/7d/14d** timing studies, only where actual completed bar and first-known data exist. Do not mechanically merge the late quarterly filing with hourly signals into a fictional ensemble.

### G1 finding 2, several apparent signals already have an owner

The canonical FRED macro owner **already includes credit spreads and VIX**, and the 2026-11-21 BTC downside mission explicitly deduplicates #2284 VIX stress and Task2 T5 change-point/failed recovery. Therefore the first incremental test, once eligible, is NOT “did VIX signal a crash?” but “did *independently new equity leadership* information, available before the issued crypto risk decision, improve alert lead/false-alarm tradeoff over an existing public macro/price champion?” If nothing is new, \`DEDUPED_TO_EXISTING_OWNER\` is the correct result.

### G1 decision and next observable trigger

**G1 disposition: \`SOURCE_COVERAGE_PARTIAL / HISTORICAL_INCREMENTAL_BACKTEST_NOT_ADMITTED\`.** This is a **source and overlap result**, not a negative causal or model-performance finding.

- **Ready:** SEC 13F source chronology; first public Q3 filing; existing FRED macro context *capability*; existing crypto retrospective actuals/method and original issue-ledger owners.
- **Not ready:** legal, source-hashed, continuous equity/semiconductor/equal-weight historical PIT features with fixed universe, entire manager 13F denominator, matched original issuances and complete relative timestamp/price source chain.
- **One bounded next action, if Strategist #1157 accepts:** have existing Task2/HRE #1596 perform a **read-only equity source-owner and rights inventory** with exact provider→source rights→as-of/adjustment→continuity→missingness and candidate experiment controls; record \`SOURCE_BLOCKED_WITH_TRIGGER\` if no qualified free source exists. No new collector or paid feed.
- **Kill at G1:** no legal public historical equity owner with enough coverage for both crisis and non-crisis periods; 13F results dependent on hindsight manager selection; no actual original risk consumer at the proposed decision clock; or G1 overlaps fully with already owned risk/VIX/credit work.
- **Scientific permission:** no R3 testing or scoring, no same-event ex-post classifier tuning, no reporting of PnL, no signal weights, no deployed alert, no site or forecast modification.
- **Review:** new G1 append changes the exact PR head and requires repeat independent Codex review/CI. Do not merge on a previous HEAD’s review.

**G1 bottom line:** The Thiel case is source-verified but does **not** yet establish a valuable predictor. An equity/credit-to-crypto stress lead is plausible, but remains unmeasured. Next money should buy *nothing* until the source and negative-control denominator are truly available.
