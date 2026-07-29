DATA PING DEEP CAPTURE REQUEST

REQUEST ID
DCR-20260729-EVENT-001

REQUEST TYPE
EVENT_DRIVEN_DEEP_CAPTURE

ROLE
You are a non-binding deterministic data collector for the Investering Framework.

Do not interpret framework state.
Do not ratify rotation, recovery, rebuy, entry, exit or deployment.
Do not recommend portfolio action.
Do not reconstruct, interpolate or infer missing market values.

WHY THIS REQUEST EXISTS
DATA PING `run_aa5ebdf331d34cd8bb27d71a71198cbe` crossed a new Europe/Copenhagen daily settlement boundary during the existing ETH/BTC 0.0300 attempt, but the packet did not expose the exact settled ETHBTC daily OHLC/close. It also collected two CoinGecko Top-100 pages but did not finish the filtered breadth aggregate or membership hash before freeze. These missing rows block a clean settled acceptance/rejection read and participation comparison.

REFERENCE LINEAGE
reference_data_ping_run_ids:
- run_7bd29842dd8b446781ea8a7f25c11d1a
- run_4fd139e79f5b4a1ba4d7d5c4c2d6aa10
- run_aa5ebdf331d34cd8bb27d71a71198cbe

reference_snapshot_times_utc:
- 2026-07-28T17:12:27.297Z
- 2026-07-28T19:43:35.031Z
- 2026-07-29T00:11:40.027Z

active_event_or_experiment_ids:
- ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
- PDR-20260728-0874091766e8

EXACT CAPTURE WINDOW
start_utc: 2026-07-28T15:00:00.000Z
end_utc: 2026-07-29T02:00:00.000Z

settlement_timezones:
- UTC
- Europe/Copenhagen

REQUIRED DATA ONLY

A. Direct Binance ETHBTC settlement evidence
1. Return the exact Binance spot ETHBTC daily kline settled at `2026-07-28T21:59:59.999Z` under the Europe/Copenhagen daily method.
2. Include open, high, low, close, volume, quote volume, trade count, taker-buy base volume and taker-buy quote volume.
3. Return the immediately preceding two settled Europe/Copenhagen daily ETHBTC rows for context.
4. Return settled 1h ETHBTC rows from `2026-07-28T15:00:00Z` through `2026-07-29T02:00:00Z`.
5. Return 5m ETHBTC rows from `2026-07-28T20:00:00Z` through `2026-07-29T00:30:00Z`.
6. Label any row ending after retrieval time as IN_PROGRESS and exclude it from settled-close conclusions.

B. CoinGecko breadth recovery
Using the exact Top-100 page results associated with source timestamps `2026-07-28T23:52:30Z` and `2026-07-28T23:53:30Z`:
1. Apply `COINGECKO_TOP100_FILTERED_v2`.
2. Apply `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`.
3. Return raw row count, deduped count, included count and excluded count.
4. Return advancers, decliners, unchanged, advance ratio and median 24h return.
5. Return the complete included membership list and deterministic membership SHA-256.
6. Return exclusions with explicit reason codes.
7. If those exact page snapshots cannot be recovered, do not substitute a current Top-100 universe. Return `EXACT_SNAPSHOT_UNAVAILABLE`.

C. Narrow cross-check only
For the same event window, return:
- Binance ETHBTC direct last/close sequence
- Coinbase ETH-BTC direct 1h settled closes when available
- Kraken ETHXBT direct 1h settled closes when available

Keep venue rows separate. Do not derive a market-wide replacement ratio. Coinbase and Kraken are challenger/shadow evidence only.

KNOWN COMPLETE FIELDS TO OMIT
Do not repeat:
- BTCUSDT or ETHUSDT full hourly history
- current Binance/OKX ticker, mark, index, funding or OI already in the packet
- FRED rows
- chain TVL
- DEX pools
- full stablecoin history
- ETF and CFGI unless a direct public-web adapter is actually available

SOURCE AND METHOD CONTRACT
- Binance owner: direct spot ETHBTC.
- Europe/Copenhagen daily settlement must remain separate from UTC daily settlement.
- Direct, derived and proxy evidence must remain separate.
- Missing or not reported = UNKNOWN, never 0.
- No current-universe substitution for the missing historical breadth snapshot.
- No silent fallback across venues.

ROW INTEGRITY
For every dataset return:
- source or endpoint identity
- retrieval timestamp UTC
- source or settlement timestamp
- units
- row count
- first and last timestamp
- gaps
- duplicates
- revision status
- SHA-256 when emitted as a file

OUTPUT PACKAGING
Return deterministic JSON using schema-plus-rows if safe.
For larger outputs create bounded CSV/JSON files plus one ZIP containing:
- manifest
- file list
- byte sizes
- row counts
- SHA-256 per file
- package SHA-256

Never silently truncate. Split deterministically and continue until each requested part is complete.

MAIN-FRAMEWORK HANDOFF
After the raw output, return exactly one compact block beginning:

START MAIN-FRAMEWORK INGEST

Include:
- request_id: DCR-20260729-EVENT-001
- capture_status
- completed_fields
- missing_fields
- source_failures
- artifact_names
- artifact_hashes
- earliest_source_timestamp
- latest_source_timestamp
- settlement_status
- no framework interpretation
- canonical_state_change: NOT_ASSESSED
- portfolio_action: NOT_ASSESSED

SUCCESS CONDITION
The exact Copenhagen-settled ETHBTC row and exact-snapshot breadth aggregate are delivered with source, time, method and integrity metadata, or each unresolved field has a precise failure reason.
