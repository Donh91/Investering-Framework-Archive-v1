# DATA PING TRIGGER PROTOCOL v1.0

**Status:** Permanent Canonical Operational Rule  
**Type:** Machine Room Governance  
**Effective from:** Highest Active DATA PING Version  
**Applies to:** DATA PING V4 and all future DATA PING threads, including V5, V6, V7 etc.  
**Created:** 2026-07-05  
**Project:** Investering Framework  

---

## 1. Executive conclusion

Every relevant DATA PING, EXTENDED SNAPSHOT, EXECUTION SNAPSHOT or comparable sensor update must automatically trigger shadow processing in the background.

The user does not need to ask:

- log RAW
- create forecast ID
- update Forecast Ledger
- track sequence
- calibrate later
- remember this for Master Monday

This now happens by default.

Visible output to the user remains short and operational.

Shadow processing becomes the learning layer.

---

## 2. Core principle

DATA PINGs are not only live market updates.

They are also the framework's highest-frequency source of pre-registered micro-forecasts.

Therefore:

**Every DATA PING should create learning.**  
**Not every DATA PING should create visible noise.**

The framework must silently preserve what it believed at the time of each ping, so that Master Monday can later evaluate:

- which source was most useful
- which signal changed probability first
- which forecast was early or late
- which gates were too strict
- which gates protected correctly
- which source conflicts mattered
- which RAWs captured the weekly move best

---

## 3. What triggers the protocol

The protocol activates when the user sends any of the following:

- Custom GPT DATA PING
- Custom GPT EXTENDED SNAPSHOT
- Grok DATA PING
- Grok shadow / adversarial update
- Claude / Research Lab market audit
- execution snapshot
- weekly range ledger
- WTD range update
- threshold ledger
- relevant market sensor block

The protocol also activates if the user says:

- Data ping
- Update
- Status
- Grok
- Custom GPT
- Claude
- Master Monday prep
- range ledger
- WTD
- forecast calibration

---

## 4. Source role classification

Before any shadow forecast is created, the source must be classified.

```text
SOURCE_ROLE:
Custom GPT = truth-layer / sensor input
Grok = shadow / adversarial context
Claude = audit / Research Lab / challenger
ChatGPT = framework brain / governance / ratification
User-verified actuals = highest-priority actual range source
```

No source may be promoted beyond its role.

Grok may inform interpretation, but must not become truth-layer.

Claude may challenge the framework, but must not directly overwrite operational state.

Custom GPT may provide verified data, but must not determine rebuy, recovery, rotation or official rows.

---

## 5. Automatic shadow steps

Every relevant ping triggers the following background process.

### Step 1 - Sensor QA row

Log:

- source
- timestamp
- run type
- data quality
- confidence
- missing fields
- role discipline
- framework separation
- canonical use

Purpose:

Prevent bad data from becoming hidden conviction.

---

### Step 2 - Hard data extraction

Extract only hard fields:

- BTC price
- ETH price
- BTC dominance
- ETH/BTC
- ETF flow status
- stablecoin status
- breadth
- funding
- OI
- macro
- CFGI / sentiment
- post-flush state
- transmission
- deployment
- CHIEF
- QUICK ACTION
- thresholds
- range data

If a field is missing, write:

```text
MISSING / UNAVAILABLE
```

Never infer missing values.

---

### Step 3 - Delta vs last anchor

Compare against the latest accepted operational anchor.

Track:

- price delta
- ETH/BTC delta
- BTC.D delta
- breadth delta
- flow delta
- rotation delta
- post-flush delta
- reclaim quality delta
- deployment delta
- risk delta

If the new thread has reset persistence, write:

```text
DELTA_NOT_COMPUTED_NEW_THREAD
```

unless a prior anchor was explicitly imported.

---

### Step 4 - Silent RAW 1-3d row

Create a frozen 1-3 day forecast row.

Required fields:

- RAW_1_3D_ID
- created_at
- source_ping_id
- base BTC
- base ETH
- base ETH/BTC
- base BTC.D
- direction bias
- structure bias
- expected range
- expected sequence
- invalidation
- primary drivers
- counter-signals
- confidence
- status: PENDING

This row remains hidden unless the user asks to see it or it becomes relevant.

---

### Step 5 - Silent RAW 5-7d row

Create a frozen 5-7 day forecast row.

Required fields:

- RAW_5_7D_ID
- created_at
- source_ping_id
- weekly context
- expected 5-7d structure
- BTC range expectation
- ETH range expectation
- ETH/BTC expectation
- rotation expectation
- reclaim / rejection expectation
- main blocker
- confidence
- status: PENDING

This is especially important for Master Monday calibration.

---

### Step 6 - Sequence / PTR row

Update the active sequence state.

Relevant sequence labels include:

- Flush
- Failed hold
- Reclaim
- F1 mechanical stabilization
- F2 organic absorption watch
- Recovery attempt
- Internal repair
- Early Rotation Watch
- Selective Rotation
- Broad Altseason
- I-loop / reflush risk
- Distribution

The row must include:

- current stage
- expected next stage
- failure path
- invalidation
- time window
- source support
- confidence

Sequence rows must not be rewritten after creation.

Only outcomes may change.

---

### Step 7 - Source conflict row

If sources disagree, log a conflict row.

Example:

```text
Custom GPT breadth constructive
Grok breadth weak
Classification:
SOURCE / DEFINITION DISAGREEMENT
```

or:

```text
Grok ETF positive recent
Custom GPT ETF unsupported
Classification:
VERIFICATION REQUIRED
```

Conflict does not automatically mean deterioration.

Conflict means:

```text
confidence compression
```

until resolved.

---

### Step 8 - FNP / opportunity-cost diagnostic

Every ping must ask:

- Could the framework be too slow here?
- Could waiting for confirmation create measurable opportunity cost?
- Could defensive bias now be protecting capital or missing capture?

Allowed states:

```text
FNP_DIAGNOSTIC:
OFF
WATCH
ARMED
ROW_CANDIDATE
OFFICIAL_ROW_PENDING_RATIFICATION
```

Important:

FNP diagnostic does not equal rebuy.

FNP diagnostic does not equal recovery confirmation.

FNP diagnostic does not create official rows unless ratified.

---

### Step 9 - Calibration tags

Each ping gets tags for later Master Monday evaluation.

Examples:

- post_flush_repair
- btc_619_reclaim
- ethbtc_0275_reclaim
- flow_missing
- stablecoin_fail
- breadth_disagreement
- early_rotation_watch
- mechanical_suppression
- absorption_floor
- range_retest
- false_recovery_risk
- recovery_attempt
- no_rebuy

These tags allow weekly clustering of what mattered.

---

### Step 10 - Master Monday eligibility note

Each ping must be marked for whether it should be included in:

- Weekly RAW Learning Snapshot
- Forecast Ledger evaluation
- Range Model calibration
- Timing Trigger calibration
- Breakout / Fakeout review
- Rotation survival review
- FNP review
- Cycle Navigator scoring
- Master Monday pre-flight

Default:

Include if data quality is Medium or higher, or if it captures an important transition.

---

## 6. Visible output rule

The user should normally only see a compact operational answer.

Default visible format:

```text
ALERT / ACTION FIRST
State:
...
Delta:
...
Main blocker:
...
Shadow logging:
RAW 1-3d + RAW 5-7d + Sequence row updated silently.
```

Do not show the full hidden ledger unless the user asks.

Only expand visibly when:

1. state changes
2. source conflict is important
3. FNP risk rises
4. false recovery risk rises
5. a key threshold is hit
6. weekly calibration value is high
7. Master Monday requires explicit review

---

## 7. Governance bans

This protocol must never be used to create hidden decisions.

The following are forbidden:

- Shadow RAW = official forecast decision
- Shadow row = official v0.2 row
- FNP diagnostic = rebuy
- Early Rotation Watch = rotation confirmed
- ETH/BTC repair = broad altseason
- Price recovery = ecosystem recovery
- Grok shadow = truth-layer
- Claude audit = operational state
- Missing data = inferred confirmation

The framework must continue to distinguish:

- diagnostic vs official
- shadow vs core
- watch vs unlock
- recovery attempt vs confirmed recovery
- rotation watch vs selective rotation

---

## 8. Shadow authority safeguard

Shadow rows are observational memory only.

Hidden rows must never modify the official framework state unless they are later evaluated through Forecast Ledger, Weekly RAW Learning Snapshot, Master Monday or another explicit governance process.

Shadow processing increases accountability, not authority.

---

## 9. Handover rule

This protocol must be included in every future DATA PING handover.

All future DATA PING threads must inherit:

```text
DATA PING TRIGGER PROTOCOL v1.0
```

The handover block must explicitly say:

```text
DATA PING TRIGGER PROTOCOL v1.0 is ACTIVE.
Every relevant DATA PING automatically creates silent:
- Sensor QA row
- RAW 1-3d row
- RAW 5-7d row
- Sequence / PTR row
- Source conflict row
- FNP diagnostic
- Calibration tags
- Master Monday eligibility note
Visible output remains compact unless escalation is required.
```

Failure to include this protocol in a new DATA PING thread is a handover error.

---

## 10. Weekly evaluation rule

Before Master Monday, the operational DATA PING thread must evaluate all shadow rows from the week.

Minimum review:

1. All RAW 1-3d rows
2. All RAW 5-7d rows
3. Active 2-3w rows if eligible
4. Sequence / PTR progression
5. Source conflicts
6. Which source was most useful
7. Which pings predicted the move best
8. Which gates protected correctly
9. Which gates were too slow
10. FNP / opportunity-cost review
11. Range Model calibration
12. Timing Trigger calibration
13. Master Monday implication

No Master Monday should be finalized before this review, unless actual data is unavailable.

If actual data is unavailable:

```text
PRICE_UNVERIFIED
```

must be used.

---

## 11. Final operational rule

From this point forward:

**Every DATA PING is both a live sensor update and a silent learning event.**

The framework improves not by adding more engines, but by freezing more timestamped micro-expectations and evaluating them honestly later.

Core chain:

```text
DATA PING
-> Shadow processing
-> RAW 1-3d
-> RAW 5-7d
-> Sequence row
-> Conflict row
-> FNP diagnostic
-> Calibration tags
-> Weekly RAW Learning Snapshot
-> Master Monday
-> Cycle Navigator calibration
```

Status:

```text
ACTIVE
PERMANENT
SHADOW-GOVERNED
HANDOVER-MANDATORY
```

---

## 12. GitHub extended archive rule

Because the native project archive has reached its upload and storage limits, GitHub is now treated as the extended project archive for Investering framework material.

When the user writes:

```text
tilføj til arkivet i GitHub
```

or similar, the intended action is:

- create or append an archive-ready markdown document in GitHub
- use the most appropriate Investering repository and folder
- treat the GitHub entry as a permanent project archive extension
- keep the visible response short and confirm where the material was stored

This does not replace existing project files.

It extends them.
