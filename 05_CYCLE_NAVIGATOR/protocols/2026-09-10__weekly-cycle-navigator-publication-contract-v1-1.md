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

## Internal longer-horizon analysis

The concise X output must not constrain the internal Cycle Navigator analysis.

The internal machine/readable package should contain a materially more detailed 2-3 week and 4-8 week horizon assessment when evidence permits. Internal analysis may include:

- base, bull and bear paths;
- expected rotation sequencing;
- ETH/BTC, breadth, BTC dominance, liquidity, leverage and macro transmission conditions;
- confirmation and invalidation logic;
- market-cap ladder implications;
- confidence and uncertainty;
- high-level deployment / capital-protection posture.

The internal 2-3 week and 4-8 week analysis is research/navigation context and must remain traceable to issue-time evidence. It may be detailed even though the X version is compressed to one short sentence per horizon.

## Longer-horizon public compass semantics

The `2-3 WEEKS` and `4-8 WEEKS` sections in `CYCLE_NAVIGATOR_X_READY.md` are deliberately concise navigation comments, not detailed range forecasts.

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

The public `2-3 WEEKS` and `4-8 WEEKS` compass sentences are not included in the normal week-to-week precision score. Their purpose is navigation, not forced weekly scoring before those horizons have matured.

Longer-horizon claims should still be frozen and retained internally so that the framework can later evaluate them at an appropriate checkpoint without hindsight rewrite.

## Longer-horizon checkpoint review

A later checkpoint publication may look back across matured 2-3 week and 4-8 week calls and comment on what actually happened.

This is separate from the normal weekly scorecard.

When used publicly, the checkpoint may include a distinct `LONGER-HORIZON PRECISION` or equivalent highlight, but only after the relevant horizon has matured and only against the exact frozen issue-time claim. It must not retroactively alter prior X posts or mix immature long-horizon calls into the weekly precision number.

The checkpoint is therefore a separate retrospective calibration/highlight layer:

- weekly precision = weekly ranges / intraday / frozen weekly analytical calls;
- longer-horizon checkpoint = matured 2-3 week and 4-8 week directional/compass calls;
- the two may be shown together, but their scores or judgments remain clearly separated.

A future mechanical long-horizon scoring protocol may be added if desired, provided horizon maturity, claim semantics and outcome rules are defined prospectively before use.

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
