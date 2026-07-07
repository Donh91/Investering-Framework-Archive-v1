# Governance Hardening v1

Date: 2026-07-07  
Status: ACTIVE GOVERNANCE SUPPORT LAYER  
Purpose: Lock the operational rules required before no-hindsight replay or ETF-flow studies are executed.

## Why this folder exists

Custom GPT Sensor Supplement v1.1 confirmed that Research Operating System v1.1 is structurally ready, but not fully data-complete.

Before running replay, three governance risks must be controlled:

1. Wrong DATA PING version selection.
2. ETF placeholder rows being mistaken for finalized flow data.
3. Hindsight leakage through source timing/cutoff errors.

## Files

- `data_ping_version_manifest_v1.md`  
  Canonical active DATA PING version/layer manifest.

- `etf_flow_finalization_and_placeholder_rule_v1.md`  
  Rules for pending, placeholder and finalized ETF flow rows.

- `replay_source_cutoff_rules_v1.md`  
  Rules for which data may be used at each as-of timestamp during replay.

## Standing conclusion

These files do not create market calls or portfolio actions.

They only make future replay/research safer and more reproducible.
