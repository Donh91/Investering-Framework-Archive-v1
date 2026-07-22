# Archive Governance Receipt - Claude Range and Pullback Audit

**Dato:** 2026-07-22  
**Status:** RECEIPT / PENDING_PR_VALIDATION  
**Område:** archive governance, Claude Research Lab ingestion  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Task branch:** `agent/task-20260722-claude-range-pullback-audit`

---

## Decision manifest

```yaml
archive_decision: PARTIAL_ACCEPT
classification:
  user_pasted_research: SOURCE_NOTE
  negative_findings: SHADOW_ONLY
  numeric_truth_layer: REJECT_PENDING_REPRODUCTION
  FRLP_method_freeze: REJECT_PENDING_FORWARD_EVIDENCE
  current_caution_flag: REJECT_AS_LIVE_ALERT
  canonical_rule: NO_NEW_RULE
  new_forward_test: NO
primary_owner: 06_RESEARCH_LAB/audit_summaries/2026-07-22__btc-range-headroom-and-pullback-predictability-audit__shadow.md
operation: CREATE_SOURCE_NOTE_SHADOW_SYNTHESIS_AND_RECEIPT
target_branch: agent/task-20260722-claude-range-pullback-audit
branch_assertion_after_remediation: PASS
paths_created:
  - 08_SOURCE_MATERIAL/claude/2026-07-22__claude-btc-range-pullback-17-experiment-summary__source-note.md
  - 06_RESEARCH_LAB/audit_summaries/2026-07-22__btc-range-headroom-and-pullback-predictability-audit__shadow.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-22__archive-governance-claude-range-pullback-audit__receipt.md
paths_updated: []
paths_deleted: []
canonical_index_change: NO
addendum_registry_change: NOT_APPLICABLE
high_impact_gate: NOT_REQUIRED
duplicate_check:
  FRLP_active_owner: FOUND
  active_test_registry: FOUND
  sensor_relationship_standard: FOUND
  pullback_and_FNP_test_owners: FOUND
  exact_prior_Claude_research: NOT_FOUND
source_lineage:
  received_as: USER_PASTED_CLAUDE_FABLE_SUMMARY
  raw_data: NOT_RECEIVED
  code: NOT_RECEIVED
  checksums: NOT_RECEIVED
  independent_reproduction: NOT_COMPLETED
backup_scope:
  backup_product: NONE
  current_version_in_snapshot: UNKNOWN
  post_merge_delta_status: NOT_REQUIRED
validation_plan:
  - read back every created file from the task branch
  - compare branch against main
  - verify exactly three intended paths
  - verify no active test, index, addendum, workflow or canonical owner changed
  - verify no numerical method promotion or current alert activation
  - inspect pull request diff and mergeability
  - merge only after validation
  - read back durable files from main
```

## Classification rationale

The research is relevant because it reports:

- a strong negative result for linear centre tilt;
- limited improvement from tested range-width refinements;
- failure of tested pullback-conditioned rebuy features;
- a useful example where hit-rate and payoff distribution disagree;
- a potentially useful challenge to how the framework allocates research effort.

It is not promoted because the message contains no raw data, source receipts, code, complete experiment table, formal multiplicity treatment or independent reproduction.

## Existing-owner routing

```text
Range forward question:
T1 FRLP_V0_1 remains active.

Pullback realised value:
T4 PULLBACK_EDGE_20260708_01_OUTCOMES remains owner.

Lock versus missed opportunity:
T5 FNP_CUMULATIVE remains owner.

BTC partial permission:
T2 GATE_BTC_PARTIAL_FT_1 remains owner.

Methodology and incremental value:
Sensor Relationship and Incremental Value Standard remains canonical owner.
```

No existing owner is rewritten by this ingestion.

## Key governance decisions

```text
PERFECT_WIDTH_ORACLE_0_624:
Retained only as a claimed width-only Jaccard result inside a fixed family.
Not accepted as a universal forecasting ceiling.

ZERO_DRIFT_TILT:
Accepted as a bounded negative finding for the tested linear previous-week-return shift.
Not generalised to every possible centre model.

DOWNSIDE_UNPREDICTABLE:
Narrowed to the tested feature set, target definition, data and split.
No impossibility claim accepted.

ATR14_X_1_50_FREEZE:
Not ratified.
FRLP forward test remains active.

HIT_RATE_PLUS_DISTRIBUTION:
Accepted as shadow reinforcement of existing loss-aware outcome governance.
No duplicate canonical rule created.

CURRENT_LOW_VOL_PULLBACK_CAUTION:
Stored as hypothesis context only.
No alert, state, gate, rebuy or portfolio effect.
```

## Write-routing incident disclosure

Before the task branch was created, two `create_file` calls were mistakenly attempted against the intended but not-yet-existing task branch.

Both calls returned `404 Branch not found` and created no repository content.

```yaml
incident_count: 2
incident_type: WRITE_ATTEMPT_BEFORE_BRANCH_CREATION
repository_mutation: NONE
incident_paths_created: []
failed_probe_path: SHOULD_NOT
remediation:
  - stopped failed route
  - loaded branch creation capability
  - created and verified the required isolated task branch
  - performed all successful writes with explicit task branch
```

This prevents an unqualified write-governance `PASS`, even though the final repository content can still pass after transparent remediation.

## Authority boundary

```text
MARKET_CALL: NO
CANONICAL_RANGE_CHANGE: NO
ACTIVE_TEST_CHANGE: NO
RULE_PROMOTION: NO
NEW_ENGINE: NO
NEW_TEST: NO
CURRENT_CAUTION_ALERT: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
DEPLOYMENT_CHANGE: NO
PORTFOLIO_ACTION: NO
```

## Pending validation status

```yaml
archive_content_result: PENDING_PR_VALIDATION
write_governance_result: PENDING_PARTIAL_REMEDIATED
final_repository_state: PENDING_PR_VALIDATION
incident_count: 2
incident_paths: []
remediation_commits: []
```
