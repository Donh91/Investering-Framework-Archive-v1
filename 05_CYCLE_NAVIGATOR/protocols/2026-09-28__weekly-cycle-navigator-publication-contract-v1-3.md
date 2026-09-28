# Weekly Cycle Navigator Publication Contract v1.3

Status: ACTIVE_PUBLICATION_CONTRACT
Supersedes for future issues: `2026-09-14__weekly-cycle-navigator-publication-contract-v1-2.md`
Effective: 2026-09-28

## Purpose

Cycle Navigator is a continuing public forecast series derived from the final durable Master Monday package. It is not a second source of market truth.

v1.3 preserves the public-series continuity and scoring boundaries from v1.2 and adds a binding scroll-first X presentation standard.

Binding public style template:

`../templates/2026-09-28__cycle-navigator-x-scroll-first-template__canonical.md`

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

Confirmed published X copies remain immutable under `05_CYCLE_NAVIGATOR/published/YYYY/`. The user is the authority on publication status; no independent X verification is required.

Approved pre-publication copies may also be archived with `APPROVED` status. They become `PUBLISHED_CONFIRMED_BY_USER` only when the user states that the exact version was published.

`X_READY` and `X_APPROVED` must never be silently relabelled as `X_PUBLISHED` without that user confirmation.

## Binding X-series continuity rule

The Cycle Navigator X publication is one continuous series.

For any request equivalent to `Cycle Navigator til X`, `CN til X`, `CN til publicering`, or `send denne uges CN til X`:

1. Resolve the latest actually published and archived Cycle Navigator post.
2. Use that post as the narrative-continuity baseline.
3. Resolve the current canonical machine package, scorecard, forecast freeze, readable output and X-ready artifact for facts, scoring and forecast evidence.
4. Apply the binding scroll-first public template for presentation density and section construction.
5. Build the new public post forward from the established public narrative; do not restart the format or introduce internal framework novelty without public need.
6. Current canonical evidence always overrides stale prose.
7. Historical public scores may only be repeated when supported under the current public scoring rules.
8. The user's publication statement is authoritative. Do not require independent X confirmation. When the user says the exact version was published, archive that version immutably as `X_PUBLISHED`, record `PUBLISHED_CONFIRMED_BY_USER`, and advance the public-series identity.

Fallback: when no confirmed prior published X artifact exists, use the closest approved/published historical public post for narrative continuity while public issue identity remains governed by confirmed publication state.

## Scroll-first public style

The public post must be easy to scan on a phone.

### Precision section

Prior-week precision is intentionally the most explicit section.

When evidence exists, show:
- market/cycle structure score;
- BTC price precision;
- ETH price precision;
- established combined price precision;
- weekly BTC and ETH Forecast -> Actual;
- Day 1-2 / Day 3-4 / Day 5-7 precision;
- concise intraday Forecast -> Actual rows;
- one short explanation of the main hit/miss and adjustment.

Public precision must continue using the established public scoring family. Internal precision expansion must not replace, rename, delete or silently alter the public score presentation.

### All other sections

Keep them materially shorter than the precision section.

Prefer compact paragraphs and data/action rows instead of many standalone explanatory sentences.

Do not surface new internal diagnostics, shadow metrics, research terminology or experimental time-window labels merely because they exist internally. Public vocabulary should evolve slowly and only when it extends the established public narrative or is explicitly approved.

## Public section continuity

When evidence is available, use:

1. prior-week precision/review;
2. what matters now;
3. market cycle timeline;
4. main signal/confirmation test;
5. this-week base case/action posture;
6. weekly price ranges and intraday map;
7. 2-3 WEEKS concise direction + action;
8. 4-8 WEEKS concise cycle direction + action;
9. final takeaway.

The established public rotation narrative remains the default continuity frame when supported:

`ETH -> large caps -> breadth -> midcaps -> small/micro`

A new internal analytical dimension does not become a new public section automatically.

## Scoring boundary

Weekly ranges, intraday ranges and explicitly frozen weekly analytical claims remain the primary next-issue evaluation surface.

Longer-horizon 2-3 week and 4-8 week statements are navigation context unless separately pre-registered for scoring.

Public continuity/style is not evidence of model edge and remains separate from scientific precision scoring.

## User-facing retrieval semantics

- `master monday`: resolve the latest final Master Monday report.
- `cycle navigator`: resolve `LATEST_CYCLE_NAVIGATOR_POINTER.json` and return the current readable issue.
- `cycle navigator til x` / `CN til X` / `CN til publicering`: resolve public-series identity, latest confirmed public narrative, current canonical evidence, then render with the scroll-first public template.
- prior published post request: return the immutable archived published artifact exactly.

## Authority firewall

Cycle Navigator may summarize, forecast and communicate final framework state. It may not modify Master Monday evidence, canonical thresholds, portfolio-execution authority, market-rule semantics or retrospective outcomes.

X publication style can never override canonical market evidence.

Typed 2-3 week and 4-8 week action postures remain navigation proposals with no independent Main-Framework execution authority.
