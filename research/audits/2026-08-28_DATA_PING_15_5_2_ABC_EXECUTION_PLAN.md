# DATA PING 15.5.2 - A/B/C Execution Plan

Status: ACTIVE IMPLEMENTATION PLAN
Date: 2026-08-28
Authority: current GitHub main; no market-rule or portfolio-execution changes authorized.

## Batch A - Truth Integrity
1. Pin baseline reads to one main commit SHA.
2. Resolve pointer -> target chains deterministically.
3. Detect pointer/root/cache conflicts fail-closed.
4. Separate retrieval/source/pointer/session freshness.
5. Validate ETF latest eligible settled-session lag.
6. Validate all numeric deltas against predecessor arithmetic.
7. Separate argument/response/normalized payload hashes.
8. Add incident fixtures from 2026-08-28 failures.
9. Require >=100 deterministic adversarial/property cases.
10. Preserve market thresholds and portfolio rules unchanged.

## Batch B - Owner Interface
1. Publish compact hourly directional summary.
2. Define canonical breadth owner/interface with versioned universes.
3. Publish durable commit/path/blob/payload provenance.
4. Publish lane-specific evidence roles.
5. Prefer fresh pinned owner macro evidence before direct FRED fallbacks.

## Batch C - Learning Closure
1. Native packet SHA / replay identity.
2. Immutable accepted-packet bridge.
3. Action Compass persistence hook without manual packet fabrication.
4. Bind forecast/outcome/calibration references to the same immutable accepted packet.
5. Portfolio execution remains forbidden.

Implementation will be split into isolated PRs A, B and C. Each layer is merged only after its relevant CI/readback checks pass.