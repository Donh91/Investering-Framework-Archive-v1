# BTC Range and Pullback Replication — Independent Rerun Audit

**Dato:** 2026-07-23  
**Status:** SHADOW_ONLY / INDEPENDENT_RERUN_COMPLETE / PATCH_REQUIRED  
**Område:** Research Lab, FRLP challenger, pullback and rebuy methodology, reproducibility  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Source package:** `08_SOURCE_MATERIAL/claude/2026-07-23__btc-range-pullback-replication-package__source-note.md`  
**Existing owners preserved:** T1 FRLP, T2 BTC Partial versus WAIT, T4 Pullback Edge Outcomes, T5 FNP Cumulative, Sensor Relationship & Incremental Value Standard

---

## 1. Executive verdict

```yaml
package_integrity: PASS
internal_409_value_checks: PASS
internal_current_hash_checks: PASS
independent_offline_pipeline_execution: PASS
independent_core_value_parity: PASS
exact_cross_run_output_parity: FAIL
extended_headline_verifier_coverage: INCOMPLETE
core_research_value: HIGH
canonical_promotion: NO
frlp_method_change: NO
current_alert: NO
new_test: NO
new_engine: NO
market_state_change: NO
rebuy_change: NO
portfolio_action: NO
next_action: TARGETED_CLAUDE_PATCH_THEN_CODEX_RERUN
```

The package is a substantial upgrade from the prior narrative summary. It contains raw responses, normalized rows, executable code, a predeclared method freeze, all 17 experiments, extended controls and internal checks.

The central research conclusions remained stable during independent execution. However, the package is not yet exact-output deterministic, and its verifier does not cover several of the headline claims that governance would rely on.

## 2. Independent execution completed

The uploaded package was extracted into a separate isolated directory and inspected before execution.

Static checks:

```text
Python scripts compile: PASS
unexpected shell or destructive system calls: NONE FOUND
network access: limited to explicit acquire_data.py endpoints
run_all subprocess scope: package-local Python scripts only
ZIP test: PASS
package SHA-256: MATCH
```

Original package validation:

```text
python3 code/verify_outputs.py
CHECKS: 409
FAILS: 0

python3 code/verify_outputs.py --hashes
CHECKS: 409
FAILS: 0
HASH CHECKS: OK
```

Independent offline rerun:

```text
python3 code/run_all_experiments.py --config 04_METHOD_FREEZE.json
pipeline result: COMPLETE
runtime: approximately 16 seconds
peak memory: approximately 149 MB

python3 code/verify_outputs.py
CHECKS: 409
FAILS: 0

python3 code/verify_outputs.py --hashes
CHECKS: 409
FAILS: 0
HASH CHECKS: OK
```

This proves that the preserved raw package can execute independently and reproduce the original 409-value table.

It does not prove exact cross-run output parity, because the hash manifest is regenerated before the hash verifier runs.

## 3. Blocking determinism defect

The package declares fixed RNG seeds and `deterministic_rerun_pass: true`.

The centre-tilt bootstrap uses:

```python
20260723 + int(d * 100) + hash(sp) % 97
```

where `sp` is the split label such as `full`, `train` or `test`.

Python string hashes are intentionally salted across interpreter processes unless hash randomisation is externally pinned. Therefore `hash(sp) % 97` is not a deterministic seed component.

Observed result:

```text
Original package environment versus independent environment:
6 non-reference files changed after the rerun.
The substantive generated differences were in:
- 09_CENTRE_TILT_RESULTS.csv
- results/machine_readable_outputs/extended.json

Two independent reruns in the same installed Python environment:
18 centre-tilt confidence-interval endpoints differed.

Every rerun still returned:
CHECKS 409 / FAILS 0
```

The changing values were bootstrap confidence-interval endpoints. Headline point estimates and final classifications remained stable, but exact-output determinism failed.

Required fix:

```text
Replace hash(sp) with an explicit frozen mapping, for example:
SPLIT_SEED_OFFSET = {"full": 0, "train": 1, "test": 2}

Optionally set PYTHONHASHSEED=0 as defence in depth,
but do not rely on process hash behaviour as the primary fix.
```

## 4. Hash verification is self-consistency, not reference parity

`run_all_experiments.py` rewrites `18_HASHES.sha256` after producing outputs.

`verify_outputs.py --hashes` then compares current files against the newly rewritten hash file.

Therefore the check proves:

```text
CURRENT_FILES_MATCH_CURRENTLY_GENERATED_MANIFEST
```

It does not prove:

```text
RERUN_OUTPUTS_MATCH_THE_ORIGINAL_RELEASE_OUTPUTS
```

Required fix:

```text
18_REFERENCE_HASHES.sha256
- frozen when the corrected release package is created
- never overwritten by a rerun
- covers deterministic files only

18_RERUN_HASHES.sha256
- generated on each rerun

verify_outputs.py --reference-hashes
- compares rerun deterministic outputs against the frozen reference manifest
- reports every excluded environment- or timestamp-dependent file explicitly
```

Environment-dependent files must either be frozen or excluded with reasons. Examples include creation time, Python version and platform-report files.

## 5. The 409 checks do not cover the main extended conclusions

The 409-value verifier validates `experiments_original.json` and current-state values.

It does not directly validate the most important new governance outputs in `extended.json`, including:

- formal family-max threshold;
- block-bootstrap threshold;
- named-variant confidence intervals;
- FRLP metric optima;
- independent event counts;
- overlap-controlled low-volatility status;
- BH and Holm results;
- final headline status mapping;
- source cross-check correction;
- boundary sensitivity.

Required extended assertions include at minimum:

```text
FORMAL_MULTIPLE_TESTING_THRESHOLD_famMax95_iid = 0.0215 within declared tolerance
famMax95_block8 = 0.0232 within declared tolerance
best named variant remains below family threshold
TEST Jaccard optimum m = 1.50
TEST Winkler alpha 0.10 optimum m = 2.25
TEST Winkler alpha 0.20 optimum m = 2.00
E12 TEST signal days = 28
E12 TEST independent events = 12
low_vol_pullback_status = FRAGILE
adaptive_width_status = NO_INCREMENTAL_VALUE
pullback_bottom_catching_status = NO_INCREMENTAL_VALUE
frlp_metric_conclusion = DIFFERENT_FROM_JACCARD
zero_linear_tilt_status = WEAKENED
current_alert_recommended = false
```

The corrected package should report separate counts for:

```text
ORIGINAL_EXPERIMENT_CHECKS
EXTENDED_GOVERNANCE_CHECKS
REFERENCE_HASH_CHECKS
TOTAL_CHECKS
```

## 6. Secondary statistical unit issue

The package applies exact binomial tests to independent merged signal events while using a day-level population success rate as the null probability.

This choice is disclosed and frozen, but the observational units differ:

```text
sample unit: independent event starts
null-rate unit: eligible days
```

That mismatch can make p-values difficult to interpret, particularly for clustered signals.

This does not invalidate the reproduced original experiments. It limits the strength of formal claims about BH survivors.

Required handling in the patch:

1. Preserve the current frozen calculation as `ORIGINAL_REPLICATION_STATISTIC`.
2. Add a clearly separate `UNIT_MATCHED_CHALLENGER` using one or more of:
   - blocked or cluster permutation;
   - matched eligible event anchors;
   - cooldown-based signal and control samples under the same event definition;
   - block bootstrap of incremental rate or outcome difference.
3. Report whether the four unconditional upside survivors remain significant.
4. Do not overwrite or retrospectively alter the original result table.

No new framework test is created by this statistical sensitivity layer.

## 7. Source QA anomaly

Both Binance source series contain one 2018-02-08 row whose reported kline close time is approximately 28 minutes after the UTC open rather than normal end-of-day.

```text
BTCUSDT open time: 2018-02-08T00:00:00Z
BTCUSDT raw close time: approximately 2018-02-08T00:28:14.788Z

ETHBTC open time: 2018-02-08T00:00:00Z
ETHBTC raw close time: approximately 2018-02-08T00:28:14.651Z
```

Open timestamps remain continuous, OHLC ordering is valid and the row is source-native. It should remain preserved, but it must be flagged.

The patch should add:

```text
SOURCE_ANOMALY_2018_02_08_EARLY_CLOSE
```

and a sensitivity row showing whether removing or replacing this one day changes any headline range result beyond tolerance.

## 8. Substantive findings that survived independent execution

The following core conclusions remained intact:

### 8.1 Range headroom

The fixed-centre width-only Jaccard oracle remains a bounded headroom measurement, not a universal forecasting ceiling.

Status:

```text
SUPPORTED_AS_SCOPED
```

### 8.2 Centre tilt

Large linear centre tilts remain harmful. The formal zero-tilt status remains `WEAKENED` because the predeclared paired-median condition for the small tilts is not satisfied.

Status:

```text
SUBSTANCE_STABLE
FORMAL_STATUS_WEAKENED
```

### 8.3 Adaptive width

No named adaptive or asymmetric variant exceeded the formal family threshold.

Status:

```text
NO_INCREMENTAL_VALUE_PROVISIONALLY_ACCEPTED
```

### 8.4 Low-volatility pullback caution

The bearish day-level story reverses under independent-event treatment and fails perturbation and multiplicity conditions.

Status:

```text
FRAGILE
NO_LIVE_ALERT
```

The durable methodological learning is that overlapping day-level observations can create misleading median outcome distributions.

### 8.5 FRLP metrics differ from Jaccard

The tested multiplier optimum depends on the loss function:

```text
TEST Jaccard grid optimum: 1.50
TEST Winkler alpha 0.10 grid optimum: 2.25
TEST Winkler alpha 0.20 grid optimum: 2.00
```

This supports retaining both DUMB 1.5 and DUMB 2.0 and rejects a universal ATR 1.5 method freeze.

The values are sample- and grid-specific. They do not promote DUMB 2.0 into a universal optimal model.

## 9. Governance conclusion

```text
FULL_REPRODUCIBILITY_PROMOTION: DEFER
SOURCE_PACKAGE_ARCHIVE: ACCEPT_WITH_QA
CORE_NEGATIVE_FINDINGS: ACCEPT_AS_REPRODUCED_SHADOW
REFERENCE_HASH_PARITY: FAIL_PENDING_PATCH
EXTENDED_VERIFICATION: FAIL_PENDING_PATCH
ATR14_X_1_50_FREEZE: REJECT
DUMB_2_0_CANONICAL_PROMOTION: REJECT
LIVE_CAUTION_FLAG: REJECT
ACTIVE_TEST_CHANGE: NO
NEW_TEST_OR_ENGINE: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
PORTFOLIO_ACTION: NO
```

The correct next step is a narrow repair package from Claude, followed by an independent Codex or local rerun. No additional exploratory research is needed before the repair.