# Archive Governance Skill Run — Full Sensor Backtest

**Dato:** 2026-07-12  
**Status:** RECEIPT_CORRECTED_V0_1_1  
**Område:** agent workflow / archive governance  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Related folders:** `04_MARKET_LEARNING/full_backtests/`, `01_CORE_FRAMEWORK/governance/`, `00_ARCHIVE_CONTROL/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `.agents/skills/canonical-context-router/SKILL.md`, `.agents/skills/archive-governance/SKILL.md`

## Context packet

```yaml
task_domain: market learning / full sensor backtest / archive governance
current_owner: 04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md
active_runtime_or_version: DATA_COMPLETION_CONTROL_STATE v1.2
required_addendum: 00_ARCHIVE_CONTROL/2026-07-12__index-addendum-full-sensor-simulation-backtest-v1.md
historical_context_allowed: YES, but legacy and source material remain non-authoritative
write_safety: isolated task branch + pull request; no direct main write
next_workflow: archive-governance
```

## Archive decision manifest

```yaml
archive_decision: EXISTING_OWNER_UPDATE
classification: CANONICAL_LEARNING_PLUS_GOVERNANCE_CONSEQUENCE
primary_owner: 04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md
operation: UPDATE_EXISTING_OWNER_AND_ADD_RECEIPT
paths_created:
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-12__archive-governance-full-sensor-backtest__receipt.md
paths_updated:
  - 04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md
  - 00_ARCHIVE_CONTROL/2026-07-12__index-addendum-full-sensor-simulation-backtest-v1.md
paths_deleted: []
canonical_index_change: NO
high_impact_gate: NOT_REQUIRED
duplicate_check: EXISTING_OWNER_FOUND_NO_PARALLEL_CANONICAL_DOCUMENT_CREATED
source_lineage:
  source_package_sha256: 75e4a4635e390b955cb3b1531cfd004cc2eda9180cb8706e318e69765af26198
  simulation_package_sha256: d75eb50829a4d9be51240e8fcf04930a85e85d455e23c6855e45718c67b83c5d
  canonical_control_state: 04_MARKET_LEARNING/truth_layer/DATA_COMPLETION_CONTROL_STATE.json
validation_plan:
  - read back all changed paths
  - verify status and frontmatter
  - verify referenced paths exist
  - verify no canonical-index modification
  - verify PR diff contains only intended files
```

## Durable unit preserved

The archive preserves the smallest durable decision unit:

1. the completed sensor-level backtest;
2. the negative findings that block unsupported BTC.D and stablecoin promotion;
3. the surviving shadow-only roles;
4. the explicit boundary against fabricating a full portfolio backtest;
5. the forward-falsification continuation path;
6. the source-package and simulation-package hashes;
7. the targeted Vault snapshot receipt already produced for the research package.

The conversational explanation itself is not copied verbatim. The canonical owner stores the durable learning, while this file stores the implementation receipt.

## Corrected pilot metrics under v0.1.1

```yaml
skill_name: archive-governance
qualified_use_number: 1
run_date: 2026-07-12
trigger_correct: YES
correct_owner_files_found: YES
registered_addenda_found: PARTIAL
legacy_as_current_error: NO
unnecessary_new_document_avoided: YES
unsupported_promotion_blocked: YES
branch_assertion: PARTIAL
explicit_branch_on_every_write: NO
manual_corrections_required: 1
incident_count: 1
archive_content_result: PASS
write_governance_result: PARTIAL_REMEDIATED
final_repository_state: PASS
notes: Existing canonical owner was updated instead of creating a duplicate. Index discoverability used the existing addendum, but a general addendum registry did not yet exist. One accidental temporary placeholder write to main occurred during tool setup and was immediately removed; no durable canonical content remained affected.
```

The previous `write_validation: PASS` classification is superseded by `write_governance_result: PARTIAL_REMEDIATED`. A clean final state does not erase the control incident.

## Remediation receipt

```text
accidental_path: _tmp_should_not_exist
creation_commit: 26d21e2a1151bb4663fedf3f61e6a50afd42fcb9
removal_commit: a19241702752ee380ade7d5f170da106df714471
final_state: PATH_ABSENT
impact: NONE_ON_CANONICAL_CONTENT
incident_retained_for_pilot: YES
```

## Backup-scope correction

```yaml
backup_product: TARGETED_SNAPSHOT
snapshot_root: snapshots/2026-07-12-full-sensor-backtest/source-tree/
snapshot_frozen_source_sha: 732a21f41d0292b3156451574f5d7b759ce3a97d
research_package_backup: PASS_TARGETED_RESEARCH_SNAPSHOT
paths_verified: 11/11
owner_update_merge_sha: ba40c6cb70121f6e3291ff882f8bd73a13386f9a
current_owner_version_in_snapshot: NO
skill_run_receipt_in_snapshot: NO
post_merge_delta_status: PENDING
full_git_mirror_status: NOT_CONFIGURED
```

The targeted snapshot protects the research package frozen before PR #8. It does not prove that the later owner upgrade, addendum update or this receipt version is already present in the Vault.

## Authority boundary

```text
market_call: NO
portfolio_action: NO
rule_ratification_from_receipt: NO
new_engine: NO
new_shadow_layer: NO
```
