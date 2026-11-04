# CN #1879 · Immutable source-price repair evidence · 4 November 2026

Status: **SOURCE_PROVENANCE_VERIFIED / FORECAST_PRODUCT_UNOBSERVED / RELEASE_REVIEW_PENDING**  
Authority: Original PR #1879 engineering evidence, **not** issuance, forecast accuracy, portfolio action or approval.

## P0 original failing behavior

The original `daily_path_recovery._source_gate` always returned
`envelope_quote_independently_verified=false`, including when a source-shaped
model-produced seven-point candidate passed the other preliminary checks.
The first-pass path required that field to be true, making 7/7 unreachable.
The original W45 frozen BTC and ETH answers were independently `UNAVAILABLE`;
there is no reconstruction, score rewrite or post-event backfill.

## Byte-verifiable W44 source proof

- Completed source week: **2026-W44**, 2026-10-26 00:00Z through
  2026-11-01 23:00Z, 168 unique contiguous 1h candles per asset.
- Native original instrument pairs: **Binance Spot BTCUSDT and ETHUSDT**,
  native quote **USDT**, never silently called USD.
- Original Hourly Sequence workflow persisted raw response SHA-256s and
  original writer commit identities. Retrieved real original Actions ZIP
  artifacts and matched **16/16 raw response hashes** across eight sampled
  runs. All overlapped 1h OHLC rows agreed.
- The actual archived `03_DAILY_CAPTURE_LOGS/weekly/2026/W44/WEEKLY_HOURLY_ENRICHED.csv`
  rows matched the raw 168h OHLC data for both assets. Independent
  canonical normalized-row SHA-256:
  `398b3b455f607707641a6a92aa82b554fdb318d9f7bcf8ace3f034775c28bd01`.
  Original `W44.json.hourly_sequence.btc/eth.week_range` matches derived
  OHLC open/high/low/close. The former weekly flow `source_rows_sha256`
  is **NOT** an OHLC digest and is never accepted as one.
- Full production verifier `attest_completed_week()` was executed on the
  hosted PR runner with real GitHub API access, original Git commit history,
  original source manifests, exact raw artifacts and original W44 source.
  **PASS**: both BTC and ETH authenticated, 168 rows per asset, **7 selected
  original runs**. See
  [GitHub Actions run 41924905946](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/41924905946),
  job `126906621743`, step
  `One-time W44 original-source artifact proof for CN 1879`.
  This is historical source-quality validation **only**, NOT a W45 reissue.
- Raw provider artifacts expire after GitHub's 14-day Actions retention.
  This value-free record preserves evidence coordinates and receipts, not
  raw market payloads. Original SHA-256s remain in immutable run manifests.

## Repair architecture

Existing Hourly Sequence writer, completed-week capture, and original weekly
CN model remain the sole producers. New
`scripts/cycle_navigator/price_input_attestation.py` checks exact original
raw artifact bytes against immutable run manifests, 168h OHLC CSV, and
completed-week price-frame summary **before** the already-scheduled model
call. Each asset's independent USDT source quote is derived from the actual
original native pair, not from the model's `price_quote`. The first-pass
seven-day admission remains fail-closed per asset and per UTC issuance clock.
The previous paid semantic retry stays disabled. No new task, scheduler,
secondary issuer, source writer, secret, W45 backfill or automated trade.

## Regression and release semantics

Original PR test lane now exercises 104 offline test cases including authentic
source positive reachability, OHLC tamper with unchanged flow hash, cross-asset
USD/USDT mismatch, late day-one cutoff, caller assertion rejection, and
Authorization-header stripping on cross-host artifact redirects. The hosted
Public Contract workflow [run 41924571612](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/41924571612)
passed **104/104** including public artifact checks; hosted W44 source run
41924905946 also passed 104/104 plus the real seven-run original-artifact proof.

**Unproven:** whether the genuine prospective W46 original model will
produce an evidence-supported seven-point BTC or ETH path; model abstention
must remain allowed and must not be mislabeled a successful 7/7 forecast.
Actual user-facing graph/site and native scoring need observation after a
qualified original PR merge. Required current exact-head CI, source/recovery
authority checks and substantive independent nonwriting review are still
release gates. No independent GitHub `APPROVED` review is claimed.
