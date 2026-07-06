# Index Addendum - 2026-07-06

Status: CANONICAL_INDEX_ADDENDUM

New pointers:

- data/canonical/latest_valid.json
- data/canonical/backbone_history.csv
- 03_WEEKLY_OPERATIONS/master_monday/latest_master_monday.json
- 03_WEEKLY_OPERATIONS/range_audits/latest_verified_weekly_range.json
- 03_WEEKLY_OPERATIONS/forecast_ledger/latest_forecast_ledger.json
- 03_WEEKLY_OPERATIONS/shadow_ledger/latest_shadow_ledger_manifest.json

New archives:

- 03_WEEKLY_OPERATIONS/master_monday/2026-07-06__master-monday-2026-w28__raw.md
- 03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-06__forecast-ledger-2026-w28__official.md
- 03_WEEKLY_OPERATIONS/range_audits/2026-07-05__weekly-range-2026-w27__verified.md
- 03_WEEKLY_OPERATIONS/automation_patches/2026-07-06__master-monday-github-archive-autoload-patch__canonical.md

Load order patch:

Read latest_valid.json, range pointer, forecast pointer, shadow manifest and latest Master Monday pointer before producing the next weekly run.
