# BACKTEST BUILD status addendum — Wave 1.3

```yaml
wave: BACKTEST_WAVE_1_3
name: AUTHORITY_AND_LINEAGE_RECOVERY
run_date: 2026-07-28
status: PARTIAL_DURABLE_PASS

Decision_Lineage:
  rows: 3
  A_FULLY_REPLAYABLE: 0
  FT_1: B_RECONSTRUCTED_NOT_POLICY_REPLAYABLE
  FNP_001: C_RETROSPECTIVE_POLICY_QUARANTINE
  TD_97: B_FORWARD_CLAIM_NO_ACTION_AUTHORITY
  actual_policy_replay_unlocked: NO

Direct_ETHBTC_Authority:
  owner: BINANCE_SPOT_ETHBTC
  approved_challenger: COINBASE_ETH-BTC
  conditional_shadow: KRAKEN_ETHXBT
  derived_ratio: DIAGNOSTIC_ONLY

Owner_Registry: FINAL_FOR_SELECTED_SCOPE
Prospective_Decision_Receipt: RATIFIED
engineering_tests: PASS_6_OF_6
final_holdout_opened: NO

rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```

Wave 1.3 closes the direct-pair authority gap for outage confirmation, but does not fabricate an A-class historical policy event. The next load-bearing work is prospective A-class receipt accumulation.