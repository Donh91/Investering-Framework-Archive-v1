DATA PING DEEP CAPTURE REQUEST

REQUEST ID
DCR-20260729-EVENT-002

REQUEST TYPE
EVENT_DRIVEN_DEEP_CAPTURE

ROLE
You are a non-binding deterministic data collector for the Investering Framework.

Do not interpret framework state.
Do not ratify rotation, recovery, rebuy, entry, exit or deployment.
Do not recommend portfolio action.
Do not reconstruct, interpolate or infer missing market values.

WHY THIS REQUEST EXISTS
Between DATA PING `run_49cf4c174e254c4ebabb6cf2042109ea` and `run_0bc8a5d0d0464542b29b4d50f2f8e19c`, the filtered Top-100 advance ratio fell from 41.5730% to 26.9663%, a decline of 14.6067 percentage points or 35.14% relative, while comparable BTC and ETH prices fell only 0.62% and 1.12%. The included-universe membership hash remained identical. Direct Binance ETHBTC also remained below 0.0300 after the prior failed settled-persistence event. The ordinary packet is sufficient for current no-rotation policy, but it does not preserve the constituent-level breadth path or the intraday composition of the relapse.

REFERENCE LINEAGE
reference_data_ping_run_ids:
- run_b5988607a8f349558a19f78198fdfde2
- run_49cf4c174e254c4ebabb6cf2042109ea
- run_0bc8a5d0d0464542b29b4d50f2f8e19c

reference_snapshot_times_utc:
- 2026-07-29T05:11:52.428Z
- 2026-07-29T09:18:00.000Z
- 2026-07-29T16:51:00.829Z

active_event_or_experiment_ids:
- ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
- PDR-20260729-52aa8a0a9bf2
- OBS-20260729-0bc8a5d0-BREADTH-RELAPSE

EXACT CAPTURE WINDOW
start_utc: 2026-07-29T08:30:00.000Z
end_utc: 2026-07-29T17:00:00.000Z

settlement_timezones:
- UTC
- Europe/Copenhagen

REQUIRED DATA ONLY

A. Exact CoinGecko breadth constituent recovery
Using the exact Top-100 page payloads already used by the collector for the following source times, when retained in the current Custom GPT thread or runtime lineage:
- predecessor pages near `2026-07-29T09:03:20Z` and `2026-07-29T09:05:20Z`
- current pages near `2026-07-29T16:29:30Z` and `2026-07-29T16:31:40.868Z`

For each snapshot:
1. Apply `COINGECKO_TOP100_FILTERED_v2`.
2. Apply `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`.
3. Return the complete included membership list with id, symbol, market-cap rank, market cap, price and 24h return.
4. Return excluded rows with explicit reason codes.
5. Return raw count, deduped count, included count, excluded count, advancers, decliners, unchanged, advance ratio, median return and membership SHA-256.
6. Return rank buckets 1-20, 21-50 and 51-100 with counts, advance ratio, median return and equal-weight mean return.
7. Return the 15 largest negative and 15 largest positive changes in 24h return between the two exact snapshots.
8. Return counts that changed from advancer to decliner, decliner to advancer, unchanged to directional and directional to unchanged.
9. Do not infer categories or sectors unless a direct source field is present. Keep unsupported classifications UNKNOWN.
10. If either exact page pair is unavailable, return `EXACT_SNAPSHOT_UNAVAILABLE` for that pair. Do not substitute a later current universe.

B. Binance direct spot event path
Return settled Binance spot rows for BTCUSDT, ETHUSDT and ETHBTC:
- 1h rows from `2026-07-29T08:00:00Z` through `2026-07-29T17:00:00Z`
- 5m rows from `2026-07-29T14:00:00Z` through `2026-07-29T17:00:00Z`

For every row include:
- open, high, low, close
- base volume and quote volume
- trade count
- taker-buy base volume and taker-buy quote volume
- settled or in-progress status

Exclude in-progress rows from settled calculations.

C. Binance derivatives anchors
For BTCUSDT and ETHUSDT, return hourly anchors from `2026-07-29T08:00:00Z` through `2026-07-29T17:00:00Z` for:
- open interest
- mark price
- index price
- basis in basis points
- funding rate or latest settled funding applicable at each anchor
- futures taker buy/sell ratio
- global long/short ratio
- top-account ratio
- top-position ratio

Keep each method and timestamp separate. Do not forward-fill unavailable observations.

D. Deterministic event decomposition
Using only returned settled rows, calculate:
- BTC, ETH and ETHBTC returns for the full event window and for each 1h interval
- high-to-low range and close location
- spot taker-buy share for BTCUSDT, ETHUSDT and ETHBTC
- OI change over the event window
- whether price and OI moved in the same or opposite direction, reported descriptively only
- time of the largest negative ETHBTC 1h move
- time of the largest deterioration in filtered breadth when exact constituent snapshots are available

KNOWN COMPLETE FIELDS TO OMIT
Do not repeat:
- FRED macro rows
- chain TVL
- DEX pools
- full stablecoin history
- CFGI stale values
- settled ETF rows
- the earlier Copenhagen daily ETHBTC settlement package
- unrelated BTC or ETH history outside the exact event window

SOURCE AND METHOD CONTRACT
- Binance direct spot ETHBTC remains the owner for the ETHBTC gate.
- CoinGecko breadth snapshots must remain tied to their exact historical membership and source timestamps.
- Direct, derived and proxy evidence must remain separate.
- Missing or not reported = UNKNOWN, never 0.
- No current-universe substitution for unavailable historical breadth snapshots.
- No framework interpretation or policy recommendation.

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
- deterministic SHA-256 when emitted as a file

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
- request_id: DCR-20260729-EVENT-002
- capture_status
- completed_fields
- missing_fields
- source_failures
- artifact_names
- artifact_hashes
- earliest_source_timestamp
- latest_source_timestamp
- breadth_snapshot_status
- direct_ETHBTC_status
- no framework interpretation
- canonical_state_change: NOT_ASSESSED
- portfolio_action: NOT_ASSESSED

SUCCESS CONDITION
The exact constituent-level breadth comparison and bounded direct spot/derivatives event path are delivered with source, time, method and integrity metadata, or every unresolved field has a precise failure reason.
