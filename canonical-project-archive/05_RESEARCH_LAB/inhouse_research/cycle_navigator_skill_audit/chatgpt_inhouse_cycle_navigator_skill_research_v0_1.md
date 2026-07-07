# ChatGPT Inhouse Research — Cycle Navigator Skill Audit v0.1

Date: 2026-07-07  
Mode: INHOUSE HIGH-INTELLIGENCE / GITHUB-FIRST RESEARCH  
Status: COMPLETED FIRST FULL PASS / NOT FINAL TRACK RECORD  
Scope: Cycle Navigator #2-#7 provisional source-backed subset; CN #8 forecast-only; Master Monday separation context.

---

## 0. Why this mode was chosen

This research was executed as **inhouse high-intelligence / GitHub-first research**, not as external Deep Research and not as agent-mode.

Reason:

- The problem is internal archive/governance/audit work.
- The highest-signal source is GitHub project archive + chat-memory extraction + user-supplied X/Grok content.
- External web search would not solve internal source-governance conflicts.
- Agent-mode is better later for bulk migration/parsing, not for current governance interpretation.

This pass does not run unattended in the background. It is a structured deep pass designed to prepare Fable/Claude for a more computational/adversarial audit when available.

---

## 1. Inputs reviewed

Key archive inputs:

1. `cycle_navigator_forecast_actual_rows_sourcebacked_v0_2.csv`
2. `cycle_navigator_skill_audit_spec_v0_1.md`
3. `cycle_navigator_skill_audit_spec_v0_1_addendum_2026-07-07.md`
4. `cycle_navigator_actuals_reconciliation_report_v0_1.md`
5. `cycle_navigator_skill_audit_rows_v0_1.csv`
6. `cycle_navigator_provisional_skill_audit_summary_v0_1.md`
7. `master_monday_sourcebacked_rows_v0_2.csv`
8. `april_2026_master_monday_conflict_resolution.md`
9. `master_monday_chat_memory_extraction_2026-07-07.md`
10. User-supplied Custom GPT / main GPT / Grok extraction results.

---

## 2. Row validation

### Included provisional rows

- CN #2
- CN #3
- CN #4
- CN #5
- CN #6
- CN #7

### Excluded rows

- CN #1: tracking begins next week / no independent actual.
- CN #8: forecast source exists, but next-week evaluation/actuals missing.
- CN #11: must be protected from copy-paste contamination.
- CN #12 onward: scoring-method upgrade applies prospectively.
- Master Monday W28: raw source exists but actuals not final yet.

---

## 3. Quantitative BTC range read

Using provisional source-backed rows CN #2-#7:

| Metric | Value |
|---|---:|
| Rows assessed | 6 |
| Full containment | 2 / 6 |
| Partial breach | 4 / 6 |
| Full miss | 0 / 6 |
| Low-side breach | 3 / 6 |
| High-side breach | 1 / 6 |
| Mean Jaccard overlap | 0.578 |
| Mean width ratio | 1.207 |
| Mean center error | 1,325 USD |
| Mean normalized center error | 0.249 |
| Mean displayed public score | 87.5 |

Interpretation:

- There is no full miss in the provisional subset.
- Range width is generally not inflated; average width ratio is close to 1.2.
- Price-range skill is real enough to study, but not strong enough to claim final edge.
- Breach distribution matters: after CN #5, errors lean low-side, meaning forecasts were somewhat too high during BTC-led absorption/chop.

---

## 4. Row-by-row interpretation

### CN #2

- Forecast: 65K-72K
- Actual: 66K-71K
- Result: FULL_CONTAINMENT
- Jaccard: 0.714
- Width ratio: 1.400
- Displayed score: 88

Interpretation:

Strong price row. Displayed score broadly aligned with independent range result.

### CN #3

- Forecast: 66K-73K
- Actual: 69K-76K
- Result: PARTIAL_BREACH, high-side
- Jaccard: 0.400
- Width ratio: 1.000
- Displayed score: 83

Interpretation:

Range was too low relative to actual upside extension. Public score may be supported by phase/rotation more than by pure range containment.

### CN #4

- Forecast: 73K-79K
- Actual: 74K-78.5K
- Result: FULL_CONTAINMENT
- Jaccard: 0.750
- Width ratio: 1.333
- Displayed score: 86

Interpretation:

Strongest early BTC price row. Forecast width efficient; price result aligns well with public score.

### CN #5

- Forecast: 76.5K-83.5K
- Actual: 75.4K-80.3K
- Result: PARTIAL_BREACH, low-side
- Jaccard: 0.469
- Width ratio: 1.429
- Displayed score: 85

Interpretation:

Caught upper structure but missed lower weakness. Public score likely reflects good regime/rotation call, not pure price accuracy.

### CN #6

- Forecast: 79K-83.5K
- Actual: 78.5K-82.5K
- Result: PARTIAL_BREACH, low-side
- Jaccard: 0.700
- Width ratio: 1.125
- Displayed score: 92

Interpretation:

Strong overlap despite low-side breach. High public score can be defended if phase/rotation and intraday blocks were strong, but pure BTC containment alone does not justify 92.

### CN #7

- BTC forecast: 79.5K-84K
- BTC actual: 77.6K-82.3K
- ETH forecast: 2.28K-2.48K
- ETH actual: 2.16K-2.37K
- BTC Jaccard: 0.438
- ETH Jaccard: 0.281
- Displayed score: 91

Interpretation:

This is the best source-backed BTC+ETH row, but both BTC and ETH were low-side breached. The high public score is more plausibly explained by phase/rotation accuracy than by pure price-range accuracy.

---

## 5. Displayed score vs independent range skill

Preliminary verdict:

`DISPLAYED_SCORE_PARTLY_SUPPORTED_BY_REGIME_NOT_RANGE`

Rationale:

- Public displayed scores likely combine price range, intraday blocks, cycle phase, rotation and qualitative regime fit.
- Independent range metrics alone would likely produce lower/more nuanced scores in CN #3, #5 and #7.
- CN #2 and CN #4 align well with displayed score.
- CN #6 is mixed: strong overlap but still low-side breach.

Current hypothesis:

`Cycle Navigator scores are not pure range-skill scores and should not be presented as such.`

---

## 6. Regime / phase / rotation audit

The subset supports the provisional hypothesis:

`structure/regime skill > exact price-range skill`

Observed:

- Phase calls mostly align: Early Bull Attempt / Early Bull BTC-led.
- Rotation calls were conservative and mostly correct: No Rotation / no sustained rotation.
- CN #7 correctly avoided Rotation Confirmed despite ETH stabilization.

This is the most defensible strength of the framework so far.

---

## 7. Failure modes detected

### 7.1 Low-side breach clustering after CN #5

Rows CN #5, CN #6 and CN #7 all show low-side breach.

Potential interpretation:

- The model may have been slightly too bullish on price level during BTC-led absorption/chop.
- It was better at identifying structure/regime than exact downside extension.

### 7.2 Displayed-score compression

Public score compresses multiple dimensions into one number.

Risk:

- Readers may interpret 88-92% as pure range accuracy.
- In reality, some high scores are supported by regime/rotation, not price containment.

### 7.3 Evaluation-source dependence

Several actuals come from next-week CN evaluation sections, not independent actual-run ledgers.

Risk:

- Internal consistency may be good, but independent audit requires source/run IDs.

### 7.4 ETH scoring sparsity

Only CN #7 currently has public ETH forecast + evaluation.

Risk:

- ETH skill cannot be generalized.

### 7.5 CN #11 contamination risk

Known copy-paste contamination must be quarantined.

Correct CN #11:

- BTC 61K-69K
- ETH 1.55K-1.90K

Contaminated values:

- BTC 79.5K-84K
- ETH 2.28K-2.48K

---

## 8. Baseline requirement

No final skill claim can be made until CN forecasts are tested against dumb baselines.

Minimum baselines:

1. Prior-week actual repeated.
2. Prior close +/- fixed percentage band.
3. ATR-based band.
4. No-skill wide band.

Baseline metrics must compute:

- containment
- Jaccard
- width ratio
- center error
- breach direction

Skill claim requires CN to beat baselines after width penalty.

---

## 9. What can be safely updated now

Safe updates:

1. Public displayed score must be described as composite score, not pure range score.
2. Cycle Navigator audit should report separate price, phase and rotation metrics.
3. CN #5-#7 low-side breach cluster should be tracked as possible bullish price-level bias.
4. CN #7 should be treated as the first useful BTC+ETH public audit row.
5. CN #12 scoring upgrade should be used prospectively and as an independent overlay for older rows.

Shadow-only hypotheses:

1. Regime/rotation skill may be materially stronger than range skill.
2. Price forecasts may run too high during BTC-led absorption.
3. Public score may overstate price accuracy if not decomposed.

Do not update yet:

1. Final public track record.
2. Claim of range edge.
3. Statistical significance.
4. Master Monday raw-score history before source reconstruction is complete.

---

## 10. Recommended Fable research task

Fable should test:

1. Displayed score inflation vs independent range metric.
2. Baseline comparison.
3. Low-side breach cluster/bullish bias.
4. Regime-vs-price decomposition.
5. CN #12 scoring-method backtest overlay.
6. Source consistency between GitHub posts, X posts and evaluation sections.

Fable should return:

- verdict label
- row validation table
- independent metrics
- displayed-score alignment table
- failure modes
- baseline test plan
- data requests
- framework recommendations

---

## 11. Final inhouse verdict

Best current verdict before Fable:

`MIXED_SKILL_PROVISIONAL / RANGE_SKILL_NOT_PROVEN / REGIME_ROTATION_SKILL_STRONGER`

This is a useful and honest interim result.

No market call.
No portfolio action.
No rule ratification.
No public track-record update.
