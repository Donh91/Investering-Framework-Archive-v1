# Claude BTC Range and Pullback Replication PATCH1

**Dato:** 2026-07-23  
**Status:** SOURCE_NOTE / EXECUTABLE_RELEASE / INDEPENDENTLY_VALIDATED  
**Område:** Claude Research Lab, weekly range research, pullback prediction, rebuy research, reproducibility  
**Primary folder:** `08_SOURCE_MATERIAL/claude/`  
**Supersedes source quality of:** `2026-07-23__btc-range-pullback-replication-package__source-note.md`  
**Related audit:** `06_RESEARCH_LAB/audit_summaries/2026-07-23__btc-range-pullback-replication-patch1-final-validation__shadow.md`

---

## 1. Package identity

```yaml
uploaded_filename: BTC RANGE PULLBACK REPLICATION 20260722 PATCH1.zip
package_root: BTC_RANGE_PULLBACK_REPLICATION_20260722
received_date: 2026-07-23
zip_size_bytes: 1432476
file_members: 66
directory_members: 8
zip_sha256_claimed: 03938802df31accd517b6fbfdd32206e4eb48d62b4173e54fc2c4fa496847e84
zip_sha256_verified: 03938802df31accd517b6fbfdd32206e4eb48d62b4173e54fc2c4fa496847e84
zip_integrity: PASS
compiled_cache_members: 0
raw_market_rows_included: YES
normalized_data_included: YES
executable_code_included: YES
method_freeze_included: YES
all_17_experiments_included: YES
reference_hash_manifest_included: YES
unit_matched_challenger_included: YES
source_anomaly_report_included: YES
cross_run_parity_report_included: YES
```

The binary ZIP is not copied into the canonical repository. The durable archive preserves its exact identity, source hash, scope, independent execution evidence, findings and authority boundary.

## 2. Main repairs relative to the first executable package

PATCH1 repairs the blocking reproducibility defects identified by the independent QA:

1. `hash(sp) % 97` was removed from bootstrap seed construction.
2. A frozen explicit split mapping is used instead:

```python
SPLIT_SEED_OFFSET = {"full": 0, "train": 1, "test": 2}
```

3. Frozen release reference hashes are separated from rerun hashes.
4. The verifier now checks original experiments, extended governance values and frozen reference parity separately.
5. A unit-matched challenger was added without overwriting the original statistics.
6. The 2018-02-08 truncated source candle is retained, flagged and sensitivity-tested.
7. `__pycache__` and `.pyc` files were removed.
8. Deterministic outputs were compared across fresh processes with different `PYTHONHASHSEED` values.

## 3. Independent validation environment

The package was independently extracted twice and executed from two separate working directories.

```yaml
independent_python_version: 3.13.5
claude_reference_environment_python: 3.12.3
run_a_pythonhashseed: 0
run_b_pythonhashseed: 987654321
separate_processes: YES
separate_working_directories: YES
network_reacquisition_used: NO
raw_package_data_used: YES
```

The frozen reference hashes were created by the supplied release on Python 3.12.3. Both independent Python 3.13.5 runs matched all frozen deterministic reference files. This closes both process-seed parity and the previously untested Python-version leg for the declared deterministic scope.

## 4. Independent execution results

Each clean run produced:

```text
ORIGINAL_EXPERIMENT_CHECKS: 409 / 0 failures
EXTENDED_GOVERNANCE_CHECKS: 36 / 0 failures
REFERENCE_HASH_CHECKS: 57 / 0 failures
TOTAL_CHECKS: 502
TOTAL_FAILURES: 0
```

Direct independent comparison:

```yaml
reference_files: 57
run_a_vs_run_b_mismatches: 0
run_a_vs_reference_mismatches: 0
run_b_vs_reference_mismatches: 0
rerun_manifests_identical: YES
rerun_manifest_sha256: 0420ff6e6990f95ba49414d7688fa1394a6d66f2659ef186469da3ed7ce8d5c6
cross_run_exact_parity: PASS
cross_version_reference_parity: PASS
```

No cache files were generated or retained after the complete runs.

## 5. Verified package findings

The independently validated final statuses are:

```yaml
range_width_headroom_status: SUPPORTED
zero_linear_tilt_status: WEAKENED
adaptive_width_status: NO_INCREMENTAL_VALUE
pullback_bottom_catching_status: NO_INCREMENTAL_VALUE
low_vol_pullback_status: FRAGILE
multiple_testing_control: PASS
frlp_metric_conclusion: DIFFERENT_FROM_JACCARD
atr14_x_1_50_method_freeze_supported: false
canonical_change_recommended: false
new_test_recommended: false
current_alert_recommended: false
framework_state_change: false
rebuy_change: false
portfolio_action: false
```

### Range metric divergence

The test-grid optimum depends on the loss function:

```text
Jaccard optimum multiplier: 1.50
Winkler alpha 0.10 optimum multiplier: 2.25
Winkler alpha 0.20 optimum multiplier: 2.00
```

This validates the conclusion that Jaccard alone cannot select the official weekly range method. It supports keeping DUMB 1.5 and DUMB 2.0 as separate baselines. It does not promote DUMB 2.0 or another multiplier into a universal forecast method.

### Unit-matched challenger

The repaired challenger reports:

```text
DOWNSIDE survivors: 0 / 24
PULLBACK-conditioned survivors: 0 / 20
COMPOSITE survivors: 0 / 6
Unconditional UPSIDE survivors retained: 3 / 4
```

The retained upside features are:

```text
atr_ts_top
clv5_top
ext20_top
```

`vol_r_top` falls outside the adjusted threshold under the unit-matched challenger.

The package transparently documents and rejects an earlier biased control construction based on complement-run start days. That construction produced two false downside survivors and was discarded before the final report.

## 6. Source anomaly

The package identifies one genuine truncated source candle on 2018-02-08 in both BTCUSDT and ETHBTC.

```yaml
source_anomaly_id: SOURCE_ANOMALY_2018_02_08_EARLY_CLOSE
status: MATERIAL
row_preserved: YES
headline_status_changes: 0
material_headline_field_changes: 1
changed_headline_field: E11 event counts
E11_existing_verdict: REJECTED_INCONSISTENT
```

The anomaly is material under the predeclared rule because some count fields move beyond tolerance. It does not alter any research-question answer, effect size, lift, median, oracle, headroom, centre-tilt conclusion, FRLP optimum or final governance status.

## 7. Source disposition

```text
SOURCE_PACKAGE_IDENTITY: ACCEPT
RAW_AND_NORMALIZED_DATA: ACCEPT_WITH_SOURCE_ANOMALY_FLAG
EXECUTABLE_PIPELINE: ACCEPT
DETERMINISTIC_REFERENCE_PARITY: PASS
EXTENDED_GOVERNANCE_VERIFIER: PASS
CORE_RESEARCH_FINDINGS: REPRODUCED_SHADOW
CANONICAL_RANGE_METHOD_CHANGE: NO
ACTIVE_TEST_CHANGE: NO
CURRENT_ALERT: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
PORTFOLIO_ACTION: NO
```
