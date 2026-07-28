# BACKTEST BUILD status addendum — Wave 1.4

```yaml
wave: BACKTEST_WAVE_1_4
name: PROSPECTIVE_A_CLASS_ACCUMULATION
status: ACTIVE_DURABLE_PASS
run_date: 2026-07-28

Prospective_Decision_Receipts:
  historical_A_rows_created: 0
  prospective_A_rows: 0
  maximum_capture_delay_seconds: 1800
  policy_families: 4
  retroactive_conversion: FORBIDDEN

Live_ETHBTC_Dual_Source:
  owner: BINANCE_SPOT_ETHBTC
  challenger: COINBASE_ETH-BTC
  live_overlap_sessions: 0
  owner_substitution_eligible: NO

Shadow_Dual_Run:
  profiles: [FULL_STACK, REDUCED_EXECUTION_STACK, MINIMAL_CORE_STACK]
  valid_runs: 0
  minimum_weeks: 12
  preferred_weeks: 26

local_tests: PASS_8_OF_8
repository_audit: PASS_ACTIVE_ZERO_EVENTS
daily_GitHub_audit: ACTIVE_READ_ONLY
actual_policy_replay_unlocked: NO
final_holdout_opened: NO

rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```

The next accepted policy-relevant decision after merge must emit an immutable receipt. No historical event has been upgraded retroactively.