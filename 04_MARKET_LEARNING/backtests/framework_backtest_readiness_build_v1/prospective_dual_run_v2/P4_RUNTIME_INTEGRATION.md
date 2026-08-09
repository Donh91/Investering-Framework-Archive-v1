# P4 RUNTIME INTEGRATION

## Integration point

v2 is wired into the existing `.github/workflows/daily-raw-owner-capture.yml` after `build_capture_index.py` creates the current `DAILY_LIVE_ANCHOR_INDEX_v3` artifact. The existing five-times-daily schedule is unchanged.

No second market-data collector is created. No existing owner is called more frequently.

## Transaction

For each current live anchor:
1. resolve `03_DAILY_CAPTURE_LOGS/captures/LATEST.json`;
2. load the immutable current anchor and hash its exact bytes;
3. load and hash current sensor registry, policy registry, native rotation evaluator and the frozen v2 policy/crosswalk contract;
4. freeze the exact 32-sensor Full profile and exact 18-sensor Reduced profile;
5. invoke the same native rotation evaluator for both profiles;
6. copy REBUY/TRIM only if an explicit profile-native output already exists in the source capture;
7. write separate immutable child artifacts for Full and Reduced;
8. write a pair receipt containing only IDs, hashes, T, eligibility, missingness and health metadata, never policy values;
9. recompute coverage from pair receipts only;
10. commit the live anchor, bounded cold evidence and v2 paired evidence in the workflow's existing writer transaction.

## Point-in-time boundary

Both profiles use the exact `captured_at_utc` of the same live-anchor artifact and the same capture byte hash. The v2 collector performs no network access.

No input published after T is read. Missing inputs remain explicitly unavailable.

## Rotation fail-closed adapter

The current live-anchor index does not expose all frozen rotation evaluator inputs as native profile evidence. Gate 0-F explicitly admitted the native fail-closed/present-input path. When no explicit profile-native rotation-evidence block is present, the adapter invokes the existing evaluator in fail-closed mode:
- nullable market fields remain `None`;
- direct ETH/BTC authority is `UNAVAILABLE`;
- non-nullable run counters receive evaluator-control sentinel zero only to express that no positive gate can be established;
- those fields remain marked `UNAVAILABLE` in the missingness ledger;
- `imputation = false`.

No threshold or evaluator logic is changed.

## REBUY and TRIM

No new evaluator is invented. `REBUY_STATE` and `TRIM_EXIT_STATE` become eligible only when source capture contains an explicit profile-native `REBUY_LOCK` or `TRIM_NO_TRIM` output. Otherwise they are `POLICY_OUTPUT_UNAVAILABLE`.

## Cadence rationale

The existing live-anchor cadence is chosen because ephemeral PIT observations are already intentionally captured five times daily. The cadence is not increased and is not selected for statistical convenience. Coverage maturity uses fixed 72-hour windows, so repeated anchors inside a window do not inflate occupied-window count.

## v1 boundary

`SHADOW_SIMPLIFICATION_DUAL_RUN_v1.json`, `RUN_LEDGER_v1.json` and all historical v1 child semantics are read-only and are not touched by v2 code or workflow writes.
