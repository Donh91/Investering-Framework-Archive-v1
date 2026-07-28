# BACKTEST WAVE 1.4 — Prospective A-Class Accumulation

```yaml
status: ACTIVE_DURABLE_PASS
historical_A_rows_created: 0
prospective_A_rows: 0
live_ETHBTC_overlap_sessions: 0
shadow_dual_run_weeks: 0
actual_policy_replay_unlocked: NO
final_holdout_opened: NO
```

## What changed

Wave 1.4 turns the lineage lesson into an operational system. Every future policy-relevant freeze, denial, trigger, supersession, closeout or explicit no-action decision must be captured within 30 minutes with exact temporal order, source hashes, owner authority, cost contract and label horizon.

Receipts are immutable one-file-per-event artifacts. Historical events cannot be inserted retroactively as A-class.

## Policy families

- `REBUY_LOCK`
- `NEW_ENTRY_PERMISSION`
- `TRIM_NO_TRIM`
- `ROTATION_PERMISSION`

Observational outputs such as Cycle Navigator ranges, TDBC context and ETF-flow description are not automatically policy events.

## Live direct ETH/BTC resilience

Binance remains owner. Coinbase is the approved direct challenger. The live ledger begins at zero sessions and requires 30 clean settled overlaps before owner-substitution eligibility can even be considered. Before then Coinbase is confirmation-only during Binance outages.

## Shadow simplification

Every accepted DATA PING should emit Full, Reduced and Minimal profile rows with a common run ID and snapshot. Promotion remains impossible before 12 weeks and is never automatic.

## Validation

- 8/8 Wave 1.4 unit tests pass locally.
- Empty active ledgers pass repository audit.
- Invalid receipts or shadow rows fail CI.
- The GitHub workflow runs on pull requests, relevant main pushes, daily schedule and manual dispatch.

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```