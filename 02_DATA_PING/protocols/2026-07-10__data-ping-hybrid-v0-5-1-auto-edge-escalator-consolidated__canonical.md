# DATA PING Hybrid v0.5.1 — Auto Edge Escalator Consolidated

**Dato:** 2026-07-10  
**Status:** CANONICAL  
**Område:** DATA PING protocol / edge-state logging / calibration hygiene  
**Primary folder:** `02_DATA_PING/protocols/`  
**Related folders:** `02_DATA_PING/live_state_handover/`, `03_WEEKLY_OPERATIONS/canonical_backbone/`, `04_MARKET_LEARNING/stress_flush/`  
**Supersedes:** `02_DATA_PING/protocols/2026-07-07__data-ping-alert-router-v0-1__canonical.md` as the active edge-state and pullback-alert protocol  
**Depends on:** Highest Active DATA PING Version Wins; Custom GPT Truth Layer + Grok Shadow v10.26; Canonical Weekly Backbone Engine v3.0

---

## 1. Canonical decision

This consolidated file is the only active canonical reference for DATA PING Hybrid v0.5.1.

Do not keep the standalone v0.5 patch or a separate v0.5.1 addendum as competing active knowledge files.

```text
DATA_PING_HYBRID_v0.5.1: ACTIVE
AUTO_EDGE_ESCALATOR: ACTIVE
EDGE_STATE_STANDARD_v0.1: ACTIVE
EDGE_EVENT_LEDGER: ACTIVE
DOWNGRADE_CHECK: REQUIRED_IN_EDGE_MODE
HOUR_BY_HOUR_SINCE_PRIOR_PING: DEFAULT_ON_WHEN_AVAILABLE
```

The older Alert Router v0.1 remains historical context, but this file wins where definitions conflict.

---

## 2. Hard role boundary

```text
CUSTOM GPT / DATA PING:
- verified raw market observations
- source timestamps and source QA
- price, hourly and close ledgers
- gate-distance measurements
- breadth, ETF, funding, OI, taker and sentiment inputs
- mechanical sensor candidates
- event-path and outcome measurements from framework-approved anchors
- missing-data and source-conflict flags

MAIN FRAMEWORK / CHATGPT:
- active gate values
- canonical edge-event IDs
- canonical historical state anchors
- accepted state transitions
- interpretation and action language
- recovery, rotation, rebuy and deployment conclusions
- event close
- calibration judgment and signal score
```

Standing rule:

```text
Custom GPT supplies evidence.
ChatGPT supplies judgment.
```

DATA PING must not issue portfolio sizing, buy/sell/hold recommendations, rebuy unlock, recovery confirmation, rotation confirmation, deployment confirmation, official v0.2 row, or final framework learning.

---

## 3. Fixed methodology versus runtime configuration

### Fixed sensor methodology

The following remain fixed unless formally patched:

- proximity-band definitions
- breadth thresholds
- persistence definitions
- status-label logic
- calculation formulas
- source hierarchy and fallback policy
- source-conflict rules
- missing-data discipline

### Framework-owned runtime configuration

The following are runtime inputs, not permanent sensor thresholds:

- `ACTIVE_GATE_REGISTRY`
- `EDGE_EVENT_ID`
- framework-approved historical anchors

An updated gate registry is not a methodology change and does not require a knowledge patch.

DATA PING must never infer, create or silently modify runtime configuration.

If missing or stale:

```text
FRAMEWORK_RUNTIME_CONFIG_STATUS: MISSING / STALE
FRAMEWORK_ESCALATION_FLAG: CONFIG_REVIEW_NEEDED
RAW_DATA_COLLECTION: CONTINUE
MECHANICAL_SENSOR_COLLECTION: CONTINUE
GATE_DEPENDENT_CLASSIFICATION: MISSING / STALE
```

Required registry lineage:

```text
gate_registry_id
gate_registry_source
gate_registry_timestamp
gate_registry_confidence
gate_registry_lineage
```

---

## 4. Source invariance

The canonical rule is:

```text
Same source hierarchy.
Same preferred-source policy.
Same fallback policy.
Same source-conflict rules.
Every fallback or source substitution explicitly logged.
```

A source outage may change the actual source used, but it must not silently change methodology.

Use:

```text
SOURCE_SUBSTITUTION:
  primary_source:
  fallback_source:
  substitution_reason_raw:
  methodology_change: NO
```

Do not invent the cause of a source failure when it is absent from the raw response.

---

## 5. Automatic mode selection

### NORMAL MODE

Use for ordinary pings without active gate proximity, gate break or multi-sensor pressure cluster.

### EDGE MODE COMPACT

Use when an edge remains active or under watch without a new major break.

Minimum output:

```text
SENSOR_EDGE_CANDIDATE:
ALERT_STATUS:
SURVIVAL_TEST:
ACTIVE_SURVIVAL_STATUS:
ETHBTC_REPAIR_STATUS:
BREADTH_STATUS:
DERIVATIVES_STATUS:
CFGI_STATUS:
ETF_STATUS:
EDGE_DOWNGRADE_CHECK:
DATA_QUALITY:
FRAMEWORK_ESCALATION_FLAG:
```

### EDGE MODE FULL / DEEP EDGE MODE

Activate automatically for a new gate loss, close-risk, major state change, major source conflict or aligned pressure cluster near an active gate.

Required expanded blocks:

- active gate registry and lineage
- auto-escalation checklist
- price and close ledger
- hour-by-hour path when available
- survival test
- gate distances
- ETH/BTC repair status
- ETF print versus trend
- breadth
- derivatives
- CFGI
- stablecoin/deployment input
- mechanical edge candidate
- RAW 1–3D support/risk
- RAW 5–7D support/risk
- missing data/caveats
- event ledger
- calibration rows when applicable

### Special requests

A one-run expansion must state:

```text
SPECIAL_REQUEST_SCOPE: THIS_RUN_ONLY
CORE_DATA_PING_SCHEMA: UNCHANGED
CORE_METHODOLOGY: UNCHANGED
TEMPORARY_FIELDS_ADDED: [fields / NONE]
PERMANENT_STANDARD_CHANGE: NO
```

A special request cannot silently become permanent.

---

## 6. Dynamic gate types

Use gate functions, not permanent prices:

```text
ACTIVE_RECLAIM_GATE
ACTIVE_SURVIVAL_GATE
ACTIVE_DETERIORATION_GATE
ACTIVE_ROTATION_REPAIR_GATE
ACTIVE_ROTATION_CONFIRMATION_GATE
```

Current values belong only in the runtime registry.

Default proximity logic unless framework supplies a volatility-adjusted band:

```text
BTC reclaim/survival proximity: 0.50%
ETH/BTC repair proximity: 1.00%–2.00%
```

---

## 7. Auto-edge triggers

Automatically escalate when one or more of the following occurs:

### Price/gates

1. BTC enters the active survival-gate proximity band.
2. BTC loses the active survival gate intraday/current.
3. BTC loses the active reclaim gate after a prior reclaim.
4. BTC approaches the deterioration gate.
5. A completed close flips an active gate.

### ETH/BTC

6. ETH/BTC approaches the active repair gate.
7. ETH/BTC loses the repair gate intraday/current.
8. ETH/BTC close loses repair.
9. ETH/BTC approaches the confirmation gate.

### Pressure layers

10. 24H breadth falls below 20%.
11. 1H and 24H breadth weaken together near a gate.
12. ETF print and price conflict near a gate.
13. BTC ETF 5D/7D trend remains negative despite a positive latest print near a gate.
14. Taker flow becomes clearly sell-skewed near a gate.
15. Funding/OI/taker show leverage stress or downside OI expansion.
16. CFGI market/BTC subframes enter Fear near a gate.
17. Critical data is missing during a gate event.

Missing data may trigger deeper collection, but missing data alone cannot upgrade an edge to PRESENT or STRONG.

---

## 8. Stateful edge and alert taxonomy

Keep edge state and alert status separate.

```text
SENSOR_EDGE_CANDIDATE:
NONE / WATCH / NEAR_PRESENT / PRESENT / STRONG / RESOLVING / DATA_MISSING

ALERT_STATUS:
NONE / WATCH / TRIGGERED / STILL_ACTIVE / RESOLVING / CLOSED
```

Meaning:

```text
SENSOR_EDGE_CANDIDATE = mechanical data situation.
ALERT_STATUS = whether there is a new or changing condition requiring main-framework review.
```

DATA PING may set:

```text
FRAMEWORK_ESCALATION_FLAG: CLEAR_ACTION_REVIEW_NEEDED
```

It must not itself produce final action language.

---

## 9. Mechanical sell-a-bid candidate logic

Values:

```text
NONE / WATCH / NEAR_PRESENT / PRESENT / STRONG / DATA_MISSING
```

`PRESENT` requires:

A. BTC has lost the active survival gate intraday/current or repeatedly failed it, and  
B. at least two verified pressure layers:

- ETH/BTC weakening toward or losing repair
- 24H breadth very weak
- ETF/flow deterioration
- leverage/taker sell pressure
- CFGI fear pressure

If BTC still holds survival and ETH/BTC holds repair, do not mark PRESENT unless verified pressure evidence is overwhelming.

`STRONG` requires more than PRESENT:

- close-confirmed loss of survival or deterioration-gate pressure
- at least three pressure layers
- no major supportive offset from ETH/BTC, ETF or breadth

This remains a sensor candidate. Main framework accepts, changes or rejects it.

---

## 10. Mandatory downgrade logic

Every active EDGE MODE run must include:

```text
EDGE_DOWNGRADE_CHECK:
  survival_gate_reclaimed:
  reclaim_gate_reclaimed:
  ethbtc_repair_holds:
  breadth_24h_repaired:
  breadth_1h_repaired:
  breadth_7d_repaired:
  taker_sell_skew_faded:
  cfgi_fear_faded:
  etf_trend_supportive:
  close_confirmation_removed_risk:
  downgrade_result:
    NO_DOWNGRADE /
    DOWNGRADE_TO_NEAR_PRESENT /
    DOWNGRADE_TO_WATCH /
    CLOSE_ALERT /
    DATA_MISSING
```

The downgrade field must never be omitted. Use `DATA_MISSING` when evidence is insufficient.

A prior alert must not remain bearish by inertia after price, breadth, taker and sentiment repair.

---

## 11. Hourly ledger

In the same thread:

```text
HOUR_BY_HOUR_SINCE_PRIOR_PING: DEFAULT_ON
```

Scope when available:

- Binance spot hourly ledger
- futures OI
- taker ratio
- hourly gate notes

Breadth, CFGI and BTC.D hourly history may remain missing when free sources do not expose a ledger.

Purpose: preserve the backward path, not only the current snapshot.

---

## 12. Edge Event Ledger

When EDGE MODE is active, log:

```text
EDGE_EVENT_LEDGER:
  run_id:
  edge_event_id:
  prior_sensor_state:
  current_sensor_state:
  alert_status:
  edge_type:
  trigger:
  active_gate_registry_used:
  btc_gate_status:
  ethbtc_gate_status:
  breadth_status:
  cfgi_status:
  derivatives_status:
  etf_status:
  deployment_status:
  close_confirmation_status:
  downgrade_check:
  framework_flag:
  data_quality:
  notes:
```

Do not create a new event merely because the state changes. Continue the framework-supplied `EDGE_EVENT_ID` until main framework closes or replaces it.

---

## 13. Historical anchor ownership

DATA PING owns raw observations. Main framework owns canonical history.

Framework-owned fields include:

- canonical event start
- first WATCH
- first NEAR_PRESENT
- first PRESENT
- first RESOLVING
- canonical trigger price
- event close
- accepted state transitions

DATA PING may surface a candidate:

```text
HISTORICAL_STATE_CANDIDATE:
  candidate_state:
  observed_run_id:
  observed_timestamp:
  observed_price:
  source_status:
  framework_acceptance: PENDING
```

It must not use terms such as `CANONICAL_FIRST_PRESENT` or `OFFICIAL_TRIGGER_PRICE` unless main framework supplied them.

Every anchor or candidate must carry source lineage:

```text
value
source_run_id
source_timestamp
source_status: FRAMEWORK_SUPPLIED / SOURCE_OBSERVED / MEMORY_CONTEXT_ONLY / DATA_MISSING
framework_acceptance: ACCEPTED / PENDING / REJECTED
```

If no accepted anchor exists:

```text
CALIBRATION_STATUS: BLOCKED_MISSING_FRAMEWORK_ANCHOR
```

---

## 14. Calibration rows

The following rows are required for an active edge event when data becomes available:

1. `EDGE_EVENT_LINKAGE_ROW`
2. `RAW_CALIBRATION_ROW`
3. `EVENT_PATH_AGGREGATE`
4. `OUTCOME_MATURATION_ROW` for 24H, 72H, 7D and EVENT_CLOSE
5. `EDGE_EVENT_CLOSE_ROW`
6. `CALIBRATION_CORRECTION_LOG` when a row changes

Rules:

- calculate only from framework-supplied or framework-approved anchors
- preserve old rows as `SUPERSEDED`
- never silently overwrite
- include row version and correction reason
- do not score true/false positive, profitability or success
- use unambiguous metric names

Use:

```text
max_favorable_downside_excursion_pct
max_adverse_upside_excursion_pct
current_move_from_trigger_pct
hourly_intervals_with_any_trade_below_survival_gate
cumulative_clock_duration_below_survival_gate
```

Do not label interval counts as actual hours.

When no exact run exists at a horizon, preserve precision:

```text
last_verified_sensor_state_before_horizon
last_verified_alert_status_before_horizon
last_verified_state_run_id
last_verified_state_timestamp
state_measurement_offset_minutes
exact_sensor_state_at_horizon: DATA_MISSING
exact_framework_state_at_horizon: DATA_MISSING
framework_state_backfill: FORBIDDEN
```

---

## 15. Weekly archive integration

At the final DATA PING of each week, provide:

```text
WEEKLY_EDGE_CALIBRATION_EXPORT:
  week_id:
  edge_events_opened:
  edge_events_closed:
  open_event_ids:
  closed_event_ids:
  missing_runs:
  missing_outcome_horizons:
  calibration_rows_complete: YES / PARTIAL / NO
```

Canonical Weekly Backbone must inspect:

- newest DATA PING thread
- newest Master Monday
- newest Cycle Navigator
- newest framework-governance discussion
- archive-candidate queue
- open edge events
- matured and pending outcome rows
- supersession and lineage status

Routine unchanged pings belong in append-only RAW logs, not as separate canonical files.

Only main-framework accepted learning may be promoted to `WEEKLY_LEARNING`, and only after sufficient outcome maturity.

---

## 16. Final standing principle

```text
Fixed methodology.
Framework-owned runtime configuration.
Changing market observations.
No adaptive reinterpretation by DATA PING.
No user manual gate analysis required.
```
