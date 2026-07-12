# Agent Run Receipt

**Date:** YYYY-MM-DD  
**Status:** RECEIPT  
**Run ID:**  
**Originating Issue:**  
**Task class:**  
**Primary domain:**  
**Target branch:**  
**Base SHA:**  
**Pull request:**  

## Request

```yaml
requested_action:
write_intent:
expected_output:
authority_boundary:
```

## Context resolution

```yaml
canonical_context_router: PASS | PARTIAL | FAIL
current_owner_files:
registered_addenda:
legacy_as_current_error: YES | NO
unresolved_conflicts:
```

## Skill composition

```text
canonical-context-router
-> task-specific existing Skill
-> research-lab-red-team, when applicable
-> archive-governance
```

## Branch assertion

```yaml
target_branch_explicitly_supplied:
target_branch_verified_to_exist:
target_branch_is_default_branch:
target_branch_is_backup_branch:
branch_assertion:
```

## Iterations

```yaml
iteration_1_result:
iteration_1_verifier:
iteration_2_used:
iteration_2_result:
final_iteration_count:
max_iteration_breach:
```

## Canary and verifier

```yaml
canary_execution_mode: PYTHON_CORE | PYTHON_FULL | CONNECTOR_EQUIVALENT | NOT_APPLICABLE
canary_result:
domain_verifier:
domain_verifier_result:
failed_checks:
```

## Repository changes

```yaml
paths_created:
paths_updated:
paths_deleted:
canonical_index_change:
addendum_registry_change:
high_impact_gate:
duplicate_check:
```

## Result separation

```yaml
task_result: PASS | PARTIAL | FAIL
write_governance_result: PASS | PARTIAL_REMEDIATED | FAIL
verifier_result: PASS | PARTIAL | FAIL
final_repository_state: PASS | PARTIAL | FAIL
incident_count:
incident_paths:
```

## Backup scope

```yaml
backup_product:
snapshot_frozen_source_sha:
current_owner_or_merge_sha:
current_version_in_snapshot:
post_merge_delta_status:
```

## Learning

- What worked:
- What failed:
- What the Canary caught:
- What the existing Skills prevented:
- What should change next:
- What must not be automated:

## Stop

```yaml
stop_reason:
unresolved_items:
manual_action_required:
```
