# DATA PING Version Manifest v1

Date: 2026-07-07  
Status: ACTIVE VERSION-GOVERNANCE MANIFEST  
Source basis: Custom GPT Sensor Supplement 2026-07-07 + existing framework governance.

---

## 1. Purpose

This file defines which DATA PING version/layers are active for Research Operating System v1.1 and no-hindsight replay.

It prevents stale DATA PING rows, old schemas or older archive threads from being treated as current live truth.

---

## 2. Core governance rule

`Highest active DATA PING version wins.`

Older DATA PING versions are archive context only unless they were the highest active operational version at the historical as-of timestamp being replayed.

No replay row may use a lower active version when a higher active version was available at the same timestamp.

---

## 3. Active version stack

| Layer/version | Status | Role | Confidence | Governance use |
|---|---|---|---:|---|
| DATA_PING_V4 | ACTIVE | LIVE_SENSOR_OUTPUT | 0.86 | Current live DATA PING sensor layer. |
| DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY | ACTIVE_BASE_SPEC | GOVERNANCE_BASE | 0.95 | Printed base spec for DATA PING rows. |
| DATA_PING_V4_1_RAW_FORECAST_IMPROVEMENT_PATCH_v1 | ACTIVE_PATCH | DATA_FIELDS_PATCH | 0.82 | Adds close ledger, ETF verification, breadth persistence, stablecoin official, range, derivatives, BTC.D consistency and raw input support summary. |
| DATA_PING_V4_2_FALLBACK_LABELS | ACTIVE_LABEL_PATCH | FALLBACK_LABELS | 0.70 | Fallback concepts/labels active; not found as standalone archive file. |
| DATA_PING_CFGI_SENTIMENT_LAYER_v1_FREE_PUBLIC | ACTIVE_LAYER | SENTIMENT_DATA_ONLY | 0.74 | Public sentiment layer. Shadow/data-only. |
| DATA_PING_FRED_CLASSIC_V1_2_MACRO_LAYER | ACTIVE_MACRO_LAYER | MACRO_SHADOW | 0.92 | Macro shadow layer. Not crypto execution trigger. |
| OLDER_DATA_PING_VERSIONS | ARCHIVE_CONTEXT_ONLY | HISTORICAL_CONTEXT | 0.80 | Use only as historical/as-of context when historically active. |

---

## 4. Layer permissions

### DATA_PING_V4

Allowed:

- collect market inputs
- print current sensor state
- provide BTC/ETH/ETHBTC/BTC.D/ETF/breadth/funding/range/stablecoin inputs
- provide data-quality and source-conflict status

Not allowed:

- ratify framework state
- unlock rebuy
- authorize portfolio action
- confirm rotation
- confirm recovery
- create official v0.2 row

### Base spec and patches

Allowed:

- define output fields
- define mandatory/optional source behavior
- define fallback labeling
- define data-quality markers

Not allowed:

- override ChatGPT governance ratifications
- replace Evidence Registry rule status

### CFGI sentiment layer

Allowed:

- sentiment data/context
- shadow-only interpretation

Not allowed:

- market call
- rebuy/deployment input alone

### FRED macro layer

Allowed:

- macro shadow context
- Master Monday macro calibration support

Not allowed:

- rebuy
- recovery confirmation
- rotation confirmation
- deployment trigger
- official FNP/PATH/v0.2 row

---

## 5. Replay usage rules

For each replay row:

1. Identify the as-of timestamp.
2. Identify the highest active DATA PING version at that timestamp.
3. Use only rows/specs/layers available at or before that timestamp.
4. If version cannot be identified, mark:

`DATA_PING_VERSION_UNRESOLVED`

5. If current DATA PING row is missing, mark:

`DATA_PING_ROW_MISSING`

6. Do not infer state from missing DATA PING rows.

---

## 6. Version conflict handling

If multiple DATA PING versions conflict:

- highest active version wins for live/as-of interpretation
- older version remains archive context
- conflict must be logged in source_conflicts
- no rule may be ratified from conflicting sensor rows alone

Conflict label:

`DATA_PING_VERSION_CONFLICT`

---

## 7. Required manifest fields for future updates

Every future DATA PING version entry must include:

- version name
- activation date/time if known
- base spec
- active patches
- role
- layer permission
- supersedes / superseded by
- archive-only status
- confidence
- notes

---

## 8. Current governance conclusion

DATA_PING_V4 is the active live sensor layer.

DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY is the active base spec.

DATA_PING V4.1 / V4.2 / CFGI / FRED layers are active as supporting patches/layers with their restrictions.

DATA PING remains sensor/archive layer only.

ChatGPT governance remains final ratification layer.
