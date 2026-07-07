# Governance Intake Response — Custom GPT Sensor Supplement 2026-07-07

Date: 2026-07-07  
Status: GOVERNANCE INTAKE ACCEPTED  
Source: Custom GPT Structured Data Supplement — Research Operating System v1.1  
Classification: DATA INPUT ONLY / NON-BINDING

---

## 1. Executive governance verdict

The Custom GPT supplement is accepted as a useful sensor/archive extraction artifact.

It should update:

- Data Asset Manifest
- Replay Harness readiness
- Open Questions Register action ordering
- future Custom GPT extraction prompts

It does not update:

- rebuy status
- rotation status
- Recovery Confirmed
- v0.2 ratification
- FNP ratification
- portfolio action

DATA PING remains sensor input only.

---

## 2. Most important new information

### 2.1 DATA PING V4 confirmed as active sensor layer

DATA_PING_V4 is currently the highest active live sensor output observed.

Base spec:

`DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY`

Active patches/layers include:

- V4.1 raw forecast improvement patch
- V4.2 fallback labels
- CFGI sentiment public layer
- FRED Classic v1.2 macro shadow layer

Governance consequence:

A canonical DATA PING version manifest should be created in GitHub.

---

### 2.2 Latest DATA PING rows are available but not enough for full replay

Custom GPT extracted three recent rows:

- 2026-07-06T21:26Z
- 2026-07-07T00:01Z
- 2026-07-07T06:31Z

These rows are useful for current-state replay seeds, but they do not cover the full P1b replay window.

Governance consequence:

The first replay window remains PARTIAL_READY_WITH_MISSING_DATA.

---

### 2.3 Master Monday and Cycle Navigator forecast archives are still missing

Custom GPT did not find accessible Master Monday or Cycle Navigator forecast rows.

Governance consequence:

Cycle Navigator Range Skill Audit is not ready until forecast-side archive is provided.

This becomes a high-priority extraction problem.

---

### 2.4 W27 actuals are available but need reconciliation

Custom GPT returned W27 actuals from Binance CEST daily klines / W27 final price close pack:

- BTC high 63461.99
- BTC low 57800.19
- ETH high 1807.65
- ETH low 1548.37

Earlier user/project-verified W27 values exist in project memory and may differ slightly.

Governance consequence:

Do not overwrite verified actuals silently.

Create a source reconciliation row when W27 is used:

`W27_ACTUALS_SOURCE_RECONCILIATION_REQUIRED`

---

### 2.5 ETF archive is partial-ready but source-cutoff must be locked

The supplement confirms:

- Farside public BTC ETF flow table available
- Farside public ETH ETF flow table available
- BTC/ETH archive dumps exist but contain placeholder rows
- 06 Jul placeholder vs finalized Farside mismatch must be reconciled

Governance consequence:

ETF replay must use latest completed trading day only, with finalization status.

Never score a placeholder 0.0 row as final.

---

## 3. Updated readiness classification

| Workstream | New status | Governance response |
|---|---|---|
| Evidence Registry | READY / UPDATED BY SUPPLEMENT | Add sensor supplement as archive input. |
| Open Questions Register | READY / NEEDS ACTION QUEUE UPDATE | Prioritize version manifest, ETF reconciliation and archive extraction. |
| No-Hindsight Replay | PARTIAL_READY_WITH_MISSING_DATA | Use templates; do not execute full replay yet. |
| P1b gate window replay | PARTIAL_READY | Requires daily rows/ledgers for full window. |
| Cycle Navigator Range Skill Audit | NOT_READY | Forecast archive missing. |
| ETH/BTC persistence test | READY_PRICE_ONLY if extractor output exists | Needs historical ETHBTC CSV. |
| ETF stabilization study | PARTIAL_READY_WITH_CAUTION | Must reconcile final/placeholder rows. |

---

## 4. New required archive tasks

### Task 1 — DATA PING Version Manifest

Create:

`data_ping_version_manifest_v1.md`

Purpose:

- identify active DATA PING version
- base spec
- active patches
- shadow layers
- archive-only versions
- governance rule: highest version wins

### Task 2 — ETF Finalization / Placeholder Rule

Create:

`etf_flow_finalization_and_placeholder_rule_v1.md`

Purpose:

- define how placeholder rows are handled
- define latest completed trading day
- define Farside public table vs archive dump hierarchy
- prevent 0.0 placeholder misuse

### Task 3 — Replay Source-Cutoff Rule

Create:

`replay_source_cutoff_rules_v1.md`

Purpose:

- define what data is allowed at each as-of timestamp
- define finalized vs pending data
- define no-hindsight source inclusion

### Task 4 — Cycle Navigator Archive Request

Create or send a request for:

- issue number
- publish date
- week covered
- BTC/ETH forecast ranges
- displayed score
- cycle phase
- rotation status
- actuals if known

### Task 5 — Master Monday Archive Request

Create or send a request for:

- date
- week number
- forecast ranges
- regime label
- score or confidence
- raw file/source path

---

## 5. Immediate governance response to Custom GPT NEEDS_GOVERNANCE_INPUT

### 1. Export canonical active DATA PING version manifest

Accepted.

Should be created next.

### 2. Provide Master Monday forecast files/paths

Open.

User or archive extraction needed.

### 3. Provide Cycle Navigator weekly post files/paths

Open.

User or archive extraction needed.

### 4. Reconcile 06 Jul ETF placeholder dumps vs finalized Farside rows

Accepted.

Create rule before ETF replay.

### 5. Lock daily replay source-cutoff rules

Accepted.

Create rule before replay execution.

### 6. Generate fixed daily ledgers for breadth, BTC.D, stablecoin official, funding/OI and ETF flows

Accepted as medium-term requirement.

Do not block price-only/ETF-only partial replay, but mark missing fields.

### 7. Keep DATA PING as sensor/archive layer only

Already ratified.

No change.

---

## 6. What can happen next

Recommended next immediate action:

1. Create DATA PING Version Manifest.
2. Create ETF finalization/placeholder rule.
3. Create replay source-cutoff rules.
4. Then run partial P1b gate replay if enough daily data exists.

Do not start Cycle Navigator range audit until forecast archive exists.

Do not ask Claude to run ETH/BTC persistence until historical ETHBTC data file is available.

---

## 7. Final governance conclusion

Custom GPT supplement materially improves archive readiness, but confirms that the replay system is not fully data-complete yet.

The archive is now ready for governance hardening tasks before empirical replay execution.

Current status:

- A Evidence Registry: usable
- B Open Questions: usable
- C Replay Harness: execution-ready template
- Full replay: partial-ready, data missing
- CN range audit: not ready, forecast archive missing
- ETF study: partial-ready, needs finalization rule

No portfolio action.

No market call.
