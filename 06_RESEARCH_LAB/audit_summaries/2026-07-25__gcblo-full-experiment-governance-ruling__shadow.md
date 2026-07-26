# GCBLO Full Experiment Governance Ruling

**Dato:** 2026-07-25  
**Status:** SHADOW_ONLY / GOVERNANCE_RULING  
**Område:** external indicator admission / macro liquidity / sell and rebuy timing  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `08_SOURCE_MATERIAL/claude/`, `01_CORE_FRAMEWORK/governance/`, `06_RESEARCH_LAB/forward_tests/shared_evidence/`  
**Depends on:** PR #147, PR #148, GCBLO full experiment package, Sensor Relationship & Incremental Value Standard

## Executive verdict

```yaml
research_content_verdict: PARTIAL_ACCEPT_STRONG_NEGATIVE_LEARNING
package_reproducibility: PARTIAL_FAIL_CROSS_ENVIRONMENT
core_conclusion_stability: PASS
original_gcblo_recovered: NO
current_reentry_permission: NO
current_sell_permission: NO
rebuy_state_change: NO
market_state_change: NO
gate_change: NO
portfolio_action: NO
new_test: NO
new_engine: NO
```

The experiment substantially strengthens the negative case against using the visible GCBLO chart as a mechanical sell or re-entry trigger.

The strongest surviving learning is:

```text
The displayed indicator family may contain slow exit-risk context,
but the visible formula description does not reproduce the chart,
the re-entry side does not generalize,
and current state classification is specification-dependent.
```

The exact package is not yet accepted as a fully reproducible release because the packaged result files do not match an independent rerun from the packaged code and data. The broad verdict survives that mismatch.

## Independent rerun reconciliation

### Stable across package and independent rerun

```text
0 configurations pass the predeclared resemblance bar
best resemblance score remains 106.7 weeks
arctangent transformation changes no tested upper downcross dates, n=16
halving mask reduces 29 raw crossings to 7
unselected median strategy Sharpe remains approximately 0.58
approximately 9 percent beat the 40-week moving-average baseline
sell-side resemblance is materially better than re-entry resemblance
current-state dispersion remains severe
```

### Not exactly reproduced

```text
complete-signal configurations: 3,240 packaged versus 3,242 rerun
top-50 RE_FIRED: 18 percent packaged versus 16 percent rerun
multiple anchor-error medians moved slightly
packaged grid_all.csv hash differs from rerun hash
```

This is consistent with either an unpinned dependency effect or a code/result packaging mismatch. No dependency lock or reference-hash verifier was supplied.

## Interpretation of the main findings

### 1. Original-formula recovery failed

The frozen candidate family produced no configuration below the predeclared 45-week total anchor-error limit. A best score of 106.7 weeks is too poor to describe the original indicator as recovered.

Accepted wording:

```text
The original GCBLO implementation was not recovered inside the frozen candidate family.
```

Rejected wording:

```text
No possible GCBLO-like implementation can exist.
```

The experiment rejects the published recipe as a sufficient reproducible specification, not every possible hidden proprietary formula.

### 2. Exit and re-entry must be separated

The sell-side anchor errors are materially smaller than the 2019 and 2022 re-entry errors. The source's own re-entry dates also generated poor 26-week outcomes in two of three completed episodes, with large adverse excursions.

Durable learning:

```text
Any surviving research value belongs to slow exit-risk or bear-avoidance context.
It does not establish top precision and does not establish executable re-entry.
```

### 3. Arctangent is presentation, not edge

The tested raw-composite and arctangent-transformed upper downcross dates are identical. The nonlinear transform changes the displayed scale and compression but not crossing order when thresholds are mapped monotonically.

Therefore values such as `+86` and `-80` receive no independent evidentiary weight.

### 4. Halving conditioning creates most of the clean historical picture

The halving-conditioned state machine removes approximately 76 percent of raw crossings.

The clean four-cycle visual is therefore materially produced by a selection rule. This does not make the rule invalid, but it means the oscillator itself cannot claim the full historical precision shown by the annotated chart.

### 5. Current re-entry classification fails specification survival

Among the best-fitting configurations, only a minority classify the current state as `RE_FIRED`, most have not completed the required stay-out sequence, and the current oscillator range spans negative and positive extremes.

Therefore:

```text
CURRENT GCBLO RE-ENTRY: NOT ROBUST
CURRENT FRAMEWORK CLASSIFICATION: WATCH ONLY
REBUY: REMAINS LOCKED
```

### 6. Unselected performance does not beat simple baselines

The full unselected family has median Sharpe below buy-and-hold, and only about 9 percent of specifications beat a macro-free 40-week moving-average rule.

The high Sharpe of the chart-anchor steelman and best-resemblance configuration is not family-level evidence. It is heavily conditioned on historical annotations or full-sample resemblance selection.

### 7. Form driver and edge driver differ

Global central-bank and BOJ/FX components improve chart resemblance, while the simpler US-only family reportedly carries more predictive quality.

This is evidence that:

```text
visual resemblance is not incremental decision value
```

It also makes FX translation a mandatory decomposition field in future multi-currency liquidity work.

### 8. October 2025 claim requires live-versus-settled separation

A settled weekly cross cannot be known before the weekly bar and required component releases exist. The October 7 screenshot showed the oscillator above the stated threshold and described it as nearing the level.

Therefore the later wording that the indicator had already shown the regime change one day after the high is retained as a taxonomy conflict:

```text
LIVE_OBSERVATION != SETTLED_SIGNAL
```

The finding does not prove deliberate hindsight. It proves that the later claim is stronger than the contemporaneous settled evidence supports.

## Governance decisions

## Decision 1 - EXT-GCBLO-2026-07-24 ledger row

```yaml
decision: ACCEPT_AS_FROZEN_SOURCE_ROW
owner: FNP_CUMULATIVE
row_type: SOURCE_CLAIM_DECISION_DIVERGENCE
primary_horizon: 13W_FROM_SOURCE_DATE
maturity_end_date: 2026-10-23
safe_evaluation_not_before: 2026-10-24T00:00:00Z
framework_observed_at_utc: 2026-07-25T13:03:46Z
row_status: FROZEN_SOURCE
outcome_status: PENDING_MATURITY
execution_authority: ZERO
```

Reason:

The external source said re-entry while the framework remained `WAIT / REBUY_LOCKED`. This is a genuine prospective decision divergence suitable for T5 opportunity-cost analysis.

The row is not a framework forecast and does not validate GCBLO. It records the cost of ignoring versus following the external claim.

Required matured fields:

```text
13-week end return
MFE
MAE
maximum drawdown
new low after claim
missed upside under WAIT
drawdown cost of immediate entry
price-confirmation date
liquidity/transmission-confirmation date
```

## Decision 2 - R2 exit-only and R1 FX decomposition

### R2 exit-only

```yaml
decision: RETAIN_AS_SHADOW_RESEARCH_TARGET
sensor_promotion: NO
new_test: NO
existing_owner_routing: [PULLBACK_EDGE_20260708_01_OUTCOMES, FNP_CUMULATIVE]
```

The indicator is not promoted. The only admissible future target is whether an upper-state deterioration reduces drawdown at acceptable missed-upside cost.

Future rows must measure:

```text
drawdown avoided
upside foregone
false-exit cost
time out of market
re-entry delay
utility versus hold
utility versus simple price-trend exit
```

No claim of exact top timing is allowed.

### R1 FX decomposition

```yaml
decision: PROMOTE_AS_MANDATORY_SOURCE_QA_AND_RELATIONSHIP_FIELD
prediction_weight: ZERO
```

Every multi-currency central-bank or global-liquidity composite must separate:

```text
native-currency component change
FX translation contribution
USD-converted component change
share of total composite movement caused by FX
sign change with and without FX translation
```

This is a reproducibility and attribution rule, not a market signal.

## Decision 3 - R3 saturation and R4 dispersion admission gates

### R3

A blanket ban on saturated indicators is too broad. Saturation can be useful for coarse regime classification.

Ratified rule:

```text
A heavily bounded or saturated indicator may be admitted as regime context,
but it may not claim precise timing unless the unbounded/raw score and
reasonable threshold perturbations preserve the timing result and beat simple baselines.
```

This is named:

```text
SATURATION_TIMING_RESTRICTION
```

### R4

Ratified as a hard admission gate:

```text
SPECIFICATION_DISPERSION_GATE
```

A sensor receives no live decision weight when equivalently plausible, outcome-independent specifications disagree materially on:

```text
sign
state
crossing date
action class
```

The equivalence set, agreement metric and tolerance must be frozen before outcome scoring.

The current GCBLO family fails this gate by a wide margin.

## Decision 4 - PBoC source

```yaml
primary_source: CHINA_NSDP_CENTRAL_BANK_SURVEY
publisher: NATIONAL_BUREAU_OF_STATISTICS_OF_CHINA
underlying_data_owner: PEOPLES_BANK_OF_CHINA
frequency: MONTHLY
native_unit: 100_MILLION_CNY
current_role: OFFICIAL_PRIMARY_SOURCE
historical_backfill_status: DATA_BLOCKED_PENDING_MANUAL_INGEST
```

Use the official monthly Central Bank Survey / Monetary Authority balance-sheet components in native CNY with:

```text
observation month
publication date and timestamp
retrieval timestamp
source URL
raw table hash
revision status
asset-side component sum
total-assets reconciliation difference
```

Do not use annual central-bank-assets-to-GDP series as the model input.

The China Statistical Yearbook may be used only as an annual reconciliation check. IMF or BIS series may be used as secondary source-QA challengers, not as silent substitutes for the PBoC/NBS monthly primary series.

Until the historical monthly backfill and release calendar are captured, PBoC remains `DATA_BLOCKED` and must not be forward-filled into a historical test.

## Promotion and kill boundaries

```text
GCBLO SENSOR WEIGHT: ZERO
GCBLO RE-ENTRY TRIGGER: REJECTED
GCBLO EXACT TOP-TIMING CLAIM: REJECTED
EXIT-RISK RESEARCH TARGET: RETAINED SHADOW-ONLY
FX DECOMPOSITION: MANDATORY QA
SATURATION TIMING RESTRICTION: RATIFIED GOVERNANCE
SPECIFICATION DISPERSION GATE: RATIFIED GOVERNANCE
PBOC LANE: DATA_BLOCKED UNTIL OFFICIAL MONTHLY BACKFILL
```

## Required package repair

The research package needs a narrow reproducibility patch, not another broad experiment.

Required corrections:

```text
pin Python, pandas and NumPy versions
add requirements lock and environment manifest
regenerate all results from final packaged code/data
add frozen reference hashes
add executable verifier
reconcile 4,800 versus 6,000 theoretical grid count
reconcile 3,240 versus 3,242 complete-signal configurations
reconcile 18 versus 16 percent top-50 RE_FIRED
fix Kraken receipt row count
prove or explicitly bound cross-environment parity
```

Exact release parity remains pending this patch. The governance decisions above rely only on findings that survived both the packaged and independent rerun outputs.

## Authority boundary

```text
SOURCE ARCHIVE: YES
PROSPECTIVE SOURCE ROW: YES
MATURED OUTCOME: NO
CANONICAL GOVERNANCE SAFEGUARDS: YES
NEW ACTIVE TEST: NO
NEW ENGINE: NO
GCBLO SENSOR PROMOTION: NO
CURRENT MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
DEPLOYMENT CHANGE: NO
PORTFOLIO ACTION: NO
```
