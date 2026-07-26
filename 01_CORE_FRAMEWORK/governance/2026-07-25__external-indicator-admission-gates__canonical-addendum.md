# External Indicator Admission Gates

**Dato:** 2026-07-25  
**Status:** CANONICAL_ADDENDUM  
**Område:** external sensor admission / reproducibility / relationship governance  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `08_SOURCE_MATERIAL/`  
**Depends on:** `2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md`  
**Supersedes:** none

## Purpose

This addendum repairs the existing Sensor Relationship & Incremental Value Standard for external bounded indicators, multi-currency liquidity composites and visually calibrated chart signals.

It creates no new test, engine, layer, score, market state, gate, rebuy permission or portfolio authority.

## 1. External formula and source recovery gate

Before an external indicator receives decision weight, preserve where available:

```text
executable formula or source code
exact source series and identifiers
units and currencies
observation frequency
release timestamp and lag
historical-vintage policy
resampling and forward-fill rules
lookbacks, weights and smoothing
threshold derivation
machine-readable historical signal log
```

When exact recovery is impossible, all reconstructed outputs must be labelled:

```text
RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_<INDICATOR>
```

Visual similarity is not original-formula recovery.

## 2. Cosmetic monotonic-transform rule

A monotonic transform such as arctangent, logistic compression or rescaling receives no independent evidentiary weight when it preserves ordering and mapped crossing dates.

Required comparison:

```text
raw or unbounded score
transformed score
mapped thresholds
crossing-date equality
ranking equality
```

A memorable transformed level is not an economic threshold unless it survives source recovery, perturbation and out-of-sample testing.

## 3. Saturation timing restriction

A highly bounded or saturated indicator may remain useful as coarse regime context.

It may not be promoted for precise timing when it spends a material share of observations near its bounds unless all of the following hold:

```text
raw or unbounded score is available
timing survives reasonable threshold perturbation
timing survives smoothing and lookback perturbation
crossing dates remain stable under real-time vintages
the result beats simple timing baselines out of sample
false-positive and false-negative costs are acceptable
```

Classification:

```text
SATURATED_REGIME_CONTEXT
```

is allowed.

Classification:

```text
PRECISE_TIMING_SIGNAL
```

is forbidden until the timing conditions above pass.

## 4. Specification dispersion gate

Before any external indicator receives live decision weight, define an outcome-independent equivalence set of plausible specifications.

The equivalence set must be selected through source fidelity, formula uncertainty, reconstruction quality or other pre-outcome criteria. It may not be selected by future market performance.

Measure dispersion across the equivalence set for:

```text
sign
state
crossing date
action class
threshold status
```

The equivalence-set definition, agreement measure and tolerance must be frozen before outcome scoring.

Hard rule:

```text
When equivalently plausible specifications disagree materially on sign,
state or action class, the indicator receives zero live decision weight.
```

Allowed status:

```text
SPECIFICATION_DISPERSION_FAIL
```

The indicator may remain an offline challenger or descriptive source.

## 5. Multi-currency FX decomposition

Every multi-currency central-bank or global-liquidity composite must preserve separately:

```text
native-currency component level
native-currency component change
FX rate and convention
FX translation contribution
USD-converted component level
USD-converted component change
share of composite change caused by FX
sign with FX translation
sign without FX translation
```

Mandatory questions:

```text
Does FX improve source resemblance?
Does FX improve out-of-sample decision value?
Does FX change sign or state?
Is the resemblance driver also the edge driver?
```

A model where FX drives visual resemblance but not predictive value must be labelled:

```text
FORM_DRIVER_NOT_EDGE_DRIVER
```

FX decomposition is source QA and relationship attribution. It is not a standalone sensor.

## 6. Mask and conditioning attribution

When halving, cycle, regime or calendar masks remove candidate signals, report:

```text
raw signal count
masked signal count
share removed
false-positive count before and after masking
independent episodes before and after masking
```

The final clean chart may not attribute all apparent precision to the oscillator when a mask performs most of the signal selection.

## 7. Live versus settled taxonomy

Every external signal must distinguish:

```text
LIVE_INTRAPERIOD_OBSERVATION
PRELIMINARY_RELEASE
SETTLED_PERIOD_SIGNAL
REVISED_HISTORICAL_SIGNAL
```

A later settled or revised crossing may not be backdated to the first live observation.

If the contemporaneous source said `nearing`, a later report may not silently describe that timestamp as an already settled crossing.

## 8. Decision-target separation

External sell and re-entry claims must be tested separately.

### Exit-risk target

Measure:

```text
drawdown avoided
upside foregone
false-exit cost
time out of market
re-entry delay
utility versus hold
utility versus simple price-trend exit
```

### Re-entry target

Measure:

```text
end return
MFE
MAE
maximum drawdown
false-entry cost
missed upside under WAIT
opportunity cost
time to price confirmation
time to final low
```

A sensor may survive as exit-risk context while failing as re-entry timing. One side may not borrow credibility from the other.

## 9. Baseline and incremental-value requirement

External indicators must compete against:

```text
buy and hold or WAIT, as appropriate
simple price trend
simple single-source liquidity proxy
existing framework macro state
existing framework macro plus price and flow confirmation
```

A chart resemblance score is not a performance baseline.

Selection on annotated historical dates is not an out-of-sample result.

## 10. Promotion and kill criteria

An external indicator may receive additional framework weight only when it has:

```text
reproducible source and method lineage
valid prospective or leakage-controlled rows
stable specification state
real-time-vintage survival
simple-baseline outperformance
incremental value after existing sensors
acceptable delay and opportunity cost
```

Reject or retain as audit-only when:

```text
formula cannot be reproduced
state depends on plausible specification choice
value is created mainly by a retrospective mask
revised data moves historical crossings
visual resemblance and predictive value come from different components
simple price or liquidity baselines are superior
```

## 11. Current GCBLO classification

The 2026-07-25 GCBLO experiment is the first implementation example for these gates.

```yaml
original_formula_recovered: false
saturation_timing_restriction: FAIL_FOR_PRECISE_TIMING
specification_dispersion_gate: FAIL
fx_decomposition_required: true
live_vs_settled_conflict: present
exit_risk_research: SHADOW_ONLY
reentry_trigger: REJECTED
current_framework_weight: ZERO
```

This example does not create a permanent GCBLO sensor.

## Authority boundary

```text
NEW TEST: NO
NEW ENGINE: NO
NEW SENSOR WEIGHT: NO
DATA PING CONTRACT CHANGE: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
PORTFOLIO ACTION: NO
```
