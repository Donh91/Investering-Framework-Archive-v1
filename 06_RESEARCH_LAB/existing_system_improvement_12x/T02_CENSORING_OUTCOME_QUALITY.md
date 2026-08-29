# T02 - Censoring and Outcome Quality

**State:** FINDING_FROZEN
**Existing owner:** Task 4 outcome maturation / architecture evidence health

## Current evidence

Recent architecture health reports 226 adjudicated outcomes in its 14-day window, with 60 censored and a censor rate of about 26.5%.

The current maturation engine uses materially different censor classes, including:

- `LEGACY_V1_TARGET_UNIT_AMBIGUOUS` - deliberate quarantine of irreproducible legacy semantics;
- `NO_EVIDENCE_WITHIN_MAX_LAG` - evidence did not arrive within the frozen allowable lag;
- `METRIC_UNAVAILABLE` - selected evidence did not expose a valid numeric target path;
- `EVIDENCE_NAMESPACE_UNAVAILABLE` - evidence contract/namespace no longer carried the required family;
- `METRIC_PATH_ROOT_AMBIGUOUS` - fail-closed root ambiguity;
- `METRIC_PATH_ROOT_UNDECLARED` - forecast provenance cannot safely establish a root contract.

The health surface currently exposes aggregate censor count/rate but does not expose a reason distribution or a split between deliberate scientific quarantine and potentially remediable operational/specification censoring.

## Frozen finding

`OUTCOME_CENSOR_REASON_OBSERVABILITY_MISSING`

This is an observability/learning-quality defect. The censoring rules themselves are not presumed wrong.

## Required improvement

Add a deterministic read-only censor-quality summary derived from immutable `MATURED_OUTCOME_v3` rows that reports:

- total outcomes by status;
- censored count by exact reason;
- deliberate quarantine count/rate;
- data/evidence availability censor count/rate;
- resolver/provenance contract censor count/rate;
- unknown/new reason count without silently classifying it;
- recent-window and lifetime views where existing timestamps permit them;
- exact source root and generation timestamp.

The summary must not rewrite, un-censor, score or reinterpret historical rows.

## Initial classification policy

`LEGACY_V1_TARGET_UNIT_AMBIGUOUS` = `DELIBERATE_QUARANTINE`.

`NO_EVIDENCE_WITHIN_MAX_LAG`, `METRIC_UNAVAILABLE`, `EVIDENCE_NAMESPACE_UNAVAILABLE` = `EVIDENCE_AVAILABILITY_OR_CONTRACT`, requiring diagnosis but not automatic repair.

`METRIC_PATH_ROOT_AMBIGUOUS`, `METRIC_PATH_ROOT_UNDECLARED` = `PROVENANCE_OR_RESOLVER_CONTRACT`, requiring diagnosis but no retrospective root guessing.

Any unrecognized reason = `UNCLASSIFIED_FAIL_CLOSED`.

## Acceptance

Positive: the summary exactly reconciles to the immutable outcome files and the architecture aggregate count.

Negative: no outcome file is edited; no censored row becomes matured; no unknown reason is auto-mapped; no mutable `LATEST` file is used as outcome evidence.

## Learning gate

Only after the distribution exists may follow-up remediation target a specific avoidable reason. A high aggregate censor rate alone does not authorize changing maturation rules.
