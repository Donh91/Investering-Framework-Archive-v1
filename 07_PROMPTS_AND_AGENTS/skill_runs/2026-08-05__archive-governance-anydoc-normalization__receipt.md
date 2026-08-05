# Archive Governance AnyDoc Normalization Receipt

**Dato:** 2026-08-05  
**Status:** IMPLEMENTATION_RECEIPT  
**Område:** archive-governance / mixed document normalization / agent utility  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`  
**Depends on:** `07_PROMPTS_AND_AGENTS/github_agent/2026-08-05__anydoc-agent-document-normalization-v1__operational.md`

## Decision manifest

```yaml
archive_decision: EXTEND_EXISTING_AGENT_CAPABILITY
classification: OPERATIONAL_AGENT_UTILITY
primary_owner: .agents/skills/archive-governance/SKILL.md
operation: UPDATE_EXISTING_SKILL_AND_ADD_BOUNDED_UTILITY
target_branch: agent/task-20260805-anydoc-agent-normalization
branch_assertion: PASS
paths_created:
  - scripts/document_ingestion/anydoc_ingest.py
  - tests/document_ingestion/test_anydoc_ingest.py
  - 07_PROMPTS_AND_AGENTS/github_agent/2026-08-05__anydoc-agent-document-normalization-v1__operational.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-08-05__archive-governance-anydoc-normalization__receipt.md
paths_updated:
  - .agents/skills/archive-governance/SKILL.md
paths_deleted: []
canonical_index_change: NO
addendum_registry_change: NOT_APPLICABLE
high_impact_gate: NOT_REQUIRED
workflow_change: NO
duplicate_check: EXISTING_PDF_OWNER_PRESERVED
source_lineage:
  upstream_repository: https://github.com/firecrawl/anydoc
  npm_package: "@firecrawl/anydoc"
  pinned_version: "0.1.3"
backup_scope: NONE
```

## Why this is not a new skill or engine

The change extends `archive-governance`, which is already registered and active.

It adds one preprocessing utility for unreadable mixed document sources. It does not add a new market engine, shadow layer, test, score, ledger, schedule or framework authority.

The existing PDF Inspector owner remains the default route for PDF classification, page-level extraction and OCR/vision routing.

## Validation

```yaml
deterministic_test_command: python -m unittest tests.document_ingestion.test_anydoc_ingest -v
deterministic_tests: 6
deterministic_tests_passed: 6
python_compile: PASS_BY_TEST_IMPORT
real_upstream_npx_smoke: NOT_RUN_LOCAL_NETWORK_UNAVAILABLE
readback_paths_verified: 4_OF_4_BEFORE_RECEIPT
branch_writes_explicit: YES
main_writes: 0
backup_branch_writes: 0
write_incidents: 0
```

Covered cases:

- office document conversion and receipt;
- default PDF routing to existing specialist;
- deliberate PDF fallback marked `DEGRADED`;
- extensionless CSV with explicit format hint;
- converter failure;
- unsupported extension.

## Authority verification

```yaml
creates_truth: false
framework_state_change: false
model_weight_change: false
portfolio_action: false
canonical_promotion: false
raw_source_auto_commit: false
generated_markdown_auto_commit: false
ocr_performed: false
visual_interpretation_performed: false
```

## Result

```yaml
archive_content_result: PASS
write_governance_result: PASS
final_repository_state: PASS_PENDING_PR_REVIEW
incident_count: 0
new_engine_created: false
new_skill_created: false
scheduled_automation_added: false
```

## Remaining gate

Run one real upstream conversion with Node 20 and package-network access before adding AnyDoc to scheduled GitHub Actions or treating it as a production automation dependency.

That future workflow change is high-impact and requires the repository safepoint and vault sequence before implementation.
