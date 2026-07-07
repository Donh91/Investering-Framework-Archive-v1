# No-Hindsight Replay Harness Spec v0.1

Date: 2026-07-07  
Status: SPECIFICATION / NOT YET EXECUTED  
Purpose: Define how the framework should be replayed historically without hindsight.

---

## 1. Core objective

The replay harness should answer:

`What would the framework have known and said at the time, and did that decision logic help?`

It must not answer:

`What can we explain after seeing the outcome?`

The purpose is to convert historical DATA PING, Master Monday, Cycle Navigator and Fable research artifacts into reproducible decision rows.

---

## 2. Replay unit

The minimum replay unit is one daily or weekly row.

### Daily replay row

Use for:

- DATA PING
- gate states
- ETF flow
- FNP tracking
- state transitions

### Weekly replay row

Use for:

- Master Monday
- Cycle Navigator
- weekly range forecasts
- weekly actuals
- public score audit

---

## 3. Mandatory no-hindsight fields

Every replay row must contain:

| Field | Description |
|---|---|
| replay_id | Unique ID. Example: `REPLAY_2026-07-02_DAILY_V1`. |
| asof_date | Date/time the framework row is pretending to know. |
| data_available_at_time | Explicit list of data available at that date. |
| data_missing_at_time | Fields missing or unavailable at that date. |
| source_versions | DATA PING version, GitHub file, Fable file, market source. |
| highest_active_data_ping | Highest active DATA PING version at that time. |
| state_at_time | Framework state using only known data. |
| gate_status_at_time | Candidate / Attempt / Pending / Probation / Dead / etc. |
| rebuy_status_at_time | LOCKED / review / other. |
| flow_status_at_time | ETF negative / nonnegative / improving / pending / missing. |
| fpn_status_at_time | FNP inactive / measuring / active diagnostic. |
| next_up_trigger_at_time | What would improve state. |
| next_down_trigger_at_time | What would invalidate or worsen state. |
| decision_allowed | Yes/no and why. Usually no. |
| actual_outcome_window | Outcome measured after row, e.g. 1d/3d/7d/14d/30d. |
| rule_helped | Which rule improved decision quality. |
| rule_hurt | Which rule added delay, false lock or noise. |
| hindsight_violation_check | PASS/FAIL. |

---

## 4. Candidate replay schema

```csv
replay_id,asof_date,row_type,highest_active_data_ping,data_sources_available,data_missing,state,gate_status,rebuy_status,flow_status,fnp_status,next_up,next_down,decision_allowed,btc_close,ethbtc,btc_etf_5d,actual_7d_return,actual_30d_return,rule_helped,rule_hurt,hindsight_check,notes
```

---

## 5. Rule evaluation logic

### v0.2 hybrid gate

Replay should test:

- Did soft breach prevent premature gate death?
- Did hard death correctly avoid zombie-gate behavior?
- Did 59.0K tight hard-death trigger too early or appropriately?
- Did the two-close below 59.4K leg do most of the work?

Scoring:

- helped if it avoided false binary death or reduced churn
- hurt if it delayed death into clear breakdown
- neutral if no state implication

### 2/3-close doctrine

Replay should test:

- Did waiting for 2/3 closes prevent fakeout?
- Did waiting add opportunity cost without benefit?
- Did flow context improve or worsen the signal?

Canonical language:

`discipline, price-edge unproven, flow-conditioning did not rescue the edge`

Scoring:

- helped only if it avoided a drawdown/fake reclaim
- hurt if it filtered a valid early reclaim or added avoidable FNP
- never score as “historically proven edge”

### FNP ledger

Replay should test:

- What was Meter A?
- What was Meter B?
- Did the framework measure opportunity cost honestly?
- Did FNP pressure create better awareness without forcing rebuy?

Scoring:

- helped if it revealed hidden opportunity cost
- hurt if it would have pressured a portfolio action without confirmation
- always ledger-only, not signal

### ETF / flow status

Replay should separate:

- ETF print
- ETF trend
- ETF streak
- ETF improvement
- ETF missing/pending

Do not treat missing ETF as neutral.

### Rotation logic

Replay must keep:

- ETH/BTC reclaim attempt separate from Rotation Confirmed
- Rotation Watch separate from Rotation Confirmed
- altseason language unavailable unless matrix confirms it

---

## 6. Baseline comparisons

Replay should compare the framework against dumb baselines.

### For gates

- binary death gate
- no gate / hold state
- simple ATR threshold
- prior low breach

### For close-persistence

- N=1
- N=2
- N=3
- random threshold control
- no-persistence baseline

### For weekly ranges

- prior-week range persistence
- 1.5x ATR symmetric band
- random walk with historical volatility
- fixed percentage range

### For Cycle Navigator score

- score vs actual containment
- score vs breach direction
- score vs dumb baseline

---

## 7. Outcome metrics

### Daily/gate metrics

| Metric | Meaning |
|---|---|
| false_permission | Rule would have allowed risk before breakdown. |
| false_lock | Rule kept rebuy locked despite valid recovery. |
| gate_churn | Repeated enter/exit/death/reset behavior. |
| adverse_move_after_signal | Drawdown after state improvement. |
| opportunity_cost | Move from low/first possible entry to first permitted entry. |
| whipsaw_avoided | Fake reclaim avoided by discipline. |

### Weekly/range metrics

| Metric | Meaning |
|---|---|
| containment | Actual high/low inside forecast range. |
| breach_direction | Upside or downside breach. |
| width_efficiency | Range width vs actual realized range. |
| midpoint_error | Forecast midpoint vs actual midpoint. |
| Jaccard_overlap | Overlap between forecast and actual range. |
| baseline_delta | Improvement over dumb baseline. |

---

## 8. Replay phases

### Phase 0 — file extraction

Collect:

- DATA PING rows
- Master Monday raw files
- Cycle Navigator weekly posts
- verified weekly actuals
- Fable P1/P1b results
- ETF flow files
- OHLC files

### Phase 1 — daily BTC gate replay

Start with:

- BTC OHLC
- ETF flow
- v0.2 rules
- FNP rules

Output:

- daily state row
- gate state
- flow state
- FNP row
- actual forward outcomes

### Phase 2 — weekly Cycle Navigator replay

Start with:

- forecast ranges
- actual weekly ranges
- displayed score
- regime label

Output:

- forecast skill table
- dumb baseline comparison
- score reliability audit

### Phase 3 — rotation replay

Start only after ETHBTC and breadth data are available.

Output:

- ETHBTC persistence test
- Rotation Watch vs Rotation Confirmed audit
- false rotation rate

---

## 9. Hindsight rules

Forbidden:

- using future ETF flow to classify current state
- using final weekly actual range to judge in-week forecast path
- using later Fable evidence to rewrite old live state
- treating missing data as neutral
- using perp wick as canonical spot low
- using old DATA PING version when newer active version existed

Required:

- mark missing data explicitly
- freeze source at as-of date
- separate state classification from future outcome scoring
- preserve what the framework actually knew
- record source conflict rows

---

## 10. First executable replay candidate

Recommended first replay:

`REPLAY_P1B_GATE_WINDOW_2026-06-02_TO_2026-07-02`

Purpose:

Test current v0.2 gate behavior with:

- BTC OHLC
- Farside ETF flow
- 59.4K soft breach
- 59.0K hard death
- FNP ~9% prior
- 2/3-close discipline language

Expected output:

- daily state rows
- gate state transitions
- FNP meter rows
- rule_helped / rule_hurt labels
- no portfolio action

---

## 11. Output files for future execution

When implemented, replay should produce:

- `daily_replay_rows.csv`
- `weekly_replay_rows.csv`
- `rule_effectiveness_summary.md`
- `baseline_comparison.csv`
- `hindsight_violation_report.md`
- `framework_change_recommendations.md`

---

## 12. Governance note

Replay results are not automatically portfolio instructions.

Replay can recommend:

- keep
- modify
- retire
- shadow-only
- needs data

Replay cannot directly authorize:

- rebuy
- deployment
- Recovery Confirmed
- Rotation Confirmed
- portfolio action

Those require separate governance ratification.
