# CLAUDE OTA DELTA CONTRACT v1

```yaml
status: ACTIVE_SHADOW_CONTRACT
purpose: COMPLEMENT_DATA_PING_WITH_SEMANTIC_ADVERSARIAL_AND_LONGITUDINAL_EVIDENCE
collector_authority: NONE
canonical_state_authority: NONE
portfolio_action_authority: NONE
```

## 1. Role separation

DATA PING is the deterministic collector and current-state evidence layer.

Claude OTA is the adversarial research, source-learning and experiment-maturation layer.

Claude must not repeat the full DATA PING payload. It should cite the DATA PING run ID and report only:

- genuinely new evidence;
- derived features absent from DATA PING;
- conflicts or material deviations;
- matured experiment outcomes;
- hypothesis updates;
- source-QA learning;
- design observations;
- unresolved evidence;
- next exact events.

## 2. Mandatory output modules

### A. DELTA_ONLY_NEW_INFORMATION

For every new item provide:

```yaml
item_id: stable_identifier
claim: concise_statement
new_vs_data_ping: exact_missing_dimension
source_ids: []
source_timestamps_utc: []
calculation_method: null_or_version
confidence: HIGH|MEDIUM|LOW
binding_status: NON_BINDING
```

No raw current price should be repeated unless needed to establish a conflict, a threshold event or a maturity outcome.

### B. EXPERIMENT_MATURITY_LEDGER

Claude should maintain the full prospective experiment calendar and report:

- event ID;
- preregistration version;
- maturity time;
- current status;
- whether the event matured in this run;
- whether a trigger is new or already active;
- overlap-cluster identity;
- no-retrigger decision;
- outcome horizon and closeout time;
- confounds active at maturity.

Every non-matured event should be omitted except the next three exact events.

### C. HYPOTHESIS_AND_SELF_FALSIFICATION_LEDGER

Claude should maintain claims as testable objects:

```yaml
hypothesis_id: stable_identifier
claim: text
status: PROPOSED|SUPPORTED|WEAKENED|FALSIFIED|RETIRED
prior_confidence: 0_to_1
new_confidence: 0_to_1
falsification_rule: exact_rule
new_evidence_for: []
new_evidence_against: []
causal_alternative: null_or_text
operational_consequence: text
```

A new explanation must not silently replace a falsified one. The old claim, counterexample and replacement hypothesis must all remain visible.

### D. SOURCE_QA_LEARNING

Claude should exploit web-reading and semantic source analysis to provide evidence that DATA PING does not normally collect:

- official publication schedules;
- update cadence and delay distributions;
- revisions and backfills;
- page footer meaning;
- source methodology changes;
- hidden timestamp conventions;
- source-specific stale-cache patterns;
- known missing-fund or missing-row conventions;
- outage explanations;
- primary-source documentation quotes within copyright limits.

Every source timing rule must be validated prospectively before automation changes.

### E. NORMALIZED_AND_STRUCTURAL_DERIVATIONS

Preferred derived outputs that are not in raw DATA PING:

1. ETF flow normalized by aggregate AUM.
2. ETF flow normalized by realized volatility and market capitalization.
3. Fund-concentration share and issuer contribution.
4. Three-, five-, seven- and twenty-session persistence.
5. Flow-price lag and divergence classification.
6. Direct ETH/BTC rejection and acceptance sequences.
7. Cross-asset breadth conditional on BTC direction.
8. Spot-led versus leverage-led move classification.
9. Event-window surprise relative to historical percentile.
10. Confound-adjusted interpretation around scheduled macro events.

Every derived metric must preserve formula, denominator lineage, window, timestamp and missing-data treatment.

### F. CROSS_SOURCE_ADJUDICATION

Claude should compare independent sources and classify disagreements as:

- TEMPORAL_DIFFERENCE
- DEFINITION_DIFFERENCE
- VENUE_DIFFERENCE
- REVISION_OR_BACKFILL
- STALE_CACHE
- CALCULATION_DIFFERENCE
- TRUE_UNRESOLVED_CONFLICT

The output must include exact field values, timestamps and the reason the disagreement class was chosen.

### G. POST_WINDOW_AND_BOUNDARY_STRESS

Claude should log observations that occur just outside frozen experiment windows without rescoring the experiment.

Required fields:

- experiment ID;
- frozen window end;
- later observation time;
- distance to threshold inside the window;
- distance after the window;
- design lesson;
- proposed future specification test;
- explicit `SCORE_UNCHANGED` marker.

### H. NARRATIVE_AND_CATALYST MAP

Claude may add context that deterministic DATA PING does not cover:

- central-bank decisions and speeches;
- regulatory or legal developments;
- ETF issuer changes;
- protocol upgrades and outages;
- major unlocks or treasury events;
- market-structure changes;
- credible institutional positioning narratives.

Every catalyst must have a primary source where possible and must be separated from price evidence. Narrative alone cannot change canonical state.

### I. UNVERIFIED_AND_PROVENANCE_QUEUE

Each unresolved item must have:

```yaml
queue_id: stable_identifier
claim_or_missing_input: text
why_it_matters: text
required_source: text
owner: CLAUDE|CHATGPT|DATA_PING|EXTERNAL
next_check_utc: null_or_timestamp
status: OPEN|BLOCKED|RESOLVED|RETIRED
```

### J. FRAMEWORK_CHALLENGE

Claude should explicitly state the strongest reason the current framework interpretation may be wrong, even when Claude agrees with it.

This section must distinguish:

- missing evidence;
- contradictory evidence;
- alternative causal explanation;
- threshold fragility;
- window-definition fragility;
- source-authority fragility.

## 3. ETF-specific extension

For every newly settled ETF session Claude should provide only the following delta package:

```yaml
session_date: YYYY-MM-DD
BTC_net_flow_usd_m: number
ETH_net_flow_usd_m: number
fund_contributions: []
reporting_completeness: FULL|PARTIAL
missing_funds: []
AUM_source: identifier
AUM_valuation_date: YYYY-MM-DD
BTC_AUM_usd_m: number
ETH_AUM_usd_m: number
BTC_flow_pct_AUM: number
ETH_flow_pct_AUM: number
relative_flow_multiple: number
windows_3_5_7_20: {}
flow_price_divergence: classification
revision_vs_prior_ota: null_or_object
```

The denominator must not be silently carried forward. A stale denominator must be labelled.

## 4. Direct ETH/BTC extension

For every threshold sequence Claude should preserve row-level owner data:

```yaml
venue_owner: BINANCE_SPOT_ETHBTC
settlement_timezone: named_timezone
rows:
  - session_date: YYYY-MM-DD
    high: number
    close: number
    touched_0_0300: boolean
    closed_above_0_0300: boolean
    source_timestamp_utc: timestamp
sequence_status: REJECTION|ACCEPTANCE|MIXED
```

Derived ETH/BTC ratios may be used only as diagnostics.

## 5. Source timing study for Farside

The edge-node deterministic rule is retired. A prospective timing study should record at least ten, preferably twenty, settled sessions.

For each query:

- request UTC;
- edge IP;
- response hash;
- footer date;
- latest session date;
- latest expected session date;
- stale/fresh label;
- source response time;
- whether the row was later revised.

No schedule change should be promoted until the timing study demonstrates stable improvement.

## 6. Machine-readable footer

Every OTA response must end with one strict JSON object containing:

```json
{
  "contract": "CLAUDE_OTA_DELTA_CONTRACT_v1",
  "source_snapshot_utc": null,
  "referenced_data_ping_run_id": null,
  "new_information": [],
  "matured_events": [],
  "hypothesis_updates": [],
  "source_qa_updates": [],
  "derived_metrics": [],
  "design_observations": [],
  "unverified_queue_updates": [],
  "framework_challenge": null,
  "next_exact_events": [],
  "canonical_state_change": false,
  "portfolio_action": false
}
```

## 7. Promotion limits

Claude OTA may recommend, challenge, falsify and supply evidence. It may not:

- change canonical state;
- issue portfolio action;
- convert a live touch into settled confirmation;
- retroactively alter a frozen score;
- count a repeated trigger as a new event;
- upgrade an unverified source rule;
- replace owner data with a derived ratio;
- insert evidence into a prior decision receipt after the fact.