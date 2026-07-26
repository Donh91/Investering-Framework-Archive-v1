# Claude Prompt: GCBLO Reproduction Environment and Release-Parity Patch

**Dato:** 2026-07-25  
**Status:** OPERATIONAL_PROMPT  
**Område:** Claude/Fable deterministic reproduction repair  
**Primary folder:** `07_PROMPTS_AND_AGENTS/claude/`  
**Related folders:** `08_SOURCE_MATERIAL/claude/`, `06_RESEARCH_LAB/audit_summaries/`  
**Depends on:** GCBLO full experiment package and independent rerun QA

```text
GCBLO RECONSTRUCTED CHALLENGER
TARGETED REPRODUCTION ENVIRONMENT AND RELEASE-PARITY PATCH

ROLE

You are Claude/Fable acting only as the original package maintainer and deterministic replication engineer.

The package:

GCBLO repro pack 20260725.zip

has been independently inspected and executed.

Confirmed independently:

- ZIP integrity passes;
- available source-receipt hashes match 11 local payloads;
- the code executes on Python 3.13.5, pandas 2.2.3 and NumPy 2.3.5;
- two fresh runs in that environment are byte-identical;
- core negative conclusions remain stable;
- no configuration passes the 45-week resemblance bar;
- best score remains 106.7 weeks;
- arctangent crossing identity remains true, n=16;
- the halving mask remains 29 raw crossings to 7;
- median unselected strategy Sharpe remains approximately 0.58;
- approximately 9 percent beat the 40-week moving-average baseline.

The release is not yet exact-output reproducible across environments.

Independent rerun differences include:

- complete-signal configurations: packaged 3,240 versus rerun 3,242;
- top-50 RE_FIRED: packaged 18 percent versus rerun 16 percent;
- 128 score rows changed;
- 14 miss-count rows changed;
- 11 stage-state rows changed;
- packaged grid_all.csv SHA-256 differs from the rerun SHA-256.

Do not run a new broad research mission.
Do not add indicators, components, thresholds or BTC outcome hypotheses.
Do not alter canonical state, gates, rebuy or portfolio action.
Do not weaken or strengthen conclusions merely to match the prior report.

============================================================
1. FREEZE THE ORIGINAL RELEASE ENVIRONMENT
============================================================

Recover and document the exact environment that generated the packaged result files.

Create:

00_PATCH_EXECUTIVE_VERDICT.md
01_ORIGINAL_ENVIRONMENT.json
02_PATCH_ENVIRONMENT.json
requirements-lock.txt

Record at minimum:

- Python version;
- pandas version;
- NumPy version;
- operating system and architecture;
- locale and timezone;
- BLAS or numerical backend where available;
- source-file hashes;
- code-file hashes;
- command line;
- environment variables affecting determinism.

Do not infer dependency versions. If the original environment cannot be recovered exactly, state:

ORIGINAL_RELEASE_ENVIRONMENT_UNRECOVERED

============================================================
2. RECONCILE THE GRID COUNT
============================================================

The report states a 4,800-configuration frozen grid.

The explicit Cartesian product in the packaged code appears to be:

5 change horizons
x 4 z-score windows
x 5 EMA lengths
x 4 weight families
x 2 currency treatments
x 3 RRP samplings
x 5 threshold quantiles
= 6,000 theoretical combinations before the shape gate.

Produce a machine-readable count ledger containing:

- theoretical Cartesian product;
- intentionally collapsed axes;
- duplicate specifications removed;
- invalid configurations skipped;
- shape-gated configurations;
- complete-signal configurations;
- final scored configurations.

Do not preserve the 4,800 claim unless the count can be derived from the final packaged method.

============================================================
3. REGENERATE ALL RESULTS FROM FINAL CODE AND DATA
============================================================

Starting from a clean extraction, regenerate:

results/grid_all.csv
results/grid_pass.csv
results/sharpe_dist.json
all reported tables and summary values

The release report must be generated from these final outputs, not manually copied from an earlier environment.

Reconcile explicitly:

- 3,240 versus 3,242 complete-signal configurations;
- 18 percent versus 16 percent top-50 RE_FIRED;
- every changed best-50 anchor-error median;
- any changed stage-state count;
- any changed score or miss count.

Where values change, update the report honestly.

============================================================
4. ADD FROZEN REFERENCE HASHES
============================================================

Create:

18_REFERENCE_HASHES.sha256
18_RERUN_HASHES.sha256

The reference manifest must be frozen when the patched release is built and must never be overwritten by a normal rerun.

The rerun manifest must be regenerated after execution.

Cover every deterministic code, data and output file.

List separately all intentionally excluded volatile files and the reason for exclusion.

============================================================
5. ADD AN EXECUTABLE VERIFIER
============================================================

Create:

code/verify_release.py

It must verify:

- source payload hashes;
- code hashes;
- row counts;
- theoretical and post-gate grid counts;
- complete-signal count;
- best resemblance score;
- resemblance PASS count;
- arctangent crossing identity and n;
- raw versus masked crossing counts;
- median unselected Sharpe;
- share beating hold;
- share beating 40-week moving average;
- top-50 current-state counts;
- blocked-file classification;
- reference-output hashes.

Report separately:

SOURCE_CHECKS
METHOD_CHECKS
RESULT_CHECKS
REFERENCE_HASH_CHECKS
TOTAL_CHECKS
TOTAL_FAILURES

The verifier must fail on a mismatch. It may not regenerate the reference manifest before checking it.

============================================================
6. FIX THE KRAKEN RECEIPT METADATA
============================================================

The current receipt records:

KRAKEN_BTC_W n_rows = 0

although the payload contains weekly rows.

Correct the row count using a deterministic definition and document whether the header row is included.

Do not alter the valid payload hash.

============================================================
7. CROSS-ENVIRONMENT PARITY
============================================================

Run from at least two clean extracted directories.

Required when available:

- original recovered environment;
- Python 3.13.5, pandas 2.2.3, NumPy 2.3.5 challenger environment;
- different PYTHONHASHSEED values.

Create:

19_CROSS_ENVIRONMENT_PARITY_REPORT.json

with:

{
  "original_environment_recovered": false,
  "environments": [],
  "deterministic_files_compared": 0,
  "exact_matches": 0,
  "mismatches": [],
  "result_field_differences": [],
  "reference_hash_parity": "PASS|FAIL",
  "cross_environment_exact_parity": "PASS|FAIL|ENVIRONMENT_BOUND",
  "core_conclusion_parity": "PASS|FAIL"
}

If exact parity is impossible because the method is dependency-sensitive, freeze and declare one authoritative environment:

ENVIRONMENT_BOUND_REPRODUCIBLE_RELEASE

Do not claim general cross-environment parity.

============================================================
8. PRESERVE THE GOVERNANCE CONCLUSIONS
============================================================

The following conclusions currently survive both the packaged and independent rerun outputs:

- original GCBLO formula not recovered;
- zero specifications pass the resemblance bar;
- re-entry side is weaker than exit side;
- arctangent is cosmetic for mapped crossing dates;
- halving mask performs most signal selection;
- current re-entry state fails specification-dispersion survival;
- the unselected family does not beat simple baselines;
- GCBLO remains WATCH-only with zero execution authority.

Retain these only if the repaired outputs continue to support them.

If a repaired value changes a conclusion, report the change and the exact cause.

============================================================
9. REQUIRED OUTPUT
============================================================

Create exactly one patched release:

GCBLO_REPRO_PACK_20260725_PATCH1.zip

Return:

1. direct ZIP attachment;
2. ZIP SHA-256;
3. exact file count;
4. original environment status;
5. authoritative patched environment;
6. grid-count reconciliation;
7. 3,240 versus 3,242 reconciliation;
8. 18 versus 16 percent reconciliation;
9. Kraken row-count correction;
10. verifier result;
11. reference-hash result;
12. cross-environment parity status;
13. strict final JSON.

Final JSON:

{
  "research_id": "GCBLO_RECONSTRUCTED_CHALLENGER_20260725_PATCH1",
  "original_gcblo_recovered": false,
  "original_release_environment_recovered": false,
  "authoritative_environment_frozen": true,
  "grid_count_reconciled": true,
  "complete_signal_count_reconciled": true,
  "current_state_count_reconciled": true,
  "kraken_receipt_row_count_fixed": true,
  "reference_hash_verification_pass": true,
  "executable_verifier_pass": true,
  "same_environment_exact_parity": true,
  "cross_environment_status": "PASS|ENVIRONMENT_BOUND|FAIL",
  "core_conclusion_parity": "PASS|FAIL",
  "gcblo_sensor_promotion": false,
  "current_reentry_permission": false,
  "market_state_change": false,
  "gate_change": false,
  "rebuy_change": false,
  "portfolio_action": false,
  "package_sha256": null
}

No canonical promotion.
No new test.
No new engine.
No live signal or portfolio action.
```
