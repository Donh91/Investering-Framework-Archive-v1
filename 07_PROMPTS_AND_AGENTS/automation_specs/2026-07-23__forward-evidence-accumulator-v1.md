# Forward Evidence Accumulator v1

**Date:** 2026-07-23  
**Status:** OPERATIONAL AUTOMATION SPEC  
**Cadence:** Daily after normal DATA PING and research enrichment work  
**Repository:** `Donh91/Investering-Framework-Archive-v1`

## Purpose

Accumulate append-only prospective source rows and matured outcomes for the existing T1, T2, T4 and T5 owners, so later retrospective analysis has matched observational units, complete distributions and exact lineage.

## Required startup

Read:

1. `AGENTS.md`
2. `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
3. current registered addenda
4. `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`
5. `06_RESEARCH_LAB/protocols/2026-07-23__continuous-forward-evidence-accumulation-v1__operational.md`
6. `06_RESEARCH_LAB/forward_tests/shared_evidence/decision_distribution_ledger_v1.csv`
7. `06_RESEARCH_LAB/forward_tests/shared_evidence/latest_state.json`
8. FRLP ledger and latest verified actuals
9. latest accepted DATA PING, decision context and relevant event/FNP ledgers

## Eligible work

- Freeze new source rows for T2, T4 or T5 when a real-time accepted source and declared horizon exist.
- Complete matured 24H, 72H, 7D or other frozen outcomes from later verified data.
- After settled weekly actuals, cross-check T1 FRLP coverage and append a shared evidence reference row where useful.
- Preserve both daily path rows and independent-event rows.
- Use matched observational units for signal and control summaries.
- Update `latest_state.json` only after merged main readback.

## Rejection rules

Reject and record the reason when:

- the source is retrospective narrative only;
- the outcome was already known at freeze time;
- source timestamp or hash is missing;
- the row duplicates an existing evidence ID or source hash;
- the fixed horizon is absent;
- a partial candle/session is presented as settled;
- an overlapping daily row is presented as an independent event;
- signal and control units differ without an explicit challenger label;
- the row would create a new test or change framework authority.

## Write discipline

Use one bounded `agent/task-*` branch and PR only when valid rows exist. Never write directly to `main`. Append only. Validate CSV field count, evidence-ID uniqueness, source hash, zero deletion and previous-state preservation. Merge only after branch readback and exact changed-file validation. Read back from main and record merge SHA.

## Notification gate

Remain silent on normal no-new-row runs and routine successful appends. Notify only on:

- a source-integrity failure;
- duplicate or lineage conflict;
- a matured strong/severe outcome;
- 20, 30 or 40 eligible outcomes reached;
- a material regime-concentrated failure mode;
- a write or readback failure;
- any action that would require a new test, method or framework authority.

## Authority boundary

```text
NEW_TEST: NO
NEW_ENGINE: NO
RULE_PROMOTION: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
PORTFOLIO_ACTION: NO
```
