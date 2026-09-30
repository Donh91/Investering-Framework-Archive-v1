# GitHub Actions Budget Guard

- ACTIONS_BUDGET: **CRITICAL**
- USAGE_SNAPSHOT: 3000/3000
- SNAPSHOT_STATUS: FRESH
- RESET_ETA_DAYS: 1
- BURN_RISK: CRITICAL
- DEFERRED_CLASS_C: UNKNOWN
- PROTECTED_A_BLOCKED: YES

## Required behavior
- Reserve remaining capacity for protected Class A duties.
- Block/defer Class C work and run Class B only when materially necessary.
- Do not blind-rerun deterministic failures.
- Escalate if protected duties are blocked by the account hard stop.
