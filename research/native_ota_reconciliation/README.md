# Native OTA Research Reconciliation — Design v1

**Status:** IMPLEMENTATION_SPEC / RESEARCH_ONLY  
**Prepared:** 2026-09-05  
**Goal:** remove the need for recurring manual Claude OTA pings by reproducing their useful research/reconciliation role natively inside GitHub Actions, while reusing current framework owners instead of building a parallel market engine.

## 1. Mission

The native replacement must answer the same useful questions the Claude OTA report has been answering:

- What changed since the previous accepted research run?
- Which observations are truly new versus already-owned framework evidence?
- Which values are settled versus still live/in-progress?
- Is an important registered gate moving closer to failure or recovery?
- Which research lanes are actually available, stale, blocked, deferred or already owned elsewhere?
- Which source-QA events matter?
- Does any new evidence justify an early research review before the next fixed slot?

The system must **not** become a new canonical market engine, a new portfolio engine, a new threshold owner or a second copy of Daily Director.

## 2. Architectural principle

**RECONCILE, DO NOT RE-COLLECT.**

The GitHub-native OTA layer should read outputs from current owners first. Only when a required field has no current owner may Astra propose a bounded new source call, and that proposal must be justified by marginal research value.

Known owner families that must be inspected/reused before any new collector is introduced include:

- daily/live market anchor and settled price history;
- Hourly and ETH/BTC persistence lifecycle;
- settled ETF calibration owner;
- pullback forensics, including executed liquidations and options/moneyness observations where available;
- Situation Room catalyst context;
- breadth / rotation owner outputs;
- Daily Director shadow outputs and conflict review;
- prospective evidence / outcome ledgers;
- relevant macro, volatility and liquidity owners already present on current main.

Astra must resolve the **current paths/contracts on main** during implementation. This spec intentionally does not freeze stale paths when an owner may have moved.

## 3. Proposed components

### A. `scripts/research/native_ota_reconcile.py`

Deterministic core. No LLM is required for validity.

Responsibilities:

1. discover/read current owner outputs;
2. normalize source timestamps and freshness;
3. classify each lane and evidence item;
4. separate LIVE from SETTLED observations;
5. compare with previous accepted native OTA report;
6. build deterministic `what_changed` deltas;
7. evaluate registered early-review conditions without inventing new thresholds;
8. write JSON + human-readable Markdown;
9. fail closed when lineage or settled status is ambiguous.

### B. `scripts/research/validate_native_ota_report.py`

Validator that must reject a report if any of the following occurs:

- a live/in-progress high is labelled as a settled or cycle high;
- a stale bridge is presented as current owner evidence;
- a lane is labelled MISSING when a fresher current owner exists;
- an external/manual OTA observation overrides newer GitHub owner evidence;
- a new threshold/market rule/portfolio action is emitted;
- prior report lineage is not reproducible;
- required source timestamps or evidence roles are absent;
- a field claimed as settled cannot be tied to a completed session.

### C. `.github/workflows/native-ota-research-reconciliation.yml`

Orchestration only.

Recommended initial trigger design:

- fixed research slots: **Monday and Friday**;
- `workflow_dispatch` for production proof / bounded manual rerun;
- event-driven invocation after relevant owner workflows complete, but the trigger evaluator should materialize a full report only when a registered early-review condition is actually met.

Do **not** poll external APIs merely to decide whether an early trigger exists when current owners already emit the required settled observations.

### D. Immutable outputs

Suggested output root:

`research/native_ota_reconciliation/outputs/YYYY/MM/`

Per accepted run:

- `NATIVE_OTA_RESEARCH_REPORT_<timestamp>.json`
- `NATIVE_OTA_RESEARCH_REPORT_<timestamp>.md`
- receipt / hashes if consistent with existing archive conventions

Pointer:

- `research/native_ota_reconciliation/LATEST_ACCEPTED.json`

The pointer may move. Timestamped accepted reports are immutable.

## 4. Proposed report contract

Contract name:

`NATIVE_OTA_RESEARCH_REPORT_v1`

Required top-level fields:

- `run_timestamp_utc`
- `run_slot` (`MONDAY_FIXED`, `FRIDAY_FIXED`, `EARLY_TRIGGER`, `MANUAL_PROOF`)
- `previous_accepted_report`
- `authority`
- `owner_context_freshness`
- `new_information`
- `evidential_items`
- `context_only_items`
- `lane_status`
- `source_qa_events`
- `what_changed`
- `registered_gate_watch`
- `early_review_evaluation`
- `limitations`
- `validation`

Mandatory authority object:

```json
{
  "canonical_state_change": false,
  "market_rule_change": false,
  "threshold_change": false,
  "portfolio_action": false,
  "experiment_promotion": false
}
```

## 5. Settled-vs-live discipline

This is non-negotiable because the manual OTA process repeatedly demonstrated the failure mode of treating an in-progress high as a final cycle high.

Every market extreme/value used in the report must include a state such as:

- `SETTLED_SESSION`
- `LIVE_IN_PROGRESS`
- `REFERENCE_BRIDGE`
- `HISTORICAL_SETTLED`

Rules:

1. `cycle_high` may only be computed from a completed/settled series.
2. a live high must be labelled `intraday_live_high` or equivalent.
3. later settlement may correct a prior live observation without marking the prior observation as a framework error; it is only an error if the live observation was falsely labelled settled/final.
4. source timestamp and session date must both be retained where applicable.

## 6. Source precedence and reconciliation

Suggested precedence:

1. fresh canonical/current GitHub owner output;
2. fresh research/shadow GitHub owner output with correct evidence role;
3. settled historical owner output;
4. explicit bridge/reference data;
5. external/manual OTA context.

Lower-precedence material must never overwrite higher-precedence evidence.

This directly prevents situations where a manual OTA says:

- ETF data are eight days old even though the native ETF owner has a fresh settled session;
- executed liquidations were not run even though pullback forensics already captured them;
- options/skew are blocked even though a current owner already produced a bounded research observation.

The native report should classify such cases as **EXTERNAL_CONTEXT_STALE_RELATIVE_TO_OWNER**, not as framework data gaps.

## 7. Lane model

The OTA lane table should become a reconciliation view, not a separate collection plan.

For every lane use explicit states such as:

- `OWNER_PASS`
- `OWNER_PARTIAL`
- `OWNER_STALE`
- `REFERENCE_BRIDGE_ONLY`
- `DEFERRED_BY_CONTRACT`
- `BLOCKED_BY_GOVERNANCE`
- `TRUE_DATA_GAP`
- `NOT_APPLICABLE_THIS_RUN`

Each lane must include:

- owner contract/path;
- owner timestamp;
- freshness;
- evidence role;
- whether a new external call was made;
- reason for status;
- whether the lane can affect research interpretation.

Astra must map the current owner for at least:

- price / settlement;
- ETH/BTC gate and persistence;
- ETH vs BTC relative leadership;
- liquidations;
- volatility/options context;
- catalyst context;
- ETF flows;
- breadth/rotation;
- liquidity/stablecoin context where already owned.

## 8. `what_changed` design

This should be deterministic first, narrative second.

Compare current normalized evidence with `LATEST_ACCEPTED.json` and emit structured deltas:

- newly settled information;
- corrected live-to-settled values;
- threshold/gate proximity changes;
- persistence changes;
- leadership changes;
- source freshness improvements/degradations;
- lane ownership/status changes;
- newly resolved or newly created blockers.

Optional AI interpretation may summarize these deltas by reusing an existing bounded research agent/Daily Director capability **only if** it does not create a duplicate market-analysis owner and remains budget-gated.

The deterministic report remains valid if the optional AI layer is unavailable.

## 9. Gate-watch semantics

The native layer may monitor **already registered gates**. It must not invent thresholds.

For ETH/BTC `0.0300` or any other registered gate, report at minimum:

- settled pass/fail count;
- last settled close;
- settled margin to gate;
- most recent settled low/high as relevant;
- live proximity separately;
- persistence/leadership context;
- whether the event is merely `PROXIMITY_RISING` or an actual `SETTLED_GATE_FAILURE`.

A proximity trend is research context, not a threshold event.

## 10. Early-review triggers

Initial design should preserve the useful concept from Claude OTA without causing expensive polling.

Possible trigger classes, only when already registered/owned:

- first settled gate failure after a defined pass streak;
- registered volatility expansion event;
- material source-QA failure that changes interpretation ability;
- governance activation of a previously blocked forensic lane;
- other already-frozen framework trigger conditions discovered by Astra.

The trigger evaluator must read native owner outputs. It should not add a new market rule.

## 11. Source QA

Every run must distinguish:

- `FRESH`
- `WARN`
- `STALE`
- `BRIDGE`
- `BLOCKED`
- `MISSING`

and record source age where meaningful.

Required QA checks include:

- settled/live label correctness;
- venue/source disagreement where current owners expose it;
- bridge age;
- current-main context age;
- owner timestamp age;
- pointer-to-target integrity;
- report lineage to previous accepted report;
- duplicate/stale source suppression.

## 12. Governance and authority

The entire native OTA system is **RESEARCH_ONLY / NON_CANONICAL**.

It may:

- surface research deltas;
- classify source quality;
- identify a registered gate event;
- request deeper forensic review;
- feed matured research into existing learning/governance lanes.

It may not:

- change portfolio action;
- change canonical market state;
- introduce or tune thresholds;
- change model weights;
- promote an experiment;
- create hindsight-labelled prospective evidence;
- override current owner contracts.

## 13. Cost discipline

Target: near-zero marginal market-data cost on ordinary fixed runs.

The first question for every OTA field is: **does GitHub already own this value?**

New paid/API calls require:

- a true owner gap;
- explicit hypothesis/value justification;
- bounded call budget;
- source rights/provenance review;
- no duplication of existing capture cadence.

## 14. Tests Astra must implement

At minimum:

1. live high cannot become `cycle_high`;
2. settled correction supersedes a prior live value cleanly;
3. fresh GitHub ETF owner beats stale external bridge;
4. current liquidation owner prevents false `lane missing` claim;
5. current options owner prevents false blocked claim when the owner is valid;
6. true missing lane remains missing — no fabrication;
7. stale owner is marked stale, not fresh;
8. previous accepted report is deterministic and hash/lineage bound;
9. `what_changed` is reproducible from two fixtures;
10. registered gate proximity is not equivalent to failure;
11. early trigger fires on settled failure, not live intraday breach alone;
12. all authority booleans remain false;
13. no duplicate external source calls when owners are available;
14. repeated workflow run with same evidence is idempotent/no duplicate accepted report unless archive conventions explicitly require a receipt;
15. current-main drift between branch creation and merge is audited.

## 15. Rollout proposal

### Phase 1 — implementation + fixtures

Build scripts, workflow, schemas and tests on a branch.

### Phase 2 — historical replay against existing OTA examples

Use available prior Claude OTA reports only as **comparison fixtures**, not truth. Reconcile each discrepancy against current owner evidence.

### Phase 3 — production proof

Run at least two manual production proofs from current main-equivalent code:

- one ordinary fixed-slot simulation;
- one early-trigger fixture/production-safe simulation.

Verify output, receipts, pointers and no unintended calls/state changes.

### Phase 4 — cutover

Once production proof is PASS:

- mark recurring manual Claude OTA as `NOT_REQUIRED_FOR_ROUTINE_OPERATION`;
- retain Claude/Astra as optional external challenger/deep-research tools;
- do not delete historical Claude OTA records.

## 16. Definition of done

The project is complete only when all of the following are true:

- native workflow exists and is indexed by GitHub Actions;
- fixed Monday/Friday execution is configured;
- event/early-trigger path exists without external polling duplication;
- deterministic JSON + Markdown report is produced;
- report reads current owner outputs and reports their provenance;
- settled/live QA is enforced by tests and runtime validator;
- current owner evidence outranks stale external/manual context;
- `what_changed` works against previous accepted native report;
- all authority fields are false;
- PR gates pass on exact head SHA;
- PR is merged only after current-main drift audit;
- production proof runs pass;
- current-main readback confirms workflow/scripts/schema are present;
- a final migration note states whether recurring Claude OTA can be retired.

## 17. Decision rule for Astra

Astra should **simplify** this design if current-main inspection shows an existing owner already provides the same function.

Astra should **not** preserve a proposed component merely because it appears in this document.

The objective is the smallest safe native layer that reproduces the useful OTA research function while eliminating manual Claude dependence and avoiding duplicate market machinery.
