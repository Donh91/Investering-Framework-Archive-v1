# P10 FINAL VERDICT

## Terminal verdict

`PROSPECTIVE_DUAL_RUN_REACTIVATED_BLINDED`

## Basis

The current GitHub repository was audited before implementation at authoritative HEAD `38942f22f715cd64291755cf2050642aa261749a`.

The legacy stop cause was `LEGACY_MANUAL_ONLY / WORKFLOW_NOT_WIRED`: v1 had been created and populated by direct ledger commits, while the scheduled prospective workflow only audited existing data and never materialized new paired rows.

The recovery implementation has now been merged through PR #338 as commit `904c61d3908efa6f1209c7286dda04bc06603fa3`.

The live collection path now:

- reuses the existing five-times-daily `Daily Live Anchor Capture` schedule;
- adds zero new market-data source calls and does not increase source cadence;
- creates same-T, same-capture-hash Full 32 and Reduced 18 child artifacts;
- excludes Legacy Minimal permanently from future collection;
- stores policy outputs only in profile child artifacts;
- stores only IDs, hashes, eligibility, missingness and health metadata in pair receipts;
- calculates coverage from fixed, non-overlapping 72h Unix-epoch windows;
- does not let the coverage monitor read profile policy outputs;
- invokes only the existing native rotation evaluator in its frozen fail-closed semantics;
- never synthesizes REBUY or TRIM outputs;
- leaves missing native policy outputs unavailable;
- leaves the Sequential Research Queue active-stage list unchanged;
- leaves all market rules, thresholds, weights and policy semantics unchanged;
- leaves v1 historical artifacts immutable.

All nine PR-triggered workflows passed before merge. The two direct recovery gates passed their dedicated regression suites and blinding assertions.

Gate 0-B2 was not run. Full-vs-Reduced agreement or divergence was not calculated. No Deep Research, new CFGI credits or paid OpenAI API calls were used.

At implementation-test time, prospective v2 evidence count was correctly zero because no historical v2 rows were manufactured and no manual live workflow was invoked. The collection path is active in the already-existing scheduler from the merged implementation onward.

## Future authorization boundary

No B2 analysis is authorized by this verdict. A future B2 run remains a separate task and may only be considered after the fixed-window coverage contract reaches its frozen readiness threshold and a separate authorization is issued.
