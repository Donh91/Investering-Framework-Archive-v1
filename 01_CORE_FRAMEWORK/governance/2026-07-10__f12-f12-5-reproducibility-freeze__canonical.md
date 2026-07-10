# F12 / F12.5 Reproducibility Freeze

**Dato:** 2026-07-10  
**Status:** CANONICAL_GOVERNANCE_CORRECTION  
**Område:** ETF-era default falsification / contested-state governance  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Depends on:** GPT-5.6 Fresh Eyes Audit Implementation; Rule and Evidence Registry  
**Supersedes:** operational use of any F12/F12.5 wording that relies on undefined terms such as `multiple`, `persistent`, `quickly`, `most conditions`, or an unspecified observation window

---

## Decision

```text
F12_ETF_DEFAULT_FALSIFICATION_STATUS: SPEC_INCOMPLETE
F12_5_CONTESTED_STATUS: SPEC_INCOMPLETE
OPERATIONAL_EVALUATION: SUSPENDED
CURRENT_OUTPUT_WHEN_REQUIRED_FIELDS_OR_SPEC_ARE_MISSING: NOT_EVALUABLE
```

The doctrine remains historically and conceptually relevant. It is not reproducible enough to control live state until the required specification is frozen.

No model may infer `DEFAULT`, `CONTESTED` or `FALSIFIED` from qualitative similarity alone.

---

## Required reproducibility packet

Before reactivation, the F12 specification must define all of the following:

```yaml
assumption_id:
assumption_text:
sequence_start_event:
observation_window_start:
observation_window_end:
required_axes:
minimum_required_axes_available:
axis_definitions:
axis_thresholds:
axis_persistence_rules:
BTC_D_measurement_window:
missing_data_treatment:
DEFAULT_entry_rule:
CONTESTED_entry_rule:
CONTESTED_exit_to_DEFAULT_rule:
CONTESTED_exit_to_FALSIFIED_rule:
FALSIFIED_entry_rule:
FALSIFIED_reversal_rule:
minimum_close_or_day_count:
source_hierarchy:
independent_reproduction_test:
```

Threshold provenance must be identified as one of:

```text
SOURCE_BACKED
HISTORICAL_REPLAY_DERIVED
FORWARD_TEST_CANDIDATE
FRAMEWORK_POLICY
DATA_MISSING
```

---

## State-machine safety

Until the exact packet exists:

```text
F12_STATE: NOT_EVALUABLE
F12_5_STATE: NOT_EVALUABLE
ETF_ERA_DEFAULT: MAY_REMAIN_AS_CONTEXT_ONLY
ETF_ERA_DEFAULT_AS_EXECUTION_OVERRIDE: FORBIDDEN
```

`CONTESTED` may not become a permanent ambiguity bucket.

Any future F12.5 reactivation must include explicit maximum review duration and mandatory exit to one of:

```text
RETURN_TO_DEFAULT
ADVANCE_TO_FALSIFIED
REMAIN_NOT_EVALUABLE_DUE_TO_DATA
```

---

## Required independent check

Before promotion, two independent runs using the same frozen input packet must return the same state.

```text
INDEPENDENT_REPRODUCIBILITY_REQUIRED: YES
AGREEMENT_STANDARD: EXACT_STATE_MATCH
DISAGREEMENT_RESULT: SPEC_FAIL
```

---

## Archive handling

Older F12/F12.5 sources remain historical governance context and must not be deleted.

Future archive work should:

1. locate the original source definitions;
2. cross-link them to this correction;
3. import only source-backed thresholds;
4. append a versioned reactivation specification;
5. preserve this freeze in the version chain.

No invented numeric threshold is authorized by this file.
