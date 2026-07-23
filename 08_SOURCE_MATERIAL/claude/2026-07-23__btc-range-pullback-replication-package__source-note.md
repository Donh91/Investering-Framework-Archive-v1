# Claude BTC Range and Pullback Replication Package

**Dato:** 2026-07-23  
**Status:** SOURCE_NOTE / EXECUTABLE_PACKAGE_RECEIVED / INDEPENDENT_QA_PENDING_PATCH  
**Område:** Claude Research Lab, weekly range research, pullback prediction, rebuy research, reproducibility  
**Primary folder:** `08_SOURCE_MATERIAL/claude/`  
**Supersedes source quality of:** `2026-07-22__claude-btc-range-pullback-17-experiment-summary__source-note.md`  
**Does not supersede governance verdict until patch and final rerun:** `06_RESEARCH_LAB/audit_summaries/2026-07-22__btc-range-headroom-and-pullback-predictability-audit__shadow.md`

---

## 1. Package identity

```yaml
uploaded_filename: BTC RANGE PULLBACK REPLICATION 20260722.zip
package_root: BTC_RANGE_PULLBACK_REPLICATION_20260722
received_date: 2026-07-23
claimed_package_members: 65
verified_package_members: 65
verified_file_members: 52
verified_directory_members: 13
compressed_size_bytes: 1398627
uncompressed_size_bytes: 4106343
claimed_zip_sha256: 872a967d230f4f8093c17016e50c51b637293f42b61474eb1ded622a3a5db364
verified_zip_sha256: 872a967d230f4f8093c17016e50c51b637293f42b61474eb1ded622a3a5db364
zip_integrity: PASS
raw_market_rows_included: YES
executable_code_included: YES
method_freeze_included: YES
full_17_experiment_registry_included: YES
frlp_metric_layer_included: YES
multiple_testing_layer_included: YES
overlap_and_era_controls_included: YES
internal_hash_manifest_included: YES
```

The original binary ZIP is not copied into the canonical repository in this ingestion. The durable repository record preserves package identity, package hash, source scope, independent QA and the required remediation contract. A corrected package should be considered for fuller source preservation after deterministic parity is repaired.

## 2. Included package structure

The package contains:

```text
00_EXECUTIVE_VERDICT.md
01_REPRODUCIBILITY_MANIFEST.json
02_DATA_LINEAGE.md
03_DATA_MANIFEST.json
04_METHOD_FREEZE.json
05_FEATURE_DICTIONARY.csv
06_ALL_17_EXPERIMENTS.csv
07_RANGE_RESULTS_FULL.csv
08_FRLP_METRIC_COMPARISON.csv
09_CENTRE_TILT_RESULTS.csv
10_PULLBACK_AND_REBUY_RESULTS.csv
11_EVENT_OVERLAP_SENSITIVITY.csv
12_ERA_AND_REGIME_STABILITY.csv
13_MULTIPLE_TESTING_REPORT.md
14_CURRENT_CONFIGURATION_AUDIT.md
15_REPRODUCTION_INSTRUCTIONS.md
16_REQUIREMENTS.txt
17_ENVIRONMENT.txt
18_HASHES.sha256
code/*
data/raw_or_acquisition_manifest/*
data/normalized/*
data/audit_samples/*
results/machine_readable_outputs/*
```

The ZIP also contains two generated `__pycache__/*.pyc` files. These are environment-specific build noise and should be removed from the corrected archive.

## 3. Primary data lineage

The package identifies the primary research series as:

```yaml
provider: Binance public data mirror
endpoint: https://data-api.binance.vision/api/v3/klines
symbol: BTCUSDT
market_type: spot
quote: USDT
interval: 1d
timezone: UTC
first_settled_date: 2017-08-17
last_settled_date: 2026-07-21
rows: 3261
calendar_gaps_by_open_time: 0
duplicates: 0
```

An ETHBTC series with the same date span and row count is included to correct the previous cross-check lineage statement.

Kraken is used only as a recent-window cross-check:

```yaml
BTC_pair: XBTUSD
ETHBTC_pair: ETHXBT
interval_minutes: 1440
rows_each: 721
fixed_comparison_window: 2024-08-06_TO_2026-07-21
primary_authority: BINANCE_MIRROR
```

Verified package cross-check claims:

```text
BTCUSDT vs Kraken XBTUSD:
715 aligned days
median absolute close difference 0.0386 percent
p95 0.1419 percent
maximum 0.2236 percent
conflicts above 0.50 percent: 0

ETHBTC vs Kraken ETHXBT:
715 aligned days
median absolute close difference 0.0315 percent
p95 0.1106 percent
maximum 0.2401 percent
conflicts above 0.50 percent: 0
```

The prior `0.031 percent` wording is therefore corrected: it referred to ETHBTC, not BTCUSDT.

## 4. Raw and normalized QA completed independently

The following were checked independently from the uploaded ZIP:

```text
all ten acquisition-response hashes: PASS
all ten acquisition-response byte sizes: PASS
BTCUSDT page concatenation equals joined raw JSON: PASS
ETHBTC page concatenation equals joined raw JSON: PASS
open timestamps ascending: PASS
open-timestamp duplicates: 0
open-time daily gaps: 0
normalized BTCUSDT values versus raw fields: exact numeric agreement
normalized ETHBTC values versus raw fields: exact numeric agreement
OHLC ordering violations: 0
```

One source-native anomaly was detected and was not identified in the package documentation:

```yaml
date: 2018-02-08
symbols: [BTCUSDT, ETHBTC]
open_time_utc: 2018-02-08T00:00:00Z
reported_close_time_utc_approx: 2018-02-08T00:28:14Z
expected_normal_daily_close_time: 2018-02-08T23:59:59.999Z
normalized_row_retained: YES
```

The source row should not be silently removed. The corrected package must flag it as a source anomaly and provide a one-row sensitivity check for material headline outcomes.

## 5. Claude-reported final statuses

```json
{
  "research_id": "BTC_RANGE_PULLBACK_REPLICATION_20260722",
  "original_17_experiments_reproduced": true,
  "raw_lineage_complete": true,
  "deterministic_rerun_pass": true,
  "independent_rerun_ready": true,
  "range_width_headroom_status": "SUPPORTED",
  "zero_linear_tilt_status": "WEAKENED",
  "adaptive_width_status": "NO_INCREMENTAL_VALUE",
  "pullback_bottom_catching_status": "NO_INCREMENTAL_VALUE",
  "low_vol_pullback_status": "FRAGILE",
  "multiple_testing_control": "PASS",
  "frlp_metric_conclusion": "DIFFERENT_FROM_JACCARD",
  "atr14_x_1_50_method_freeze_supported": false,
  "canonical_change_recommended": false,
  "new_test_recommended": false,
  "current_alert_recommended": false,
  "framework_state_change": false,
  "rebuy_change": false,
  "portfolio_action": false
}
```

Independent QA accepts the substantive statuses as provisionally stable but rejects `deterministic_rerun_pass: true` and unqualified `independent_rerun_ready: true` until the deterministic-output and verifier defects are repaired.

## 6. Source disposition

```text
PACKAGE_IDENTITY_AND_HASH: ACCEPT
RAW_SOURCE_PRESERVATION: ACCEPT_WITH_SOURCE_ANOMALY_NOTE_REQUIRED
ORIGINAL_17_EXPERIMENT_EXECUTION: ACCEPT
CORE_HEADLINE_REPRODUCTION: PASS_PROVISIONAL
DETERMINISTIC_EXACT_PARITY: FAIL_PENDING_PATCH
EXTENDED_VERIFIER_COVERAGE: FAIL_PENDING_PATCH
FRLP_METHOD_CHANGE: NO
LIVE_CAUTION_ALERT: NO
NEW_TEST_OR_ENGINE: NO
MARKET_OR_PORTFOLIO_AUTHORITY: ZERO
```

The package is materially stronger than the previous narrative-only source. It is not yet promoted to a fully reproducible truth-layer artifact because exact cross-run parity and extended-output verification are incomplete.