# Replay Harness Runbook v0.2

Date: 2026-07-07  
Status: EXECUTION-READY RUNBOOK  
Scope: Daily and weekly no-hindsight replay for the Investering Framework.

---

## 1. Objective

The replay harness must reconstruct what the framework would have known and said at a specific time.

It must never use future outcomes to decide the state-at-time.

The replay row has two separated sections:

1. **As-of section**
   - only data available at the timestamp
   - state/gate/rebuy/flow/FNP classification
   - next up/down triggers

2. **Outcome section**
   - forward returns and actual outcome windows
   - rule_helped / rule_hurt scoring
   - baseline comparison

---

## 2. Required source order

For every replay row, use this source hierarchy:

1. Highest active DATA PING version at that time.
2. GitHub canonical archive file if available.
3. Fable research artifact only if it existed at or before replay date.
4. Market data available at that date.
5. Outcome data only in outcome columns.

If a higher DATA PING version exists and is active, older DATA PING rows are archive context only.

---

## 3. Hard no-hindsight rules

Forbidden:

- Using future ETF flow to classify current flow status.
- Using future Fable research to rewrite an old live decision.
- Using final weekly high/low to judge in-week forecast state.
- Treating missing ETF/funding/breadth as neutral.
- Using perp wick as canonical spot low.
- Using a stale DATA PING version when newer active version existed.
- Filling missing rows by intuition.

Required:

- Mark missing data as DATA_MISSING.
- Mark source conflicts explicitly.
- Separate latest ETF print from trailing ETF trend.
- Preserve what the framework actually knew at the time.
- Put future outcome only in outcome columns.

---

## 4. Daily replay workflow

### Step 1 — select replay window

Example:

`2026-06-02 to 2026-07-02`

### Step 2 — collect as-of data

For each date:

- BTC OHLC up to and including that date
- ETH/BTC if available
- ETF flow prints known by that date
- funding/OI if available
- breadth if available
- latest DATA PING row at or before that date
- relevant framework rules active at that date

### Step 3 — classify state-at-time

Populate:

- state_at_time
- gate_status
- rebuy_status
- flow_status
- FNP_status
- next_up_trigger
- next_down_trigger
- decision_allowed

### Step 4 — apply rule checks

Rules to apply first:

- v0.2 soft breach close <59.4K
- v0.2 hard death: 1 close <59.0K OR 2 consecutive closes <59.4K
- 2/3-close discipline, language only
- FNP Meter A/B tracking
- ETF flow status line
- 64K dead-level restriction
- perp wick diagnostic-only restriction

### Step 5 — add outcome columns

After state-at-time is frozen, add:

- actual 1d return
- actual 3d return
- actual 7d return
- actual 14d return
- actual 30d return
- max adverse excursion
- max favorable excursion
- whether next_up occurred
- whether next_down occurred

### Step 6 — score rule effectiveness

Use `rule_effectiveness_scoring_matrix_v0_1.md`.

Allowed labels:

- HELPED
- HURT
- NEUTRAL
- DATA_MISSING
- NOT_APPLICABLE
- HINDSIGHT_RISK

---

## 5. Weekly replay workflow

Weekly replay is for:

- Master Monday
- Cycle Navigator
- weekly forecast range
- weekly score and track record

For each week, populate:

- forecast date
- week covered
- BTC forecast low/high
- ETH forecast low/high
- actual BTC low/high
- actual ETH low/high
- forecast containment
- breach direction
- width efficiency
- baseline comparison
- displayed score
- score reliability note

Do not use actual weekly range to modify the forecast row.

---

## 6. First executable daily replay

Recommended first execution:

`REPLAY_P1B_GATE_WINDOW_2026-06-02_TO_2026-07-02`

Purpose:

- Test v0.2 gate behavior in the same regime P1b studied.
- Track FNP Meter A/B in live-style rows.
- Evaluate whether 59.0K tight hard-death worked as intended.
- Evaluate whether 2/3-close discipline helped or hurt.
- Keep rebuy locked unless a separate ratified rebuy package exists.

Minimum required data:

- BTC OHLC
- Farside BTC ETF flow
- v0.2 rule definitions
- FNP prior
- DATA PING state rows if available

If DATA PING rows are missing:

- mark DATA_PING_ROW_MISSING
- create market-only replay rows
- do not infer live state beyond explicit rules

---

## 7. First executable weekly replay

Recommended first weekly replay:

`CYCLE_NAVIGATOR_RANGE_SKILL_BACKFILL_V0_1`

Purpose:

- Test weekly range forecasts against actuals.
- Compare against dumb baselines.
- Audit whether displayed score reflects real forecast quality.

Minimum required data:

- issue/week number
- forecast range
- actual range
- forecast date
- score
- regime label

If score or actual is missing:

- mark DATA_MISSING
- do not estimate

---

## 8. Output files after execution

Daily replay should produce:

- `daily_replay_rows.csv`
- `daily_rule_effectiveness_summary.md`
- `daily_hindsight_violation_report.md`

Weekly replay should produce:

- `weekly_replay_rows.csv`
- `weekly_range_baseline_comparison.csv`
- `cycle_navigator_score_audit.md`

---

## 9. Governance output format

Every replay result should end with:

```text
FRAMEWORK CONSEQUENCE:
keep / modify / retire / shadow-only / needs-data

PORTFOLIO ACTION:
none

REBUY STATUS:
unchanged unless separately ratified
```

---

## 10. Current status

This runbook is execution-ready.

It is not itself a replay result.

The next required step is data population from Custom GPT / GitHub archive / uploaded Fable data.
