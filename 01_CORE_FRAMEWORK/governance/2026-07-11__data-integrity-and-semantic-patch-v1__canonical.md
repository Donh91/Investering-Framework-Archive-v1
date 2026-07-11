# Data Integrity and Semantic Patch v1.0

**Date:** 2026-07-11  
**Status:** CANONICAL PROCESS PATCH  
**Authority:** Governance/process only; no predictive promotion.

## Revisable observation fields

Every revisable source print must support:

- `print_status`: PRINT_PROVISIONAL / PRINT_FINAL / PRINT_REVISED / DATA_MISSING
- `original_value`
- `current_value`
- `revision_delta`
- `source_published_ts`
- `source_verified_ts`
- `primary_source`
- `conflict_status`
- `notes`

A print less than 24 hours old is provisional unless its primary source explicitly marks it final.

## Semantic protections

- Replace `EXECUTE_WINDOW` with `MAX_ATTENTION_WINDOW` in every zero-execution layer.
- `regime_state` is descriptive context, not a future-risk forecast.
- ETF A1/A2 = urgency only.
- ETH/BTC C = warning/repair only.
- D price/vol = confirmation/veto.
- No one-sensor action.
- No blended overall score.
- No self-reported actuals for scoring.
- No shadow field gains execution authority without promotion governance.

## Sensor birth certificate

New sensor rows should include:

- `first_available_date`
- `historical_coverage_start`
- `live_since`
- `revision_risk`
- `regime_coverage`
- `cross_cycle_claim_allowed`

A sensor cannot support a cross-cycle claim before its data exists.

## Effective scope

Applies to DATA PING, Sunday Closeout, Master Monday, FRLP, rotation logs, Research Lab exports and future sensor audits.
