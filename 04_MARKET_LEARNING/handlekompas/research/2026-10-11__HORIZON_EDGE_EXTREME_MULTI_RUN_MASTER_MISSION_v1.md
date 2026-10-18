# READ FIRST: HORIZON EDGE EXTREME - multi-run Compass research and implementation mission v1

**Mission ID:** `COMPASS-HORIZON-EDGE-20261011`  
**Issued:** 2026-10-11, Europe/Copenhagen  
**Status:** EXECUTION-READY RESEARCH DESIGN / NOT AN EXECUTED EXPERIMENT  
**User authorization:** design and execute an exceptionally deep, phased investigation; improve **clarity only** of the existing on-demand phone-first Kompas by labelling the jobs of 2–3W, 5–7D and 12–72H. **No changes to current Compass trading signals, governed BUY/HOLD/SELL authority, thresholds, scores, history or model weights.**  
**Home:** `04_MARKET_LEARNING/handlekompas/research/`  
**Existing owners:** #1516 Forward Path Engine; #1553 risk-to-action; #1530 EDGE governor; CN M3/range_baselines; AATA translation audit; Official Compass + Strategic Compass; existing DEL/M6; existing Master Monday and CN precision learning.  
**Start with existing evidence note:** `2026-10-11__weekly_vs_2_3w_horizon_edge_and_portfolio_utility__shadow.md`.  
**This document is an execution spec, NOT proof or permission to auto-trade.**

## 0. Prime directive: maximize INVESTABLE DECISION QUALITY, not scores

Research three distinct questions without pretending they are interchangeable:

**Q1 Price-zone edge:** Can governed 5–7D BTC/ETH weekly high-low *bands* outperform independently frozen simple same-horizon ranges, especially on sharpness, placement and missed-tail severity, rather than broad 100% containment?

**Q2 Direction-and-path edge:** Can prospectively frozen 14D/21D paths detect structural direction, pullback-to-recovery ordering, turning windows and rotation better than matching naive controls? Is the 2–3W thesis useful for avoiding impulsive exits / false altseason purchases, or merely slower?

**Q3 Action-value edge:** Does the proposed dual-horizon interpretation (2–3W thesis -> 5–7D price-risk map -> 12–72H freshness/permission) *actually* improve decision utility for (i) incumbent holders and (ii) fresh capital, relative to the one-horizon approaches and no-action controls, after **decision delay, action availability, fees, spread, slippage, turnover, missed upside, re-entry drag and tail risk**?

Priority if data are limited: rigorous Q1 and Q2 with NO economic edge claim; Q3 stays UNKNOWN until executable-price evidence is admissible. Negative results are first-class learning.

## 1. Explicit existing constraints, fresh-read at EACH run

Every execution round starts with current `main`, HEAD SHA, `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`, `CURRENT_PRODUCTION_DATA_AUTHORITY.json`, operational cockpit and exact owner paths. Respect source-plane visibility and private evidence. The Archive is public. Never publish a wallet address, portfolio holdings, raw restricted data, private hashes/paths, raw PII or credentials in this PR, issue comments, log, or site. For restricted research use only separately authorized private lane; in this public home keep a *value-free* completion status, never private source-derived conclusions.

Read at minimum:
- `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json` and its hash-bound immutable target, `SCORING_CONTRACT_v2.md`, `strategic/README.md`, `STRATEGIC_COMPASS_SCORING_CONTRACT_v1_1.md`; `shadow_v2/` as a challenger only.
- `07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json` and its canonical contract; `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md`; `scripts/data_ping/native_handlekompas.py`; protection tracker, separate SELL/Swing.
- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`; weekly freeze / machine packages; `05_CYCLE_NAVIGATOR/range_baselines/`; internal precision and settlement protocols; `06_RESEARCH_LAB/m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md`.
- `05_CYCLE_NAVIGATOR/internal_learning/research/2026-10-10_master_audit_work_receipt_v2/EXECUTIVE_REPORT_AND_HANDOVER.md` with its **partial/temporal-limit** warnings.
- `research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/analysis_to_action_translation_audit_v1/ERROR_TAXONOMY_AND_SCORING_CONTRACT_v1.md` and `PROSPECTIVE_CAPTURE_CONTRACT_v1.json` for existing analysis -> price -> action -> timing -> utility decomposition. Never create competing error taxonomy.
- `06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/CHARTER_v1.md` and M6 T2 1.1/1.2 episode family rules; existing warning/delivery owners; DEL and portfolio-owner contracts.
- GitHub #1516, #1553, #1530, PR #1573, active PRs modifying the exact files being touched, live queue state; dedup and preserve existing higher P0 mission. Do not assume old PR/issue snapshots still govern.

**Evidence already known (not a new measurement):**
- M3: 4 correlated asset-week rows W39–W40; CN weekly band *alpha not demonstrated*; CN lost Jaccard 3/4 against each ATR band; retrospective baseline formation was not an original frozen prospective series; independent native weekly benchmark starts W41.
- Public master audit: pinned 142 official freezes / 426 horizon rows / 319 outcomes / 107 missing. The selected 29 scored BTC 168H forecasts yielded 27/29 correct, **ALL SIDEWAYS**, with 55 abstentions, ±5% sideways tolerance. A selected 21-row BTC12H UP/DOWN comparator was 9 correct/12 wrong for both Compass and persistence. This is **NOT a market direction-trading edge**.
- Audit publication/first-knowledge time remains unresolved; strong PIT admission requires additional evidence.
- 2–3W current CN is not automatically a comparable frozen numeric 14D/21D band. The existing strategic anchor is **21–30D**, never silently relabel it 14–21D. No matched 7D versus 14–21D economic winner is established.
- `WARNING != SELL`; `LIVE_EXIT_RULE = NONE` absent a separately governed permitted owner. `BUILDING` is not a sell trigger. Never convert directional evidence to a BUY/SELL permission.

## 2. Mission control / multi-session protocol (MANDATORY)

Execute in **distinct rounds** with a bounded durable receipt after each. Every round:
1. Fresh-read exact HEAD, compare the last checkpoint against current owners/PRs, list nonduplicative changes and accepted pending gates.
2. Keep one branch/PR per *coherent reviewed change* and one research-only mission/receipt stream under the existing owner's territory. This PR #1573 may hold ONLY additive public research/design docs. Execution code, presentation copy and scoring changes use independent owner-scoped PRs, after scoped review. Do NOT use this design PR as a production release.
3. Record `run_id`, `parent_checkpoint_id`, `main_head_sha`, `source_owner_paths + hashes`, `PR/issue map`, `eligible/blocked counts`, `completed stage/acceptance tests`, `findings pro+contra`, `next_exact_action`, `manual_blockers`, `consumed cost/time where knowable` and `roll_back`.
4. Use existing research governance and trial registry. Dedupe by hypothesis/owner/target/outcome/time. Never silently re-run failed stages as independent N. Retry idempotently and disclose failures.
5. After every stage produce a *machine-readable stage receipt* AND a five-line Danish human handover, suitable for another Work/Codex/ChatGPT/Claude thread. Public receipts must be value-free on restricted scopes.
6. Stop/continue rules: continue within the authorized safe mission as tools allow; if privacy, evidence, capital/credential, missing source, independent-review or destructive-separation gate fails, fail that lane closed with a deterministic block code and move to another independent safe lane. Do not mark a blocked stage PASS, ask user to copy raw data, or wait invisibly. No requirement for a new scheduler. A future chat must explicitly invoke another round or an already established approved owner runner.
7. **Approval ceiling:** this message approves research execution and optional *presentation-only* quality updates. It does not authorize automated portfolio trading, new SELL rules, private data publication, CI bypass, new paid service, new budget outside existing guard, or unconditional merge of production changes.
8. No late-stage claims from unperformed work. If only a dry-run or PR was created, record `STAGED_NOT_EXECUTED` and the next runnable action, never `DONE`.

### Recommended execution batches, with parallelism limits

- **Run A**: R0 governance/owner graph + R1 provenance & denominators, and UX0 presentation-only independent candidate. Parallel read-only agent tasks allowed; single integration writer and no competing owner modifications.
- **Run B**: R2 weekly range research + R3 multiweek direction/path research *design/prospective admission*. Safe parallel work when exact frozen data are disjoint; one adjudicator reconciles.
- **Run C**: R4 actual decision economics/lead-time study + R5 adversarial falsification and ablation *where eligible evidence exists*. If economic admission is blocked, deliver honest blocked report and improve read-only source health, not synthetic returns.
- **Run D**: R6 prospective monitoring/maturation handshake + R7 independent review, system verification, Master Monday feedback and closure/adjudication. Revisit after enough genuinely matured, independent future windows, not repeated polling to manufacture N.

Run order is dependency-governed; UX0 is authorized presentation-only after R0 independent source/contract preflight. Do not hold a harmless wording correction hostage to months of outcome maturation.

## 3. R0 - owner-boundary graph, branch dedup and pre-registration freeze

**Task:** map current data and authority path end-to-end:
`point-in-time owner capture -> market packet -> native observation -> official frozen horizons -> protection / SELL boundaries -> weekly CN + strategic anchor -> outcome scorer -> decision economics -> Master Monday precision learning -> on-demand Kompas renderer/site consumer`.

**Output:**
- Owner graph: names, current exact sha/path, generation cadence, source health, freshness SLA, output schema, maximum authority, historical version boundaries, scheduler/CI, fallback.
- Dependency graph for #1516 #1553 #1530 and PR #1573. Identify existing owner doing each work item; categorize `REUSE / EXTEND / REPAIR / BLOCKED / NOOP`.
- Baselines, inclusion/exclusion, primary/secondary endpoints, regimes, economic assumptions and planned variants preregistered **before** inspecting future outcomes. Fixed research protocol SHA, publication and first-knowledge eligibility policy.
- Resource estimate: simple deterministic calculation first, bounded Sol adversarial review only on material evidence/owner differences; never trigger expensive all-history reanalysis by default.
- Adversarial challenge: does planned work actually create a different decision than official owners can already support, or only better prose? If only prose, cap scope at UX0 and observation.
**Gate R0:** `OWNER_MAP_PASS && PRIVACY_BOUNDARY_PASS && NOVELTY_CHECK_PASS && PRE_REGISTRATION_FROZEN`. Missing gate => dry-run/blocked.

## 4. R1 - source truth, cohort recovery and independent unit construction

**Objective:** rebuild the *denominator* and exact time semantics, not recover flattering scores.

**Steps:**
- Reproduce pinned public audit from exact immutable Git tree, verify original start/target/reference close timestamps, hash binding and missing rows. Publication-time UNKNOWN is not promoted to verified merely by freeze hash.
- Group by *one decision timestamp* and *one independent market family*, not `asset x duplicate daily freeze x overlapping window` as independent successes.
- Cohorts: original published CN issues (legacy source provenance); current automated weekly freezes; Official Daily Compass 12/72/168h; existing strategic 21–30D; future 14/21D #1516 prospective rows. Era labels prohibit pooled "overall" score.
- Classify each row: `PIT_VERIFIED / EVENT_TIME_PROXY / RECONSTRUCTED / UNTESTABLE`; `PENDING_MATURITY / MATURED / CENSORED / MISSING_TARGET / SOURCE_CONFLICT / ABSTAIN`.
- Differentiate scoring-v1 versus scoring-v2 effective horizons and candle open/close semantics; no daily close labelled future evidence, no gap interpolation, no cherry-picked provider.
- Deduplicate same-episode BTC/ETH price shocks and repeated same-week/range snapshots; retain asset-specific metrics without inflation of independent N.
- Construct regime strata only from features genuinely known at cutoff; no unverified microcap or altseason proxy as a label of actual execution.

**Output:** audit-graded cohort manifest with total eligible, pending, excluded by reason, sample-family IDs, source availability, regime counts and strict controls. **Acceptance:** independent replay identical on two runs, source hashes match, deliberately negative fixtures rejected. If required evidence inaccessible, isolate that cohort; never fill missing values.

## 5. R2 - price-range championship (5–7D and 14D/21D when eligible)

**Question:** does a better band identify better **usable prices**, not just minimize public scoring embarrassment?

**Controls at identical source cutoff/horizon:**
- Native independently frozen CN weekly baseline W41+.
- Existing DUMB1.5/DUMB2.0 ATR methods only within their correctly admitted/era version.
- Frozen naive prior-week excursion/range carry and equal-horizon realized-volatility proxy if predeclared.
- Raw CN official 7D band, optional frozen 14/21D #1516 band after it exists and was frozen BEFORE outcome. Never manufacture 14/21D numeric bands from `MIXED`, a 21–30D anchor or textual forecast.
- Challenge sign-specific volatility and transition stability; do NOT optimize 17 parameter grids on 2 weeks.

**Primary technical metrics** separately asset/horizon/regime:
1. full realized-window extrema coverage and daily close containment, **never conflate them**;
2. upper/lower miss depth as percent at true decision-time reference, not percent at later convenient close;
3. band width / realized range width, Jaccard IoU with actual full span, midpoint and tail error;
4. proper interval/Winkler score at predeclared coverage, use valid matched interpretation, never score after picking winner; calibration/reliability by bands;
5. volatility/range normalization `width / as-of ATR or permitted pre-freeze scale`, plus breach magnitude in units of risk budget;
6. **sequence blind spot:** whether low preceded high, adverse excursion before terminal profit; a high-low *set* cannot predict order.
7. sensitivity to 24/7 crypto close conventions, Binance vs canonical governed owner basis, and horizon anchor drift.

**Horizon fairness:** 7D versus 21D raw interval widths are NOT directly comparable because 21D exposures are longer. Compare each arm's *incremental lift vs its own matching horizon baseline*, and compare economic action decisions from identical initial cutoff, common evaluation horizon and normalization. Where no eligible 21D band exists state `NO_PAIRED_RANGE_COMPARISON_YET`.

**Score guarding:** public CN Price Range Precision remains immutable and exactly the published continuity formula. The research tables may report independent width/utility, never overwrite or recompute legacy public scores.

**Stop:** no claim of robust 7D range skill until sufficient genuine prospective independent weeks, stress-regime breadth, baselines and adversarial replay. A 4-row test is discovery only.

## 6. R3 - market direction, path and turning-window tournament

**Question:** is the 2–3W **ordered price path and capital rotation** more useful than its terminal direction?

Create only through #1516 prospectively frozen 3–7D / 8–14D / 15–21D checkpoints, governed structured `source_at / first_known_at / issued_at`, tentative scenario envelope, falsification and selected horizon. 22–30D must remain separately tied to eligible CN strategic owner; 4–6W is SHADOW, 4–8W governed CN structural overlay. Do not create an independent long-horizon truth owner.

**Before outcomes:** pre-register for each horizon/asset:
- `UP / DOWN / SIDEWAYS / MIXED / NO_EDGE / UNAVAILABLE` with exact scoring meaning. No automatic conversion of MIXED/NO_EDGE into CORRECT when the result is mild. Define and count actual **directional participation** and *abstention*.
- terminal signed return, max adverse and favorable excursion, sequence labels (down-then-up/up-then-down/continuation/sideways), major path checkpoints and turning/reversal windows only when forecast gave explicit operational bounds.
- base/bull/bear **scenario weights** are not predictive probabilities until independently calibrated; NEVER report these as win probabilities.
- separate BTC, ETH, ETH/BTC, broad alt participation, leadership, microcap conditional permission and memes separately governed/unavailable.
- two levels of forecast: original frozen analysis thesis vs price-range/action translation, honoring existing AATA error taxonomy.

**Controls:** same-horizon no-change/persistence, naive momentum reversal/continuation, volatility-scaled signed-return prior, frozen cycle regime, and straightforward no-rotation control. Freeze each control before outcome. Stable timescale and no peeking at later outcomes.

**Outcome:** conditional directional skill on *UP/DOWN eligible forecasts*, separately SIDEWAYS coverage and abstention; balanced accuracy and confusion by realized signed-return bins, class balance, Brier/log loss ONLY if genuinely calibrated probabilities were preregistered; path edit distance or ordered event error only under predeclared deterministic definitions; turning event first-knowledge/executable lead time; missed and false transitions. Report directional increment **beyond** simple baseline, not forecast class accuracy alone.

**High-value failure modes to seek deliberately:** (a) model says MIXED while significant downside risk grows, (b) accurate late week-close but intolerable midweek drawdown, (c) 2–3W stale bullish prior despite source deterioration, (d) correct regime but wrong BTC/ETH capital hierarchy, (e) overdefensive abstention during violent rebound, (f) false altseason ignition because proxies lag, (g) failed producer maturation/latency makes a correct eventual call useless at decision time.

## 7. R4 - risk-to-action and portfolio economics: ONLY with real admission

**Existing owners:** #1553 protection / M6 EDGE-001 for warning information; DEL/AATA and portfolio owner for economic utility. Warning events are not sell decisions. No permission from this mission to use a real wallet or trade.

**Separate populations:** incumbent-held exposure and fresh cash. An existing holder baseline is to hold; fresh cash baseline is wait/cash. Never score `HOLD_WAIT` as a protective realized sale. Never assume a meme or microcap could have been liquidated/rebought at a BTC benchmark close.

**Experimental arms, frozen before outcomes:**
- B0-H old exposure held unchanged; B0-C fresh capital uninvested (separate outcomes).
- B1 transparent price-only/volatility-only price/control warnings under equal data/clock.
- A7 weekly map decision-support and existing governed action, if any.
- A21 14–21D context / #1516 path, if prospectively admitted.
- A7x21 context plus weekly map plus 12–72H owner permission; same capital, permission universe and action availability.
- Optional risk-review-only `COUNTERFACTUAL ACTION CANDIDATE`, if owner preregisters it in governed research; never retro-label as live trades or as current SELL.
- Same risk budget, legal information time, forecaster latency, verified delivery time, first executable time, timing delay, spread, fees, slippage, liquidity, size constraints, imperfect fill and no hindsight trades for ALL arms.

**Primary economic endpoint:** matched **net utility and drawdown-aware distribution** on the SAME eligible independent shock families, *separately* for incumbent vs cash, with a predeclared vector:
- net wealth against B0/B1; max drawdown, drawdown avoided, worst-event loss, tail/CVaR when enough regimes;
- opportunity cost from false trims, missed rally, churn, re-entry drag, time out of market;
- early warning lead beyond price-only, false-positive warning days and false-negative missed shock families;
- MFE/MAE, path-dependent order, re-entry availability, first-executable latency and no-fill rate;
- coverage, abstentions and missingness for every arm.
- Tax is an explicitly disclosed sensitivity requiring actual tax assumptions and legal review, NOT built into invented generic friction.

**Stop/negative-control rules:**
- If delivery timestamps, decision rights, price/volume tradability or private execution tape are inadmissible => `ECONOMIC_EDGE_NOT_MEASURABLE`; deliver only information-edge accounting.
- If no action differs between arms => `NO_DECISION_DIVERGENCE`; no "economic uplift" even if narrative improved.
- If after-cost effect disappears under modest fees/slippage/latency, a few events, regime balance or negative controls => kill/retain as descriptive.
- If results are mostly from selected crashes but fail on V-shaped rebounds and pumps => not robust risk-to-action edge.

## 8. R5 - extreme cross-examination, stress tests, multiple testing and mechanism tests

**Adversarial reviewers (independent roles, not presumed installed):** one code/provenance verifier, one quant/statistics falsifier, one risk/economic adversary, one UI/authority reviewer. Parallel reads allowed. No paid model calls unless current guard permits and a material outcome could change decision.

**Stress matrix**, *only if time-admitted sources permit*:
- consolidation/grind up/grind down, fast crash, V-recovery, prolonged drawdown, liquidity drought, rotation false-positive, BTC-leadership ETH-relative recovery, genuine broad alt rotation;
- trend strength vs short-term volatility expansion, ETF/liquidity/news shocks, stablecoin claims independently verified, weekday/weekend market behavior; onchain/sentiment factors only after PIT and independent incremental tests;
- as-of recording gaps, stale official pointer, conflicting source clocks, delayed publication, revised provider data, cutover across scoring v1/v2, censored outcomes;
- negative-control shuffles inside regimes, embargoed label permutation, time-scrambled warning matched controls; do not break temporal autocorrelation unreasonably;
- exclude extreme winning episode and remeasure effect; leave-one-family-out, leave-one-era-out, BTC vs ETH correlated episode family grouping; ablate 2–3W context, 7D map, 12–72H freshness one at a time.

**Statistics:**
- never treat `142 x 3` overlapping daily horizons as 426 independent bets;
- report N independent episode families, cluster-aware uncertainty (block bootstrap/time series clustering), conditional performance, eligible/missing, comparator gaps;
- multiple hypothesis penalty and held-out prospective test, no param selection on evaluation outcomes, global trial denominator and every attempted variant logged to existing research governance;
- preregister practical materiality threshold per component with owner and economics. If no defensible sample-size bound, result is `INSUFFICIENT_INDEPENDENT_FAMILIES`; do NOT turn arbitrary `N=50` into proof.
- no artificial alpha confidence or probability adjectives without realized calibration.

**Required red-team questions:**
1. Are 2–3W calls just weekly forecast restatements with autocorrelation?
2. Does apparent 7D reliability come from predicting SIDEWAYS too often?
3. Are intervals merely wide enough to make misses rare?
4. Is 2–3W "accuracy" credited using an unregistered scenario or changed forecast?
5. Does any improvement survive naive trend/ATR, independent regime family and actual data availability?
6. Did advisory warning ever reach a *tradable* decision before the episode?
7. Does existing-holder utility disagree with fresh-capital utility?
8. Does the proposed hybrid add a different action or just persuasive narrative?
9. Are parameter choices, research variants and test repetitions counted?
10. Does cost-adjusted benefit remain positive on late signals, thin liquidity and V-recovery controls?
11. Would a skeptical professional investor be able to reproduce it entirely from immutable source and cutoffs?

## 9. R6 - forward freeze, maturation and compounding learning

**Do NOT** create a second forecasting engine, new scheduler, or duplicate weekly precision owner. Use #1516's proposed immutable 3–7D, 8–14D, 15–21D checkpoints and existing strategic maturation machinery, after schema and PIT gates. Use the established CN independent weekly baseline and weekly scoring/learning owner; no new Cron.

Every matured family produces:
- immutable source/forecast/outcome join with `knowledge_at`, `published_at`, `first_executable_at`, precomputed control and all eligible arms;
- named error causes from existing AATA, CN learning and risk-to-action taxonomy;
- **single, bounded, value-of-information based improvement proposal** when actionable: `KEEP / INVESTIGATE / FALSIFY / REVISE_DRAFT / NOOP`, research only;
- cumulative prospective learning curves by independent family, horizon, regime and owner version; positive AND negative results and drift;
- new questions go to existing Research Governance/EDGE governor only upon material novelty, not a daily proliferation of mini-agents.

No model self-retraining, threshold shifts, new action weights, range replacement or automatic policy promotion. Master Monday ingests only eligible matured owner outcomes; otherwise `NOT_ADMITTED_TO_LEARNING`.

## 10. UX0 - approved immediate presentation enhancement to EXISTING Kompas, SEPARATE implementation PR

**The user has explicitly approved clearer presentation of the three roles.** This is presentation only; it MAY be executed after R0's source/contract preflight, without waiting for economic alpha proof.

Retain the two mandatory, narrow, three-column Markdown tables in the chat invocation contract EXACTLY:
1. `Mit taktiske Kompas`: `Tid | Retning | Handling`
2. `Aktivklasser`: `Aktiv | Status | Handling`

Retain all mandated asset rows, horizon coverage, separate SELL/Swing/protection/reentry, timestamps, one bounded `🧠 MIN FORTOLKNING` and prohibition of widgets.

**Minimal UI interpretation band**: one short, clean *text-only* block adjacent to the tactical table:
```text
LÆS KOMPAS I TRE LAG
2–3 uger   · Markedsforløb / kapitalrisiko   [kildebundet status eller UKENDT]
5–7 dage   · Taktiske BTC/ETH prisområder     [kun frosset interval; ellers UKENDT]
12–72 timer· Aktuel bekræftelse / handling   [kun eksisterende officiel handling]
```
Use human concise wording, no extra machine direction/classification, dates only from authoritative timestamp/horizon. The three roles are **functions of horizons**, not assertions that alpha has been proven.

Suggested near-table micro-labels (as formatting only, not new score):
- `2–3 uger: HOVEDRETNING / SCENARIE` (only when actually supported; otherwise `UKENDT`).
- `5–7 dage: PRISOMRÅDE / RETEST` (do not show number if source is missing or expired).
- `12–72 timer: BEKRÆFT / AFVENT / eksisterende KØB/HOLD/... permission`.
- If horizons disagree, show `KORT/MELLEM HORISONT UENIGE` as descriptive English/Danish copy only, never force an action downgrade.
- Show e.g. `Interval er et udfaldsrum, ikke et forventet indkøbsniveau`; compact 1 sentence, only when numerical ranges are actually shown.
- A source-bound note `RETNING ≠ HANDELSTILLADELSE` when direction and action differ meaningfully.
- Explicit `Frosset: ... / gyldigt til: ...` when the owner provides it; older 12H is NEVER stretched into 24H.
- `ENDELIG PULBACK/SELL SIGNAL: IKKE BEKRÆFTET` only if owner actually supplies that safe classification; unknown remains unknown.

**No new objects** on website by default: the user requests *current on-demand Kompas*. The public site is a later separately reviewed optional presentation extension, never a new truth owner. No denser tables, larger screen height, colored badges, charts, GenUI widgets, hidden scores, shadow-to-official promotion or new notification.

**User acceptance snapshots/tests:**
A. Mixed 2–3W + bearish 12H + HOLD: outputs differing direction/action correctly.
B. Strong 7D trend + unavailable 14–21D: no synthetic longer view.
C. Stale official 12H at hour 20: no 24H extrapolation.
D. Missing weekly range but available strategic thesis: range remains unavailable.
E. Missing private portfolio/SELL owner: no `REDUCER/EXIT` fabricated.
F. Shadow disagrees with official: shadow noted separately, not promoted.
G. Degraded optional news but accepted market data: traceable caveat, not arbitrary bearish call.
H. Meme/microcap separation, mobile width no more than three columns, no widgets.
I. Public/privacy inspection of exact presented fields.
J. One-word `Kompas` invocation returns both tables without clarification.

**Gate UX0:** reviewed copy diff; no changes to `scripts/learning/*` forecast/scoring, decision operators, producer models, governance and site unless a separately approved narrow presentation-only site PR; snapshot tests and explicit role-vs-action invariants; independent exact-head review; main readback. If route contract change requires version bump, use additive backwards-compatible prose renderer version without historical rewrite.

## 11. R7 - adjudication and deployment/closure rules

**Each major stage gets its own verdict**:
`PASS / NEGATIVE_EVIDENCE / INSUFFICIENT_DATA / SOURCE_BLOCKED / TEMPORAL_BLOCKED / REVIEW_PENDING / NOT_RUN`.

Report **seven separate scores/claims**, never a false all-in precision:
- source/clock integrity and missingness;
- weekly 7D range incremental alpha;
- 14–21D direction and path incremental skill;
- warning lead/failure;
- net incumbent economic utility;
- net fresh-capital utility;
- UI information clarity with zero authority leakage.

**Falsification stop/kill:** Any broad edge claim fails if gains disappear with same-clock naive comparator, costs, denied time/source, hidden abstentions, unsupported 14–21D freeze, family independence or blind replication. Prefer `NOT_DEMONSTRATED` to `PROMISING` when statistical evidence is underpowered.

**Promotion firewall:** This master mission never itself changes official Compass market state, accuracy scoring, trading execution or portfolio weights. Meaningful future action changes require independently approved prospective owner-specific contract, new version, evidence of after-cost decision lift, independent review, CI, exact-head merge, readback and rollback. Future site UX review cannot overrule this.

**Completion means**:
- this written research mission has exact source/evidence/gates and working multi-session receipts;
- UX0 presentation PR either verified and merged with clear before/after test, or recorded `REVIEW_PENDING` with exact linked blocker;
- no unfrozen numeric 14–21D bands;
- a reproducible matched range/direction report *or an explicit quantified, source-backed admission gap*;
- #1516 and #1553 have non-duplicate bounded follow-up handovers;
- prospective test and owner maturation integration built/verified if admitted, otherwise `PENDING_FUTURE_MATURITY` and original Kompas remains intact;
- exact PR/issue/commit links, tests and two-tier user and machine-readable closure.
- **Do not declare market edge demonstrated just because infrastructure work was completed.**

## 12. Hard prompts to execute stages across separate Work/Codex runs

**Start command:** `Read this exact document and accompanying mission manifest at the current PR #1573 head. Fresh-read main/owners. Run the earliest incomplete stage in the dependency graph, now. Use the stage acceptance gates, archive an immutable checkpoint via the appropriate existing owner, and finish with next exact stage. Re-run only if the stage has changed or source SHA moved materially.`

**Continue command:** `COMPASS-HORIZON-EDGE-20261011 CONTINUE. Resolve latest verified checkpoint, current main SHA, current #1516/#1553 status and pending gates. Execute next admissible stages; don't repeat already verified analysis, and report blockers precisely.`

**Review command:** `Adversarial review COMPASS-HORIZON-EDGE-20261011: try to falsify PIT, denominators, baseline independence, sideway/abstention inflation, asset-family correlation, action economics and privacy. Produce an evidence-bound counter-verdict; no write to canonical market state.`

## 13. Required final human report (Danish, mobile-first)

```text
MISSION: COMPASS-HORIZON-EDGE-20261011
RUN: A/B/C/D | STAGE: R0..R7 / UX0
KILDER: exact main/head SHA | data PASS / DEGRADED / UNKNOWN
UDFØRT: concrete commits/PRs/tests, not aspirations
RESULTAT: what is supported, falsified, and not measured
EDGE: range / direction+path / warning / incumbent / cash (separate)
KOMPAS: presentation unchanged / scoped PR / verified merged; trading logic UNCHANGED
NÆSTE: one precise owner, action and gate
LINKS: exact GitHub URLs
```

## 14. Research execution ethics and budget

Existing API guard is binding. Cheap deterministic / existing evidence first, GPT intelligence only if likely to change an admitted research decision; no mass-token ingestion, unbounded agents, duplicate schedulers, paid external datasets or cost explosions. No "auto run until finished" promise across future conversations without a real existing configured orchestration runner. All future user sessions follow durable owner checkpoints. Preserve independent recovery/destructive authority separation under `AGENTS.md`.

**Definition of value:** a disciplined system that is measurably earlier and more useful for capital-protection decisions than a naive reference, *not* a system that says it is accurate.
