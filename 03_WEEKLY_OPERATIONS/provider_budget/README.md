# Provider Budget Health

Operational-only provider credit observability. This lane never creates market evidence or portfolio authority.

Current owner: CFGI credit headers already returned by the existing Live Anchor CFGI request. `provider-budget-readback.yml` reads the completed Live Anchor Actions artifact and preserves only sanitized billing metadata (`credits_used`, `credits_remaining`, current standard-call expected credits). It makes **no additional CFGI/API call**.

States:
- `PASS`: provider reports enough credits for at least the current standard call cost.
- `LOW_INSUFFICIENT_FOR_NEXT_STANDARD_CALL`: remaining credits are below the latest standard-call expected cost.
- `EXHAUSTED`: provider reports zero remaining credits.
- `UNKNOWN_CREDIT_HEADER_ABSENT`: no credit header was available; never treat missing as zero.

Native Handlekompas consumes `LATEST.json` when present. Account-level monthly OpenAI/Work/Codex spend is a separate scope and must remain unknown unless a trustworthy account-level ledger is explicitly bound.
