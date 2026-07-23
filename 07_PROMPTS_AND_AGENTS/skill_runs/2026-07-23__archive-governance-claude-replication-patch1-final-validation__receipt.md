# Archive Governance Receipt - Claude Replication PATCH1 Final Validation

**Dato:** 2026-07-23  
**Status:** PASS_CONTENT / FULL_REPRODUCIBILITY_VALIDATED  
**Område:** Claude Research Lab ingestion, independent reproduction, archive governance  
**Initial task branch:** `agent/task-20260723-claude-replication-patch1-final-validation`  
**Finalization branch:** `agent/finalize-claude-replication-patch1-validation-20260723`

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
paths_updated_after_merge:
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-23__archive-governance-claude-replication-patch1-final-validation__receipt.md
paths_deleted: []
canonical_index_change: NO
active_test_registry_change: NO
workflow_change: NO
runtime_change: NO
main_merge:
  pull_request: 127
  merge_commit_sha: ce03c07bc47adef7d7afabc5b4ddd22b067197a6
  merge_method: SQUASH
  changed_files: 3
  merged: YES
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

## Validation completed

```text
TASK_BRANCH_READBACK_SOURCE_NOTE: PASS
TASK_BRANCH_READBACK_FINAL_AUDIT: PASS
TASK_BRANCH_READBACK_RECEIPT: PASS
PR_127_CHANGED_FILE_SCOPE: PASS_EXACTLY_3_INTENDED_PATHS
PR_127_MERGEABLE: PASS
PR_127_MAIN_MERGE: PASS
MAIN_MERGE_SHA: ce03c07bc47adef7d7afabc5b4ddd22b067197a6
CANONICAL_OWNER_FILES_CHANGED: NO
ACTIVE_TEST_REGISTRY_CHANGED: NO
INDEX_CHANGED: NO
WORKFLOW_CHANGED: NO
RUNTIME_CHANGED: NO
MARKET_OR_PORTFOLIO_AUTHORITY_CREATED: NO
```

## Final status

```yaml
archive_content_result: PASS_ACCEPT_REPRODUCIBLE_SHADOW
write_governance_result: PASS
final_repository_state: PASS
full_reproducibility_promotion: PASS_FOR_DECLARED_SHADOW_SCOPE
canonical_promotion: NO
main_merge_commit_sha: ce03c07bc47adef7d7afabc5b4ddd22b067197a6
```

The archive now preserves the corrected package lineage, exact cross-process and cross-version deterministic parity, the unit-matched statistical correction, the source anomaly and the bounded governance consequence. No method, state, gate, rebuy or portfolio authority changed.
