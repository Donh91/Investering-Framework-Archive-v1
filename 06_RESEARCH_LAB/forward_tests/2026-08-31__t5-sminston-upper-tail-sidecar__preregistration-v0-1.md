# T5 Sminston Upper-Tail Sidecar v0.1 - Preregistration

**Date:** 2026-08-31  
**Status:** DATA_BLOCKED_PREREGISTERED  
**Parent test:** `FNP_CUMULATIVE`  
**Related T2 repair:** `SMINSTON_BTC_CHALLENGER_V0_1`  
**Authority:** RESEARCH_ONLY / NO_TRIM_AUTHORITY

## 1. Purpose

Sminston's Decay / upper-tail work addresses a different error class from bottom permission.

T2 asks whether BTC can be permitted earlier than WAIT.

This T5 sidecar asks whether a frozen upper-tail metric can reduce missed BTC trim opportunity without causing premature trims.

The two questions must remain separate.

## 2. Candidate inputs

Target inputs:

- Decay Channel position / oscillator
- upper-tail quantile / decay relationship
- optional OLS residual context if exact point-in-time values become reproducible

At registration, exact decision-ready Decay values are not publicly available enough for an auditable forward action rule.

Therefore:

`STATUS = DATA_BLOCKED_PREREGISTERED`

## 3. No threshold invention rule

No trim threshold is defined in v0.1.

A threshold may be added only by a prospective amendment created before the first eligible outcome row, after exact source semantics and point-in-time values are available.

The amendment must freeze:

```text
source_metric
source_value_semantics
source_version
trigger_threshold
trim_fraction
benchmark_action
entry_reference_for_counterfactual
7D_horizon
30D_horizon
90D_horizon
premature_trim_cost
missed_trim_cost
reset_rule
```

A threshold discovered by optimizing historical peaks is prohibited.

## 4. Benchmark requirement

The benchmark must be the actual canonical BTC action at the same information cutoff.

The sidecar may not assume that `NO_TRIM` was the framework action unless a source-backed owner state proves it.

## 5. Valid divergence

A T5 sidecar row becomes evidence only if:

- source metric is frozen before the outcome,
- canonical action is frozen at the same cutoff,
- experimental trim action is frozen,
- the actions differ,
- horizons are frozen,
- no threshold or metric version changes after issuance.

## 6. Loss function

The sidecar must score both sides of the error:

- missed-trim cost when the benchmark holds through a material drawdown,
- premature-trim cost when the candidate trims and BTC subsequently continues higher.

Raw peak-call accuracy is insufficient.

## 7. Promotion and kill

There is no automatic promotion.

Promotion review requires repeated independent prospective divergences and positive net trim value after premature-trim cost and complexity.

Kill immediately if:

- exact source values cannot be frozen reliably,
- the source is revised in a way that cannot be audited point in time,
- a proxy is labelled as the original Decay metric,
- thresholds are fitted after observing outcomes.

Kill after sufficient eligible rows if the candidate does not improve the FNP loss function versus the canonical benchmark.

## 8. Current conclusion

The upper-tail thesis is research-relevant but not currently test-ready from public data.

Correct action:

`PRESERVE_AS_DATA_BLOCKED_SIDECAR`.

Incorrect actions:

- invent a Decay proxy and call it Sminston,
- backfit a top threshold,
- merge upper-tail logic into the T2 bottom-permission score.
