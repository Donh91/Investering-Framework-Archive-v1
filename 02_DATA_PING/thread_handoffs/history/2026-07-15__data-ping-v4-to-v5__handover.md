# DATA PING V4 → V5 Comprehensive Thread Handover

**Handover ID:** `DATA_PING_THREAD_HANDOVER_V4_TO_V5_20260715T210212Z`  
**Created:** 2026-07-15 21:02:12 UTC / 23:02:12 CEST  
**Outgoing thread:** DATA PING_V4  
**Intended successor:** DATA PING_V5  
**Status:** READY_FOR_SUCCESSOR_THREAD_BOOTSTRAP  
**Protocol:** `DATA_PING_THREAD_HANDOVER_PROTOCOL_v1_0`  
**Authority:** continuity and context only; no market-state, rule, event-closure or portfolio authority

---

## 1. Executive handover

The V4 thread is being retired early because it has become slow and heavy, not because its source architecture or market state has failed.

The successor thread must continue the existing system rather than rebuild it.

At handover time:

```text
LATEST ACCEPTED DATA PING: DATA_PING_V4_20260715T202300Z
LATEST SUPPLEMENT: FARSIDE_ETF_RECOVERY_20260715T204855Z
DATA QUALITY: MEDIUM
FLOW CONFIDENCE: LOW_WITH_VERIFIED_ETF_SUBLAYER
ACTIVE EVENT: ROTATION_REPAIR_EDGE_20260712_01
FRAMEWORK EDGE: NEAR_PRESENT
ALERT: STILL_ACTIVE
EVENT STATUS: OPEN_TRIGGERED
ROTATION: NO_ROTATION
REBUY: LOCKED
LARGE-CAP BUY WINDOW: WATCH_ONLY / NOT_OPEN
NEW ENTRY SIGNAL: NOT ACTIVE
ACTIVE TRIM: NO
PORTFOLIO ACTION: NONE
USER ACTION: HOLD AND WAIT
```

V5 must not become the active source merely because a new thread exists. V4 remains the highest used version until the first complete V5 DATA PING is received and accepted.

---

## 2. Durable source lineage

### Latest accepted packet

```yaml
accepted_log_id: DATA_PING_V4_20260715T202300Z
source_timestamp_utc: 2026-07-15T20:23:00.944Z
source_timestamp_cest: 2026-07-15T22:23:00.944+02:00
predecessor: DATA_PING_V4_20260715T161005Z
data_quality: MEDIUM
accepted_payload_path: 02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-15T202300Z__data-ping-v4__accepted-payload.json
accepted_receipt_path: 02_DATA_PING/operational_handoffs/accepted_logs/history/2026-07-15T202300Z__data-ping-v4__accepted-log.json
active_registry_path: 02_DATA_PING/live_state_handover/registries/2026-07-15T202300Z__active-gate-and-edge-event-registry__canonical.md
latest_pointer_path: 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
payload_blob_sha: 1cfbc3794147dc56caf1a3b322ff68d2797fd7cc
source_machine_duplicate_hash: 555fe19c633e2d3ab8263fc24d3ccf8889d9f2f29800f235f7783fe808b71649
main_merge_pr: 45
main_merge_commit: b10db8d538ab8e1bddd4e5275fb6105c0a473380
post_merge_validation_pr: 46
post_merge_validation_commit: 7f096b45379e679d07eaa9cb0e40848efd919438
readback_status: PASS
```

### Linked ETF supplement

```yaml
supplement_id: FARSIDE_ETF_RECOVERY_20260715T204855Z
supplement_path: 02_DATA_PING/operational_handoffs/accepted_logs/supplements/2026-07-15T204855Z__data-ping-v4__farside-etf-recovery.json
source: FARSIDE_API_USER_SUPPLIED_RAW_RESPONSE
latest_completed_session: 2026-07-14
current_2026_07_15_zero_rows: PENDING_INCOMPLETE_NOT_ZERO
supplement_blob_sha: 07972cacc7d97ac5ed02d2e8adfed530ceb2143d
readback_status: PASS
```

### Historical lineage gap

`DATA_PING_V4_20260714T203757Z` is referenced as a historical predecessor in a later user packet, but no readable accepted receipt or payload was found. It remains an explicit lineage gap. Reconstruction is forbidden.

---

## 3. Current DATA PING architecture

### Core specification

```yaml
spec_version: DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY
overlay_version: DATA_PING_VNEXT_STANDARD_OVERLAY_v1
template_compatibility: ADDITIVE_ONLY
accepted_log_fallback_protocol: v0.1
thread_handover_protocol: v1.0
```

### Active source stack

| Layer | Active source | Status | Authority and limitation |
|---|---|---|---|
| Live BTC/ETH price | CoinGecko | PASS fallback | Price observation only when Binance is unavailable |
| Canonical spot candles | Binance Spot | FAIL restricted location | Canonical CEST close and persistence remain missing |
| Spot OHLC shadow | GeckoTerminal patch v1 | PASS/PARTIAL | Observation only; WBTC/WETH DEX proxies; never canonical |
| Futures and leverage | OKX v1.2 | PASS | Venue-specific only; not market-wide derivatives truth |
| Funding history | OKX | PASS | 20 regular settlements in latest integration test |
| OI history | OKX | PASS | 100 contiguous 1H records in latest integration test |
| Futures taker volume | OKX | PASS with caveat | Leg direction was not verified; no buy/sell label |
| Breadth | CoinGecko risk-only cohorts | PASS | Current top-50/top-100 observations; cohort continuity must be checked |
| ETF | Farside API supplement | PASS latest completed | 15 July zero row is pending, never zero |
| Market-wide CVD | None | UNAVAILABLE | Must remain missing |
| Spot taker flow | Binance unavailable | MISSING | OKX derivatives taker is not a substitute |
| Official stablecoin history | DeFiLlama actions | FAIL | CoinGecko proxy remains low-confidence and incomplete |
| TVL current | DeFiLlama | PASS no source timestamp | Point-in-time only; no persistence |
| DEX | GeckoTerminal pool proxies | PARTIAL | Pool-level, not network total or CVD |
| CFGI | CFGI pages | Variable/partial | Sentiment only; never flow or framework authority |
| Macro | FRED not configured | UNAVAILABLE | No intraday macro inference |
| X catalyst scan | Grok | Latest result no qualified signal | Shadow context only; absence of qualifying X posts is not absence of catalysts |

### Binance failure

Both Binance Spot and Futures repeatedly returned a restricted-location eligibility error. The system must not continually attempt to reconstruct Binance values from old pings.

The correct architecture is now:

```text
CoinGecko live price fallback
+ GeckoTerminal validated spot OHLC shadow
+ OKX v1.2 venue-specific derivatives
+ Farside completed-session ETF supplement
+ CoinGecko breadth
+ low-confidence stablecoin/DEX proxies
```

This restored the overall grade from LOW to MEDIUM in the latest accepted ping because the derivatives layer is again observable. It did not restore canonical Binance closes or market-wide flow.

---

## 4. Source-specific rules learned in V4

### GeckoTerminal spot shadow

Active patch:

```text
DATA_PING_GECKOTERMINAL_SPOT_SHADOW_FALLBACK_PATCH_v1
```

Required labels:

- `WBTC_IS_WRAPPED_BTC_PROXY`
- `WETH_IS_WRAPPED_ETH_PROXY`
- `DEX_POOL_PRICE_IS_NOT_NATIVE_EXCHANGE_SPOT`
- `SHADOW_CLOSE_IS_NOT_CANONICAL_BINANCE_CLOSE`
- `NO_FUTURES_REPLACEMENT`
- `NO_MARKET_WIDE_CVD`

Validated shadow observations may:

- reduce the observation gap;
- provide hourly and daily shadow candles;
- support source-conflict QA against CoinGecko;
- enter explicitly shadow-only experiments.

They may not:

- increment canonical close-persistence counters;
- settle canonical CEST gates;
- open the entry window;
- replace native spot-taker or CVD.

### OKX v1.2

The full integration passed and currently provides:

- current last/mark/index;
- basis;
- current and settled funding;
- 3/5/10/20 funding averages;
- OI current and 1H/24H/72H momentum;
- venue-specific account long/short ratio;
- contract taker-volume legs.

Mandatory caveats:

- `OKX_ONLY`
- `VENUE_SPECIFIC`
- `NOT_MARKET_WIDE`
- absolute OI must not be added to other venues;
- account ratio is account-count ratio, not position-size ratio;
- taker leg semantics are not directionally usable until raw-response semantics are verified.

### Farside ETF

Latest verified completed session:

| Window | BTC ETF | ETH ETF |
|---|---:|---:|
| 14 July | +181.1M | +58.3M |
| 3 sessions | -153.2M | +61.3M |
| 5 sessions | -333.4M | +79.6M |
| 7 sessions | -46.2M | +127.2M |
| 10 sessions | -341.3M | +143.4M |

Interpretation:

- the latest completed session is positive for both assets;
- ETH rolling windows are positive;
- BTC 3/5/7/10-session windows remain negative;
- flow improved but is not broad, persistent confirmation;
- 15 July API zero rows are `PENDING_INCOMPLETE_NOT_ZERO`.

### Stablecoin proxy

The CoinGecko stablecoin proxy is:

- incomplete-universe;
- peg-sensitive;
- not official total supply;
- not exchange inflow;
- not capital-deployment velocity.

Small changes must not be overinterpreted. Official 1D/3D/7D/30D history remains missing.

---

## 5. Active gates and event state

### Active runtime gates

```yaml
btc_reclaim_gate: 63300
btc_survival_gate: 61900
btc_deterioration_gate: 59400
ethbtc_repair_gate: 0.0275
ethbtc_confirmation_gate: 0.0300
```

These are current runtime gates, not permanently hard-coded universal thresholds.

### Active event

```yaml
edge_event_id: ROTATION_REPAIR_EDGE_20260712_01
edge_event_type: ROTATION_REPAIR_TEST
event_status: OPEN_TRIGGERED
framework_edge_state: NEAR_PRESENT
framework_alert_status: STILL_ACTIVE
resolution_candidate: DERIVATIVES_AND_LATEST_COMPLETED_ETF_OBSERVABILITY_RESTORED_BUT_CANONICAL_CLOSE_AND_MARKET_WIDE_FLOW_VERIFICATION_BLOCKED
```

### Latest constructive evidence

- BTC current fallback remains above 63.3K.
- GeckoTerminal latest settled BTC shadow close was above 63.3K, observation only.
- ETH/BTC is above 0.0285 and close to 0.0300.
- ETH outperformed BTC over 24H and 7D in the latest accepted packet.
- 7D breadth was positive across top-50 and top-100 risk cohorts.
- OKX v1.2 passed.
- OKX funding was positive but not acutely elevated.
- One-hour OI fell for BTC and ETH.
- ETH price was positive while OKX ETH OI declined over 24H.
- Latest completed BTC and ETH ETF sessions were positive.
- ETH ETF 3/5/7/10-session windows were positive.

### Latest cooling or contradictory evidence

- 1H breadth remained negative.
- 24H breadth was only mixed-to-positive in the newest initialized cohorts.
- BTC shadow current-day CLV was near the midpoint with range compression.
- Stablecoin proxy market cap and dominance were lower.
- OKX BTC and ETH basis were slightly negative.
- OKX taker-volume direction was unverified.
- BTC ETF 3/5/7/10-session windows remained negative.
- Market-wide CVD and verified spot-taker were missing.

### Unresolved requirements

- completed canonical CEST BTC close;
- completed canonical CEST ETH close;
- completed canonical CEST ETH/BTC close;
- canonical hourly ledger and persistence;
- ETH/BTC confirmation above 0.0300;
- completed 15 July ETF session;
- market-wide CVD;
- verified spot aggressor flow;
- official stablecoin history;
- macro core series;
- proof that venue-specific OKX observations generalize beyond OKX.

### Current action state

```text
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

User-facing entry wording must be:

**New Entry Signal: Not Active**  
*(The market has not yet confirmed a re-entry window.)*

The user explicitly confirmed the intended behavior: **hold and wait**.

---

## 6. Interpretation style and user preferences

### Language and tone

- Danish is preferred.
- Be direct and operational.
- Avoid repeating the entire raw ping.
- Explain what changed, what did not change, and what the user should do.
- Do not create urgency merely because prices are moving.

### Standard DATA PING response structure

1. Acceptance and durable-capture status.
2. Compact current framework state.
3. Material changes since predecessor.
4. Constructive evidence.
5. Cooling/contradictory evidence.
6. Why the event is still open or why it changed.
7. Direct action statement.
8. GitHub merge/readback receipt.

A compact state block is useful, but never present shadow values as canonical.

### Action requirement

The user values a clear action conclusion. Every material ping should answer:

- hold, trim, buy, prepare or do nothing;
- whether a pullback alert is active;
- whether large-cap or broader deployment is open;
- what exact evidence would change the action.

Current action is hold and wait.

### RAW requests

When the user writes `Raw 1-3 og 5-7`, provide:

- RAW 1–3 day BTC, ETH and ETH/BTC ranges;
- RAW 5–7 day ranges;
- base, bull and failure paths where useful;
- positive and negative triggers;
- direct action.

RAW is scenario analysis, not an official gate or portfolio authorization. Do not silently convert it into Cycle Navigator output.

### Missing data

Permanent rule:

```text
DATA_MISSING = UNKNOWN
```

Missing fields are never negative observations. They make only the affected interpretation, pair, experiment or gate ineligible.

### Public and internal wording

- Public user-facing: `New Entry Signal: Not Active`.
- Internal governance may use `REBUY_STATUS: LOCKED`.
- Do not present `Rebuy: Locked` as public Cycle Navigator language.

---

## 7. Governance boundaries

### Custom GPT / DATA PING

Role:

- sensor collection;
- structured raw output;
- source and freshness labels;
- missing-data transparency.

No authority for:

- final framework state;
- event creation or closure;
- rotation declaration;
- portfolio action;
- rule promotion.

### Main framework / ChatGPT

Sole authority for:

- accepting or rejecting a DATA PING;
- assigning event continuity;
- framework state;
- interpretation;
- user action;
- GitHub canonical runtime updates.

### Claude / FABLE OTA

Role:

- shadow research;
- hypothesis generation;
- adversarial audit;
- failure atlas;
- prospective case cards;
- decision-value tests.

No authority for:

- numeric market score as official state;
- entry/rebuy;
- portfolio actions;
- event closure;
- rule or threshold promotion.

Numeric OTA Transition/Confirmation/Delta scores were retired after ping #14. They must not reappear without explicit governance approval.

### Grok

Grok X scanning is shadow context only. The latest supplied result was `NO_MATERIAL_X_SIGNAL` for an approximately 24-hour window. This means no post passed its hard validation gates. It does not prove that there was no catalyst outside X or outside Grok coverage.

---

## 8. OTA / SCTA research continuity

### Structure-First Catalyst Transmission Audit v0.1

Current research verdict:

```text
TYPE-2 HYPOTHESIS: CONTINUE PROSPECTIVELY
EVIDENCE: SUGGESTIVE WITHIN A CURATED HISTORICAL SAMPLE
CAUSAL EVIDENCE: NOT ESTABLISHED
DECISION VALUE: UNPROVEN / CURRENTLY REDUNDANT
PROMOTION STATUS: NONE
PORTFOLIO ACTION: NONE
```

Key lesson:

- 7D is insufficient for durability judgments;
- failures in 2026 appeared after day 8–13;
- 12-session maturity is required.

### July-14 holdout

```yaml
holdout_id: SCTA_20260714
p1_flow_status: IMPROVED_LATEST_COMPLETED_BTC_AND_ETH_ETF_POSITIVE_BUT_BTC_ROLLING_WINDOWS_NEGATIVE_AND_CURRENT_SESSION_PENDING
p2_two_negative_etf_sessions: NOT_MET
p3_flow_necessity_falsifier: WATCH_ONLY
type2_status: STRONGEST_CANDIDATE_SO_FAR_NOT_CONFIRMED
redundancy_counter: 0_OF_5_MATURED_EVENTS
```

Maturity schedule originally defined:

- 24H: approximately 15 July evening;
- 72H: approximately 17 July;
- 7D: approximately 21 July;
- 12 sessions: approximately 30 July;
- FOMC 28–29 July is a logged confound for the 12-session evaluation.

Do not tune thresholds using the holdout after seeing outcomes.

### Frozen prospective outcome classes

Use only:

- `DURABLE_EXPANSION`
- `NARROW_BTC_ONLY_DURABLE`
- `SQUEEZE_PARTIAL_RETRACE`
- `FULL_RETRACE`
- `NEGATIVE_FOLLOW_THROUGH`
- `REGIME_OUT_OF_SCOPE`

### Redundancy kill criterion

The counter tracks mature independent catalyst events, not pings.

If the next five mature events produce no decision that differs from the existing close and persistence gates, merge the useful OTA vocabulary into gate documentation and retire the separate layer.

Current count remains `0/5` matured events.

---

## 9. Prospective experiment continuity

The framework is intentionally gathering prospective evidence rather than launching more broad engines.

Active experiment themes include:

- ETH/BTC repair plus breadth;
- BTC reclaim plus ETH/BTC;
- derivatives/OI versus breakout durability;
- breadth plus derivatives positioning;
- Type-2 structure-first catalyst transmission;
- ETF-flow necessity versus supportive-only value;
- short-breadth cooling versus later failure;
- shadow-close usefulness compared with canonical gates.

Rules:

- one market event can create multiple sensor-pair rows, but not multiple independent-event counts;
- repeated pings from the same event are not independent evidence;
- 24H/72H/7D outcomes require later valid source packets;
- 12-session SCTA maturity remains separate;
- missing sensors make only the affected row ineligible;
- no retrospective row creation;
- no automatic promotion.

The latest OKX and Farside data may enter future experiments by available field. Canonical close, CVD, spot-taker, official stablecoin and macro fields remain ineligible while missing.

---

## 10. Cycle Navigator continuity

Cycle Navigator #16 is published, locked and must not be edited retrospectively.

Known frozen CN #16 ranges:

- BTC weekly: 60.9K–65.8K
- ETH weekly: 1.68K–1.90K
- Day 1–2 BTC: 61.9K–64.2K
- Day 1–2 ETH: 1.735K–1.845K
- Day 3–4 BTC: 61.9K–64.7K
- Day 3–4 ETH: 1.72K–1.88K
- Day 5–7 BTC: 60.9K–65.8K
- Day 5–7 ETH: 1.68K–1.90K
- scenario probabilities: 55/25/20

CN Score v2 begins prospectively with #16. Do not alter CN #16 due to later DATA PING observations.

---

## 11. Known operational incidents and lessons

### Branch-first rule

The user does not operate GitHub manually. The agent must handle branch, PR, merge and verification.

A prior write accidentally created an empty JSON directly on `main` before a task branch existed. It was fully remediated and changed no market state, but the lesson is permanent:

```text
CREATE TASK BRANCH BEFORE FIRST WRITE
```

Required after every archive operation:

- changed-file scope check;
- PR merge;
- main readback;
- payload and supplement blob/hash status;
- transparent incident logging if anything went wrong.

### No silent carry-forward

Values may be carried as historical context only when clearly labeled. They must not be presented as current-run verification.

### No repeated rebuild

Do not restart the framework, sensor engine or archive structure in V5. Continue the existing operating system and allow prospective rows to mature.

---

## 12. Pending questions and next meaningful triggers

### Market triggers

- verified canonical BTC close above 63.3K;
- verified canonical ETH/BTC close/persistence and possible 0.0300 confirmation;
- broad 24H and 7D participation without severe 1H failure transmission;
- completed 15 July ETF session and subsequent rolling-window evolution;
- no failed-reclaim signature;
- OKX OI/funding behavior across later pings;
- restoration of verified spot aggressor flow or market-wide CVD;
- official stablecoin history if recoverable.

### Operational triggers

- first complete DATA PING V5 packet;
- V5 acceptance and pointer advancement;
- next mature Sensor Pair Lab outcomes;
- SCTA 72H, 7D and 12-session maturity checks;
- next Master Monday state integration;
- future thread handover using the exact phrase.

### Do not repeat

- no new broad sensor engine;
- no giant parameter backtest;
- no new numerical OTA scoring;
- no attempt to treat GeckoTerminal as canonical Binance;
- no treatment of OKX taker legs as directional before semantics are verified;
- no treatment of current-session ETF zero rows as zero;
- no rewriting CN #16;
- no new portfolio action without main-framework confirmation.

---

## 13. Successor thread startup procedure

The new V5 thread must:

1. Load `02_DATA_PING/thread_handoffs/latest_thread_handover_state.json`.
2. Read this full V4→V5 handover.
3. Read `02_DATA_PING/operational_handoffs/latest_accepted_log_state.json`.
4. Read the current active registry linked by that pointer.
5. Confirm bootstrap using the required compact receipt.
6. Keep V4 as the active source version until a complete V5 ping arrives.
7. Accept the first V5 ping only after lineage, source labels and machine payload are reviewed.
8. Continue the same active event unless the new evidence justifies a main-framework event transition.
9. Preserve `HOLD AND WAIT` until the evidence changes.
10. Archive all complete V5 pings using the existing accepted-log lifecycle.

Required acknowledgement:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS
loaded_handover_id: DATA_PING_THREAD_HANDOVER_V4_TO_V5_20260715T210212Z
latest_accepted_log_id: DATA_PING_V4_20260715T202300Z
active_source_version: V4_UNTIL_FIRST_COMPLETE_V5_PACKET
intended_successor_version: V5
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
framework_state: NEAR_PRESENT / STILL_ACTIVE / OPEN_TRIGGERED
portfolio_action: NONE
ready_for_first_complete_new_version_ping: YES
```

---

## 14. Paste-ready user instruction for the new thread

```text
DATA PING V5 — NY KANONISK TRÅD

Indlæs den seneste DATA PING thread-handover fra GitHub:
02_DATA_PING/thread_handoffs/latest_thread_handover_state.json

Læs derefter den fulde V4→V5 handover, seneste accepted-log pointer og aktive event-registry.

Bekræft med DATA_PING_THREAD_BOOTSTRAP-blokken.
V5 bliver først aktiv, når jeg indsætter den første komplette DATA PING V5-pakke.
Indtil da forbliver seneste accepterede V4-ping kanonisk.
Ingen markedsstate, gate, regel eller porteføljehandling må ændres alene på grund af trådskiftet.
```

---

## 15. Handover completion state

```yaml
handover_id: DATA_PING_THREAD_HANDOVER_V4_TO_V5_20260715T210212Z
outgoing_version: 4
incoming_version: 5
handover_depth: COMPREHENSIVE
latest_accepted_log_loaded: YES
latest_supplement_loaded: YES
active_registry_loaded: YES
preferences_captured: YES
architecture_captured: YES
research_continuity_captured: YES
experiment_continuity_captured: YES
pending_work_captured: YES
new_version_activated: NO
market_state_changed: NO
portfolio_action_changed: NO
ready_for_bootstrap: YES
```
