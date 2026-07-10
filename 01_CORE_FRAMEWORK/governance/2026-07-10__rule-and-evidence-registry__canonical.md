# Rule and Evidence Registry

**Dato:** 2026-07-10  
**Status:** CANONICAL  
**Område:** governance / evidence / rule survival  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Depends on:** GPT-5.6 Fresh Eyes Audit Implementation

---

## Registry contract

This is a registry, not an engine.

Each active rule must expose:

```text
rule_id
status
definition
decision_effect
source
rows_total
valid_rows
baseline
evidence_status
owner
promotion_condition
kill_condition
last_review
```

Allowed evidence states:

```text
FUNCTIONING
PARTIALLY_SUPPORTED
WRITTEN_NOT_PROVEN
SPEC_INCOMPLETE
NEEDS_ROWS
DATA_BLOCKED
NOT_SUPPORTED
SUSPENDED
LEGACY
```

---

## Active registry

| rule_id | status | decision_effect | rows_total / valid_rows | baseline | evidence_status | owner | promotion / kill condition |
|---|---|---|---:|---|---|---|---|
| DP_TRUTH_LAYER | ACTIVE | DATA PING supplies evidence but cannot ratify recovery, rotation, rebuy or deployment | event and source rows exist | source QA | FUNCTIONING | DATA PING / Governance | Kill only if role separation repeatedly fails |
| DYNAMIC_GATE_RUNTIME | ACTIVE | Current gates change through framework runtime registry without methodology rewrite | runtime rows exist | n/a | FUNCTIONING | Governance | Kill if silent gate inference occurs |
| EDGE_ALERT_SEPARATION | ACTIVE | Separates persistent edge state from user notification state | active event rows exist | prior stateless behavior | FUNCTIONING | DATA PING / Governance | Modify if repeated duplicate alerts remain |
| EDGE_DOWNGRADE_CHECK | ACTIVE | Prevents warning inertia after market repair | active event contains downgrade path | no-downgrade counterfactual pending | PARTIALLY_SUPPORTED | DATA PING | Needs additional event outcomes; kill if no behavior change across 10 eligible events |
| SOURCE_INVARIANCE | ACTIVE | Keeps source hierarchy and fallback behavior deterministic | source logs exist | n/a | FUNCTIONING | DATA PING | Kill only if unworkable; fallback substitutions must stay logged |
| HISTORICAL_ANCHOR_OWNERSHIP | ACTIVE | Prevents sensor-selected canonical history | correction chain exists | prior error | FUNCTIONING | Governance | Any repeated self-selected anchor is governance failure |
| F12_ETF_DEFAULT_FALSIFICATION | SUSPENDED_OPERATIONAL_EVALUATION | May contest or falsify ETF-era default only after reproducible spec exists | DATA_MISSING | DATA_MISSING | SPEC_INCOMPLETE | Governance / Research Lab | Promote after exact inputs, windows, state transitions and independent reproducibility; otherwise remain NOT_EVALUABLE |
| F12_5_CONTESTED_STATE | SUSPENDED_OPERATIONAL_EVALUATION | Intermediate state between default and falsified | DATA_MISSING | DATA_MISSING | SPEC_INCOMPLETE / GOVERNANCE_RISK | Governance | Promote only with exact entry and exit rules; kill if it becomes permanent ambiguity |
| KILL_CRITERIA_AT_BIRTH | ACTIVE_PRINCIPLE | Every new active rule/test needs explicit death conditions | registry initialized | n/a | FUNCTIONING_AS_GOVERNANCE | Governance | Any new rule without kill condition is blocked |
| RANGE_FORECAST_EDGE | FORWARD_TEST_ONLY | Range may inform public forecast but cannot be marketed as proven edge | historical audit n=14; forward rows pending | DUMB_1.5 / DUMB_2.0 | NOT_SUPPORTED_HISTORICALLY | Cycle Navigator / Research Lab | FRLP K1-K8 decide survival; suspend human adjustment if baseline loss persists |
| VERIFIED_ACTUALS_ONLY | ACTIVE | Blocks self-scoring and unverifiable precision | scoring governance exists | external actuals | FUNCTIONING | Cycle Navigator / Governance | No exception without explicit provisional label |
| SEQUENCE_IMMUTABILITY | ACTIVE | Freezes path expectations before outcome | schema and some rows | latest-state rewrite | FUNCTIONING_GOVERNANCE / NEEDS_MORE_ROWS | Forecast / Sequence Ledger | Kill only if immutability cannot be audited |
| ROTATION_SURVIVAL | ACTIVE_INTERPRETATION | Requires survival beyond first ETH/BTC signal | degraded replay rows exist | first-cross rule | PARTIALLY_SUPPORTED | Governance / Research Lab | Needs forward multi-axis rows; kill/modify if no incremental value |
| PULLBACK_POLICY_V0_2 | GUIDANCE_ONLY | Describes mild/moderate/large/extreme posture but cannot mechanically classify or trigger action | no reproducible band series found | n/a | SPEC_INCOMPLETE | Governance | Promote after exact measurement and hard-trigger definitions; otherwise keep guidance-only |
| BTC_PARTIAL_PERMISSION | FORWARD_TEST | Tests asset-tiered BTC permission versus WAIT | 0 valid divergence rows at audit | WAIT | NEEDS_ROWS | Research Lab / Governance | Suspend if no decision divergence in defined review window; promote only on outcome-adjusted benefit |
| GRADUATED_ALT_DEPLOYMENT | BLOCKED | Tests staged alt permission | 0 valid rows | WAIT | DATA_BLOCKED | Research Lab | Remains blocked until breadth, BTC.D and deployment fields are complete |
| FNP_OPPORTUNITY_COST | ACTIVE_LEDGER_REQUIREMENT | Measures genuine missed action versus correct restraint | insufficient cumulative live rows | WAIT / frozen horizon | NEEDS_ROWS | Governance / Research Lab | Kill or redesign if horizons are not frozen or no usable divergence is produced |
| TECHDEV_MACRO_COMPASS | ACTIVE | Supports roadmap and PREPARE context, never standalone DEPLOY | source claims exist; scoring ledger new | simple timing/range benchmarks pending | PARTIALLY_SUPPORTED | Governance / Research Lab | Execution authority remains zero; reduce weight if claim ledger shows poor calibration |
| MULTI_PING_AGGREGATION | FEATURE_TEST_ONLY | May reduce false state flips | 0 benchmarked rows | latest ping alone | WRITTEN_NOT_PROVEN | DATA PING / Research Lab | Kill as named concept if no false-flip improvement or delay is excessive |
| CHIEF_ACTION_COMPRESSION | ACTIVE_CONTRACT | Compresses framework judgment into clear action language | no reproducibility series found | same input repeated | NEEDS_TEST | Governance | Modify if identical inputs yield materially inconsistent classes |
| CN_PUBLIC_TRACK_RECORD | LOCKED | Prevents unverified historical precision marketing | historical reconciliation incomplete | independent ledger | GOVERNANCE_LOCK | Cycle Navigator | Unlock only after verified actuals, baselines and separate score categories are reconciled |
| MASTER_MONDAY_RATIFICATION | ACTIVE | Only ratified final normally drives CN and official scoring | version-chain protocol exists; W28 lineage unresolved | raw-only source | FUNCTIONING_RULE / CURRENT_LINEAGE_GAP | Master Monday / Archive | Any forecast lacking ratification path is unscored until corrected |

---

## Review rule

Every weekly review must update only fields supported by new evidence.

Do not convert `NEEDS_ROWS` into `FUNCTIONING` because a schema or prompt exists.

Do not convert `SPEC_INCOMPLETE` into a market state.

Do not convert `DATA_BLOCKED` into daily pseudo-rows.
