# Native zero-manual-feed operating model

Date: 2026-09-08
Issue: #822
Implementation branch: `feat/native-zero-manual-feed-v2-20260908`
Supersedes the exploratory draft branch/PR created earlier in the same session; continue this clean branch/PR for production graduation.

## User directive
Routine market data must no longer depend on manual chat feeding. If data can be acquired reproducibly by an admitted GitHub owner/API/source adapter, the machinery owns acquisition, validation, timestamps, provenance, predecessor continuity and archival.

User-facing readback aliases:
- `Kompas` / `Handlekompas`: concise current action context from latest verified native state.
- `Status`: state delta + machinery health.
- `Data Ping`: native GitHub readback/audit, not a request to paste data.
- `CN`: current Cycle Navigator authority package plus contextual native state; live context never rewrites frozen weekly state.
- `OTA`: latest Native OTA state; extra research only via adaptive gate or explicit request.

## Required chain
sources -> unattended GitHub owners -> pinned AUTO_MARKET_STATE_PACKET_v1 -> Native Handlekompas -> Entry Signal / Cycle Navigator / OTA / learning

Chat history is not the predecessor database. GitHub owns predecessor, deltas, provenance, freshness and degradation.

## Failure and budget policy
- Repeated deterministic operational failures are repaired by bounded automation where safe.
- Missing/stale/ambiguous data remains UNKNOWN/DEGRADED/UNAVAILABLE; no silent substitution.
- Pointer/hash mismatch fails closed.
- Missing pre/post-call receipts are never reconstructed post-hoc.
- Provider/auth/quota/rate-limit/token/budget exhaustion is operational health, never market evidence, and must be surfaced in Handlekompas and eligible weekly operations/Master Monday context.
- CFGI failures are classified where evidence permits; quota/auth/token problems suppress wasteful retries.
- Exact monthly spend is never fabricated when an account-level cost ledger is unavailable.
- No autonomous portfolio execution, threshold mutation, owner substitution, or historical rewrite.

## Graduation
Production promotion requires focused tests/CI PASS, merge to main, exact main readback and verified continued operation. Manual Custom-GPT Data Ping remains diagnostic/fallback only.
