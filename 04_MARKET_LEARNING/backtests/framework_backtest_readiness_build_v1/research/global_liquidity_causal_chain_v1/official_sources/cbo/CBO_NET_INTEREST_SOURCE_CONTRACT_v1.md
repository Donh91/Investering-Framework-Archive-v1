# CBO Net Interest Source Contract v1

**Dato:** 2026-07-29  
**Status:** `IMMUTABLE_POINTER_BOUND / BYTE_MATERIALIZATION_PENDING`  
**Program:** `GLOBAL_LIQUIDITY_CAUSAL_CHAIN_RESEARCH_v1`

## Purpose

Bind CBO's machine-readable fiscal projection vintages without treating the latest projection as historical real-time knowledge.

## Owner

```text
Congressional Budget Office
US-CBO/cbo-data
repository commit 284a95665f9f2f74ed1f482feb629b43fce323da
```

CBO describes the repository as machine-readable data for automated systems with standardized schemas and multiple vintages.

## Bound dataset

```yaml
dataset: ten_year_budget
publication_id: 51118
frequency: annual fiscal year
canonical_columns: [date, variable, value]
schema_blob: 8c9b7884ce88394a44d22df3643eef254b89a8d4
```

Primary variable:

```text
proj_outlays_net_interest
```

Unit:

```text
billions_of_dollars
```

Scale-normalized challenger:

```text
proj_outlays_net_interest_gdp_share
```

Required controls:

```text
proj_debt_held_by_public
proj_primary_deficit
```

## Bound vintages

| Vintage | Path | GitHub blob SHA | Status |
|---|---|---|---|
| 2024-06 | `data/budget/ten_year_budget/annual_fy_2024-06.csv` | `c71ef5986e1ccf6bdb4d993b6fcc141bfc3db9bc` | POINTER_BOUND |
| 2025-01 | `data/budget/ten_year_budget/annual_fy_2025-01.csv` | `999655e773307bd04b7ea07bd03b81f5d516fa7b` | POINTER_BOUND |
| 2026-02 | `data/budget/ten_year_budget/annual_fy_2026-02.csv` | `99f55b63bb8db8c214e2ee08de5ce0c216358fac` | POINTER_BOUND |

GitHub blob SHAs make the repository objects immutable references, but they do not replace the required SHA-256, row count and raw-byte receipt. Those remain pending materialization.

## Point-in-time rule

For any decision date `t`, use only a vintage published at or before `t`.

A later vintage may not revise earlier knowledge.

```text
eligible_vintage(t) = latest CBO release with release_timestamp <= t
```

Every projected fiscal year must retain both:

```text
vintage_date
projection_year
```

A projection row is not an observation of realized interest expense.

## Required normalization

Output long rows:

```text
vintage_date
publication_timestamp
fiscal_year
variable
value
unit
source_commit
source_blob_sha
source_sha256
knowledge_at
```

No interpolation between fiscal years.

No forward fill across vintages.

No use of the 2026 vintage to reconstruct what was believed in 2024 or 2025.

## Remaining work

1. materialize bytes for all three bound repository files;
2. calculate SHA-256 and row counts;
3. extract source publication timestamps;
4. reconcile earlier CBO website vintages under a separate mapping;
5. validate primary variables exist in each vintage;
6. build a deterministic vintage selector;
7. keep economic execution closed until G20.

## Authority boundary

```text
SOURCE POINTER BINDING: YES
POINT-IN-TIME ENGINEERING: YES
ECONOMIC TEST: NO
PARAMETER SEARCH: NO
FINAL HOLDOUT: SEALED
FRAMEWORK PROMOTION: NO
PORTFOLIO ACTION: NO
```
