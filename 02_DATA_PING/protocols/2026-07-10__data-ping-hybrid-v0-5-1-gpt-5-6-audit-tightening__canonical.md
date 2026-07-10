# DATA PING Hybrid v0.5.1 — GPT-5.6 Audit Tightening

**Dato:** 2026-07-10  
**Status:** CANONICAL_MANDATORY_ADDENDUM  
**Område:** DATA PING authority / rotation fields / missing data / anti-bloat  
**Primary folder:** `02_DATA_PING/protocols/`  
**Depends on:** `2026-07-10__data-ping-hybrid-v0-5-1-auto-edge-escalator-consolidated__canonical.md`; GPT-5.6 Fresh Eyes Audit Implementation  
**Supersedes:** conflicting interpretations only; does not replace the consolidated v0.5.1 protocol

---

## 1. Authority field

Every diagnostic or shadow-derived field that can appear near action language must include:

```yaml
authority:
  TRUTH_LAYER
  FRAMEWORK_RATIFIED
  SHADOW_ONLY
  EXPLANATORY_ONLY
  FORWARD_TEST_ONLY
  DATA_MISSING
```

`SHADOW_ONLY`, `EXPLANATORY_ONLY` and `FORWARD_TEST_ONLY` cannot unlock recovery, rotation, rebuy, deployment or portfolio action.

---

## 2. Missing data

```text
DATA_MISSING = UNKNOWN
DATA_MISSING != NEGATIVE_EVIDENCE
```

Missing critical data may:

- reduce data quality;
- block a permission;
- trigger deeper collection;
- create a source-quality warning.

It may not:

- count as bearish confirmation;
- increase a pressure-layer count;
- create `ROTATION_FAILED`;
- create `PRESENT` or `STRONG` by itself.

---

## 3. Rotation output boundary

DATA PING may output only mechanical rotation components:

```text
ETHBTC_GATE_STATUS
ETHBTC_HOLD_DAYS
BREADTH_STATE
BTC_D_STATE
DEPLOYMENT_STATE
FLOW_CONGRUENCE
DATA_QUALITY
```

Optional mechanical fields:

```text
ETHBTC_DISTANCE_TO_REPAIR
ETHBTC_DISTANCE_TO_CONFIRMATION
BREADTH_SURVIVAL_STATUS
BTC_D_DIRECTION_AND_WINDOW
DEPLOYMENT_INPUT_AVAILABILITY
ROTATION_SURVIVAL_CANDIDATE
```

DATA PING must not output a binding:

```text
ROTATION_CONFIRMED
ALTSEASON_CONFIRMED
DEPLOY_NOW
```

Those remain main-framework judgments.

When required data is absent:

```text
ROTATION_EVALUATION_STATUS: DATA_INCOMPLETE
```

not `NO_ROTATION` unless the available verified data positively supports that state and main framework has ratified it.

---

## 4. BTC lane versus alt lane

DATA PING must preserve separate evidence blocks:

```yaml
BTC_LANE_EVIDENCE:
  price_structure:
  reclaim_survival:
  ETF_spot_absorption:
  leverage_quality:
  macro_context_available:

ALT_LANE_EVIDENCE:
  ETHBTC:
  breadth:
  BTC_D:
  deployment:
  flow_congruence:
  data_quality:
```

Weak alt transmission may block alt permission without automatically negating a BTC-specific forward-test candidate.

BTC strength may not be used to confirm alt rotation.

---

## 5. Multi-ping aggregation

```text
OLD_NAME: CONSENSUS_LAYER
ACTIVE_NAME: MULTI_PING_AGGREGATION
TYPE: FEATURE_ONLY
INDEPENDENT_AUTHORITY: NO
```

If used, output:

```yaml
MULTI_PING_AGGREGATION:
  window_runs:
  latest_ping_state:
  aggregated_state:
  state_flip_reduced:
  delay_minutes:
  data_quality:
  authority: FORWARD_TEST_ONLY
```

Do not claim value until benchmark rows compare it with latest-ping-only behavior.

---

## 6. Extended ping discipline

```text
NORMAL_MODE: DEFAULT
EDGE_MODE_COMPACT: ACTIVE_EDGE_WITHOUT_NEW_MAJOR_CHANGE
EDGE_MODE_FULL: NEW_GATE_EVENT_OR_MATERIAL_CONFLICT_ONLY
```

Extended fields are justified only by:

- real gate proximity or break;
- material state transition;
- material source conflict;
- active event maturity calculation;
- explicit one-run special request.

Routine field expansion without decision or ledger value is forbidden.

---

## 7. RAW horizon rows

RAW 1–3D and RAW 5–7D rows must be:

- timestamped;
- pre-registered at creation;
- source-backed;
- linked to a forecast or event ID;
- frozen before outcome;
- separated from framework action.

Required labels:

```text
RAW_HORIZON_TYPE: 1_3D / 5_7D
FORECAST_STATUS: FROZEN / OUTCOME_PENDING / MATURED
AUTHORITY: TRUTH_LAYER_OBSERVATION / FORWARD_TEST_ONLY
FRAMEWORK_ACTION: SEPARATE
```

A narrative written after price movement is not a valid RAW forecast row.

---

## 8. Final boundary

```text
DATA PING collects and measures.
Main framework interprets and permits.
Missing data is unknown.
Rotation remains multi-axis and framework-ratified.
More fields are not automatically more intelligence.
```
