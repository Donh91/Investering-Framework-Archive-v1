# Archive Governance Skill Run — Full Sensor Backtest

**Dato:** 2026-07-12  
**Status:** RECEIPT  
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
7. the targeted Vault snapshot receipt already produced for this research package.

The conversational explanation itself is not copied verbatim. The canonical owner stores the durable learning, while this file stores the implementation receipt.

## Pilot metrics

```yaml
skill_name: archive-governance
run_date: 2026-07-12
trigger_correct: YES
correct_owner_files_found: YES
legacy_as_current_error: NO
unnecessary_new_document_avoided: YES
unsupported_promotion_blocked: YES
manual_corrections_required: 1
write_validation: PASS
notes: Existing canonical owner was updated instead of creating a duplicate. Index discoverability was preserved through the existing addendum, avoiding a high-impact CANONICAL_INDEX edit. One accidental temporary placeholder write to main occurred during tool setup and was immediately removed in the next commit; no durable archive content was affected.
```

## Remediation receipt

```text
accidental_path: _tmp_should_not_exist
creation_commit: 26d21e2a1151bb4663fedf3f61e6a50afd42fcb9
removal_commit: a19241702752ee380ade7d5f170da106df714471
final_state: PATH_ABSENT
impact: NONE_ON_CANONICAL_CONTENT
```

## Authority boundary

```text
market_call: NO
portfolio_action: NO
rule_ratification_from_receipt: NO
new_engine: NO
new_shadow_layer: NO
```
