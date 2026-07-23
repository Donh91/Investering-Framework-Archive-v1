# Archive Governance Receipt - Claude Replication PATCH1 Final Validation

**Dato:** 2026-07-23  
**Status:** RECEIPT / PENDING_PR_VALIDATION  
**Område:** Claude Research Lab ingestion, independent reproduction, archive governance  
**Task branch:** `agent/task-20260723-claude-replication-patch1-final-validation`

---

## Decision manifest

```yaml
archive_decision: ACCEPT_REPRODUCIBLE_SHADOW
source_package:
  filename: BTC RANGE PULLBACK REPLICATION 20260722 PATCH1.zip
  sha256: 03938802df31accd517b6fbfdd32206e4eb48d62b4173e54fc2c4fa496847e84
  zip_size_bytes: 1432476
  file_members: 66
classification:
  package_identity: ACCEPT
  executable_pipeline: ACCEPT
  raw_and_normalized_data: ACCEPT_WITH_SOURCE_ANOMALY_FLAG
  original_17_experiment_execution: PASS
  extended_governance_verification: PASS
  deterministic_reference_parity: PASS
  cross_process_parity: PASS
  cross_python_version_reference_parity: PASS
  core_findings: REPRODUCED_SHADOW
  canonical_range_change: NO
  active_test_change: NO
  current_alert: NO
  new_test: NO
  new_engine: NO
  market_state_change: NO
  gate_change: NO
  rebuy_change: NO
  portfolio_action: NO
paths_created:
  - 08_SOURCE_MATERIAL/claude/2026-07-23__btc-range-pullback-replication-patch1__source-note.md
  - 06_RESEARCH_LAB/audit_summaries/2026-07-23__btc-range-pullback-replication-patch1-final-validation__shadow.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-23__archive-governance-claude-replication-patch1-final-validation__receipt.md
paths_updated: []
paths_deleted: []
canonical_index_change: NO
active_test_registry_change: NO
workflow_change: NO
runtime_change: NO
```

## Independent validation evidence

```text
ZIP SHA-256: PASS
ZIP member integrity: PASS
Syntax inspection: PASS
Compiled cache members in uploaded ZIP: 0

Clean Run A:
Python 3.13.5
PYTHONHASHSEED 0
409 original checks / 0 failures
36 extended checks / 0 failures
57 reference checks / 0 failures
502 total checks / 0 failures

Clean Run B:
Python 3.13.5
PYTHONHASHSEED 987654321
409 original checks / 0 failures
36 extended checks / 0 failures
57 reference checks / 0 failures
502 total checks / 0 failures

Run A versus Run B deterministic files:
57 / 57 exact

Run A versus frozen Python 3.12.3 reference:
57 / 57 exact

Run B versus frozen Python 3.12.3 reference:
57 / 57 exact

Rerun manifests:
byte-identical
SHA-256 0420ff6e6990f95ba49414d7688fa1394a6d66f2659ef186469da3ed7ce8d5c6
```

## Final research statuses

```text
WIDTH_ONLY_HEADROOM: SUPPORTED_AS_SCOPED
ZERO_LINEAR_TILT: SUBSTANCE_STABLE / FORMAL_STATUS_WEAKENED
ADAPTIVE_WIDTH: NO_INCREMENTAL_VALUE
PULLBACK_BOTTOM_CATCHING: NO_INCREMENTAL_VALUE
LOW_VOL_PULLBACK: FRAGILE / NO_ALERT
FRLP_METRICS_VS_JACCARD: DIFFERENT
ATR14_X_1_50_METHOD_FREEZE: REJECT
DUMB_2_0_UNIVERSAL_PROMOTION: REJECT
SOURCE_ANOMALY_2018_02_08: MATERIAL_BUT_NON_DECISION_CHANGING
```

## Existing-owner routing

```text
T1 FRLP_V0_1 remains active.
T2 BTC Partial versus WAIT remains unchanged.
T4 Pullback Edge Outcomes remains unchanged.
T5 FNP Cumulative remains unchanged.
Sensor Relationship and Incremental Value Standard remains canonical owner.
```

No historical result is inserted as a forward row.

## Validation plan before merge

```text
1. Read back all three files from the task branch.
2. Compare task branch with main.
3. Verify exactly three intended paths.
4. Verify no canonical owner, active registry, workflow, index or runtime file changed.
5. Open PR and inspect exact filenames and mergeability.
6. Merge only after bounded-scope validation.
7. Read back the source note and final audit from main.
8. Finalize this receipt with PR and merge SHA.
```

## Pending status

```yaml
archive_content_result: PENDING_PR_VALIDATION
write_governance_result: PENDING_PR_VALIDATION
final_repository_state: PENDING_PR_VALIDATION
full_reproducibility_promotion: READY_PENDING_PR_VALIDATION
```
