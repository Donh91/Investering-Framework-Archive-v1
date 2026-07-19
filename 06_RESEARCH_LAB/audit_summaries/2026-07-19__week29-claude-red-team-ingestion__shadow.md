# Week 29 Claude Red-Team Ingestion

**Dato:** 2026-07-19  
**Status:** SHADOW_ONLY / PROVISIONAL_HORIZON  
**Område:** Research Lab / W29 red team / forecast and method audit  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `06_RESEARCH_LAB/forward_tests/`, `04_MARKET_LEARNING/etf_era/`, `02_DATA_PING/decision_value/`  
**Depends on:** `08_SOURCE_MATERIAL/claude/2026-07-19__claude-week29-research-package__source-note.md`, `03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-13__forecast-ledger-2026-w29__official.md`, `01_CORE_FRAMEWORK/governance/2026-07-10__f12-f12-5-reproducibility-freeze__canonical.md`, `04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

---

## 1. Ingestion verdict

Claude's independent red-team package contains useful challenge material, but it does not support a final W29 outcome or new canonical method rule.

```text
RESEARCH_VALUE: MODERATE
NEW_TRUTH_LAYER_VALUE: LOW
NEW_CANONICAL_VALUE: NONE
SHADOW_METHOD_VALUE: REAL
OFFICIAL_SCORING_VALUE: ZERO_AT_INGESTION
```

The useful durable unit is a provisional red-team synthesis mapped into existing framework tests and governance, not a new engine, new test or rewritten W29 forecast.

## 2. Accepted shadow findings

### A. Lock discipline remained defensible during the observed window

Claude argues that keeping the large-cap and rebuy windows closed avoided chasing a catalyst-assisted breakout before medium-horizon transmission was confirmed.

This is retained as a provisional counterfactual observation, not as a matured outcome.

```text
CLAUDE_H1_LOCK_CORRECT: PROVISIONALLY_SUPPORTED
MATURITY: PENDING_COMPLETE_W29_AND_EXISTING_OUTCOME_HORIZONS
OFFICIAL_FNP_CLASSIFICATION: NOT_CREATED
```

Reason for caution:

- Sunday was partial;
- official Binance CEST weekly actuals were not used;
- breadth remained noncanonical;
- package ETF windows were invalid.

Mapping:

```text
EXISTING_TEST_OWNER: T5_FNP_CUMULATIVE
NEW_TEST_CREATED: NO
VALID_OUTCOME_ROW_CREATED: NO
```

### B. BTC gate observations had apparent event value

The package supports the view that:

```text
63.3K reclaim separated weakness from renewed repair
61.9K survival distinguished an intraday wick from settled failure
```

This is consistent with the active event and does not constitute independent threshold ratification.

```text
THRESHOLD_CHANGE: NONE
UNIVERSAL_GATE_CLAIM: FORBIDDEN
EVENT_SCOPED_RESEARCH_SUPPORT: YES
```

### C. ETH/BTC repair held without confirmation

The package independently restates:

```text
ETHBTC_ABOVE_0275: REPAIR_INPUT_HELD
ETHBTC_ABOVE_0300: NOT_CONFIRMED
```

This is not new archive information. Its useful role is as a frozen transmission axis in the existing rotation-survival and transmission-matrix work.

Mapping:

```text
EXISTING_TEST_OWNER: T6_ROTATION_SURVIVAL_FORWARD
TRANSMISSION_MATRIX_AXIS: PRICE_SURVIVAL
NEW_FORWARD_TEST: NO
```

### D. BTC versus ETH ETF flow divergence matters for transmission

The primary-source 16 July observation is:

```text
BTC ETF total: +79.1M
ETH ETF total: -28.0M
```

Claude's interpretation that this weakens a broad-rotation claim is reasonable as shadow context.

However, the observation was already durably captured in the accepted DATA PING decision context and prospective event review. It is therefore not a new standalone ledger row.

```text
NEW_DATA_ROW: NO_DUPLICATE
NEW_INTERPRETIVE_ANGLE: YES_SHADOW
ROTATION_AUTHORITY: ZERO
```

## 3. H10 falsifiability finding

Claude's sharpest red-team claim is that an ETF-era absorption default can become too flexible if it explains both inflow-led upside and outflow-led downside without an outcome it cannot explain.

This concern is valid, but it is not a new canonical candidate.

The repository already has:

```text
F12 / F12.5 status: SPEC_INCOMPLETE
operational evaluation: SUSPENDED
ETF-era default: CONTEXT_ONLY
execution override: FORBIDDEN
independent reproducibility: REQUIRED
```

The Transmission Matrix protocol also already requires frozen axes, explicit evaluation horizons, source semantics and a promotion gate.

Therefore:

```text
H10_CANONICAL_CANDIDATE: REJECT_AS_DUPLICATIVE_AND_UNDER-SPECIFIED
H10_SHADOW_REINFORCEMENT: ACCEPT
F12_REACTIVATION: NO
F12_STATE: NOT_EVALUABLE
```

Claude's proposed example:

```text
ETH/BTC closes above 0.0300 while BTC ETF flows are negative
```

may be preserved only as a candidate counterexample for a future reproducibility packet. It is not sufficient by itself because it lacks:

- exact ETF observation window;
- number and persistence of negative sessions;
- BTC price and dominance context;
- breadth and deployment requirements;
- entry and exit rules;
- source hierarchy;
- independent replay evidence.

## 4. Claims rejected from durable learning

### A. Final W29 forecast outcome

```text
REJECT_REASON: WEEK_NOT_SETTLED_AND_WRONG_PRICE_CONVENTION
```

The package's BTC `HIT` and ETH `PARTIAL` labels are independent provisional audit labels only. They do not enter the official lineage.

### B. Four-session deceleration sequence

```text
181.1 -> 107.7 -> 79.1 -> 83.2
```

Rejected because 17 July was a provisional estimate. Farside later completed the BTC session at +132.3M and ETH at +36.7M.

### C. Negative 10-session BTC ETF window

Rejected because the package's ledger omitted completed sessions and calculated windows over incomplete numeric rows.

### D. Complete 20-session ETF ledger

Rejected. The file contained 16 settled rows, one provisional, one pending and two weekend rows.

### E. Japan 20 percent ETF-tax approval formulation

Rejected as overstated. Retain only the broader source-backed regulatory reclassification context until exact legal and tax implementation details are independently sourced.

### F. Market-wide flow conclusion

No market-wide CVD or multi-venue spot panel was produced. The package correctly labels the method gap, and no inferred flow conclusion is retained.

## 5. Existing-test routing

```yaml
T5_FNP_CUMULATIVE:
  candidate_input: provisional lock-versus-opportunity-cost narrative
  valid_row: false
  reason: incomplete horizon and incompatible price convention

T6_ROTATION_SURVIVAL_FORWARD:
  candidate_input: ETHBTC repair held, confirmation absent, BTC/ETH ETF divergence
  valid_row: false
  reason: missing canonical breadth and deployment axes

T10_ARCHIVE_LINEAGE_INTEGRITY:
  candidate_input: independent source package demonstrates why official source convention matters
  valid_outcome_row: false
  reason: official actual chain not complete

TRANSMISSION_MATRIX_FORWARD_TEST:
  candidate_input: absorption-without-transmission pattern
  valid_row: false
  reason: no frozen complete multi-axis row in the Claude package
```

## 6. What the package adds to the brain

The net new learning is narrower than Claude's own archive recommendation:

```text
1. Independent red-team agreement can coexist with rejection of its numeric outcome package.
2. A plausible conclusion must still fail archive promotion when source convention and maturity are wrong.
3. ETF absorption language must remain falsifiable, but current governance already freezes it as context-only.
4. Forecast evaluation must wait for the frozen provider, timezone and settled horizon.
5. Provisional source estimates must be revised before rolling-window conclusions are accepted.
```

## 7. Next valid actions

After W29 settles, the framework may:

1. generate official Binance Spot USDT CEST-resampled W29 actuals;
2. preserve the completed Sunday candle;
3. build the exact official forecast-outcome row under the existing lineage contract;
4. use only completed Farside sessions for ETF windows;
5. evaluate T5 and T6 only when their required fields and horizons are satisfied;
6. keep the H10 concern as a candidate input when the F12 reproducibility packet is eventually specified.

## 8. Authority boundary

```text
MARKET_STATE_CHANGE: NO
EVENT_STATE_CHANGE: NO
ALERT_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
DEPLOYMENT_CHANGE: NO
PORTFOLIO_ACTION: NO
CANONICAL_PROMOTION: NO
NEW_TEST: NO
```
