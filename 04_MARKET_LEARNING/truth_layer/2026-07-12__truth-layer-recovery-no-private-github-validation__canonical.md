# Truth-Layer Recovery — No Private GitHub/Prior Thread Validation

**Date:** 2026-07-12  
**Status:** CANONICAL_CALIBRATION_EVIDENCE  
**Recovery package SHA-256:** `1973f59dd2756d8479013133259b2ad86d3cdf1cb279dde231c78a853e27944c`  
**Targeted private-GitHub offline export SHA-256:** `4328f79b6fb93562df9b460976a55e97c2118570dd7eebf52f400f60ebad89b1`

## Recovery package verdict

```text
FULL_M1_DIRECT_CONVENTION_READY: NO
M3_LEDGER_COVERAGE_READY: NO
STABLECOIN_HISTORY_READY: NO
PRIVATE_GITHUB_EXPORT_REQUIRED: YES
PRIOR_THREAD_REUPLOAD_REQUIRED: YES unless equivalent originals exist in GitHub
```

The recovery package correctly avoided:

- false private-GitHub access claims;
- false prior-thread continuity;
- all-missing calendar pseudo-data;
- retrospective state reconstruction;
- TVL substitution for supply/DEX activity;
- treating generated prior-thread ledgers as original source files.

## Main recovery findings

- Direct daily `CRYPTOCAP:BTC.D` history was not recovered.
- Historical DeFiLlama supply + DEX rows were not recovered through the available Custom GPT actions.
- The 21-row recovered decision ledger contained 3 accessible source-backed records and 18 inaccessible-prior-thread references.
- None were M3-eligible inside the Custom GPT environment.

## Main-framework GitHub reconciliation

ChatGPT had direct access to the private canonical repository and created a targeted offline snapshot containing actual source content for:

- the July 8–11 pullback-edge event ledger;
- the active gate/event registry;
- the 72H close receipt;
- W28 Master Monday raw source;
- W28 Forecast Ledger and lineage correction;
- current canonical/shadow pointers.

This upgraded 13 prior-thread rows to source-backed status and added one framework event-close row.

Current status:

```text
M3_JULY_8_11_EVENT_WINDOW_SOURCE_BACKED: YES
M3_LEDGER_COVERAGE_READY: NO
```

The event window is now usable for event-level analysis, but it remains a single short regime sequence and cannot support cross-regime promotion.

## Forecast-lineage warning

The W28 Forecast Ledger values remain frozen, but the later canonical correction controls:

```text
SOURCE_LINEAGE_UNRESOLVED
OFFICIAL_STATUS: SUSPENDED_PENDING_SOURCE_REPAIR
W28_SCORING_ELIGIBILITY: NO
```

No scoring or public/internal precision claim may use W28 until the ratification chain is repaired.

## Remaining blockers

### FULL M1

Requires a direct daily BTC.D series or an explicit provider export with settled timestamps.

### M3

Requires broader source-backed history from:

- Master Monday;
- Forecast Ledger;
- RAW 1–3D / 5–7D / 2–3W;
- PTR / Sequence;
- rebuy/deploy;
- profit/exit preparation;
- additional independent event regimes.

### Stablecoin deployment history

Requires chain-by-chain historical supply and DEX-volume exports or a runtime able to save those JSON responses.

## Governance

No market call.  
No portfolio action.  
No rule ratification.  
Rows remain evidence for later analysis only.
