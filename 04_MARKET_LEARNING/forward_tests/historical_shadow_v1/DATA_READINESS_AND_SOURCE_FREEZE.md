# Data Readiness and Source Freeze

Status: `NOT_READY_FOR_ELIGIBLE_ROWS`
Authority: `RESEARCH_ONLY_NON_CANONICAL`

## Purpose

The Stage 2 review showed that historical failure came primarily from missing contemporaneous sensor-state provenance. This file prevents the prospective program from repeating that defect.

No prospective row may be marked eligible until every required field has an explicit owner, source identity, calculation rule and timestamp cutoff.

## PT-HS-001 readiness

| Field | Required | Current readiness | Freeze requirement |
|---|---|---|---|
| Stablecoin Alt Inflow 3D | YES | `SOURCE_MAPPING_REQUIRED` | Freeze universe, flow definition, 3D window, timestamp convention, owner/source version |
| Large-cap Alt Volume Share 3D | YES | `SOURCE_MAPPING_REQUIRED` | Freeze large-cap universe, denominator, volume source, 3D calculation and cutoff |
| ETH/BTC | YES | `OWNER_AVAILABLE_REQUIRES_BINDING` | Bind direct ETHBTC owner, settlement/cutoff and missing-data rule |
| BTC dominance | YES | `OWNER_AVAILABLE_REQUIRES_BINDING` | Bind exact BTC.D provider/denominator/version and cutoff |
| Breadth context | CONTROL | `OWNER_AVAILABLE_REQUIRES_BINDING` | Freeze membership universe/source version |
| Current-stack context | CONTROL | `AVAILABLE_REQUIRES_TIMESTAMP_BINDING` | Freeze exact contemporaneous output identity only |

PT-HS-001 may not start eligible sample accumulation while either distinctive input remains `SOURCE_MAPPING_REQUIRED`.

## PT-HS-002 readiness

PT-HS-002 inherits PT-HS-001 readiness and additionally requires:

| Field | Required | Current readiness | Freeze requirement |
|---|---|---|---|
| Brief ETH/BTC improvement | YES | `SEMANTIC_FREEZE_REQUIRED` | Define the observation/change window before first case |
| High BTC.D | YES | `SEMANTIC_FREEZE_REQUIRED` | Freeze exact recovered meaning/source without outcome tuning |
| Weak breadth | YES | `SEMANTIC_FREEZE_REQUIRED` | Freeze breadth state rule and membership universe |
| Failure/confirmation label | YES | `LABEL_FREEZE_REQUIRED` | Define prospectively before first eligible Type 3 case |

## Universal no-lookahead rules

- Source timestamps must be at or before `information_cutoff_utc`.
- Missing data stays missing.
- No interpolation or proxy substitution unless that exact method is preregistered before the first eligible row.
- Later source revisions must create a new source-version boundary, not silently rewrite old rows.
- Outcome data must be joined only after the observation row is immutable.
- The eight maturation horizons are fixed and all remain reportable.

## Activation gate

Change registry status from `PREREGISTERED_DATA_READINESS_PENDING` to `ACTIVE_PROSPECTIVE_CAPTURE` only after a machine-readable source-freeze receipt exists containing:

1. source/provider identity for every required field,
2. exact calculation formula/window,
3. timestamp and settlement convention,
4. missing/stale-data policy,
5. source-version identifiers,
6. deterministic test fixture proving no lookahead,
7. first eligible observation time strictly after the freeze commit.

Until then, zero eligible rows is the correct scientific result.
