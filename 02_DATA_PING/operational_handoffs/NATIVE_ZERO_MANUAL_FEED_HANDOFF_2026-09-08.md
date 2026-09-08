# Native zero-manual-feed operating model

Date: 2026-09-08
Issue: #822

## User directive
Routine market data must no longer depend on manual chat feeding. If data can be acquired reproducibly by an admitted GitHub owner/API/source adapter, the machinery owns acquisition, validation, timestamps, provenance, predecessor continuity and archival.

User-facing readback aliases:
- `Kompas` / `Handlekompas`: concise current action context from latest verified native state.
- `Status`: state delta + machinery health.
- `Data Ping`: native GitHub readback/audit, not a request to paste data.
- `CN`: current Cycle Navigator authority package plus contextual native state; live context never rewrites frozen weekly state.
- `OTA`: latest Native OTA state; extra research only via adaptive gate or explicit request.

## Production chain
`sources -> unattended GitHub owners -> Hourly Sequence -> Entry Signal / pinned AUTO_MARKET_STATE_PACKET_v1 -> Native Handlekompas -> Cycle Navigator / OTA / learning readbacks`

Chat history is not the predecessor database. GitHub owns predecessor, deltas, provenance, freshness and degradation.

## Implemented and merged
- #826: native zero-manual-feed market state, Native Handlekompas and bounded native recovery.
- #827: CFGI provider-credit readback bound into Handlekompas without adding a provider call.
- #832: Native Handlekompas event-chained from successful Entry Signal Ledger completion; fixed :57 schedule remains watchdog fallback.
- #833: Entry Signal / Auto Market State event-chained from successful Hourly Sequence completion; fixed :50 schedule remains watchdog fallback.

## Verified production evidence as of 2026-09-09 01:21 Europe/Copenhagen
`04_MARKET_LEARNING/handlekompas/LATEST.json` exists on main and points to:
`04_MARKET_LEARNING/handlekompas/runs/2026/09/08/230115_a7667bcc2d4a.json`

Readback facts:
- Handlekompas SHA256: `a7667bcc2d4a5692a747b234a54a26aeb6249be4e8f761dbd0bcd69df6af71f4`
- source AUTO_MARKET_STATE packet SHA256: `7abf040ab0931c7d905ccd173ebb1939d5caf15395c8a0c3e37c850a49024404`
- pointer and packet source SHA bind exactly
- `manual_market_data_required=false`
- current Handlekompas: `HOLD_WAIT_DATA_DEGRADED`
- data health: `DEGRADED` because the bound source packet still had the pre-event-chain `hourly_market` blocker
- budget health: `PASS`
- CFGI credits remaining: `67819`; latest observed standard call cost `30`; provider receipt status PASS
- exact account-level monthly spend/remaining budget remains explicitly unavailable; do not infer it from CFGI credits.

This first Handlekompas materialization came from the :57 watchdog schedule, so it is NOT sufficient by itself to prove the new end-to-end event chain.

## Failure and budget policy
- Repeated deterministic operational failures are repaired by bounded automation where safe.
- Missing/stale/ambiguous data remains UNKNOWN/DEGRADED/UNAVAILABLE; no silent substitution.
- Pointer/hash mismatch fails closed.
- Missing pre/post-call receipts are never reconstructed post-hoc.
- Provider/auth/quota/rate-limit/token/budget exhaustion is operational health, never market evidence, and must be surfaced in Handlekompas and/or Master Monday.
- Automatic retries are suppressed when a provider is genuinely exhausted/auth-blocked/budget-blocked.
- Exact monthly spend remains UNKNOWN until an authoritative account-level cost ledger is bound.
- No autonomous portfolio execution, threshold mutation, owner switching, proxy promotion or history rewrite.

## Current P0/P1 verification gate
Do not close issue #822 until all are true:
1. at least three consecutive NATURAL post-#833 `Hourly Sequence -> Entry Signal/AUTO_MARKET_STATE -> Native Handlekompas` cycles complete successfully;
2. each Handlekompas source hash binds to the corresponding Auto Market State packet and remote readback succeeds;
3. `manual_input_residual_pct=0` and `manual_market_data_required=false` remain true;
4. no schedule-ordering defect leaves the downstream state bound to an older hourly owner when an event-chain run should have followed it;
5. provider/quota/token/budget states remain explicit and no user market-data fallback is introduced;
6. any fresh P0/P1 automation failure is reproduced and either repaired through normal governance or left explicitly blocked/degraded.

## Slow-cycle P0 note
The automation-health RED for `daily-slow-cycle-shadow.yml` was caused by an older run whose test hard-coded July 2026 as the latest World Bank Pink Sheet month after the source advanced to August. The test was already fixed on main by commit `92d5355f851d451e4cc6e72f65531d360a3023a7` (`Fix slow-cycle validation across monthly source publications`) and now validates arbitrary valid monthly advancement/year rollover. Do not create a duplicate patch; require a fresh natural/rerun production success to clear the stale health incident.

## Astra / Sol / Luna
Issue #829 was absorbed into draft PR #812; do not build a parallel model router. X-derived heuristics are eval criteria only, not facts. PR #812 remains draft until its four real blockers are closed: durable cross-run reservations, unified paid-gateway accounting, verified live Astra credential/model access, and actual Codex-host usage/quota/atomic dispatch integration. Do not falsely promote from unit tests.

## Overnight closure protocol
A temporary hourly overnight audit/repair loop is active while Master Monday is temporarily paused. Each run reads fresh main, reproduces defects before changing code, uses branch -> PR -> relevant CI -> merge -> exact readback, and should be silent on no-change iterations. Once the terminal gate above is satisfied, perform one final fresh-main/readback audit, close/update #822 with exact evidence, re-enable the normal Master Monday + CN automation, and stop the temporary overnight closure loop.
