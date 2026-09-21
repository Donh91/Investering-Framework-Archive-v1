# Master Monday current-routing notice

**Status:** NAVIGATION_ONLY  
**Current routing owner:** `../../00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`

## Current production route

For present-day Master Monday state, start from:

```text
../../LATEST_OPERATIONS_DASHBOARD.json
../../LATEST_HANDOFF.json
```

Then follow the exact autonomous weekly output pointer, target path, hash and receipt named there.

Manual user-submitted DATA PING is not a prerequisite for current Master Monday production.

## Legacy filename warning

`latest_master_monday.json` is preserved for historical compatibility and older lineage. It currently represents an older architecture generation and **must not be treated as the current production pointer merely because the filename says `latest`**.

Likewise, historical files such as `*_data_ping_derived_*` correctly preserve lineage for their frozen weeks but do not define today's upstream architecture.

An old Master Monday or DATA PING artifact becomes current only if a current operational routing surface explicitly names it.

## Invariant

```text
CURRENT MASTER MONDAY = CURRENT AUTONOMOUS POINTER CHAIN.
HISTORICAL `latest_master_monday.json` = LEGACY UNLESS CURRENT ROUTING EXPLICITLY NAMES IT.
```

## Cycle Navigator precision consumer rule

When Master Monday, calibration, a website consumer, or a chat asks for the **public Cycle Navigator score/frozen ranges**, do not infer the public issue from the weekly machine `issue_number`.

Resolve:

```text
../../05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json
../../05_CYCLE_NAVIGATOR/CANONICAL_SCORE_AND_LINEAGE.md
```

Then follow the exact `latest_completed_score.scorecard_path`.

Reason: the September 2026 migration left the machine issue counter one ahead of the actually published public CN series. Joining by issue number alone can pair the wrong forecast week, falsely report published ranges as missing, or combine scores from different forecast lineages.

Master Monday provides outcome evidence. It must not redefine public CN identity.

