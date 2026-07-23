# BTC Range and Pullback Replication PATCH1 Final Validation

**Dato:** 2026-07-23  
**Status:** SHADOW_ONLY / INDEPENDENT_REPRODUCTION_PASS  
**Område:** Research Lab, FRLP challenger, pullback and rebuy methodology, reproducibility  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Source:** `08_SOURCE_MATERIAL/claude/2026-07-23__btc-range-pullback-replication-patch1__source-note.md`  
**Supersedes validation status of:** `2026-07-23__btc-range-pullback-replication-independent-rerun__shadow.md`

---

## 1. Governance verdict

```yaml
package_integrity: PASS
raw_lineage: PASS
original_experiment_reproduction: PASS
extended_governance_verification: PASS
reference_hash_parity: PASS
cross_process_exact_parity: PASS
cross_python_version_reference_parity: PASS
core_research_value: HIGH
canonical_promotion: NO
frlp_method_change: NO
active_test_change: NO
current_alert: NO
new_test: NO
new_engine: NO
market_state_change: NO
gate_change: NO
rebuy_change: NO
portfolio_action: NO
```

PATCH1 closes the reproducibility defects found in the first executable package. The package can now be treated as an independently reproducible retrospective challenger release for its declared deterministic scope.

It does not acquire canonical market or execution authority.

## 2. Independent reproduction evidence

Two clean extractions were executed independently with:

```text
Python: 3.13.5
PYTHONHASHSEED A: 0
PYTHONHASHSEED B: 987654321
```

The supplied frozen reference was generated in the package author's Python 3.12.3 environment.

Both Python 3.13.5 runs returned:

```text
409 original checks / 0 failures
36 extended checks / 0 failures
57 reference hash checks / 0 failures
502 total checks / 0 failures
```

Direct byte comparison returned:

```text
Run A versus Run B: 57 / 57 exact
Run A versus frozen reference: 57 / 57 exact
Run B versus frozen reference: 57 / 57 exact
Rerun hash manifests identical: YES
```

This is stronger than same-process self-consistency. It establishes exact parity across fresh processes, different string-hash seeds and Python 3.12 to Python 3.13 for every file inside the frozen deterministic scope.

## 3. Durable reproduced learning

### 3.1 Width-only headroom

Status:

```text
SUPPORTED_AS_SCOPED
```

The result concerns width-only Jaccard headroom inside the specified fixed-centre symmetric ATR family. It remains inappropriate to describe it as a universal ceiling for weekly range forecasting.

### 3.2 Linear centre tilt

Status:

```text
SUBSTANCE_STABLE
FORMAL_STATUS_WEAKENED
```

Large linear centre tilts remain harmful. Zero tilt remains the best tested construction in level results and under Winkler. The formal status remains `WEAKENED` because the predeclared paired-median condition for the smaller tilts is not met.

Bounded operational learning:

```text
Do not add a linear previous-week-return centre shift without new forward evidence.
```

### 3.3 Adaptive and asymmetric width

Status:

```text
NO_INCREMENTAL_VALUE
```

No named adaptive or asymmetric range variant exceeded the formal family threshold. This supports the existing complexity restraint. It does not prove that every possible adaptive forecast architecture is impossible.

### 3.4 Pullback bottom-catching

Status:

```text
NO_INCREMENTAL_VALUE
```

The tested pullback-conditioned momentum, extension and composite constructions do not show robust incremental value after conditioning, multiplicity control and unit-matched evaluation.

This supports confirmation-based deployment discipline. It does not create a new timing or rebuy rule.

### 3.5 Unconditional upside

The unit-matched challenger retains three of four previously reported upside survivors:

```text
atr_ts_top
clv5_top
ext20_top
```

`vol_r_top` weakens outside the adjusted threshold.

These are retrospective research findings. They are not standalone buy signals and receive no execution authority.

### 3.6 Low-volatility pullback configuration

Status:

```text
FRAGILE
NO_LIVE_ALERT
```

The bearish day-level result reverses under independent-event treatment and fails stability and multiplicity requirements. The durable learning is methodological:

```text
Overlapping daily observations can distort hit rates, medians and forward distributions.
Signal and control statistics must be reported on matched observational units.
```

## 4. FRLP consequence

The package verifies that metric choice materially changes the preferred width:

```text
TEST Jaccard optimum: ATR multiplier 1.50
TEST Winkler alpha 0.10 optimum: ATR multiplier 2.25
TEST Winkler alpha 0.20 optimum: ATR multiplier 2.00
```

Governance consequence:

```text
JACCARD_ONLY_METHOD_SELECTION: REJECT
ATR14_X_1_50_UNIVERSAL_FREEZE: REJECT
DUMB_2_0_UNIVERSAL_PROMOTION: REJECT
DUMB_1_5_AND_DUMB_2_0_AS_SEPARATE_BASELINES: RETAIN
FRLP_ACTIVE_FORWARD_TEST: RETAIN
```

Historical optimum values are sample- and grid-specific. They do not replace forward FRLP scoring or its kill criteria.

## 5. Source anomaly consequence

The 2018-02-08 Binance rows are genuine truncated source candles and must remain flagged.

Status:

```text
SOURCE_ANOMALY_2018_02_08_EARLY_CLOSE: MATERIAL
```

The label is retained because the package used a predeclared strict tolerance and some counts changed. The anomaly does not change:

- any research-question answer;
- any final status;
- width oracle or headroom;
- centre-tilt conclusion;
- FRLP metric optimum;
- pullback or rebuy conclusion.

The only headline field outside tolerance is E11 event count, whose experiment verdict was already `REJECTED_INCONSISTENT`.

## 6. Existing-owner routing

```text
T1 FRLP_V0_1:
Remains the range-method forward owner.

T2 GATE_BTC_PARTIAL_FT_1:
Remains the confirmation versus WAIT owner.

T4 PULLBACK_EDGE_20260708_01_OUTCOMES:
Remains the realised pullback-protection owner.

T5 FNP_CUMULATIVE:
Remains the lock-versus-opportunity owner.

Sensor Relationship and Incremental Value Standard:
Remains the canonical methodology and complexity owner.
```

No new test, engine or parallel owner is created.

## 7. Final conclusion

The strongest reproduced findings are negative and governance-relevant:

```text
1. Simple adaptive range refinements did not add robust incremental value.
2. Linear return-based centre tilt should not be added without forward evidence.
3. Pullback-conditioned bottom-catching did not show robust edge.
4. Metric choice changes the preferred range width materially.
5. Hit-rate and day-level distribution claims can be misleading when observations overlap.
6. Confirmation-based deployment remains better supported than retrospective bottom selection.
```

The package is now suitable as reproducible shadow research and as a historical challenger input to existing owners.

It does not justify a canonical range-method change, a live caution flag, a rebuy change or any portfolio action.

## 8. Authority boundary

```text
CANONICAL_RANGE_CHANGE: NO
ACTIVE_TEST_CHANGE: NO
NEW_ENGINE: NO
NEW_TEST: NO
CURRENT_ALERT: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
DEPLOYMENT_CHANGE: NO
PORTFOLIO_ACTION: NO
```
