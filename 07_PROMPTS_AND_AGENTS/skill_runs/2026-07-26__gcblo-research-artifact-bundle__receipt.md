# Governance Receipt: GCBLO Research Artifact Bundle

**Dato:** 2026-07-26  
**Status:** PASS  
**Initial branch:** `agent/task-20260726-gcblo-research-artifacts`  
**Finalization branch:** `agent/task-20260726-finalize-gcblo-research-artifacts`  
**Scope:** source preservation / reproducibility core / no live authority

## Final decision manifest

```yaml
archive_decision: ACCEPT_RELEVANT_MACHINE_READABLE_RESEARCH_CORE
source_owner: GCBLO_FULL_EXPERIMENT_SOURCE_NOTE
research_owner: GCBLO_FULL_EXPERIMENT_GOVERNANCE_RULING
operation: CREATE_10_UPDATE_1
full_zip_hash_preserved: YES
full_pdf_hash_preserved: YES
all_original_member_hashes_preserved: YES
large_public_payloads_copied: NO_HASH_AND_RECEIPT_ANCHORED
packaged_grid_all_copied: NO_PENDING_RELEASE_PARITY_PATCH
new_test: NO
new_engine: NO
market_state_change: NO
gate_change: NO
rebuy_change: NO
portfolio_action: NO
```

## Directly archived artifact paths

```text
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/ARCHIVE_SCOPE.md
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/REPORT.md
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/PACKAGE_FILE_MANIFEST.csv
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/code/engine.py
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/code/outcomes.py
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/code/ablate.py
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/data/receipts.json
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/data/kraken_time.json
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/results/grid_pass.csv
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/results/sharpe_dist.json
```

Updated pointer:

```text
08_SOURCE_MATERIAL/claude/2026-07-25__gcblo-full-experiment-reproduction-package__source-note.md
```

## Preservation boundary

The original ZIP has 22 members. Exact path, size and SHA-256 for all members are preserved in `PACKAGE_FILE_MANIFEST.csv`.

The large raw FRED/Kraken extracts and packaged `grid_all.csv` are not duplicated because the original release has unresolved cross-environment parity and PATCH1 must establish the authoritative environment and frozen reference hashes. Their exact hashes and source receipts remain preserved.

This does not discard evidence. It prevents a disputed generated result file from being silently promoted to canonical truth.

## Final validation record

```yaml
branch_readback: PASS
manifest_member_count: PASS_22
source_note_pointer: PASS
changed_file_scope: PASS_EXACTLY_12
zero_deletions: PASS
pull_request: 153
pull_request_url: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/153
pull_request_changed_files: 12
pull_request_additions: 660
pull_request_deletions: 0
workflow_runs: NONE
merge: PASS
merge_sha: 6aaad57bcc1a8a32bdb01de639de4c875e921d70
main_readback_manifest: PASS
main_readback_source_note: PASS
main_readback_report: PASS
main_readback_code: PASS
main_readback_receipts: PASS
main_readback_small_results: PASS
archive_content_result: PASS
write_governance_result: PASS
final_repository_state: PASS
```

## Authority boundary

```text
RESEARCH ARCHIVE: YES
SOURCE PRESERVATION: YES
EXECUTABLE CORE: YES
AUTHORITATIVE PATCHED RELEASE: NO
NEW ACTIVE TEST: NO
NEW ENGINE: NO
CURRENT GCBLO SIGNAL: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
PORTFOLIO ACTION: NO
```
