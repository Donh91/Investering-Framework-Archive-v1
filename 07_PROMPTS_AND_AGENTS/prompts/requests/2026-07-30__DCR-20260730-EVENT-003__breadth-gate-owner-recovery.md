# DATA PING DEEP CAPTURE REQUEST

## Request identity

```yaml
request_id: DCR-20260730-EVENT-003
request_type: EVENT_DRIVEN_DEEP_CAPTURE
status: PREPARED
canonical_authority: NONE
portfolio_authority: NONE
```

## Role

You are a non-binding deterministic data collector for the Investering Framework.

Do not interpret framework state. Do not ratify rotation, recovery, rebuy, entry, exit or deployment. Do not recommend portfolio action. Do not reconstruct, interpolate, forward-fill or infer missing market values.

## Why this request exists

DATA PING `run_4dd78b1e713b4258aedcade193b29b8b` reported filtered Top-100 breadth at 55.0562%, above both the 50% selective gate and the 55% broad gate. At the same time, Binance direct ETHBTC owner data was unavailable because of geo restriction. The derived CoinGecko ratio was 0.02967964 and cannot score the direct gate.

The run also used a rejected QA-only predecessor, so its packet-supplied deltas are not canonical. The exact current breadth constituent rows were not emitted as the required sidecar.

A new settled follow-up session after the first 0.0300 acceptance is now available. This is a material new settled state and a material evidence gap within the existing overlap cluster.

## Reference lineage

```yaml
last_accepted_market_run: run_0bc8a5d0d0464542b29b4d50f2f8e19c
last_accepted_market_snapshot: snap_0e19c112413d471d8270cad1a18148a7
current_run: run_4dd78b1e713b4258aedcade193b29b8b
current_snapshot: snap_bed564693b804b8c9c2b7476386abd3d
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
current_observation: OBS-20260730-4dd78b1e-BREADTH-REBOUND-OWNER-OUTAGE
```

Do not use `run_7793a18aa7e94ab7b31edc60f74d928a` as a market predecessor. It is QA-only.

## Exact capture window

```yaml
start_utc: 2026-07-29T20:00:00.000Z
end_utc: 2026-07-30T14:00:00.000Z
settlement_timezones:
  - UTC
  - Europe/Copenhagen
```

## Required data only

### A. Direct Binance ETHBTC owner recovery

Return direct Binance or Binance public-data-mirror rows for ETHBTC:

1. UTC daily rows for sessions 2026-07-28 and 2026-07-29, plus 2026-07-30 marked in progress when applicable.
2. Copenhagen-settled daily rows ending at 21:59:59.999Z for 2026-07-28 and 2026-07-29, deterministically constructed from settled 1h rows.
3. Settled 1h rows from 2026-07-29T20:00:00Z through 2026-07-30T14:00:00Z.
4. Settled 5m rows from 2026-07-30T12:00:00Z through 2026-07-30T14:00:00Z.
5. For every row include open, high, low, close, base volume, quote volume, trade count, taker-buy base volume, taker-buy quote volume and settled or in-progress status.
6. Return the first settled daily follow-up after the 2026-07-28 close at 0.03007 and whether that follow-up settled at, above or below 0.0300. Report descriptively only.
7. Return direct source identity, endpoint or mirror identity, retrieval timestamp, source timestamps, row count, first and last timestamp, gaps, duplicates and SHA-256.

Do not substitute a derived USD ratio for direct ETHBTC.

### B. Exact CoinGecko point-in-time breadth sidecar

Using the exact Top-100 page payloads used by the current collector, when retained in accessible runtime lineage:

```yaml
page_1_source_timestamp: 2026-07-30T13:22:30Z
page_2_source_timestamp: 2026-07-30T13:26:12.462Z
method_id: COINGECKO_TOP100_FILTERED_v2
filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
```

Return:

1. Complete included rows with id, symbol, market-cap rank, market cap, price and 24h return.
2. Complete excluded rows with id, symbol and exclusion reason.
3. Raw, deduped, included and excluded counts.
4. Advancers, decliners, unchanged, advance ratio, median return and membership SHA-256.
5. Rank buckets 1-20, 21-50 and 51-100 with count, advance ratio, median return and equal-weight mean return.
6. Deterministic sort rule, artifact row count, bytes and SHA-256.
7. Exact replay parity against packet aggregate: 49 advancers, 32 decliners, 8 unchanged, ratio 0.550561797752809 and membership hash `49d41929bf0ebe9b7b16c37bb1e31d6808b0b199e0f051a17b766b41c12a6b81`.

When the exact page payloads are unavailable, return `EXACT_SNAPSHOT_UNAVAILABLE`. Do not substitute a later current universe.

### C. Bounded crosscheck

Return current direct or closest available ETH/BTC rows from OKX, Kraken and Coinbase only when a direct base pair exists. Keep each venue separate. Do not synthesize a direct pair from USD legs unless explicitly labeled `DERIVED_DIAGNOSTIC_NON_OWNER`.

### D. Deterministic decomposition

Using settled direct ETHBTC rows only, calculate:

- return from 2026-07-29T20:00Z to the latest settled row;
- high-to-low range;
- close location;
- spot taker-buy share;
- largest negative 1h move and its timestamp;
- count of settled hourly closes at or above 0.0300 and below 0.0300;
- UTC and Copenhagen daily settlement agreement or disagreement.

Do not assign framework labels or policy meaning.

## Known fields to omit

Do not repeat FRED, ETF, CFGI, stablecoin, chain TVL, DEX, BTC/USD or ETH/USD history unless required solely for source integrity. Do not repeat DCR-001 or DCR-002 event paths outside the exact new window.

## Integrity contract

- Direct, derived and proxy evidence must remain separate.
- Missing or not reported equals UNKNOWN, never zero.
- No current-universe substitution.
- No post-freeze source calls.
- No silent truncation.
- Split large outputs deterministically.

## Output packaging

Return deterministic JSON using schema-plus-rows when safe. For larger outputs create bounded CSV or JSON files plus one ZIP with manifest, file list, byte sizes, row counts, SHA-256 per file and package SHA-256.

After the raw output, return exactly one compact block beginning:

`START MAIN-FRAMEWORK INGEST`

Include:

- request_id
- capture_status
- completed_fields
- missing_fields
- source_failures
- artifact_names
- artifact_hashes
- earliest_source_timestamp
- latest_source_timestamp
- exact_breadth_snapshot_status
- direct_ETHBTC_status
- settled_follow_up_status
- no framework interpretation
- canonical_state_change: NOT_ASSESSED
- portfolio_action: NOT_ASSESSED

## Success condition

The first settled direct ETHBTC follow-up after the 0.0300 acceptance and the exact current breadth sidecar are delivered with complete source, timestamp, method and integrity metadata, or every unresolved field has a precise failure reason.