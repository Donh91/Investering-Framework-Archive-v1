# T06 - Incremental Value Attribution and Correlated-Signal Compression

**State:** FINDING_FROZEN
**Existing owner:** Sensor Relationship & Incremental Value Standard

## Current evidence

Canonical governance already defines the correct relationship classes:

`CORRELATED / NONLINEARLY_DEPENDENT / REDUNDANT / UNIQUE / SYNERGISTIC / REGIME_DEPENDENT / UNSTABLE / DATA_BLOCKED`.

It also establishes the permanent simplification preference:

`ONE PRIMARY SENSOR + OPTIONAL VALIDATION SENSOR + AUDIT-ONLY SUPPORTING FIELDS`.

The existing audit corpus contains historical relationship/survival work, while current forward-test governance requires valid rows, time-in-state, out-of-sample improvement and explicit delay/complexity cost before promotion.

What is missing operationally is a current compact relationship/compression readout that tells downstream agents which existing sensor families are presently:

- proven unique;
- likely redundant;
- data-blocked;
- still untested prospectively;
- regime-dependent;
- eligible only as validation/audit context.

Without that readout, agents can obey the written rule in principle yet still over-narrate several correlated measurements as several independent reasons.

## Frozen finding

`CURRENT_SENSOR_RELATIONSHIP_COMPRESSION_READOUT_MISSING`

The standard exists; the operational compression surface is incomplete.

## Required improvement

Build a deterministic research-only relationship summary from existing registered tests, relationship audit artifacts and eligible outcome rows. It must:

- preserve the canonical relationship vocabulary exactly;
- cite exact sensor family / pair / test IDs;
- distinguish historical evidence from prospective current evidence;
- show sample size and eligibility state;
- expose `PRIMARY / VALIDATION / AUDIT_ONLY / DATA_BLOCKED / UNRESOLVED` as presentation roles only, never market weights;
- flag when multiple reasons in the current evidence packet belong to the same known factor/family;
- fail closed when data are insufficient.

The output is designed to help Director, red-team and human review avoid double-counting. It does not change any live model.

## Acceptance

Positive: known duplicate/related family evidence is surfaced as such, with exact provenance and no additional conviction count.

Negative: low linear correlation cannot produce `UNIQUE`; historical closed-lab evidence cannot be presented as current prospective validation; no sensor is removed or reweighted automatically.

## Review cadence

Use the existing governance cadence: material regime shift, 20-30 new eligible rows where relevant, and quarterly simplification review. Weekly Master Monday should consume status/flags only, not rerun a full relationship lab.
