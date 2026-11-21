# Pre-Fable Independent Strategic Intelligence: risk truth, scientific closure and research leverage

**Dato:** 2026-11-21  
**Status:** SHADOW_ONLY / INDEPENDENT_RESEARCH / NOT A RELEASE AUTHORIZATION  
**Område:** Research Lab, Task 2, Kompas, S1, Alpha Lab, Fable Tuesday  
**Primary folder:** \`06_RESEARCH_LAB/reports/\`  
**Primary owner:** Existing Research Lab #1512, Strategist #1157; implementation authority stays with domain owners #1596, #1553, #1827, #1516 and S1 #1156.  
**Current comparison:** Bridge \`claude/log/reports/claude/plan/MASTER_PLAN_v2.md\`, \`FABLE_TUESDAY_MANDATE_v2.md\` and \`FABLE_TUESDAY_MANDATE_v2_ADDENDUM_1.md\`, inspected 2026-11-21.  
**Scope:** independent source review, external method scouting, adversarial objections and an optional bounded Fable clarification. **No production changes, code, backtest outcome scoring, paid model call, trading permission or new task.**  
**Archive choice:** one reviewable research note with existing owners, not a new engine, source authority, registry, test or mandate.

## Executive decision

**Keep Fable Tuesday 24 November focused. Do not add another engine, regime model, backtest, OpenAI/Claude agent or research workload to that session.** The highest-value work remains the already-authorized W5+D2 re-chain (~25%), AUDIT-04b plus #2276 completed-close and packet-integrity fixes (~55%), and only-if-capacity W4/W6/A11 (~20%). A useful independent research delta is *semantic precision*: distinguish four observable facts that existing prose and some proposed code risk collapsing:

1. **Source/data freshness**: When was each observation available to this issued packet, and is its clock/quote/source binding eligible?
2. **Forecast factual validity**: Has a completed, source-admitted close breached a frozen daily/weekly floor? What day, asset, target, venue/quote and canonical original freeze?
3. **Risk-decision provenance**: Was the risk/protection classification recomputed from admitted new evidence, or carried forward from an older issue?
4. **Consumer delivery**: Was the current signal actually served by Pages and readable by its intended user? A merge or built artifact is not an alert receipt.

The Fable v2 specification's instruction that a completed-close floor breach makes \`risk_freshness\` 'at least STALE' is practical for exposing an inherited decision, but risks conflating **forecast invalidation** with **source staleness**. This is a *design concern*, not a demonstrated code bug in the still-unbuilt patch. Preserve \`risk_freshness\` as proposed, but demand separately inspectable, typed \`source_freshness\`, \`forecast_floor_status\` / \`cn_band_status\` and \`risk_state_basis\` with reason/clock/binding. When a floor breaches, the consumer must say that the *frozen expectation was broken*; it must not claim a newly calibrated bearish forecast, an automatically authorized SELL, or a fresh risk classifier.

**No evidence obtained here establishes incremental price prediction, avoided drawdown, executable microcap PnL or economic alpha.** The recommendation concerns epistemic honesty and measurable delivery, not performance promotion.

## Live source audit: what is fact, not inferred completion

| Evidence | Direct source | Finding and immediate disposition |
|---|---|---|
| Current plan pointer | Bridge \`reports/claude/plan/CURRENT.md\`, blob \`65d987ef52736464743778e82471879f578e4888\` | References Masterplan v2, Tuesday mandate v2 plus Addendum 1; Fable exact-version owner GO is separate. |
| Tuesday frozen proposal | Bridge \`reports/claude/plan/FABLE_TUESDAY_MANDATE_v2.md\`, blob \`46c182be4aacb3e2beb6a8b5af045bfd8e67695d\` | Bridge-only Fable output, no new runtime permissions; ~25/55/20 split. Part 2 explicitly allows REJECTED/UNTESTABLE if defect cannot be reproduced. |
| Completed-close extension | Bridge \`reports/claude/plan/FABLE_TUESDAY_MANDATE_v2_ADDENDUM_1.md\`, blob \`3a3fd6b254bac831abdd2e0702524e50434d7841\` | Exact schema consumer census, official packet ID versioning, original hourly Git 23:00 UTC close, Sunday next-week boundary, candle timestamps, real hash oracle and mutants are already specified. Do not create duplicate ticket. |
| Inherited protection source | Archive \`scripts/cycle_navigator/weekly_offline_issuer.py\`, blob \`37bb9fda86078ec9b1e5a838066c5cef06a75685\`, lines ~180-198 | K11 comments and assignments explicitly carry prior protection state and mark \`INHERITED_FROM_PRIOR_ISSUE\`. It does not recompute protection. |
| Official packet wiring | Archive \`scripts/data_ping/native_handlekompas.py\`, fetched 2026-11-21, official \`build_official_compass\` area ~1569-1712 | Packet constructs action, horizons, protection and data_status from multiple owners. \`compass_id\` includes schema version, so an incompatible schema edit can affect immutable slot identity. A packet source read is not proof of alert delivery. |
| W47 original freeze | Archive \`05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_FORECAST_FREEZE.json\`, blob \`1e72eb62e2da2f164a0da4108a4cf5f51b910f41\` | BTC/ETH USDT daily ranges and exact week are frozen. This allows factual comparisons, NOT ex-ante edge claims. |
| #2289 public truth banner | [Archive PR #2289](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2289) | **Merged** when checked. Real served-CDN root + \`data/compass.json\` readback was not established in this research session; classify \`MERGED; SERVED_UNVERIFIED_HERE\` rather than closed. |
| #2276 official band status | [Archive PR #2276](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2276), checked head \`c89b111f5a5462df8a426e137e8b5265f600c0be\` | OPEN DRAFT, not merged. Issues are appropriately absorbed by Fable Part 2. Never assume the completed-close producer is already live. |
| W47 scorecard | [Archive PR #2292](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2292), head \`594307e891531e6da85bc71a5b42762e57266c67\` | OPEN DRAFT; frozen first-mature score needs the actual 23 Nov maturity before honest public display. B1 stays unavailable absent immutable matched row. |
| Risk02 | [Archive PR #2284](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2284) | \`W48 NOT_ADMITTED\`, W49 SCIENTIFIC_HOLD. First-known B1 and other clocks unproven. Do not retro-admit. |
| Alpha | Bridge \`MASTER_PLAN_v2.md\` blob \`0c34d7f93cdce21c43586f687b8aa468f34f8450\`, P2 | Strategy Arena currently lacks an admitted input producer; denominator missing and actual trades zero in the checked snapshot. This is a *product evidence gap*, not proof a strategy fails or wins. Verify fresh MAL before implementation. |
| Additional source defect | [Archive PR #2293](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2293), OPEN DRAFT | Synthetic OKX OI parser fixture reproduces unit ambiguity: positional base amount treated as USD in two positives. This is a research-local example of why signal provenance/units can dominate smarter models. Existing #387/#2267 owns the repair. |

For Fable and implementation, **always refresh HEAD, main, rule and issue state at execution time**. The rows above are dated observations, not permanent readiness assertions. Source-of-truth precedences are in Archive \`AGENTS.md\` (blob \`18b6dbbe4adbeb2660590dc14cdb9e2ef3714994\`), \`00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md\` (blob \`c8ead1b0e92c32eef4a911ad1b6bf33a09170966\`) and current research-method file \`06_RESEARCH_LAB/methods/RESEARCH_PACKAGE_TO_REVIEW_PR_v1.md\` (blob \`52993aa6f791ef445e0286b13d809b87fe48333e\`).

## The most useful adversarial finding: truth status is not a prediction

The 2026-10 risk-to-action and integrity owner issues [#1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553) and [#1827](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1827) already documented: historical 12h directional nowcast confusion, HOLD-based actions, unavailable SELL/trim owner, weak end-to-end evidence of timely actual alerts, and risk/protection semantics with separate clocks. The new Fable fix is essential but **limited to truthful provenance and publication**. It does not by itself fix a late-warning predictive detector or prove profitable early de-risking.

### Synthetic countercases that should be forced through Fable tests

- A fresh, correct daily source and inherited prior risk: \`source_freshness=FRESH\`; \`risk_freshness=INHERITED\`. Neither automatically means forecast breached.
- An admitted completed-close BTC floor breach while daily source is fresh, protection still inherited: factual \`forecast_floor_status=BREACHED\`; explicit source clock; \`risk_freshness\` must truthfully flag inherited/obsolete basis per current contract. Do **not** silently replace risk/protection severity or investment action.
- A stale or missing daily input but valid unchanged freeze: \`source_freshness=STALE/UNKNOWN\`, \`forecast_floor_status=UNTESTABLE\`. It is dishonest to claim "no breach".
- A future close, incomplete candle, quote mismatch, pre-issuance observation or byte mismatch: \`UNTESTABLE\`, no success and no inferred breach.
- Sunday 23:00 UTC close observed next ISO week: allowed only at the exact bounded finalized-close clock, with frozen original forecast-week binding.
- A previous packet slot regenerated after schema bump: immutable historical bytes retained, new schema produces a new packet ID, and consumers tolerate both schema generations.
- A valid new packet and successful build but missing/old Pages deployment: \`MERGED_BUT_NOT_SERVED\`; user alert NOT confirmed. No claim of an operational warning.
- Two simultaneous signs, stale daily source + factual breach from another valid admitted record: display both evidence provenance channels, do not overwrite one with the other.

The proposed typed fields can be derived from existing data. This is a *contract review request*, not permission to broaden Fable's patch beyond the mandated files. If adding separate fields would exceed the bounded scope, preserve a clear \`basis/reasons\` structure and file the downstream UI adaptation under existing P1 owner. Do not weaken Fable's stop rule.

## Archive archaeology: ideas previously found versus actually measured

**June Research Lab source:** The attached project source \`Research Claude 10-6-2026.txt\` explicitly warns against \`ACCEPTANCE_THEATER\` (critique acknowledged, paperwork created, no new evidence) and \`CLOSED_EPISTEMIC_LOOP\` (one system writes rules, scores itself and claims success). This is an *archival recommendation*, not a verified current alert-engine implementation. Remedy: require at least one native producer result, real consumer receipt and an independent falsifier for any promoted research claim.

**May adaptive-learning archive:** \`12 maj - adaptive læringslag.txt\` describes SRE, FAE, CCE, ODM and RWE as activated shadow meta-components. That text alone cannot establish which components presently write actual output, are wired into official decision consumers, or improve prospective outcomes. Search the canonical owner/production output before rebuilding or trusting this layer. Avoid turning five named engines into five new workstreams.

**March/April TechDev and Shadow PDFs:** \`TechDev_Master_Alignment_Full_Document.pdf\` asserts strong macro/TechDev alignment and a Tier-1 65% / Tier-2 25% / Tier-3 10% historical conceptual mix. \`Shadow Layer syntese v1-v8, audit-klar og Shadow-only.pdf\` includes illustrative Copper/Gold, BTC dominance, CFGI, SSR and ETH/BTC heuristic thresholds. Neither is evidence that those weights or triggers are currently effective, independent, well-timed or currently authoritative. The relevant source questions are point-in-time availability, false signals, confluence dependence and decision divergence. The old PDF refers to Fed SR 11-7; the Fed's **17 April 2026 SR 26-2 supersedes it** (https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This is a reference currency correction, not a claimed regulatory obligation for a private crypto research system.

**June transition-survival archive:** \`Agent-idé Transition Survival.txt\` separates BTC absorption from ecosystem transmission and requires persistence of ETH leadership/breadth/rotation. \`Markedspsykologi og transition.txt\` stresses macro-positive and rotation-negative can coexist. Both are useful *hypothesis partitions* for Task 2/long-horizon Kompas but no prospective incremental performance was proven by these narrative documents.

**June weekly fallback archive:** \`CANONICAL WEEKLY BACKBONE ENGINE v2.0 FIX.txt\` documents historical \`MANUAL_BACKFILL_PASS\` / \`NO_EXTERNAL_WRITE\` when chat lacked actual external data. The present Sep-2026 current authority has moved to autonomous/hash-bound data. Important failure class: a chat-level manual backfill MUST NOT be interpreted as the same thing as exact original GitHub/market availability. The authoritative routing file \`00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md\` (blob \`c57b0578f273dd93511f5d546abaeec30bd8acef\`) supersedes manual upstream assumptions. Preserve history, do not resurrect its fallback as scientific authority.

**Research overlaps already underway:** [#2162 Shadow archaeology](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2162), [#2161 macro regime](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2161), [#2281 four-year calendar](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2281), [#2290 cross-asset 13F](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2290), [#2055 five-era warning cost](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2055), [#2054 CN/B1 comparison](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2054) and [#2208 CN/protection dispatch](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2208) establish substantial **prior research and already assigned ownership**. Do not launch parallel models until those original owner decisions are deduplicated and source-qualified.

## External method scouting, bounded alternatives

External tool availability is **not** evidence of better market forecasts. No tool was installed or run and no comparative backtest was executed.

| Open source / method | Real capability and fit | Decision and safest test |
|---|---|---|
| [MAPIE](https://mapie.readthedocs.io/en/stable/) conformal intervals, including time-series EnbPI / ACI | Calibrates uncertainty intervals; relevant if frozen forecast bands have systematic undercoverage. Temporal shifts can break exchangeability; no universal market coverage guarantee. | Later shadow-only interval comparator, compare realized coverage and width with *original* CN bands at matched target, horizon and first-known clocks. Not Tuesday. |
| [River](https://github.com/online-ml/river) online drift detectors ADWIN / Page-Hinkley | Detects changing data distributions/errors prospectively when updates are legally available. | Later cheap diagnostic monitor of **original forecast residuals**, with false alarms and latency; do not use latest hindsight data to explain past warnings. |
| [ruptures](https://github.com/deepcharles/ruptures) offline change point detection | Useful for retrospective regime segmentation and failure atlas. | For diagnosis only; an offline best segmentation is not evidence the change could have been detected on the day. Do not promote an after-the-fact changepoint to a live alpha signal. |
| [statsmodels MarkovRegression](https://www.statsmodels.org/stable/generated/statsmodels.tsa.regime_switching.markov_regression.MarkovRegression.html) | Statistically explicit regime model for a low-complexity challenger. | Compare filtered, contemporaneously available state with simple persistence; *smoothed full-sample state must never enter a historical live-time claim*. Only if Task 2 asks for a model challenger. |
| [skforecast walk-forward](https://skforecast.org/0.18.0/user_guides/backtesting.html) | Implementation and evaluation patterns for temporal, nonshuffled backtesting. | Borrow timing discipline/testing patterns, not an entire forecasting replacement. |
| [NautilusTrader](https://nautilustrader.io/docs/latest/concepts/backtesting/) | Event-driven simulation with order/fill, venue and latency assumptions, and comparable live event architecture. | **Alpha Lab realistic paper simulation candidate**. Evaluate a minimal fill/fee/latency model against current private MAL strategy arena before adopting a heavy trading platform. No trading activation. |
| [Microsoft Qlib](https://github.com/microsoft/qlib) and [RD-Agent](https://github.com/microsoft/RD-Agent) | Automated quantitative factor/model research and backtesting pipelines. | Architectural reference for reproducible hypothesis→implementation→review, not another permitted autonomous production agent. Current Research Lab method and S1 coverage should be benchmarked first. |
| Bailey/Lopez de Prado [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) | Addresses research selection bias, many strategy trials and non-normal return distributions. | For future Alpha strategies only after real prospective eligible trades and a known search/trial denominator; do not apply to Round 3 prohibited outcomes. |
| Federal Reserve [SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm) (17 Apr 2026) | Current model risk management reference replacing SR 11-7, not investment alpha or a binding standard for this framework. | Use its independent validation spirit, avoid falsely calling older SR 11-7 the current text. |

## Research opportunity and decision-value register

1. **P0: honest alarm and served product, not new ML.** Owner #1553/#1827 + already merged #2289; next observable pass is root+data CDN readback, correct unchanged forecast, and banner text on mobile and desktop. A merged PR without consumer proof is an incomplete product.
2. **P0: frozen official packet truth.** Owner Fable v2 Part 2 plus #2276; actual completed close and immutable source binding, distinct fact axes, fail-closed negatives, safe schema evolution, observed next newly issued packet. This is the only suggested Tuesday scope clarification.
3. **P1: W47 scorecard first mature output.** Existing #1596/#2217/#2292. Wait for 23 Nov 00Z maturity and original Git evidence. Compare candidate with its equal-target original benchmark only; report misses, missingness and unavailable B1. Do not use “N wins” without complete denominator or true baseline.
4. **P1: warning utility after factual integrity.** Existing #1553/#1596/#2055. A warning should be judged by *when a real user could know it*, equal alerts and opportunity cost. Compare lead-time distribution, false exits, missed downside and missed rebound against always-HOLD and a simple original observable-price baseline. No post-hoc tuned warning on W46/W47 as independent holdout.
5. **P1: Alpha realistic paper evidence.** Private MAL existing Arena/outcome owners. First verify admitted candidate population denominator, timestamped trade eligibility, order rejection, liquidity/slippage/fees, failed or unfilled orders and copied public Kompas regime first-known SHA; then design minimal execution simulation. No false zero-fee “alpha”.
6. **P2: source-unit and provenance integrity.** Existing #2293/#2267 on OKX OI units. Decide first from code/fixture and independent oracle before adding new derivative-based warning features.
7. **P2: cross-asset macro / ETF era source ablations.** Existing #2161/#2290/#2281 and historic transmission hypothesis. Only future, source-qualified G1 if a new feature changes a defined current decision beyond simple price/breadth baselines.
8. **P3: online uncertainty/regime innovation.** MAPIE/River/filtered Markov optional Task 2 shadow comparators once the original scoring source is trustworthy and eligible. Do not introduce a new predictor to compensate for an untruthful old one.

Every proposed action routes through an existing issue and the existing [research-to-reviewed-PR method](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/06_RESEARCH_LAB/methods/RESEARCH_PACKAGE_TO_REVIEW_PR_v1.md). There is **no new scheduler, engine, prompt task, production classifier, test ID or paid-model entitlement**.

## Exactly three optional Fable mandate clarifications, not three new work items

**D1 (recommended, Part 2):** Preserve typed distinction between \`risk_freshness\` and an admitted completed-close \`forecast_floor_status\`. In tests validate all four combinations of source freshness and forecast breach, including inherited decision basis. \`risk_freshness=STALE\` may be used for obsolete decision basis only with explicit \`basis\`, never as a fabricated new risk severity. If the source does not justify a separate field, carry reason-coded metadata in the existing output and log the UI dependency without expanding mandate.

**D2 (already planned, make it a hard acceptance, Part 2):** #2276 schema version consumer census, immutable old slot, Git-sourced 23:00 close, exact Sunday boundary, candle-close timestamps, same-quote/source/asset and independent \`git hash-object\` oracle. These are not optional cleanup. Maintain byte parity for unrelated packet fields.

**D3 (release handoff, no additional Fable code):** Make **merged / native producer emitted / Pages served / user-visible** four separate receipts in Claude's package README. Fable can draft the intended checks, but only the subsequent reviewed PR and actual naturally emitted new official packet + CDN readback can prove live impact.

**Leave Fable Part 1 and Part 3 unchanged.** No attempt to add MAPIE, River, Qlib, Alpha, RISK-02, OKX OI, new warnings, S1 autonomy promotion or a second re-chain. Enforce exact mandate GO and keep all Fable writes in Bridge \`claude/log\`, as currently required.

## Adversarial counterargument and falsification

- **Against our own recommendation:** Four status axes may add surface complexity. If users cannot distinguish them or consumers cannot read them, a single truthful message with encoded basis and exact timestamp may be better. Choose the *smallest visible contract* that cannot lie.
- **Against urgency rhetoric:** A factual floor breach is a late confirmation, not an early-warning forecast. It may not improve actionable capital protection. Run prospective equal-budget warning utility comparisons later, with source as-of and real delivery clock.
- **Against model enthusiasm:** Offline change-point, smoothed Markov state and retrospectively calibrated warning weights can look excellent after observing the selloff. Treat them as after-the-fact explanations, not verified predictors.
- **Against archive inflation:** The source archive already contains many similar hypotheses and active research PRs. This report claims *synthesis and one surgical clarification*, not a new alpha insight.
- **Against false autonomy:** S1's existing code/review receipt and release policies, not comments or a memo, determine authority. An independent review “no major issues” is advisory unless admitted under live native rules. A model cannot grant itself production GO.

## English Claude handoff, as a review request

\`\`\`text
PRE-FABLE INDEPENDENT RESEARCH REVIEW, 2026-11-21
Read the reviewable Archive research note with this title and its exact HEAD before the owner issues GO for FABLE_TUESDAY_MANDATE_v2 plus ADDENDUM_1.

Verdict: KEEP 25/55/20 SCOPE. No new engine or optional research lane on Tuesday.

Most useful new design concern: do not conflate (1) source freshness, (2) factual completed-close forecast-band breach, (3) inherited/non-recomputed protection state and (4) real Pages delivery. A breached floor is not itself a freshly estimated bearish risk class or an authorized portfolio action. Require typed basis, independent clock/quote/source lineage, explicit UNKNOWN, and observed consumer readback. If a separate field is too expensive, use an existing reason-coded field with no additional engine.

Already-mandatory Addendum 1 gates MUST remain: schema ID bump, full consumer census, immutable historical slot, git-bound 23:00 close, Sunday week boundary, candle-close timestamps and independent hash oracle with negative/mutation tests.

Scope protection: W5+D2 25%, AUDIT-04b/#2276 55%, only-capacity W4/W6/A11 20%. Bridge-only draft, no paid call, Round 3 read/test or external repo writes by Fable. A REJECTED or UNTESTABLE scientific outcome is valid if backed by evidence.

Independent diligence found archived acceptance-theater/closed-loop warnings, pre-existing Shadow and ETF-era hypotheses without live outcome authority, currently draft #2276/#2292/#2293 and multiple duplicate-risk research PRs (#2162/#2161/#2281/#2290/#2055/#2054). Do NOT divert Tuesday to these.

Please review and disposition:
(A) ADOPT AS TEST CLARIFICATION within existing Part 2,
(B) DEFER TO EXISTING OWNER if it expands scope,
(C) REJECT with an explicit evidence-based reason.
Do not treat this research-only PR as owner GO, a production fix or a Fable session trigger.
\`\`\`

## Evidence and science limits

- Github source files, issues and PR metadata were checked in a single read-only investigation on 2026-11-21. This was a **targeted critical-path census, not a byte-by-byte inspection of the entire historical GitHub archive, all action logs or private MAL**.
- A small set of uploaded March-June PDFs and text notes was examined for *prior ideas*, not current policy or quantitative outcomes. The old source claims were not promoted.
- Pages URLs were not independently accessible via the current public web read, so no CDN/live UI verification is claimed.
- No lawful Round 3 outcomes were opened, scored or used for model selection.
- No newly trained model, actual walk-forward backtest, native CI test, consumer deploy, actual paper strategy fill, independent external reviewer verdict, or market edge was generated in this research.
- All external projects above were assessed from official source documents and repositories; no packages were installed or execution/performance tested.
- Refresh the Fable mandate, original research owners and all affected PR heads before Tuesday. **Owner GO on the exact current frozen mandate remains mandatory.**

**Proposed Strategist classification:** MODIFY_EXISTING_TEST / RESEARCH_ONLY, limited to the AUDIT-04b consumer truth contract; all new model ideas remain DEDUP_TO_EXISTING_OWNER or FUTURE_SHADOW_RESEARCH, not independent test registrations.
