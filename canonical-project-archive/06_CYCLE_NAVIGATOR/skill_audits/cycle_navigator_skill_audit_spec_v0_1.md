# Cycle Navigator Skill Audit Spec v0.1

Date: 2026-07-07  
Status: ACTIVE AUDIT SPEC / NOT A RESULT  
Scope: Public Cycle Navigator forecast/evaluation rows, source-backed archive rows, and later Master Monday comparison.

---

## 0. Executive purpose

This spec defines how to audit Cycle Navigator forecast skill without overclaiming.

It separates:

1. **Cycle Navigator's own displayed weekly score**
2. **Independent range-skill metrics**
3. **Regime / rotation classification accuracy**
4. **Master Monday internal forecast quality**

This spec does not score anything by itself.

It defines what may be scored later.

---

## 1. Current archive readiness

Current status:

`PARTIAL_READY_SOURCE_BACKED`

Reason:

- Several public Cycle Navigator rows are source-backed.
- Several next-week evaluation sections are source-backed.
- CN #7 is the strongest early row because it includes BTC and ETH forecast/evaluation.
- CN #8 is forecast-backed, but next-week evaluation is missing.
- Master Monday W28 raw archive is source-backed, but actuals are not yet available.

Still not final-ready because:

- independent actual run IDs are missing for many early rows
- W22/W23/W24/W27 actuals have source conflicts
- some rows rely on later CN evaluation sections rather than independent actual ledgers
- raw Master Monday archive before W28 is incomplete

---

## 2. Source hierarchy

Use this hierarchy when scoring or building audit rows:

1. Original public Cycle Navigator post text / public X post / committed source file.
2. Next-week Cycle Navigator evaluation section, if clearly tied to the prior forecast.
3. Verified independent actual range ledger with run ID and source/time basis.
4. Master Monday raw forecast archive.
5. Reconstructed Master Monday archive.
6. Memory context only.

Memory rows must never be final-scored.

---

## 3. Row status definitions

| Status | Meaning | Can be scored? |
|---|---|---|
| SOURCE_BACKED | Original forecast source found. | Yes, if actuals are reconciled. |
| SOURCE_BACKED_FROM_NEXT_WEEK_EVALUATION | Forecast/actual found in later evaluation section. | Yes with caveat, if mapping is clear. |
| PARTIAL_SOURCE_BACKED | Forecast source found, but actuals or score missing. | Not final-scored until completed. |
| MEMORY_CONTEXT_ONLY | Only memory/context found. | No. |
| SOURCE_CONFLICT | Sources disagree materially. | No until reconciled. |
| DATA_MISSING | Required fields missing. | No. |

---

## 4. Minimum scoring eligibility

A Cycle Navigator row may only be scored if all five conditions are true:

1. Source-backed forecast range exists.
2. Forecast window is known.
3. Actual high/low is source-backed or reconciled.
4. No unresolved source conflict exists for the scored field.
5. The row is not memory-only.

If any condition fails, mark:

`NOT_SCOREABLE_YET`

---

## 5. Public CN score vs independent audit score

Cycle Navigator public score should be stored as:

`displayed_score`

Independent audit score should be separately computed as:

`independent_skill_score`

Do not merge them.

Reason:

The public score may include:

- price range
- intraday blocks
- cycle phase
- rotation classification
- qualitative regime fit

Independent audit must show which part of the public score was actually accurate.

---

## 6. Independent range-skill metrics

For BTC and ETH separately:

### 6.1 Containment

| Case | Label |
|---|---|
| actual_low >= forecast_low and actual_high <= forecast_high | FULL_CONTAINMENT |
| one side breaches | PARTIAL_BREACH |
| both sides breach | DOUBLE_BREACH |
| actual fully outside forecast | MISS |

### 6.2 Breach direction

Allowed labels:

- NO_BREACH
- LOW_SIDE_BREACH
- HIGH_SIDE_BREACH
- DOUBLE_BREACH

### 6.3 Range width efficiency

Calculate:

`forecast_width / actual_width`

Interpretation:

| Ratio | Label |
|---|---|
| 0.80 - 1.50 | EFFICIENT |
| 1.50 - 2.50 | WIDE_BUT_USABLE |
| >2.50 | TOO_WIDE |
| <0.80 | TOO_NARROW |

### 6.4 Jaccard overlap

Calculate overlap between forecast range and actual range.

`overlap_width / union_width`

Use as numeric skill indicator.

### 6.5 Center error

Calculate:

`abs(forecast_mid - actual_mid)`

Normalize by actual width where possible.

---

## 7. Baselines

Every scored row should compare CN forecast against at least one dumb baseline.

Preferred baselines:

1. Previous-week actual range repeated.
2. ATR-based range around prior close.
3. Simple no-skill wide band.
4. Prior week close +/- fixed percentage band.

If baseline data is missing, mark:

`BASELINE_DATA_MISSING`

Do not claim skill without baseline comparison.

---

## 8. Intraday block scoring

Intraday blocks may be scored separately only when:

- block forecast exists
- block actual exists
- block dates are clear
- source is public post/evaluation section

Intraday block score should not be merged with weekly range skill unless explicitly separated.

Allowed labels:

- BLOCK_FULL_CONTAINMENT
- BLOCK_PARTIAL_BREACH
- BLOCK_MISS
- BLOCK_DATA_MISSING

---

## 9. Cycle phase scoring

Cycle phase forecast can be scored only if both forecast and actual phase are in the source/evaluation section.

Allowed labels:

- PHASE_MATCH
- PHASE_CLOSE
- PHASE_MISS
- PHASE_DATA_MISSING

Example:

Forecast: Early Bull BTC-led  
Actual: Early Bull BTC-led  
Label: PHASE_MATCH

Do not use price performance alone to infer cycle phase accuracy.

---

## 10. Rotation scoring

Rotation must be scored conservatively.

Allowed labels:

- ROTATION_MATCH
- ROTATION_CLOSE
- ROTATION_MISS
- ROTATION_DATA_MISSING

Rules:

- `No Rotation` is not the same as `Rotation Confirmed`.
- ETH/BTC stabilization alone is not Rotation Confirmed.
- Rotation scoring must respect the framework's conservative rotation language.

Do not infer broad altseason from source rows unless the row explicitly says so and the framework matrix confirms it.

---

## 11. Master Monday vs Cycle Navigator separation

Master Monday and Cycle Navigator must be scored separately.

### Cycle Navigator

Public/compressed output.

Score dimensions:

- public BTC range
- public ETH range if present
- public displayed score
- public phase/rotation language

### Master Monday

Internal forecast/governance layer.

Score dimensions:

- raw BTC/ETH forecast
- internal regime label
- source verification status
- internal Precision Score

Do not use public Cycle Navigator score as Master Monday score unless the source explicitly states the relationship.

---

## 12. Current row-level scoreability matrix

| Row | Current status | Can score now? | Reason |
|---|---|---|---|
| CN #1 | SOURCE_BACKED forecast | No | Tracking begins next week / independent actual missing. |
| CN #2 | SOURCE_BACKED forecast/evaluation | Maybe later | Needs actual source reconciliation or acceptance of CN #3 evaluation section. |
| CN #3 | SOURCE_BACKED forecast/evaluation | Maybe later | Needs actual source reconciliation or acceptance of CN #4 evaluation section. |
| CN #4 | SOURCE_BACKED forecast/evaluation | Maybe later | Needs actual source reconciliation or acceptance of CN #5 evaluation section. |
| CN #5 | SOURCE_BACKED via CN #6 evaluation | Maybe later | Stronger now, but independent actual run ID missing. |
| CN #6 | SOURCE_BACKED from CN #7 evaluation | Maybe later | Original CN #6 post found by Grok, but forecast/evaluation mapping must remain explicit. |
| CN #7 | SOURCE_BACKED forecast/evaluation incl. ETH | Best candidate | Still needs independent actual run ID if strict audit. |
| CN #8 | PARTIAL_SOURCE_BACKED forecast only | No | Next-week evaluation missing. |
| MM W28 | SOURCE_BACKED raw | No | W28 actuals not available yet. |

---

## 13. Source conflict handling

If actual values differ across sources:

1. Preserve all values.
2. Mark `SOURCE_CONFLICT`.
3. Do not score the conflicted field.
4. Prefer user-verified final run only if source/run ID and time basis are clear.
5. If two valid sources use different time basis, create separate rows:
   - `ACTUALS_CEST_EXCHANGE`
   - `ACTUALS_CG_GLOBAL`
   - `ACTUALS_YAHOO`

Never silently overwrite actuals.

Known conflicts:

- W22 BTC actuals
- W23 BTC actuals
- W24 BTC high
- W27 BTC/ETH actuals
- April Master Monday forecast variants
- Uge 25 memory vs reconstructed forecast low

---

## 14. Audit outputs to produce later

When execution begins, create:

1. `cycle_navigator_skill_audit_rows_v0_1.csv`
2. `cycle_navigator_range_skill_summary_v0_1.md`
3. `cycle_navigator_score_vs_independent_skill_v0_1.md`
4. `cycle_navigator_actuals_reconciliation_report_v0_1.md`
5. `cycle_navigator_track_record_update_recommendation_v0_1.md`

The final file may recommend public track-record update only if enough rows are source-backed and actuals are reconciled.

---

## 15. What a scored row must include

CSV fields should include:

- row_id
- cn_issue
- forecast_source
- evaluation_source
- actual_source
- source_status
- week_start
- week_end
- btc_forecast_low
- btc_forecast_high
- btc_actual_low
- btc_actual_high
- btc_containment_label
- btc_breach_direction
- btc_width_efficiency
- btc_jaccard
- eth_forecast_low
- eth_forecast_high
- eth_actual_low
- eth_actual_high
- eth_containment_label
- displayed_score
- independent_skill_score
- score_gap
- phase_forecast
- phase_actual
- phase_score_label
- rotation_forecast
- rotation_actual
- rotation_score_label
- baseline_result
- source_conflict
- scoreable_status
- notes

---

## 16. Current audit permission

Allowed now:

- build scoring template
- score only draft rows internally with `PROVISIONAL_NOT_FOR_PUBLIC_TRACK_RECORD`
- reconcile actual sources
- compare CN displayed score against independent metrics for clearly sourced rows

Not allowed now:

- final public track-record update
- claim overall model edge
- claim statistically significant forecast skill
- mix memory-only rows into scored set
- hide actual source conflicts

---

## 17. Governance conclusion

Cycle Navigator Skill Audit is now partially ready.

The next execution step should be a provisional audit on the source-backed subset only, clearly marked:

`PROVISIONAL_SOURCE_BACKED_SUBSET_NOT_FINAL_TRACK_RECORD`

No market call.
No portfolio action.
No rule ratification.
