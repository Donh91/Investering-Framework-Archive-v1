# DAILY RAW CAPTURE LOGS v1

Status: ACTIVE SHADOW INPUT AFTER MERGE

## Purpose

Capture verified owner-data five times per day so the framework can study intraday sequence, deterioration, recovery attempts, leverage changes, breadth survival and pre-pullback behavior without manual DATA PING feeding.

## Schedule, Europe/Copenhagen

- 06:13
- 10:47
- 15:22
- 19:38
- 23:11

The schedule intentionally avoids exact hour boundaries.

## Storage

Raw owner payloads are uploaded as GitHub Actions artifacts with seven-day retention.

Only compact permanent indexes are committed to Git:

- source status
- retrieval/freeze metadata found in receipts
- file hashes
- file sizes
- row/constituent counts where available
- membership hashes where available
- artifact/run linkage
- calibration eligibility

Images, charts and raw bulk payloads must not be committed here.

## Authority

These captures are not canonical DATA PINGs. They are shadow observations and calibration inputs.

They may not:

- change framework state;
- change model weights;
- create portfolio action;
- overwrite forecasts;
- infer missing data;
- convert source failure to zero.

## Weekly bridge

Every Sunday at 23:45 Europe/Copenhagen, the weekly builder reads the compact capture indexes and produces:

`03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json`

The pointed weekly pack is an explicit input for:

- RAW weekly calibration;
- Forecast Ledger evaluation;
- Master Monday preparation;
- Specialist weekly review.

Master Monday and RAW must preserve disagreement and missingness. Capture count is evidence density, not market confirmation.

## Promotion path

Automated captures run in parallel with canonical DATA PING. Replacement or promotion requires a separate parity program and explicit governance approval.
