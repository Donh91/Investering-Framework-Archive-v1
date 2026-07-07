# First Replay Window — 2026-06-02 to 2026-07-02

Date created: 2026-07-07  
Status: EXECUTION PLAN / NOT YET POPULATED  
Replay ID: `REPLAY_P1B_GATE_WINDOW_2026-06-02_TO_2026-07-02`

---

## 1. Why this window is first

This is the most natural first replay window because it directly overlaps with:

- Fable P1/P1b current-regime pullback episode
- v0.2 hybrid gate logic
- 59.4K soft breach
- 59.0K hard-death
- FNP Meter A/B tracking
- Farside ETF-flow conditioning
- BTC OHLC / true ATR retest

It is narrow enough to execute, but important enough to teach the framework whether its live decision logic worked.

---

## 2. Primary questions

This replay must answer:

1. Would v0.2 have handled the June/July 2026 gate window better than binary death?
2. Did 59.0K act as a useful tight hard-death or too-tight invalidation?
3. Did 2/3-close discipline help avoid fake recovery, or did it add unnecessary FNP?
4. Did ETF flow context improve state classification?
5. Did FNP Meter A/B reveal hidden opportunity cost without creating rebuy pressure?
6. Were any state calls dependent on missing data?

---

## 3. Required data

Minimum:

- BTC OHLC daily, 2026-06-02 to 2026-07-02
- Farside BTC ETF daily flows for same window
- DATA PING rows for same window if available
- v0.2 rule definitions
- FNP prior and Meter A/B definitions

Optional but useful:

- ETH/BTC daily
- BTC.D
- funding/OI
- breadth
- perp wick diagnostics

If optional data is unavailable, mark DATA_MISSING.

Do not infer.

---

## 4. Rules active in this replay

### v0.2 hybrid gate

- soft breach: close <59.4K
- hard death: 1 close <59.0K OR 2 consecutive closes <59.4K
- 59.0K annotation: tight hard-death, not wide ATR buffer
- v0.2 can classify and measure, but cannot buy

### 2/3-close discipline

- discipline only
- price-edge unproven
- flow-conditioning did not rescue edge in P1b
- N <= 3
- cannot confirm recovery alone

### FNP

- prior: ~9% [7-12]
- p90: ~12%
- ledger-only
- not signal
- Meter A = context
- Meter B = verdict basis

### ETF flow

- separate print, trend, streak and improving status
- missing is not neutral
- latest known context must be preserved

### Rebuy

- remains LOCKED unless separate ratified rebuy package exists

---

## 5. Required row outputs

For each date, produce one row in `daily_replay_rows.csv`.

Mandatory row fields:

- replay_id
- asof_date
- highest_active_data_ping
- data available
- data missing
- state_at_time
- gate_status
- rebuy_status
- flow_status
- FNP_status
- next_up_trigger
- next_down_trigger
- decision_allowed
- BTC OHLC
- ETF flow 1d / 5d / 7d if available
- soft breach true/false
- hard death true/false
- close persistence count
- actual forward outcomes
- rule_helped
- rule_hurt
- hindsight_check

---

## 6. Baselines

Compare v0.2 against:

1. binary death on first close below survival shelf
2. no-death hold state
3. simple ATR buffer death
4. prior-low breach

Compare 2/3-close against:

1. N=1 reclaim
2. N=2 reclaim
3. N=3 reclaim
4. no reclaim rule

---

## 7. Expected output files after execution

When populated, this replay should create:

- `daily_replay_rows_2026-06-02_to_2026-07-02.csv`
- `daily_rule_effectiveness_summary_2026-06-02_to_2026-07-02.md`
- `hindsight_violation_report_2026-06-02_to_2026-07-02.md`
- `framework_change_recommendations_2026-06-02_to_2026-07-02.md`

---

## 8. Execution prompt for future run

```text
Execute REPLAY_P1B_GATE_WINDOW_2026-06-02_TO_2026-07-02.

Use only data available at each as-of date for state classification.
Use future data only in outcome columns.
Mark missing data as DATA_MISSING.
Do not infer missing DATA PING rows.
Do not treat missing ETF/funding/breadth as neutral.

Apply:
- v0.2 hybrid gate
- 59.4K soft breach
- 59.0K tight hard-death
- 2 consecutive closes below 59.4K hard-death leg
- 2/3-close discipline, language-only
- FNP Meter A/B
- ETF print/trend/streak separation
- rebuy locked rule

Return:
- daily replay rows
- rule effectiveness summary
- hindsight violation report
- framework change recommendations

No portfolio action.
No rebuy unlock.
No Recovery Confirmed or Rotation Confirmed unless separately ratified.
```

---

## 9. Current status

This file is a runbook, not a result.

Replay execution requires populated BTC OHLC, ETF flow and DATA PING rows.

If DATA PING rows are unavailable, a market-only replay may be created, but it must be labeled:

`DATA_PING_ROW_MISSING / MARKET_ONLY_REPLAY`
