# Historical Shadow Prospective Tests v1

Authority: `RESEARCH_ONLY_NON_CANONICAL`
Portfolio execution: forbidden
Automatic market-rule, threshold, weight or sensor-semantic changes: forbidden
Promotion from this package: forbidden

This package converts the independent Stage 2 verdicts into bounded prospective test contracts. It does not claim that any sensor works.

The only direct sensor identities admitted are:

- `PT-HS-001` — `EARLY_ROTATION_PRE_TRIGGER_V1_1`
- `PT-HS-002` — `FAKE_ROTATION_TYPE3_V2`

Method controls:

- CCE-style dependence mapping is mandatory.
- ODM-style fixed maturation uses the frozen horizons `6h, 12h, 24h, 48h, 72h, 7d, 14d, 30d`.

Core rule:

> A protocol is not a forward test until timestamped eligible rows exist.

Current state is intentionally `PREREGISTERED_DATA_READINESS_PENDING`. No historical data may be backfilled into prospective rows. The first eligible observation must occur after the exact source identities, calculation methods and timestamp cutoffs in `DATA_READINESS_AND_SOURCE_FREEZE.md` are frozen and available.

The archived Fake Rotation Type 3 `55-75%` failure-rate claim remains `NOT_REPRODUCED` and is not used as a prior, target or success criterion.
