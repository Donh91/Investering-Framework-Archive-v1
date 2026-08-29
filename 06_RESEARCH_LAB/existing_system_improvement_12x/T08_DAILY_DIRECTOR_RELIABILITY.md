# T08 - Daily Director Reliability and Deterministic Output Quality

**State:** IMPLEMENTATION_DEPENDENCY_BOUND
**Existing owner:** Daily Director Shadow / API Agent
**Existing remediation:** `codex-daily-director-directional-threshold-root-cause-v1`
**Current queue signature at audit:** `774d6478412574ae9461`

## Current evidence

Recent operational health identified Daily Director as stale and its latest semantic status as `API_OUTPUT_INVALID`. The governed Codex queue already contains an expedited bounded task whose objective is to reproduce and resolve the exact `directional_pct_threshold_required` failure without weakening forecast semantics or fabricating thresholds.

The Daily Director workflow already has:

- owner-bound multi-horizon context;
- explicit delta/freshness gates;
- bounded budget guards;
- deterministic skipped-output behavior;
- conflict-routing lane;
- current canonical Action Compass phase/warning language;
- explicit no-portfolio/no-canonical-state authority.

Creating another repair candidate would violate deduplication governance.

## Frozen program decision

`NO_DUPLICATE_CODEX_TASK_EXISTING_REMEDIATION_IS_OWNER`

This track therefore owns verification and reliability acceptance, not a parallel code fix.

## Required success criteria

The existing remediation is not considered complete for this 12x program until all of the following are true:

1. the exact parse/schema defect is reproduced and fixed within its allowed scope;
2. positive and negative contract tests pass;
3. one production-shape fixture passes without relaxing required forecast semantics;
4. at least one **natural** Daily Director run completes on fresh eligible owner evidence without `directional_pct_threshold_required` or another schema-invalid substitution;
5. output receipt/context hashes remain valid and no invalid output is silently converted to PASS;
6. architecture health no longer reports Director stale solely because production is unable to emit valid output.

## Reliability principle

A simpler valid output is preferable to a sophisticated invalid output, but required semantics must never be removed just to make parsing pass. `PHASE=UNCLEAR`, explicit missingness and empty forecast candidates are valid fail-closed outputs when evidence is insufficient; invented thresholds are not.

## No new intelligence work

Do not add model complexity, prompt sections, sensors or extra API calls under this track until production continuity is healthy.
