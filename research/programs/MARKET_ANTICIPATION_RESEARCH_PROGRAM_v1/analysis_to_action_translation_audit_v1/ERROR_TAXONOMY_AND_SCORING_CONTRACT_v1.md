# AATA Error Taxonomy and Scoring Contract v1

**Dato:** 2026-07-30  
**Status:** PREREGISTERED_RESEARCH_CONTRACT  
**Område:** analysis, price translation, action and timing decomposition  
**Depends on:** existing Forecast Ledger scorers, FNP opportunity-cost fields and Backtest Readiness Build

## 1. Non-blended rule

No composite AATA score is allowed.

The audit must preserve separate findings for:

```text
ANALYSIS
PRICE_TRANSLATION
ACTION_POLICY
TIMING
UTILITY
```

A strong range result may not erase a wrong regime or leadership call. A correct analysis may not erase a harmful action policy.

## 2. Error taxonomy

Use one or more labels only when supported by a valid owner outcome:

```text
ANALYSIS_STATE_ERROR
LEADERSHIP_ANALYSIS_ERROR
ROTATION_ANALYSIS_ERROR
PRICE_RANGE_TRANSLATION_ERROR
TRIGGER_TRANSLATION_ERROR
INVALIDATION_TRANSLATION_ERROR
ACTION_PERMISSION_ERROR
ACTION_PREMATURE_COST
ACTION_DELAY_COST
TIMING_ERROR
NO_MATERIAL_ERROR
MIXED_ERROR
DATA_LINEAGE_BLOCK
OUTCOME_NOT_MATURE
```

The taxonomy is descriptive. It creates no new weighted score.

## 3. Evaluation lanes

### Analysis

Allowed result:

```text
CORRECT
MIXED
WRONG
BLOCKED
```

Questions:

- Was the regime or transition call directionally correct?
- Was leadership correctly identified?
- Was rotation correctly distinguished from relative strength?
- Did the stated falsifiers correspond to the actual failure mechanism?

### Price translation

Use the existing owner range and state scorers only.

Evaluate separately by asset and horizon:

- 1-3 day
- 5-7 day
- weekly or longer only when explicitly frozen

Preserve continuation and invalidation performance separately from range containment.

### Action policy

Allowed classification:

```text
PROTECTIVE_VALUE
EXCESS_RESTRAINT
PREMATURE_RISK
NEUTRAL
BLOCKED
```

No classification is valid without a frozen action state and an eligible counterfactual benchmark.

### Timing

Allowed classification:

```text
EARLY
ON_TIME
LATE
NOT_APPLICABLE
BLOCKED
```

Timing must reference the frozen horizon and the first owner-verified confirmation or invalidation event.

### Utility

Use existing owner definitions only:

- MFE
- MAE
- maximum drawdown
- drawdown avoided
- missed upside
- opportunity cost
- false-permission cost
- time out of market
- deployment delay

## 4. Baselines

At economic-execution time, compare against the exact baseline available at forecast time:

```text
SOURCE_ANALYSIS_WITH_NO_ACTION
FRAMEWORK_FROZEN_ACTION
WAIT
FIRST_VALID_PERMISSION
SIMPLE_PRICE_TREND
```

Do not reconstruct a hindsight baseline.

## 5. False-positive and false-negative costs

False positive:

- declaring a translation error when the source never froze a concrete path;
- treating a blocked lineage row as economic evidence;
- penalising WAIT without a valid permission benchmark.

False negative:

- allowing a good range score to hide a wrong leadership call;
- allowing correct defensive analysis to hide excessive action delay;
- allowing a profitable action to conceal incorrect analysis.

## 6. Promotion and kill

Promotion requires at least:

```yaml
temporally_valid_rows: 12
distinct_regimes: 2
material_decision_divergences: 4
blind_replication: PASS
owner_defined_outcomes: COMPLETE
```

Kill or retain as descriptive-only when:

- no material decomposition divergence appears after 12 valid rows;
- labels are not independently reproducible;
- more than 25 percent of eligible rows remain ambiguous;
- existing Forecast Ledger and FNP outputs already explain all decision value;
- the audit increases documentation without changing measurable decisions.

## 7. Authority boundary

```text
NEW ACTIVE TEST: NO
NEW ENGINE: NO
NEW SCORE: NO
MARKET STATE CHANGE: NO
ROTATION CHANGE: NO
REBUY CHANGE: NO
PORTFOLIO ACTION: NO
```
