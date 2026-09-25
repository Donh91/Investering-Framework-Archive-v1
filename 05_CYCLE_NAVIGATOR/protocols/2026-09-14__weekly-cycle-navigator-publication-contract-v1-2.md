# Weekly Cycle Navigator Publication Contract v1.2

Status: ACTIVE_PUBLICATION_CONTRACT  
Supersedes for future issues: `2026-09-10__weekly-cycle-navigator-publication-contract-v1-1.md`  
Effective: 2026-09-14

## Purpose

Cycle Navigator is a continuing public forecast series derived from the final durable Master Monday package. It is not a second source of market truth.

This version adds a binding X-publication continuity rule so a new weekly X post is never treated as a fresh standalone format when a prior confirmed published Cycle Navigator exists.

## Required Monday order

1. Final completed ISO-week evidence freeze.
2. Final Master Monday calibration, scorecard, operational translation and delivery pointer.
3. Evaluate the immediately preceding frozen Cycle Navigator against the completed week.
4. Freeze the new Cycle Navigator forecast before future-week outcomes are observed.
5. Materialize machine, readable and X-ready variants from the same canonical package.
6. Commit and durable-readback all artifacts.

## Durable artifacts

Under `05_CYCLE_NAVIGATOR/weekly/YYYY/Www/`:

- `CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`
- `CYCLE_NAVIGATOR_SCORECARD.json`
- `CYCLE_NAVIGATOR_FORECAST_FREEZE.json`
- `CYCLE_NAVIGATOR_READABLE.md`
- `CYCLE_NAVIGATOR_X_READY.md`
- `CYCLE_NAVIGATOR_SOURCE_MANIFEST.json`
- `CYCLE_NAVIGATOR_DELIVERY_POINTER.json`

Published X copies remain immutable under `05_CYCLE_NAVIGATOR/published/YYYY/`. `X_READY` must never be silently relabelled as `X_PUBLISHED`.

## Binding X-series continuity rule

The Cycle Navigator X publication is one continuous series.

For any request equivalent to `Cycle Navigator til X`, `CN til X`, `CN til publicering`, or `send denne uges CN til X`:

1. Resolve the latest **actually published and archived** Cycle Navigator post under `05_CYCLE_NAVIGATOR/published/YYYY/`.
2. Treat that exact published post as the canonical **style, structure, tone, rhythm, numbering and narrative-continuity baseline** for the new public issue.
3. Resolve the current week's canonical machine package, scorecard, forecast freeze, readable output and `X_READY` artifact for the new week's facts, scoring and forecast evidence.
4. Build the new public post **forward from the prior published post**. Preserve the recognizable publication format and story progression unless the user explicitly requests a format change.
5. `CYCLE_NAVIGATOR_X_READY.md` is a current-evidence/content input. It is **not** the default publication-style authority when a prior confirmed published post exists.
6. Current canonical evidence always overrides stale prose. Continuity must never carry forward obsolete facts, unsupported precision claims, stale ranges or invalid forecasts.
7. Historical published scores may only be repeated when they remain supported under the current scoring/publication rules. Unsupported legacy claims must not be preserved merely for stylistic continuity.
8. After the user confirms the new X post was actually published, archive the exact published text immutably under `05_CYCLE_NAVIGATOR/published/YYYY/`. That archived post becomes the baseline for the following issue.

Fallback: only when no confirmed prior published X artifact exists may the current `CYCLE_NAVIGATOR_X_READY.md` act as the initial publication-format baseline.

This rule applies across all user-facing threads, including Kompas/Handlekompas threads. Starting a new chat or thread must never reset the public series.

## Public section continuity

The prior published issue controls the recognizable public layout. Within that continuity, preserve the analytical order when evidence is available:

1. prior-week precision/review;
2. current state;
3. market/altcoin cycle progression;
4. main signal/confirmation test;
5. this-week base case/action posture;
6. weekly price ranges and intraday map when canonically available;
7. `2-3 WEEKS` concise direction + action;
8. `4-8 WEEKS` concise cycle direction + action;
9. final takeaway.

If a required evidence field is unavailable, state `UNAVAILABLE` / `NOT PUBLISHED` rather than inventing a value.

## Scoring boundary

Weekly ranges, intraday ranges and explicitly frozen weekly analytical claims remain the primary next-issue evaluation surface. Longer-horizon 2-3 week and 4-8 week compass statements are navigation context unless separately pre-registered for scoring.

Public continuity/style is not evidence of model edge and must remain separate from scientific precision scoring.

## User-facing retrieval semantics

- `master monday`: resolve the latest final `MASTER_MONDAY_REPORT.md` and present the readable summary.
- `cycle navigator`: resolve `LATEST_CYCLE_NAVIGATOR_POINTER.json` and return the current readable issue.
- `cycle navigator til x` / `CN til X` / `CN til publicering`: resolve the latest confirmed published X artifact first as the continuity baseline, then use the current canonical CN package and X-ready evidence to produce the next issue in that continuing format.
- a request for a prior published post: return the immutable archived published artifact exactly.

## Authority firewall

Cycle Navigator may summarize, forecast and communicate the final Master Monday state. It may not modify Master Monday evidence, canonical thresholds, portfolio-execution authority, market-rule semantics or retrospective outcomes. X publication style can never override canonical market evidence.

Typed 2-3 week and 4-8 week `action_posture` fields remain navigation proposals with no independent Main-Framework action permission. Official Compass may expose a proactive `BUY` or `PREPARE_BUY` posture only up to the current Main-Framework permission ceiling; otherwise the action must fail closed while the frozen Cycle Navigator state/direction remains intact.
