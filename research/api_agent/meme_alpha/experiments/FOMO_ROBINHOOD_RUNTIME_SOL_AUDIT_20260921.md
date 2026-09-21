# FOMO Robinhood Runtime - Sol High Independent Audit v1

Date: 2026-09-21
Status: HOLD_ACTIVATION / CODE_REVIEW_REQUIRED
Owner: #1087 / #1134
Authority: SHADOW_RESEARCH_ONLY
Reviewed code:
- scripts/api_agent/meme_alpha_fomo_robinhood_observer.py
- scripts/api_agent/meme_alpha_fomo_robinhood_convergence.py
Normative contracts:
- FOMO_ROBINHOOD_FORWARD_EVIDENCE_HARDENING_v1
- FOMO_ROBINHOOD_PROSPECTIVE_OBSERVER_PACKET_v1

## Verdict

Do not wire the current convergence code into a live/scheduled observation path yet. The research design remains useful, but the current code does not fully implement its fail-closed promotion gate.

## Material findings

### F1 - independence state is recorded but not enforced
The observer emits `independence_state`, but `eligible_receipt()` never requires `CONFIRMED` or an equivalent frozen pass state. A receipt can therefore become convergence-eligible while its explicit independence state is still PENDING.

Required fix: eligibility must require the contract-defined confirmed independence state, not merely a non-empty economic_entity_id.

### F2 - source health is not enforced
Hardening requires source health and exact lineage. The observer stores `source_health`, but convergence eligibility ignores it.

Required fix: define the accepted source-health pass vocabulary from the existing owner and fail closed on UNKNOWN/DEGRADED/error states. Do not invent a new market/source-health semantic.

### F3 - market-data health is under-specified in code
The hardening gate explicitly requires `market_data_health=true`. Observer classification currently treats non-null liquidity as sufficient market-health evidence. This is weaker than the frozen contract.

Required fix: consume an explicit existing market-data-health result or remain MARKET_HEALTH_PENDING. Non-null liquidity alone must not prove health.

### F4 - exact source lineage is not required for convergence
The observer can produce PROVENANCE_PASS without requiring a source transaction/log locator or exact source event timestamp. Hardening requires exact timestamp lineage for promotion eligibility.

Required fix: promotion/convergence eligibility must require exact comparable event/observation lineage and the required source locator/evidence refs. UNKNOWN may be retained but not counted.

### F5 - batch replay can re-increment the same convergence
The convergence ID is deterministic, which is good, but the batch function reports `promotion_counter_increment = len(events)` without checking an existing append-only convergence ledger/set. Reprocessing the same batch can therefore present the same deterministic event as a fresh increment to a caller.

Required fix: counter increments must be based on first-seen convergence IDs against the existing prospective evidence owner, or the function must emit events only and leave counter mutation to the idempotent owner. Prefer the latter if an existing owner already controls counters.

### F6 - one event per token per batch hides window semantics
The algorithm loops each possible start but breaks after the first qualifying convergence. This may be acceptable for a token-level first-convergence experiment, but the preregistration uses 15/30/60/180m windows. Current default 60m output does not prove all frozen windows are evaluated consistently.

Required fix: read the preregistered windows from the existing contract or produce a deterministic first-convergence receipt per frozen window without increasing the unique-event denominator. Do not invent new windows.

## What is already good

- exact-ish deterministic observation/convergence IDs;
- wallet cohort filtering;
- self-initiated requirement;
- gift/dust/seed/passive-transfer rejection;
- economic-entity collapse;
- sellability gate;
- no BUY/SELL/copy-trade/portfolio authority;
- deterministic-first design.

These positives do not override F1-F6.

## Minimal code packet

Only patch the existing two scripts and their focused tests. Do not add a scheduler, scanner, scorer, ledger or model.

Acceptance:
1. WATCH/FURN recipient-seeding fixtures remain rejected and never increment.
2. independence PENDING cannot converge.
3. source_health UNKNOWN/DEGRADED cannot converge.
4. liquidity present but market-data health not explicitly PASS cannot converge.
5. missing required source lineage cannot converge.
6. replay of the same convergence cannot create a second promotion increment.
7. frozen 15/30/60/180m windows are represented without denominator inflation.
8. valid two-entity independently reproduced healthy/sellable fixture can freeze one eligible convergence.
9. all authority fields remain false.
10. no historical row is rewritten and no retrospective winner is inserted.

## Routing

Sol has completed the semantic/root-cause review. Remaining work is a bounded code correction + deterministic tests. Under current governance this is appropriate last-mile Codex work only. Sol must independently review the resulting diff before activation.
