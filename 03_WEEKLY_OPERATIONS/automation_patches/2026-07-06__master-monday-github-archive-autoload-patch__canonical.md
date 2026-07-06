# Master Monday GitHub Archive Autoload Patch

**Dato:** 2026-07-06  
**Status:** CANONICAL  
**Område:** Master Monday, GitHub Archive Sync, range ledger, Forecast Ledger, weekly automation  
**Run context:** First Master Monday after GitHub was implemented as extended data archive for the Investering framework.

---

## Executive conclusion

The first GitHub-backed Master Monday exposed a retrieval gap, not a market-logic gap.

The framework already required GitHub-first reading and verified weekly range loading, but the weekly range ledger was not stored behind a stable machine-readable pointer before the run.

The correction is now active:

```text
Master Monday must load range and forecast pointers before generating output.
Master Monday raw output must be archived every week.
The new weekly forecast must be written to Forecast Ledger every week.
The latest pointers must be updated after every run.
```

---

## Root cause fixed

Previous problem:

```text
Verified weekly range existed in project context, but was not automatically discoverable as a canonical GitHub file.
```

Correct status going forward:

```text
If actual range exists but prior forecast ledger is missing:
ACTUAL_RANGE_VERIFIED
FORECAST_LEDGER_MISSING
RANGE_SCORE_PARTIAL
```

Wrong status:

```text
PRICE_UNVERIFIED
```

---

## New required pre-flight load order

Every Master Monday run must now load in this order:

```text
0. Read 00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
1. Read 00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md if routing or precedence is unclear
2. Identify highest active DATA PING version
3. Load active DATA PING V* operational handoff
4. Load data/canonical/latest_valid.json
5. Load 03_WEEKLY_OPERATIONS/range_audits/latest_verified_weekly_range.json
6. Load 03_WEEKLY_OPERATIONS/forecast_ledger/latest_forecast_ledger.json
7. Load 03_WEEKLY_OPERATIONS/shadow_ledger/latest_shadow_ledger_manifest.json
8. Load ETF/Farside ledger
9. Load FRED/macro shadow status
10. Load latest Master Monday pointer
11. Generate Master Monday
12. Write raw Master Monday archive file
13. Write/update Forecast Ledger for the new week
14. Update latest pointers
15. Append backbone_history.csv
16. Update CANONICAL_INDEX.md when operationally important
```

---

## Files created by this patch

```text
03_WEEKLY_OPERATIONS/range_audits/2026-07-05__weekly-range-2026-w27__verified.md
03_WEEKLY_OPERATIONS/range_audits/latest_verified_weekly_range.json
03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-06__forecast-ledger-2026-w28__official.md
03_WEEKLY_OPERATIONS/forecast_ledger/latest_forecast_ledger.json
03_WEEKLY_OPERATIONS/master_monday/2026-07-06__master-monday-2026-w28__raw.md
03_WEEKLY_OPERATIONS/master_monday/latest_master_monday.json
03_WEEKLY_OPERATIONS/shadow_ledger/latest_shadow_ledger_manifest.json
data/canonical/latest_valid.json
data/canonical/backbone_history.csv
```

---

## Weekly archive rule

Each weekly Master Monday must be archived as:

```text
03_WEEKLY_OPERATIONS/master_monday/YYYY-MM-DD__master-monday-YYYY-wWW__raw.md
```

Each weekly forecast ledger must be archived as:

```text
03_WEEKLY_OPERATIONS/forecast_ledger/YYYY-MM-DD__forecast-ledger-YYYY-wWW__official.md
```

Each verified weekly range must be archived as:

```text
03_WEEKLY_OPERATIONS/range_audits/YYYY-MM-DD__weekly-range-YYYY-wWW__verified.md
```

---

## Automation requirement

A weekly automation must run Master Monday with this instruction:

```text
Run Master Monday v3.1 or newest canonical successor.
Use GitHub-first load order.
Do not generate final output before latest range and forecast ledgers have been checked.
Archive the raw Master Monday output in GitHub.
Write/update the new Forecast Ledger.
Update latest_valid.json, latest_master_monday.json, latest_forecast_ledger.json, latest_verified_weekly_range.json if new actuals exist, latest_shadow_ledger_manifest.json and backbone_history.csv.
If any required source is missing, write explicit missing status and continue conservatively.
```

---

## Run status impact

Before patch:

```text
MANUAL_BACKFILL_PASS due missing pointer files.
```

After patch target:

```text
AUTO_PASS possible if GitHub is accessible, latest pointers are loaded, verified ranges are available and shadow ledger is at least checked.
```

---

## Final rule

The framework brain is not allowed to rely only on chat memory for weekly ranges anymore.

```text
Verified ranges must exist as stable GitHub files and latest pointers before precision scoring.
```
