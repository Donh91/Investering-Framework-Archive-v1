# Native OTA Research Readback v1

**Date:** 2026-09-04  
**Status:** PROPOSED_NATIVE_REPLACEMENT / SHADOW_ONLY  
**Authority:** ZERO_CANONICAL / ZERO_PORTFOLIO / ZERO_THRESHOLD / ZERO_PROMOTION

## 1. Purpose

Replace the recurring Claude OTA operator with a deterministic GitHub-native research readback that consumes evidence already produced by framework-owned jobs.

The objective is **functional continuity without duplicate source collection, duplicate truth, or a new market engine**.

Claude OTA historically added value as a shadow overlay for:

- settled-session follow-through;
- ETH/BTC persistence and threshold proximity;
- BTC-versus-ETH relative leadership;
- false-start / transition-versus-confirmation tracking;
- source QA and correction;
- optional forensic lane activation;
- adversarial research commentary.

Those functions are now mostly native owners. The readback therefore orchestrates and reconciles existing evidence instead of independently scraping the same market.

## 2. Non-goals

Native OTA may not:

- become a replacement for DATA PING;
- ratify recovery, rotation, altseason, distribution or portfolio action;
- create a new threshold or reinterpret an existing threshold;
- call an incomplete session settled;
- call an in-progress high a cycle high;
- invent a missing catalyst, liquidation, options or ETF observation;
- infer minute-scale order-book persistence from multi-hour captures;
- promote a research result automatically;
- rewrite historical Claude OTA rows;
- create hindsight L4 catalyst tags.

## 3. Source-owner map

Native OTA reads existing artifacts only.

### Price / BTC / ETH / ETHBTC
Owner: `03_DAILY_CAPTURE_LOGS/hourly/`

Use direct hourly BTC, ETH and ETHBTC rows. A UTC session is `SETTLED_COMPLETE_24H` only when all 24 unique UTC hour opens `00..23` are present. Anything else is `IN_PROGRESS_INCOMPLETE`.

### ETH/BTC registered reference
The existing registered `0.0300` level is read-only context. Native OTA may measure:

- consecutive settled closes at/above the level;
- settled close and low margin to the level;
- a settled cross below;
- a settled reclaim;
- descriptive last-seven-session margin slope.

It may not optimize, move or promote the level.

### Relative leadership
Derived only from complete UTC sessions:

- ETH-led settled sessions in the latest 4 and 6 sessions;
- consecutive BTC-led settled sessions;
- latest settled ETH-minus-BTC return spread.

Any current incomplete session is separately labelled `IN_PROGRESS_CONTEXT_ONLY`.

### ETF
Owner: `research/etf_owner/LATEST_FARSIDE_ETF_OWNER.json`

Native OTA reads the latest `session_final=true` row for BTC and ETH. An external OTA report missing this owner is an `OTA_CONTEXT_GAP`, not a framework data gap.

### Pullback Forensics
Owner: `03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json`

Read:

- Lane 1 executed liquidations;
- Lane 2a DVOL availability/defer status;
- Lane 2b exchange-native moneyness-bucket skew.

The options lane must remain explicitly **NOT 25-delta skew**.

Lane 3 order book remains deferred for change/persistence research because the cadence cannot support minute-scale refill/evaporation inference.

### Catalyst context
Owner: `03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/`

Situation Room and primary-source verification are native discovery/context. This does **not** by itself complete L4 catalyst attribution.

Until a native prospective event-window producer satisfies every L4 field, Native OTA reports:

`PARTIAL_NATIVE_DISCOVERY_CONTEXT_NOT_FULL_L4_ATTRIBUTION_OWNER`

Unverified discoveries never become L4 evidence rows. Missing verification remains UNKNOWN.

### Breadth
Owner: `03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json`

Role remains `PROXY_ONLY_DESCRIPTIVE_ZERO_EXECUTION_WEIGHT` under current governance. Native OTA must not resurrect the retired frozen-breadth predictive gate.

### Adaptive attention
Owner: `03_DAILY_CAPTURE_LOGS/cadence/LATEST.json`

Adaptive Rotation Cadence remains operational sampling only. A boost is attention, not confirmation and not a new market rule.

## 4. The critical gap distinction

Native OTA MUST distinguish:

### `FRAMEWORK_DATA_GAP`
The relevant native owner artifact is absent/unreadable or the native owner explicitly reports unavailable data.

### `OTA_CONTEXT_GAP`
The native owner has the data, but an external or legacy OTA report did not have/read it.

This prevents stale external context from being misreported as a framework capability gap.

## 5. Live-versus-settled QA

Hard rules:

1. `SETTLED_COMPLETE_24H` requires exactly 24 unique UTC hourly rows, hours 00 through 23.
2. Incomplete-day high/low/close is always `IN_PROGRESS`.
3. An incomplete-session high may never be labelled cycle high.
4. A new all-time/cycle-high claim requires a separately frozen historical scope; Native OTA v1 therefore reports session highs, not an unbounded `cycle_high` field.
5. Corrections must be additive and attributable; no rewrite of prior immutable run files.

This directly closes the recurring Claude OTA error class where an in-progress high was reported as the series maximum.

## 6. Fixed and early cadence

### Full research readback
Run Monday and Friday at **22:45 Europe/Copenhagen**, after the 22:13 Daily Live Anchor has had time to persist its evidence.

This is a research cadence, not a source-collection cadence.

### Daily early-trigger check
Run at **02:45 Europe/Copenhagen**, after the 02:13 live-anchor window.

The trigger-only job emits a full Native OTA report only for a genuine settled transition across the already registered ETH/BTC 0.0300 reference:

- settled cross below 0.0300; or
- settled reclaim back to/above 0.0300.

Adaptive Rotation Cadence may raise attention but does not force a full report by itself.

This intentionally avoids inventing a volatility threshold merely to reproduce Claude wording.

### Manual
`workflow_dispatch` may run a full readback or trigger-only check.

## 7. Output contract

Each emitted report must include:

- `contract = NATIVE_OTA_READBACK_v1`;
- generated timestamp and trigger;
- zero-authority declaration;
- latest complete settled session;
- incomplete current session separately, when present;
- ETH/BTC registered-reference persistence and proximity;
- relative ETH/BTC leadership summary;
- ETF owner readback;
- Pullback Forensics owner readback;
- Situation Room / L4 bridge status;
- breadth descriptive context;
- adaptive cadence context;
- classified deltas versus the prior native report;
- framework-data-gap list;
- legacy Claude OTA pointer marked context-only;
- QA semantics;
- content hash.

Outputs:

- immutable: `04_MARKET_LEARNING/ota_native/YYYY/MM/DD/HHMMSS_NATIVE_OTA_READBACK.json`
- pointer: `04_MARKET_LEARNING/ota_native/LATEST.json`

## 8. Classified delta vocabulary

Native OTA v1 uses:

- `NEW_INFORMATION` — new completed session or newly available owner observation;
- `EVIDENTIAL` — direct settled threshold transition/persistence evidence;
- `CONTEXT_ONLY` — descriptive slope, leadership, forensic or source-quality context.

The report may return `NO_MATERIAL_DELTA`. It must never force a finding.

## 9. AI role after migration

Routine OTA operation no longer requires Claude.

Qualitative challenge already exists through the framework's Daily Director / conflict-review architecture. It can challenge the same owner-bound evidence without becoming truth authority.

External Claude remains useful **on demand** for:

- red-team audits;
- source-hierarchy or governance review;
- novel historical research;
- independent falsification.

It should no longer be the fixed Monday/Friday data operator.

## 10. Legacy Claude OTA handling

`04_MARKET_LEARNING/claude_ota/` remains immutable historical research context.

After production proof of Native OTA:

- legacy Claude OTA files are not deleted;
- `LATEST_CLAUDE_OTA_STATUS_v1.json` is not a current market owner;
- no scheduled Claude OTA run is required;
- a future external Claude report is treated as challenger input and reconciled against native owners.

## 11. L4 migration boundary

The current L4 protocol names Claude OTA as external owner. Native OTA v1 does **not** silently pretend this is solved.

Production replacement is allowed while L4 remains fail-closed because:

- Claude itself repeatedly left L4 unexecuted;
- native Situation Room already provides prospective discovery plus primary-source checks;
- pretending a retrospective catalyst story is worse than an explicit UNKNOWN.

A later L4 owner migration requires a producer that freezes event ID, event/publication/classification timestamps, outcome window, category, scheduled status, primary source, source tier, confidence, move-before/after fields, affected assets and confound status before the outcome window ends.

## 12. Promotion / kill criteria

Native OTA v1 is a research readback, not a sensor.

Review or retire it if:

- it repeatedly disagrees with native owners because of its own parser logic;
- it labels incomplete data settled;
- it creates duplicate source calls that add no decision value;
- it becomes a second state authority;
- its Monday/Friday output adds no incremental research value beyond existing weekly/daily outputs after an evidence review.

The market owners survive even if this presentation/readback layer is retired.

## 13. Success definition

The migration succeeds when the framework can obtain the useful OTA functions automatically from GitHub while:

1. reducing external-model dependency;
2. eliminating stale-context false gaps;
3. shortening correction half-life;
4. preserving settled/live semantics;
5. retaining adversarial AI as an optional challenger rather than an operator;
6. making zero changes to canonical market or portfolio authority.
