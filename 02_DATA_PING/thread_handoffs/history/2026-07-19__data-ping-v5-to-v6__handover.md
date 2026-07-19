# DATA PING V5 → V6 Comprehensive Thread Handover

**Handover ID:** `DATA_PING_THREAD_HANDOVER_V5_TO_V6_20260719T144323Z`  
**Created:** 2026-07-19 14:43:23 UTC / 16:43:23 CEST  
**Outgoing thread:** DATA PING_V5  
**Intended successor:** DATA PING_V6  
**Status:** READY_FOR_SUCCESSOR_THREAD_BOOTSTRAP  
**Protocol:** `DATA_PING_THREAD_HANDOVER_PROTOCOL_v1_0`  
**Authority:** continuity and source architecture only; no market-state, gate, event, score or portfolio authority

## 1. Transition rule

V6 is prepared because the collector contract has materially changed and V5 contains substantial schema-test and source-QA history.

```text
V5 remains the active canonical DATA PING source.
V6 becomes active only after the first complete V6 raw packet is reviewed and accepted by ChatGPT/Main Framework.
An empty V6 thread or bootstrap acknowledgement does not supersede V5.
```

## 2. Durable source lineage

### Canonical accepted owner

```yaml
latest_accepted_log_pointer: 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
latest_decision_context_pointer: 02_DATA_PING/operational_handoffs/latest_decision_context_state.json
latest_canonical_accepted_log_id: DATA_PING_V5_20260717T162231Z
latest_canonical_payload_sha256: 0e67f519748b6c484fc9041b41a5adbcbbea5f44de813c93db3beb7c0b69f782
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
canonical_source_version: 5
```

The latest state must be resolved from the live pointers. This handover does not copy or advance canonical market state.

### Latest complete V5 raw collector packet

```yaml
collector_packet_id: DATA_PING_V5_AI2AI_TEST_20260719T105549Z
collector_packet_utc: 2026-07-19T10:55:49.567Z
collector_packet_cest: 2026-07-19T12:55:49.567+02:00
collector_packet_sha256: 5f40932f7ba692f55ca85092e8bccfa050bafdc47d70a4beffc669833b9d850a
lineage_status: VALIDATION_ONLY_RAW_CONTEXT
canonical_acceptance: false
state_change: false
portfolio_action: false
```

This V5 packet may be named as `collector_predecessor_id` in the first V6 packet. It may not be named as the canonical predecessor.

## 3. V6 architecture owner

```text
02_DATA_PING/version_governance/2026-07-19__data-ping-v6-raw-collector-contract-v1__canonical.md
```

Packet contract:

```text
DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
```

Exact wire format:

```text
DATA_PING_MAIN_THREAD_INGEST_BEGIN
{one valid 11-field JSON object}
DATA_PING_MAIN_THREAD_INGEST_END
IGNORE FOR MAIN-FRAMEWORK INGEST
PACKET_SHA256: <hash or NOT_GENERATED>
```

Exact top-level fields:

```text
packet
meta
quality
source_health
observations
source_ledgers
deterministic_source_aggregates
readiness
missing
artifacts
authority
```

## 4. Binding role separation

```text
CUSTOM GPT / DATA PING V6
= source-backed raw observations, preserved source ledgers and reproducible source aggregates

CHATGPT / MAIN FRAMEWORK
= CLV, range position, retention, gates, falsifiers, Stage-1, FNP, recovery, rotation, permissions, canonical acceptance and portfolio action

CLAUDE / OTA / FABLE
= challenger and audit only

GITHUB
= durable lineage, receipts and accepted state
```

The V6 collector must not return human market commentary, follow-through classification, recovery-attempt classification, divergence interpretation, market-input-up/down lists or action conclusions.

## 5. Mandatory V6 source ledgers

Every full V6 run should prospectively maintain:

1. complete current ISO-week BTC CEST daily OHLCV rows;
2. complete current ISO-week ETH CEST daily OHLCV rows;
3. direct ETH/BTC CEST daily OHLC rows;
4. latest settled and current partial rows with exact UTC/CEST timestamps;
5. at least ten completed Farside BTC/IBIT/ETH ETF session rows;
6. BTC and ETH Spot taker source constituents for settled 15M/1H/4H/24H windows under `DIRECT_SETTLED_HORIZONS_v1`;
7. funding, basis, OI and required OI history;
8. reproducible dynamic breadth membership, exclusions, IDs, hash and raw horizon rows;
9. source-native stablecoin, TVL, DEX, CFGI and macro observations when available;
10. raw Master Monday readiness availability fields.

Rolling 24H values never replace CEST daily candles. Weekend ETF status is `NO_SESSION_WEEKEND`, never zero.

## 6. Deterministic collector aggregates

Collector aggregates are allowed only when their underlying source rows are included.

Allowed:

- ETF session sums;
- weekly OHLC convenience aggregate;
- breadth descriptive statistics;
- net taker and buy share calculated from supplied quote-volume fields.

Main Framework recomputes and owns all decision-relevant derived values.

## 7. Breadth continuity

Dynamic breadth must preserve exact membership and membership hash. When membership changes:

```text
BREADTH_DELTA_STATUS: NOT_COMPARABLE_SAMPLE_CHANGED
```

Canonical fixed breadth remains:

```yaml
FIXED_RISK35_v1_status: UNKNOWN
reconstruction_forbidden: true
master_monday_blocking: false
sunday_closeout_blocking: false
full_data_ping_blocking: false
```

Any recovered 35-ID candidate remains `CANDIDATE_SHADOW / NOT_CANONICAL / NOT_PROMOTED` until original provenance and hash are verified.

## 8. ETF source governance

Farside is primary. Secondary OTA/Lookonchain observations remain separate and provisional.

The 17 July source history currently contains competing observations and must not be averaged:

```yaml
farside_primary_current_record:
  BTC_total_usd_m: 132.3
  ETH_total_usd_m: 36.7
secondary_provisional_observation:
  BTC_total_usd_m: 83.2
  ETH_total_usd_m: 4.3
required_handling: PRESERVE_SEPARATELY_AND_RECONCILE_SOURCE_OR_DATE_CONVENTION
```

Historical revisions remain visible. Pending is never zero.

## 9. V6 execution modes

```text
FULL_RAW_RUN
WEEKLY_SETTLED_CLOSEOUT_RAW_v1
```

The weekly closeout mode is a small source freeze after the settled Sunday CEST close. It must not regenerate a giant full-week report or repeat already preserved intraday arrays.

## 10. Master Monday data gate continuity

Current Monday workflow:

```yaml
adaptive_data_checks_cest: ["07:15", "08:15", "09:15"]
master_monday_cest: "10:00"
github_archive_sync_cest: "12:30"
```

The data gate generates a copy-ready Custom GPT completion prompt only for raw inputs that are actually missing, stale, partial, incompatible or unresolved. Main Framework performs all calculations.

Non-blocking source limitations must not generate repeated recovery requests by themselves:

- canonical FIXED_RISK35 identity missing;
- market-wide CVD unavailable;
- official stablecoin history unavailable after verified source failure;
- ETF 20-session window missing;
- TVL/DEX persistence unavailable without timestamps/history.

## 11. Current canonical decision boundary

Read current state from:

```text
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
```

At handover creation, the pointer records:

```yaml
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
rotation: NO_ROTATION
broad_recovery: NOT_CONFIRMED
large_cap_window: WATCH_ONLY_NOT_OPEN
new_entry_signal: NOT_ACTIVE
active_trim_signal: NO
portfolio_action: NONE
user_action: HOLD_AND_WAIT
```

These values are pointer context only and may be superseded by later accepted Main-Framework decisions. The handover itself changes none of them.

## 12. First V6 packet contract

The first complete V6 packet must include:

```yaml
packet: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
canonical_predecessor_id: DATA_PING_V5_20260717T162231Z
collector_predecessor_id: DATA_PING_V5_AI2AI_TEST_20260719T105549Z
execution_mode: FULL_RAW_RUN
binding: false
canonical_acceptance: false
framework_state_change: false
portfolio_action: false
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

Main Framework will validate source fields, recompute derived values and decide whether to activate V6.

## 13. Required V6 bootstrap acknowledgement

Before the first packet, the successor thread returns only:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_handover_id: DATA_PING_THREAD_HANDOVER_V5_TO_V6_20260719T144323Z
loaded_contract: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
latest_accepted_log_id: DATA_PING_V5_20260717T162231Z
active_source_version: V5
intended_successor_version: V6
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
portfolio_action: NONE
ready_for_first_complete_v6_ping: YES / NO
```

This acknowledgement is continuity-only and cannot activate V6.

## 14. Pending work and forbidden repetition

Pending:

- first complete V6 raw packet;
- Main-Framework review and activation decision;
- settled weekly closeout data before Master Monday;
- source reconciliation where primary and secondary ETF observations conflict.

Do not repeat:

- V5 format-test artifact proliferation;
- collector-owned CLV, gates or framework interpretation;
- FIXED_RISK35 reconstruction attempts;
- giant ZIP/report generation unless explicitly requested;
- reconstruction of missing market values or predecessor packets.
