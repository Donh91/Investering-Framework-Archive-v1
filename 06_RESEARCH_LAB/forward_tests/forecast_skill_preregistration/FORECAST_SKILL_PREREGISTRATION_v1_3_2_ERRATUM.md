# Forecast Skill Preregistration v1.3.2 — Pre-Activation Endpoint Erratum

**Date:** 2026-09-03  
**Status:** PRE_ACTIVATION_BINDING_ERRATUM  
**Parent:** `FORECAST_SKILL_PREREGISTRATION_v1_3_1`  
**Forecast skill:** `UNPROVEN`  
**Confirmatory study:** `NOT_STARTED_SCIENTIFIC_FIREWALL`

## Why this exists

Acceptance work against the actual v1.3 ZIP found one load-bearing prose/code mismatch before runtime activation. The sealed and verified v1.3 code in `simulation/src/engine.py` and `inference_bakeoff/candidates.py` does **not** use a row-weighted `mean(d_r)` as the final point estimate. It first groups admitted F1 rows by `OUTCOME_DUE_CALENDAR_DAY`, takes the arithmetic mean within each observed due day, and then gives each observed due day equal weight.

V1.3.1 incorrectly described the point estimate as `sum(d_r)/N`. That wording is withdrawn for the T13 confirmatory test. No T13 cohort has activated, no row has been admitted, and no prospective T13 outcome has been inspected. This is therefore a prospective correction binding production code to the already sealed-validated estimator, not a post-outcome method change.

## Binding endpoint

For each admitted F1 row:

```text
d_r = HIT_r - p_clim_r
```

For each UTC outcome-due calendar day `k`:

```text
a_k = mean(d_r for admitted rows due on k)
m_k = 1 if k has at least one admitted row, otherwise 0
```

The regular UTC calendar index retains empty days explicitly. Empty days occupy calendar-block footprint but contribute neither evidence nor zero.

The only confirmatory point estimate is:

```text
Theta_hat = sum(a_k * m_k) / sum(m_k)
```

Thus every **observed OUTCOME_DUE calendar day has equal weight**. Row-weighted `sum(d_r)/N` is forbidden as the confirmatory statistic.

## Binding batch-means inference

Tile the regular OUTCOME_DUE calendar series into non-overlapping 28-calendar-day blocks from the first outcome-due calendar position.

For block `g`:

```text
S_g = sum(a_k * m_k)
D_g = sum(m_k)
```

Blocks with `D_g = 0` remain part of the calendar tiling but are excluded from the variance sum. Let `G` be the number of blocks with `D_g > 0`.

```text
Theta_hat = sum(S_g) / sum(D_g)
Var(Theta_hat) = [G/(G-1)] * sum((S_g - Theta_hat*D_g)^2) / [sum(D_g)^2]
SE = sqrt(Var)
t = Theta_hat / SE
df = G - 1
reject H0 only if t > StudentT_0.975(df)
```

No resampling enters the confirmatory decision.

## Frozen source binding

This erratum is dictated by the v1.3 sealed implementation, particularly:

```text
inference_bakeoff/candidates.py SHA-256:
9524492ed5f128c9274902c2e73327bc60174d4da85ea1138658930752a67841

selected candidate:
B_CALENDAR_BATCH_MEANS_T

design point:
240 freeze/accrual calendar days, 28-calendar-day blocks
```

It preserves all other v1.3.1 corrections and gates, including the fixed 240-day freeze/accrual window and zero-tolerance confirmatory missingness rule.

## Firewall

```text
FORECAST SKILL = UNPROVEN
NO T13 ROW EXISTS YET
NO COHORT ACTIVATION RECEIPT EXISTS YET
NO OUTCOME WAS USED TO MAKE THIS CORRECTION
ROW-WEIGHTED CONFIRMATORY THETA IS FORBIDDEN
```

The effective T13 scientific contract is now `v1.3.1 + this v1.3.2 endpoint erratum` until a future prospectively validated successor explicitly supersedes it.
