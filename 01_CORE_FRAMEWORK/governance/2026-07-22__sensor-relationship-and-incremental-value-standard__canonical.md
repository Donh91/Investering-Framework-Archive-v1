# Sensor Relationship & Incremental Value Standard

**Dato:** 2026-07-22  
**Status:** CANONICAL  
**Område:** Framework governance, sensor promotion, simplification  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** New-engine freeze, Rows Before New Documents, Kill Criteria at Birth  
**Supersedes:** No existing engine or sensor rule

## Canonical decision

Sensor agreement is not automatically independent confirmation.

Future framework work must distinguish:

```text
CORRELATED
NONLINEARLY_DEPENDENT
REDUNDANT
UNIQUE
SYNERGISTIC
REGIME_DEPENDENT
UNSTABLE
DATA_BLOCKED
```

before assigning additional decision weight to a sensor or sensor pair.

## Why this rule exists

A closed-lab audit found that:

- many derived sensor proxies compressed into a smaller number of latent factors;
- low linear correlation could conceal strong nonlinear dependence;
- sensor combinations sometimes added value that neither input provided alone;
- apparent lead-lag relations changed across regimes;
- sequence duration contained information not present in the initial state label;
- change-point dates depended on the chosen sensor family;
- historical pattern similarity did not beat a simple baseline.

Therefore, counting aligned signals can create pseudo-confirmation.

## Mandatory relationship audit

Before a new sensor is promoted, or an existing sensor receives more independent weight, the following must be checked where data permits:

### 1. Linear dependence

At minimum:

- Pearson or equivalent linear dependence;
- rank-based dependence.

### 2. Nonlinear dependence

At least one nonlinear dependency test or transparent nonlinear diagnostic must be used when sample size permits.

Low Pearson or Spearman correlation must not be interpreted as independence.

### 3. Incremental value

The sensor must be tested against:

- a simple baseline;
- the existing sensor family;
- the existing state or meta-score.

The relevant question is:

```text
Does this sensor improve out-of-sample decision information
after existing information is already known?
```

### 4. Synergy and interaction

Sensor pairs may receive combined value only when the pair adds repeatable information beyond the stronger single sensor.

Agreement alone is insufficient.

### 5. Regime stability

Relationships must be inspected across:

- time windows;
- market regimes;
- volatility states;
- relevant framework states.

A global full-history coefficient is not sufficient evidence.

### 6. Structural-break sensitivity

Where practical, relationship claims must be checked for:

- change points;
- concept drift;
- coefficient instability.

A relationship that survives only in one historical segment must be labelled regime-dependent.

### 7. Sequence duration

For transition, recovery, rotation, stress and post-flush states:

```text
TIME_IN_STATE
```

is a first-class explanatory field.

A state label and a state of identical name at day 1 and day 10 must not automatically be treated as equivalent.

This rule does not create universal duration thresholds.

### 8. Complexity budget

A new sensor or mathematical layer must not be implemented when the same learning can be obtained through:

- an existing sensor;
- an existing factor;
- a simpler derived field;
- a periodic audit;
- an offline challenger.

## Change-point governance

Change-point and drift methods are approved only as:

```text
SHADOW_DIAGNOSTIC
SOURCE_QA
RELATIONSHIP_MONITOR
AUDIT_CHALLENGER
```

They have no standalone authority to:

- change canonical market state;
- change gates;
- unlock rebuy;
- trigger deployment;
- alter portfolio action.

Where used, consensus across independent sensor families is preferred over one global multivariate breakpoint.

## Pattern-analogue governance

Historical sequence similarity is not forecast evidence by itself.

Any analogue or matrix-profile method must beat:

- unconditional historical baseline;
- current-state persistence;
- a simple momentum/volatility baseline;

in a leakage-controlled expanding or walk-forward test.

Otherwise it remains descriptive only.

## Permanent simplification implication

When multiple sensors largely represent the same latent factor, the framework should prefer:

```text
ONE PRIMARY SENSOR
+
OPTIONAL VALIDATION SENSOR
+
AUDIT-ONLY SUPPORTING FIELDS
```

over equal-weight multi-sensor counting.

This is a simplification rule, not an automatic deletion rule.

No existing sensor is removed by this document.

## Promotion and kill criteria

A relationship method may be promoted only if it produces:

- valid rows;
- predeclared outcomes;
- out-of-sample improvement;
- stability or explicit regime conditioning;
- marginal value after complexity cost.

It must be rejected or retired if:

- it fails a simple baseline;
- its value disappears after controlling for existing sensors;
- it is unstable without a valid regime explanation;
- it creates signal-count inflation;
- it cannot produce reproducible rows.

## Current implementation status

```yaml
new_engine_created: false
runtime_changed: false
data_ping_contract_changed: false
market_state_changed: false
gates_changed: false
portfolio_action_changed: false
permanent_learning_added: true
```

## Core permanent learning

```text
Do not count sensors.
Measure what each sensor uniquely adds,
what it merely repeats,
what only emerges in combination,
and whether that relationship survives regime change.
```
