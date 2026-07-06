# MM CN CONTROL MATRIX 2026-07-06

Status: Active control matrix
Date added: 2026-07-06
Applies to: Master Monday, Cycle Navigator, verified actuals, Forecast Ledger

## Purpose

This file is the operational bridge between the public Cycle Navigator archive and the Master Monday decision archive.

Read this before using historical CN or MM records.

## Source files

- canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/PUBLISHED_X_POST_REGISTER.md
- canonical-project-archive/07_MASTER_MONDAY/MASTER_MONDAY_REGISTER.md
- canonical-project-archive/03_FORECAST_LEDGER/VERIFIED_WEEKLY_RANGES_2026_Q2.md

## Control matrix

| CN | CN date | Public CN file | Public CN status | MM run file | MM status | Actuals status | Score source | Next action |
|---|---|---|---|---|---|---|---|---|
| #14 | 2026-06-29 | CN_014_PUBLISHED_X_POST_2026-06-29.md | FULL_TEXT_ARCHIVED | runs/MM_2026-06-29.md | RECONSTRUCTED | PARTIAL / public score only | Public CN post | Add verified week 26/27 actuals if canonical source exists |
| #13 | 2026-06-22 | CN_013_PUBLISHED_X_POST_2026-06-22.md | FULL_TEXT_ARCHIVED | runs/MM_2026-06-22.md | RECONSTRUCTED | VERIFIED_WEEK_25 | Public CN + verified actuals | Keep |
| #12 | 2026-06-15 | CN_012_PUBLISHED_X_POST_2026-06-15.md | FULL_TEXT_ARCHIVED | runs/MM_2026-06-15.md | RECONSTRUCTED | VERIFIED_WEEK_24 | Public CN + verified actuals | Keep |
| #11 | 2026-06-08 | CN_011_PUBLISHED_X_POST_2026-06-08.md | FULL_TEXT_ARCHIVED | runs/MM_2026-06-08.md | RECONSTRUCTED | VERIFIED_WEEK_23 | Public CN + verified actuals | Keep |
| #10 | 2026-06-01 | MISSING | GAP | TBD | GAP | UNKNOWN | Missing | Find public CN #10 text |
| #9 | 2026-05-25 | CN_009_PUBLISHED_X_POST_2026-05-25.md | FULL_TEXT_ARCHIVED | runs/MM_2026-05-25.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #8 | 2026-05-18 | CN_008_PUBLISHED_X_POST_2026-05-18.md | FULL_TEXT_ARCHIVED | runs/MM_2026-05-18.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #7 | 2026-05-11 | CN_007_PUBLISHED_X_POST_2026-05-11.md | FULL_TEXT_ARCHIVED | runs/MM_2026-05-11.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #6 | 2026-05-04 | MISSING | GAP | TBD | GAP | UNKNOWN | Missing | Find public CN #6 text |
| #5 | 2026-04-27 | CN_005_PUBLISHED_X_POST_2026-04-27.md | FULL_TEXT_ARCHIVED | runs/MM_2026-04-27.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #4 | 2026-04-20 | CN_004_PUBLISHED_X_POST_2026-04-20.md | FULL_TEXT_ARCHIVED | runs/MM_2026-04-20.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #3 | 2026-04-14 | CN_003_PUBLISHED_X_POST_2026-04-14_CHUNK_01.md to CHUNK_03.md | FULL_TEXT_ARCHIVED | runs/MM_2026-04-14.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Keep chunked archive |
| #2 | 2026-04-07 | CN_002_PUBLISHED_X_POST_2026-04-07.md | FULL_TEXT_ARCHIVED | runs/MM_2026-04-07.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Add actuals if found |
| #1 | 2026-03-30 | CN_001_PUBLISHED_X_POST_2026-03-30.md | FULL_TEXT_ARCHIVED | runs/MM_2026-03-30.md | RECONSTRUCTED | PUBLIC_POST_ONLY | Public CN post | Keep |

## Governance rules

1. Public CN file is the public record.
2. Master Monday file is the decision record.
3. RECONSTRUCTED does not mean original raw Master Monday was found.
4. Verified actuals override public score commentary when measuring model accuracy.
5. Public score remains historical public record and should not be silently rewritten.
6. Gaps must stay visible until source text is found.
7. Do not invent missing CN #6 or CN #10.

## Current gaps

- CN #10 / 2026-06-01
- CN #6 / 2026-05-04

## Highest-confidence verified actuals currently linked

- CN #13 uses Week 25 verified actuals.
- CN #12 uses Week 24 verified actuals.
- CN #11 uses Week 23 verified actuals.

## Operating instruction for future runs

Before producing or scoring a new Cycle Navigator output, read:

1. this control matrix
2. the published CN register
3. the Master Monday register
4. the verified weekly actuals file
5. the highest active DATA PING version

## Update log

- 2026-07-06: Created.