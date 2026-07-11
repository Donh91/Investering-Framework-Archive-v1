# Truth-Layer Data Pack — Ingestion and Validation

**Date:** 2026-07-11  
**Package:** `INVESTERING_TRUTH_LAYER_DATA_PACK_20260711`  
**Status:** CANONICAL DATA-PACK INGESTION  
**Verdict:** PARTIAL_DATA_READY  
**Authority:** Data extraction / seed evidence only. No market call, portfolio action or rule ratification.

---

## 1. Independent integrity validation

The uploaded ZIP was unpacked and validated independently by ChatGPT governance.

Checks completed:

```text
11 required files present
All 10 manifest-listed data/report SHA-256 checksums match
CSV schemas parse successfully
Declared row counts match actual row counts
No interpolation detected in the BTC.D gap ledger
Breadth aggregates reproduce from the frozen rows
```

Validated row counts:

```text
BTC_D_DAILY_2023_CURRENT.csv: 1,287 rows
DECISION_LEDGER_SOURCE_BACKED.csv: 18 rows
LOSS_FUNCTION_SOURCE_INPUTS.csv: 8 rows
BREADTH_SNAPSHOT_FORWARD_001.csv: 100 rows
BREADTH_INCLUDED_UNIVERSE: 71 assets
STABLECOIN_DEPLOYMENT_PROXY_DAILY.csv: 6 rows
```

---

## 2. Critical interpretation correction

The BTC.D file is **not** a populated historical dominance series.

It is a schema-complete daily gap ledger:

```text
2023-01-01 through 2026-07-10
1,287 requested dates
all BTC market-cap / total-market-cap / BTC.D values = DATA_MISSING
```

Therefore:

```text
FULL_M1_UNLOCKED = NO
```

The file remains useful as an explicit no-fabrication gap record, but it contains no historical BTC.D observations suitable for replay or scoring.

---

## 3. Decision-ledger seed

The source-backed decision ledger contains:

```text
18 total rows
16 live rows marked M3-eligible
1 governance-only row
1 retrospective FNP row excluded from M3 scoring
```

However, the 16 eligible rows are heavily concentrated in a short July 2026 event sequence and do not represent the complete CHIEF / Master Monday / RAW / PTR / Sequence history.

Therefore:

```text
M3_UNLOCKED = NO
DECISION_LEDGER_SEED_VALID = YES
```

The seed is suitable for schema validation and forward continuation, not full challenger scoring.

---

## 4. Loss-function evidence

The pack confirms strong directional preferences:

```text
capital protection over capturing the final 10–20%
fewer false permissions
no hindsight leakage
false precision worse than null
graduated exits over all-at-once exits
```

Only one explicit numerical score weighting exists:

```text
Phase = 1
Timing = 1
Top = 2
```

This weighting is limited to the stated weekly precision score and must not be generalized into an M3 loss matrix.

Status:

```text
M3_NUMERIC_LOSS_MATRIX = NOT SOURCE_BACKED
GOVERNANCE_BINDING_REQUIRED
```

Governance response:
Use a dual-objective scorecard rather than inventing scalar weights until broader decision rows exist:

```text
CAPITAL_PROTECTION_OBJECTIVE:
- missed >=Storm / terminal-risk events
- realized max drawdown
- early-rebuy damage
- late-exit damage

OPPORTUNITY_COST_OBJECTIVE:
- false-positive trim
- missed upside
- missed rotation
- late rebuy

HARD DOMINANCE RULE:
A challenger cannot be preferred if it creates an additional missed >=Storm event or worsens maximum drawdown by more than 3 percentage points, even if opportunity-cost metrics improve.
```

This is a provisional governance evaluation rule, not a live trading rule.

---

## 5. Forward breadth snapshot

The frozen CoinGecko top-100 snapshot is valid for **forward logging only**.

Independent aggregate reproduction:

```text
Included assets: 71
Positive 7d breadth: 36.6197%
Positive 30d breadth: 61.9718%
Equal-weight 7d return: -0.126214%
Median 7d return: -1.361964%
30d-MA breadth: DATA_MISSING
```

Exclusions:

```text
BTC: 1
ETH: 1
stablecoin / fixed-NAV cash-like: 27
included: 71
```

Status:

```text
FORWARD_BREADTH_LOGGING_UNLOCKED = YES
HISTORICAL_BREADTH_BACKFILL = FORBIDDEN_WITH_CURRENT_CONSTITUENTS
```

Future snapshots must preserve exact CoinGecko IDs/ranks and must not rewrite historical universe membership.

---

## 6. Stablecoin deployment seed

The six current rows are valid supply seeds for:

```text
TOTAL
Ethereum
Solana
BSC
Base
Arbitrum
```

But chain history and DEX volume are missing.

Status:

```text
STABLECOIN_DEPLOYMENT_SHADOW_UNLOCKED = PARTIAL_CURRENT_SEED_ONLY
```

The rows must not be called:

```text
velocity
net inflow
proof of deployment
rotation confirmation
```

The only permitted label is:

```text
STABLECOIN_DEPLOYMENT_PROXY
```

until daily supply and DEX-volume series exist.

---

## 7. Governance disposition

```text
RATIFY NOW:
- checksum-validated package ingestion
- decision-ledger seed schema
- forward breadth snapshot #001
- stablecoin current supply seed
- explicit BTC.D missing-data ledger

FORWARD LOG:
- breadth snapshots using frozen daily constituents
- stablecoin supply seeds with source timestamps
- decision rows from all future DATA PING / CHIEF / Master Monday / RAW / PTR / CN outputs

DO NOT CLAIM:
- FULL M1 unlocked
- M3 unlocked
- historical breadth evidence
- stablecoin velocity/deployment proof
- populated BTC.D history
```

---

## 8. Next remediation priorities

```text
1. Obtain matched settled-UTC BTC market-cap and total-market-cap history.
2. Recover complete CHIEF / Master Monday / RAW / PTR / Forecast / Sequence ledgers.
3. Start append-only forward breadth snapshots.
4. Start append-only stablecoin supply + DEX activity collection when accessible.
5. Continue FRLP and challenger forward rows.
```

---

## 9. Canonical one-line summary

```text
The truth-layer pack is internally consistent and useful as a seed, but it does not unlock FULL M1 or M3: the BTC.D file is an all-missing gap ledger, the decision ledger is a narrow 18-row seed, while forward breadth logging is genuinely unlocked and stablecoin deployment remains current-seed-only.
```
