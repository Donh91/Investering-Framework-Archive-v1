# ASTRA HIGH — Mission 3/5
## Scientific design review for a next-generation Kompas

**Supplied source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **RESEARCH DESIGN / STATIC SOURCE REVIEW / SHADOW ONLY**  
**Execution:** No tools, code, repository writes, external retrieval, paid dispatch, or trading performed.  
**Evidence boundary:** Supplied text was inspected; file bytes, SHA digests, Git ancestry, publication receipts, and current repository state were **not independently verified**.

**This is not a repetition of the prior W46 assessment. W47 is not scored here. No new market outcomes are introduced.**

## Executive judgment

The defensible next-generation Kompas is **not initially a larger predictive model**. It is an existing-owner forecasting system that can demonstrate, separately:

1. **What information was genuinely available before issuance;**
2. **What exact forecast was actually issued, and when;**
3. **Which independently observed outcome became known afterward;**
4. **Whether the forecast improved on simple, same-clock alternatives;**
5. **Whether any improvement survived dependence, model selection, abstention, and implementation costs.**

The supplied code materially improves what can be inspected compared with the earlier report: A’s formula, calibration procedure, scoring implementation, and internal digest definition are now visible. But it also exposes important unresolved methodological risks:

- Filtering historical bars by their **event time** does not prove those exact data vintages were available at issuance.
- A’s model-origin clock, A’s own publication, B’s own publication, and consumer delivery are distinct.
- A’s weekly decision logic can accept sufficiently populated but unfinished weeks and can overlook unresolved earlier weeks.
- B’s scoring route expressly lacks verified **B-first-issuance** evidence.
- A’s probabilistic close intervals and CN’s uncalibrated range envelopes do not have equivalent forecast semantics.
- B’s directional probabilities are, algebraically, **identical across BTC and ETH for identical views and horizons**, despite different volatility inputs.
- Historical evidence-index membership does not establish predictive feature use.
- No supplied evidence establishes an LSTM advantage, calibrated official probabilities, or risk-to-action economic value.

**Priority:** repair and test scientific admission before expanding model complexity. Preserve official ownership; treat every research challenger as an unpromoted alternative.

---

# 1. Evidence register and limits

For compact references, let:

`R = 06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/`

The digests below are **supplied identifiers**, not independently recomputed hashes.

| Ref. | Supplied source | SHA-256 | What it supports |
|---|---|---|---|
| **S0** | `AGENTS.md` | `4c2cc641e35e07e49e31d16b6aa960bbf6ceb4bd1ae1eb9fb05b2f53d275093a` | Governance, source/publication boundaries, existing ownership, Round 3 restriction, no self-promotion, display-only exception. |
| **S1** | `R/2026-11-16_ASTRA_HIGH_W46W47_ORIGINAL_RESEARCH_UNAUDITED_v1.md` | `981ce1be3655a031810aba7c7f79044ed923b0c608d509ce54fa3bd9f3bce864` | Prior source-limited assessment and documented gaps; not an independently audited result. |
| **S2** | `R/2026-11-15_W47_PREREGISTRATION_CANDIDATE_v1.md` | `abc1b55f547bcba249ce1dae263641f0d50d43a13bc3fd2a9be9a608a417f82f` | Candidate risk experiment, original owner references, proposed event definition, explicit unproven preregistration chronology. |
| **S3** | `06_RESEARCH_LAB/task2_challenger_a/issued/2026/W47/CHALLENGER_A_FROZEN_ISSUANCE.json` | `5bd6b6c35dfdf4603e078bbe32f86fb2f3d2ce602df03e75467a60261552cda9` | An A issuance object, its declared clocks, intervals, calibration summary, and research-only authority. No outcomes. |
| **S4** | `05_CYCLE_NAVIGATOR/CANONICAL_SCORE_AND_LINEAGE.md` | `765a35bf13b78cc02806286126543b68b66644a8e1655210e264b4ce2fc63e4f` | Public-series identity and retrieval rules; separation of frozen forecasts and completed scores. |
| **S5** | `scripts/research/task2_r1_original_causal_source_matrix_v1.py` | `dd0c23efb00aea63e45b2c343e1b963cea8f6d334a7dfbe35b2e1e73180a49cc` | Static source-role inventory and explicit historical PIT limitations. Execution results were not supplied. |
| **S6** | `scripts/research/task2_challenger_a_sqrt_t_vol_band_v1.py` | `6befca58d8eae42332132566373a016aaadf1db30cc43099572e364b3cec20b0` | A’s implementation, source filters, calibration, integrity checks, scorer, and decision logic. |
| **S7** | `scripts/research/task2_challenger_b_kompas_tilt_v1.py` | `0451d65720dedaed8721d5c4077ec11317cb223e8d6a019c00e0fcad19040fd6` | B’s transformation, packet selection, source binding, Brier scorer, and unresolved B-publication admission. |

### Important evidence gaps

The packet does **not** include:

- The required current cockpit, boundary maps, active registry, current production authority, or relevant skills.
- Independently witnessed first-publication receipts for the supplied research artifacts.
- Original hourly byte captures and complete vendor/revision availability histories.
- A row-level, vintage-bound calibration manifest for A.
- Original B forecast issuances and their own publication receipts.
- Complete official forecast, abstention, amendment, and delivery censuses.
- The current strategic projection artifact for 21–30 days.
- Original probabilities for official qualitative or ordinal outputs.
- An admissible decision/fill/cost/exit ledger supporting economic evaluation.

Consequently, this report does not certify current production routing or implementation readiness. Restricted-evidence-dependent verification remains **`PRIVATE_DATA_AUTHORITY_UNAVAILABLE`** in this session; private evidence must not be inferred or copied into this public research design.

S4’s “current” examples concern an older frozen period. Its **identity rules** are useful; its old current-week labels are not evidence of today’s current issue.

---

# 2. New scientific diagnosis from the supplied implementations

These are **static findings**, not claims that tests were run or that production behavior was observed.

## 2.1 What is already sound—and should be retained

A includes several valuable controls:

- Exact contiguous hourly slots for its volatility window;
- Rejection of duplicate and off-grid timestamps;
- Positive, finite, internally consistent price fields;
- Complete expected hourly census for scored paths;
- Original issuance digest verification;
- Refusal to regenerate a frozen issuance during scoring;
- Pairing A and CN on the same asset-days for their primary comparison;
- A separate A-only aggregate, rather than silently mixing denominators;
- Explicit research-only and no-promotion flags. [S6]

B adds:

- Explicit separation between evidence balance and probability;
- A separately defined probability-producing transformation;
- Source-bound reconstruction checks rather than trusting a self-generated digest alone;
- An earlier-week resolution barrier in its decision routine;
- An explicit final admission label stating that B-first-main issuance verification is pending. [S7]

These are meaningful design improvements. They are not, by themselves, proof of scientific admissibility.

## 2.2 Event-time filtering is not point-in-time provenance

A’s `issue()` excludes bars not closed by `t0`, and `calibrate()` uses completed prior weeks. That prevents a straightforward future-*event*-time leak.

However, `load_hourly()` reads repository CSV contents without a per-observation original-availability or revision-vintage gate. An old bar revised or first captured after `t0` can still have an event timestamp before `t0`.

Therefore:

> “Uses only days completed before T0” is necessary, but insufficient, for “point-in-time by construction.”

Required distinctions:

- Event occurred before T;
- Exact value was published before T;
- Exact value was captured and available to the producer before T;
- Exact value was actually used in the issued forecast.

The same applies to calibration data, seed derivation, source-health booleans, and feature transformations—not just prices. [S5–S6]

**Consequence:** no historical PIT admission solely from timestamp filtering.

## 2.3 A has multiple clocks; B adds another

A’s `issue_clock_utc` is tied to CN’s first-main clock. A’s own first-main availability is recovered separately during scoring.

That separation is helpful, but it establishes two different objects:

- **Model origin:** the clock used for A’s formula;
- **Research issuance availability:** when A’s exact artifact actually became available.

Neither is automatically consumer delivery.

B then derives a forecast from A and selected official packets, but its score gate uses **A’s availability**, not B’s own independently verified publication. The CLI correctly labels the result:

`SHADOW_DESCRIPTIVE_PENDING_B_FIRST_MAIN_ISSUANCE_VERIFICATION`

A deterministic forecast that can be reconstructed later is not necessarily a forecast that was issued earlier. [S3, S6–S7]

**Required rule:** every arm needs its own original issuance identity and availability proof. A’s receipt cannot serve as B’s receipt.

## 2.4 A’s maturity and “first eight valid weeks” logic need stronger barriers

In `score()`, A can assign a weekly winner once its paired-row minimum is met. There is no explicit full-week maturity requirement in that function.

In `confirmatory_decision()`:

- Missing or tied weeks are filtered out;
- Supplied valid weeks are sorted;
- The first eight supplied valid weeks are selected;
- There is no mandatory complete census proving that all earlier scheduled weeks are terminally resolved.

This can permit a premature decision if an unfinished week already has enough rows, or if an unresolved earlier week is absent from the input.

B’s `decide()` is stronger: it blocks an unresolved earlier week. But B’s maturity proxy is presence of the final hourly bar, and a mature `MISSING` week can be skipped. A missing-data state needs an explicit terminal-resolution policy; otherwise later recovery may alter cohort membership. [S6–S7]

**Nuance:** excluding exact ties in a properly specified sign test is not inherently invalid. The risks are unresolved eligibility, outcome-dependent inclusion, incomplete opportunity censuses, and unproven independence—not the word “tie” alone.

## 2.5 Eight weekly signs are not automatically eight independent trials

Both challengers use weekly cluster decisions. This is better than treating each asset-day as independent.

Nevertheless:

- BTC and ETH share market shocks;
- Consecutive weeks can belong to one extended episode;
- Rolling calibration reuses much of the same training history;
- Adaptive models can create serially dependent loss differences.

An exact binomial sign test needs justified assumptions about the signs. Labeling observations “weeks” does not establish those assumptions.

The current sign tests can be retained as **registered descriptive summaries** where appropriate, but a confirmatory claim needs an episode/dependence audit and effect-size uncertainty, not only a p-value. [S6–S7]

## 2.6 The interval comparison contains a target-semantics mismatch

A issues separate close and range bands at stated nominal levels.

CN’s bands, as described in the supplied assessment and acknowledged in A’s scorer, are source-issued range envelopes without established close-quantile semantics.

A evaluates CN’s envelope against the close using the same interval-loss coefficient as its primary probabilistic close interval.

That numeric comparison can be a **preregistered common decision-loss diagnostic**. It does not establish that CN issued an 80% close interval, and it does not make CN probabilistically miscalibrated at a nominal level it never claimed.

Also:

- `A_interval_score` is a single-level interval score, not WIS.
- Range containment is not endpoint containment.
- Full-day path containment is not a quantile forecast of the close.
- Public CN “precision” remains its own canonical product metric, not a substitute for MAE, WIS, or calibration. [S4, S6]

## 2.7 A’s uncertainty clock does not start at its price observation

The supplied object gives a price bar open at 07:00 and a declared issue clock at 08:35:56. Under the code’s hourly convention, that anchor is the close of the 07:00–08:00 bar.

The formula scales uncertainty by elapsed time from **issue clock**, while the anchor price is observed earlier.

This is a model-design question, not merely a timestamp formatting issue:

- Is the distribution conditional on a price observed at the anchor’s completion?
- Is there an unobserved interval between that observation and issuance?
- Should uncertainty include that interval, or should a fresher eligible anchor be used?
- Does calibration reproduce the same anchor age and partial-day scoring window?

A’s calibration uses a Monday 08:00 proxy; the supplied issuance uses a different origin and first scoring window. The historical pooled calibration does not automatically validate that changed geometry. [S3, S6]

**Do not repair the original issuance retrospectively.** Test a future, separately versioned alternative.

## 2.8 Calibration rows are not independent calibration evidence

A pools “needed z” observations across:

- Assets;
- Days within a week;
- Cumulative leads;
- Prior weeks.

Its four-week calibration summary contains 56 rows, but those are not 56 independent market episodes. Tail quantiles estimated from this pool are particularly uncertain.

Pooling can be sample-efficient, but it assumes enough comparability across horizon, asset, volatility state, and anchor age. Those assumptions need testing.

A’s four-/eight-week fallback and registered seed are visible in code. What remains unverified is:

- Original preregistration of that entire fallback policy;
- Original availability of every input vintage;
- The calibration-row manifest;
- Seed derivation chronology;
- Conditional coverage and tail stability. [S3, S6]

## 2.9 B’s probability is asset-invariant under shared views

Let

\[
v_{13}=(bull_{13}-bear_{13})/10,\qquad
v_{57}=(bull_{57}-bear_{57})/10.
\]

Using B’s implementation, its probability reduces algebraically to:

\[
p_{\mathrm{up}}(h)=
\Phi\!\left[
\frac{\mathrm{tilt}\left(
v_{13}\min(h,72)+v_{57}\max(h-72,0)
\right)}
{\sqrt{24h}}
\right].
\]

The asset-specific volatility cancels.

Thus, with identical horizon values and packet views, BTC and ETH receive the same directional probability, apart from numerical rounding. Their price centres can differ, but the probability evidence is not asset-specific.

This is not necessarily an implementation defect. It is a substantive restriction:

- B tests a shared market-direction transformation;
- It does not demonstrate independently estimated asset-level direction;
- Two correlated asset outcomes do not double the independent forecast evidence.

Further, the 5–7-day view contributes after 72 hours, including the intervening period before day five. That interpolation belongs to **B’s model**, not to the original official forecast. [S7]

## 2.10 B’s packet selection does not establish original expiry compliance

`select_views()` checks declared issue time, first-main time, status, and a lookback window. In the supplied function it does not explicitly check the original source-valid-until deadline.

It also searches for the latest **OK** view. A newer packet with a non-OK state may therefore be bypassed in favor of an older OK view.

Whether an older view remains legally usable depends on the original invalidation and expiry contract, which is not supplied. A lookback window is not itself an expiry contract.

**Required negative test:** a newer authoritative invalidation must not silently resurrect an older view unless the governing contract explicitly permits that behavior. [S0, S7]

## 2.11 Two earlier gaps can now be narrowed

**Digest domain:** S6 defines A’s internal digest as compact, sorted JSON before adding `issuance_sha256`. Its value need not equal the SHA-256 of a formatted file. The differing digests in S3 are therefore not, by themselves, evidence of corruption. Reproduction remains unperformed.

**Feature attribution:** S5 explicitly distinguishes the historical 24-field evidence index from the direct directional computation and health gates. The inspected code describes a delta-continuation mechanism, not demonstrated multifeature predictive intelligence.

Its assertions about historical counts and admissions are not execution receipts. Nevertheless, they explicitly reject treating publication witnesses or engine replay as full historical PIT admission. [S5–S6]

---

# 3. The essential scientific object: a genuine issuance–outcome pair

A forecast record and an outcome record must remain **separate immutable objects**, joined only after maturity.

## 3.1 Required clocks

For each forecast input:

- Event/window start and completion;
- Original provider publication or governed availability evidence;
- First collector receipt of the exact vintage;
- Producer availability;
- Revision identity;
- Source expiry.

For each forecast:

- Information cutoff;
- Model-fit cutoff;
- Model/formula version;
- Declared model origin;
- Exact artifact freeze;
- Independently evidenced issuance availability;
- First consumer delivery, where relevant;
- Explicit target start and end.

For each outcome:

- Target event/window;
- Observation completion;
- Original outcome publication/capture;
- First-known time for the accepted outcome vintage;
- Maturity/settlement rule;
- Subsequent correction lineage.

### Admission inequalities

For information-edge evaluation:

\[
t_{\text{qualified input availability}}
\le t_{\text{information cutoff}}
\le t_{\text{forecast issuance}}
< t_{\text{target end}}.
\]

For a wholly future path target:

\[
t_{\text{forecast issuance}}\le t_{\text{target start}}.
\]

For every training label:

\[
t_{\text{label first-known}}\le t_{\text{fit cutoff}}.
\]

For consumer-action evaluation, the relevant decision reference must be **after actual delivery and the frozen response latency**, not merely after repository publication.

Unknown consumer delivery can block action-value evaluation without necessarily invalidating a separately proven public forecast experiment. These are different admission gates.

## 3.2 Join identity

Use the existing owner’s identifiers, extended only through its governed schema:

- Forecast identity and immutable version;
- Public CN identity where applicable;
- Asset, venue, quote currency;
- Target definition/version;
- Target start/end;
- Forecast functional: point, quantile, class probability, path event, or qualitative state;
- Outcome identity and vintage;
- Experiment/model version.

**Never join by machine issue number alone.** S4 requires forecast week plus immutable public-series binding.

An amended forecast is a new version, not a replacement of the original. An outcome correction appends lineage; it must not silently rewrite the first-known record.

## 3.3 Denominators must precede scoring

Retain:

1. All scheduled opportunities;
2. Source-eligible opportunities;
3. Issued forecasts;
4. Missing/stale/unsupported-target abstentions;
5. Mature outcomes;
6. Pending, censored, missing, and corrected outcomes;
7. Common-eligible paired comparisons;
8. Distinct market episodes;
9. Quiet/non-warning opportunities.

A source row, forecast schema, publication witness, or initialization record is **not an outcome pair**.

---

# 4. What should compete—and what should not be conflated

| Arm | Legitimate interpretation | Required restriction |
|---|---|---|
| **Naive persistence** | Last qualified price remains the endpoint forecast; prior directional state may be a separately defined class baseline. | Freeze the same eligible anchor and target. Prior-week close and latest preissue price are different baselines. |
| **Drift** | Simple preissue trend extrapolation, preferably shrunk toward zero. | Lookback, shrinkage, clipping, and fit rules fixed before outer evaluation. |
| **Volatility challenger A** | Symmetric, horizon-scaled research intervals with rolling empirical multipliers. | Vintage-bound calibration; explicit nominal levels and target semantics; no historical repair. |
| **Directional challenger B** | A new probability model using official evidence balance as input. | B owns its probabilities and issuance. Official balance is still not probability. |
| **Official forecast** | Immutable native/official numerical or qualitative forecast in its original domain. | No conversion of prose into numerical forecasts after outcomes; no horizon stretching. |
| **HOLD** | A decision-policy comparator preserving a specified existing position state. | Not a price forecast, not automatically “no risk,” and not synonymous with no new purchase. |
| **Feature-engineered model** | Low-dimensional, regularized use of genuinely preknown inputs. | Source vintages, release lags, ablations, nested selection, and missingness controls. |
| **LSTM** | A higher-capacity SHADOW hypothesis. | No presumption that more bars equal more independent training episodes; no promotion from a small pilot. |
| **Live research display** | Existing narrowly authorized visual formula. | S0 says it is never scored or used for decisions or promotion. Exclude it entirely from experimental outcome evidence. |

The official owner remains the **operational incumbent**. That does not mean its statistical superiority has been established.

HOLD belongs in the decision-value experiment, not in a price-MAE ranking.

---

# 5. Horizon-specific targets and conditional research

The following are **proposed future target contracts**, not descriptions of existing admitted forecasts.

| Horizon family | Candidate numerical targets | Conditional/path questions | Ownership boundary |
|---|---|---|---|
| **1–3 days** | Exact 24-, 48-, and 72-hour endpoints, or separately contracted calendar closes | Subsequent downside excursion, first passage, short-lived wick versus persistent deterioration | Existing short-horizon owner; no conversion of a 12-hour forecast into a longer forecast. |
| **5–7 days** | Exact 120-, 144-, and 168-hour endpoints, or original calendar windows | Persistence of adverse regime, rebound risk, within-window low/high | Existing CN/Kompas bindings; preserve actual issuance-to-target durations. |
| **2–3 weeks** | Exact 14- and 21-day targets | Slow trend persistence, volatility transition, recovery versus continued drawdown | Numerical evaluation only when an actual numerical issuance exists. |
| **21–30 days** | Explicit 21- and 30-day targets from the governed strategic projection | Regime-transition risk and longer path downside | Governed weekly strategic owner only. No stretching of 2–3-week output. |

A 21-day target appearing in two presentation families is **one underlying forecast/outcome target**, not two independent successes.

### Path-wise downside

Separate at least:

- **Maximum adverse excursion from the frozen reference price**;
- **Peak-to-trough drawdown within the forecast window**;
- **First passage below a preregistered threshold**;
- **Recovery after the first adverse passage**.

These are different quantities.

With hourly bars, first passage inferred from an hourly low is interval-censored within that hour. A completed-bar warning cannot use the final low before the bar closes.

The candidate 72-hour adverse-event definition in S2 is a design source—not evidence that C1 was fully specified or prospectively issued. A warning activated by a breach cannot receive advance-warning credit for that same activating breach.

### Regimes

Start with a small, frozen set of preissue conditions, such as:

- Trailing volatility state;
- Trailing trend state;
- Source-quality state;
- A governed, preknown macro-event window where available.

Do not define regimes afterward as “the weeks when the model worked.”

Realized regime-transition labels may be used as outcomes or audit strata, but never retroactively as information available at forecast origin.

---

# 6. Evaluation: proper scores, dependence, and model selection

## 6.1 Point forecasts

Primary point loss:

\[
L_{\text{point}}=|\hat P-P_{\text{outcome}}|.
\]

Report raw asset-specific MAE and a paired normalized version using the same preissue scale.

Do not treat B’s log-space centre as an arithmetic conditional mean without an explicit forecast-functional contract. Likewise, A’s P0 must not retrospectively become a separately issued expected-close forecast.

## 6.2 Probabilistic intervals

For a genuinely issued central interval \([l_\alpha,u_\alpha]\):

\[
IS_\alpha=(u_\alpha-l_\alpha)
+\frac{2}{\alpha}(l_\alpha-y)_+
+\frac{2}{\alpha}(y-u_\alpha)_+.
\]

For original quantile intervals and an explicitly issued median \(m\), standard WIS can be frozen as:

\[
WIS=
\frac{
\frac12|y-m|
+\sum_{k=1}^{K}\frac{\alpha_k}{2}IS_{\alpha_k}
}{
K+\frac12
}.
\]

Report alongside:

- Marginal and prespecified conditional coverage;
- Width;
- Lower-tail and upper-tail misses;
- Horizon-specific results;
- Dependence-aware uncertainty.

If the median was not issued, use a clearly named interval-only score or a newly specified future contract—not an invented historical median.

For path envelopes, report simultaneous containment and width as their own target. Standard endpoint WIS does not automatically score a joint low/high path forecast properly.

## 6.3 Classification

Brier, log score, and probability calibration require **original issued probabilities**.

They do not apply directly to:

- Bull/bear evidence-balance counts;
- Ordinal pullback severity;
- Qualitative labels;
- A retrospective probability mapping fitted after outcomes.

For deterministic classes, use a preregistered confusion/loss framework, class prevalence, and abstention coverage.

B’s treatment of `close == P0` excludes those observations. That changes its target to a non-tie conditional evaluation. Preserve the historical definition; specify any future binary or three-class alternative before issuance.

## 6.4 Risk-to-action value

Evaluate a complete frozen policy, not just a warning label:

- Initial state;
- Permitted response;
- Delivery latency;
- Reference/executable price convention;
- Position rule;
- Re-entry/reset rule;
- Fees, spread, slippage, impact, and other applicable costs;
- Missed rebound/opportunity loss;
- Matched HOLD comparator.

Without those records, report **forecast/risk discrimination**, not economic benefit.

Actual realized economics and a prospective paper decision study are different evidence classes. Neither is established here.

## 6.5 Nested walk-forward design

Use chronological outer evaluation blocks.

Within each outer training history:

1. Admit only source vintages available at each historical origin.
2. Admit only labels already mature and known at the inner fit cutoff.
3. Fit scaling, imputation, feature selection, calibration, and hyperparameters inside inner chronological folds.
4. Freeze the resulting model or adaptive policy before the outer block.
5. Evaluate the outer block once.

Group BTC/ETH observations and all related horizons by market episode. Purge training labels whose target windows overlap an outer test episode. Embargo must account for both the longest relevant target and outcome-publication lag.

Do not naively form one enormous transitive cluster from continuously overlapping daily windows. Use prespecified sparse primary origins and episode/block rules; retain denser forecasts as correlated secondary evidence.

### Model-selection controls

- Maintain the census of all attempted candidates, including failed and abandoned ones.
- Do not pick a favorable horizon, asset, regime, or score after seeing results.
- A new parameterization after an outer result is a new development version.
- A final confirmatory cohort must remain untouched by model selection.
- A preregistered adaptive strategy is evaluated as **one strategy**, not as its hindsight-best component.

## 6.6 Sample efficiency without pseudo-replication

Use partial pooling and low-dimensional models before adding features or network capacity.

For the proposed program:

- Treat **eight fully resolved, distinct episode/horizon blocks** as an administrative pilot floor, drawing on the existing eight-cluster design—not as a power guarantee.
- Freeze the actual required sample \(N_j^\*\) from a prespecified minimum worthwhile effect, dependence estimate, and precision/power calculation before confirmatory collection.
- For rare-event work, require separately adequate adverse and quiet episode counts.
- For conditional claims, require support within each declared condition, not merely a sufficient pooled total.
- If variance, prevalence, or independent block counts cannot be estimated defensibly, the result remains a feasibility study.

No numeric \(N_j^\*\) can honestly be calculated from this packet.

Use a fixed scheduled cohort or a genuinely preregistered sequential design. Do not extend “valid weeks” until significance.

---

# 7. Twenty source-bound, falsifiable hypotheses

**Status of every ID below: `PROPOSED_NOT_REGISTERED / SHADOW_ONLY`.**

These are experiment specifications for original-owner review—not claims that new experiments or engines are authorized.

### Shared gates

- **G0 — Integrity:** independently admitted input vintages, original forecast issuance, exact targets, complete opportunity census, mature outcome lineage.
- **GP — Paired evidence:** at least the pilot floor above **and** the experiment’s prospectively fixed \(N_j^\*\); common-eligible comparisons.
- **GC — Conditional/class evidence:** GP plus adequate independent support in every claimed regime/class. Original probabilities required for calibration.
- **GR — Risk evidence:** GP plus a proposed minimum of eight adverse and eight quiet independent episodes as a feasibility floor; power/precision may require substantially more.
- **GL — Learning evidence:** enough disjoint training history to complete nested folds and a predeclared learning-curve/data-sufficiency gate, plus GP for untouched evaluation.
- **GU — Utility evidence:** GR plus a complete, frozen, latency- and cost-aware decision policy and matched HOLD reference.

The numerical floors above are **proposed design rules, not observed sample counts or guarantees of adequacy**.

For loss comparisons, define gain as baseline loss minus challenger loss. Support requires the preregistered uncertainty bound to exceed the minimum worthwhile gain \(\delta_j\). An upper bound below that threshold falsifies the claimed worthwhile advantage; intermediate results are inconclusive.

| ID | Source-bound hypothesis: null and alternative | Experiment and minimum-data/failure gate |
|---|---|---|
| **K3-01 — Official point value** | **H0:** Original official numerical forecasts do not improve paired MAE over same-clock persistence by \(\delta_1\). **H1:** They do. [S1, S4–S5] | Compare only genuinely issued numerical endpoints at each registered horizon. **G0+GP.** Unsupported endpoints abstain. Fail the advantage claim if it depends on a later baseline anchor, selected assets, or excluded losing opportunities. |
| **K3-02 — Shrunk drift** | **H0:** A simple shrunk-drift forecast has no worthwhile MAE advantage over persistence. **H1:** Its preissue trend information improves future endpoints. [S5–S6] | Freeze lookback, shrinkage, and bounds through inner folds. **G0+GP**, with both trending and non-trending support for a general claim. Fail if benefit disappears against identical-clock persistence or is concentrated in one exposed episode. |
| **K3-03 — Volatility scaling** | **H0:** A-style volatility-scaled intervals do not improve proper interval loss over a same-level, preissue historical-residual interval baseline without current-volatility adjustment. **H1:** They do. [S3, S6] | Same targets and nominal levels; score coverage and sharpness together. **G0+GP.** Fail if apparent improvement is coverage-only, relies on revised calibration inputs, or loses under proper width-penalized scoring. |
| **K3-04 — Conditional calibration** | **H0:** Horizon/anchor-age partial pooling does not improve A’s pooled calibration. **H1:** It improves conditional coverage and WIS without material aggregate deterioration. [S3, S6] | Small prespecified strata, hierarchical shrinkage, no post-hoc bins. **G0+GC.** Fail if a claimed condition lacks support or gains come from unbounded widening. |
| **K3-05 — Asymmetric tails** | **H0:** Allowing separately estimated downside/upside quantiles adds no useful interval skill over symmetric A. **H1:** Preissue asymmetry improves proper quantile/interval loss. [S2, S6] | Freeze a low-complexity asymmetric challenger; report both tails. **G0+GC**, including adverse and rebound episodes. Fail if downside improvement is purchased by unacceptable opposite-tail or total-score deterioration. |
| **K3-06 — Anchor-age uncertainty** | **H0:** Accounting explicitly for elapsed time since the price observation does not improve interval loss/calibration. **H1:** It does where anchor age is material. [S3, S6] | Future-only comparison of two explicitly defined clock conventions with identical anchors and targets. **G0+GP**, including nonzero anchor-age cases. Fail if target definitions differ or the result requires rewriting old A objects. |
| **K3-07 — B’s probability skill** | **H0:** Original B probabilities do not outperform both neutral probability and a training-only class-rate baseline. **H1:** They improve Brier score with acceptable calibration. [S7] | Require B’s own preoutcome issuance receipts. **G0+GC.** No artifact receipt means no confirmatory test. Fail if only the neutral baseline is beaten while a simple prevalence baseline dominates. |
| **K3-08 — Evidence balance beyond price** | **H0:** B’s balance input adds no predictive value beyond simple preissue price/trend/volatility information. **H1:** It supplies incremental out-of-sample information. [S5, S7] | Matched low-complexity models with and without balance; same probability functional and clocks. **G0+GL+GC.** Fail if ablation removes no skill, or balance merely repackages the same recent-price signal. |
| **K3-09 — Health-gated selectivity** | **H0:** A preregistered research abstention rule using source-health information does not improve selective forecast loss at matched coverage. **H1:** It does. [S5] | Preserve mandatory safety gates; compare only additional research selectivity. **G0+GP**, with adequate degraded and healthy episodes. Fail if “improvement” is solely disappearance of difficult periods from the denominator. |
| **K3-10 — Feature-engineered increment** | **H0:** PIT-safe breadth, relative strength, derivatives, settled-flow, or liquidity features add no worthwhile skill beyond price-only baselines. **H1:** A small frozen subset does. [S5] | First-known vintages and release lags for every feature; nested selection and leave-family-out ablations. **G0+GL.** Fail for any postissue feature, unstable selection, or no incremental outer-block gain. |
| **K3-11 — Preissue regime conditioning** | **H0:** A small volatility/trend regime partition does not improve downside prediction over an unconditional model. **H1:** It improves conditional future downside risk. [S2, S6] | Freeze regime definitions from preissue variables. **G0+GC+GR.** Fail if regimes are defined from subsequent crashes, or improvement is unsupported outside one transition. |
| **K3-12 — 2–3-week forecast value** | **H0:** A genuinely issued 14/21-day projection adds no value over persistence and shrunk drift. **H1:** It improves the registered point/interval target. [S0–S1, S5] | Require actual long-horizon issuance; do not extrapolate seven daily bands. **G0+GP** at the longer dependence scale. No numerical projection means `UNSUPPORTED_TARGET`, not a manufactured prediction. |
| **K3-13 — Strategic 21–30-day value** | **H0:** The governed strategic projection does not beat simple same-origin benchmarks at its original targets. **H1:** It does. [S0, S4] | Use only the original strategic owner and frozen target contract. **G0+GP** at month-scale dependence. Fail admission if source missing; do not count shared 21-day targets twice. |
| **K3-14 — Sequential downside escalation** | **H0:** Fully specified C1 does not improve subsequent-event warning value against both simple risk and original issued risk at equal alert budget. **H1:** It improves lead/decision loss without excess false alerts. [S2] | Freeze qualifier, escalation mapping, reset, reference price, and subsequent event. **G0+GR.** Fail if warning gets credit for its own triggering breach, or advantage disappears under actual delivery timing. |
| **K3-15 — Confirmation versus wick** | **H0:** Consecutive completed-bar confirmation does not improve net warning quality over immediate breach detection. **H1:** False-alert reduction exceeds the cost of lost lead time. [S2, S6] | One frozen confirmation rule; include transients, persistent declines, and recoveries. **G0+GR.** Fail if confirmation systematically arrives after the relevant avoidable loss or creates worse missed-event costs. |
| **K3-16 — Adaptive recalibration** | **H0:** A preregistered drift-triggered calibration policy does not improve on A’s scheduled rolling rule. **H1:** It adapts better to shifts without destabilizing quiet-period forecasts. [S6] | Drift detector, update trigger, training cutoff, and fallback frozen as one strategy. **G0+GC**, with genuine transition and stable episodes. Fail if updates use immature residuals or are selected after seeing which adaptation won. |
| **K3-17 — Uncertainty-based abstention** | **H0:** A frozen uncertainty/ood abstention policy adds no whole-opportunity value over always forecasting. **H1:** It improves selective risk and total policy loss after pricing abstention. [S0, S5–S6] | Compare risk–coverage curves and one frozen operating point; retain all opportunities. **G0+GP.** Fail if skipped opportunities have no assigned evaluation treatment or coverage falls below the registered minimum. |
| **K3-18 — Risk-to-action versus HOLD** | **H0:** A fixed shadow response/re-entry policy provides no net advantage over the matched HOLD policy. **H1:** It improves registered downside-sensitive utility after all costs and missed recovery. [S1–S2, S5] | **G0+GU.** Separate paper feasibility from actual realized economics. Missing decision, delivery, sizing, exit, or cost evidence makes utility `NOT_EVALUABLE`, not zero. |
| **K3-19 — LSTM incremental value** | **H0:** A bounded LSTM adds no robust out-of-sample value over persistence, drift, and a regularized feature model after compute/selection costs. **H1:** It adds a stable worthwhile gain. [S5–S6; no LSTM evidence supplied] | Same admissible inputs; nested chronological selection; fixed seed policy and tuning budget. **G0+GL**, with a preregistered training-sufficiency gate. Fail for unstable seeds, insufficient episodes, or gains attributable to broader tuning rather than architecture. |
| **K3-20 — Budget-efficient orchestration** | **H0:** Adaptive research computation either saves no meaningful cost or degrades forecast/source performance beyond tolerance. **H1:** It reduces measured compute cost while meeting a frozen noninferiority margin and source coverage. [S0, S6–S7] | Compare replayable execution policies using actual cost/runtime/coverage receipts. **G0+GP** over quiet and stressed operational periods. Fail for missed required captures, changed forecast opportunities, duplicate dispatch, or unverified cost accounting. |

### Multiplicity and priority

Do not launch twenty concurrent “confirmatory” searches.

Recommended first scientific wave, after admission:

1. **K3-01:** official point value against persistence;
2. **K3-03:** volatility-interval value;
3. **K3-14:** subsequent-event downside warning value, only once fully specified.

Freeze one primary horizon/estimand for each and a familywise procedure, such as Holm control at a proposed 5% level. Other hypotheses remain development or later preregistered cohorts. A later confirmatory claim cannot reuse a holdout already used to select that hypothesis.

---

# 8. System design inside CN/MM/Task2—without another truth store

## 8.1 Logical flow

**Existing governed source owners**  
→ original capture/vintage bindings  
→ **existing canonical forecast owners**  
→ immutable research issuance references  
→ separate mature-outcome references  
→ **existing Task2 evaluator**  
→ source-qualified research results  
→ MM/CN consume the relevant canonical result or limitation.

This is a logical design, not a claim that the required extensions already exist.

### Ownership

- **Source #1827:** original capture, clocks, freshness, completeness, revision evidence.
- **CN #1516:** public-series identity, original forecast/target binding, product accountability.
- **Task2 #1596:** research admission, comparison protocol, paired evaluation, candidate census.
- **Risk #1553:** warning semantics, episode definitions, escalation/reset policy.
- **Strategic owner:** 21–30-day projection authority, resolved through the existing canonical route.
- **Bridge #173:** independent advisory methods review through the existing route.

These owner references come from the supplied material; their current operational status was not verified.

## 8.2 Storage principles

- Extend existing owner schemas only after discovering their actual definitions.
- Store references to canonical inputs, not another copied market-data database.
- Keep immutable history separate from compact active/pending manifests.
- Preserve original, amended, and corrected versions.
- Keep public metadata/value-free bindings separate from restricted payloads.
- Reuse existing validators and scorers; repair their admission boundaries rather than duplicating them.
- A render request does not create a new forecast issuance.
- A source tick alone does not create another experiment dispatch.

For any producer change, document the S0 chain:

**producer → persisted object → manifest → receiver → consumer → executed CI → retention**

Forecast growth at 7/30/90 days from actual record sizes and opportunity counts; do not invent byte estimates.

## 8.3 Adaptive, budget-efficient research

Use increasing-cost stages:

1. Source/target validation;
2. Persistence and drift;
3. Existing A/B deterministic computation;
4. Small regularized feature model;
5. LSTM only after data-sufficiency and incremental-value gates.

Reuse identical validated source snapshots across arms. Cache by source/model/target identity. Do not recompute because an unchanged clock or pointer was reread.

Adaptation may change **research computation allocation** under a frozen policy. It must not silently change the forecast-opportunity denominator or stop collecting difficult outcomes.

Any paid model work requires a separate current authorization and verified cap. The supplied policy prohibits automatic Astra selection or fallback. No paid route is launched or proposed as automatically available here.

---

# 9. Exact tests to commission through the existing owners

**All tests below are proposed and unexecuted.** They are acceptance criteria, not fabricated PASS results.

| Test ID | Adversarial or positive fixture | Required result |
|---|---|---|
| **T01 — Event/availability split** | A bar’s event ends before T, but its exact vintage is first available after T. | Reject it as an input to that forecast, despite its old event timestamp. |
| **T02 — Forecast’s own publication** | CN is available at T; A or B first appears later. | Preserve separate clocks. Never inherit CN/A publication as the later arm’s issuance. |
| **T03 — B receipt missing** | B has a valid deterministic digest but no original B publication proof. | Descriptive-only or blocked; no confirmatory probability result. |
| **T04 — Digest domains** | Reformat an unchanged JSON object; separately alter a value. | File hash may change under reformatting while canonical payload digest remains valid; value alteration must fail the payload check. |
| **T05 — Exact hourly census** | Missing, duplicated, off-grid, or invalid OHLC entry in a required window. | Fail the affected source/target gate; never silently overwrite or interpolate. |
| **T06 — Calibration vintage leak** | A completed prior-week observation is revised after the current issue. | The later vintage cannot enter the original calibration. |
| **T07 — Anchor-clock contract** | Anchor completion, model origin, and target start differ. | Require explicit elapsed-time and conditioning semantics; reject an undefined mixture. |
| **T08 — Target/metric mismatch** | Feed an uncalibrated range envelope to a probabilistic close-calibration routine. | Reject the calibration claim; allow only an explicitly named common-loss diagnostic. |
| **T09 — Premature weekly result** | Enough paired rows exist, but the registered week/episode is unfinished. | `PENDING`; no weekly confirmatory winner. |
| **T10 — Earlier cohort gap** | Later winning weeks are supplied while an earlier scheduled week is unresolved. | Decision remains pending. Duplicate cohort identities invalidate the look. |
| **T11 — Expiry/invalidation** | An older OK packet exists, but its expiry passed or a newer authoritative invalidation exists. | No revival of the older view unless the source contract explicitly permits it. |
| **T12 — B algebraic restriction** | Different asset volatilities, identical views and horizons. | Confirm the expected shared probability structure; do not count it as independent asset-specific model evidence. |
| **T13 — Future-data invariance** | Change data unavailable at the frozen origin while retaining all admissible inputs. | Original forecast must remain unchanged. |
| **T14 — Fold leakage** | A training label matures after the fit cutoff, or an episode crosses train/test boundaries. | Exclude/purge it according to the frozen fold contract. |
| **T15 — Duplicate target evidence** | The same 21-day target appears under two horizon headings or two consumers. | One underlying outcome identity; no duplicated independent sample credit. |
| **T16 — Intrabar warning leakage** | A warning uses a bar’s final low before the bar completes. | Reject that timing. Report hourly first passage as interval-censored, not tick-exact. |
| **T17 — Probability provenance** | Input is an ordinal severity or bull/bear balance without an original probability model issuance. | Disable Brier/log/calibration claims for that input. |
| **T18 — Missing outcome semantics** | Outcome incomplete, unavailable, or still immature. | `PENDING`, `MISSING`, or `CENSORED` as contracted—never automatically success, failure, or negative event. |
| **T19 — Semantic idempotency** | Same source bindings, target, model, and state are processed again. | No duplicate issuance/dispatch. A genuinely new registered target can create exactly one new object. |
| **T20 — Authority/privacy/display isolation** | A private value enters public output, a live-display number enters scoring, or a shadow result requests official promotion. | Hard rejection; preserve the public/private boundary and research-only authority. |

For consequential implementation, tests must be executed in native exact-head CI and include guard-removal checks demonstrating that the critical negative tests actually fail when the guard is removed. Test existence or collection is not execution evidence. [S0]

---

# 10. Prioritized 30/60/90-day program

The schedule is a program of **conditional work**, not authorization to run restricted studies.

**Round 3 remains `PROSPECTIVE_COLLECTION_ONLY`; hypothesis testing and outcome scoring remain OFF.** Any evaluation below requires an explicitly authorized cohort and active test outside that restriction. Otherwise the deliverable remains collection/integrity evidence only. Rounds 1 and 2 are not reopened.

## Days 1–30: establish admission and freeze the science

### Priority 0 — Source and clock integrity

- Resolve the current cockpit, boundary maps, canonical owners, active registry, and relevant skills.
- Obtain exact original issuance/publication evidence for each research arm.
- Bind calibration rows to original availability vintages.
- Separate model origin, issuance, delivery, target, and outcome-known clocks.
- Resolve official expiry/invalidation semantics.
- Reconcile public CN identities through the canonical series route.

### Priority 1 — Freeze the first research contracts

- Define target functionals and calendars for all four horizon families.
- Select first-wave primary estimands and minimum worthwhile effects.
- Freeze opportunity census, missing-data resolution, episode grouping, sample size/stopping, and multiplicity.
- Specify C1 fully or retain `C1_UNSPECIFIED`.
- Obtain independent methods review before any confirmatory issuance.

### Priority 2 — Test admission defects

Commission T01–T11 first, through the existing intake and implementation owners.

**Day-30 deliverable:** an audited source/target contract and executable-test evidence, or explicit blockers. Not a model-skill claim.

## Days 31–60: collect and validate the paired system

- Run permitted prospective collection under existing owners.
- Preserve all scheduled opportunities and abstentions.
- Validate producer-to-consumer joins without using outcomes to tune the design.
- Freeze persistence, drift, A, and any fully admitted B arm at the same registered opportunities.
- Audit path completeness and source latency.
- Complete leakage, episode, privacy, and idempotency tests.
- Measure real compute, storage growth, duplicate ratio, and pending backlog.

Feature engineering can proceed only as permitted development on separately admitted material. LSTM work remains deferred unless the training-sufficiency gate is met.

**Day-60 deliverable:** a reproducible, source-bound issuance/outcome linkage process and an honest maturity census. No forced interim efficacy look.

## Days 61–90: independent adjudication, not automatic adoption

For any separately authorized cohort whose preregistered endpoints and sample requirements are satisfied:

- Perform the single registered evaluation;
- Report paired losses, proper interval scores, calibration where legal, coverage, abstention, and episode uncertainty;
- Audit missingness and model-selection history;
- Evaluate warning lead and false-alarm costs separately from economic value;
- Retain, reject, or classify each hypothesis as inconclusive.

If sample gates are not met, do not substitute extra correlated rows.

In particular, **90 days cannot be assumed to provide adequate independent 21–30-day evidence**. Long-horizon research may require substantially longer collection. Sparse events can also leave short-horizon downside studies inconclusive.

**Day-90 deliverable:** an independently audited shadow research decision and the next predeclared collection boundary. **No live model promotion.**

---

# 11. Independent Claude methods audit — requested handoff

**Please route the following request to an independent Claude reviewer through the existing Task2/Bridge owner route. No audit has been dispatched or received in this response.**

> **Independent Claude methods audit requested — Mission 3/5**
>
> Review this design against supplied source-main  
> `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
> and the eight SHA-identified sources in its evidence register.
>
> Do not repeat the prior W46 report, score W47, reopen closed evidence, analyze Round 3 outcomes, or infer publication from Git committer metadata alone.
>
> Independently adjudicate:
>
> 1. Whether A’s event-time filtering supports its PIT claim;
> 2. Separation of CN origin, A issuance, B issuance, and consumer delivery;
> 3. A’s incomplete-week and earlier-cohort-gap risks;
> 4. B’s maturity and terminal-missing semantics;
> 5. The algebraic cancellation of volatility in B’s directional probability;
> 6. Original expiry and newer-invalidation handling;
> 7. Anchor-age, proxy-origin, close/range, and horizon semantics;
> 8. WIS eligibility and the limits of applying probabilistic interpretations to CN envelopes;
> 9. Episode grouping, nested walk-forward, multiplicity, and sample sufficiency;
> 10. Whether each of the twenty hypotheses has a genuinely falsifiable null, adequate source binding, and an enforceable failure gate;
> 11. Whether the proposed implementation remains within CN/MM/Task2 ownership and excludes the never-scored live display;
> 12. Whether any proposed economic claim exceeds available decision, delivery, execution, and cost evidence.
>
> Return a finding-by-finding assessment distinguishing **source fact**, **static implication**, **runtime evidence needed**, and **methodological judgment**. Identify blockers and required revisions. Do not issue release authority or model-promotion approval.

## Bottom line

The supplied material supports a stronger **research design**, not a demonstrated predictive edge.

The highest-value next step is to make original availability, issuance, target identity, maturity, and dependence **enforceable in the existing evaluator**. Then test the simplest alternatives first.

A next-generation Kompas earns credibility by knowing when it has not forecast, when an outcome is not yet known, when an apparent gain is merely selection, and when it must abstain—not by producing a more elaborate line.