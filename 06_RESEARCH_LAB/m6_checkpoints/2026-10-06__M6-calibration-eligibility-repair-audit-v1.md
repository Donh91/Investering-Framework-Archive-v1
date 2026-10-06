# M6 calibration eligibility repair audit v1

Date: 2026-10-06
Status: P0_REPAIR_APPLIED / AWAITING_NEXT_AUTOMATED_REBUILD
Authority: RESEARCH_MEASUREMENT_ONLY / ZERO_LIVE_ACTION_AUTHORITY

## Finding
The prospective outcome chain was operational, but the downstream protection calibration gate had drifted behind the current Official Compass policy.

Observed before repair:
- Official Compass current decision policy: 2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0.
- Calibration accepted only policies matching the retired 2026-09-25 decision-integrity prefix.
- Latest calibration: 253 source outcomes, 0 eligible series rows.
- 46 outcomes excluded as PRE_DECISION_INTEGRITY_POLICY.
- Therefore ZERO eligible rows was partly an instrumentation/version-registration defect, not evidence absence alone.

A second semantic mismatch existed:
- Lane-C primary warning identity is pullback_risk_state in {ELEVATED,HIGH,CONFIRMED}.
- distribution_risk is not required to be non-UNKNOWN for that warning identity.
- Calibration rejected any row with distribution_risk=UNKNOWN, which could suppress a legally valid Lane-C pullback warning.

## Repair
scripts/learning/action_compass_exit_calibration.py now:
1. uses an explicit registered-policy allowlist rather than a loose historical prefix;
2. registers both:
   - 2026-09-25_DECISION_INTEGRITY_V3_2
   - 2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0
3. keeps unknown/unregistered future policies fail-closed;
4. requires pullback_risk_state to be assessable, but no longer requires distribution_risk to be known;
5. preserves MACHINE_PACKAGE projection provenance, data-quality, invalidation and immutable forecast/outcome binding gates.

Tests now include the current V4 policy with ELEVATED pullback and UNKNOWN distribution and require it to be eligible and counted as a warning.

## Why this is not gate loosening
The repair does not admit arbitrary newer policies.
It replaces a stale string-prefix gate with an explicit policy registry and aligns warning eligibility to the already frozen M6 Lane-C protocol.

No historical prose is backfilled.
No warning is created.
No threshold changes.
No SELL/TRIM mapping.
No portfolio execution.

## Automation audit
Verified:
- Official Daily Compass automatically freezes typed protection states.
- Official Compass Outcomes runs hourly and matures 12h/72h/168h outcomes from immutable freezes.
- Framework Learning Operations automatically rebuilds ACTION_COMPASS_PROTECTION_CALIBRATION_v2.
- Recent commit history proves both Compass outcome maturation and integrated learning workflows are actively persisting outputs.

Decision:
DO_NOT_BUILD_DUPLICATE_M6_COLLECTOR.

The existing chain is the correct owner path.

## Next evidence gate
On the next Framework Learning Operations rebuild:
- eligible_series_row_count should be recomputed under the registered V4 policy;
- BUILDING/NORMAL rows may become calibration controls but are not primary warnings;
- warning_series_row_count remains zero unless a matured ELEVATED/HIGH/CONFIRMED row actually exists;
- zero warnings after the repair is legitimate prospective evidence state, not an instrumentation conclusion.

If the rebuild still returns zero eligible rows, investigate the remaining explicit exclusion classes rather than weakening admission.

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
