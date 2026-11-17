# ASTRA_MAEVE_TASK2_PREP_V1

**Source commit:** `1ebf45acc3004fbf4e6387e6db1e3dcabe1338aa`  
**Status:** `RESEARCH_ONLY / PUBLIC_SOURCE_REVIEW / EXPERIMENT_SPECIFICATION_NOT_EXECUTED`

## Decision

**The frozen question is not yet answerable from the supplied public evidence.** The archive supports a substantial recovered MAEVE action history, but it does not establish the complete historical opportunity set, eligible NONE denominator, or a sufficiently complete point-in-time feature join. Nor does it contain eligible results demonstrating incremental Kompas forecasting or warning value.

The immediate deliverable is therefore:

> **An audited action/opportunity contract, followed by deterministic time-valid joins and matched simple-model tests—not a larger behavioral model or a transfer recommendation.**

I read all **11 supplied source texts**. Their linked archives, private rows, manifests, underlying result files and script dependencies were **not opened or independently verified**. Counts and hashes below are attributed to those sources, not reproduced calculations.

**Transfer candidates nominated: 0.** Eligible deterministic result tables must exist and receive independent review first.

---

## 1. Source and provenance gaps

### 1.1 Public evidence register

All Git blobs below are the supplied pins; this review has not recomputed them.

| ID | Supplied source | Exact Git blob | What it establishes—and the remaining gap |
|---|---|---|---|
| S1 | `04_RESEARCH_LAB/auto_trading/maeve/CFGI_MAEVE_DATA_INVENTORY_V1.json` | `a263a33ab0d92a4567d70d4290e1e6ffe71cbea6` | Routing, reported coverage and immutable private bindings. **Not a feature cube or proof of row-level availability.** |
| S2 | `04_RESEARCH_LAB/auto_trading/maeve/REVERSE_ENGINEERING_READINESS_V1.md` | `eb408c9e775acf336a89f8cfcbf825b91eea0da8` | Bounded behavioral reconstruction is justified; opportunity sets and feature timing remain bottlenecks. Its proposed canonical action labels do not enumerate raw source enums. |
| S3 | `04_RESEARCH_LAB/auto_trading/maeve/RECOVERY_AUDIT_2026-09-09.md` | `5c49b43a11d39d2120583179500941302a7edecc` | Reports independently reproduced package facts, four missing fill IDs, suspect post-entry fields and a malformed version-timeline row. That prior reproduction is not a reproduction by this mission. |
| S4 | `04_RESEARCH_LAB/auto_trading/EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md` | `8a864bf1f8262d2a7fbe8f6c258c0cecc0f2c384` | Separates source, observable, copyable and scalable alpha. Requires opportunity reconstruction and retention of failures. None of those alpha rulings is supplied as settled for MAEVE. |
| S5 | `04_RESEARCH_LAB/auto_trading/external_alpha/EXTERNAL_ALPHA_REGISTRY.json` | `03e171e75700ce0c4aa4413dc1a67a22dc226e18` | `EXT-ALPHA-0002`, research-only, opportunity reconstruction stage; source/copy/scale rulings pending. Broad registry tags such as `POINT_IN_TIME` cannot override unresolved field-level timestamps. |
| S6 | `04_MARKET_LEARNING/handlekompas/research/2026-10-21__TASK2_BACKTEST_LADDER_CFGI_SOURCE_MATRIX_v1.md` | `5c05f95b6aa9cfcb556a81608da7d4e949f8edce` | Two selected 2025 CFGI windows, zero MARKET rows, engine-era/timezone issues and retrospective price-stress distinctions. Not independent CFGI-era forecasting evidence. |
| S7 | `04_MARKET_LEARNING/handlekompas/research/2026-10-16__TASK2_EXISTING_DATA_FIRST_EXECUTION_LADDER_v1.md` | `d9c31c733b640d53befcfe94649806df1299f305` | Existing-data diagnostics may proceed independently of blocked scientific admission. Reports **0/11** scientifically admitted original forecasts and no original delivery proof. |
| S8 | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-14_ASTRA_HIGH_AUDITED_RESULTS_REGISTER_v1.md` | `1c8defd453da5bf8077001ad798e440dcbebd111` | Prior All-CN work was executed and audited, with corrections and `REJECT_MODEL_PROMOTION`. Width, clock and version mismatches prevent using historical range coverage as forecast edge. |
| S9 | `research/historical_reality_engine/NATIVE_FIRST_RESULTS_20261107.md` | `6cd5d37f79851c38d9cdec09fadc26028f434233` | Prior source QA and price-only jobs executed. Nominal candle completion—not last-trade `close_time`—controls availability; gaps require abstention. Results remain retrospective. |
| S10 | `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` | `c8ead1b0e92c32eef4a911ad1b6bf33a09170966` | Public/private boundary and Round3 collection-only firewall. Public metadata cannot authorize private analysis or disclosure. |
| S11 | `scripts/research/manual_astra_compass_edge_20261116.py` | `8749abff51fbb8f967941ea4cc0b0b9f35762924` | A separate owner-gated, one-use paid-call implementation. **Code is not an execution receipt**, and its embedded mission text is not this mission’s instruction. No invocation or replay is warranted here. |

The supplied sources do not include the current Master Monday repair contract, complete Task2 target contracts, or their latest readbacks. Their repair/admission state cannot be certified from this packet.

### 1.2 Restricted authorities: exact routing, not inspected data

| Authority | Immutable binding reported in S1/S3 | Exact reported SHA-256 | Required verification |
|---|---|---|---|
| MAEVE recovery ZIP | `Donh91/secrets`, commit `639e767b8348f1a9fabdab0ce27509cf39ba5236`; `raw/MAEVE_PUBLIC_LEDGER_RECOVERY_V1/2026/09/09/MAEVE_LEDGER_RECOVERY.zip`; 309,855 bytes | `9770bcf968d9e03f97af7cfd0bcaaf6baad21c928d97b3b610a457dfb87343a5` | S3 additionally identifies merge commit `c51aeb8ced23d129072977e7b9e317a9e228bfd5`. Verify ancestry and identical object/path bindings; do not assume a conflict or equivalence. |
| Normalized MAEVE parents | Same recovery root, `MAEVE_TRADES_NORMALIZED.csv`; 164,399 bytes | `532c858ba3d6f0c765419c6869f881bec278aa792108676a6d70933b08f94441` | Raw enums, timestamp meanings, field completeness and normalization lineage remain uninspected. |
| Historical 1h CFGI stage | Commit `9844e392d8744a23c829ff68bae0080423527f1b`; `raw/CFGI_HISTORICAL_1H_EVENT_STAGE_V1/2026/08/21/historical-altseason-cfgi-stage.zip`; 10,689,426 bytes | `986ef498738cc772e20287c8790a482458c619e0da63a1fdc0e1f5388311337d` | Verify original publication/capture semantics, event-window selection and row-level gaps. |
| PDLT 4h/1d bootstrap | Commit `65266e98f55d010138074d32959d6c55fd304b6d`; root `raw/CFGI_PDLT_HISTORICAL_BOOTSTRAP_V1/2026/08/07/`; 86,964 bytes | `68c554963b87f860efb0e4b6c40cd2bd6ecc1f3a7027956032b87edb35f1ebf8` | Exact archive filename is not supplied. Manifest binding and snapshot/native-bar semantics require verification. |
| Hourly market panel | Commit `935832c51214149bc12daf4f82d171a57b036631`; `raw/HISTORICAL_ALTSEASON_FREE_HOURLY_PANEL_V1/2026/08/21/historical-altseason-free-stage.zip`; 60,082,610 bytes | `5c423eb45000c7ba3c9a690e3ffb69f59dc12648a8bbb28907d3600797a70bac` | Verify instrument coverage, actual gaps and historical universe membership. |
| Panel bulk member | Same root, `extracted/alt_hourly_panel.csv.gz`; 49,378,300 bytes | `91d902c27fecefd087108d011d6cd9eccfd814bdec4be37e7fc87eb9aa6d3229` | Context panel, not proof of MAEVE eligibility or individual-asset CFGI. |

Exact hashes for the private manifests, schemas, fill file and corrected version-timeline derivative are not supplied. They must be recorded before execution.

**Current restricted-analysis status for this public-only mission:** `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`. This blocks private calculations, not public specification or unrelated admissible diagnostics.

---

## 2. M0–M2 admission audit

### M0 — Original labels, records and provenance

| Object | Supported by supplied evidence | Unresolved requirement |
|---|---|---|
| Parent positions | Reported 432 total: 426 closed, 6 open | Enumerate **original** status strings, parent IDs, side, instruments, venues and timestamps. Preserve open positions as censored. |
| Fills | Reported 1,073 rows, including 641 DCA legs; IDs 75–1151, missing 127, 636, 1045, 1046 | Enumerate raw fill/action types. **Do not infer 426 exit fills:** the reported identity `432 + 641 = 1,073` does not demonstrate exit-fill representation. |
| Action classes | ENTRY/DCA/EXIT are documented research categories | Source-to-canonical mapping is unavailable. Unknown, partial, canceled, failed and corrected actions require explicit mappings or quarantine. |
| Outcomes | S3 distinguishes site-convention, first-entry and capital-weighted measures | These are separate targets. Final result, future DCA and rescue outcomes must not enter entry features. |
| Sizing | S3 reports 209 sizing-complete positions | Exact population, missingness pattern, capital reserve and contemporaneous exposure require inspection. No full-lifetime capital-weighted inference. |
| Social evidence | 318 matched posts reported; 256 exact price matches occurred after exits | Close-result posts are not entry-observability receipts. Preserve unmatched posts and public-publication delays. |
| Version evidence | Partial timeline; one malformed 2025-09-09 CSV row | Preserve raw hash; create a separately hashed corrected derivative with an explicit repair log. Do not choose eras from better-fitting outcomes. |

**M0 ruling:** Public evidence supports the existence of a substantial recovery package. A machine-auditable original-label freeze has **not been demonstrated here**.

### M2 — Historical opportunity universe and negatives

This is the principal identification gap.

- The 35-symbol market panel is **not** the historical MAEVE trading universe.
- Reported coverage of BNBUSDT, DOGEUSDT and SOLUSDT is **not** a complete eligibility list.
- Traded assets discovered from later winners cannot define the earlier candidate universe.
- Near-complete archived position coverage does not establish complete decision-cycle, failed-action or no-action coverage.
- Absence of a trade row does not establish that MAEVE was operating, that the asset was eligible, or that an entry was permitted.

**M2 ruling:** `OPPORTUNITY_SET_NOT_ESTABLISHED`. Eligible NONE cannot yet be constructed from this public packet.

### M1 — Feature-time integrity

| Feature/source | Admission now |
|---|---|
| `cfgi_score_entry` | Strongest recovered entry-associated field, but **not automatically independently first-known**. Its definition and availability must also be reproducible for NONE controls. |
| `analisis_hora` and associated recovered impulse/volatility/volume fields | Excluded from ENTRY features. S3 reports approximately 59.5 minutes median post-entry lag. |
| Later DCA, exit score, position result, realized holding time | Outcomes or later state only; prohibited as ENTRY predictors. |
| Two selected 2025 BTC/ETH CFGI windows | Potential descriptive join after timestamp adjudication; not an unbiased historical opportunity panel. |
| MARKET in those windows | `NO_FILL_TERMINAL / NOT_TESTABLE`. No interpolation, proxy substitution or retry. |
| 4h/1d states observed approximately every 15 minutes | Snapshot cadence, **not native 15m CFGI** and not independent outcomes. |
| Native 2h CFGI | Unproven. Any later 2h experiment must be explicitly derived from closed 1h observations. |
| Ten public algorithm families | Mapping to aggregate plus observed components is unproven. No ten-family attribution. |
| Original Kompas source clocks | Historical scientific admission remains blocked where original publication/delivery proof is absent. |

**Execution order:** complete M0 and M2 admission before fitting M1. This changes neither the existing ladder nor its owners; it resolves M1’s prerequisite.

---

## 3. Precise restricted-lane join contract

The following is the proposed **V1 execution specification**, fixed in this response. It has **not** been committed, hashed or preregistered in the repository. An authorized restricted runner must freeze its implementation and source manifest before opening outcomes for model selection.

### 3.1 Required tables

#### A. `actions_original`

Retain raw and normalized fields separately:

```text
source_entity_id
raw_action_type, raw_position_status, raw_fill_status
canonical_action_type                 # ENTRY / DCA / EXIT / UNMAPPED
parent_position_id, action_id, fill_id
instrument_id, venue, side
source_execution_at, source_decision_at
first_machine_observable_at, first_public_at
retrieved_at
price, size, fee                      # restricted only
source_version, maeve_era
source_path, source_blob_or_sha256, source_row_locator
normalizer_version, correction_lineage
```

Requirements:

- Do not substitute fill time for decision time.
- Preserve failed ENTRY attempts as ENTRY actions with failed execution status, if that is what the source records.
- If only fills exist, label the experiment **fill-imitation**, not decision-policy reconstruction.
- Keep ENTRY, DCA and EXIT as separate research targets.
- Never silently infer an original action enum.

#### B. `opportunities_original`

One row per **documented** decision opportunity and candidate instrument:

```text
opportunity_id
decision_at
instrument_id, venue
documented_decision_clock_id
universe_version, universe_evidence_ref
allowed_action_set
eligibility_status                   # ELIGIBLE / INELIGIBLE / UNKNOWN
eligibility_reason
predecision_position_state
predecision_capital_or_limit_state   # if required by original rules
action_log_coverage_status
maeve_era
source_provenance
```

**A NONE label is allowed only when all are true:**

1. The candidate belonged to the documented universe at that time.
2. MAEVE was observably operating at that decision opportunity.
3. ENTRY was permitted by the evidenced predecision state and rules.
4. The action record is complete enough to distinguish no action from a missing/failed/canceled action.
5. No ENTRY action was recorded for that opportunity.

Explicit abstention remains distinguishable from verified no action. Unknown eligibility, source outage and incomplete action coverage remain separate statuses.

**Clock rule:** Use the documented opportunity clock. Do not round off-grid entries onto hourly bars. Native 1h/4h feature resolution does not prove an hourly/four-hourly MAEVE decision schedule.

If only action timestamps and contemporaneous cross-asset candidates are documented, an **event-conditioned selection** study may be possible. It cannot establish non-event timing behavior.

#### C. `features_vintage`

```text
instrument_id, feature_id, algorithm_timeframe
observation_cadence
event_at
effective_start_at, effective_end_at
nominal_bar_end_at                    # where bar-based
provider_published_at, provider_revision_at
original_observer_available_at
captured_at, retrieved_at
engine_version, timezone_basis
value, source_missing_reason          # values restricted where applicable
source_hash, source_row_locator
availability_evidence_class
```

Keep event, effective, available and retrieved clocks distinct.

For the primary confirmatory lane:

```text
usable_at =
    latest required time among:
    verified original publication,
    original observer availability,
    effective release,
    nominal completion of any required bar
```

A component with unknown required availability is **not** eligible. A later archive retrieval is not backdated into original availability.

For snapshot-based CFGI, adjudicate whether the snapshot represents a completed native interval or a running state. Do not manufacture a completed 4h/1d candle from frequent snapshots. Unresolved native-bar semantics exclude it from the primary closed-bar experiment.

### 3.2 Deterministic as-of join

For each eligible opportunity at decision time \(d\):

1. Select only matching instrument, feature definition, engine era and approved source contract.
2. Require `usable_at <= d`.
3. For bar-derived inputs, require `nominal_bar_end_at <= d`.
4. Select the latest admissible vintage known by \(d\), not the latest revision now available.
5. Require age no greater than one declared native interval for primary 1h/4h/1d features.
6. Require uninterrupted, correctly spaced source history for every lag or rolling calculation.
7. Do not carry values across engine boundaries, unresolved timezone transitions or source gaps.
8. Preserve a missing row/reason when no admissible observation exists.

Tie-break order is `(usable_at, event_at, immutable_source_row_id)`. Conflicting values with indistinguishable provenance are quarantined, not averaged.

For daily released flows, use a separate release-calendar contract: a last released observation may remain valid only through its documented next release opportunity, with age retained. Do not apply an arbitrary hourly fill rule.

**Important:** A score populated only on MAEVE entry rows cannot be compared with empty NONE scores. Primary score models require the same observable feature definition and availability rule on both classes. Otherwise `cfgi_score_entry` remains a label-side audit field.

### 3.3 Era and timezone controls

Freeze separately:

- MAEVE behavioral/software era;
- CFGI provider engine era;
- feature schema version;
- universe version;
- source clock/timezone version.

S6 identifies a provider-era boundary around **8 July 2026** and unresolved v2 Madrid-local timestamp semantics. Verify the exact effective instant from existing evidence. Ambiguous/nonexistent daylight-saving timestamps are quarantined unless an offset is evidenced. Never interpret all local timestamps as UTC.

### 3.4 Required negative fixtures

The implementation must pass these deterministic tests before analysis:

| Fixture | Required result |
|---|---|
| Feature available at `decision_at + 1 second` | Excluded |
| Bar’s last trade precedes nominal bucket end | Unusable until nominal bucket end |
| Later provider revision carries earlier event timestamp | Earlier decision receives only original known vintage |
| Missing hour inside lag, rolling or target window | Feature/outcome abstention; no interpolation |
| Unknown candidate eligibility | Never NONE |
| Failed ENTRY attempt | Preserved as failed ENTRY, not NONE |
| DCA fill attached to existing parent | Never a new independent ENTRY |
| Post-entry `analisis_hora` or future DCA count inserted into design matrix | Hard failure |
| Approximately 15m sampled 4h state labeled native 15m | Hard failure |
| MARKET supplied in terminally unavailable frozen windows | Hard failure |
| Corrected timeline overwrites original bytes | Hard failure |
| Overlapping parent/target crosses train-test boundary | Purge or reject split |
| Source hash, row count or missingness mask drifts | Stop and create a new version |
| Round3 provider values appear in analysis inputs | `ROUND3_ANALYSIS_GATE_CLOSED` |

No such tests were executed here.

---

## 4. Prioritized executable experiments

### P0 — `MAEVE-M0-LABEL-PROVENANCE-001`

**Purpose:** Freeze source identity, original labels, clocks, missingness and lineage.

**Inputs:** Existing restricted recovery package only; no new acquisition.

**Calculations:**

- Enumerate every raw enum and its count, including unparsed/unmapped values.
- Reconcile parent/fill/action keys without assuming exits are fills.
- Reproduce the reported parent/fill counts and four missing IDs.
- Produce completeness by field, asset, era and source interval.
- Record timestamp meaning and evidence separately from timestamp presence.
- Repair the malformed timeline only in a new derivative.
- Inventory canceled, failed, unresolved and corrected records; report when their coverage is unknown.

**Acceptance:** Exact hashes and normalization lineage verified; discrepancies explicit; no unexplained collapsing or dropping.

**Failure:** `LABEL_OR_PROVENANCE_UNRESOLVED`. Descriptive package audit may continue; modeling stays blocked.

**Owner:** Existing MAEVE `EXT-ALPHA-0002`, standing owner #937, lifecycle #885.

---

### P0 — `MAEVE-M2-ELIGIBLE-DENOMINATOR-001`

**Purpose:** Establish the documented observable opportunity universe.

**Calculations:**

- Construct opportunity rows from original universe/schedule/status evidence.
- Enumerate counts for ELIGIBLE, INELIGIBLE and UNKNOWN by era and instrument.
- Preserve source outages, unavailable capital-state evidence and incomplete action logs.
- Reconcile each ENTRY to an opportunity or mark it unmatched.
- Produce the eligible NONE denominator before attaching future returns.

**Primary controls:** All verified eligible NONE opportunities.

**Frozen sampling sensitivity:**

- Retain every ENTRY.
- From verified NONE rows in each `(era, instrument, documented clock class, UTC calendar month)` stratum, select at most five per ENTRY using ascending SHA-256 of `(mission_id, opportunity_id)`.
- No price outcome, subsequent trade, future volatility or future episode label enters selection.
- Apply known inverse inclusion weights; evaluate calibration on the full eligible test population.

Strata with no ENTRY still remain in the full-universe timing evaluation; they are not silently removed.

**Falsifier:** An apparent ENTRY association that depends on convenient negative sampling, undocumented universe membership, or dropping source-missing periods is not an identified policy.

**Stop:** If only event-conditioned candidates are supportable, restrict the claim to contemporaneous selection. If neither is supportable, no ENTRY-versus-NONE model.

---

### P1 — `MAEVE-M1-COMMON-CLOCK-001`

**Purpose:** Measure incremental ENTRY explanation over frequency and simple price/volatility.

**Inputs:** Only admitted M0/M2 rows and time-valid features.

**Separate experiments:** Native 1h and native 4h features. No mechanical transfer of fitted parameters between resolutions.

**Primary estimator:** L2 logistic regression. Training-fold-only standardization. Regularization grid:

```text
C ∈ {0.01, 0.1, 1, 10}
```

Choose by inner chronological validation log loss; ties select stronger regularization. Conditional frequency tables precede fitting. No tree search, neural model or threshold sweep in V1.

**Primary contrast:** Blended versus price/volatility baseline, paired on identical eligible rows.

**Metrics:** Log loss and Brier score; PR-AUC and calibration as secondary diagnostics. Report action prevalence, abstention/coverage and class counts. AUC or accuracy alone is insufficient.

**Falsifiers:** Lift disappears under valid clocks, matched rows, negative-policy sensitivity, era separation or simple price controls.

---

### P1 — `MAEVE-M3-FAMILY-SEQUENCE-001`

**Purpose:** Identify whether observable families add information beyond level and price state.

Use the frozen family definitions below. No attribution to proprietary algorithms.

**Execution:** Deterministic feature construction first, then add-one and leave-one-family-out comparisons. Do not fit unavailable families with proxy inputs.

**Special limit:** The two selected 2025 event/control windows remain `LOW_POWER_DESCRIPTION / NOT_CONFIRMED`, even if row-level timestamps are repaired. Their many observations do not become many independent events.

---

### P2 — `TASK2-MAEVE-INDEPENDENT-FORECAST-001`

**Purpose:** Test transfer to independent Kompas forecasting, not MAEVE action agreement.

**Prerequisites:**

- A frozen, source-admitted primitive from the prior experiments;
- independent Task2 opportunities not selected by MAEVE actions;
- original forecast issuance and mature-outcome pairs;
- exact horizon/asset/target mapping;
- no parent, episode or target-window contamination from primitive selection.

**Comparators at the same issuance clock:**

1. Naive persistence;
2. Simple prior-return/drift;
3. Price/volatility/volume model;
4. Original Kompas forecast, when independently admissible;
5. The same baseline plus the frozen family.

Use the **existing target contract unchanged**. An original 12h target cannot be relabeled as 24h, and a newly generated retrospective forecast is not an original Kompas forecast.

**Metrics by target type:**

- Point forecasts: MAE relative to a predecision price denominator.
- Probability forecasts: Brier/log loss only where probabilities genuinely exist.
- Intervals: declared-coverage interval score/WIS, sharpness and coverage; compare equal-age and width-matched controls.

**Current status:** Not executable as confirmatory analysis from this packet. Historical source-clock failures remain failures.

**Original shadow owner:** Task2 #1596; CN-specific targets retain #1516/#1593.

---

### P2 — `TASK2-MAEVE-INDEPENDENT-WARNING-001`

**Purpose:** Test incremental downside information and false-warning burden.

A separate research endpoint may reuse S9’s existing definition:

\[
Y_d=1
\quad\text{if}\quad
\min(\text{low over next 72 completed hours})
\le 0.92\,P_d,
\]

where \(P_d\) is the last fully closed price at the documented decision clock.

This is a **research endpoint**, not a new live threshold or a 4/5 risk trigger.

**Comparators:** Same-clock prior drawdown, ATR/range, realized volatility and price trend; original typed warnings only when their original source/issuance joins are admitted.

**Required denominator:** Alerts, nonalerts, abstentions, failed issuances and unavailable sources.

**Metrics:** Brier score where probabilities exist; event-level recall, false-warning burden, warning lead time and missed-event rate. Thresholded warning comparisons use thresholds fixed by the existing contract or selected solely within training folds.

Overlapping daily 72h labels are not independent crises.

**Original shadow owners:** EDGE #1530 and Task2 #1596. Risk-to-Action #1553 owns any later economic interpretation.

---

### P3 — `MAEVE-DCA-EXIT-ECONOMICS-001`

**Purpose:** Prevent DCA rescue or exit conventions from masquerading as entry skill.

Separate analyses:

- First-entry forward return and adverse excursion;
- subsequent DCA probability, timing and added capital;
- realized parent outcome;
- EXIT/holding policy;
- capital reserve, concurrent exposure and opportunity cost.

Future DCA and exit fields may appear only as outcomes or as state already known at a later DCA/EXIT decision.

**Economic prerequisite:** Original available action clock, executable fills/quotes, fees, spread, slippage, funding/borrow where relevant, latency, reserve policy and capacity.

Without those inputs, report `ECONOMICS_UNKNOWN`, not after-cost alpha. Warning does not imply SELL, and the historical source fill is not a follower’s executable price.

---

## 5. Frozen model and family matrix

### 5.1 Common model arms

Let **F** contain frequency information only: asset, documented clock, time-of-day/day-of-week and evidenced era. Any category absent from training maps to an explicit unknown category.

| Arm | Included inputs |
|---|---|
| Frequency-only | F |
| Price/volatility | F + closed-price returns, realized volatility, ATR/range and volume |
| CFGI level-only | F + time-valid CFGI score |
| CFGI-only | F + admitted CFGI families; no external market features |
| Blended | F + price/volatility + admitted CFGI and market-state families |
| Add-one family | Price/volatility + one nominated test family |
| Leave-one-family-out | Blended minus exactly one family |

“CFGI-only” retains the common frequency nuisance controls; it excludes price and external-state predictors.

**Pairing rule:** Every contrast uses an identical row-ID set, target, clock, costs and missingness mask for both arms. For the full family matrix, use the common intersection. If that intersection is too small, retain separately declared paired-family cohorts, report their attrition, and do not rank their effects as though they used the same population.

Source absence is not zero. Missing-source indicators belong in a separate diagnostic arm, not a covert substitute for unavailable feature values.

### 5.2 Exact V1 transforms

Here \(k\) denotes a completed **native** interval, not a sampled snapshot.

| Family | Frozen construction |
|---|---|
| Price/volatility baseline | Log returns over 1, 3, 6 and 24 native bars; realized volatility over 6 and 24; ATR over 14; current closed-bar volume divided by prior-24-bar mean. Required history must be contiguous. |
| CFGI level | Current admissible score on its documented scale. No threshold inferred from entry-score medians or win rates. |
| Velocity | Score differences over 1, 3 and 6 native intervals. |
| Short sequences | Last four admissible native scores; signs of their three successive differences; same-sign run length capped at six. No outcome-selected pattern dictionary. |
| Percentile/range | Current score’s empirical percentile against the previous 168 native observations, excluding current; trailing range location. Constant-range case flagged explicitly. |
| Cross-timeframe | Latest available closed-native 1h–4h and 4h–1d score differences; source age retained. No future-containing resampling. |
| Market divergence | Asset score minus contemporaneously available MARKET score. BTC–ETH disagreement is a separately named feature, never a MARKET proxy. Terminal MARKET absence means this family is untestable there. |
| Nonprice residual | Only components with proven definitions/mapping. Regress them on F and price-state predictors within training folds; apply frozen residual transform to validation/test. Price-derived components cannot be declared nonprice merely by name. |
| ETF/spot | Documented released/settled flows and verified spot-flow measures, using publication availability rather than trade date. Do not backdate end-of-day totals. |
| Leverage | Original observable OI and funding quotes; realized settlement values only after settlement. No Round3 values. |
| ETHBTC/breadth | Closed ETHBTC relative returns; breadth on a contemporaneously documented universe. The current 35-symbol panel is not automatically a survivorship-free breadth universe. |

No native 15m or derived 2h extension is admitted in V1. Those require a separately justified, frozen experiment after 1h/4h results.

### 5.3 Negative controls

1. **One-native-candle lag:** Replace each tested family with its admissible value at \(d-\Delta\), retaining the same target at \(d\). This is not an execution-delay simulation.
2. **Family shuffle:** Shuffle entire feature-family blocks within compatible training era/asset strata, preserving internal component relationships.
3. **Outcome shuffle:** Shuffle complete outcome bundles between compatible nonoverlapping episode blocks in training; leave outer-test outcomes untouched.
4. **Clock corruption fixtures:** Future availability, early bar-close and later-revision cases must be rejected by the join, not merely produce poor scores.

Use **1,000** shuffle repetitions where the number of exchangeable blocks permits them. Otherwise label the negative control insufficient.

A lagged family retaining skill is not automatically a failure: persistent state may be informative. But it weakens any claim that immediate timing or rapid transitions are the mechanism. Shuffled pipelines repeatedly showing comparable lift trigger leakage/selection investigation, not promotion.

---

## 6. Evaluation, dependence, sample size and costs

### Chronological nested walk-forward

For each admitted era and native-resolution experiment:

1. Freeze calendar boundaries from the outcome-blind opportunity census.
2. Initial training uses the first 50% of the documented calendar span.
3. Five outer tests use successive 10% calendar spans.
4. Within each outer training span, use an expanding inner split: initial 60%, followed by three equal chronological validation spans.
5. Empty or insufficient folds remain failed/abstained folds; do not move boundaries to obtain a favorable sample.

No random train/test split.

### Purge and embargo

- Purge training targets overlapping validation/test targets.
- Minimum boundary embargo is the largest target horizon in that experiment—72h for the warning endpoint.
- Keep a parent position and all ENTRY/DCA/EXIT records in one fold.
- Purge overlapping parent-position episodes across boundaries, even when this requires more than 72h.
- Group shared market catalysts, source packets and overlapping BTC/ETH outcomes.
- Do not split a long connected parent episode merely to manufacture more independent observations.

Historical outcomes may be used for **purging and evaluation**, never for opportunity eligibility or feature selection.

### Uncertainty and multiplicity

- Report paired loss differences, not only separate arm scores.
- Use **10,000 episode-group bootstrap replicates**, with the same resampled groups for both arms.
- Freeze RNG seeds as the first eight bytes of SHA-256 of  
  `mission_id | experiment_id | operation`.
- Use Holm correction across all confirmatory family, resolution and target contrasts in the frozen trial register.
- Retain failed, abandoned, source-blocked and null experiments in that register.

Calendar-block uncertainty is a sensitivity analysis, not proof that those blocks are independent economic events. If event-family assignments are unverified, independent-event N remains unknown.

### Sample admission

Row counts, fills, snapshots and overlapping labels are not effective N.

Before confirmatory interpretation:

- Training must have at least 20 minority-class observations per fitted effective coefficient.
- Each claimed evaluation requires at least 50 independently justified episode groups and at least 20 positive and 20 negative groups for binary targets.
- Additionally require 80% power for the frozen minimum relevant paired loss reduction:
  - ENTRY log loss: **0.01 nats per decision**;
  - probabilistic forecast/warning Brier score: **0.01 absolute**.

These are design constants, not effects estimated from W46/W47.

Estimate paired group-level variance from training data only. A conservative planning requirement is:

\[
N_{\rm required}
=
\left\lceil
\frac{(z_{1-\alpha/(2K)}+z_{0.80})^2\,s_D^2}{\delta^2}
\right\rceil,
\]

where \(K\) is the frozen number of confirmatory contrasts. This is a planning approximation; dependence and rare-event simulation may require more data.

**If any requirement fails:** descriptive estimates may be reported with limitations, but the ruling is `INSUFFICIENT_N`, not “no effect” and not “validated edge.”

### Costs and net utility

For an eventual economic comparison, freeze one shared contract covering:

- order/observation clock and delay;
- venue/instrument;
- order size and capital reserve;
- fees, spread, slippage and impact;
- funding/borrow;
- fill failures and partial fills;
- exit/reentry policy;
- concurrency and exposure limits.

All arms use the same eligible decisions and cost model. Missing executable evidence cannot be replaced with indicative bar closes and then called realized utility. Illustrative friction stresses remain explicitly hypothetical.

---

## 7. Result artifacts and independent review gate

The authorized runner should produce these artifacts under the existing lifecycle—not create a new owner, scheduler or canonical store.

| Artifact | Required contents |
|---|---|
| `SOURCE_MANIFEST` | Exact paths, commits, bytes, SHA-256, schema/normalizer hashes, clock semantics and engine eras |
| `M0_LABEL_AUDIT` | Raw enums, mappings, missing IDs, unresolved records, corrections and completeness |
| `M2_OPPORTUNITY_AUDIT` | Universe evidence, eligible/ineligible/unknown counts, unmatched actions and NONE construction |
| `JOIN_AUDIT` | Included/excluded rows, reasons, feature ages, source absences, revision choices and unit-test results |
| `FOLD_MANIFEST` | Calendar boundaries, parent/event groups, purge/embargo exclusions and untouched holdout policy |
| `RESULTS` | Every arm/contrast, paired row-set hash, sample counts, effect, uncertainty, multiplicity and control results |
| `TRIAL_REGISTER` | All frozen, failed, abandoned, unavailable and completed specifications |

A result row must include at least:

```text
experiment_id, specification_hash, source_manifest_hash
eligible_rowset_hash, feature_matrix_hash, target_hash
era, native_resolution, target_horizon
N_attempts, N_eligible, N_UNKNOWN, N_abstain, N_censored
N_entries, N_NONE, N_parents, N_independent_episodes
source_missingness, complete_case_attrition
baseline, challenger, paired_effect, confidence_interval
adjusted_p_value, power_status
cost_contract_id, science_classification
```

Private values and restricted derivatives remain restricted. Public-safe outputs require boundary review; do not publish small-cell statistics that disclose restricted provider values.

### Transfer nomination gate

Only after independent reproduction of eligible result tables may **at most three** candidates be proposed. Each nomination must contain:

- exact primitive and original source/result hashes;
- null hypothesis;
- falsifier;
- paired effect size and multiplicity-adjusted uncertainty;
- required versus achieved independent sample;
- incremental information and, separately, net utility;
- source and maintenance cost;
- explicit kill criteria;
- original Task2 shadow owner.

Required kill criteria include time leakage, unidentifiable eligibility, failure against matched price controls, dependence on one era or negative policy, inadequate N, negative-control failure and—where utility is claimed—loss of advantage after realistic costs.

**No candidates pass this gate in the supplied packet.**

---

## 8. Holdouts, lifecycle and non-execution record

### Protected boundaries

- **W46:** exposed development evidence, not a clean confirmatory holdout. Do not derive this experiment’s thresholds from it.
- **W47:** untouched holdout remains under its existing freeze. Do not inspect, tune on, repurpose or rescore it for this mission.
- **Round3:** collection-only. No value reads, feature discovery, outcome linkage or informal scoring.
- **Master Monday:** may consume reviewed eligible findings only after its current contract repair is independently verified. That repair is not established here.
- **Prior one-shot calls:** no repeat, replay, new paid submission or budget inference from the supplied launcher.
- **Governance:** retain #937/#885 for MAEVE research and #1596/#1530/#1553 for Task2 transfer. No live model, rule, weighting, threshold, scheduler or portfolio change.

### What has not executed

This mission performed a textual review and specification only. It did **not**:

- read private ledger or CFGI rows;
- inspect public cold-raw archives or referenced artifacts;
- verify Git objects, archive bytes or checksums;
- reproduce prior reported statistics;
- enumerate original source enums;
- reconstruct eligibility or label any NONE row;
- join features, calculate sequences or fit models;
- run unit tests, backtests, permutations or uncertainty calculations;
- independently reproduce result tables;
- evaluate W46 or W47;
- nominate a transfer primitive;
- invoke the supplied script, call an API, modify a repository or change a workflow.

**Priority handoff:** verify original labels and clocks → establish the opportunity denominator → build the deterministic paired join → run simple 1h/4h comparisons and falsifiers → independently audit eligible results → only then consider independent Kompas transfer.

Until those steps produce admissible evidence, the answer remains **incremental explanatory and forecasting value unknown**, not zero and not demonstrated.