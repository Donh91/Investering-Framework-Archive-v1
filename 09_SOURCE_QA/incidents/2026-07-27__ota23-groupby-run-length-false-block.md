# SOURCE_QA incident — OTA23 `groupby` run-length false block

```yaml
incident_id: SOURCE_QA_OTA23_GROUPBY_RUN_LENGTH_20260727
observed_at_utc: 2026-07-27T05:39:20Z
component: H7_CONDITION_1_RUN_LENGTH
severity: HIGH
failure_class: FALSE_BLOCK
caught_before_external_finalization: YES
canonical_harm_observed: NO
blast_radius: UNKNOWN_PENDING_CODE_SEARCH
status: OPEN_REPAIR_REQUIRED
```

## Defect

Buggy expression:

```python
runA = max(
    sum(1 for _ in g)
    for g in groupby(diffs, key=lambda x: x > 0)
    if g[0]
)
```

`itertools.groupby` yields `(key, group_iterator)`. The code iterated the outer tuple, which always has length two, instead of the grouped observations.

For the supplied signs:

```text
False, True, True, True
```

the buggy result was `2`; the correct longest positive run is `3`.

## Correct pattern

```python
from itertools import groupby


def longest_positive_run(values: list[float]) -> int:
    runs = (
        sum(1 for _ in group)
        for is_positive, group in groupby(values, key=lambda value: value > 0)
        if is_positive
    )
    return max(runs, default=0)
```

## Required regression cases

| Input sign pattern | Expected |
|---|---:|
| `[-]` | 0 |
| `[+]` | 1 |
| `[+, +]` | 2 |
| `[-, +, +, +]` | 3 |
| `[+, +, -, +]` | 2 |
| `[-, -, -]` | 0 |
| `[]` | 0 |

Also require an exact H7 fixture:

```yaml
log_diffs: [-0.01512, 0.00242, 0.00482, 0.02007]
expected_longest_positive_run: 3
```

## Governance treatment

The defect does not invalidate the H7 raw rows because the canonical condition can be evaluated by explicit pairwise comparisons:

```text
C3 > C2
C4 > C3
C5 > C4
```

All three comparisons pass in the supplied direct settled CEST series. The buggy helper is bypassed for the current adjudication.

## Required follow-up

1. patch the helper;
2. add the regression tests above;
3. search prior OTA and shadow outputs for the same code pattern;
4. identify any prior false blocking or false passing;
5. record repair receipt and affected-run list;
6. prohibit future use of the helper until the repair receipt passes.

```yaml
current_H7_adjudication_blocked_by_bug: NO
future_automated_H7_scoring_blocked_until_patch: YES
```
