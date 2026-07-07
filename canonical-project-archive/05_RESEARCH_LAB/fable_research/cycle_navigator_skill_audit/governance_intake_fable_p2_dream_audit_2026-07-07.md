# Governance Intake — Fable P2 Dream Audit 2026-07-07

Status: RESEARCH-LAB INTAKE / NO RATIFICATION  
Source: Claude Fable 5 P2 Dream Audit report supplied by user  
Scope: E7 benchmarks, Cycle Navigator precision decomposition, E2 ETH/BTC gate audit.

---

## 1. Intake verdict

Accepted as high-priority adversarial research output.

Governance status:

`RESEARCH_ACCEPTED / RULES_NOT_RATIFIED / PUBLIC_TRACK_RECORD_NOT_UPDATED`

Primary verdict from Fable:

`CLEAR_EDGE_NOT_PROVEN`

This is stronger and more adversarial than the prior inhouse interim verdict:

`MIXED_SKILL_PROVISIONAL / RANGE_SKILL_NOT_PROVEN / REGIME_ROTATION_SKILL_STRONGER`

ChatGPT governance interpretation:

- Fable's report supersedes the optimistic part of the interim framing.
- The phrase `REGIME_ROTATION_SKILL_STRONGER` must be downgraded from provisional hypothesis to `UNPROVEN_SELF_REPORTED_CATEGORY_SIGNAL` until independent labels exist.
- CN range-skill must be considered `WEAK_OR_UNPROVEN_VS_BASELINES` in this tested subset.
- Framework-level edge remains untestable without a decision ledger.

---

## 2. Accepted findings

### Finding A — Framework edge not proven

Accepted.

Reason:

No framework decision ledger exists, so framework returns, drawdown avoidance, recovery capture and opportunity cost cannot be tested against BTC B&H, ETH B&H, 70/30 BTC/stables, DCA or other dumb benchmarks.

Required status:

`FRAMEWORK_EDGE_PROOF_BLOCKED_BY_DECISION_LEDGER_MISSING`

### Finding B — CN displayed scores are not pure range skill

Accepted and escalated.

Fable found displayed score mean around 88 versus independent Jaccard median around 0.39.

Required status:

`CN_DISPLAYED_SCORE_IS_COMPOSITE_NOT_RANGE_ACCURACY`

### Finding C — CN self-reported actuals must not be used as final scoring basis

Accepted and critical.

Fable recomputed actuals from raw OHLC and found systematic differences from CN self-reported actuals.

Required status:

`CN_SELF_REPORTED_ACTUALS_QUARANTINED_FOR_FINAL_SCORING`

Future scoring must use raw OHLC/reconciled independent actuals.

### Finding D — Naive baselines match or beat CN range skill

Accepted as provisional on the small sample.

Fable found median Jaccard:

- CN: 0.412
- prior-week repeat: 0.404
- ATR-1.5: 0.468
- ATR-2.0: 0.507
- fixed-5%: 0.502
- fixed-7.5%: 0.460
- fixed-10%: 0.345

Required status:

`CN_RANGE_SKILL_WEAK_VS_SIMPLE_BASELINES_P2_SAMPLE`

### Finding E — Regime/rotation skill remains unproven

Accepted.

Even if self-reported phase/rotation match is higher than range Jaccard, the labels are self-reported and categorical. They are not an independent proof of regime edge.

Required status:

`REGIME_ROTATION_EDGE_UNPROVEN_WITHOUT_INDEPENDENT_LABELS`

### Finding F — ETH/BTC 0.0275 remains early pressure, not confirmation

Accepted as consistent with existing framework language.

Fable found 0.0275 at one close had weak/fakeout-prone signal. 0.0300 was cleaner in this sample.

Required status:

`ETHBTC_0275_EARLY_PRESSURE_ONLY / ETHBTC_0300_STRONGER_SHADOW_CANDIDATE`

No rotation rule is ratified here.

---

## 3. Governance changes allowed now

Allowed immediately:

1. Add warning that CN displayed score is composite and not pure range accuracy.
2. Mark CN self-reported actuals as not acceptable for final scoring unless independently reconciled.
3. Require raw-OHLC actuals for future CN scoring.
4. Require baseline comparison for any future range-skill claim.
5. Downgrade `regime/rotation skill stronger` from provisional verdict to unproven hypothesis.
6. Treat 0.0300 ETH/BTC as a shadow candidate for cleaner rotation pressure testing.

---

## 4. Not allowed

Do not:

- update public track record
- claim CN range edge
- claim regime/rotation edge
- ratify 0.0300 as official rotation gate
- change rebuy state
- change portfolio rules
- create market conclusion
- use CN self-reported actuals as final truth

---

## 5. Required next data/actions

Critical:

1. Framework decision ledger export.
2. Forecast Ledger raw export.
3. Independent CN actual ledger from OHLC.
4. Independent phase/rotation label protocol.
5. Canonical DATA PING rows.
6. Meta-score formulas.
7. Sequence ledger.
8. ETH/ETHBTC continuation after 2026-06-14.

Next recommended archive action:

Create `cycle_navigator_scoring_governance_update_v0_1.md` to enforce:

- Displayed score = composite score
- Independent range score = Jaccard/containment/breach/width/center error
- Actual basis = raw OHLC or reconciled independent ledger
- Baseline comparison mandatory
- Self-reported actuals = diagnostic only unless reconciled

---

## 6. Final governance status

`P2_DREAM_AUDIT_ACCEPTED_AS_ADVERSARIAL_RESEARCH`

`CLEAR_EDGE_NOT_PROVEN`

`CN_RANGE_SKILL_WEAK_VS_BASELINES_P2_SAMPLE`

`REGIME_ROTATION_EDGE_UNPROVEN_WITHOUT_INDEPENDENT_LABELS`

`FRAMEWORK_EDGE_BLOCKED_BY_DECISION_LEDGER_MISSING`

No market call. No portfolio action. No rule ratification. No public track-record update.
