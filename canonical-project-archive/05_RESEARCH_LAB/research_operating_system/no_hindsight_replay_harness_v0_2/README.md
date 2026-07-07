# No-Hindsight Replay Harness v0.2

Date: 2026-07-07  
Status: EXECUTION-READY TEMPLATE / NOT YET POPULATED WITH FULL DATA  
Supersedes: `no_hindsight_replay_harness_spec_v0_1.md` as active replay execution framework.

## Purpose

This folder turns the no-hindsight replay idea into an executable structure.

It does not yet claim historical replay results.

It defines exactly how to create replay rows that answer:

1. What did the framework know at the time?
2. What state would the framework have assigned?
3. Which rules helped?
4. Which rules hurt?
5. What actually happened later?
6. Was any hindsight accidentally used?

## Files in this folder

- `replay_harness_runbook_v0_2.md`  
  Step-by-step runbook for executing replay safely.

- `daily_replay_rows_template_v0_1.csv`  
  CSV schema for daily replay rows.

- `weekly_replay_rows_template_v0_1.csv`  
  CSV schema for Cycle Navigator / Master Monday weekly replay rows.

- `rule_effectiveness_scoring_matrix_v0_1.md`  
  Scoring rules for rule_helped / rule_hurt / neutral.

- `first_replay_window_2026-06-02_to_2026-07-02.md`  
  First recommended replay window, directly connected to Fable P1/P1b.

## Current recommended first replay

`2026-06-02 to 2026-07-02`

Why this window:

- It contains the current pullback episode from Fable P1/P1b.
- It touches v0.2 hybrid gate logic.
- It includes the 59.4K / 59.0K soft/hard-death zone.
- It can use BTC OHLC and Farside ETF flow.
- It can test FNP Meter A/B tracking.

## Standing governance constraints

Replay can recommend:

- keep
- modify
- retire
- shadow-only
- needs data

Replay cannot directly authorize:

- rebuy
- portfolio action
- Recovery Confirmed
- Rotation Confirmed
- deployment

## Critical no-hindsight rule

Future outcomes may only be used in the outcome columns, not in the state-at-time columns.
