# ASTRA HIGH mission 4/5 — early deterioration and cycle/rotation research

**Requested source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **RESEARCH DESIGN ONLY — no live threshold changes, trades, backtest results, promotion, or new delivery claim.**

## Executive finding

**A move from 3/5 ELEVATED to 4/5 HIGH could be legitimate before a drawdown—but this packet does not establish that such an upgrade was warranted, issued, delivered, or actionable in any particular episode.**

Three questions must remain separate:

1. **Was HIGH permitted by the then-effective risk contract?** The actual protection contract, upstream producer and refresh logic are not supplied.
2. **Could legally available evidence have supported an earlier HIGH assessment?** Potentially, but this requires point-in-time inputs, a rule fixed before evaluation, independent episodes and matched-warning-budget controls.
3. **Would the warning have protected capital?** That additionally requires actual delivery—or explicitly simulated counterfactual delivery—plus feasible quotes, a separately specified response and complete costs.

The best research direction is **not a more elaborate crash narrative**. It is a source-admitted test of whether **deteriorating resilience and failed recovery add useful warning time beyond price/volatility**, without increasing false alarms, warning occupancy or false-exit harm. This follows the supplied research constraints; it is not an established finding. [S1–S3, S6, S8]

W46 remains **exposed development material**. This mission neither re-scores it nor invents an earlier alert. W47 is not scored here. [S2, S7, S8]

---

## 1. Evidence boundary and SHA register

I inspected only the text supplied in this conversation. **No tools, repository reads, code execution, independent hash verification or Claude invocation occurred.** The association between these bytes and requested source-main has not been independently verified.

References below distinguish:

- **TEXT:** directly visible in a supplied document or code.
- **REPORTED:** a supplied document’s account of underlying evidence, not reproduced here.
- **HYPOTHESIS:** proposed research, not empirical support.
- **UNINSPECTED:** underlying material absent from the packet.

| Ref. | Supplied source | Supplied SHA-256 |
|---|---|---|
| **S1** | `AGENTS.md` | `4c2cc641e35e07e49e31d16b6aa960bbf6ceb4bd1ae1eb9fb05b2f53d275093a` |
| **S2** | `04_MARKET_LEARNING/handlekompas/research/2026-11-13__W46_PULLBACK_FAILURE_RPL_V1.md` | `00a60f12bad570ac5951c5843544411a95b5965abe58817ddd4233da2a0f9c32` |
| **S3** | Corresponding `2026-11-13__W46_PULLBACK_FAILURE_RPL_V1.json` | `b6c072419358a2200a628c0ec354218e9698338750a52a4cd005d3cdc9710d35` |
| **S4** | `scripts/research/task2_rpl8_source_replay_v1.py` | `43b967c511be796149da2dfff0938651b9f7ab6d0e67278dea3a03bc3c469289` |
| **S5** | `canonical-project-archive/09_ROTATION_AND_ALTSEASON/EARLY_ROTATION_PRE_TRIGGER.md` | `ca04affdbfb14543124c957de75c2245299ceb5d62e68280569042c828f6605c` |
| **S6** | `research/framework_evolution_learning/2026-11-05__altseason_capital_path_microcap_early_largecap_exit_research_mandate_v1.md` | `bfaaf4063d4e01ada2d34dfa53ffb2a0a03ee007b46c02a7d4dfdd02b1d652c9` |
| **S7** | `05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_FORECAST_FREEZE.json` | `bc6ca7623179ba588929c1c856db68dc7f981f0bcd65e749793dc178269de348` |
| **S8** | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-16_ASTRA_HIGH_W46W47_ORIGINAL_RESEARCH_UNAUDITED_v1.md` | `981ce1be3655a031810aba7c7f79044ed923b0c608d509ce54fa3bd9f3bce864` |

**Important source qualifications**

- S2 reports protection-state pass-through and earlier Claude findings. Neither the producer code nor those native review receipts is supplied. These are investigation leads, not freshly verified implementation or performance findings.
- S3 labels its work **PLANNED**, source eligibility **UNKNOWN**, and model run evidence empty.
- S4 is inspectable code, **not an executed result**. Its hard-coded consistency assertions do not establish that current underlying inputs pass. Its explicit limitations reject original PIT, independent-event power and executable economic-edge claims.
- S8 is explicitly **UNAUDITED**, uses a different source-main, and cites additional sources absent here. Its nested references do not become inspected evidence through citation.
- S7 explicitly describes uncalibrated deterministic hypotheses, unverified breadth/leadership and no verified numerical 2–3-week path. It supplies no support for extrapolating a 4–6-week numeric forecast. [S2–S4, S7–S8]

Repository preflight and current-authority resolution remain **unperformed**. This memo is therefore a packet-bounded design, not a current Compass render or repository-qualified operational decision. Round 3 remains collection-only; the proposed experiments must not be run on Round 3 under present authority. [S1]

---

## 2. Could ELEVATED legitimately become HIGH before drawdown?

### 2.1 Four distinct meanings of “before”

A warning can precede:

1. **The first deterioration**;
2. **The objectively defined shock onset**;
3. **A specified drawdown barrier**;
4. **The remaining actionable downside after delivery**.

These are not interchangeable. A warning after an initial decline may provide useful protection against further decline, but cannot receive credit for predicting the decline already observed. A floor-breach trigger cannot claim advance warning of its own triggering breach. [S8; methodological extension]

### 2.2 Admission conditions

| Question | Evidence required | Present conclusion |
|---|---|---|
| Is 3/5 → 4/5 the correct official mapping? | Then-effective protection contract and mapping implementation | User framing accepted for research; mapping not independently inspected |
| Did existing rules already permit HIGH? | Pinned upstream producer, refresh logic, configuration and applicable contract | **UNKNOWN** |
| Did pre-event evidence satisfy those rules? | Complete eligible decision census and source-known inputs | **NOT EVALUABLE** |
| Was HIGH actually issued? | Original immutable warning/version and issuance receipt | Not established by supplied evidence |
| Was it actually delivered? | Consumer receipt identifying that exact version | Not established |
| Was meaningful downside still actionable? | Post-delivery executable quote, latency and subsequent source-qualified path | Not established |
| Could a new candidate improve warning quality? | Preregistered counterfactual test and untouched prospective evaluation | **Testable hypothesis, not a finding** |

A legitimate **existing-rule** upgrade would require the applicable rule to have been satisfied using evidence actually available at that time. If the existing rule did not permit it, a later researcher may propose a challenger—but may not relabel the original historical state.

The reported absence of HIGH classifications in an earlier audit does **not**, by itself, prove a broken classifier. Possible explanations include conservative semantics, missing eligible evidence, an upstream refresh problem, rare qualifying conditions or genuinely unhelpful escalation. Resolving them requires the full producer-to-consumer trace. [S2–S3]

### 2.3 Necessary chronology

For every constituent input and warning, retain:

`observation/bar-end → provider publication → collector first-known → accepted interpretation → issuance → consumer observation → actionable quote`

Additional requirements:

- A completed-bar feature cannot use its final high, low or close before completion.
- Revised ETF, macro or sentiment data must retain their original vintage.
- Git first-add is not provider-first-known, HTTP delivery or proof a human saw the warning.
- A site readback proves that content was observable at that readback time. Without earlier observations, it generally does not prove the exact first availability time.
- An hourly breach label may support only an interval for the breach, not a fabricated tick timestamp.
- A reconstructed candidate was **not actually delivered**. Any delivery assumption must be labelled simulated, even if based on observed historical pipeline latency. [S2, S8]

**Decisive test:** Could the frozen challenger have produced an admissible warning early enough that its benefit survived realistic delivery delay and executable-price comparison against the simplest competing warning?

---

## 3. Separate six objects—not one composite “risk score”

| Object | Meaning | Forbidden inference |
|---|---|---|
| **Market severity** | Conditional damage, fragility and recovery difficulty | HIGH does not mean an 80% crash probability |
| **Forecast probability** | Calibrated likelihood of a precisely defined event/horizon | Bull/Bear evidence balance is not probability |
| **Alarm intensity** | Communication urgency, repetition and escalation | More notifications are not more independent evidence |
| **Hedge/hold policy** | Separately authorized response given exposure, costs and constraints | A warning is not SELL; HOLD_WAIT does not liquidate existing exposure |
| **Delivery** | Which version reached which consumer, and when | Issuance does not establish delivery |
| **Outcome/economics** | Subsequent path and, separately, feasible net response results | Correct bearish direction does not establish capital preserved |

A high-severity but uncertain scenario can justify strong **risk communication** without a calibrated event probability. Conversely, a likely modest pullback need not be high-severity. Policy choice additionally depends on response costs and false-exit regret. [S1–S2, S6–S8]

**Proposed output discipline:** expose these fields separately, with individual evidence status. Do not average source quality, severity, probability and action into a single number.

---

## 4. Staged early-deterioration indicators

Everything in this section is an **unpromoted hypothesis**. Source references establish relevance and constraints, not predictive validity. No lookback, weight, persistence threshold or HIGH cutoff is selected here. [S2, S5–S8]

### 4.1 Research stages

| Stage | Interpretation | What would advance the investigation? |
|---|---|---|
| **A. Latent fragility** | Vulnerability without a confirmed adverse path | Thin executable liquidity, concentrated leadership or crowded leverage |
| **B. Deterioration** | Market resilience is weakening | Broader participation loss, weaker absorption or persistent adverse flows |
| **C. Failed repair** | Rebounds do not restore prior resilience | Weak breadth recovery, poor depth refill, renewed selling impact |
| **D. Shock propagation** | Damage is transmitting across assets/venues | Cross-market stress, deleveraging, financing or stablecoin disruption |
| **E. Recovery or relapse** | Repair survives—or fails—a new test | Sustained participation/liquidity repair versus another deterioration |

These stages must allow **skipping, coexistence and reversal**. They are not a required chronological cycle and not a replacement live severity scale.

### 4.2 Indicator families and their strongest alternative explanations

| Family | Early deterioration candidate | Stronger confirmation / falsifier |
|---|---|---|
| **BTC/ETH price structure** | Downside persistence, failed reclaim, ETH-relative weakness, greater downside response to comparable shocks | Test incremental value over price/volatility itself. A relative ETH decline does not establish absolute market decline; both assets can rally. |
| **Executable liquidity** | Wider spreads, lower depth at fixed notionals, poor replenishment, rising cross-venue dispersion | Require archived order-book/quote observations. Displayed depth may cancel; one venue is not global liquidity. |
| **Breadth** | Fewer assets sustaining prior strength; equal-weight deterioration beneath cap-weighted stability | Freeze universe and membership. Delistings, suspended markets and missing prices remain in the denominator with explicit status. |
| **ETF persistence** | Repeated adverse flow surprises or poor price absorption despite inflows | Use first-publication times, settlement conventions and unrevised vintages. Test against lagged price and calendar effects; one outflow day is not persistent withdrawal. |
| **Derivatives/OI/funding** | Crowding followed by deteriorating price response, basis stress or unstable leverage | Separate contract OI from USD-valued OI; distinguish predicted from realized funding. Liquidations observed after a fall are usually propagation evidence, not advance proof. |
| **Stablecoin/FX** | Persistent peg stress, impaired redemption/transfer conditions, relevant dollar/financing pressure | Distinguish minting from deployable demand, bridge movements from new issuance, and USD from USDT quotes. Macro releases require vintage and publication clocks. |
| **Rotation transmission** | ETH/BTC strength fails to spread into a viable basket; narrow alt rallies repeatedly fail survival | Test future investable-basket outcomes—not only ETH/BTC sign or a trailing altseason index. |
| **Leadership quality** | Fewer leaders, deteriorating equal-weight leadership, unstable handoffs, leaders failing before the index | Rebalance and universe changes can manufacture dispersion. Compare with a fixed-membership control. |
| **Absorption** | Similar sell pressure produces greater price damage and slower recovery | Normalize for volatility, venue coverage and time of day. Price-derived “absorption” may add nothing beyond price momentum. |
| **Market fragility** | Joint deterioration in financing, depth, concentration and recovery capacity | Joint signals may reflect one common price shock. Corroboration across mechanisms is not statistical independence. |

S7 specifically warns that venue taker data are not proof of global buying/distribution, and that BTC/ETH observations do not establish broad participation. S4 contains explicit negative/limited-evidence treatments for breadth, ETF and derivatives research; those families start with a burden of proof, not presumed edge. [S4, S7]

### 4.3 Rotation: distinguish opportunity from false reassurance

The supplied pre-trigger sequence is:

**Pre-trigger → survival → ETH/BTC persistence → breadth survival → deployment confirmation → rotation confirmation.**

It explicitly prohibits treating pre-trigger as entry or confirmed altseason. [S5]

A useful research distinction is:

- **Token-local opportunity:** a small set of assets can perform while broad conditions deteriorate.
- **Broad rotation:** persistent participation across an investable, point-in-time universe.
- **Distribution risk:** worsening liquidity and recovery despite apparent leadership.

Microcap excitement must not cancel broad-market risk. Equally, broad weakness must not be claimed to disprove every token-local opportunity. The two sleeves need separate outcomes and a finite capital ledger; no forced BTC→ETH→large→small→micro sequence. [S6]

---

## 5. Horizon-specific shadow research

These are research targets for existing owners, **not four new forecast engines**. The 4–6-week lane must retain Cycle Navigator/strategic ownership; it cannot be manufactured by extending a short-horizon signal. [S1]

| Horizon | Main question | Suitable candidate evidence | Main limitation |
|---|---|---|---|
| **1–3 days** | Is fragility becoming a near-term adverse path? | Completed price structure, depth/refill, leverage stress, rapid breadth deterioration | Delivery latency can consume most apparent lead time |
| **5–7 days** | Does deterioration persist through rebounds and flow cycles? | Breadth survival, failed repair, ETF persistence, leadership durability | Weekly publication and settlement clocks can create false contemporaneity |
| **2–3 weeks** | Is this a repairable shock or persistent regime deterioration? | Repeated recovery tests, financing/liquidity conditions, sustained rotation failure | Current supplied CN object does not provide a numerical path for this horizon |
| **4–6 weeks** | Is capital transmission recovering, stalling or regressing? | Stage transitions, financing regime, multiweek leadership and investable-basket survival | Few independent blocks; no source-supported numeric depth/ETA supplied |

For each horizon, freeze its exact endpoint and whether the target is a close, a path barrier, recovery survival or terminal paper wealth. A 72-hour warning and a 42-day cycle hypothesis must not share an outcome label merely because both are “bearish.” [S6, S8; proposed design]

**Cross-horizon disagreement is information, not a defect to average away.** A short relief rally can coexist with longer deterioration. “Micro bullish / macro fragile” should remain a labelled conflict with separate timestamps, not collapse into an unsupported neutral state.

---

## 6. Proposed architecture: extend existing owners, not authority

### 6.1 Evidence path

```text
Existing governed sources
    ↓
PIT, freshness, universe and source-health admission
    ↓
Existing-owner feature families + shared-input/dependency tags
    ↓
Research annotations:
risk trend | breadth survival | absorption decay | shock/recovery path
    ↓
Horizon-specific challenger interpretation or abstention
    ↓
Immutable research issuance, where authorized
    ↓
Separate consumer-delivery and executable-price evidence
    ↓
Existing validator/scorer and independent review
```

Raw/restricted values remain in their authorized plane. Public research receives only permitted evidence and bindings; a public report must not reconstruct private holdings, wallet records or normalized restricted feeds. [S1, S6]

### 6.2 Five proposed modules

**1. Risk trend**

Retain deterioration direction, persistence, acceleration and failed-repair count—not merely the current ordinal state.

- Preserve the original official state unchanged.
- Annotate `worsening / stable / improving / UNKNOWN`.
- Track feature age and changes since the last *new evidence*, not since the last hourly publication.
- Do not treat repeated copies of the same weekly state as repeated confirmation.

**2. Breadth survival**

Form a cohort using information available at an earlier, frozen formation time. At decision time, measure how many members retain the predefined strength/liquidity condition.

Report separately:

- surviving;
- observably failed;
- delisted or non-executable;
- missing/unresolved.

Dropping unavailable assets would manufacture survival. Treating every unavailable asset as a proven failure would also be wrong. A forward survival label must never enter its own earlier feature.

**3. Absorption decay**

Test whether comparable adverse pressure increasingly produces:

- larger price impact;
- slower recovery;
- weaker order-book refill;
- broader subsequent weakness.

Control for preknown volatility, venue mix and session effects. If the measure is mostly a transformation of recent returns, its relevant benchmark is a comparably flexible price-only model.

**4. Shock path and recovery**

Represent competing transitions:

`fragility → shock → stabilization → durable recovery`  
or  
`fragility → shock → failed recovery → renewed shock`

Exogenous shocks may have no detectable precursor. The model should be evaluated on honest misses, not required to produce a retrospective explanation for everything.

Recovery needs independent evidence; a price rebound alone may be insufficient, but requiring every family to recover could create costly late re-entry. That trade-off must be tested.

**5. Confidence and abstention**

Keep at least:

- source integrity;
- temporal eligibility;
- coverage;
- model-validation status;
- cross-horizon agreement;
- decision eligibility.

Do not turn them into a fabricated probability. Missing critical inputs produce **UNKNOWN/abstention**, not LOW or automatic HIGH. The last valid state may be retained for history, clearly expired; it must not be refreshed by re-rendering. [S1, S4–S8; all module designs are hypotheses]

### 6.3 Candidate escalation logic—symbolic only

A research challenger might investigate:

\[
\text{admitted inputs}
\land \text{persistent deterioration}
\land \text{failed repair}
\land \text{incremental corroboration}
\]

as a basis for a **shadow escalation candidate**.

All persistence, severity, corroboration and reset parameters remain undefined until preregistration. Requiring “three indicators” is not inherently robust if all three derive from the same returns. This schematic grants neither an official 4/5 label nor a hedge action.

---

## 7. Matched-warning-budget experiments

### 7.1 Cohorts before crashes

Build a source-feasibility inventory first, then select contiguous historical periods or a rule-defined episode universe **without selecting only known crashes**.

Include:

- quiet periods;
- slow declines;
- sharp crashes;
- transient liquidations;
- V-shaped recoveries;
- false breakouts;
- narrow alt rallies;
- sustained broad rallies;
- stablecoin/venue stress;
- prolonged distribution without a single dramatic crash.

These are **required case types, not claims that qualifying datasets are supplied**.

Separate historical eras by actual feature availability. A pre-ETF period cannot receive synthetic ETF zeros, and a modern reconstructed token universe cannot stand in for a historical investable universe. [S6]

Use three evidence classes:

1. **Original PIT and delivery verified:** eligible for original-warning evaluation.
2. **Historical market data with incomplete availability lineage:** development-only counterfactual research.
3. **Untouched prospective collection:** confirmatory only after registration and authorization.

An inspected historical era is no longer untouched merely because a new model is applied to it. [S1, S8]

### 7.2 Independent episode unit

Hourly rows are observations, not independent trials.

- Cluster BTC and ETH responses to the same shock.
- Merge overlapping event windows where they share the same market event.
- Keep prolonged shock/recovery sequences together.
- Purge train/test overlap using the longest evaluated outcome horizon and applicable information leakage.
- For 4–6-week targets, a 72-hour purge is plainly insufficient.
- Report residual dependence and effective block counts; “one week” is not automatically an independent shock.

Never increase apparent power by counting repeated alerts, multiple assets or several horizons from the same episode. [S2, S4, S8]

### 7.3 Budget definition

Match more than alert count:

- **first-alert episodes per eligible observation time;**
- **time spent in warning state;**
- **re-alert/reset policy;**
- **notification intensity;**
- **coverage and abstention.**

A system continuously warning is not equivalent to a selective system issuing the same number of notifications.

**Procedure**

1. Select candidate and baseline parameters on development data only.
2. Freeze a warning-budget operating point and deterministic notification/reset rules.
3. Run chronologically on held-out data without retuning to achieve a convenient realized count.
4. Report actual out-of-sample alert counts and warning occupancy, including budget deviations.
5. Present any achieved-budget interpolation as secondary descriptive analysis, not the primary prospective result.

A communication cap must not silently falsify the recorded risk state. If a notification is suppressed, retain the underlying state and suppression reason.

The original classifier must remain unchanged as an observed benchmark. If it never emits HIGH in a cohort, report zero HIGH warnings; do not fabricate a matched HIGH policy for it. [S2–S3, S8; proposed experimental specification]

### 7.4 Counterfactual benchmarks

| Benchmark | Purpose |
|---|---|
| Original as-issued risk and action | Actual system comparison, with original coverage and delivery |
| Persistent prior risk / always-ELEVATED / no-warning | Detect gains attributable merely to frequent caution |
| Simple price-trend warning | Establish whether non-price evidence adds anything |
| Simple preknown volatility/drawdown warning | Control for obvious deterioration and changing volatility |
| Matched-budget placebo alerts | Test whether timing matters beyond warning frequency |
| Price-only model with matched complexity | Prevent a richer feature set winning solely through flexibility |
| Family ablations | Remove ETF, breadth, derivatives, liquidity, etc., one family at a time |
| HOLD and cash/no-trade paper controls | Separate warning accuracy from economic usefulness |

For rotation/economics, retain the supplied mandate’s BTC, ETH, large-cap and PIT broad-alt HOLD controls, static diversification and token-native microcap benchmark. Compare identical capital, clocks and feasible sizes. Reuse existing T5/T6/Shared Row and equal-width work where applicable; do not rebuild prior projects. [S2, S6, S8]

### 7.5 Outcomes and actionable downside

**Warning outcomes**

- event recall;
- false-alert episodes per qualified observation time;
- warning occupancy;
- first-warning lead;
- lateness;
- severity-weighted missed events;
- false alarms during benign pullbacks and recoveries.

Severity weights must be frozen independently of which model won.

**Three lead times**

\[
L_{\text{source}}=t_{\text{event}}-t_{\text{legal-input-availability}}
\]

\[
L_{\text{issued}}=t_{\text{event}}-t_{\text{original-warning}}
\]

\[
L_{\text{consumer}}=t_{\text{event}}-t_{\text{verified-consumer-observation}}
\]

These diagnose different bottlenecks. Missing issuance or delivery means the corresponding metric is unavailable—not equal to source lead.

**Actionable downside**

For a specified hypothetical reduction, use the first feasible side-specific quote after verified delivery plus frozen response latency. Compare the subsequent path from that quote, not from the earlier peak.

That remaining downside is still **not realized savings**. Economic evaluation also needs:

- action size and capacity;
- partial/rejected fills;
- exit and re-entry rules;
- spreads, fees, impact and slippage;
- hedge funding/borrow/margin where applicable;
- missed continuation and false-exit regret;
- terminal liquidatable wealth.

A subsequent minimum price can describe adverse excursion; it cannot become an assumed perfect repurchase. [S6, S8]

### 7.6 Inference and multiplicity

Freeze one primary challenger comparison and primary endpoint. The remaining research tracks are exploratory until separately registered.

Use paired event/block uncertainty, not hourly binomial confidence intervals. Preserve the full denominator:

`scheduled → eligible → issued/abstained → delivered/unknown → mature/censored/missing`

Report both common-eligible comparisons and whole-pipeline coverage. If event counts are inadequate, return **INCONCLUSIVE**, not a highly precise estimate from correlated rows. [S1, S4, S8]

---

## 8. Twenty ranked research tracks

**Ranking criterion:** expected information gained per unit of implementation, provenance and overfitting risk—not expected trading profit. These are a research backlog, not twenty new engines or approved jobs.

| Rank | Track | Decisive test / rejection condition | Source basis |
|---:|---|---|---|
| **1** | Source-to-consumer clock reconstruction | Reject timing claims when original source, issuance or consumer clocks cannot be bounded | S1–S3, S8 |
| **2** | Existing ELEVATED→HIGH authority and producer trace | Establish whether escalation was permitted, blocked, stale or simply unsupported; reject “stuck classifier” if trace disproves it | S2–S3 |
| **3** | Complete denominator and episode census | Reject evaluation that omits quiet, missing, censored or non-warning periods | S1, S4, S8 |
| **4** | Matched-budget price/volatility benchmark | Reject added complexity if advantage disappears at comparable alert burden | S2, S8 |
| **5** | Delivery-latency/actionable-price erosion | Reject useful-warning claims if the apparent gain disappears before feasible response | S6, S8 |
| **6** | PIT breadth survival | Test fixed-vintage participation and failures; reject gains dependent on survivor-only membership | S5–S6 |
| **7** | Failed-repair / absorption decay | Test incremental value beyond recent return and volatility; reject redundant transformations | S2, S6–S7 |
| **8** | Executable depth and refill deterioration | Test real quote capacity; reject conclusions based only on displayed or single-venue volume | S6–S7 |
| **9** | Risk trend versus static ordinal state | Test whether trend annotations improve lead without raising occupancy; reject mere alert amplification | S2–S3 |
| **10** | Shock-path/recovery discrimination | Test V recovery, second flush and durable repair; reject rules that win only on terminal crashes | S6, S8 |
| **11** | BTC/ETH joint and divergent deterioration | Compare with BTC-only/ETH-only controls; reject double-counting one shock as corroborating trials | S4, S7–S8 |
| **12** | Leadership concentration and dispersion | Use fixed membership; reject effects explained by index composition or market beta | S6–S7 |
| **13** | ETF persistence and absorption | Use publication-vintage flows; reject claims lost after lagged-price/calendar controls | S2, S4, S6 |
| **14** | Derivatives crowding and deleveraging | Normalize OI/funding definitions; reject lift absent on independent episodes or first-known clocks | S4, S6 |
| **15** | Stablecoin/FX/financing stress | Separate real liquidity impairment from accounting transfers and quote effects | S2’s source-admission framework; new hypothesis |
| **16** | False rotation and breadth transmission | Require investable-basket survival; reject ETH/BTC sign as sufficient altseason proof | S5–S7 |
| **17** | Cross-horizon contradiction handling | Test explicit conflict/abstention against naive aggregation; reject a cosmetic consensus score | S1, S7–S8 |
| **18** | Microcap-versus-broad-cycle separation | Test token-native outcomes and failed exits; reject broad-alt claims driven by a few winners | S6 |
| **19** | Sentiment/news/forum incremental value | Admit original captures and deduplicated sources; reject lagged price echoes, rumors and narrative selection | S2–S4 |
| **20** | Full defensive-policy/capital-path economics | Evaluate finite capital, after-cost wealth and false-exit regret; stop without feasible fills and independent events | S6, S8 |

The first five tracks determine whether later tracks can be evaluated honestly. Complex feature research should not outrun clock, denominator and price feasibility.

---

## 9. Failure modes and explicit defenses

| Failure mode | Defense |
|---|---|
| **Post hoc risk upgrade** | Preserve original state; label every reconstructed alternative counterfactual/development-only |
| **Correlated hourly observations treated as proof** | Episode-level inference, shared-shock clustering and deduplicated alerts |
| **Stale signals presented as current** | Original expiry clock survives every consumer/render; stale means ineligible |
| **Fake rotation** | Fixed universe, absolute and relative returns, participation survival and executable liquidity |
| **Micro/macro contradiction averaged away** | Separate sleeves, horizons and conflict status |
| **Missing data marked safe** | Explicit UNKNOWN; structural non-applicability distinguished from missingness |
| **Lagged sentiment treated as foresight** | First-known capture, price-lag controls and sentiment-free ablation |
| **Cherry-picked crashes** | Predeclared contiguous cohorts, benign cases and all eligible non-warning periods |
| **Forum noise counted as corroboration** | Deduplicate common origin; verify primary evidence; otherwise narrative-only/SOURCE_BLOCKED |
| **Several feeds copying one source** | Source-lineage family tags; provider count is not independent evidence count |
| **ETF or macro revisions leak backward** | Vintage-aware replay and publication clocks |
| **OI growth caused by price valuation** | Contract/unit normalization and separate price effects |
| **USDT movement mistaken for USD asset movement** | Explicit quote currency and observed conversion evidence |
| **Recovery ignored to make exits look good** | Full terminal horizon, missed upside, re-entry costs and false-exit regret |
| **Selective abstention manufactures accuracy** | Coverage and pipeline-denominator reporting alongside paired performance |
| **A rule learned from one era looks universal** | Chronological holdouts, era-specific feasibility and explicit non-generalization |

These defenses extend the supplied source-clock, missing-data, independence and economic-accountability requirements; none is claimed implemented or tested. [S1–S8]

---

## 10. Deterministic guard tests to require

These are **test specifications, not executed tests**. Implement only through existing owners after inspecting current validators. Critical guards need mutation tests proving that removing the guard makes the test fail. [S1]

| Fixture | Required result |
|---|---|
| Valid completed bar, eligible source and exact version | Admission succeeds for its permitted use |
| Hourly final low supplied before bar completion | Reject as future information |
| Historical source revised after the decision cutoff | Original vintage only; reject substituted revision |
| Git first-add supplied as provider-publication time | Reject that provenance upgrade |
| Issuance supplied as consumer delivery | Delivery remains UNKNOWN |
| Consumer sees an older cached warning version | No delivery credit for the new warning |
| Same evidence republished for many hours | One semantic observation/episode; no inflated independent count |
| BTC and ETH warnings share one shock | Shared cluster, separate asset outcomes |
| Missing ETF input represented as zero | Reject missing-to-neutral conversion |
| Pre-ETF period labelled “ETF missing” | Record structural non-applicability; do not invent a flow |
| Stale official source re-rendered now | Original expiry retained; current use blocked |
| Breadth asset disappears from price feed | Keep membership; unresolved outcome remains explicit |
| Relative alt strength while all assets fall | No automatic broad-altseason confirmation |
| Weekly-band breach after loss already occurred | Credit only eligible subsequent outcomes |
| Alert never delivered but profitable hypothetical price supplied | No actual-delivery/economic claim |
| Quote before delivery/latency or above capacity | Reject executable-price eligibility |
| USD and USDT prices joined without conversion evidence | Reject cross-quote comparison |
| Overlapping 42-day labels split across folds | Reject leakage/incorrect independence |
| Immature horizon recorded as failure | Keep pending/censored under the original contract |
| Probability derived from ordinal risk or Bull/Bear scale | Reject unsupported calibration |
| Research-only live-display output enters a scorer/decision | Reject under its restricted exception |
| Caller supplies a “Claude approved” text field | No independent-review credit without genuine receipt |

S4 also deserves careful reuse: matching aggregate sample counts in a helper does not itself prove row-ID matching or PIT eligibility. Those properties require the underlying scorer and source evidence. Its optional `--output` path writes a report; therefore “offline” must not be confused with “incapable of writing.” These are static observations, not demonstrated defects in a deployed workflow. [S4]

---

## 11. Preregistration and prospective stop criteria

### 11.1 Freeze before any confirmatory outcome

A complete protocol needs:

- exact source-main, source bytes/hashes and applicable owner contracts;
- source eligibility, vintages, freshness and quote conventions;
- asset universe and delisting/failure treatment;
- feature definitions, dependency families and parameter-selection history;
- candidate escalation, persistence, expiry, reset and recovery rules;
- exact horizon/event definitions;
- first-warning and episode-clustering rules;
- alert budget and warning-occupancy accounting;
- original and counterfactual delivery treatment;
- executable quote, latency, size and cost assumptions;
- primary benchmark, endpoint and minimum meaningful effect;
- multiplicity policy and dependence-aware inference;
- sample-size rationale based on independent events—not hourly rows;
- fixed efficacy-look schedule;
- missingness, censoring and abstention rules;
- independent-review requirements;
- adoption authority and explicit no-automatic-promotion statement.

Every numeric decision threshold remains **an unpromoted hypothesis** until this freeze and separate owner approval. Existing Pullback Radar episode definitions should be inspected and reused where applicable, not reconstructed from the W46 summary. [S1–S3, S8]

### 11.2 Stop/hold rules

**Immediate integrity stop**

- future-data leakage;
- timestamp or version mutation;
- private-data exposure;
- retroactive alteration of a frozen forecast;
- unauthorized scoring, trading or production influence;
- fabricated delivery or independent-review evidence.

**Evaluation hold**

- missing original clocks;
- unavailable realistic execution prices;
- unidentified universe;
- unresolved event dependence;
- insufficient matured outcomes;
- critical coverage below the prospectively frozen requirement.

These produce **SOURCE_BLOCKED / NOT_EVALUABLE / INCONCLUSIVE**, not negative market evidence.

**Scientific rejection**

Reject the challenger if the preregistered comparison shows that:

- gains vanish against matched-budget price/volatility controls;
- gains depend on repeated alerts or selective coverage;
- useful lead disappears under delivery delay;
- false-alarm/recovery harm offsets the proposed benefit;
- feasible after-cost economics are worse than the frozen control.

**No optional continuation until success.** Any extension, new threshold or new primary endpoint requires a new prospective registration. Historical findings remain at most candidates for forward testing. Round 3 testing/scoring stays OFF unless its authority changes through the proper route. [S1, S6, S8]

---

## 12. Independent Claude method review

**Status: NOT RUN · NOT DISPATCHED · NO REVIEW VERDICT CLAIMED.**

The earlier Claude findings mentioned in S2 do not constitute review of this mission. S8 likewise explicitly requires future independent adjudication. [S2, S8]

### Proposed review packet—not a submitted review

Route through the **existing Claude/original-owner channel**, without creating an agent, schedule or paid call.

The reviewer should receive the frozen memo and source manifest, then independently assess:

1. **Distinctness:** Does this mission avoid recycling W46 as an untouched test?
2. **Authority:** Is any candidate threshold accidentally presented as an existing live rule?
3. **Chronology:** Are source-known, issuance, consumer observation and simulated delivery kept separate?
4. **Independence:** Do asset, horizon and hourly correlations inflate evidence?
5. **Budget fairness:** Are count, occupancy, resets, coverage and actual out-of-sample budget deviations handled?
6. **Incrementality:** Could price/volatility explain the proposed non-price signals?
7. **Rotation validity:** Are PIT membership, failures and investable-basket outcomes required?
8. **Economics:** Are path extrema, fills and terminal wealth properly distinguished?
9. **Abstention:** Can missingness or selective silence create a false win?
10. **Implementation:** Do positive, adversarial and guard-removal tests cover the actual code?
11. **Boundary:** Is Round 3 untouched and restricted data kept private?
12. **Negative decision:** What specific finding would make the reviewer reject the challenger?

Require a genuine native receipt, exact reviewed source/version, findings with evidence references and explicit unresolved limitations. The reviewer must be detached from authorship. Agreement between models is advisory, not evidence of forecasting edge.

---

## 13. Uninspected sources and smallest next steps

### Material uninspected sources

1. **Authority/preflight:** current cockpit; `CROSS_REPO_DATA_BOUNDARY.md`; context map; production-authority canonical and machine mirror; canonical index/addendum registry; relevant skills and active-test registry.
2. **Risk implementation:** `PROTECTION_TRACKER_CONTRACT_v1.md`; `scripts/data_ping/native_handlekompas.py`; upstream CN structured-risk producer and `event_refresh`.
3. **Original episode rules:** the 31 October Pullback Radar 2.0 SHADOW preregistration.
4. **Original observations:** complete official issue census, provider captures, source-health receipts, immutable publication/consumer evidence and feasible quotes.
5. **S4 dependencies:** `task2_archive_first_edge_matrix_v1`, `task2_cfgi_capture_clock_audit_v1`, and every referenced input dataset.
6. **Existing research/economics:** T5/EDGE-001, T6 rotation survival, Shared Row, synthetic protection harness and equal-width comparator source/current status.
7. **Independent reviews:** native Claude Bridge receipts and underlying reports.
8. **Restricted evidence:** private authority, bindings, health receipts, fills and wallet records—not accessed and not needed for this public method memo.

If execution needs private evidence and authorization/access is unavailable, the affected lane must stop with **`PRIVATE_DATA_AUTHORITY_UNAVAILABLE`**, not infer it from public proxies. [S1]

### Three bounded original-owner work packages

1. **Provenance and authority census:** establish what the existing classifier could legally do, with complete issue and delivery denominators.
2. **One frozen matched-budget challenger:** compare a minimal deterioration/failed-repair annotation against original risk and price/volatility controls; historical work remains development-only.
3. **Prospective collection and independent review:** only in an authorized registered lane, with delivery/quote evidence, fixed stopping rules and no production influence.

No package is persisted, dispatched or declared `CODEX_READY`.

---

## Final assessment

**The supplied evidence supports investigating delayed or insufficiently informative risk escalation. It does not establish a legitimate historical 4/5 alert, an earlier first warning, or a capital-preservation win.**

The most promising falsifiable hypothesis is:

> **Persistent loss of breadth and liquidity resilience, especially failed repair after an initial shock, may improve warnings of further downside beyond price/volatility—provided the gain survives source clocks, a matched warning budget, actual delivery delay and false-recovery costs.**

The equally important null is:

> **Those features may be delayed, correlated descriptions of price deterioration that add complexity without actionable advantage.**

**Current disposition:** `RESEARCH_ONLY` · `NO_LIVE_CHANGE` · `NO_NEW_BACKTEST` · `NO_TRADE` · `CLAUDE_REVIEW_PENDING` · `NOT_PERSISTED`.