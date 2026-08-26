# Action Compass owner simplification

**Date:** 2026-08-26
**Status:** PROPOSED_CANONICAL_CHANGE

## Decision

- Three-Horizon Action Compass v1.1 is the sole current Main-Framework decision vocabulary for DATA PING and RAW interpretation.
- Lane-3 warning and action are independent. No warning mechanically authorizes `REDUCE` or `EXIT`.
- The historical E0-E7 Exit Ladder is `RETIRED_UNIMPLEMENTED`; its header-only CSV remains provenance and receives no rows.
- The existing T9 Chief Reproducibility owner will consume prospective Action Compass receipts after implementation. No new test ID is created.
- One bounded immutable receipt and five separate outcome-sidecar horizons are authorized under the existing owner for implementation in a follow-on pull request.

## Boundaries

```text
new engine: NO
new test ID: NO
new market threshold: NO
new score: NO
historical backfill: NO
portfolio execution: NO
warning-to-action mapping: NO
E0-E7 row production: OFF
```

## Safety

The high-impact safepoint branch `backup-safepoint/2026-08-26-action-compass-accountability` was verified at source `main` SHA `9296cd283ef2a91e9cda9ae4e57aa4d6fbd0c9d5`. External-vault access returned 404 for the current GitHub app, so backup status is honestly `PARTIAL_INTERNAL_ONLY`.
