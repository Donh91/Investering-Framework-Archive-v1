# Decision Ledger — Private GitHub Source-Lineage Upgrade

**Date:** 2026-07-12  
**Input:** 21-row recovery ledger + targeted private-GitHub offline snapshot  
**Output rows:** 22  
**Rows upgraded from `INACCESSIBLE_PRIOR_THREAD` to `OFFLINE_GITHUB_SNAPSHOT_BACKED`:** 13  
**M3-eligible rows after upgrade:** 13

## Result

The July 8–11 pullback-edge event window is now materially source-backed through actual private-GitHub canonical files:

- `02_DATA_PING/live_state_handover/2026-07-08__pullback-edge-20260708-01__event-ledger.md`
- `02_DATA_PING/live_state_handover/2026-07-10__active-gate-and-edge-event-registry__canonical.md`
- `02_DATA_PING/live_state_handover/2026-07-11__pullback-edge-20260708-01__72h-event-close-receipt.md`

The event ledger provides exact run timestamps, sensor/framework state transitions and alert status. The close receipt provides the framework event-close decision and matured 72H outcome.

## Eligibility treatment

- Point-in-time rows with exact timestamps and explicit framework state/acceptance are marked `eligible_for_M3=YES`.
- The 2026-07-10 17:29:31Z row remains `NO` because the file explicitly says framework acceptance was retrospective.
- The separate 22:33:53Z first-close row remains inaccessible because that exact run is not present in the exported canonical event files.
- Earlier April/May/July 3 rows remain inaccessible until their original sources are exported.

## Current M3 status

`M3_LEDGER_COVERAGE_READY: NO`

Reason: the newly source-backed rows are concentrated in one short event sequence. They unlock event-level M3 analysis and schema validation, but not a cross-regime challenger tournament.

## New intermediate status

`M3_JULY_8_11_EVENT_WINDOW_SOURCE_BACKED: YES`

No scoring or rule promotion was performed.
