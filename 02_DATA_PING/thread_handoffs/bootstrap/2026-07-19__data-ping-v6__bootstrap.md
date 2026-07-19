# DATA PING V6 Bootstrap

**Status:** `PREPARED_NOT_ACTIVE`  
**Authority:** continuity and source-contract loading only  
**Activation:** first complete V6 packet reviewed and accepted by ChatGPT/Main Framework

## Startup instruction

Read in this exact order:

```text
1. 02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
2. 02_DATA_PING/thread_handoffs/checkpoints/2026-07-19__data-ping-v5__recovery-checkpoint.md
3. 02_DATA_PING/version_governance/2026-07-19__data-ping-v6-raw-collector-contract-v1__canonical.md
4. 02_DATA_PING/thread_handoffs/history/2026-07-19__data-ping-v5-to-v6__handover.md
5. 02_DATA_PING/operational_handoffs/latest_decision_context_state.json
6. 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
7. the accepted payload, receipt and active registry referenced by those pointers
8. 02_DATA_PING/decision_value/prospective_events/ROTATION_REPAIR_EDGE_20260712_01.json
9. the first complete packet posted in DATA PING_V6
```

Do not reconstruct missing fields from memory. Do not infer market values from this bootstrap.

## Active source rule

```text
Highest numbered DATA PING version containing an actual complete Main-Framework-accepted packet wins.
```

Until a complete V6 packet is accepted:

```yaml
active_source_version: V5
V6_status: PREPARED_NOT_ACTIVE
canonical_predecessor_id: DATA_PING_V5_20260717T162231Z
collector_predecessor_id: DATA_PING_V5_AI2AI_TEST_20260719T105549Z
market_state_change_from_bootstrap: NO
portfolio_action_from_bootstrap: NONE
```

An empty V6 thread, greeting, bootstrap receipt or schema-only test does not supersede V5.

## V6 packet interface

Use:

```text
DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
```

Exact output envelope:

```text
DATA_PING_MAIN_THREAD_INGEST_BEGIN
{one valid JSON object with exactly 11 top-level fields}
DATA_PING_MAIN_THREAD_INGEST_END
IGNORE FOR MAIN-FRAMEWORK INGEST
PACKET_SHA256: <hash or NOT_GENERATED>
```

Exact 11 top-level fields:

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

No progress messages, Markdown tables, human market summary, downloads, ZIPs, duplicate text/JSON output or sidecar artifacts unless explicitly requested.

## Collector role

V6 supplies verified source observations and reproducible source ledgers only.

Required full-run foundation:

- current ISO-week BTC CEST daily OHLCV rows;
- current ISO-week ETH CEST daily OHLCV rows;
- direct ETH/BTC CEST daily OHLC rows;
- latest settled and current partial rows;
- ten completed Farside BTC/IBIT/ETH ETF session rows;
- settled BTC/ETH Spot taker 15M/1H/4H/24H inputs under `DIRECT_SETTLED_HORIZONS_v1`;
- futures funding, basis, OI and source history;
- reproducible dynamic breadth membership and hash;
- source-native stablecoin, TVL, DEX, CFGI and macro observations when available;
- raw-data readiness fields.

Main Framework computes CLV, range position, retention, gates, falsifiers, Stage-1, FNP, recovery, rotation, permissions and action.

## Source rules

```yaml
weekly_candle_basis: BINANCE_CEST_DAILY_SOURCE_ROWS
rolling_24h_substitution: FORBIDDEN
etf_primary: FARSIDE
secondary_etf_values: SEPARATE_PROVISIONAL_ONLY
weekend_etf: NO_SESSION_WEEKEND
spot_taker_method: DIRECT_SETTLED_HORIZONS_v1
dynamic_breadth_membership_hash: REQUIRED
fixed_risk35_reconstruction: FORBIDDEN
market_wide_cvd_substitution: FORBIDDEN
```

`FIXED_RISK35_v1` remains `UNKNOWN` unless the original authoritative membership, provenance and hash are recovered. It does not block V6 collection or Master Monday raw input.

## Weekly closeout mode

Use:

```text
WEEKLY_SETTLED_CLOSEOUT_RAW_v1
```

only after the settled Sunday CEST close. This mode freezes the settled weekly source rows, ETF/IBIT ledger verification, P1 source observations and readiness fields. It must remain compact and must not regenerate a giant full-week package.

## Required acknowledgement

Before the first V6 packet, return only:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_handover_id: DATA_PING_THREAD_HANDOVER_V5_TO_V6_20260719T144323Z
loaded_checkpoint_id: DATA_PING_V5_RECOVERY_CHECKPOINT_20260719T144323Z
loaded_contract: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
latest_accepted_log_id: DATA_PING_V5_20260717T162231Z
active_source_version: V5
intended_successor_version: V6
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
portfolio_action: NONE
ready_for_first_complete_v6_ping: YES / NO
```

This is a continuity receipt, not market analysis.

## First complete V6 packet

The first packet must identify both:

```yaml
canonical_predecessor_id: DATA_PING_V5_20260717T162231Z
collector_predecessor_id: DATA_PING_V5_AI2AI_TEST_20260719T105549Z
```

and must end with:

```yaml
binding: false
canonical_acceptance: false
framework_state_change: false
portfolio_action: false
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

Main Framework validates and decides activation. No state changes from the packet alone.
