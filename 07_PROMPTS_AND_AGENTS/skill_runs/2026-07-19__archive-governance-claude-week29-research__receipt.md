# Archive Governance Receipt - Claude Week 29 Research Package

**Dato:** 2026-07-19  
**Status:** RECEIPT / PENDING_PR_VALIDATION  
**Område:** archive governance / Research Lab ingestion  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Task branch:** `agent/task-20260719-w29-claude-research-audit`

---

## Decision manifest

```yaml
archive_decision: PARTIAL_ACCEPT
classification:
  source_package: SOURCE_NOTE_PARTIAL_PASS_WITH_BLOCKING_LIMITATIONS
  durable_learning: SHADOW_ONLY
  official_actuals: REJECT
  official_score: REJECT
  canonical_rule: REJECT
  new_forward_test: REJECT
primary_owner: 06_RESEARCH_LAB/audit_summaries/2026-07-19__week29-claude-red-team-ingestion__shadow.md
operation: CREATE_TWO_DURABLE_SYNTHESIS_FILES_AND_RECEIPT
target_branch: agent/task-20260719-w29-claude-research-audit
branch_assertion: PASS
paths_created:
  - 08_SOURCE_MATERIAL/claude/2026-07-19__claude-week29-research-package__source-note.md
  - 06_RESEARCH_LAB/audit_summaries/2026-07-19__week29-claude-red-team-ingestion__shadow.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-19__archive-governance-claude-week29-research__receipt.md
paths_updated: []
paths_deleted: []
canonical_index_change: NO
addendum_registry_change: NOT_APPLICABLE
high_impact_gate: NOT_REQUIRED
duplicate_check:
  active_event_and_decision_context: OVERLAP_FOUND
  F12_falsifiability_governance: OVERLAP_FOUND
  transmission_forward_test: OVERLAP_FOUND
  active_test_registry: EXISTING_OWNERS_FOUND
source_lineage:
  zip_name: CLAUDE WEEK29 RESEARCH PACKAGE 2026.zip
  zip_sha256: dc9e2362dbe03500fcef560810f4ac3303179b861934524a64a62af47cc8a889
  zip_files: 14
  executive_pdf_sha256: f0b9e0daa2ce1b755f8dace74da641fc6cbd7ca964175365a9a5de37fde267a8
  red_team_pdf_sha256: 03566aa4deaef494660a5f89bf1c04be4a827a8a8908f7ba9e82de0b99e79c80
backup_scope:
  backup_product: NONE
  current_version_in_snapshot: UNKNOWN
  post_merge_delta_status: NOT_REQUIRED
validation_plan:
  - verify ZIP hash and member count
  - parse all CSV and JSON files
  - compare source convention with frozen Forecast Ledger
  - verify week settlement status
  - verify ETF ledger completed-session count
  - verify current Farside completion against provisional values
  - route H10 through current F12 and Transmission Matrix governance
  - read back all branch writes
  - inspect exact PR changed-file scope
  - merge only after diff validation
```

## Key QA results

```text
ZIP_HASH: PASS
FILES_PRESENT: 14_OF_14
CSV_JSON_PARSE: PASS
RAW_SOURCE_REPRODUCIBILITY: FAIL
OFFICIAL_PRICE_CONVENTION: FAIL_CRYPTOCOM_UTC_NOT_BINANCE_CEST
WEEK_SETTLEMENT: FAIL_SUNDAY_PARTIAL
ETF_20_COMPLETED_SESSION_CLAIM: FAIL_16_SETTLED_ONLY
17JUL_FARSIDE_REVISION: PACKAGE_STALE
ETF_WINDOW_AGGREGATES: REJECT
H10_CANONICAL_NOVELTY: REJECT_EXISTING_F12_FREEZE_AND_FALSIFICATION_PROTOCOL
SHADOW_RESEARCH_VALUE: PASS
```

## Archive inflation avoided

The following package files were not copied individually into GitHub:

```text
seven CSV ledgers
six Markdown reports
one JSON summary
two PDF renderings
binary ZIP
```

Reason:

- multiple files repeat the same conclusions;
- several numeric claims are provisional or invalid;
- raw source receipts and reproduction code are absent;
- archive policy prefers the durable learning rather than every intermediate Claude report.

## Authority result

```text
MARKET_CALL: NO
PORTFOLIO_ACTION: NO
RULE_PROMOTION: NO
NEW_ENGINE: NO
NEW_TEST: NO
OFFICIAL_W29_SCORE: NO
```

## Final validation fields

```yaml
archive_content_result: PENDING_PR_VALIDATION
write_governance_result: PENDING_PR_VALIDATION
final_repository_state: PENDING_PR_VALIDATION
incident_count: 0
incident_paths: []
remediation_commits: []
```
