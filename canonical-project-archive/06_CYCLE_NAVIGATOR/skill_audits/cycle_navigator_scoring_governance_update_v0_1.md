# Cycle Navigator Scoring Governance Update v0.1

Date: 2026-07-07  
Status: ACTIVE GOVERNANCE UPDATE / SCORING RULES ONLY  
Source basis: Fable P2 Dream Audit report + uploaded reproducibility CSVs.

---

## 1. Purpose

This update locks the scoring lessons from the Fable P2 Dream Audit into Cycle Navigator governance.

It does not ratify market rules, portfolio actions, rebuy state, or public track record.

---

## 2. Core governance change

Cycle Navigator scoring must now separate:

1. `DISPLAYED_COMPOSITE_SCORE`
2. `INDEPENDENT_RANGE_SCORE`
3. `PHASE_SCORE`
4. `ROTATION_SCORE`
5. `BASELINE_COMPARISON`

The public displayed score may no longer be interpreted as pure range accuracy.

---

## 3. Actuals policy

CN self-reported actuals are now quarantined for final scoring.

Allowed uses:

- diagnostic reconstruction
- source comparison
- public-post context

Not allowed:

- final scoring basis
- public track-record claim
- range-skill evidence without independent reconciliation

Final actuals must use:

- raw OHLC recomputation, or
- independent actual ledger, or
- reconciled canonical actuals with explicit source basis.

---

## 4. Mandatory range metrics

Every future CN range audit must include:

- forecast_low
- forecast_high
- actual_low
- actual_high
- actual_basis
- containment label
- breach direction
- Jaccard overlap
- width ratio
- center error
- normalized center error

---

## 5. Mandatory baselines

No future range-skill claim may be made unless CN is compared against dumb baselines.

Minimum baselines:

1. prior-week repeat
2. ATR-1.5
3. ATR-2.0
4. fixed-5 percent
5. fixed-7.5 percent
6. fixed-10 percent

The P2 audit found CN median Jaccard did not beat ATR-2.0 or fixed-5 percent in the tested subset.

Therefore current range status is:

`CN_RANGE_SKILL_WEAK_VS_SIMPLE_BASELINES_P2_SAMPLE`

---

## 6. Displayed-score wording rule

Allowed wording:

`Composite score`

`Composite framework score`

`Displayed score`

Forbidden wording unless separately proven:

`Range accuracy score`

`Price forecast accuracy`

`88 percent range precision`

`Track record proves edge`

---

## 7. Regime / rotation status

Regime and rotation accuracy remain unproven until independent labels exist.

Current status:

`REGIME_ROTATION_EDGE_UNPROVEN_WITHOUT_INDEPENDENT_LABELS`

Phase and rotation evaluation sections may be used as self-reported context, but not as independent evidence of edge.

---

## 8. ETH/BTC gate status

The P2 audit supports existing conservative language:

- ETH/BTC 0.0275 at one close = early pressure / reclaim attempt only
- not Rotation Confirmed
- ETH/BTC 0.0300 is a stronger shadow candidate
- no official gate is ratified by this update

Current status:

`ETHBTC_0275_EARLY_PRESSURE_ONLY`

`ETHBTC_0300_STRONGER_SHADOW_CANDIDATE`

---

## 9. Public track record lock

Public track-record updates remain locked until all are available:

1. independent OHLC actuals for historical CN rows
2. clear forecast source rows
3. decision ledger or public scoring methodology ledger
4. baseline comparison
5. separation of composite score vs independent range score

Current status:

`PUBLIC_TRACK_RECORD_LOCKED_PENDING_INDEPENDENT_SCORING_LEDGER`

---

## 10. Required future CN output format

Future Cycle Navigator outputs should include two separated lines:

`Composite score: XX%`

`Independent range quality: Jaccard X.XX / containment label / breach direction`

If actuals are not yet available:

`Independent range quality: pending`

---

## 11. Research artifact references

Fable output CSVs archived under:

`canonical-project-archive/05_RESEARCH_LAB/fable_research/cycle_navigator_skill_audit/outputs/`

Key files:

- `benchmark_results.csv`
- `cn_range_metrics.csv`
- `cn_vs_baselines.csv`
- `data_manifest_used.csv`
- `ethbtc_gate_events.csv`
- `phase_rotation_audit.csv`
- `missing_items.csv`

---

## 12. Final governance line

No market call.
No portfolio action.
No rule ratification.
No public track-record update.
