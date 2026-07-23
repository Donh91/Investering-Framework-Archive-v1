# Claude Patch Prompt — BTC Range Pullback Replication Determinism Repair

**Dato:** 2026-07-23  
**Status:** REMEDIATION_PROMPT / NO_NEW_RESEARCH  
**Purpose:** Repair the received replication package without changing its frozen research design or headline claims.

---

Copy the complete prompt below to Claude and attach the original replication ZIP.

```text
BTC RANGE AND PULLBACK REPLICATION
TARGETED DETERMINISM, VERIFIER AND SOURCE-QA PATCH

ROLE

You are Claude/Fable acting as the original replication engineer.

Your package:

BTC_RANGE_PULLBACK_REPLICATION_20260722

was independently extracted, inspected and executed successfully.

Confirmed independently:

- package SHA-256 matched;
- ZIP integrity passed;
- 65 members were present;
- all acquisition-response hashes and byte sizes passed;
- raw page concatenation passed;
- normalized BTCUSDT and ETHBTC values matched raw fields;
- the offline pipeline completed;
- the original 409 value checks returned 0 failures;
- the central point estimates and classifications remained stable.

The package is not rejected.

It requires a narrow repair before it may be called exact-output deterministic and independently reproducible.

Do not rerun broad exploratory research.
Do not change the original 17 hypotheses.
Do not change targets, thresholds, splits, feature formulas or result classifications unless a repaired deterministic run genuinely requires a correction.
Do not activate a canonical change, new test, alert, gate, rebuy or portfolio action.

============================================================
1. BLOCKING DETERMINISM DEFECT
============================================================

Independent execution found this seed construction in extended_analysis.py:

20260723 + int(d * 100) + hash(sp) % 97

Python string hash values are process-salted.

Observed evidence:

- original package versus an independent Python environment changed the generated centre-tilt confidence intervals;
- two fresh runs in the same installed Python environment produced 18 different confidence-interval endpoints in extended.json;
- 09_CENTRE_TILT_RESULTS.csv and extended.json changed while verify_outputs.py still reported 409/0.

Required repair:

Replace hash(sp) with an explicit frozen mapping such as:

SPLIT_SEED_OFFSET = {
  "full": 0,
  "train": 1,
  "test": 2
}

Use only deterministic integer seed composition.

You may set PYTHONHASHSEED=0 as defence in depth, but the pipeline must not depend on Python's salted hash function.

Search the complete codebase for any other use of:

- hash(...)
- unordered set iteration affecting output order;
- environment-dependent random seeds;
- current time inside deterministic result files;
- unpinned dictionary or filesystem ordering;
- platform-dependent float formatting.

Document every remediation.

============================================================
2. REFERENCE HASH PARITY
============================================================

The current pipeline rewrites 18_HASHES.sha256 and then verifies files against the newly written manifest.

That proves current self-consistency, not parity with the released reference package.

Create two separate manifests:

18_REFERENCE_HASHES.sha256

- frozen when the corrected release ZIP is created;
- never overwritten by run_all_experiments.py;
- covers every deterministic member file;
- excludes only explicitly declared nondeterministic metadata files.

18_RERUN_HASHES.sha256

- regenerated on each rerun.

Extend verification with:

python3 code/verify_outputs.py --reference-hashes

It must:

1. compare deterministic rerun files to 18_REFERENCE_HASHES.sha256;
2. fail on any changed deterministic file;
3. report files excluded from exact parity and the reason for each exclusion;
4. retain the current internal self-consistency check separately.

Do not claim HASH PARITY from a manifest generated during the same run.

============================================================
3. EXTENDED GOVERNANCE VERIFIER COVERAGE
============================================================

The existing 409 checks mainly validate experiments_original.json and current-state values.

Add exact assertions for the extended outputs used in the executive conclusion.

At minimum verify, within frozen tolerances:

- formal family-max iid threshold approximately 0.0215;
- block-8 family-max threshold approximately 0.0232;
- no named adaptive variant exceeds the formal threshold;
- TEST Jaccard grid optimum multiplier = 1.50;
- TEST Winkler alpha 0.10 grid optimum multiplier = 2.25;
- TEST Winkler alpha 0.20 grid optimum multiplier = 2.00;
- E12 TEST signal-day count = 28;
- E12 TEST independent-event count = 12;
- low_vol_pullback_status = FRAGILE;
- adaptive_width_status = NO_INCREMENTAL_VALUE;
- pullback_bottom_catching_status = NO_INCREMENTAL_VALUE;
- zero_linear_tilt_status = WEAKENED;
- frlp_metric_conclusion = DIFFERENT_FROM_JACCARD;
- atr14_x_1_50_method_freeze_supported = false;
- current_alert_recommended = false;
- framework_state_change = false;
- rebuy_change = false;
- portfolio_action = false;
- BTC cross-check median = 0.0386 percent within tolerance;
- ETHBTC cross-check median = 0.0315 percent within tolerance;
- Sun-Sat boundary sensitivity remains recorded.

Report separately:

ORIGINAL_EXPERIMENT_CHECKS
EXTENDED_GOVERNANCE_CHECKS
REFERENCE_HASH_CHECKS
TOTAL_CHECKS
TOTAL_FAILURES

============================================================
4. STATISTICAL UNIT SENSITIVITY
============================================================

The original replication uses independent merged signal events as the sample but a day-level population success rate as the exact-binomial null.

Preserve this calculation unchanged and label it:

ORIGINAL_REPLICATION_STATISTIC

Add a separate, non-overwriting challenger labelled:

UNIT_MATCHED_CHALLENGER

Use at least one statistically coherent method with matched observational units, preferably two:

A. matched eligible event anchors under the same merge/cooldown rule;
B. block or cluster permutation preserving temporal dependence;
C. block bootstrap of signal-minus-control outcome or success-rate difference.

Requirements:

- use the same event construction for signal and control;
- report event counts for both;
- report effect size and uncertainty, not only p-values;
- apply multiplicity treatment separately;
- state whether the four reported unconditional upside survivors remain supported;
- state whether the zero downside survivors result remains unchanged;
- do not alter the original-replication table retrospectively.

This is a sensitivity layer, not a new framework test.

============================================================
5. SOURCE QA ANOMALY
============================================================

Independent raw inspection found one source-native close-time anomaly in both Binance series:

Date:
2018-02-08

BTCUSDT open time:
2018-02-08T00:00:00Z

BTCUSDT reported raw close time:
approximately 2018-02-08T00:28:14.788Z

ETHBTC reported raw close time:
approximately 2018-02-08T00:28:14.651Z

Expected normal daily close time:
2018-02-08T23:59:59.999Z

Do not silently delete or alter the raw source row.

Add:

SOURCE_ANOMALY_2018_02_08_EARLY_CLOSE

Document:

- raw values;
- whether this reflects a known source-native shortened candle or another condition;
- whether the row is retained;
- one sensitivity rerun excluding this row;
- changes, if any, to every headline range status and key point estimate.

If no headline result moves beyond tolerance, classify:

SOURCE_ANOMALY_NON_MATERIAL

Otherwise classify the affected findings explicitly.

============================================================
6. PACKAGE HYGIENE
============================================================

Remove generated environment noise from the corrected ZIP:

- code/__pycache__/
- *.pyc

Do not include compiled bytecode.

Separate files into:

DETERMINISTIC_REFERENCE_FILES
ENVIRONMENT_REPORT_FILES
ACQUISITION_TIMESTAMP_FILES

Environment-report files may state the current Python version, but they must not be claimed as exact cross-environment parity files.

The corrected ZIP must contain one top-level directory and no hidden credentials.

============================================================
7. REQUIRED TWO-RUN PROOF
============================================================

Before delivery, execute two clean offline reruns from two fresh extracted copies.

Preferably use:

- two separate Python processes;
- different PYTHONHASHSEED values;
- if available, Python 3.12 and Python 3.13.

Both reruns must produce:

- identical deterministic reference files;
- identical extended.json;
- identical 09_CENTRE_TILT_RESULTS.csv;
- identical final classifications;
- identical deterministic output hashes.

Create:

19_CROSS_RUN_PARITY_REPORT.json

Required fields:

{
  "run_a_environment": {},
  "run_b_environment": {},
  "pythonhashseed_a": null,
  "pythonhashseed_b": null,
  "deterministic_files_compared": 0,
  "exact_matches": 0,
  "mismatches": [],
  "excluded_files": [],
  "extended_governance_checks": 0,
  "extended_governance_failures": 0,
  "reference_hash_parity": "PASS|FAIL",
  "cross_run_exact_parity": "PASS|FAIL"
}

Do not set deterministic_rerun_pass=true unless this report passes.

============================================================
8. REQUIRED CORRECTED OUTPUT
============================================================

Create exactly one corrected ZIP:

BTC_RANGE_PULLBACK_REPLICATION_20260722_PATCH1.zip

Include:

- all corrected source and result files;
- complete raw and normalized data;
- all 17 experiments;
- original and unit-matched statistical results;
- frozen reference hashes;
- rerun hashes;
- cross-run parity report;
- updated verifier;
- updated method freeze and manifest;
- source anomaly report;
- no __pycache__ or pyc files.

Provide ZIP SHA-256.

============================================================
9. FINAL STATUS RULES
============================================================

The substantive research status should remain unchanged unless repaired execution produces contrary evidence.

The final JSON must include the previous fields plus:

{
  "deterministic_seed_defect_fixed": true,
  "reference_hash_verification_pass": true,
  "extended_governance_verifier_pass": true,
  "cross_run_exact_parity_pass": true,
  "unit_matched_challenger_completed": true,
  "source_anomaly_2018_02_08_status": "NON_MATERIAL|MATERIAL|UNRESOLVED",
  "compiled_cache_files_removed": true,
  "independent_codex_rerun_ready": true
}

Do not recommend canonical promotion.
Do not create a new test.
Do not activate an alert.
Do not change market state, gates, rebuy or portfolio action.

============================================================
10. FINAL RESPONSE
============================================================

Return:

1. direct link to the corrected ZIP;
2. corrected ZIP SHA-256;
3. old versus corrected file count;
4. exact determinism defect repaired;
5. original 409 check result;
6. extended check result;
7. reference hash parity result;
8. two-run exact parity result;
9. unit-matched statistical sensitivity verdict;
10. source anomaly sensitivity verdict;
11. strict final JSON.

Do not return only prose.
```

## Expected next step after Claude returns

The corrected ZIP must be given to an independent Codex or local runner with a narrow mandate:

```text
EXTRACT
VERIFY PACKAGE HASH
RUN TWO CLEAN OFFLINE COPIES
COMPARE REFERENCE HASHES
VERIFY EXTENDED ASSERTIONS
INSPECT UNIT-MATCHED CHALLENGER
REPORT DIFFERENCES
DO NOT MODIFY RESEARCH
DO NOT MERGE OR PROMOTE
```
