# Archive Governance Receipt — Claude Replication Independent QA

**Dato:** 2026-07-23  
**Status:** RECEIPT / PENDING_PR_VALIDATION  
**Område:** Claude Research Lab ingestion, independent execution QA, reproducibility remediation  
**Task branch:** `agent/task-20260723-claude-replication-independent-qa`

---

## Decision manifest

```yaml
archive_decision: PARTIAL_ACCEPT_WITH_PATCH_REQUIRED
source_package:
  filename: BTC RANGE PULLBACK REPLICATION 20260722.zip
  sha256: 872a967d230f4f8093c17016e50c51b637293f42b61474eb1ded622a3a5db364
  zip_members: 65
  file_members: 52
  uncompressed_bytes: 4106343
classification:
  package_identity: ACCEPT
  raw_and_normalized_data: ACCEPT_WITH_SOURCE_ANOMALY_NOTE_REQUIRED
  original_17_experiment_execution: ACCEPT
  core_headline_results: REPRODUCED_SHADOW
  deterministic_exact_parity: FAIL_PENDING_PATCH
  extended_verifier_coverage: FAIL_PENDING_PATCH
  frlp_method_change: NO
  current_alert: NO
  canonical_rule: NO_NEW_RULE
  new_forward_test: NO
operation: CREATE_SOURCE_NOTE_INDEPENDENT_QA_PATCH_PROMPT_AND_RECEIPT
paths_created:
  - 08_SOURCE_MATERIAL/claude/2026-07-23__btc-range-pullback-replication-package__source-note.md
  - 06_RESEARCH_LAB/audit_summaries/2026-07-23__btc-range-pullback-replication-independent-rerun__shadow.md
  - 07_PROMPTS_AND_AGENTS/research_prompts/2026-07-23__claude-btc-range-pullback-replication-determinism-patch.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-07-23__archive-governance-claude-replication-independent-qa__receipt.md
paths_updated: []
paths_deleted: []
canonical_index_change: NO
active_test_registry_change: NO
workflow_change: NO
market_state_change: NO
gate_change: NO
rebuy_change: NO
portfolio_action: NO
```

## Independent validation evidence

```text
ZIP SHA-256 matched claimed value: PASS
ZIP member integrity: PASS
Python compilation: PASS
Acquisition-response hashes and byte sizes: PASS
Raw page concatenation: PASS
Normalized versus raw numeric values: PASS
Original verifier: 409 checks / 0 failures
Original current hash self-check: PASS
Independent offline pipeline: COMPLETE
Independent verifier: 409 checks / 0 failures
Independent current hash self-check: PASS
```

## Defects found

### D1 — Process-salted seed component

`extended_analysis.py` uses `hash(sp) % 97` in a bootstrap seed.

Effect observed:

```text
cross-environment generated CI differences: YES
same-installed-environment fresh-process CI differences: YES
independent-run extended-output exact parity: FAIL
headline classifications changed: NO
```

### D2 — Current-manifest hash self-check

The pipeline rewrites `18_HASHES.sha256` and then checks current files against that regenerated manifest.

Effect:

```text
self_consistency_proved: YES
release_reference_parity_proved: NO
```

### D3 — Extended headline verifier gap

The 409 checks do not directly assert the main extended governance conclusions.

### D4 — Statistical unit mismatch sensitivity required

Merged independent event observations are tested against a day-level null rate. Original calculations are preserved, but a unit-matched challenger is required.

### D5 — Unflagged source close-time anomaly

Both BTCUSDT and ETHBTC contain a 2018-02-08 source row with a reported close time approximately 28 minutes after open rather than normal daily close. Raw row retention is appropriate, but explicit flag and sensitivity are required.

### D6 — Package hygiene

Two `__pycache__/*.pyc` members are present and should be excluded from the corrected release.

## Existing-owner routing

```text
Range forward owner: T1 FRLP_V0_1 remains active.
BTC partial versus WAIT owner: T2 remains unchanged.
Pullback realised-value owner: T4 remains unchanged.
FNP lock-versus-opportunity owner: T5 remains unchanged.
Methodology owner: Sensor Relationship & Incremental Value Standard remains canonical.
```

No historical result is inserted as a forward row.

## Durable provisional learning

```text
WIDTH_ONLY_HEADROOM: SUPPORTED_AS_SCOPED
ZERO_LINEAR_TILT: SUBSTANCE_STABLE / FORMAL_STATUS_WEAKENED
ADAPTIVE_WIDTH: NO_INCREMENTAL_VALUE_PROVISIONAL
PULLBACK_BOTTOM_CATCHING: NO_INCREMENTAL_VALUE_PROVISIONAL
LOW_VOL_PULLBACK: FRAGILE / NO_ALERT
FRLP_METRICS_VS_JACCARD: DIFFERENT
ATR14_X_1_50_METHOD_FREEZE: REJECT
DUMB_2_0_UNIVERSAL_PROMOTION: REJECT
```

## Validation plan before merge

```text
1. Read back all four files from the task branch.
2. Compare task branch against current main.
3. Verify exactly four intended paths.
4. Verify no canonical owner, active registry, workflow, index or runtime file changed.
5. Open PR and inspect exact filenames and patch.
6. Merge only if branch remains clean and bounded.
7. Read back source note and QA audit from main.
8. Finalize receipt with PR and merge SHA.
```

## Pending status

```yaml
archive_content_result: PENDING_PR_VALIDATION
write_governance_result: PENDING_PR_VALIDATION
final_repository_state: PENDING_PR_VALIDATION
corrected_claude_package_received: NO
independent_codex_rerun_completed: NO
```