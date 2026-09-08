# Budget health semantics

Provider quota/rate-limit/token/budget exhaustion is operational evidence and must be surfaced when observable. It is never market evidence.

Until account-level spend/remaining-budget data is durably bound into GitHub, exact monthly spend is `UNKNOWN_EXACT_SPEND_NO_EXHAUSTION_SIGNAL` when no exhaustion signal is observed. The framework must not fabricate exact cost or remaining budget.
