# GCBLO Full Experiment Reproduction Package

**Dato:** 2026-07-25  
**Status:** SOURCE_NOTE  
**Område:** Claude/Fable research package / GCBLO reverse engineering  
**Primary folder:** `08_SOURCE_MATERIAL/claude/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `01_CORE_FRAMEWORK/governance/`, `06_RESEARCH_LAB/forward_tests/shared_evidence/`  
**Depends on:** PR #147 and PR #148 GCBLO source/audit package

## Package identity

```yaml
research_label: RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GCBLO
run_date: 2026-07-25
reported_run_clock: 2026-07-25_14_0X_UTC
kraken_server_unixtime: 1784988187
uploaded_zip: GCBLO repro pack 20260725.zip
zip_sha256: 054d2ef1a49bf03fb22d295a6aca8d165c7ad28c1095db4e7baceab2e770f791
zip_size_bytes: 390039
zip_member_count: 22
uploaded_pdf: GCBLO FULL REPORT.pdf
pdf_sha256: 7291f4e50b8907ccf5da22d41239eeb32c4f27b3231734399d11604f8bfb7edb
pdf_size_bytes: 44453
zip_integrity_test: PASS
```

## Repository artifact bundle

The relevant machine-readable research core is preserved under:

```text
08_SOURCE_MATERIAL/claude/gcblo/2026-07-25__full-experiment-package/
```

Directly archived:

```text
ARCHIVE_SCOPE.md
REPORT.md
PACKAGE_FILE_MANIFEST.csv
code/engine.py
code/outcomes.py
code/ablate.py
data/receipts.json
data/kraken_time.json
results/grid_pass.csv
results/sharpe_dist.json
```

`PACKAGE_FILE_MANIFEST.csv` preserves exact size and SHA-256 for all 22 original ZIP members. Large public-source extracts and the disputed packaged `grid_all.csv` are hash-anchored rather than copied as canonical rows before the environment-parity patch resolves which release is authoritative.

## Package contents

```text
REPORT.md
code/engine.py
code/outcomes.py
code/ablate.py
results/grid_all.csv
results/grid_pass.csv
results/sharpe_dist.json
data/WALCL.csv
data/WTREGEN.csv
data/RRPONTSYD.csv
data/ECBASSETSW.csv
data/JPNASSETS.csv
data/DEXUSEU.csv
data/DEXJPUS.csv
data/DTWEXBGS.csv
data/CBBTCUSD.csv
data/kraken_btc_w.json
data/kraken_time.json
data/receipts.json
data/BAMLH0A0HYM2.csv
data/CHNASSETS.csv
data/PBOCASSETS.csv
```

The three blocked CSV paths contain explicit upstream error text and were not used as valid numeric inputs.

## Receipt verification

The independently inspected package contains SHA-256 receipts for the available Kraken and FRED payloads. The following available local files matched their receipt hashes:

```text
KRAKEN_BTC_W
KRAKEN_TIME
FRED_WALCL
FRED_WTREGEN
FRED_RRPONTSYD
FRED_ECBASSETSW
FRED_JPNASSETS
FRED_DEXUSEU
FRED_DEXJPUS
FRED_DTWEXBGS
FRED_CBBTCUSD
```

Result:

```yaml
available_receipt_hashes_checked: 11
available_receipt_hash_mismatches: 0
blocked_receipts_preserved: 5
```

Blocked lanes:

```text
WDTGAL
BAMLH0A0HYM2
ALFRED_WALCL_20251007
ALFRED_WTREGEN_20251007
PBOC_ALL_CANDIDATES
```

## Claude-reported main findings

The package reports:

```text
shape-gated configurations: 4,575
configurations with all seven historical signals: 3,240
resemblance PASS at score <=45 weeks: 0
best resemblance score: 106.7 weeks
raw crossings before halving mask: 29
masked crossings: 7
arctangent downcross dates equal raw-composite downcross dates: TRUE, n=16
unselected median strategy Sharpe: approximately 0.58
buy-and-hold Sharpe: approximately 0.66
40-week moving-average Sharpe: approximately 0.87
share beating 40-week moving average: approximately 9 percent
current top-50 RE_FIRED share: 18 percent
current top-50 oscillator range: approximately -84 to +92
```

The report concludes that the candidate family does not reproduce the displayed chart, that the re-entry side is materially weaker than the exit side, that the arctangent scale is cosmetic for crossing dates, and that the halving mask removes most raw crossings.

## Independent execution result

The supplied code executed successfully in an isolated local copy using:

```text
Python 3.13.5
pandas 2.2.3
NumPy 2.3.5
```

Two clean runs with different `PYTHONHASHSEED` values produced byte-identical rerun outputs inside that environment.

Core results survived:

```text
shape-gated configurations: 4,575
resemblance PASS: 0
best score: 106.7 weeks
arctangent crossing identity: TRUE, n=16
halving mask: 29 -> 7
median strategy Sharpe: 0.5839
share beating 40-week moving average: approximately 8.7 percent
```

However, the packaged result files did not exactly reproduce from the packaged code and data in the independent environment.

Observed release-parity differences:

```yaml
packaged_grid_all_sha256: a14d72ff05ab2e33bcdb85a74168573fece94960c151c75c3a0d022f78383a81
independent_rerun_grid_all_sha256: bf240e39286ea10de62fafc55f8e758ac779623fc604c21c64cd273e08af6682
packaged_complete_signal_configs: 3240
independent_complete_signal_configs: 3242
packaged_top50_re_fired_share: 18_percent
independent_top50_re_fired_share: 16_percent
score_rows_changed: 128
miss_count_rows_changed: 14
stage_state_rows_changed: 11
```

Several best-50 median anchor errors also moved slightly, while the broad sell-versus-re-entry asymmetry remained.

## Reproducibility gaps

The ZIP does not contain:

```text
requirements.txt or dependency lock
Python/pandas/NumPy environment manifest
frozen reference-output hash manifest
rerun-output hash manifest
executable output verifier
cross-environment parity report
```

The report also describes a 4,800-configuration frozen grid, while the explicit Cartesian product in the supplied code contains 6,000 theoretical combinations before the shape gate:

```text
5 change horizons
x 4 z-score windows
x 5 EMA lengths
x 4 weight families
x 2 currency treatments
x 3 RRP samplings
x 5 threshold quantiles
= 6,000
```

This discrepancy requires reconciliation.

The Kraken receipt records `n_rows: 0` despite the payload containing weekly rows. The content hash is valid, but the row-count metadata should be corrected in a patch.

## Evidence boundary

```text
PACKAGE IDENTITY: PASS
RAW RECEIPT HASHES: PASS FOR AVAILABLE FILES
CODE EXECUTION: PASS
SAME-ENVIRONMENT REPEATABILITY: PASS
EXACT RELEASE PARITY: FAIL
CORE CONCLUSIONS: STABLE SHADOW LEARNING
EXACT COUNTS AND OUTPUT HASHES: PENDING PATCH
ORIGINAL GCBLO FORMULA: NOT RECOVERED
LIVE SIGNAL AUTHORITY: ZERO
```

The package is retained as source-backed research, not as canonical market truth or execution evidence.
