# Governance Receipt: GCBLO Research Artifact Bundle

**Dato:** 2026-07-26  
**Status:** PENDING_PR_VALIDATION  
**Branch:** `agent/task-20260726-gcblo-research-artifacts`  
**Scope:** source preservation / reproducibility core / no live authority

## Decision manifest

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

## Validation plan

```yaml
branch_readback: PENDING
manifest_member_count: PENDING_EXPECT_22
source_note_pointer: PENDING
changed_file_scope: PENDING_EXPECT_12_INCLUDING_RECEIPT
zero_deletions: PENDING
pull_request: PENDING
merge: PENDING
main_readback: PENDING
archive_content_result: PENDING
write_governance_result: PENDING
final_repository_state: PENDING
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
