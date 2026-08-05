# Targeted Provenance Research Source Record

```yaml
request_id: TRR-CIRCLE-ARC-PROVENANCE-20260805-02
parent_request: TRR-CIRCLE-ARC-20260805-01
source_agent: CLAUDE
source_run_utc: 2026-08-05T21:52:00Z
canonical_effect_claimed: NONE
portfolio_effect_claimed: NONE
requires_main_thread_crosscheck: YES
source_verdict: METHOD_AND_FIELD_PATH_RECOVERED_AND_PROVEN_ORIGINAL_RAW_LINEAGE_LOST_FAIL_CLOSED
```

## Original claim under review

`Total stablecoin supply = USD 305.9B on 2026-08-05.`

## Recovered original method

```yaml
endpoint: https://stablecoins.llama.fi/stablecoincharts/all
arguments: NONE
field_path: record[date==1785888000].totalCirculatingUSD.peggedUSD
source_row_timestamp_utc: 2026-08-05T00:00:00Z
peg_universe: peggedUSD_ONLY
aggregation: DIRECT_FIELD_READ_NO_LOCAL_SUM
price_basis: PRICE_ADJUSTED_USD_MARKET_VALUE
original_fetch_count: 1
original_retrieval_timestamp: LOST_BOUNDED_TO_2026-08-05T20:12Z_20:19Z
original_raw_payload_sha256: LOST_UNRECOVERABLE
```

The field path is proven. The supplied raw row shows `totalCirculatingUSD.peggedUSD = 305903571269.19`, which rounds to USD 305.9B. The neighboring nominal field was `totalCirculating.peggedUSD = 305733650680.16`.

## Reproduction

```yaml
reproduction_1_utc: 2026-08-05T21:48:35Z
reproduction_2_utc: 2026-08-05T21:49:45Z
raw_payload_sha256_both: b215b5b4ab7b7ee15f301a53480476ca695f9b0f7b723e088dd0eba47c974910
payload_bytes: 1219192
record_count: 3172
reproduced_value_usd: 305903571269.19
byte_identical: true
```

The original raw payload cannot be reconstructed, and the current-day row changed between the original retrieval window and the later reproductions.

## Taxonomy defect

The `2026-08-05T00:00:00Z` record was still an in-progress daily row when read. It was not a settled observation and later revised. This violates the framework rule that partial daily rows must never be treated as closes or settled state.

The last settled row identified in the reproduced payload was:

```yaml
settled_date_utc: 2026-08-04T00:00:00Z
field_path: totalCirculatingUSD.peggedUSD
value_usd: 305860800000_APPROX_FROM_SOURCE_REPORT
raw_payload_sha256: b215b5b4ab7b7ee15f301a53480476ca695f9b0f7b723e088dd0eba47c974910
status: NEW_QA_OBSERVATION_NOT_ORIGINAL_CLAIM_NOT_SENSOR_AUTHORIZED
```

## Endpoint mixing correction

The original TRR mixed two incompatible endpoint bases:

- global total `305.9B` from `/stablecoincharts/all` using source-aggregated price-adjusted `totalCirculatingUSD.peggedUSD`;
- USDT/USDC components and shares from `/stablecoins` using a locally summed nominal denominator near `307.21B`.

Those shares are withdrawn until numerator and denominator use one field basis, one endpoint contract, one universe and one settled timestamp.

## Remaining unresolved items

- Chart API price-adjusted value near 305.90B versus rendered public-page value 300.384B: approximately 5.52B gap remains unexplained.
- `/stablecoins` asset sum near 307.18B versus chart nominal total near 305.73B: approximately 1.45B gap remains unexplained.
- DefiLlama duplicate, bridged-representation and asset-membership rules are not exposed sufficiently for independent verification.
- The chart endpoint exposes aggregate rows without an asset-membership hash.

## Source-issued correction

1. The original USD 305.9B value is retracted as a settled observation because it came from an in-progress day row.
2. The field-path claim is retained: the value came from `totalCirculatingUSD.peggedUSD`.
3. The original mixed-endpoint share calculations are retracted.
4. The proposed settled 2026-08-04 value is a new QA observation only and does not activate a sensor.
