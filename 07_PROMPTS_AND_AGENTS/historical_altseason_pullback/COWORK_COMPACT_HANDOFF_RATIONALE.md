# Compact Cowork Handoff Rationale

The handoff ZIP intentionally contains instructions, research protocols, readiness/billing snapshots and immutable artifact pointers only.

Cowork is expected to read `Donh91/Investering-Framework-Archive-v1` directly on `main` for authoritative research data, code and prospective evidence. This avoids duplicating GitHub into the ZIP and prevents a stale handoff copy from silently competing with the repository source of truth.

Large historical bulk is referenced by the SHA-256-bound `FREE_BULK_ARTIFACT_POINTER.json` and must be fetched from the exact bound GitHub Actions run. The ZIP must never embed a reconstructed substitute.

This delivery-model change does not alter research labels, episode semantics, CFGI semantics, market rules, thresholds, weights, portfolio authority or the `FORWARD_TEST` promotion ceiling.
