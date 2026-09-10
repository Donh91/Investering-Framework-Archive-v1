# Weekly Cycle Navigator Publication Contract v1.1

Status: ACTIVE_PUBLICATION_CONTRACT
Supersedes for future issues: `2026-08-24__weekly-cycle-navigator-publication-contract-v1.md`
Effective: 2026-09-10

## Purpose

Every Monday Cycle Navigator must be generated only after the final durable Master Monday package for the completed ISO week exists. Cycle Navigator remains a user-facing communication and forecast artifact derived from Master Monday, not a second source of market truth.

## Required Monday order

1. Final completed ISO-week evidence freeze.
2. Final Master Monday calibration, scorecard, operational translation and delivery pointer.
3. Cycle Navigator evaluation of the immediately preceding frozen Cycle Navigator against the just-completed week.
4. Freeze the new Cycle Navigator forecast before any future-week outcome is observed.
5. Materialize all Cycle Navigator variants from the same machine package.
6. Commit and durable-readback all artifacts.

A fixed clock time may be used only as a retry. The primary dependency is the final Master Monday delivery pointer for the target ISO week.

## Required durable artifacts per issue

Under `05_CYCLE_NAVIGATOR/weekly/YYYY/Www/`:

- `CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`
- `CYCLE_NAVIGATOR_SCORECARD.json`
- `CYCLE_NAVIGATOR_FORECAST_FREEZE.json`
- `CYCLE_NAVIGATOR_READABLE.md`
- `CYCLE_NAVIGATOR_X_READY.md`
- `CYCLE_NAVIGATOR_SOURCE_MANIFEST.json`
- `CYCLE_NAVIGATOR_DELIVERY_POINTER.json`

Global pointers/ledgers:

- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
- `05_CYCLE_NAVIGATOR/track_record/CN_TRACK_RECORD_LEDGER.jsonl`

Published X copies remain immutable under `05_CYCLE_NAVIGATOR/published/YYYY/`. `X_READY` is never silently relabelled as `X_PUBLISHED`. An exact published copy is archived only when an external publication receipt or exact confirmed post text exists.

## Required public section order

The weekly analytical forecast remains the primary scoreable part of the public issue. After the current-state / weekly-base-case sections, the publication must present the coming week's price ranges and intraday map before the longer-horizon compass comments.

Required late-section order:

1. Weekly / coming-week price ranges.
2. Intraday map, including Day 1-2, Day 3-4 and Day 5-7 where available.
3. `🔭 2-3 WEEKS` - one very short sentence describing expected direction plus action posture.
4. `🛰️ 4-8 WEEKS` - one very short sentence describing cycle direction plus high-level action compass.
5. Final key takeaway / closing action message.

The 2-3 week and 4-8 week sections are mandatory in future public Cycle Navigator issues unless the source evidence is genuinely unavailable, in which case the section must state `UNAVAILABLE` rather than invent a view.

## Longer-horizon compass semantics

The `2-3 WEEKS` and `4-8 WEEKS` sections are deliberately concise navigation comments, not detailed range forecasts.

Each should normally be one sentence and should combine:

- direction / cycle path;
- the main confirmation or invalidation condition when materially necessary;
- the corresponding high-level posture such as HOLD, PREPARE, SELECTIVE DEPLOYMENT, BROADER DEPLOYMENT or PROTECT CAPITAL.

They must not become long scenario trees, detailed price-target sections or pseudo-precision forecasts.

Example form only:

`🔭 2-3 WEEKS: Selective expansion remains possible - prepare to deploy if breadth and ETH leadership confirm.`

`🛰️ 4-8 WEEKS: Broader alt rotation remains the constructive path - stay positioned, but protect capital if transmission fails.`

Wording must reflect the issue-time evidence and may not be copied mechanically when the state changes.

## Scoring boundary

Weekly price ranges, intraday ranges and explicitly frozen weekly analytical claims remain the primary next-issue evaluation surface.

The `2-3 WEEKS` and `4-8 WEEKS` compass sentences are public directional context and are not included in the normal weekly precision score merely because they are published. They may be archived and later reviewed qualitatively for continuity and calibration, but must not silently inflate or dilute the weekly score.

A future separate prospective long-horizon scoring protocol may score them only if it defines horizon maturity, frozen claim semantics and outcome rules before the observation period.

## Precision and reproducibility

Each issue must freeze the exact forward claims needed for next Monday's evaluation. At minimum this includes any BTC and ETH ranges, structural/regime calls, ETH/BTC conditions, breadth conditions, market-cap transmission state, anticipation windows, scoring method/version and source hashes.

The public continuity score must be stored separately from scientific evidence claims. A communication score cannot be treated as validated model edge. Missing historical artifacts remain `UNAVAILABLE`; they must never be silently reconstructed.

## User-facing retrieval semantics

When a DATA PING/main analysis thread receives:

- `master monday`: resolve the latest final `MASTER_MONDAY_REPORT.md` and present a readable user-facing summary.
- `cycle navigator`: resolve `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` and return `CYCLE_NAVIGATOR_READABLE.md`.
- `cycle navigator til x`: return `CYCLE_NAVIGATOR_X_READY.md` for the current issue, or the immutable exact published artifact when the user explicitly asks for a prior published post.

These are user-facing outputs, not internal variants.

## Authority firewall

Cycle Navigator may summarize, forecast and communicate the final Master Monday state. It may not modify Master Monday evidence, canonical thresholds, portfolio execution authority, market-rule semantics or retrospective outcomes. Research/shadow evidence may be mentioned only with its recorded authority and may not be promoted by publication prose.
