# Failure policy

- Repeated failures with deterministic repair paths should be repaired by automation, not delegated to the user.
- Missing/stale source evidence remains degraded or unavailable.
- Pointer/hash mismatch fails closed.
- Missing pre/post-call receipts are never reconstructed after the call.
- Authentication/quota/rate-limit/token/budget failures are surfaced in DATA_HEALTH/BUDGET_HEALTH and may trigger operator attention.
- No failure state may be interpreted as bearish/bullish market evidence by itself.
